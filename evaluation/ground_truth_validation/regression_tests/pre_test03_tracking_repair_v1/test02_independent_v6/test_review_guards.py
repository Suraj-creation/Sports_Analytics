"""Independent review guards: incomplete runs and cross-chunk proof forgeries."""

from copy import deepcopy

import numpy as np
import pytest
from audit_acquisition_coverage import audit_camera_proofs
from native_completion_gate import STATUS, completion_contract, source_pair_contract, verify_native_completion


def config():
    return {"expected_commit": "a" * 40, "source_sha256": "b" * 64, "frame_count": 2}


def completed():
    value = {
        "status": STATUS,
        "candidate_commit": "a" * 40,
        "source_sha256": "b" * 64,
        "frames": 2,
        "artifact_sha256": {"synthetic": "c" * 64},
    }
    value.update(
        {
            k: True
            for k in [
                "new_neural_inference",
                "own_run_semantic_parity",
                "annotations_and_baselines_unchanged",
                "source_helpers_models_profile_frozen",
                "actual_model_identity_equal",
                "no_cleanup",
                "no_test3",
            ]
        }
    )
    return value


@pytest.mark.parametrize(
    "change", ["worker_only", "wrong_commit", "wrong_source", "short", "no_parity", "no_artifacts", "partial_models"]
)
def test_incomplete_or_foreign_orchestration_never_authorizes_analysis(change):
    v = completed()
    if change == "worker_only":
        v["status"] = "completed"
    if change == "wrong_commit":
        v["candidate_commit"] = "d" * 40
    if change == "wrong_source":
        v["source_sha256"] = "d" * 64
    if change == "short":
        v["frames"] = 1
    if change == "no_parity":
        v["own_run_semantic_parity"] = False
    if change == "no_artifacts":
        v["artifact_sha256"] = {}
    if change == "partial_models":
        v["actual_model_identity_equal"] = None
    with pytest.raises(ValueError):
        completion_contract(v, config())


def test_missing_completion_stops_before_importing_native_helper_or_reading_results(tmp_path):
    c = {**config(), "artifact_root": str(tmp_path / "incomplete"), "native_root": str(tmp_path / "not_a_repository")}
    with pytest.raises(ValueError, match="not complete"):
        verify_native_completion(c, tmp_path)
    assert list(tmp_path.iterdir()) == []


def packets():
    a = np.eye(3)
    b = a.copy()
    b[0, 2] = 1.0

    def frame(f, g):
        return {"f": f, "g": g.ravel().tolist(), "cs": "VALID", "v": "main", "r": False, "cd": None}

    policy = {
        "match_format": "singles",
        "layout_format_confirmed": True,
        "layout_format_context": {"match_format": "singles", "confirmed": True},
    }
    first = {"start": 0, "end": 0, "v": 23, "ci": deepcopy(policy), "frames": [frame(0, a)]}
    current = frame(1, b)
    current["cd"] = {
        "version": "detector-layout-scene-decision:v3",
        "raw_hypothesis": False,
        "decision": "barrier",
        "expected_participants": 2,
        "previous_frame": 0,
        "previous_camera": a.ravel().tolist(),
        "previous_to_current": b.ravel().tolist(),
    }
    second = {"start": 1, "end": 1, "v": 23, "ci": deepcopy(policy), "frames": [current]}
    return [first, second]


def test_actual_previous_camera_is_verified_across_chunk_boundary():
    result = audit_camera_proofs(packets())
    assert result["relative_claim_count"] == result["cross_chunk_claim_count"] == 1
    assert result["weak_barrier_frames"] == [1]
    assert result["format_context_transition_mismatches_requiring_runtime_order_review"] == []


@pytest.mark.parametrize(
    "change", ["previous", "relative", "missing_actual", "prior_invalid", "unconfirmed", "wrong_format"]
)
def test_self_consistent_chunk_start_claim_cannot_replace_actual_previous_source(change):
    p = packets()
    d = p[1]["frames"][0]["cd"]
    if change == "previous":
        fake = np.eye(3)
        fake[0, 2] = 5.0
        d["previous_camera"] = fake.ravel().tolist()
        d["previous_to_current"] = (
            (np.asarray(p[1]["frames"][0]["g"]).reshape(3, 3) @ np.linalg.inv(fake)).ravel().tolist()
        )
    if change == "relative":
        d["previous_to_current"][2] = 2.0
    if change == "missing_actual":
        p = p[1:]
    if change == "prior_invalid":
        p[0]["frames"][0]["cs"] = "LOST"
    if change == "unconfirmed":
        p[1]["ci"]["layout_format_context"]["confirmed"] = False
    if change == "wrong_format":
        p[1]["ci"]["layout_format_context"]["match_format"] = "doubles"
    with pytest.raises(ValueError):
        audit_camera_proofs(p)


def test_post_chunk_format_change_preserves_true_before_chunk_context():
    p = packets()
    p[0]["ci"]["match_format"] = "doubles"
    p[1]["ci"]["layout_format_context"] = {"match_format": "doubles", "confirmed": True}
    p[1]["ci"]["match_format"] = "doubles"
    p[1]["frames"][0]["cd"]["expected_participants"] = 4
    result = audit_camera_proofs(p)
    assert result["format_context_per_chunk"][0]["before_chunk_context"]["match_format"] == "singles"
    assert result["format_context_transition_mismatches_requiring_runtime_order_review"] == []


@pytest.mark.parametrize("field", ["source_sha256", "proxy_sha256", "source_size_bytes", "frame_count"])
def test_source_pairing_requires_exact_source_proxy_extent_and_timeline(field):
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


def test_native_module_location_and_root_must_both_match(tmp_path):
    from native_completion_gate import native_module_contract

    root = tmp_path / "candidate"
    native_module_contract(root / "research/pipeline_repair_run_analysis.py", root, root)
    with pytest.raises(ValueError, match="Actual native"):
        native_module_contract(tmp_path / "main/research/pipeline_repair_run_analysis.py", root, root)
    with pytest.raises(ValueError, match="Actual native"):
        native_module_contract(root / "research/pipeline_repair_run_analysis.py", tmp_path / "main", root)


@pytest.mark.parametrize("name", ["../foreign.json", "/absolute.json"])
def test_completion_cannot_bind_foreign_artifact_paths(name):
    v = completed()
    v["artifact_sha256"] = {name: "c" * 64}
    with pytest.raises(ValueError, match="Foreign artifact"):
        completion_contract(v, config())


def test_current_v4_decision_camera_proof_uses_same_original_arithmetic():
    p = packets()
    for packet in p:
        packet["v"] = 24
    p[1]["frames"][0]["cd"]["version"] = "detector-layout-scene-decision:v4"
    result = audit_camera_proofs(p)
    assert result["weak_barrier_frames"] == [1]
    assert result["cross_chunk_claim_count"] == 1
    p[1]["frames"][0]["cd"]["previous_to_current"][2] = 2.0
    with pytest.raises(ValueError):
        audit_camera_proofs(p)
