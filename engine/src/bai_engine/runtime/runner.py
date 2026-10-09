"""Session runner and engine service.

One :class:`SessionRunner` thread per active session:

1. **Ingest** — (YouTube download) → probe/validate → plan → start the proxy/HLS transcode on a
   worker thread.  The session becomes ``ready_to_play`` as soon as the first HLS segment exists.
2. **Warm start** — sample keyframes across the *source* (cheap keyframe seeks) to seed the
   shuttle background model and propose a court calibration before the first chunk.
3. **Progressive analysis** — the *main cursor* walks HLS segments in order (decode → perceive →
   cache → temporal engine → tracks/events/status published).  When the viewer seeks far ahead of
   the analysis frontier, a *preview cursor* perceives segments around the playhead (overlays
   appear immediately); their perception is cached so the main cursor reuses it — no GPU work is
   ever done twice.
4. **Commands** (calibrate, correct, …) are applied between chunks on the runner thread, so the
   temporal engine is never touched concurrently.

:class:`EngineService` owns the runners and consumes commands from the bus — the same code runs
embedded in the API process (development) or as the dedicated GPU engine container.
"""

from __future__ import annotations

import contextlib
import queue
import threading
import time
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any

import av
import cv2
import numpy as np

from bai_engine.bus import Bus, topic
from bai_engine.config import Profile, Settings, load_profile
from bai_engine.decode import DecodedChunk, SegmentDecoder
from bai_engine.media import MediaError, Tools, hls_status, plan_proxy, probe, transcode, validate
from bai_engine.media.proxy import ProxyPlan, build_sprite
from bai_engine.obs import ANALYSIS_RATE, DEGRADED, EVENTS_TOTAL, FRONTIER_LEAD, QUEUE_DEPTH, get_logger
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import (
    Event,
    EventStatus,
    MediaInfo,
    Session,
    SessionStatus,
    SourceKind,
    TrackObject,
    samples_to_table,
)
from bai_engine.sources import YouTubeSource, parse_youtube_url
from bai_engine.sport import SportSession, get_plugin
from bai_engine.store import SessionRepository
from bai_engine.wire import encode_tracks

log = get_logger(__name__)
#: session.meta key holding human events to re-apply after a re-analysis
CARRY_KEY = "carried_human"


class _SessionGoneError(KeyError):
    """The session was deleted while its runner was active."""


@dataclass
class _Shared:
    playhead: int = 0
    playing: bool = False
    stop: threading.Event = field(default_factory=threading.Event)
    commands: queue.Queue[dict[str, Any]] = field(default_factory=queue.Queue)


class SessionRunner(threading.Thread):
    #: a finished runner stays resident this long without commands (corrections, calibration)
    RESIDENT_IDLE_S = 30 * 60

    def __init__(
        self,
        session_id: str,
        repo: SessionRepository,
        bus: Bus,
        settings: Settings,
        registry: ModelRegistry,
        attach: bool = False,
    ) -> None:
        super().__init__(name=f"session-{session_id[-6:]}", daemon=True)
        self.session_id = session_id
        self.attach = attach
        self.repo = repo
        self.bus = bus
        self.settings = settings
        self.registry = registry
        self.shared = _Shared()
        self.tools = Tools.resolve(settings.ffmpeg, settings.ffprobe)
        self.sport: SportSession | None = None
        self.plan: ProxyPlan | None = None
        self._transcode_thread: threading.Thread | None = None
        self._transcode_error: str | None = None
        self._rate_t0 = time.perf_counter()
        self._rate_frames = 0
        self.main_k = 0

    # ================================================================== helpers
    @property
    def session(self) -> Session:
        s = self.repo.get(self.session_id)
        if s is None:
            raise _SessionGoneError(self.session_id)
        return s

    def _status(self, status: SessionStatus | None = None, detail: str | None = None, **extra: Any) -> None:
        if status is not None:
            self.repo.set_status(self.session_id, status, detail)
        s = self.session
        n = s.media.n_frames if s.media else 0
        msg = {
            "type": "status",
            "status": s.status.value,
            "detail": s.status_detail,
            "n_frames": n,
            "frontier_frame": s.frontier_frame,
            "playhead": self.shared.playhead,
            **extra,
        }
        if self.sport is not None:
            msg["degraded"] = self.sport.degraded()
        self.bus.publish(topic(self.session_id, "status"), msg)

    def _emit_events(self, events: list[Event]) -> None:
        for e in events:
            EVENTS_TOTAL.labels(type=e.type, status=e.status.value).inc()
        self.bus.publish(
            topic(self.session_id, "events"), {"type": "events", "events": [e.model_dump(mode="json") for e in events]}
        )

    def command(self, cmd: dict[str, Any]) -> None:
        if cmd.get("cmd") == "playhead":
            self.shared.playhead = max(0, int(cmd.get("frame", 0)))
            self.shared.playing = bool(cmd.get("playing", False))
        else:
            self.shared.commands.put(cmd)

    def stop(self) -> None:
        self.shared.stop.set()

    # ================================================================== ingest
    def _ensure_media(self) -> None:
        s = self.session
        mp = self.repo.media_paths(s.source.sha256 or "")
        if s.media is not None and hls_status(mp).ended:
            self.plan = ProxyPlan(
                fps=s.media.fps,
                height=s.media.height,
                frames_per_segment=int(s.meta["frames_per_segment"]),
                encoder="existing",
                audio=s.media.has_audio,
            )
            return
        self._status(SessionStatus.INGESTING, "Preparing video")
        src = Path(s.source.uri)
        if s.source.kind is SourceKind.YOUTUBE and not src.exists():
            yt = YouTubeSource(
                parse_youtube_url(s.source.uri),
                max_height=self.settings.youtube_max_height,
                max_bytes=self.settings.max_upload_bytes,
                max_duration_s=self.settings.max_duration_s,
            )
            stored = yt.download(
                self.repo.data_dir / "media",
                on_progress=lambda f: self._status(None, None, ingest_progress=round(f * 0.5, 3)),
            )
            self.repo.update(
                self.session_id,
                source=s.source.model_copy(
                    update={"uri": str(stored.path), "sha256": stored.sha256, "original_name": stored.original_name}
                ),
                title=s.title if s.title != "YouTube video" else (stored.original_name or s.title),
            )
            s = self.session
            src = stored.path
            mp = self.repo.media_paths(stored.sha256)
        pr = probe(src, self.tools, self.settings.ffprobe_timeout_s)
        validate(pr, self.settings.max_duration_s)
        plan = plan_proxy(pr, self.tools, max_height=self.settings.proxy_height, prefer_gpu=True)
        self.plan = plan
        n_est = int(pr.duration_s * float(plan.fps))
        width = round(pr.width * plan.height / pr.height / 2) * 2
        media = MediaInfo(
            fps_num=plan.fps.numerator,
            fps_den=plan.fps.denominator,
            n_frames=n_est,
            width=width,
            height=plan.height,
            duration_us=int(pr.duration_s * 1e6),
            has_audio=pr.has_audio,
            source_width=pr.width,
            source_height=pr.height,
            source_codec=pr.codec,
            source_fps=str(pr.fps),
            variable_frame_rate=pr.variable_frame_rate,
        )
        self.repo.update(
            self.session_id,
            media=media,
            meta={**s.meta, "frames_per_segment": plan.frames_per_segment, "encoder": plan.encoder},
        )
        if hls_status(mp).ended:
            return
        mp.root.mkdir(parents=True, exist_ok=True)
        job = transcode(
            str(src),
            mp,
            plan,
            self.tools,
            pr.duration_s,
            on_progress=lambda f: self.bus.publish(
                topic(self.session_id, "status"), {"type": "ingest", "progress": round(f, 3)}
            ),
        )

        def run() -> None:
            try:
                job.run()
                st = hls_status(mp)
                n = sum(round(d * float(plan.fps)) for d in st.durations)
                cur = self.session
                if cur.media is not None and n > 0:
                    self.repo.update(self.session_id, media=cur.media.model_copy(update={"n_frames": n}))
                with contextlib.suppress(MediaError):
                    build_sprite(mp.proxy, mp, self.tools, pr.duration_s)
            except MediaError as e:
                self._transcode_error = str(e)
                log.error("transcode.failed", session=self.session_id, error=str(e))

        self._transcode_thread = threading.Thread(target=run, name=f"transcode-{self.session_id[-6:]}", daemon=True)
        self._transcode_thread.start()
        # wait for the first playable segment
        while hls_status(mp).segments == 0:
            if self._transcode_error:
                raise MediaError(self._transcode_error)
            if self.shared.stop.wait(0.2):
                return
        self._status(SessionStatus.READY_TO_PLAY, "Video ready — analysis starting")

    # ================================================================== warm start
    def _sample_keyframes(self, n: int = 24) -> list[np.ndarray]:
        s = self.session
        assert s.media is not None
        out: list[np.ndarray] = []
        try:
            with av.open(s.source.uri) as c:
                st = c.streams.video[0]
                dur = (st.duration * st.time_base) if st.duration else Fraction(s.media.duration_us, 1_000_000)
                for i in range(n):
                    t = float(dur) * (i + 0.5) / n
                    c.seek(int(t / st.time_base), stream=st, any_frame=False)
                    for fr in c.decode(st):
                        img = fr.to_ndarray(format="bgr24")
                        out.append(cv2.resize(img, (s.media.width, s.media.height), interpolation=cv2.INTER_AREA))
                        break
        except (av.FFmpegError, OSError) as e:
            log.warning("keyframes.failed", error=str(e))
        return out

    # ================================================================== analysis loop
    def _cache_path(self, k: int) -> Path:
        d = self.repo.paths(self.session_id).root / "perception"
        d.mkdir(parents=True, exist_ok=True)
        return d / f"seg_{k:05d}.msgpack"

    def _perceive(self, dec: SegmentDecoder, k: int) -> Any:
        assert self.sport is not None
        cp = self._cache_path(k)
        if cp.exists():
            return self.sport.decode_perception(cp.read_bytes())
        chunk: DecodedChunk = dec.decode_segment(k)
        p = self.sport.perceive(chunk)
        tmp = cp.with_suffix(".tmp")
        tmp.write_bytes(self.sport.encode_perception(p))
        tmp.replace(cp)
        return p

    def _publish_tracks(self, samples: list[Any], start: int, end: int, write: bool = True) -> None:
        if not samples:
            return
        if write:
            ts = self.repo.tracks(self.session_id)
            for obj in (TrackObject.SHUTTLE, TrackObject.PLAYER):
                part = [x for x in samples if x.obj is obj and start <= x.frame_idx <= end]
                if part:
                    ts.write_chunk(obj, start, end, samples_to_table(part))
        self.bus.publish(
            topic(self.session_id, "tracks"),
            {"type": "tracks", "from": start, "to": end, "bin": encode_tracks(samples, start, end)},
        )

    def _drain_commands(self) -> None:
        assert self.sport is not None
        while True:
            try:
                cmd = self.shared.commands.get_nowait()
            except queue.Empty:
                return
            reply_to = cmd.get("reply_to")
            try:
                result = self.sport.handle(cmd)
            except Exception as e:
                log.warning("command.failed", cmd=cmd.get("cmd"), error=str(e))
                result = {"ok": False, "error": str(e)}
            if reply_to:
                self.bus.publish(reply_to, {"type": "reply", "cmd": cmd.get("cmd"), "result": result})
            self.bus.publish(
                topic(self.session_id, "state"),
                {"type": "state", "state": self.sport.public_state(), "analytics": self.sport.analytics()},
            )

    def run(self) -> None:
        try:
            self._ensure_media()
            if self.shared.stop.is_set():
                return
            if self.attach:
                self._attach()
            else:
                self._analyse()
            self._resident()
        except _SessionGoneError:
            log.info("session.gone", session=self.session_id)
        except Exception as e:  # a runner failure must never kill the service
            if self.shared.stop.is_set():
                log.info("session.stopped", session=self.session_id, error=str(e))
                return
            log.exception("session.failed", session=self.session_id)
            with contextlib.suppress(Exception):
                self._status(SessionStatus.FAILED, f"Analysis failed: {e}")

    def _analyse(self) -> None:
        s = self.session
        assert s.media is not None and self.plan is not None
        profile: Profile = load_profile(s.profile, self.settings.profiles_dir)
        self.sport = self._create_sport()
        for d in self.sport.degraded():
            DEGRADED.labels(reason=d["stage"]).inc()
        self.sport.seed(self._sample_keyframes())
        mp = self.repo.media_paths(s.source.sha256 or "")
        dec = SegmentDecoder(mp, self.plan.frames_per_segment)
        F = self.plan.frames_per_segment
        fps = float(self.plan.fps)
        lead_segs = max(1, int(profile.lead_buffer_s * fps / F))
        self._status(SessionStatus.ANALYSING, "Analysing", lead_buffer_s=profile.lead_buffer_s)
        k = 0
        while not self.shared.stop.is_set():
            self._drain_commands()
            st = hls_status(mp)
            QUEUE_DEPTH.labels(session=self.session_id).set(max(0, st.segments - k))
            if k >= st.segments:
                if st.ended or self._transcode_error:
                    break
                self.shared.stop.wait(0.15)
                continue
            # seek preview: perceive near the playhead when it is far beyond the frontier
            play_k = self.shared.playhead // F
            if play_k > k + lead_segs + 2:
                for pk in range(play_k, min(play_k + 2, st.segments)):
                    if not self._cache_path(pk).exists():
                        p = self._perceive(dec, pk)
                        self._publish_tracks(self.sport.tracks_from_perception(p), pk * F, pk * F + F - 1, write=True)
                        break
            p = self._perceive(dec, k)
            self.sport.ingest(p)
            start, end = k * F, k * F + F - 1
            self._publish_tracks(self.sport.drain_tracks(), start, end)
            k += 1
            self.main_k = k
            self._progress(end, fps)
        if not self.shared.stop.is_set():
            self.sport.flush()
            self._publish_tracks(self.sport.drain_tracks(), max(0, (k - 1) * F), k * F)
            self._apply_carried()
            self.bus.publish(
                topic(self.session_id, "state"),
                {"type": "state", "state": self.sport.public_state(), "analytics": self.sport.analytics()},
            )
            if self._transcode_error:
                self._status(SessionStatus.FAILED, f"Video processing failed: {self._transcode_error}")
            else:
                self._status(SessionStatus.ANALYSED, "Analysis complete")

    def _create_sport(self) -> SportSession:
        s = self.session
        profile: Profile = load_profile(s.profile, self.settings.profiles_dir)
        store = self.repo.events(self.session_id)
        return get_plugin(s.sport).create_session(s, store, profile, self.registry, self._emit_events)

    def _attach(self) -> None:
        """Re-attach to a finished analysis: rebuild the sport session's state from the log so
        commands work — nothing is perceived or re-emitted."""
        self.sport = self._create_sport()
        restore = getattr(self.sport, "restore", None)
        n = restore(self.session.frontier_frame) if restore else 0
        log.info("session.attached", session=self.session_id, rallies=n)
        self.bus.publish(
            topic(self.session_id, "state"),
            {"type": "state", "state": self.sport.public_state(), "analytics": self.sport.analytics()},
        )
        self._status(SessionStatus.ANALYSED, "Analysis complete")

    def _resident(self) -> None:
        """Stay available for commands after analysis; exit after RESIDENT_IDLE_S without any
        (a later command re-attaches)."""
        if self.sport is None:
            return
        idle_since = time.monotonic()
        while not self.shared.stop.is_set():
            if not self.shared.commands.empty():
                self._drain_commands()
                idle_since = time.monotonic()
            elif time.monotonic() - idle_since > self.RESIDENT_IDLE_S:
                log.info("session.idle_exit", session=self.session_id)
                return
            self.shared.stop.wait(0.1)

    def _apply_carried(self) -> None:
        """Re-apply human corrections carried across a re-analysis (see EngineService)."""
        s = self.session
        raw = s.meta.get(CARRY_KEY)
        if not raw:
            return
        carry = getattr(self.sport, "carry_over", None)
        if carry is not None:
            n = carry([Event.model_validate(x) for x in raw])
            log.info("session.carried_over", session=self.session_id, events=len(raw), applied=n)
        self.repo.update(self.session_id, meta={k: v for k, v in s.meta.items() if k != CARRY_KEY})

    def _progress(self, frontier: int, fps: float) -> None:
        self._rate_frames += 1
        now = time.perf_counter()
        frames_done = frontier + 1
        elapsed = max(1e-6, now - self._rate_t0)
        rate_x = frames_done / fps / elapsed
        ANALYSIS_RATE.labels(session=self.session_id).set(rate_x)
        lead_ms = (frontier - self.shared.playhead) / fps * 1000
        FRONTIER_LEAD.labels(session=self.session_id).set(lead_ms)
        self.repo.update(self.session_id, frontier_frame=frontier, analysed_frames=frames_done)
        assert self.sport is not None
        self._status(None, None, rate_x=round(rate_x, 2), lead_ms=round(lead_ms), semantic_frame=frontier)
        if self._rate_frames % 4 == 0:
            self.bus.publish(
                topic(self.session_id, "state"),
                {"type": "state", "state": self.sport.public_state(), "analytics": self.sport.analytics()},
            )


class EngineService:
    """Owns session runners; consumes engine commands from the bus."""

    def __init__(self, repo: SessionRepository, bus: Bus, settings: Settings) -> None:
        self.repo = repo
        self.bus = bus
        self.settings = settings
        self.registry = ModelRegistry(settings.models_dir)
        self.runners: dict[str, SessionRunner] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="engine-commands", daemon=True)

    def start(self) -> None:
        self._thread.start()
        log.info("engine.started", profile=self.settings.profile)

    def shutdown(self, timeout: float = 15.0) -> None:
        self._stop.set()
        with self._lock:
            runners = list(self.runners.values())
        for r in runners:
            r.stop()
        for r in runners:
            r.join(timeout=timeout)

    def stop_session(self, session_id: str, timeout: float = 15.0) -> None:
        """Stop a session's runner and wait for it (used before deleting a session)."""
        with self._lock:
            r = self.runners.pop(session_id, None)
        if r is not None:
            r.stop()
            r.join(timeout=timeout)

    def _loop(self) -> None:
        while not self._stop.is_set():
            cmd = self.bus.next_command(timeout=0.5)
            if cmd is None:
                continue
            try:
                self.dispatch(cmd)
            except Exception:
                log.exception("engine.command_failed", cmd=cmd.get("cmd"))

    def dispatch(self, cmd: dict[str, Any]) -> None:
        sid = cmd.get("session_id")
        if not sid:
            return
        name = cmd.get("cmd")
        with self._lock:
            runner = self.runners.get(sid)
            if name in ("start", "reanalyse"):
                if runner is not None and runner.is_alive():
                    if name == "start":
                        return
                    runner.stop()
                    runner.join(timeout=30)
                attach = False
                if name == "reanalyse":
                    self._reset_semantics(sid)
                else:
                    attach = self._prepare_start(sid)
                runner = SessionRunner(sid, self.repo, self.bus, self.settings, self.registry, attach=attach)
                self.runners[sid] = runner
                runner.start()
                return
            if name == "stop":
                if runner:
                    runner.stop()
                return
        if runner is None or not runner.is_alive():
            if name == "playhead":
                return
            # commands for a finished session restart it (cached perception makes this cheap)
            self.dispatch({"cmd": "start", "session_id": sid})
            runner = self.runners[sid]
        runner.command(cmd)

    def _prepare_start(self, sid: str) -> bool:
        """Decide how a (re)started runner begins. Returns True to re-attach to a finished
        analysis. An interrupted analysis can't resume mid-log, so it restarts from a clean log
        (cheap: perception is cached) keeping the human inputs."""
        s = self.repo.get(sid)
        if s is None or self.repo.events(sid).last_seq() == 0:
            return False
        if s.status is SessionStatus.ANALYSED:
            return True
        self._reset_semantics(sid)
        return False

    def _reset_semantics(self, sid: str) -> None:
        """Drop the event log and tracks (keeping the perception cache) for a full re-analysis.

        Human inputs survive: the latest manual calibration is re-appended to the new log, and
        human-verified events are carried in session meta and re-applied (matched by frames)
        when the new analysis finishes.
        """
        store = self.repo.events(sid)
        live = store.query()
        human = [e for e in live if e.status is EventStatus.HUMAN_VERIFIED]
        manual_cal = [e for e in live if e.type == "calibration" and e.payload.get("source") == "human"]
        s = self.repo.get(sid)
        meta = dict(s.meta) if s else {}
        carried = {(d["type"], d["frame_start"]): d for d in meta.get(CARRY_KEY) or []}
        for e in human:  # newer human input for the same moment wins
            carried[(e.type, e.frame_start)] = e.model_dump(mode="json")
        self.repo.reset_analysis(sid)
        if manual_cal:
            c = manual_cal[-1]
            self.repo.events(sid).append(Event.model_validate(c.model_dump(exclude={"event_id", "seq", "supersedes"})))
        if carried:
            meta[CARRY_KEY] = list(carried.values())
        else:
            meta.pop(CARRY_KEY, None)
        self.repo.update(sid, meta=meta)
