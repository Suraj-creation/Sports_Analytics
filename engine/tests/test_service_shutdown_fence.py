"""Shutdown must fence commands and writers before the API closes their stores."""

import threading

import pytest
import yaml

from bai_engine.bus import LocalBus
from bai_engine.config import Settings
from bai_engine.runtime.runner import EngineService
from bai_engine.schema import Session, Source, SourceKind
from bai_engine.store import SessionRepository


def service(tmp_path, bus):
    models = tmp_path / "models"
    models.mkdir()
    (models / "manifest.yaml").write_text(yaml.safe_dump({"models": {}}))
    repo = SessionRepository(tmp_path / "data")
    settings = Settings(data_dir=repo.data_dir, models_dir=models, _env_file=None)
    return EngineService(repo, bus, settings), repo


def test_shutdown_waits_for_command_consumer_before_stores_can_close(tmp_path):
    entered, release = threading.Event(), threading.Event()

    class HeldBus(LocalBus):
        def next_command(self, timeout=None):
            entered.set()
            assert release.wait(5)
            return None

    engine, repo = service(tmp_path, HeldBus())
    engine.start()
    try:
        assert entered.wait(2)
        with pytest.raises(TimeoutError, match="command"):
            engine.shutdown(timeout=0.01)
        assert engine._thread.is_alive()
    finally:
        release.set()
        engine._thread.join(2)
        engine.shutdown()
        repo.close()


def test_a_queued_start_cannot_launch_after_shutdown_begins(tmp_path, monkeypatch):
    entered, release = threading.Event(), threading.Event()
    started = []

    class HeldBus(LocalBus):
        def next_command(self, timeout=None):
            entered.set()
            assert release.wait(5)
            return {"cmd": "start", "session_id": session.session_id}

    engine, repo = service(tmp_path, HeldBus())
    session = repo.save(Session(title="Stopped", source=Source(kind=SourceKind.UPLOAD, uri="unused")))
    monkeypatch.setattr(engine, "_prepare_start", lambda sid: started.append(sid))
    engine.start()
    try:
        assert entered.wait(2)
        engine._stop.set()
        release.set()
        engine.shutdown()
        assert not started
        assert not engine._thread.is_alive()
        # Directly dispatched commands must respect the same shutdown fence.
        engine.dispatch({"cmd": "start", "session_id": session.session_id})
        assert not started and not engine.runners
    finally:
        release.set()
        engine._thread.join(2)
        engine.shutdown()
        repo.close()


def test_shutdown_reports_a_writer_that_does_not_relinquish_ownership(tmp_path):
    release, stopped = threading.Event(), threading.Event()

    class HeldWriter(threading.Thread):
        def run(self):
            assert release.wait(5)

        def stop(self):
            stopped.set()

    engine, repo = service(tmp_path, LocalBus())
    writer = HeldWriter()
    writer.start()
    engine.runners["controlled"] = writer
    try:
        with pytest.raises(TimeoutError, match="writer"):
            engine.shutdown(timeout=0.01)
        assert stopped.is_set() and writer.is_alive()
    finally:
        release.set()
        writer.join(2)
        engine.shutdown()
        repo.close()


def test_shutdown_between_command_reattach_and_recursive_start_is_safe(tmp_path, monkeypatch):
    engine, repo = service(tmp_path, LocalBus())
    dispatch = engine.dispatch

    def stop_before_recursive_start(command):
        if command.get("cmd") == "start":
            engine._stop.set()
        return dispatch(command)

    monkeypatch.setattr(engine, "dispatch", stop_before_recursive_start)
    try:
        dispatch({"cmd": "seek", "session_id": "controlled"})
        assert engine._stop.is_set() and not engine.runners
    finally:
        engine.shutdown()
        repo.close()


def test_command_for_a_missing_session_does_not_index_an_absent_runner(tmp_path):
    engine, repo = service(tmp_path, LocalBus())
    try:
        engine.dispatch({"cmd": "seek", "session_id": "missing"})
        assert not engine.runners
    finally:
        engine.shutdown()
        repo.close()
