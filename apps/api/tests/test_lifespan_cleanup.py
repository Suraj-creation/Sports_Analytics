"""Application resources close on abnormal lifespan exit, without a network server."""

import pytest

from bai_api.app import create_app
from bai_engine.bus import LocalBus
from bai_engine.store import SessionRepository


async def test_lifespan_exception_closes_repository_and_transport(settings, monkeypatch):
    bus = LocalBus()
    app = create_app(settings, bus=bus, start_engine=False)
    closed = []
    close = SessionRepository.close

    def close_repository(repo):
        closed.append("repo")
        close(repo)

    monkeypatch.setattr(SessionRepository, "close", close_repository)
    monkeypatch.setattr(bus, "close", lambda: closed.append("bus"))
    with pytest.raises(RuntimeError, match="controlled lifespan failure"):
        async with app.router.lifespan_context(app):
            raise RuntimeError("controlled lifespan failure")
    assert sorted(closed) == ["bus", "repo"]


async def test_transport_close_failure_still_closes_repository(settings, monkeypatch):
    bus = LocalBus()
    app = create_app(settings, bus=bus, start_engine=False)
    closed = []
    close = SessionRepository.close

    def close_repository(repo):
        closed.append("repo")
        close(repo)

    monkeypatch.setattr(SessionRepository, "close", close_repository)

    def fail_close():
        raise RuntimeError("controlled transport close failure")

    monkeypatch.setattr(bus, "close", fail_close)
    with pytest.raises(RuntimeError, match="controlled transport close failure"):
        async with app.router.lifespan_context(app):
            pass
    assert closed == ["repo"]


async def test_partial_engine_start_is_stopped_before_resources_close(settings, monkeypatch):
    from bai_engine.runtime import runner

    calls = []
    close = SessionRepository.close

    class PartialStart:
        def __init__(self, repo, bus, config):
            pass

        def start(self):
            calls.append("start")
            raise RuntimeError("controlled partial start")

        def shutdown(self):
            calls.append("stop")

    def close_repository(repo):
        calls.append("repo")
        close(repo)

    bus = LocalBus()
    monkeypatch.setattr(bus, "close", lambda: calls.append("bus"))
    monkeypatch.setattr(SessionRepository, "close", close_repository)
    monkeypatch.setattr(runner, "EngineService", PartialStart)
    app = create_app(settings, bus=bus)
    with pytest.raises(RuntimeError, match="controlled partial start"):
        async with app.router.lifespan_context(app):
            pytest.fail("A failed engine start must not yield a running application")
    assert calls == ["start", "stop", "bus", "repo"]


async def test_shutdown_timeout_keeps_resources_owned_by_active_writer(settings, monkeypatch):
    from bai_engine.runtime import runner

    calls = []
    close = SessionRepository.close

    class ActiveWriter:
        def __init__(self, repo, bus, config):
            pass

        def start(self):
            calls.append("start")

        def shutdown(self):
            calls.append("stop")
            raise TimeoutError("controlled active writer")

    def close_repository(repo):
        calls.append("repo")
        close(repo)

    bus = LocalBus()
    monkeypatch.setattr(bus, "close", lambda: calls.append("bus"))
    monkeypatch.setattr(SessionRepository, "close", close_repository)
    monkeypatch.setattr(runner, "EngineService", ActiveWriter)
    app = create_app(settings, bus=bus)
    try:
        with pytest.raises(TimeoutError, match="controlled active writer"):
            async with app.router.lifespan_context(app):
                pass
        assert calls == ["start", "stop"]
        assert app.state.repo.list() == []  # the writer's repository remains open
    finally:
        # This controlled fake has no actual writer; release its retained test handles.
        close(app.state.repo)
