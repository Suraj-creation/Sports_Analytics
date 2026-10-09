"""Session runner lifecycle: resident after analysis, re-attach after a restart, and re-analysis
that keeps the human inputs (manual calibration, verified corrections). Real FFmpeg media, a fake
sport plugin that emits one rally per HLS segment."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, ClassVar

import av
import msgpack
import numpy as np
import pytest

from bai_engine.bus import LocalBus
from bai_engine.config import REPO_ROOT, Settings
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.runner import EngineService
from bai_engine.schema import Event, EventStatus, Provenance, Session, SessionStatus
from bai_engine.schema.session import Source, SourceKind
from bai_engine.sources import store_upload
from bai_engine.sport import register
from bai_engine.store import EventStore, SessionRepository

PROFILE = """
description: lifecycle test
device: cpu
chunk_frames: 30
lead_buffer_s: 0.5
shuttle: {model: none, backend: none}
player_detector: {model: none, backend: none}
pose: {model: none, backend: none}
stroke: {model: none, backend: none}
"""
HUMAN = Provenance(model="human", worker="test")


class FakeSession:
    instances: ClassVar[list[FakeSession]] = []

    def __init__(self, session: Session, store: EventStore, profile: Any, registry: Any, emit: Any) -> None:
        self.session, self.store, self._emit_cb = session, store, emit
        self.restored: int | None = None
        self.carried: list[Event] = []
        FakeSession.instances.append(self)

    def _emit(self, evs: list[Event]) -> list[Event]:
        out = self.store.append_many(evs)
        self._emit_cb(out)
        return out

    # protocol
    def seed(self, keyframes: list[Any]) -> None:
        if not self.store.query(types=["calibration"]):
            self._emit([self._ev("calibration", 0, 0, {"source": "auto"})])

    def perceive(self, chunk: DecodedChunk) -> Any:
        return {"start": chunk.start, "end": chunk.end}

    def encode_perception(self, p: Any) -> bytes:
        return msgpack.packb(p)

    def decode_perception(self, data: bytes) -> Any:
        return msgpack.unpackb(data)

    def ingest(self, p: Any) -> None:
        self._emit([self._ev("rally_end", p["start"], p["end"], {"winner": "P1"})])

    def flush(self) -> None: ...

    def drain_tracks(self) -> list[Any]:
        return []

    def tracks_from_perception(self, p: Any) -> list[Any]:
        return []

    @property
    def in_play(self) -> bool:
        return False

    def public_state(self) -> dict[str, Any]:
        return {}

    def analytics(self) -> dict[str, Any]:
        return {}

    def degraded(self) -> list[dict[str, str]]:
        return []

    def handle(self, cmd: dict[str, Any]) -> dict[str, Any]:
        if cmd["cmd"] == "calibrate":
            self._emit([self._ev("calibration", 0, 0, {"source": "human", "points": cmd["points"]})])
        elif cmd["cmd"] == "correct_winner":
            ev = next(e for e in self.store.query(types=["rally_end"]) if e.event_id == cmd["rally_event_id"])
            self._correct(ev, cmd["winner"])
        return {"ok": True}

    def restore(self, last_frame: int) -> int:
        self.restored = last_frame
        return len(self.store.query(types=["rally_end"]))

    def carry_over(self, events: list[Event]) -> int:
        self.carried.extend(events)
        n = 0
        for h in events:
            for r in self.store.query(types=["rally_end"]):
                if r.frame_start == h.frame_start and r.payload["winner"] != h.payload["winner"]:
                    self._correct(r, h.payload["winner"])
                    n += 1
        return n

    # helpers
    def _ev(self, type_: str, a: int, b: int, payload: dict[str, Any]) -> Event:
        return Event(
            session_id=self.session.session_id,
            type=type_,
            frame_start=a,
            frame_end=b,
            pts_us=0,
            payload=payload,
            status=EventStatus.CONFIRMED,
            provenance=Provenance(model="fake"),
        )

    def _correct(self, ev: Event, winner: str) -> None:
        self._emit(
            [ev.correct(payload={**ev.payload, "winner": winner}, status=EventStatus.HUMAN_VERIFIED, provenance=HUMAN)]
        )


class FakePlugin:
    name = "fake"

    def create_session(
        self, session: Session, store: EventStore, profile: Any, registry: Any, emit: Any
    ) -> FakeSession:
        return FakeSession(session, store, profile, registry, emit)


@pytest.fixture
def env(tmp_path: Path) -> tuple[Settings, SessionRepository, str]:
    register(FakePlugin())  # type: ignore[arg-type]
    FakeSession.instances.clear()
    prof = tmp_path / "profiles"
    prof.mkdir()
    (prof / "life.yaml").write_text(PROFILE, encoding="utf-8")
    settings = Settings(
        data_dir=tmp_path / "data",
        profiles_dir=prof,
        models_dir=REPO_ROOT / "models",
        profile="life",
        redis_url=None,
        _env_file=None,
    )  # type: ignore[call-arg]
    clip = tmp_path / "clip.mp4"
    with av.open(str(clip), "w") as out:
        s = out.add_stream("libx264", rate=30)
        s.width, s.height, s.pix_fmt = 320, 180, "yuv420p"
        for i in range(90):
            for pkt in s.encode(av.VideoFrame.from_ndarray(np.full((180, 320, 3), i % 255, np.uint8), format="bgr24")):
                out.mux(pkt)
        for pkt in s.encode():
            out.mux(pkt)
    stored = store_upload([clip.read_bytes()], settings.data_dir / "media", "clip.mp4", 10**9)
    repo = SessionRepository(settings.data_dir)
    sess = repo.save(
        Session(
            title="t",
            sport="fake",
            profile="life",
            source=Source(kind=SourceKind.UPLOAD, uri=str(stored.path), original_name="clip.mp4", sha256=stored.sha256),
        )
    )
    return settings, repo, sess.session_id


def _wait(cond: Any, timeout: float = 60) -> None:
    t0 = time.time()
    while time.time() - t0 < timeout:
        if cond():
            return
        time.sleep(0.1)
    raise AssertionError("timed out")


def _analysed(repo: SessionRepository, sid: str) -> bool:
    s = repo.get(sid)
    return s is not None and s.status is SessionStatus.ANALYSED


def _rallies(repo: SessionRepository, sid: str) -> list[Event]:
    return repo.events(sid).query(types=["rally_end"])


def test_runner_stays_resident_and_applies_commands_after_analysis(env: Any) -> None:
    settings, repo, sid = env
    svc = EngineService(repo, LocalBus(), settings)
    try:
        svc.dispatch({"cmd": "start", "session_id": sid})
        _wait(lambda: _analysed(repo, sid))
        n = len(_rallies(repo, sid))
        assert n >= 2  # one fake rally per HLS segment
        first = _rallies(repo, sid)[0]
        svc.dispatch({"cmd": "correct_winner", "session_id": sid, "rally_event_id": first.event_id, "winner": "P2"})
        _wait(lambda: _rallies(repo, sid)[0].payload["winner"] == "P2")
        assert len(_rallies(repo, sid)) == n  # applied in place: no re-analysis, no duplicates
        assert len(FakeSession.instances) == 1
        assert svc.runners[sid].is_alive()
    finally:
        svc.shutdown()


def test_restart_reattaches_to_a_finished_analysis(env: Any) -> None:
    settings, repo, sid = env
    svc = EngineService(repo, LocalBus(), settings)
    svc.dispatch({"cmd": "start", "session_id": sid})
    _wait(lambda: _analysed(repo, sid))
    svc.shutdown()
    seq_before = repo.events(sid).last_seq()
    first = _rallies(repo, sid)[0]
    n = len(_rallies(repo, sid))

    svc2 = EngineService(repo, LocalBus(), settings)  # a new process: no runner in memory
    try:
        svc2.dispatch({"cmd": "correct_winner", "session_id": sid, "rally_event_id": first.event_id, "winner": "P2"})
        _wait(lambda: _rallies(repo, sid)[0].payload["winner"] == "P2")
        assert len(_rallies(repo, sid)) == n
        assert repo.events(sid).last_seq() == seq_before + 1  # only the correction was appended
        assert FakeSession.instances[-1].restored is not None
        assert _analysed(repo, sid)
    finally:
        svc2.shutdown()


def test_reanalyse_keeps_manual_calibration_and_corrections(env: Any) -> None:
    settings, repo, sid = env
    svc = EngineService(repo, LocalBus(), settings)
    try:
        svc.dispatch({"cmd": "start", "session_id": sid})
        _wait(lambda: _analysed(repo, sid))
        second = _rallies(repo, sid)[1]
        svc.dispatch({"cmd": "calibrate", "session_id": sid, "points": {"near_left": [1, 2]}})
        svc.dispatch({"cmd": "correct_winner", "session_id": sid, "rally_event_id": second.event_id, "winner": "P2"})
        _wait(lambda: _rallies(repo, sid)[1].payload["winner"] == "P2")

        svc.dispatch({"cmd": "reanalyse", "session_id": sid})
        _wait(
            lambda: len(FakeSession.instances) == 2 and _analysed(repo, sid) and bool(FakeSession.instances[-1].carried)
        )
        cals = repo.events(sid).query(types=["calibration"])
        assert [c.payload["source"] for c in cals] == ["human"]  # auto calibration re-derived only if needed
        winners = [r.payload["winner"] for r in _rallies(repo, sid)]
        assert winners[:2] == ["P1", "P2"] and set(winners[2:]) <= {"P1"}
        s = repo.get(sid)
        assert s is not None and "carried_human" not in s.meta  # consumed
    finally:
        svc.shutdown()


def test_interrupted_analysis_restarts_cleanly(env: Any) -> None:
    settings, repo, sid = env
    svc = EngineService(repo, LocalBus(), settings)
    svc.dispatch({"cmd": "start", "session_id": sid})
    _wait(lambda: _analysed(repo, sid))
    first = _rallies(repo, sid)[0]
    svc.dispatch({"cmd": "correct_winner", "session_id": sid, "rally_event_id": first.event_id, "winner": "P2"})
    _wait(lambda: _rallies(repo, sid)[0].payload["winner"] == "P2")
    svc.shutdown()
    repo.set_status(sid, SessionStatus.ANALYSING, "Analysing")  # the process died mid-analysis

    svc2 = EngineService(repo, LocalBus(), settings)
    try:
        svc2.dispatch({"cmd": "start", "session_id": sid})
        _wait(lambda: _analysed(repo, sid) and bool(FakeSession.instances[-1].carried))
        winners = [r.payload["winner"] for r in _rallies(repo, sid)]
        assert winners[0] == "P2" and set(winners[1:]) == {"P1"}
        assert len(winners) == len({r.frame_start for r in _rallies(repo, sid)})  # no duplicates
    finally:
        svc2.shutdown()
