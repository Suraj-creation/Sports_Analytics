"""No inference: protect controlled semantic regression from invalid evidence."""

from __future__ import annotations

import copy
import json

import pytest

from evaluation.ground_truth_validation.orchestration import run_controlled_semantic_regression as runner


@pytest.fixture
def applied(tmp_path):
    current = {
        runner.ENGINE: "new-engine",
        runner.ADMISSION: "new-helper",
        "sports/badminton/src/bai_badminton/perception/racket.py": "unchanged",
    }
    recorded = {runner.ENGINE: "old-engine", "sports/badminton/src/bai_badminton/perception/racket.py": "unchanged"}
    receipt = {
        "schema": "test2-applied-correctness-fix:v1",
        "fix": "racket_anatomical_alias_abstention_v1",
        "regressions_passed": True,
        "baseline_protected": True,
        "perception_models_profile_unchanged": True,
        "production_files": {
            str(tmp_path / runner.ENGINE): {"before_sha256": "old-engine", "after_sha256": "new-engine"},
            str(tmp_path / runner.ADMISSION): {"before_sha256": None, "after_sha256": "new-helper"},
        },
    }
    return receipt, current, recorded, tmp_path


def test_exact_two_file_engine_intervention_is_explicit(applied):
    receipt, current, recorded, root = applied
    changes = runner.validate_applied_fix(receipt, current, recorded, root=root)
    assert set(changes) == runner.ALLOWED_CHANGES
    assert changes[runner.ADMISSION]["recorded"] is None


@pytest.mark.parametrize(
    "path",
    [
        "engine/src/bai_engine/runtime/runner.py",
        "sports/badminton/src/bai_badminton/perception/racket.py",
        "sports/badminton/src/bai_badminton/events/contact.py",
    ],
)
def test_additional_core_change_refuses_fixed_perception_claim(applied, path):
    receipt, current, recorded, root = applied
    current[path] = "changed-without-authorization"
    with pytest.raises(ValueError, match=r"exact engine\.py"):
        runner.validate_applied_fix(receipt, current, recorded, root=root)


@pytest.mark.parametrize("field", ["regressions_passed", "baseline_protected", "perception_models_profile_unchanged"])
def test_unvalidated_fix_receipt_rejected(applied, field):
    receipt, current, recorded, root = applied
    receipt[field] = False
    with pytest.raises(ValueError, match="requires true"):
        runner.validate_applied_fix(receipt, current, recorded, root=root)


def test_incorrect_after_hash_rejected(applied):
    receipt, current, recorded, root = applied
    receipt["production_files"][str(root / runner.ENGINE)]["after_sha256"] = "different"
    with pytest.raises(ValueError, match="source hashes"):
        runner.validate_applied_fix(receipt, current, recorded, root=root)


def test_missing_core_delta_rejected(applied):
    receipt, current, recorded, root = applied
    current[runner.ENGINE] = recorded[runner.ENGINE]
    with pytest.raises(ValueError, match=r"exact engine\.py"):
        runner.validate_applied_fix(receipt, current, recorded, root=root)


@pytest.fixture
def proof(tmp_path):
    n = runner.CONTRACTS[1]["frames"]
    return {
        "schema": runner.REPLAY_SCHEMA,
        "baseline_parity": True,
        "geometry_bracket": False,
        "contact_motion_reliability": False,
        "source_intervention": None,
        "source_report_sha256": "report",
        "cache_sha256": {"seg0": "original-cache"},
        "session_id": "UPLOADTEST1",
        "source_run": str(tmp_path),
        "frames": n,
        "trace_step_count": n,
        "trace_ranges_telemetry_only": [[0, n]],
        "harness_source_sha256": {"helper": "hash"},
    }, tmp_path


def check_proof(proof, path):
    return runner.require_proof_contract(
        proof, test=1, report_sha="report", caches={"seg0": "original-cache"}, run=path
    )


def test_original_strict_proof_contract_accepts_same_run_and_cache(proof):
    value, path = proof
    check_proof(value, path)


@pytest.mark.parametrize(
    ("key", "changed"),
    [
        ("baseline_parity", False),
        ("source_report_sha256", "foreign-report"),
        ("cache_sha256", {"seg0": "foreign-cache"}),
        ("session_id", "UPLOADTEST2"),
        ("frames", 29296),
        ("trace_step_count", 100),
        ("trace_ranges_telemetry_only", [[0, 100]]),
        ("source_intervention", {"not": "strict baseline"}),
    ],
)
def test_incomplete_or_foreign_baseline_proof_refused(proof, key, changed):
    value, path = proof
    value = copy.deepcopy(value)
    value[key] = changed
    with pytest.raises(ValueError, match="strict full-timeline"):
        check_proof(value, path)


def test_original_profile_or_asset_mutation_refused(tmp_path):
    asset = tmp_path / "profile.yaml"
    asset.write_text("original")
    hashes = {str(asset): runner.sha(asset)}
    asset.write_text("changed")
    with pytest.raises(ValueError, match="Protected original input changed"):
        runner.frozen_files(hashes)


def test_applied_fix_requires_retained_test_evidence():
    with pytest.raises(ValueError, match="retained regression"):
        runner.fix_test_logs({"test_logs": []})


def test_regression_log_hash_is_verified(tmp_path):
    log = tmp_path / "tests.log"
    log.write_text("23 passed")
    declared = {"test_logs": [{"path": str(log), "sha256": runner.sha(log)}]}
    assert runner.fix_test_logs(declared) == {str(log): runner.sha(log)}
    log.write_text("modified after claimed pass")
    with pytest.raises(ValueError, match="log hash"):
        runner.fix_test_logs(declared)


@pytest.mark.parametrize(
    "records",
    [
        [{"call": "step", "frame": 0, "available_through": 1}],
        [{"call": "step", "frame": 0, "available_through": 1}, {"call": "step", "frame": 0, "available_through": 1}],
        [{"call": "step", "frame": 0, "available_through": 3}, {"call": "step", "frame": 1, "available_through": 1}],
    ],
)
def test_actual_trace_missing_duplicate_or_future_frontier_rejected(tmp_path, records):
    trace = tmp_path / "trace.jsonl"
    trace.write_text("".join(json.dumps(x) + "\n" for x in records))
    with pytest.raises(ValueError, match="trace"):
        runner.verify_trace(trace, 2)


def test_full_trace_contains_every_frame_in_order(tmp_path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text("".join(json.dumps({"call": "step", "frame": f, "available_through": 1}) + "\n" for f in range(2)))
    assert runner.verify_trace(trace, 2) == 2


def schedule_trace(tmp_path, name, *, contact_state="idle", terminal_state="idle"):
    rows = []
    for frame in range(6):
        frontier = 2 if frame < 3 else 5
        rows.append(
            {
                "call": "step",
                "frame": frame,
                "available_through": frontier,
                "before": {"state": "idle"},
                "after": {"state": "idle"},
            }
        )
        if frame == 2:
            rows.append(
                {
                    "call": "on_contact_evidence",
                    "frame": frame,
                    "available_through": frontier,
                    "before": {"state": "idle"},
                    "after": {"state": contact_state},
                }
            )
    rows.append(
        {
            "call": "flush",
            "frame": 5,
            "available_through": 5,
            "before": {"state": "idle"},
            "after": {"state": terminal_state},
        }
    )
    path = tmp_path / name
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    return path


def test_contact_after_step_changes_next_chunk_driver(tmp_path):
    baseline = schedule_trace(tmp_path, "before.jsonl")
    candidate = schedule_trace(tmp_path, "after.jsonl", contact_state="in_play")
    result = runner.compare_schedule_feedback(baseline, candidate, [2, 5], 6)
    assert result["all_step_before_after_states_equal"] is True
    assert result["schedule_driver_equal"] is False
    assert result["differing_driver_frontiers"] == [2]
    assert result["fresh_inference_required_due_to_feedback_change"] is True


def test_nonidle_state_difference_does_not_change_binary_schedule(tmp_path):
    baseline = schedule_trace(tmp_path, "before.jsonl", contact_state="in_play")
    candidate = schedule_trace(tmp_path, "after.jsonl", contact_state="closed")
    result = runner.compare_schedule_feedback(baseline, candidate, [2, 5], 6)
    assert result["schedule_driver_equal"] is True
    assert result["final_fsm_states_equal"] is False
    assert result["fsm_state_differing_frontiers"] == [2]


def test_terminal_flush_does_not_drive_a_nonexistent_next_neural_chunk(tmp_path):
    baseline = schedule_trace(tmp_path, "before.jsonl")
    candidate = schedule_trace(tmp_path, "after.jsonl", terminal_state="in_play")
    result = runner.compare_schedule_feedback(baseline, candidate, [2, 5], 6)
    assert result["schedule_driver_equal"] is True
    assert result["terminal_frontier_excluded_from_next_chunk_feedback"] == 5
    assert result["baseline_terminal_record"]["state_after"] != result["candidate_terminal_record"]["state_after"]


def test_missing_actual_chunk_frontier_cannot_certify_scheduling(tmp_path):
    path = schedule_trace(tmp_path, "missing.jsonl")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    for row in rows:
        row["available_through"] = 5
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    result = runner.compare_schedule_feedback(path, path, [2, 5], 6)
    assert result["unknown_driver_frontiers"] == [2]
    assert result["schedule_driver_equal"] is None
    assert result["frontier_count_compared"] == 0
    assert result["fresh_inference_required_due_to_feedback_change"] is False
    assert result["fresh_inference_required_due_to_feedback_uncertainty"] is True
    assert result["fresh_inference_required"] is True
    assert result["frontier_comparisons"][0]["baseline_last_operation"] is None


def test_unobserved_frontier_does_not_allow_missing_full_source_steps(tmp_path):
    path = schedule_trace(tmp_path, "missing-step.jsonl")
    records = [json.loads(line) for line in path.read_text().splitlines()]
    records = [r for r in records if not (r["call"] == "step" and r["frame"] == 1)]
    path.write_text("".join(json.dumps(row) + "\n" for row in records))
    with pytest.raises(ValueError, match="full source steps"):
        runner.trace_schedule_states(path, [2, 5], 6)


@pytest.fixture
def report_recovery(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    output = tmp_path / "old-output"
    output.mkdir()
    helper = root / "report.py"
    dependency = root / "dependency.py"
    helper.write_text("original helper")
    dependency.write_text("original dependency")
    monkeypatch.setattr(runner, "__file__", str(helper))
    hashes = {str(helper): runner.sha(helper), str(dependency): runner.sha(dependency)}
    for path in (helper, dependency):
        archived = output / "executed_helpers" / path.relative_to(root)
        archived.parent.mkdir(exist_ok=True, parents=True)
        archived.write_bytes(path.read_bytes())
    protected = root / "model_manifest.yaml"
    protected.write_text("unchanged manifest")
    receipt = output / "applied_fix_receipt.json"
    receipt.write_text("original receipt")
    preflight = {
        "test": 2,
        "frames": 29296,
        "helper_sha256": hashes,
        "protected_inputs_sha256": {str(protected): runner.sha(protected)},
        "applied_fix_receipt_sha256": runner.sha(receipt),
    }
    (output / "preflight.json").write_text(json.dumps(preflight))
    helper.write_text("corrected report helper")
    return output, root, helper, dependency, protected, preflight


def test_resume_validates_archived_original_helper_not_current_edited_helper(report_recovery):
    output, root, helper, _, _, preflight = report_recovery
    assert runner.sha(helper) != preflight["helper_sha256"][str(helper)]
    old, verified = runner.verify_report_resume_preflight(output, {"test": 2, "frames": 29296}, root=root)
    assert old == preflight
    assert len(verified) == 2


def test_resume_rejects_tampered_archived_original_helper(report_recovery):
    output, root, helper, _, _, _ = report_recovery
    (output / "executed_helpers" / helper.relative_to(root)).write_text("tampered original")
    with pytest.raises(ValueError, match="archived helper"):
        runner.verify_report_resume_preflight(output, {"test": 2}, root=root)


def test_resume_rejects_unrelated_evaluation_dependency_edit(report_recovery):
    output, root, _, dependency, _, _ = report_recovery
    dependency.write_text("unreviewed dependency")
    with pytest.raises(ValueError, match="evaluation dependency"):
        runner.verify_report_resume_preflight(output, {"test": 2}, root=root)


@pytest.mark.parametrize("existing", ["semantic_regression_metrics.json", "REPORT.md", "completion.json"])
def test_resume_never_overwrites_existing_reports(report_recovery, existing):
    output, root, _, _, _, _ = report_recovery
    (output / existing).write_text("preserve this record")
    with pytest.raises(ValueError, match="existing report"):
        runner.verify_report_resume_preflight(output, {"test": 2}, root=root)
    assert (output / existing).read_text() == "preserve this record"


def test_resume_rejects_changed_original_inputs(report_recovery):
    output, root, _, _, protected, _ = report_recovery
    protected.write_text("different model manifest")
    with pytest.raises(ValueError, match="Protected original input"):
        runner.verify_report_resume_preflight(output, {"test": 2}, root=root)


def test_resume_rejects_foreign_preflight(report_recovery):
    output, root, _, _, _, _ = report_recovery
    with pytest.raises(ValueError, match="preflight binding"):
        runner.verify_report_resume_preflight(output, {"test": 1}, root=root)
