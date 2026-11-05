"""Exercise the existing command service, without model/media side effects."""

import threading

from bai_engine.bus import LocalBus
from bai_engine.config import Settings
from bai_engine.runtime import runner as runtime
from bai_engine.schema import Session, Source, SourceKind
from bai_engine.store import SessionRepository


def test_existing_service_survives_task_fault_retries_and_cancels(tmp_path, monkeypatch):
    repo = SessionRepository(tmp_path / "data")
    session = repo.save(Session(title="Contract", source=Source(kind=SourceKind.UPLOAD, uri="unused")))
    bus = LocalBus()
    failed, started, cancelled = threading.Event(), threading.Event(), threading.Event()
    attempts = []

    class ModelFreeRunner:
        def __init__(self, *args, **kwargs):
            attempts.append(kwargs.get("attach"))
            if len(attempts) == 1:
                failed.set()
                raise RuntimeError("controlled task initialization failure")
            self.running = False

        def start(self):
            self.running = True
            started.set()

        def is_alive(self):
            return self.running

        def stop(self):
            self.running = False
            cancelled.set()

        def join(self, timeout=None):
            assert not self.running

    monkeypatch.setattr(runtime, "SessionRunner", ModelFreeRunner)
    models = tmp_path / "models"
    models.mkdir()
    (models / "manifest.yaml").write_text("version: 1\nmodels: {}\n")
    service = runtime.EngineService(repo, bus, Settings(data_dir=tmp_path / "data", models_dir=tmp_path / "models"))
    service.start()
    try:
        bus.send_command({"cmd": "start", "session_id": session.session_id})
        assert failed.wait(2), "the controlled failure must actually execute"
        bus.send_command({"cmd": "start", "session_id": session.session_id})
        assert started.wait(2), "a failed task must not kill the real command consumer"
        bus.send_command({"cmd": "stop", "session_id": session.session_id})
        assert cancelled.wait(2), "cancellation must reach the runner through the actual queue"
        assert attempts == [False, False]
    finally:
        service.shutdown(timeout=2)
        bus.close()
        repo.close()
