"""Bound native OpenCV pools before the real command consumer can start work."""

import pytest
from pydantic import ValidationError

from bai_engine.bus import LocalBus
from bai_engine.config import Settings
from bai_engine.runtime import runner
from bai_engine.store import SessionRepository


@pytest.mark.parametrize("threads", [1, 2, 8])
def test_positive_opencv_thread_configuration_is_supported(threads):
    assert Settings(opencv_threads=threads, _env_file=None).opencv_threads == threads


@pytest.mark.parametrize("threads", [0, -1, 1.5, "invalid", float("nan"), float("inf")])
def test_invalid_opencv_thread_configuration_fails_before_engine_initialization(threads):
    with pytest.raises(ValidationError):
        Settings(opencv_threads=threads, _env_file=None)


@pytest.mark.parametrize("threads", [1, 3])
def test_native_pool_is_set_before_recovery_or_any_command_worker(tmp_path, monkeypatch, threads):
    models = tmp_path / "models"
    models.mkdir()
    (models / "manifest.yaml").write_text("version: 1\nmodels: {}\n")
    settings = Settings(data_dir=tmp_path / "data", models_dir=models, opencv_threads=threads, _env_file=None)
    repo, bus = SessionRepository(settings.data_dir), LocalBus()
    service = runner.EngineService(repo, bus, settings)
    events = []
    monkeypatch.setattr(runner.cv2, "setNumThreads", lambda value: events.append(("native", value)))
    mark_interrupted, start_thread = repo.mark_interrupted, service._thread.start

    def recover():
        assert events == [("native", threads)]
        events.append(("recovery", None))
        return mark_interrupted()

    def start():
        assert events == [("native", threads), ("recovery", None)]
        events.append(("worker", None))
        start_thread()

    monkeypatch.setattr(repo, "mark_interrupted", recover)
    monkeypatch.setattr(service._thread, "start", start)
    try:
        service.start()
        assert events == [("native", threads), ("recovery", None), ("worker", None)]
        assert service._thread.is_alive()
    finally:
        service.shutdown(timeout=2)
        bus.close()
        repo.close()
