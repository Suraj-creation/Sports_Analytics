"""Badminton match engine — the sequential temporal layer of the platform.

Consumes perception chunks **in frame order** and appends canonical events to the session's
event store.  Everything here is deterministic given the perception input, so the whole
semantic pipeline can be replayed from recorded perception (golden tests, re-analysis after a
model upgrade, CPU development without weights).

Latency model (VOD): a frame is *finalised* once ``lookahead`` frames after it have been seen
(gap filling, contact scoring and rally-end confirmation need that context).  Points are
emitted after the rally end plus the OCR waiting window.  With the analysis frontier running
ahead of playback by the lead buffer, all of this is invisible to the viewer.

Event flow::

    contact (provisional) ─► stroke (at next contact / rally end) ─► contact confirmed
    rally_start (provisional) ─► rally_end ─► point (+ game_end / interval / side_switch /
    match_end) ─► highlight (if notable)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from bai_badminton.analytics.match import MatchAnalytics, RallyRecord
from bai_badminton.court import Homography
from bai_badminton.events.contact import CONTACT_MODEL, ContactCandidate, detect_contacts
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallySegment
from bai_badminton.events.rally_outcome import CourtImageGeometry, Outcome, analyze_rally_end, outcome_confidence
from bai_badminton.events.stroke import (
    RuleStrokeClassifier,
    StrokeClassifier,
    StrokeContext,
    assess_smash,
    jump_features,
)
from bai_badminton.identity import IdentityResolver
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.ontology import get_ontology
from bai_badminton.perception.keypoints import KP
from bai_badminton.perception.shuttle_post import Track, process
from bai_badminton.perception_types import ChunkPerception, FramePerception, ScoreReading
from bai_badminton.rules import MatchConfig, MatchState, RallyResult, Transition, apply_rally, initial_state, other
from bai_badminton.score_ocr import ScoreReconciler
from bai_engine.schema import (
    Actors,
    ConfidenceBand,
    Event,
    EventStatus,
    Evidence,
    EvidenceKind,
    Provenance,
    StateSnapshot,
    TrackObject,
    TrackSample,
)
from bai_engine.store import EventStore
from bai_engine.timeline import Timeline

EmitFn = Callable[[list[Event]], None]


@dataclass(frozen=True)
class EngineConfig:
    fps: float
    frame_width: int
    frame_height: int
    lookahead: int = 40  # frames of future context before a frame is final
    context_back: int = 45  # past frames re-processed with each window (spike/gap context)
    history: int = 1800  # frames retained in memory (rally outcome & jump windows)
    ocr_wait_s: float = 4.0
    highlight_min_score: float = 4.0
    checkpoint_every_s: float = 10.0
    match: MatchConfig = field(default_factory=MatchConfig)
    profile: str = "unknown"


@dataclass
class _Calib:
    homography: Homography
    geometry: CourtImageGeometry


@dataclass
class _Contact:
    cand: ContactCandidate
    event: Event
    stroke_event: Event | None = None


@dataclass
class _PendingRally:
    seg: RallySegment
    contacts: list[_Contact]
    start_event: Event | None


@dataclass
class _RallyEvents:
    """Events produced for one completed rally (needed to re-emit on corrections)."""

    rally_end: Event
    point: Event | None
    transitions: list[Event]
    record: RallyRecord
    geometry_winner: str | None
    outcome: str


class BadmintonMatchEngine:
    def __init__(
        self,
        session_id: str,
        cfg: EngineConfig,
        store: EventStore,
        emit: EmitFn | None = None,
        stroke_classifier: StrokeClassifier | None = None,
        player_names: dict[str, str | None] | None = None,
    ) -> None:
        self.session_id = session_id
        self.cfg = cfg
        self.store = store
        self._emit_cb = emit
        self.timeline = Timeline.from_rate(cfg.fps, 10**9)
        self.ont = get_ontology()
        self.stroke_clf: StrokeClassifier = stroke_classifier or RuleStrokeClassifier()
        self.identity = IdentityResolver(frame_height=float(cfg.frame_height))
        self.fsm = RallyFSM(RallyParams(fps=cfg.fps))
        self.analytics = MatchAnalytics(cfg.fps)
        self.ocr = ScoreReconciler(player_names=player_names or {})
        self.state: MatchState = initial_state(cfg.match)
        self.match_cfg = cfg.match
        self.calibration: dict[int, _Calib] = {}
        self._main_calib: _Calib | None = None
        self._track_out: list[TrackSample] = []

        # dense buffers (absolute frame = _buf0 + index)
        self._buf0 = 0
        self._sx: list[float] = []
        self._sy: list[float] = []
        self._svis: list[bool] = []
        self._sconf: list[float] = []
        self._replay: list[bool] = []
        self._shot: list[int] = []
        self._players: dict[str, dict[str, list[Any]]] = {
            pid: {"bbox": [], "kps": [], "court": []} for pid in ("P1", "P2")
        }
        self._proc: Track | None = None  # processed shuttle over the current window
        self._proc0 = 0
        self._last_frame = -1
        self._final = -1  # last finalised frame
        self._open_contacts: list[_Contact] = []
        self._rally_start_event: Event | None = None
        self._pending: list[_PendingRally] = []
        self._rallies: list[_RallyEvents] = []
        self._last_checkpoint_frame = 0
        self._ocr_seen = False
        self._provenance = {"perception": "unknown"}

    # ================================================================== inputs
    def set_calibration(
        self,
        shot_id: int,
        homography: Homography,
        net_top_left: tuple[float, float] | None = None,
        net_top_right: tuple[float, float] | None = None,
        *,
        emit: bool = True,
        source: str = "auto",
    ) -> Event | None:
        """Install the court calibration for a camera shot (``emit=False`` when restoring).

        ``source`` is ``"human"`` for a calibration placed in the UI — those survive a re-analysis.
        """
        geom = CourtImageGeometry.from_homography(homography, net_top_left, net_top_right)
        self.calibration[shot_id] = _Calib(homography, geom)
        self._main_calib = self.calibration[shot_id]  # broadcasts return to the main camera after cuts
        if shot_id == 0 or self.identity.net_image_y is None:
            self.identity.net_image_y = geom.net_ground_y
        if not emit:
            return None
        frame = max(self._last_frame, 0)
        ev = self._event(
            "calibration",
            frame,
            frame,
            payload={
                "shot_id": shot_id,
                **homography.to_json(),
                "net_ground_y": geom.net_ground_y,
                "net_top_y": geom.net_top_y,
                "source": source,
            },
            confidence=float(np.clip(1.0 - homography.reprojection_error_px / 20.0, 0.0, 1.0)),
            status=EventStatus.CONFIRMED,
            model="calibration",
        )
        self._emit([ev])
        return ev

    def on_ocr(self, reading: ScoreReading) -> None:
        self._ocr_seen = True
        self.ocr.add(reading)

    def ingest(self, chunk: ChunkPerception) -> None:
        if chunk.start != self._last_frame + 1:
            raise ValueError(f"chunk starts at {chunk.start}, expected {self._last_frame + 1}")
        self._provenance.update(chunk.models)
        for fp in chunk.frames:
            self._append(fp)
        self._last_frame = chunk.end
        self._advance(self._last_frame - self.cfg.lookahead)
        self._finalize_pending(self._last_frame)
        self._maybe_checkpoint()
        self._trim()

    def flush(self) -> None:
        """End of stream: finalise everything."""
        if self._last_frame < 0:
            return
        self._advance(self._last_frame)
        upd = self.fsm.flush(self._last_frame)
        self._handle_fsm(upd, self._last_frame)
        self._finalize_pending(self._last_frame + 10**9)

    # ================================================================== buffering
    def _append(self, fp: FramePerception) -> None:
        if fp.shuttle_xy is not None:
            self._sx.append(float(fp.shuttle_xy[0]))
            self._sy.append(float(fp.shuttle_xy[1]))
            self._svis.append(True)
        else:
            self._sx.append(np.nan)
            self._sy.append(np.nan)
            self._svis.append(False)
        self._sconf.append(fp.shuttle_conf)
        self._replay.append(fp.replay)
        self._shot.append(fp.shot_id)
        calib = self._calib(fp.shot_id)
        for p in fp.persons:
            if p.court_xy is None and calib is not None:
                feet = np.array([[(p.bbox[0] + p.bbox[2]) / 2, p.bbox[3]]])
                cx, cy = calib.homography.image_to_court(feet)[0]
                p.court_xy = (float(cx), float(cy))
        assigned = (
            self.identity.assign(fp.persons, {k: v.value for k, v in self.state.ends.items()}) if not fp.replay else {}
        )
        for pid, buf in self._players.items():
            p = assigned.get(pid)
            buf["bbox"].append(p.bbox if p is not None else None)
            buf["kps"].append(p.kps if p is not None and p.kps is not None else None)
            buf["court"].append(p.court_xy if p is not None else None)
        # identity-resolved track samples for the track store / live overlays
        self._track_out.append(
            TrackSample(
                frame_idx=fp.frame_idx,
                obj=TrackObject.SHUTTLE,
                x=fp.shuttle_xy[0] if fp.shuttle_xy else None,
                y=fp.shuttle_xy[1] if fp.shuttle_xy else None,
                visible=fp.shuttle_xy is not None,
                conf=float(fp.shuttle_conf),
                model=self._provenance.get("shuttle", ""),
            )
        )
        for pid, p in assigned.items():
            self._track_out.append(
                TrackSample(
                    frame_idx=fp.frame_idx,
                    obj=TrackObject.PLAYER,
                    track_id=p.track_id,
                    player_id=pid,
                    x=float((p.bbox[0] + p.bbox[2]) / 2),
                    y=float(p.bbox[3]),
                    court_x=p.court_xy[0] if p.court_xy else None,
                    court_y=p.court_xy[1] if p.court_xy else None,
                    bbox=tuple(float(v) for v in p.bbox),  # type: ignore[arg-type]
                    keypoints=tuple(tuple(float(v) for v in row) for row in p.kps) if p.kps is not None else None,
                    conf=float(p.conf),
                    model=self._provenance.get("pose", self._provenance.get("player_detector", "")),
                )
            )

    def _calib(self, shot_id: int) -> _Calib | None:
        return self.calibration.get(shot_id) or self._main_calib

    def drain_tracks(self) -> list[TrackSample]:
        """Identity-resolved per-frame samples appended since the last call."""
        out, self._track_out = self._track_out, []
        return out

    def _trim(self) -> None:
        keep_from = min(self._final - self.cfg.history, self._final - self.cfg.context_back - 1)
        pend = [p.seg.start for p in self._pending] + [c.cand.frame for c in self._open_contacts]
        if pend:
            keep_from = min(keep_from, min(pend) - 60)
        drop = keep_from - self._buf0
        if drop <= 0:
            return
        for lst in (self._sx, self._sy, self._svis, self._sconf, self._replay, self._shot):
            del lst[:drop]
        for buf in self._players.values():
            for lst in buf.values():
                del lst[:drop]
        self._buf0 += drop

    def _window(self, lo: int, hi: int) -> WindowObs:
        """Dense observation arrays for absolute frames [lo, hi]."""
        a, b = lo - self._buf0, hi - self._buf0 + 1
        track = process(
            Track.from_arrays(
                np.array(self._sx[a:b]), np.array(self._sy[a:b]), np.array(self._svis[a:b]), np.array(self._sconf[a:b])
            )
        )
        n = b - a
        players = {}
        for pid, buf in self._players.items():
            s = PlayerSeries.empty(n)
            for i in range(n):
                bb = buf["bbox"][a + i]
                if bb is not None:
                    s.bbox[i] = bb
                k = buf["kps"][a + i]
                if k is not None:
                    s.kps[i] = k
                c = buf["court"][a + i]
                if c is not None:
                    s.court_xy[i] = c
            players[pid] = s
        return WindowObs(
            frame0=lo, fps=self.cfg.fps, shuttle=track, players=players, replay=np.array(self._replay[a:b], bool)
        )

    # ================================================================== frame advance
    def _advance(self, upto: int) -> None:
        start = self._final + 1
        if upto < start:
            return
        lo = max(self._buf0, start - self.cfg.context_back)
        w = self._window(lo, self._last_frame)
        self._proc, self._proc0 = w.shuttle, lo
        i0, i1 = w.idx(start), w.idx(upto) + 1
        contacts = {c.frame: c for c in detect_contacts(w, start=i0, stop=i1)}
        t = w.shuttle
        spd = np.zeros(w.n)
        spd[1:] = np.nan_to_num(np.hypot(np.diff(t.x), np.diff(t.y)))
        for i in range(i0, i1):
            f = w.frame0 + i
            c = contacts.get(f)
            if c is not None:
                self._handle_fsm(self.fsm.on_contact(f), f)
                self._on_contact(c, w)
            self._handle_fsm(self.fsm.step(f, bool(t.vis[i]), float(spd[i]), bool(w.replay[i])), f)
        self._final = upto

    def _handle_fsm(self, upd: Any, frame: int) -> None:
        if upd.started is not None:
            self._rally_start_event = self._event(
                "rally_start",
                upd.started,
                upd.started,
                payload={"rally_no": self.state.rally_no + 1},
                confidence=0.6,
                model="rally_fsm_v1",
            )
            self._emit([self._rally_start_event])
        if upd.cancelled_start is not None and self._rally_start_event is not None:
            self._emit([self._rally_start_event.retract(self._prov("rally_fsm_v1"), "rally shorter than minimum")])
            for c in self._open_contacts:
                self._retract_contact(c, "rally cancelled")
            self._open_contacts, self._rally_start_event = [], None
        if upd.finalized is not None:
            seg: RallySegment = upd.finalized
            in_rally = [c for c in self._open_contacts if seg.start - 3 <= c.cand.frame <= seg.end + 3]
            self._open_contacts = [c for c in self._open_contacts if c not in in_rally]
            self._pending.append(_PendingRally(seg, in_rally, self._rally_start_event))
            self._rally_start_event = None

    # ================================================================== contacts & strokes
    def _retract_contact(self, c: _Contact, note: str) -> None:
        """Withdraw a contact *and* the stroke classified from it (and its analytics)."""
        prov = self._prov("rally_fsm_v1")
        out = [c.event.retract(prov, note)]
        if c.stroke_event is not None:
            out.append(c.stroke_event.retract(prov, note))
            self.analytics.on_stroke_retracted(c.stroke_event)
        self._emit(out)

    def _on_contact(self, c: ContactCandidate, w: WindowObs) -> None:
        ev = self._event(
            "contact",
            c.frame,
            c.frame,
            actors=Actors(player_id=c.player_id),
            payload={"shuttle_xy": list(c.shuttle_xy) if c.shuttle_xy else None},
            confidence=c.p,
            evidence=(
                Evidence(kind=EvidenceKind.COMPONENT_SCORES, scores=c.components),
                Evidence(kind=EvidenceKind.TRACK_WINDOW, obj="shuttle", frames=(c.frame - 3, c.frame + 3)),
            ),
            model=CONTACT_MODEL,
        )
        self._emit([ev])
        prev = self._open_contacts[-1] if self._open_contacts else None
        self._open_contacts.append(_Contact(c, ev))
        if prev is not None and prev.stroke_event is None:
            self._classify(prev, next_frame=c.frame, is_serve=len(self._open_contacts) == 2, receiver=c)

    def _post_contact_kinematics(self, frame: int) -> tuple[float | None, float | None]:
        """Initial shuttle speed (px/s) and vertical velocity over the 4 frames after contact."""
        if self._proc is None:
            return None, None
        i = frame - self._proc0
        t = self._proc
        idx = [j for j in range(i + 1, min(len(t), i + 6)) if t.vis[j]]
        if len(idx) < 2:
            return None, None
        dt = (idx[-1] - idx[0]) / self.cfg.fps
        vx = (t.x[idx[-1]] - t.x[idx[0]]) / dt
        vy = (t.y[idx[-1]] - t.y[idx[0]]) / dt
        return float(np.hypot(vx, vy)), float(vy)

    def _player_at(
        self, pid: str | None, frame: int
    ) -> tuple[np.ndarray | None, np.ndarray | None, tuple[float, float] | None]:
        if pid is None:
            return None, None, None
        i = frame - self._buf0
        if not (0 <= i < len(self._players[pid]["bbox"])):
            return None, None, None
        b = self._players[pid]
        return b["bbox"][i], b["kps"][i], b["court"][i]

    def _classify(self, c: _Contact, next_frame: int | None, is_serve: bool, receiver: ContactCandidate | None) -> None:
        cand = c.cand
        bbox, _, court_xy = self._player_at(cand.player_id, cand.frame)
        speed, vy = self._post_contact_kinematics(cand.frame)
        above_head: bool | None = None
        if bbox is not None and cand.shuttle_xy is not None:
            above_head = bool(cand.shuttle_xy[1] < bbox[1] + 0.12 * (bbox[3] - bbox[1]))
        flight = (next_frame - cand.frame) / self.cfg.fps if next_frame is not None else None
        hitter_side = None
        if cand.player_id is not None:
            hitter_side = self.state.ends[cand.player_id].value
        ctx = StrokeContext(
            frame=cand.frame,
            player_id=cand.player_id,
            is_serve=is_serve,
            hitter_court_xy=court_xy,
            speed_after_px_s=speed,
            frame_height_px=float(self.cfg.frame_height),
            flight_time_s=flight,
            vy_after_px_s=vy,
            hitter_side=hitter_side,
            contact_above_head=above_head,
        )
        pred = self.stroke_clf.predict(ctx)
        stroke, p = pred.top
        payload: dict[str, Any] = {
            "stroke": stroke,
            "label": self.ont.stroke(stroke).label,
            "probs": dict(sorted(pred.probs.items(), key=lambda kv: -kv[1])[:4]),
            "is_serve": is_serve,
            "hitter_court_xy": list(court_xy) if court_xy else None,
            "speed_px_s": speed,
            "flight_time_s": flight,
            "contact_event_id": c.event.event_id,
            "receiver_id": receiver.player_id if receiver else None,
        }
        if receiver is not None:
            _, _, rc = self._player_at(receiver.player_id, receiver.frame)
            payload["landing_court_xy"] = list(rc) if rc else None
        comps: dict[str, float] = {}
        if stroke == "smash" or pred.probs.get("smash", 0.0) > 0.3:
            jf = self._jump_features(cand.player_id, cand.frame)
            sa = assess_smash(pred.probs.get("smash", 0.0), speed, float(self.cfg.frame_height), above_head, jf)
            payload["p_smash"] = round(sa.p_smash, 3)
            comps = {k: round(v, 4) for k, v in sa.components.items()}
            if sa.p_smash >= 0.5:
                stroke, p = "smash", max(p, sa.p_smash)
                payload["stroke"], payload["label"] = "smash", self.ont.stroke("smash").label
                if sa.p_jump is not None:
                    payload["p_jump"] = round(sa.p_jump, 3)
                    if sa.p_jump >= 0.5:
                        payload["subtype"] = "jump_smash"
                        payload["label"] = self.ont.subtypes["jump_smash"]["label"]
        margin = pred.margin
        conf = float(min(p, 0.99))
        band = self.ont.band(conf)
        if margin < 0.15 and band is ConfidenceBand.CONFIRMED:
            band = ConfidenceBand.PROBABLE
        ev = self._event(
            "stroke",
            cand.frame,
            cand.frame,
            actors=Actors(
                player_id=cand.player_id, opponent_id=other(cand.player_id) if cand.player_id in ("P1", "P2") else None
            ),  # type: ignore[arg-type]
            payload=payload,
            confidence=conf,
            band=band,
            evidence=(
                Evidence(kind=EvidenceKind.EVENT, event_id=c.event.event_id),
                Evidence(kind=EvidenceKind.COMPONENT_SCORES, scores=comps or {"margin": round(margin, 4)}),
                Evidence(kind=EvidenceKind.POSE, frames=(cand.frame - 20, cand.frame + 6)),
            ),
            model=pred.model,
            status=EventStatus.CONFIRMED,
        )
        c.stroke_event = ev
        confirmed_contact = c.event.correct(
            status=EventStatus.CONFIRMED, payload={**c.event.payload, "stroke_event_id": ev.event_id}
        )
        c.event = confirmed_contact
        self._emit([ev, confirmed_contact])
        self.analytics.on_stroke(ev)

    def _jump_features(self, pid: str | None, frame: int) -> dict[str, float] | None:
        if pid is None:
            return None
        lo, hi = frame - 22, frame + 8
        a, b = lo - self._buf0, hi - self._buf0
        buf = self._players[pid]
        if a < 0 or b > len(buf["kps"]):
            return None
        n = b - a
        ank = np.full((n, 2), np.nan)
        hips = np.full(n, np.nan)
        hts = np.full(n, np.nan)
        for i in range(n):
            k = buf["kps"][a + i]
            bb = buf["bbox"][a + i]
            if k is None or bb is None:
                continue
            ank[i] = (k[KP.L_ANKLE, 1], k[KP.R_ANKLE, 1])
            hips[i] = (k[KP.L_HIP, 1] + k[KP.R_HIP, 1]) / 2
            hts[i] = bb[3] - bb[1]
        if np.isnan(hips).mean() > 0.5:
            return None
        return jump_features(ank, hips, hts, frame - lo)

    # ================================================================== rally end → point
    def _finalize_pending(self, frontier: int) -> None:
        wait = int(self.cfg.ocr_wait_s * self.cfg.fps) if self._ocr_seen else 0
        ready = [p for p in self._pending if frontier >= p.seg.end + wait]
        for p in ready:
            self._pending.remove(p)
            self._finalize_rally(p, until=p.seg.end + wait)

    def _finalize_rally(self, p: _PendingRally, until: int) -> None:
        seg = p.seg
        # classify the last stroke (no next contact) before deciding the rally
        if p.contacts and p.contacts[-1].stroke_event is None:
            self._classify(p.contacts[-1], next_frame=None, is_serve=len(p.contacts) == 1, receiver=None)
        outcome, fault, check, conf_s = self._outcome(seg)
        before = self.state
        geometry_winner: str | None = None
        if fault in ("near", "far"):
            loser = next(pid for pid, e in before.ends.items() if e.value == fault)
            geometry_winner = other(loser)  # type: ignore[arg-type]
        winner, source = self.ocr.winner_from_ocr(dict(before.score), seg.end, until, geometry_winner)
        loser_pid = other(winner) if winner in ("P1", "P2") else None  # type: ignore[arg-type]
        shots = [
            {
                "event_id": c.stroke_event.event_id if c.stroke_event else None,
                "frame": c.cand.frame,
                "player_id": c.cand.player_id,
                "stroke": c.stroke_event.payload.get("stroke") if c.stroke_event else "unknown",
                "subtype": c.stroke_event.payload.get("subtype") if c.stroke_event else None,
                "is_serve": c.stroke_event.payload.get("is_serve") if c.stroke_event else False,
            }
            for c in p.contacts
        ]
        rally_no = before.rally_no + 1
        conf = conf_s if source == "geometry" else 0.97
        rally_end = self._event(
            "rally_end",
            seg.start,
            seg.end,
            payload={
                "rally_no": rally_no,
                "serve_frame": seg.serve_frame,
                "end_reason": seg.reason,
                "outcome": outcome,
                "fault_side": fault,
                "winner": winner,
                "loser": loser_pid,
                "winner_source": source,
                "rule_check": check,
                "n_shots": len(shots),
                "shots": shots,
                "rally_start_event_id": p.start_event.event_id if p.start_event else None,
                "duration_s": round((seg.end - seg.start + 1) / self.cfg.fps, 2),
            },
            confidence=conf if winner else 0.2,
            evidence=(
                Evidence(
                    kind=EvidenceKind.TRACK_WINDOW,
                    obj="shuttle",
                    frames=(max(seg.start, seg.end - int(3 * self.cfg.fps)), seg.end),
                ),
                Evidence(kind=EvidenceKind.SCORE_OCR if source == "ocr" else EvidenceKind.COURT, note=source),
            ),
            model="rally_outcome_v1",
            status=EventStatus.CONFIRMED,
        )
        self._emit([rally_end])
        record = RallyRecord(
            rally_id=rally_end.event_id,
            rally_no=rally_no,
            start=seg.start,
            end=seg.end,
            winner=winner,
            loser=loser_pid,
            outcome=outcome,
            shots=shots,
            score_after=dict(before.score),
            game_no=before.game_no,
            flags_before=before.flags(self.match_cfg),
            duration_s=(seg.end - seg.start + 1) / self.cfg.fps,
        )
        point, transitions = None, []
        if winner in ("P1", "P2") and not before.finished:
            res = apply_rally(before, winner, self.match_cfg)  # type: ignore[arg-type]
            point, transitions = self._point_events(res, rally_end, seg, source)
            self.state = res.after
            record.score_after = (
                dict(res.after.score)
                if Transition.GAME_END not in res.transitions
                else {"P1": res.after.completed_games[-1][0], "P2": res.after.completed_games[-1][1]}
            )
            self.store.put_state(
                StateSnapshot(
                    session_id=self.session_id,
                    frame_idx=seg.end,
                    state=self.state.to_public(self.match_cfg),
                    event_seq=point.seq,
                )
            )
        self._presence_analytics(seg)
        self.analytics.on_rally(record)
        self._rallies.append(_RallyEvents(rally_end, point, transitions, record, geometry_winner, outcome))
        h = self.analytics.score_rally(record)
        if h.score >= self.cfg.highlight_min_score:
            self._emit(
                [
                    self._event(
                        "highlight",
                        seg.start,
                        seg.end,
                        actors=Actors(player_id=h.player),
                        payload=h.to_public(),
                        confidence=min(1.0, h.score / 10),
                        model="highlight_mmr_v1",
                        status=EventStatus.CONFIRMED,
                        evidence=(Evidence(kind=EvidenceKind.EVENT, event_id=rally_end.event_id),),
                    )
                ]
            )

    def _outcome(self, seg: RallySegment) -> tuple[str, str, str, float]:
        calib = self._calib(self._shot_at(seg.end))
        if calib is None or self._proc is None:
            return Outcome.UNKNOWN.value, "unknown", "uncalibrated", 0.2
        # The FSM marks the *start* of the end condition (first stationary / invisible frame);
        # the outcome cascade must also see the shuttle at rest on the floor (CHECK 0), as the
        # legacy pipeline did with its stop-frame end times.
        settle = self.fsm.params.stationary_window if seg.reason == "stationary" else 3
        end = min(self._last_frame, seg.end + settle)
        lo = max(self._buf0, end - int(3.5 * self.cfg.fps))
        w = self._window(lo, end)
        res = analyze_rally_end(w.frames, w.shuttle.x, w.shuttle.y, w.shuttle.vis, end, calib.geometry, self.cfg.fps)
        return res.outcome.value, res.fault, res.check, outcome_confidence(res)

    def _shot_at(self, frame: int) -> int:
        i = frame - self._buf0
        return self._shot[i] if 0 <= i < len(self._shot) else 0

    def _presence_analytics(self, seg: RallySegment) -> None:
        a, b = seg.start - self._buf0, seg.end - self._buf0 + 1
        for pid, buf in self._players.items():
            pts = [c for c in buf["court"][max(0, a) : b] if c is not None]
            if pts:
                self.analytics.on_presence(pid, pts)

    def _point_events(
        self, res: RallyResult, rally_end: Event, seg: RallySegment, source: str
    ) -> tuple[Event, list[Event]]:
        cfg = self.match_cfg
        f = seg.end
        point = self._event(
            "point",
            f,
            f,
            actors=Actors(player_id=res.winner, opponent_id=other(res.winner)),
            payload={
                "winner": res.winner,
                "rally_no": res.after.rally_no,
                "state_before": res.before.to_public(cfg),
                "state_after": res.after.to_public(cfg),
                "flags_before": res.before.flags(cfg),
                "transitions": [t.value for t in res.transitions],
                "game_point_saved": res.game_point_saved,
                "source": source,
            },
            confidence=rally_end.confidence,
            evidence=(Evidence(kind=EvidenceKind.EVENT, event_id=rally_end.event_id),),
            model="bwf_rules_v1",
            status=EventStatus.CONFIRMED,
            parent_id=rally_end.event_id,
        )
        out = [point]
        for t in res.transitions:
            if t is Transition.POINT:
                continue
            payload: dict[str, Any] = {"rally_no": res.after.rally_no}
            if t is Transition.GAME_END:
                payload.update(
                    {"game_no": res.before.game_no, "winner": res.winner, "score": list(res.after.completed_games[-1])}
                )
            elif t is Transition.MATCH_END:
                payload.update({"winner": res.winner, "games": [list(g) for g in res.after.completed_games]})
            elif t is Transition.SIDE_SWITCH:
                payload.update({"ends": {k: v.value for k, v in res.after.ends.items()}})
            elif t is Transition.INTERVAL:
                payload.update({"kind": "between_games" if Transition.GAME_END in res.transitions else "mid_game"})
            out.append(
                self._event(
                    t.value,
                    f,
                    f,
                    payload=payload,
                    confidence=point.confidence,
                    model="bwf_rules_v1",
                    status=EventStatus.CONFIRMED,
                    parent_id=point.event_id,
                )
            )
        appended = self._emit(out)
        return appended[0], appended[1:]

    # ================================================================== corrections
    def correct_rally_winner(self, rally_event_id: str, winner: str, provenance: Provenance) -> list[Event]:
        """Human (or OCR) correction of a rally winner: re-fold the match from that rally."""
        idx = next((i for i, r in enumerate(self._rallies) if r.rally_end.event_id == rally_event_id), None)
        if idx is None:
            raise KeyError(rally_event_id)
        winners = [r.record.winner for r in self._rallies]
        winners[idx] = winner
        state = initial_state(self.match_cfg)
        for w in winners[:idx]:
            if w in ("P1", "P2") and not state.finished:
                state = apply_rally(state, w, self.match_cfg).after  # type: ignore[arg-type]
        new_events: list[Event] = []
        retractions: list[Event] = []
        for i in range(idx, len(self._rallies)):
            r = self._rallies[i]
            w = winners[i]
            if i == idx:
                corr = r.rally_end.correct(
                    payload={**r.rally_end.payload, "winner": w, "loser": other(w), "winner_source": "human"},  # type: ignore[arg-type]
                    status=EventStatus.HUMAN_VERIFIED,
                    provenance=provenance,
                    confidence=1.0,
                )
                corr = self._emit([corr])[0]  # stored before the point events that reference it
                new_events.append(corr)
                r.rally_end = corr
                r.record.winner, r.record.loser = w, other(w)  # type: ignore[arg-type]
            for old in ([r.point] if r.point else []) + r.transitions:
                retractions.append(old.retract(provenance, "re-folded after winner correction"))
            if w in ("P1", "P2") and not state.finished:
                res = apply_rally(state, w, self.match_cfg)  # type: ignore[arg-type]
                seg = RallySegment(r.record.start, r.record.end, None, "correction")
                point, trans = self._point_events(res, r.rally_end, seg, "human" if i == idx else "refold")
                new_events.extend([point, *trans])
                r.point, r.transitions = point, trans
                state = res.after
                self.store.put_state(
                    StateSnapshot(
                        session_id=self.session_id,
                        frame_idx=r.record.end,
                        state=state.to_public(self.match_cfg),
                        event_seq=point.seq,
                    )
                )
        self.state = state
        new_events.extend(self._emit(retractions))
        # analytics are a fold: rebuild from the corrected rally records
        self._rebuild_analytics()
        return new_events

    def on_superseded(self, ev: Event) -> None:
        """Keep the rally bookkeeping on the live version when an event is corrected outside the
        engine (e.g. a human verification appended by the plugin)."""
        for r in self._rallies:
            if r.rally_end.event_id == ev.supersedes:
                r.rally_end = ev

    # ================================================================== restart / re-analysis
    def restore_from_log(self, last_frame: int) -> int:
        """Re-attach to a finished analysis: rebuild rally bookkeeping, match state and analytics
        from the stored live view, so corrections and calibration work after a restart without
        re-running (and re-emitting) the analysis. Returns the number of rallies restored."""
        from bai_badminton.analytics.rebuild import lineage_ids, rally_records

        rallies = self.store.query(types=["rally_end"])
        records = rally_records(self.store)
        point_by_parent = {p.parent_id: p for p in self.store.query(types=["point"])}
        trans_by_parent: dict[str | None, list[Event]] = {}
        for t in self.store.query(types=[t.value for t in Transition if t is not Transition.POINT]):
            trans_by_parent.setdefault(t.parent_id, []).append(t)
        state = initial_state(self.match_cfg)
        self._rallies = []
        for ev, rec in zip(rallies, records, strict=True):
            point = next((point_by_parent[i] for i in lineage_ids(self.store, ev) if i in point_by_parent), None)
            if rec.winner in ("P1", "P2") and not state.finished:
                state = apply_rally(state, rec.winner, self.match_cfg).after  # type: ignore[arg-type]
            transitions = trans_by_parent.get(point.event_id, []) if point else []
            self._rallies.append(_RallyEvents(ev, point, transitions, rec, ev.payload.get("winner"), rec.outcome))
        self.state = state
        self._rebuild_analytics()
        self._last_frame = self._final = last_frame
        return len(self._rallies)

    def carry_over(self, events: list[Event], provenance: Provenance) -> int:
        """Re-apply human-verified events from an earlier analysis of the same video. Ids change
        on re-analysis, so events are matched by frames: rallies by overlap, other events by the
        nearest same-type event within a few frames. Idempotent; returns how many applied."""
        applied = 0
        changed_strokes = False
        for h in sorted(events, key=lambda e: e.frame_start):
            if h.status is not EventStatus.HUMAN_VERIFIED:
                continue
            if h.type == "rally_end":
                tgt = self._match_rally(h.frame_start, h.frame_end)
                if tgt is None:
                    continue
                w = h.payload.get("winner")
                if w in ("P1", "P2") and tgt.rally_end.payload.get("winner") != w:
                    self.correct_rally_winner(tgt.rally_end.event_id, w, provenance)
                    applied += 1
                elif tgt.rally_end.status is not EventStatus.HUMAN_VERIFIED:
                    corr = tgt.rally_end.correct(
                        payload=tgt.rally_end.payload,
                        status=EventStatus.HUMAN_VERIFIED,
                        provenance=provenance,
                        confidence=1.0,
                    )
                    tgt.rally_end = self._emit([corr])[0]
                    applied += 1
                continue
            cur = self._nearest(h.type, h.frame_start, tol=3)
            if cur is None:
                continue
            # labels only: ids inside the old payload point at the previous analysis
            labels = {k: v for k, v in h.payload.items() if not (k.endswith("_id") or k.endswith("_ids"))}
            payload = {**cur.payload, **labels}
            if cur.status is EventStatus.HUMAN_VERIFIED and payload == cur.payload:
                continue
            self._emit(
                [cur.correct(payload=payload, status=EventStatus.HUMAN_VERIFIED, provenance=provenance, confidence=1.0)]
            )
            changed_strokes |= h.type == "stroke"
            applied += 1
        if changed_strokes:
            self._rebuild_analytics()
        return applied

    def _match_rally(self, start: int, end: int) -> _RallyEvents | None:
        best, best_ov = None, 0
        for r in self._rallies:
            ov = min(end, r.record.end) - max(start, r.record.start)
            if ov > best_ov:
                best, best_ov = r, ov
        if best is None:
            return None
        shorter = min(end - start, best.record.end - best.record.start) or 1
        return best if best_ov / shorter >= 0.5 else None

    def _nearest(self, type_: str, frame: int, tol: int) -> Event | None:
        cands = [e for e in self.store.query(types=[type_]) if abs(e.frame_start - frame) <= tol]
        return min(cands, key=lambda e: abs(e.frame_start - frame), default=None)

    def _rebuild_analytics(self) -> None:
        self.analytics = MatchAnalytics(self.cfg.fps)
        for ev in self.store.query(types=["stroke"]):
            self.analytics.on_stroke(ev)
        for r in self._rallies:
            self.analytics.on_rally(r.record)

    # ================================================================== helpers
    def _maybe_checkpoint(self) -> None:
        every = int(self.cfg.checkpoint_every_s * self.cfg.fps)
        if self._final - self._last_checkpoint_frame >= every:
            self.store.put_state(
                StateSnapshot(
                    session_id=self.session_id,
                    frame_idx=max(self._final, 0),
                    kind="checkpoint",
                    state=self.state.to_public(self.match_cfg),
                    event_seq=self.store.last_seq(),
                )
            )
            self._last_checkpoint_frame = self._final

    def _prov(self, model: str) -> Provenance:
        return Provenance(model=model, profile=self.cfg.profile)

    def _event(
        self,
        type_: str,
        frame_start: int,
        frame_end: int,
        *,
        actors: Actors | None = None,
        payload: dict[str, Any] | None = None,
        confidence: float | None = None,
        band: ConfidenceBand | None = None,
        evidence: tuple[Evidence, ...] = (),
        model: str,
        status: EventStatus = EventStatus.PROVISIONAL,
        parent_id: str | None = None,
    ) -> Event:
        return Event(
            session_id=self.session_id,
            type=type_,
            frame_start=frame_start,
            frame_end=frame_end,
            pts_us=self.timeline.frame_to_pts_us(frame_start),
            actors=actors or Actors(),
            payload=payload or {},
            confidence=confidence,
            band=band or self.ont.band(confidence),
            status=status,
            evidence=evidence,
            provenance=self._prov(model),
            parent_id=parent_id,
        )

    def _emit(self, events: list[Event]) -> list[Event]:
        if not events:
            return []
        appended = self.store.append_many(events)
        if self._emit_cb is not None:
            self._emit_cb(appended)
        return appended

    # ================================================================== public views
    @property
    def final_frame(self) -> int:
        return self._final

    def public_state(self) -> dict[str, Any]:
        return self.state.to_public(self.match_cfg)
