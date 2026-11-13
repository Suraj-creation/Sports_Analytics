"""Joint image-witness policy, distinct from athlete/identity authority."""

import numpy as np
import pytest

from bai_badminton.perception import scene_change


def measured(monkeypatch, changed, static=0, *, final_consistency=0.1):
    total = changed + static
    cls = getattr(scene_change, "SceneContinuityDetectorV3", None)
    assert cls is not None, "Versioned observer required for bounded scene-only foreground stream"
    calls = 0

    def flow(*_args):
        nonlocal calls
        pair, region = divmod(calls, total + 1)
        calls += 1
        if region == 0:
            return 80, 1.0, 1.0, 0.0
        innovative = pair == 2 and region <= changed
        return 40, final_consistency if innovative else 0.95, 100.0 if innovative else 3.0, 0.1

    monkeypatch.setattr(
        scene_change, "_flow_groups",
        lambda previous, current, masks: [flow(previous, current, mask) for mask in masks],
    )
    image = np.random.default_rng(761).integers(20, 220, (240, 600, 3), dtype=np.uint8)
    observer = cls()
    for frame in range(4):
        previous = (
            [
                scene_change.ForegroundRegion(frame - 1, f"visual:{k}", (20 + k * 55, 20, 55 + k * 55, 150), True, True)
                for k in range(total)
            ]
            if frame
            else []
        )
        result = observer.observe(
            frame, image, previous_regions=previous, previous_view_valid=True, current_view_valid=True
        )
    return result


@pytest.mark.parametrize("changed,static", [(2, 0), (2, 1), (4, 1), (4, 4)])
def test_joint_supported_regions_survive_static_context(monkeypatch, changed, static):
    result = measured(monkeypatch, changed, static)
    assert len(result.regions) == changed + static
    assert result.correspondence_hypothesis and result.hypothesis
    assert set(result.supporting_region_keys) == {f"visual:{i}" for i in range(changed)}
    assert result.authoritative is False


@pytest.mark.parametrize("static", [0, 1, 3])
def test_one_changed_region_never_proves_multi_region_change(monkeypatch, static):
    result = measured(monkeypatch, 1, static)
    assert not result.hypothesis
    assert result.supporting_region_keys == ()


def test_overflow_abstains_without_selecting_best_eight(monkeypatch):
    result = measured(monkeypatch, 4, 5)
    assert not result.hypothesis
    assert result.supporting_region_keys == ()
    assert result.status == "unknown"


def test_reversible_flow_does_not_erase_separate_appearance_witness(monkeypatch):
    result = measured(monkeypatch, 2, 1, final_consistency=1.0)
    assert not result.correspondence_hypothesis
    assert result.appearance_hypothesis
    assert set(result.supporting_region_keys) == {"visual:0", "visual:1"}


def test_one_witness_per_different_channel_cannot_be_combined(monkeypatch):
    cls = getattr(scene_change, "SceneContinuityDetectorV3", None)
    assert cls is not None
    calls = 0

    def flow(*_args):
        nonlocal calls
        pair, region = divmod(calls, 3)
        calls += 1
        if region == 0:
            return 80, 1.0, 1.0, 0.0
        if region == 1:
            # High prior photometric residual but stable reversible flow:
            # final correspondence innovation only, no appearance ratio.
            return 40, 0.1 if pair == 2 else 0.99, 100.0 if pair == 2 else 50.0, 0.1
        # The other region has appearance change with perfectly reversible flow.
        return 40, 1.0, 100.0 if pair == 2 else 3.0, 0.1

    monkeypatch.setattr(
        scene_change, "_flow_groups",
        lambda previous, current, masks: [flow(previous, current, mask) for mask in masks],
    )
    source = np.random.default_rng(875).integers(20, 220, (240, 600, 3), dtype=np.uint8)
    observer = cls()
    for frame in range(4):
        previous = (
            [
                scene_change.ForegroundRegion(frame - 1, f"visual:{k}", (20 + k * 55, 20, 55 + k * 55, 150), True, True)
                for k in range(2)
            ]
            if frame
            else []
        )
        result = observer.observe(
            frame, source, previous_regions=previous, previous_view_valid=True, current_view_valid=True
        )
    assert not result.correspondence_hypothesis and not result.appearance_hypothesis
    assert not result.hypothesis and result.supporting_region_keys == ()


def test_two_overlapping_keys_are_not_independent_visual_witnesses(monkeypatch):
    cls = getattr(scene_change, "SceneContinuityDetectorV3", None)
    assert cls is not None
    calls = 0

    def flow(*_args):
        nonlocal calls
        pair, region = divmod(calls, 3)
        calls += 1
        return (
            (80, 1.0, 1.0, 0.0) if region == 0 else (40, 0.1 if pair == 2 else 0.95, 100.0 if pair == 2 else 3.0, 0.1)
        )

    monkeypatch.setattr(
        scene_change, "_flow_groups",
        lambda previous, current, masks: [flow(previous, current, mask) for mask in masks],
    )
    source = np.random.default_rng(221).integers(20, 220, (240, 600, 3), dtype=np.uint8)
    observer = cls()
    for frame in range(4):
        previous = (
            [
                scene_change.ForegroundRegion(frame - 1, f"visual:{k}", (20.0, 20.0, 55.0, 150.0), True, True)
                for k in range(2)
            ]
            if frame
            else []
        )
        result = observer.observe(
            frame, source, previous_regions=previous, previous_view_valid=True, current_view_valid=True
        )
    assert len(result.regions) == 2
    assert not result.hypothesis and result.supporting_region_keys == ()


@pytest.mark.parametrize("admitted", [(), (0,), (0, 1)])
def test_positive_raw_layout_continuity_does_not_depend_on_participant_admission(monkeypatch, admitted):
    from bai_badminton.perception.content import ContentContinuityProviderV2, validate_scene_decision_binding
    from bai_badminton.perception.players import PlayerDetectionProbe

    raw = measured(monkeypatch, 2, 1)
    boxes = tuple(region.region.bbox for region in raw.regions)
    probe = PlayerDetectionProbe(
        raw.frame, (240, 600, 3), "0" * 64, boxes, (0.95,) * len(boxes), (0, 0, 600, 240), admitted
    )
    result = ContentContinuityProviderV2(mode="barrier_detector_layout_v2").layout_decision(
        raw, probe, detector_model="controlled-raw-proposals", geometry_valid=True
    )
    assert result.decision == "no_barrier"
    assert len(result.matched_pairs) == 2
    validate_scene_decision_binding(result, raw)


def test_missing_region_features_remain_unknown(monkeypatch):
    calls = 0

    def flow(*_args):
        nonlocal calls
        region = calls % 3
        calls += 1
        return (80, 1.0, 1.0, 0.0) if region == 0 else (0, None, None, None)

    monkeypatch.setattr(
        scene_change, "_flow_groups",
        lambda previous, current, masks: [flow(previous, current, mask) for mask in masks],
    )
    image = np.random.default_rng(912).integers(20, 220, (240, 600, 3), dtype=np.uint8)
    observer = scene_change.SceneContinuityDetectorV3()
    for frame in range(4):
        previous = (
            [
                scene_change.ForegroundRegion(
                    frame - 1, f"visual:{k}", (20.0 + k * 55, 20.0, 55.0 + k * 55, 150.0), True, True
                )
                for k in range(2)
            ]
            if frame
            else []
        )
        result = observer.observe(
            frame, image, previous_regions=previous, previous_view_valid=True, current_view_valid=True
        )
    assert len(result.regions) == 2
    assert result.background_features == 80
    assert not result.hypothesis and result.supporting_region_keys == ()
    assert result.status == "unknown"
