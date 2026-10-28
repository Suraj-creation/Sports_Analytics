"""Paired diagnostics compare implementations on identical observed shuttle samples."""

import importlib

import pytest


def tool():
    try:
        return importlib.import_module("research.evaluation.inspect_shuttle_motion")
    except ModuleNotFoundError:
        pytest.fail("paired source-bound shuttle-motion diagnostic is not implemented")


def probe():
    return {
        "source_video_sha256": "a" * 64,
        "source_frames": [100, 106],
        "fps": 30.0,
        "resize": "1280x720",
        "model_sha256": {"tracknet": "b" * 64, "detector": "c" * 64, "pose": "d" * 64},
        "contact_candidates": [{"frame": 101, "t_s": 101 / 30, "shot_family": "unknown"}],
        "shuttle_track": [
            {
                "frame": 100 + i,
                "x": float(i) if i != 3 else None,
                "y": float(i * 2) if i != 3 else None,
                "visible": i != 3,
                "interpolated": i == 4,
                "confidence": 0.8 if i != 3 else 0.0,
            }
            for i in range(7)
        ],
    }


class EngineStub:
    @staticmethod
    def _post_contact_kinematics(context, frame):
        track, index = context._shuttle_around(frame)
        assert index == 1 and track.interp[4] and not track.vis[3]
        return (120.0, 240.0)


def test_report_calls_engine_on_exact_observations_and_marks_unlabelled():
    result = tool().motion_report(probe(), EngineStub, "f" * 64, "1" * 64)
    assert result["accuracy_claim_eligible"] is False
    assert result["probe_sha256"] == "f" * 64
    assert result["events"][0]["frame"] == 101
    assert result["events"][0]["observed_samples"] == 3
    assert result["events"][0]["interpolated_samples"] == 1
    assert result["events"][0]["speed_px_s"] == 120


def test_comparison_never_joins_different_probes_or_fabricates_accuracy():
    module = tool()
    before = module.motion_report(probe(), EngineStub, "f" * 64, "1" * 64)
    after = module.motion_report(probe(), EngineStub, "f" * 64, "2" * 64)
    after["events"][0]["speed_px_s"] = None
    after["events"][0]["vy_px_s"] = None
    result = module.compare_motion(before, after)
    assert result["accuracy_claim_eligible"] is False
    assert result["before_available"] == 1 and result["after_available"] == 0
    assert result["changes"][0]["frame"] == 101
    assert "accuracy" not in result and "precision" not in result
    after["probe_sha256"] = "e" * 64
    with pytest.raises(ValueError, match="same probe"):
        module.compare_motion(before, after)


def test_rejects_duplicate_or_missing_frame_samples():
    module = tool()
    data = probe()
    data["shuttle_track"][2]["frame"] = 101
    with pytest.raises(ValueError, match="contiguous"):
        module.motion_report(data, EngineStub, "f" * 64, "1" * 64)
