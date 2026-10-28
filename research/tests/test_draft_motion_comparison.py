"""Diagnostic comparison must not turn unconfirmed motion into ground truth."""

import importlib

import pytest


def _tool():
    try:
        return importlib.import_module("research.evaluation.compare_motion_draft")
    except ModuleNotFoundError:
        pytest.fail("source-bound draft motion comparison is not implemented")


def _draft():
    return {
        "schema_version": "ai-motion-review-v1",
        "status": "draft",
        "human_reviewed": False,
        "exhaustive": False,
        "evaluation_eligible": False,
        "media": {"sha256": "a" * 64, "fps_num": 30, "fps_den": 1},
        "review_window_s": [6.0, 15.0],
        "candidate_motion_windows": [
            {"time_range_s": [6.7, 7.1], "contact_confirmed": False},
            {"time_range_s": [11.8, 12.5], "contact_confirmed": False},
        ],
    }


def _probe(frames):
    return {
        "source_video_sha256": "a" * 64,
        "source_frames": [180, 449],
        "fps": 30.0,
        "model_sha256": {"tracknet": "b" * 64, "detector": "c" * 64, "pose": "d" * 64},
        "implementation_sha256": {"diagnostic": "e" * 64, "contact": "f" * 64, "stroke": "1" * 64},
        "contact_candidates": [{"frame": f, "t_s": f / 30, "shot_family": "unknown"} for f in frames],
    }


def test_motion_comparison_reports_overlap_without_accuracy_claims():
    result = _tool().compare_draft(_draft(), _probe([201, 366, 400]), _probe([201, 400]))
    assert result["accuracy_claim_eligible"] is False
    assert result["review_exhaustive"] is False
    assert result["before"]["hypotheses_in_windows"] == [[201], [366]]
    assert result["after"]["hypotheses_in_windows"] == [[201], []]
    assert result["before"]["hypotheses_outside_windows"] == [400]
    assert result["after"]["unknown_family_count"] == 2
    assert not any(key in result for key in ("precision", "recall", "f1", "accuracy"))


@pytest.mark.parametrize("mutation", ["source", "window", "duplicate", "human", "confirmed"])
def test_rejects_mismatched_or_misrepresented_inputs(mutation):
    draft, before, after = _draft(), _probe([201, 366]), _probe([201, 366])
    if mutation == "source":
        after["source_video_sha256"] = "b" * 64
    elif mutation == "window":
        after["source_frames"] = [181, 449]
    elif mutation == "duplicate":
        after["contact_candidates"].append(after["contact_candidates"][0])
    elif mutation == "human":
        draft["human_reviewed"] = True
    else:
        draft["candidate_motion_windows"][0]["contact_confirmed"] = True
    with pytest.raises(ValueError):
        _tool().compare_draft(draft, before, after)


def test_comparison_rejects_missing_model_or_implementation_provenance():
    draft, before, after = _draft(), _probe([201]), _probe([201])
    del after["model_sha256"]
    with pytest.raises(ValueError, match="provenance"):
        _tool().compare_draft(draft, before, after)


def test_diagnostic_provenance_is_derived_from_actual_input_bytes(tmp_path):
    import hashlib

    diagnostic = importlib.import_module("research.evaluation.fresh_component_diagnostic")
    files = []
    for name in ("video", "tracknet", "detector", "pose"):
        file = tmp_path / name
        file.write_bytes(name.encode())
        files.append(file)
    helper = getattr(diagnostic, "input_provenance", None)
    assert callable(helper), "diagnostic must bind reports to actual source and model bytes"
    result = helper(*files)
    assert result["source_video_sha256"] == hashlib.sha256(b"video").hexdigest()
    assert result["model_sha256"]["tracknet"] == hashlib.sha256(b"tracknet").hexdigest()
    assert all(len(value) == 64 for value in result["implementation_sha256"].values())


def test_comparison_rejects_different_model_checkpoints():
    draft, before, after = _draft(), _probe([201]), _probe([201])
    after["model_sha256"]["pose"] = "9" * 64
    with pytest.raises(ValueError, match="model hashes differ"):
        _tool().compare_draft(draft, before, after)


def test_cli_checks_local_video_hash_and_emits_no_accuracy(tmp_path):
    import hashlib
    import json
    import subprocess
    import sys

    video = tmp_path / "source.mp4"
    video.write_bytes(b"small-video-fixture")
    digest = hashlib.sha256(video.read_bytes()).hexdigest()
    draft, before, after = _draft(), _probe([201]), _probe([201, 366])
    draft["media"]["sha256"] = before["source_video_sha256"] = after["source_video_sha256"] = digest
    paths = []
    for name, value in (("draft", draft), ("before", before), ("after", after)):
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(value))
        paths.append(path)
    command = [
        sys.executable,
        "research/evaluation/compare_motion_draft.py",
        "--video",
        str(video),
        "--draft",
        str(paths[0]),
        "--before",
        str(paths[1]),
        "--after",
        str(paths[2]),
    ]
    run = subprocess.run(command, capture_output=True, text=True, check=True)
    result = json.loads(run.stdout)
    assert result["provenance"]["video_sha256_verified"] is True
    assert result["accuracy_claim_eligible"] is False
    video.write_bytes(b"different")
    failed = subprocess.run(command, capture_output=True, text=True)
    assert failed.returncode != 0 and "do not match" in failed.stderr


def test_diagnostic_serializes_track_evidence_without_nan_or_frame_shift():
    import numpy as np

    from bai_badminton.perception.shuttle_post import Track

    diagnostic = importlib.import_module("research.evaluation.fresh_component_diagnostic")
    serializer = getattr(diagnostic, "track_observations", None)
    assert callable(serializer), "diagnostic must expose source-bound track observations"
    track = Track.from_arrays(
        np.array([1.0, 2.0, np.nan]),
        np.array([3.0, 4.0, np.nan]),
        np.array([True, True, False]),
        np.array([0.8, 0.2, 0.0]),
    )
    track.interp[1] = True
    result = serializer(track, 180)
    assert [row["frame"] for row in result] == [180, 181, 182]
    assert result[0] == {"frame": 180, "x": 1.0, "y": 3.0, "visible": True, "interpolated": False, "confidence": 0.8}
    assert result[1]["interpolated"] is True
    assert result[2]["x"] is None and result[2]["y"] is None and result[2]["visible"] is False
