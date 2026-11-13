"""A raw LK patch error is distinct from supported adaptive scene evidence."""

from dataclasses import asdict

import numpy as np
import pytest

from bai_badminton.perception import scene_change as scene
from bai_badminton.perception.content import scene_change_from_dict, scene_change_to_dict


def observe_low_feature_pair(monkeypatch, feature_count):
    calls = 0

    def flow(*_args):
        nonlocal calls
        pair, region = divmod(calls, 3)
        calls += 1
        if region == 0:
            return 80, 1.0, 1.0, 0.0
        if pair == 2 and region == 1:
            return feature_count, 0.5, 6.0, 0.1
        return 40, 0.95, 1.0, 0.1

    monkeypatch.setattr(scene, "_flow", flow)
    detector = scene.SceneContinuityDetectorV4()
    image = np.random.default_rng(44).integers(20, 220, (240, 600, 3), dtype=np.uint8)
    outputs = []
    for frame in range(7):
        regions = (
            tuple(
                scene.ForegroundRegion(frame - 1, str(i), (20.0 + i * 60, 20.0, 50.0 + i * 60, 100.0), True, True)
                for i in range(2)
            )
            if frame
            else ()
        )
        outputs.append(
            detector.observe(frame, image, previous_regions=regions, previous_view_valid=True, current_view_valid=True)
        )
    return outputs


@pytest.mark.parametrize("features", [0, 1, 5])
def test_low_feature_residual_preserves_unknown_ratio_and_prior_history(monkeypatch, features):
    outputs = observe_low_feature_pair(monkeypatch, features)
    raw = outputs[3]
    region = raw.regions[0]
    assert region.median_patch_error == 6.0
    assert region.appearance_previous_mean == 1.0
    assert region.appearance_adaptive_ratio is None and region.discontinuity is None
    assert not raw.hypothesis and not raw.acquisition_region_keys and not raw.relative_region_keys
    assert scene_change_from_dict(scene_change_to_dict(raw)) == raw
    # Missing current support clears that episode's history; subsequent fresh
    # observations rebuild it instead of fabricating a ratio from stale data.
    assert outputs[4].regions[0].appearance_previous_mean is None
    assert outputs[5].regions[0].appearance_previous_mean is None
    assert outputs[6].regions[0].appearance_previous_mean == 1.0
    assert all(scene_change_from_dict(scene_change_to_dict(value)) == value for value in outputs)


@pytest.mark.parametrize(
    "field,value", [("appearance_adaptive_ratio", 6.0), ("adaptive_ratio", 3.0), ("discontinuity", 3.0)]
)
def test_low_feature_measurement_cannot_acquire_supported_scene_evidence(monkeypatch, field, value):
    raw = asdict(observe_low_feature_pair(monkeypatch, 5)[3])
    raw["regions"][0][field] = value
    with pytest.raises(ValueError, match="feature support"):
        scene_change_from_dict(raw)


def test_six_features_still_obey_existing_ratio_arithmetic_and_acquisition_gate(monkeypatch):
    raw = observe_low_feature_pair(monkeypatch, 6)[3]
    assert raw.regions[0].appearance_adaptive_ratio == 6.0
    assert raw.acquisition_region_keys == ("0",)
    assert not raw.relative_region_keys and not raw.hypothesis
    assert scene_change_from_dict(scene_change_to_dict(raw)) == raw
    value = asdict(raw)
    value["regions"][0]["appearance_adaptive_ratio"] = 6.1
    with pytest.raises(ValueError, match="prior history"):
        scene_change_from_dict(value)
