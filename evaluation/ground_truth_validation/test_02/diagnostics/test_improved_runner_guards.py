"""Read-only guard/comparison tests; never invoke the fresh runner or inference."""

from __future__ import annotations

import copy
import json

import pytest

from evaluation.ground_truth_validation.orchestration import run_test02_improved as runner


def references():
    metrics = {
        "matching_policy": {"minimum_iou": 0.5},
        "detection": {"precision": 1.0, "recall": 1.0},
        "boundary_and_duration_errors": {"start": {"mae": 1.0}},
        "unavailable": None,
        "flag": False,
        "missed_gt_rallies": [],
    }
    return {
        "interval_reference_comparisons": {
            name: {"role": "synthetic_reference", "metrics": copy.deepcopy(metrics)} for name in runner.REFERENCE_NAMES
        }
    }


def test_before_after_uses_saved_metrics_and_preserves_unavailable():
    before, after = references(), references()
    name = "Test2_Full.csv"
    after["interval_reference_comparisons"][name]["metrics"]["boundary_and_duration_errors"]["start"]["mae"] = 0.5
    comparison = runner.compare_saved_references(before, after)
    assert comparison[name]["numeric_deltas"]["boundary_and_duration_errors.start.mae"] == -0.5
    assert comparison[name]["baseline"]["unavailable"] is None
    assert "flag" not in comparison[name]["numeric_deltas"]
    assert comparison[name]["metrics_equal"] is False


def test_test1_or_partial_reference_populations_are_rejected():
    before, after = references(), references()
    after["interval_reference_comparisons"]["Test1_Full2.csv"] = after["interval_reference_comparisons"].pop(
        "Test2_Full.csv"
    )
    with pytest.raises(ValueError, match="exactly three Test2"):
        runner.compare_saved_references(before, after)


@pytest.mark.parametrize("field", ["role", "matching_policy"])
def test_reference_semantics_cannot_change_to_improve_scores(field):
    before, after = references(), references()
    item = after["interval_reference_comparisons"]["Test2_Full.csv"]
    if field == "role":
        item["role"] = "new-interpretation"
    else:
        item["metrics"]["matching_policy"] = {"minimum_iou": 0.1}
    with pytest.raises(ValueError, match="interpretation/matching"):
        runner.compare_saved_references(before, after)


def test_existing_output_is_refused_without_creating_fix_or_log(tmp_path, monkeypatch):
    art = tmp_path / "already-complete"
    art.mkdir()
    marker = art / "receipt.json"
    marker.write_text("immutable")
    monkeypatch.setattr(runner, "ART", art)
    monkeypatch.setattr(runner, "REPORT", tmp_path / "new-report")
    monkeypatch.setattr(runner, "TEST", tmp_path / "test")
    with pytest.raises(ValueError, match="must not exist"):
        runner.preflight()
    assert marker.read_text() == "immutable"
    assert list(art.iterdir()) == [marker]


def test_failed_regressions_do_not_allocate_artifact_directory(tmp_path, monkeypatch):
    fix = tmp_path / "fix.json"
    fix.write_text(json.dumps({"regressions_passed": False, "baseline_protected": True}))
    art = tmp_path / "new-artifacts"
    monkeypatch.setattr(runner, "FIX", fix)
    monkeypatch.setattr(runner, "ART", art)
    monkeypatch.setattr(runner, "REPORT", tmp_path / "new-report")
    monkeypatch.setattr(runner, "TEST", tmp_path / "test")
    with pytest.raises(ValueError, match="passed regressions"):
        runner.preflight()
    assert not art.exists()


def test_failure_handler_never_writes_into_a_previous_run(tmp_path, monkeypatch):
    art = tmp_path / "old-run"
    art.mkdir()
    monkeypatch.setattr(runner, "ART", art)
    monkeypatch.setattr(runner, "OWNED_ART", False)
    monkeypatch.setattr(runner, "state", lambda *args, **kwargs: None)
    runner.record_failure(ValueError("existing output refused"))
    assert not list(art.iterdir())


def test_failure_handler_preserves_this_runs_partial_evidence(tmp_path, monkeypatch):
    art = tmp_path / "owned-run"
    art.mkdir()
    marker = art / "partial.log"
    marker.write_text("original failure evidence")
    monkeypatch.setattr(runner, "ART", art)
    monkeypatch.setattr(runner, "OWNED_ART", True)
    monkeypatch.setattr(runner, "state", lambda *args, **kwargs: None)
    runner.record_failure(ValueError("probe"))
    assert marker.read_text() == "original failure evidence"
    assert json.loads((art / "failure.json").read_text())["media_deleted"] is False


def test_same_models_in_different_staging_directories_compare_equal():
    before = {
        "models_verified_during_analysis": {
            "registry_artifacts": {"model": {"sha256": "checkpoint", "staged_path": "before"}}
        }
    }
    after = copy.deepcopy(before)
    after["models_verified_during_analysis"]["registry_artifacts"]["model"]["staged_path"] = "after"
    assert runner.model_identity(before) == runner.model_identity(after)
    after["models_verified_during_analysis"]["registry_artifacts"]["model"]["sha256"] = "different-checkpoint"
    assert runner.model_identity(before) != runner.model_identity(after)
