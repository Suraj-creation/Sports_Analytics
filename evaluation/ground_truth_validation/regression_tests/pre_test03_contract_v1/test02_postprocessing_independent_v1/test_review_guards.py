"""Separate fresh-worker/postprocessing completion and unchanged arithmetic guards."""

import ast
import json
from pathlib import Path

import pytest
from native_completion_gate import (
    SCHEMA,
    STATUS,
    completion_contract,
    original_failure_contract,
    root_contract,
    source_pair_contract,
    verify_native_completion,
)

HERE = Path(__file__).resolve().parent


def config():
    return {
        "expected_commit": "a" * 40,
        "source_sha256": "b" * 64,
        "frame_count": 2,
        "neural_artifact_root": "/original",
        "original_run": "/original/run",
        "original_failure_record": "/original/failure.json",
        "artifact_root": "/postprocessing",
        "native_root": "/producer",
    }


def completed():
    c = config()
    value = {
        "schema": SCHEMA,
        "status": STATUS,
        "candidate_commit": c["expected_commit"],
        "source_sha256": c["source_sha256"],
        "frames": 2,
        "test": 2,
        "original_NN_root": "/original",
        "producer_root": "/producer",
        "new_neural_inference": False,
        "artifact_sha256": {"synthetic": "c" * 64},
    }
    value.update(
        {
            k: True
            for k in (
                "original_neural_inference_was_fresh",
                "original_failed_outer_unchanged",
                "own_run_semantic_parity",
                "annotations_and_baselines_unchanged",
                "source_helpers_models_profile_frozen",
                "actual_model_identity_equal",
                "no_cleanup",
                "no_test3",
            )
        }
    )
    return value


def test_distinct_postprocessing_completion_is_valid_without_invented_nn():
    completion_contract(completed(), config())


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", "ordinary_completed_run"),
        ("status", "completed"),
        ("candidate_commit", "d" * 40),
        ("source_sha256", "d" * 64),
        ("frames", 1),
        ("test", 1),
        ("original_NN_root", "/foreign"),
        ("producer_root", "/foreign"),
        ("new_neural_inference", True),
        ("new_neural_inference", None),
        ("original_neural_inference_was_fresh", False),
        ("original_failed_outer_unchanged", False),
        ("own_run_semantic_parity", False),
        ("annotations_and_baselines_unchanged", False),
        ("actual_model_identity_equal", None),
        ("artifact_sha256", {}),
        ("no_test3", False),
    ],
)
def test_partial_foreign_or_fabricated_receipts_rejected(field, value):
    item = completed()
    item[field] = value
    with pytest.raises(ValueError):
        completion_contract(item, config())


@pytest.mark.parametrize(
    "changes",
    [
        {"artifact_root": "/original"},
        {"artifact_root": "/original/derived"},
        {"original_run": "/postprocessing/run"},
        {"original_failure_record": "/foreign/failure.json"},
    ],
)
def test_navigation_or_nested_root_cannot_substitute_original_run(changes):
    with pytest.raises(ValueError):
        root_contract(config() | changes)


def test_missing_new_completion_stops_before_native_import_or_metrics(tmp_path):
    c = config() | {"artifact_root": str(tmp_path / "not_completed")}
    with pytest.raises(ValueError, match="not complete"):
        verify_native_completion(c, tmp_path)
    assert not list(tmp_path.iterdir())


def test_original_outer_failure_cannot_be_rewritten_as_completed(tmp_path):
    (tmp_path / "completion.json").write_text("{}")
    with pytest.raises(ValueError, match="no invented original completion"):
        original_failure_contract(tmp_path, {})


def test_missing_or_changed_original_failure_proof_rejected(tmp_path):
    (tmp_path / "failure.json").write_text('{"status":"failed"}')
    with pytest.raises(ValueError, match="absent or changed"):
        original_failure_contract(tmp_path, {"original_artifact_sha256": {}})


@pytest.mark.parametrize("field", ["source_sha256", "proxy_sha256", "source_size_bytes", "frame_count"])
def test_exact_source_proxy_and_frame_contract(field):
    c = {"source_sha256": "a" * 64, "expected_proxy_sha256": "b" * 64, "source_size_bytes": 100, "frame_count": 2}
    bound = {"source_sha256": "a" * 64, "proxy_sha256": "b" * 64, "media": {"n_frames": 2}}
    source_pair_contract(bound, c, 100)
    if field in {"source_sha256", "proxy_sha256"}:
        bound[field] = "c" * 64
    elif field == "source_size_bytes":
        c[field] = 101
    else:
        bound["media"]["n_frames"] = 1
    with pytest.raises(ValueError):
        source_pair_contract(bound, c, 100)


def function(source, name):
    return next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)


def test_existing_numerical_comparison_helpers_and_constants_unchanged():
    original = (HERE / "prepared_sources/review_completed_run.py").read_text()
    current = (HERE / "review_completed_run.py").read_text()
    for name in ("dist", "iou"):
        assert ast.dump(function(original, name)) == ast.dump(function(current, name))

    def numbers(text):
        return [
            n.value
            for n in ast.walk(function(text, "main"))
            if isinstance(n, ast.Constant) and type(n.value) in (int, float)
        ]

    assert numbers(original) == numbers(current)


def test_existing_camera_proof_arithmetic_is_identical():
    a = (HERE / "prepared_sources/audit_acquisition_coverage.py").read_text()
    b = (HERE / "audit_acquisition_coverage.py").read_text()
    assert ast.dump(function(a, "audit_camera_proofs")) == ast.dump(function(b, "audit_camera_proofs"))


def test_all_nine_seeded_weak_resets_kept_in_review_config():
    c = json.loads((HERE / "review_config.json").read_text())
    assert c["known_weak_reset_anchors"] == [355, 699, 1095, 3394, 4581, 5958, 11691, 11985, 25521]
    assert set(c["known_weak_reset_anchors"]) <= set(c["known_source_case_anchors"])
    assert c["annotation_count"] == 7 and c["interval_reference_count"] == 3
    assert c["mandatory_source_review_ranges_halfopen"] == [[807, 905], [11688, 11763]]


def test_comparison_rows_are_loaded_from_existing_detail_file_not_aggregate():
    source = (HERE / "review_completed_run.py").read_text()
    assert 'before_reference_rows[name]["comparison"]' in source
    assert 'after_reference_rows[name]["comparison"]' in source
    assert 'row for row in a["comparison"]' not in source
    assert 'row for row in b["comparison"]' not in source
