"""Focused guard contracts; never start subprocess inference or modify old data."""

import copy
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

SOURCE = Path(__file__).resolve().parents[2] / "orchestration/run_pre_test03_regression.py"
SPEC = importlib.util.spec_from_file_location("pre_test03_runner", SOURCE)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


@pytest.mark.parametrize("location", ["main", "candidate", "old", "ancestor", "named_baseline"])
def test_old_run_and_repository_paths_cannot_be_new_outputs(tmp_path, location):
    main, candidate, old = [tmp_path / name for name in ("repo", "candidate", "old-artifacts")]
    output = {
        "main": main / "new",
        "candidate": candidate / "new",
        "old": old / "new",
        "ancestor": tmp_path,
        "named_baseline": tmp_path / "new-artifacts/baseline_v1/new",
    }[location]
    with pytest.raises(ValueError):
        runner.require_new_output(output, candidate, main=main, old=old)


def test_existing_failure_output_is_immutable(tmp_path):
    output = tmp_path / "failed"
    output.mkdir()
    (output / "failure.log").write_text("preserve")
    with pytest.raises(ValueError, match="immutable"):
        runner.require_new_output(output, tmp_path / "candidate", main=tmp_path / "main", old=tmp_path / "old")
    assert (output / "failure.log").read_text() == "preserve"


def test_new_external_output_allowed_without_creating_it(tmp_path):
    output = tmp_path / "new-artifacts/test_01"
    assert (
        runner.require_new_output(output, tmp_path / "candidate", main=tmp_path / "main", old=tmp_path / "old")
        == output
    )
    assert not output.exists()


def test_unsupported_test_refused_before_any_path_access():
    with pytest.raises(ValueError, match="Only Test1 or Test2"):
        runner.preflight(SimpleNamespace(test=3))


@pytest.mark.parametrize(
    "config",
    [
        {"annotation": "labels"},
        {"nested": [{"gt_path": "truth"}]},
        {"ground_truth": False},
        {"path": "/repo/Part2/dataset/Test1_Full/file.json"},
        {"path": "Part2/file.json"},
        {"path": "labels.csv"},
        {"path": r"C:\Part2\test\truth.json"},
    ],
)
def test_annotation_free_worker_configuration(config):
    with pytest.raises(ValueError, match="worker"):
        runner.no_annotations(config)


def test_worker_profile_and_model_inputs_can_be_annotation_free():
    runner.no_annotations({"shuttle": {"params": {"threshold": 0.5}}, "diagnostics": {"ranges": [[0, 29]]}})
    runner.no_annotations(["/candidate/models/manifest.yaml", "/candidate/models/cache/lock.json", "/video/Test2.mp4"])


def completed(test):
    spec = runner.SPEC[test]
    info = {
        "status": "completed",
        "cached_perception_used": False,
        "source_sha256": spec["sha"],
        "frames_processed": spec["n"],
        "frontier_frame": spec["n"] - 1,
        "proxy_sha256": "proxy",
        "perception_cache_catalog": {"sha256": "catalog", "file_count": 123},
    }
    parent = {
        "status": "completed",
        "worker_exit_code": 0,
        "frozen_source_inputs_unchanged": True,
        "output_proxy_sha256": "proxy",
        "perception_cache_catalog_verification": {
            "status": "verified",
            "catalog_sha256": "catalog",
            "frames": spec["n"],
            "files": 123,
        },
    }
    return info, parent


@pytest.mark.parametrize("test", [1, 2])
def test_exact_full_worker_parent_and_catalogue_admission(test):
    runner.require_completed(*completed(test), test=test)
    with pytest.raises(ValueError):
        runner.require_completed(*completed(3 - test), test=test)


@pytest.mark.parametrize(
    "location,key,value",
    [
        (0, "status", "running"),
        (0, "cached_perception_used", True),
        (0, "frames_processed", 10),
        (0, "frontier_frame", 17266),
        (0, "source_sha256", "other"),
        (1, "status", "running"),
        (1, "worker_exit_code", 1),
        (1, "frozen_source_inputs_unchanged", False),
        (1, "output_proxy_sha256", "other"),
        (1, "perception_cache_catalog_verification", {"status": "unverified"}),
    ],
)
def test_incomplete_or_foreign_inference_cannot_complete(location, key, value):
    documents = completed(1)
    documents[location][key] = value
    with pytest.raises(ValueError):
        runner.require_completed(*documents, test=1)


def native_plan(root, protocol):
    return {
        "root": str(protocol),
        "code_commit": "frozen",
        "profile_source": str(root / runner.PROFILE),
        "cases": {"test1": {"frames": 17268, "source_sha256": runner.SPEC[1]["sha"]}},
        "source_files_sha256": {str(root / "sports/badminton/src/bai_badminton/engine.py"): "code"},
    }


@pytest.mark.parametrize(
    "damage", ["none", "old_source_root", "wrong_protocol", "commit", "frames", "video", "profile"]
)
def test_plan_root_is_protocol_but_source_paths_must_be_candidate_native(tmp_path, damage):
    root, protocol = tmp_path / "candidate", tmp_path / "artifacts/protocol"
    plan = native_plan(root, protocol)
    if damage == "old_source_root":
        plan["source_files_sha256"] = {"/original-repo/sports/badminton/engine.py": "old"}
    elif damage == "wrong_protocol":
        plan["root"] = str(root)
    elif damage == "commit":
        plan["code_commit"] = "different"
    elif damage == "frames":
        plan["cases"]["test1"]["frames"] = 17267
    elif damage == "video":
        plan["cases"]["test1"]["source_sha256"] = "different"
    elif damage == "profile":
        plan["profile_source"] = "/old/profile.yaml"
    if damage == "none":
        runner.require_native_plan(plan, root, protocol, test=1, head="frozen")
    else:
        with pytest.raises(ValueError):
            runner.require_native_plan(plan, root, protocol, test=1, head="frozen")


@pytest.mark.parametrize("actual,expected", [("changed", "old"), ("value", None), (None, "old")])
def test_numerical_profile_and_model_pins_cannot_change(actual, expected):
    with pytest.raises(ValueError, match="pin"):
        runner.require_pin(actual, expected, "profile")


def strict_semantic():
    return {
        "schema": "cached-external-semantic:v2",
        "baseline_parity": True,
        "source_intervention": None,
        "geometry_bracket": False,
        "contact_motion_reliability": False,
        "frames": 17268,
        "trace_step_count": 17268,
        "trace_ranges_telemetry_only": [[0, 17268]],
        "source_report_sha256": "report",
    }


@pytest.mark.parametrize(
    "key,value",
    [
        ("baseline_parity", False),
        ("source_intervention", {"changed": True}),
        ("frames", 17267),
        ("trace_step_count", 17267),
        ("trace_ranges_telemetry_only", [[100, 200]]),
        ("geometry_bracket", True),
        ("source_report_sha256", "other"),
    ],
)
def test_semantic_replay_requires_strict_full_own_run_parity(key, value):
    proof = strict_semantic()
    runner.require_semantic(proof, test=1, source_report_sha="report")
    proof[key] = value
    with pytest.raises(ValueError):
        runner.require_semantic(proof, test=1, source_report_sha="report")


def test_partial_reference_nulls_and_every_tolerance_are_retained():
    before = {
        name: {
            "role": "generated",
            "metrics": {
                "matching_policy": {"minimum_iou": 0.5},
                "detection": {"precision": None, "false_positives": None},
                "boundary_tolerances": {"start": [{"frames": 1, "matched_accuracy": 0.5, "all_gt_accuracy": 0.3}]},
            },
        }
        for name in runner.SPEC[1]["refs"]
    }
    after = copy.deepcopy(before)
    result = runner.checked_references(before, after, 1)
    partial = result["Test1_Full2.csv"]["candidate"]
    assert partial["detection"]["precision"] is None
    flat = runner.flat(partial)
    assert flat["boundary_tolerances.start[0].frames"] == 1
    assert flat["boundary_tolerances.start[0].all_gt_accuracy"] == 0.3
    assert runner.display(None) == "Unavailable"
    del after["Test1_Full2.csv"]
    with pytest.raises(ValueError):
        runner.checked_references(before, after, 1)


def test_original_matching_policy_cannot_be_changed():
    before = {
        name: {"role": "generated", "metrics": {"matching_policy": {"minimum_iou": 0.5}}}
        for name in runner.SPEC[2]["refs"]
    }
    after = copy.deepcopy(before)
    after["Test2_Full.csv"]["metrics"]["matching_policy"]["minimum_iou"] = 0.1
    with pytest.raises(ValueError, match="matching"):
        runner.checked_references(before, after, 2)


def test_unsupported_accuracy_must_be_null():
    runner.require_unsupported_null({"unsupported_metrics": {"pose": {"value": None}}})
    with pytest.raises(ValueError, match="null"):
        runner.require_unsupported_null({"unsupported_metrics": {"pose": {"value": 0}}})
