"""Session-owned components close after residents, stops and failed analysis."""

from types import SimpleNamespace

import pytest
from test_independent_pipeline_plugin import _MachinePlugin, _runner

from bai_engine.runtime.runner import _SessionGoneError


@pytest.mark.parametrize("exit_path", ["normal", "failure", "gone", "stop"])
def test_runner_closes_its_pipeline_after_all_exit_paths(tmp_path, monkeypatch, exit_path):
    runner, repo, _ = _runner(tmp_path, monkeypatch, _MachinePlugin(), "mean")
    closed = []
    owned = SimpleNamespace(close=lambda: closed.append(True), degraded=lambda: [])
    monkeypatch.setattr(runner, "_ensure_media", lambda: None)

    def analyse():
        runner.sport = owned
        if exit_path == "failure":
            raise RuntimeError("controlled analysis failure")
        if exit_path == "gone":
            raise _SessionGoneError("controlled removed session")
        if exit_path == "stop":
            runner.shared.stop.set()

    def resident():
        assert not closed, "A resident pipeline closed before command handling finished"

    monkeypatch.setattr(runner, "_analyse", analyse)
    monkeypatch.setattr(runner, "_resident", resident)
    try:
        runner.run()
        assert closed == [True]
    finally:
        repo.close()


def test_legacy_pipeline_without_close_keeps_working(tmp_path, monkeypatch):
    runner, repo, _ = _runner(tmp_path, monkeypatch, _MachinePlugin(), "mean")
    monkeypatch.setattr(runner, "_ensure_media", lambda: None)
    monkeypatch.setattr(runner, "_analyse", lambda: setattr(runner, "sport", SimpleNamespace()))
    monkeypatch.setattr(runner, "_resident", lambda: None)
    try:
        runner.run()
    finally:
        repo.close()


def test_close_failure_does_not_replace_the_recorded_analysis_failure(tmp_path, monkeypatch):
    runner, repo, _ = _runner(tmp_path, monkeypatch, _MachinePlugin(), "mean")
    closed = []
    monkeypatch.setattr(runner, "_ensure_media", lambda: None)

    def close():
        closed.append(True)
        raise RuntimeError("controlled close failure")

    def analyse():
        runner.sport = SimpleNamespace(close=close, degraded=lambda: [])
        raise RuntimeError("original analysis failure")

    monkeypatch.setattr(runner, "_analyse", analyse)
    try:
        runner.run()
        assert closed == [True]
        assert "original analysis failure" in repo.get(runner.session_id).status_detail
    finally:
        repo.close()
