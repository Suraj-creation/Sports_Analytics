"""Progress/capability metadata survives disconnection and analysis reset."""

from pathlib import Path
from threading import Event as ThreadEvent
from threading import Thread
from types import SimpleNamespace

from bai_engine.bus import LocalBus
from bai_engine.config import Settings
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.runtime.runner import SessionRunner
from bai_engine.schema import Event, Provenance, Session, Source, SourceKind
from bai_engine.store import SessionRepository


def test_status_persists_runtime_capabilities_for_reconnected_clients(tmp_path: Path) -> None:
    repo = SessionRepository(tmp_path / "data")
    try:
        session = repo.save(
            Session(
                title="Audit",
                source=Source(kind=SourceKind.UPLOAD, uri="x.mp4"),
                meta={"analysis_revision": 3},
                frontier_frame=29,
                analysed_frames=30,
            )
        )
        settings = Settings(data_dir=repo.data_dir, _env_file=None)
        bus = LocalBus()
        messages = []
        bus.publish = lambda channel, msg: messages.append(msg)
        runner = SessionRunner(session.session_id, repo, bus, settings, ModelRegistry(settings.models_dir))
        capabilities = {"stroke": {"status": "heuristic", "active_model": "stroke_rules_v0"}}
        runner.sport = SimpleNamespace(
            degraded=lambda: [{"stage": "pose", "reason": "unavailable"}], capabilities=lambda: capabilities
        )
        runner._status()
        assert messages[-1]["analysis_revision"] == 3
        assert messages[-1]["analysed_frames"] == 30
        assert messages[-1]["capabilities"] == capabilities
        assert repo.get(session.session_id).meta["degraded"][0]["stage"] == "pose"
        runner.sport = None  # a new connection need not instantiate all neural models
        runner._status()
        assert messages[-1]["capabilities"] == capabilities
        runner._emit_events([])
        assert messages[-1]["analysis_revision"] == 3
    finally:
        repo.close()


def test_analysis_snapshot_prevents_reset_closing_an_active_reader(tmp_path: Path) -> None:
    repo = SessionRepository(tmp_path / "data")
    session = repo.save(Session(title="Audit", source=Source(kind=SourceKind.UPLOAD, uri="x.mp4")))
    store = repo.events(session.session_id)
    store.append(
        Event(
            session_id=session.session_id,
            type="rally_start",
            frame_start=0,
            frame_end=0,
            pts_us=0,
            provenance=Provenance(model="test"),
        )
    )
    entered, finished = ThreadEvent(), ThreadEvent()
    errors = []

    def reset() -> None:
        entered.set()
        try:
            repo.reset_analysis(session.session_id)
        except Exception as exc:
            errors.append(exc)
        finally:
            finished.set()

    try:
        with repo.analysis_snapshot(session.session_id) as (snapshot, events, _):
            worker = Thread(target=reset)
            worker.start()
            assert entered.wait(2)
            assert not finished.wait(0.05)
            assert events.last_seq() == 1
            assert snapshot.meta.get("analysis_revision", 0) == 0
        worker.join(5)
        assert finished.is_set() and not errors
        with repo.analysis_snapshot(session.session_id) as (snapshot, events, _):
            assert snapshot.meta["analysis_revision"] == 1
            assert events.last_seq() == 0
    finally:
        repo.close()
