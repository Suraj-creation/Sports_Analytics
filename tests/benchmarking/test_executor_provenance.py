import subprocess
from pathlib import Path

import pytest

from research.next_evidence_provenance import (
    executor_sources_unchanged,
    snapshot_executor,
    trace_epoch_reset_indices,
)


def idle():
    return {
        "state": "idle",
        "start": None,
        "closed": None,
        "moving_run": 0,
        "invisible_run": 0,
        "last_contact": None,
    }


def test_epoch_replacement_uses_trace_state_at_arbitrary_frames():
    rows = [
        {"call": "flush", "frame": 41, "after": {**idle(), "invisible_run": 12}},
        {"call": "discontinuity", "frame": 42, "before": idle()},
        {"call": "flush", "frame": 480, "after": {**idle(), "last_contact": 470}},
        {"call": "step", "frame": 481, "before": idle()},
        {"call": "flush", "frame": 999},
    ]
    assert trace_epoch_reset_indices(rows) == {0, 2}


def test_nonterminal_flush_without_replacement_preserves_carried_state():
    rows = [
        {"call": "flush", "frame": 119, "after": {**idle(), "invisible_run": 12}},
        {"call": "step", "frame": 120, "before": {**idle(), "invisible_run": 12}},
    ]
    assert trace_epoch_reset_indices(rows) == set()


def test_ambiguous_epoch_is_rejected_instead_of_guessed():
    with pytest.raises(ValueError, match="state snapshots"):
        trace_epoch_reset_indices([{"call": "flush", "frame": 119}, {"call": "step", "frame": 120}])


def test_epoch_cannot_hide_decreasing_frame_identity():
    with pytest.raises(ValueError, match="decreases"):
        trace_epoch_reset_indices(
            [{"call": "flush", "frame": 119, "after": idle()}, {"call": "step", "frame": 118, "before": idle()}]
        )


def test_equal_idle_snapshots_do_not_prove_a_provider_reset():
    rows = [
        {"call": "flush", "frame": 41, "after": idle()},
        {"call": "step", "frame": 42, "before": idle()},
    ]
    assert trace_epoch_reset_indices(rows) == set()


def test_unexplained_state_change_is_rejected():
    rows = [
        {"call": "flush", "frame": 41, "after": idle()},
        {"call": "step", "frame": 42, "before": {**idle(), "last_contact": 40}},
    ]
    with pytest.raises(ValueError, match="unexplained"):
        trace_epoch_reset_indices(rows)


def test_recorded_format_events_establish_replacement_with_equal_idle_snapshots():
    rows = [
        {"call": "flush", "frame": 41, "after": idle()},
        {"call": "step", "frame": 42, "before": idle()},
        {"call": "flush", "frame": 480, "after": idle()},
        {"call": "step", "frame": 481, "before": idle()},
    ]
    events = [
        {"event_id": "a", "type": "format_decision", "frame_start": 42, "status": "confirmed"},
        {"event_id": "b", "type": "format_decision", "frame_start": 481, "status": "confirmed"},
    ]
    assert trace_epoch_reset_indices(rows, format_events=events) == {0, 2}
    assert trace_epoch_reset_indices(rows, format_events=[]) == set()


def test_format_event_without_own_trace_flush_is_rejected():
    events = [{"event_id": "a", "type": "format_decision", "frame_start": 42, "status": "confirmed"}]
    with pytest.raises(ValueError, match="unique trace flush"):
        trace_epoch_reset_indices([{"call": "step", "frame": 42, "before": idle()}], format_events=events)


def test_retracted_format_decision_cannot_force_an_epoch():
    events = [
        {"event_id": "a", "type": "format_decision", "frame_start": 42, "status": "confirmed"},
        {"event_id": "b", "type": "format_decision", "frame_start": 42, "status": "retracted", "supersedes": "a"},
    ]
    assert trace_epoch_reset_indices([], format_events=events) == set()


def test_executor_snapshots_dirty_and_untracked_bytes_independently_of_trace(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=repo)

    git("init", "-q")
    harness = repo / "harness.py"
    harness.write_text("version = 1\n")
    git("add", "harness.py")
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "initial")
    harness.write_text("version = 2\n")
    helper = repo / "untracked.py"
    helper.write_text("support = True\n")
    output = tmp_path / "experiment"
    output.mkdir()
    record = snapshot_executor(repo, output, [harness, helper], harness)
    assert record["git_commit"] == git("rev-parse", "HEAD").decode().strip()
    assert record["source_dirty"]
    assert (output / "executor_source/harness.py").read_bytes() == harness.read_bytes()
    assert (output / "executor_source/untracked.py").read_bytes() == helper.read_bytes()
    assert b"version = 2" in (output / "executor.diff").read_bytes()
    assert executor_sources_unchanged(repo, record)
    helper.write_text("support = False\n")
    assert not executor_sources_unchanged(repo, record)
    assert (output / "executor_source/untracked.py").read_text() == "support = True\n"


def test_executor_refuses_overwriting_source_snapshot(tmp_path):
    (tmp_path / "executor_source").mkdir()
    with pytest.raises(FileExistsError):
        snapshot_executor(tmp_path, tmp_path, [], Path(__file__))
