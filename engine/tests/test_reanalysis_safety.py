"""Reanalysis cannot destroy the only results or race a still-running writer."""

from __future__ import annotations

import json
from pathlib import Path
from threading import Event as ThreadEvent
from typing import Any

import pytest

from bai_engine.bus import LocalBus
from bai_engine.config import Settings
from bai_engine.runtime.runner import EngineService
from bai_engine.schema import Event, EventStatus, Provenance, Session, SessionStatus, Source, SourceKind, StateSnapshot
from bai_engine.store import EventStore, SessionRepository


def _session(tmp_path: Path) -> tuple[SessionRepository, str]:
    repo = SessionRepository(tmp_path / "data")
    session = repo.save(
        Session(
            title="Review me",
            source=Source(kind=SourceKind.UPLOAD, uri="source.mp4"),
            status=SessionStatus.ANALYSED,
            meta={"match_start": 12, "review_note": "Human reviewed"},
        )
    )
    repo.events(session.session_id).append(
        Event(
            session_id=session.session_id,
            type="rally_end",
            frame_start=0,
            frame_end=12,
            pts_us=0,
            status=EventStatus.HUMAN_VERIFIED,
            provenance=Provenance(model="human"),
            payload={"winner": "P2"},
        )
    )
    return repo, session.session_id


def test_reset_saves_consistent_events_states_tracks_exports_and_metadata(tmp_path: Path) -> None:
    repo, sid = _session(tmp_path)
    store = repo.events(sid)
    store.put_state(StateSnapshot(session_id=sid, frame_idx=12, state={"score": {"P1": 0, "P2": 1}}))
    store.set_meta("frontier", "12")
    paths = repo.paths(sid)
    paths.tracks.mkdir()
    (paths.tracks / "sample.parquet").write_bytes(b"track-result")
    paths.exports.mkdir()
    (paths.exports / "report.pdf").write_bytes(b"report-result")

    repo.reset_analysis(sid)

    backups = list((repo.data_dir / "backups" / sid).glob("*"))
    assert len(backups) == 1 and not backups[0].name.endswith(".incomplete")
    backup = backups[0]
    with EventStore(backup / "events.sqlite", sid) as saved:
        assert saved.query()[0].payload["winner"] == "P2"
        assert saved.query()[0].status is EventStatus.HUMAN_VERIFIED
        assert saved.state_at(12).state["score"] == {"P1": 0, "P2": 1}
        assert saved.get_meta("frontier") == "12"
    assert (backup / "tracks" / "sample.parquet").read_bytes() == b"track-result"
    assert (backup / "exports" / "report.pdf").read_bytes() == b"report-result"
    assert json.loads((backup / "session.json").read_text())["meta"]["match_start"] == 12
    assert repo.events(sid).last_seq() == 0
    assert not paths.tracks.exists()
    assert (paths.exports / "report.pdf").exists()
    repo.close()


def test_failed_backup_preserves_original_results(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo, sid = _session(tmp_path)

    def fail(*_: Any) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(EventStore, "backup_to", fail, raising=False)
    with pytest.raises(OSError, match="disk full"):
        repo.reset_analysis(sid)
    assert repo.events(sid).last_seq() == 1
    assert repo.get(sid).status is SessionStatus.ANALYSED
    repo.close()


class _ControlledRunner:
    def __init__(self, *, stubborn: bool = False) -> None:
        self.alive = True
        self.stubborn = stubborn
        self.stops = 0

    def is_alive(self) -> bool:
        return self.alive

    def stop(self) -> None:
        self.stops += 1

    def join(self, timeout: float) -> None:
        if not self.stubborn:
            self.alive = False

    def start(self) -> None:
        self.alive = True


def test_reanalysis_refuses_reset_when_old_writer_does_not_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import bai_engine.runtime.runner as runtime

    repo, sid = _session(tmp_path)
    svc = EngineService(repo, LocalBus(), Settings(data_dir=repo.data_dir, _env_file=None))
    runner = _ControlledRunner(stubborn=True)
    svc.runners[sid] = runner  # type: ignore[assignment]
    monkeypatch.setattr(runtime, "SessionRunner", lambda *args, **kwargs: _ControlledRunner())
    with pytest.raises(RuntimeError, match="stop"):
        svc.dispatch({"cmd": "reanalyse", "session_id": sid})
    assert repo.events(sid).last_seq() == 1
    assert not (repo.data_dir / "backups").exists()
    assert runner.stops == 1
    repo.close()


def test_conflicting_reanalysis_coalesces_until_completion(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import bai_engine.runtime.runner as runtime

    repo, sid = _session(tmp_path)
    svc = EngineService(repo, LocalBus(), Settings(data_dir=repo.data_dir, _env_file=None))
    started: list[_ControlledRunner] = []

    def create(*_: Any, **__: Any) -> _ControlledRunner:
        runner = _ControlledRunner()
        started.append(runner)
        return runner

    monkeypatch.setattr(runtime, "SessionRunner", create)
    svc.dispatch({"cmd": "reanalyse", "session_id": sid})
    svc.dispatch({"cmd": "reanalyse", "session_id": sid})
    assert len(started) == 1 and started[0].stops == 0
    assert repo.get(sid).status is SessionStatus.ANALYSING
    assert len(list((repo.data_dir / "backups" / sid).glob("*"))) == 1
    # A new user request is allowed after the previous analysis completed.
    repo.set_status(sid, SessionStatus.ANALYSED)
    svc.dispatch({"cmd": "reanalyse", "session_id": sid})
    assert len(started) == 2 and started[0].stops == 1
    assert len(list((repo.data_dir / "backups" / sid).glob("*"))) == 2
    repo.close()


def test_command_loop_reports_backup_rejection_without_invalidating_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, sid = _session(tmp_path)
    bus = LocalBus()
    svc = EngineService(repo, bus, Settings(data_dir=repo.data_dir, _env_file=None))
    updated = ThreadEvent()
    messages: list[dict[str, Any]] = []

    def fail(*_: Any) -> Path:
        raise OSError("disk unavailable at /private/server/location")

    def publish(channel: str, message: dict[str, Any]) -> None:
        if message.get("type") == "status":
            messages.append(message)
            updated.set()

    monkeypatch.setattr(repo, "backup_analysis", fail)
    monkeypatch.setattr(bus, "publish", publish)
    svc.start()
    try:
        bus.send_command({"cmd": "reanalyse", "session_id": sid})
        assert updated.wait(timeout=3), "The rejected command did not publish status feedback"
        session = repo.get(sid)
        assert session.status is SessionStatus.ANALYSED
        assert (
            session.status_detail == "Reanalysis could not start; existing results were preserved. Check server logs."
        )
        assert "/private" not in session.status_detail
        assert messages[-1]["status"] == "analysed"
        assert messages[-1]["detail"] == session.status_detail
        assert repo.events(sid).last_seq() == 1
    finally:
        svc.shutdown()
        svc._thread.join(timeout=2)
        repo.close()
