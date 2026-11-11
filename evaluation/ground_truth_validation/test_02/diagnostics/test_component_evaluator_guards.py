"""Source/annotation/evidence guards protect the Test2 evaluation contract."""

from __future__ import annotations

import copy
import json

import pytest

from evaluation.ground_truth_validation.orchestration import evaluate_test02_components as evaluator


@pytest.fixture
def coordinate_contract(tmp_path):
    evidence = tmp_path / "review.png"
    evidence.write_bytes(b"source-bound diagnostic illustration")
    hashes = {
        "player_detections.csv": "players",
        "Test2_Full_ball_filled.csv": "shuttle",
        "Test2_Full_court.json": "court",
    }
    bound = {"source_sha256": evaluator.TEST2_SHA, "media": {"n_frames": 29296}}
    certificate = {
        "status": "source_and_coordinate_semantics_verified",
        "source_sha256": evaluator.TEST2_SHA,
        "frame_size": [1280, 720],
        "fps_num": 30,
        "fps_den": 1,
        "reviewed_frames": [0, 300],
        "reviewer_type": "agent_diagnostic",
        "evidence": [{"path": str(evidence), "sha256": evaluator.sha(evidence)}],
        "reference_sha256": hashes.copy(),
        "legacy_player_point": "bbox_bottom_center",
        "legacy_shuttle_point": "analysis_image_xy",
        "court_corner_semantics": "outer_singles_floor_corners",
    }
    return certificate, bound, hashes, evidence


def test_missing_certificate_does_not_claim_distance_accuracy():
    assert evaluator.binding_status(None, {}, {})["status"] == "unverified"


def test_valid_binding_remains_diagnostic(coordinate_contract):
    certificate, bound, hashes, _ = coordinate_contract
    result = evaluator.binding_status(certificate, bound, hashes)
    assert result["status"] == "diagnostic_coordinate_binding_declared"
    assert result["independent_physical_accuracy"] is False


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("source_sha256", "wrong-video"),
        ("frame_size", [1920, 1080]),
        ("fps_num", 25),
        ("reviewed_frames", [29296]),
        ("reviewed_frames", [True]),
        ("legacy_player_point", "box_center"),
        ("court_corner_semantics", "unknown"),
    ],
)
def test_coordinate_conventions_are_not_inferred(coordinate_contract, key, value):
    certificate, bound, hashes, _ = coordinate_contract
    certificate[key] = value
    with pytest.raises(ValueError):
        evaluator.binding_status(certificate, bound, hashes)


def test_modified_visual_evidence_rejects_binding(coordinate_contract):
    certificate, bound, hashes, evidence = coordinate_contract
    evidence.write_bytes(b"different visual evidence")
    with pytest.raises(ValueError, match="evidence"):
        evaluator.binding_status(certificate, bound, hashes)


def test_modified_annotation_rejects_binding(coordinate_contract):
    certificate, bound, hashes, _ = coordinate_contract
    hashes["player_detections.csv"] = "changed"
    with pytest.raises(ValueError, match="hash mismatch"):
        evaluator.binding_status(certificate, bound, hashes)


@pytest.mark.parametrize("ids", [[0, 2], [0, 1, 1], [1, 2, 3], [0, 1]])
def test_dense_rows_never_get_filled_reordered_or_deduplicated(ids):
    with pytest.raises(ValueError, match="timeline"):
        evaluator.validate_dense_timeline([{"Frame": i} for i in ids], "Frame", 3)


def test_wrong_video_rejected_before_completion_or_annotation_access(tmp_path, monkeypatch):
    run = tmp_path / "run"
    run.mkdir()
    (run / "session.json").write_text(json.dumps({"source": {"sha256": "test1"}}))

    def must_not_call(*args, **kwargs):
        pytest.fail("Wrong video reached completion/annotation handling")

    monkeypatch.setattr(evaluator, "load_analysis_input", must_not_call)
    with pytest.raises(ValueError, match="exact original Test2"):
        evaluator.evaluate_components(run, tmp_path / "out")


def test_summary_does_not_destroy_raw_evidence():
    raw = {"values": [1, 3], "count": 2, "metrics": {"mean": 2, "values": [1, 3]}}
    original = copy.deepcopy(raw)
    assert evaluator.compact(raw) == {"count": 2, "metrics": {"mean": 2}}
    assert raw == original
