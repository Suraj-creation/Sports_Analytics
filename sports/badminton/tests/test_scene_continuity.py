"""Scene hypotheses are causal image evidence, never automatic cut authority."""

from __future__ import annotations

from dataclasses import replace

import cv2
import numpy as np
import pytest

from bai_badminton.perception.scene_change import ForegroundRegion, SceneContinuityDetector


def source_pair(n=2):
    rng = np.random.default_rng(71)
    background = rng.integers(35, 120, (360, 640, 3), dtype=np.uint8)
    textures = [rng.integers(0, 255, (56, 36, 3), dtype=np.uint8) for _ in range(n)]
    positions = [(140 + 100 * (k % 2), 80 + 150 * (k // 2)) for k in range(n)]

    def frame(f, *, changed=False, one_occluded=False):
        image = background.copy()
        regions = []
        for k, ((x, y), texture) in enumerate(zip(positions, textures, strict=True)):
            x += f
            if changed or (one_occluded and k == 0):
                x += 100
            image[y : y + 56, x : x + 36] = texture
            regions.append(ForegroundRegion(f, f"episode:{k}", (x, y, x + 36, y + 56), True, True))
        return image, regions

    return frame


def warmed(n=2):
    frames = source_pair(n)
    detector = SceneContinuityDetector()
    previous = []
    for f in range(6):
        image, regions = frames(f)
        detector.observe(f, image, previous_regions=previous, previous_view_valid=True, current_view_valid=True)
        previous = regions
    return detector, frames, previous


def test_abrupt_multiple_actor_change_is_only_a_typed_hypothesis():
    detector, frames, previous = warmed(2)
    result = detector.observe(
        6, frames(6, changed=True)[0], previous_regions=previous, previous_view_valid=True, current_view_valid=True
    )
    assert result.hypothesis
    assert result.authoritative is False
    assert len(result.regions) == 2
    assert result.frame == 6 and result.previous_frame == 5
    assert result.source_basis == "observed_pixels_and_previous_frame_regions"


def test_four_regions_are_preserved_and_weak_background_abstains():
    detector, frames, previous = warmed(4)
    result = detector.observe(
        6, frames(6, changed=True)[0], previous_regions=previous, previous_view_valid=True, current_view_valid=True
    )
    assert len(result.regions) == 4
    assert result.authoritative is False
    if result.background_consistent_fraction < 0.5:
        assert not result.hypothesis and result.status == "unknown"


def test_natural_motion_and_whole_image_pan_do_not_propose_edit():
    detector, frames, previous = warmed()
    image = frames(6)[0]
    image = cv2.warpAffine(image, np.array([[1, 0, 4], [0, 1, 0]], float), (640, 360), borderMode=cv2.BORDER_REFLECT)
    result = detector.observe(6, image, previous_regions=previous, previous_view_valid=True, current_view_valid=True)
    assert result.hypothesis is False
    assert result.authoritative is False


def test_global_exposure_change_does_not_propose_edit():
    detector, frames, previous = warmed()
    image = cv2.convertScaleAbs(frames(6)[0], alpha=1.05, beta=12)
    result = detector.observe(6, image, previous_regions=previous, previous_view_valid=True, current_view_valid=True)
    assert result.hypothesis is False


def test_one_actor_occlusion_does_not_establish_scene_discontinuity():
    detector, frames, previous = warmed()
    result = detector.observe(
        6, frames(6, one_occluded=True)[0], previous_regions=previous, previous_view_valid=True, current_view_valid=True
    )
    assert result.hypothesis is False


def test_missing_pixels_or_actor_features_remain_unknown():
    detector = SceneContinuityDetector()
    blank = np.full((360, 640, 3), 100, np.uint8)
    detector.observe(0, blank, previous_regions=[], previous_view_valid=True, current_view_valid=True)
    regions = [ForegroundRegion(0, str(i), (100 + 50 * i, 100, 130 + 50 * i, 160), False, False) for i in range(2)]
    result = detector.observe(1, blank, previous_regions=regions, previous_view_valid=True, current_view_valid=True)
    assert result.hypothesis is False and result.status == "unknown"


def test_stale_roi_frame_is_rejected_without_guessing_person_position():
    detector, frames, previous = warmed()
    previous[0] = replace(previous[0], frame=4)
    with pytest.raises(ValueError, match="preceding frame"):
        detector.observe(6, frames(6)[0], previous_regions=previous, previous_view_valid=True, current_view_valid=True)


def test_skipped_frame_and_explicit_cut_never_compare_different_contexts():
    detector, frames, _ = warmed()
    result = detector.observe(
        9, frames(9, changed=True)[0], previous_regions=frames(8)[1], previous_view_valid=True, current_view_valid=True
    )
    assert result.status == "unknown" and not result.hypothesis
    result = detector.observe(
        10,
        frames(10, changed=True)[0],
        previous_regions=frames(9)[1],
        previous_view_valid=True,
        current_view_valid=True,
        hard_cut=True,
    )
    assert not result.hypothesis and "known_camera_cut" in result.reasons


def test_invalid_view_and_carried_region_provenance_are_preserved():
    detector, frames, previous = warmed()
    previous = [replace(region, detector_matched=False, detector_observed=True) for region in previous]
    result = detector.observe(
        6, frames(6)[0], previous_regions=previous, previous_view_valid=True, current_view_valid=False
    )
    assert not result.hypothesis and result.status == "unknown"
    assert "excluded_view" in result.reasons


def test_checkpoint_restores_exact_next_observation_and_reset_clears_history():
    detector, frames, previous = warmed()
    checkpoint = detector.checkpoint()
    first = detector.observe(
        6, frames(6, changed=True)[0], previous_regions=previous, previous_view_valid=True, current_view_valid=True
    )
    detector.restore(checkpoint)
    repeated = detector.observe(
        6, frames(6, changed=True)[0], previous_regions=previous, previous_view_valid=True, current_view_valid=True
    )
    assert first == repeated
    detector.reset()
    result = detector.observe(
        7, frames(7)[0], previous_regions=frames(6)[1], previous_view_valid=True, current_view_valid=True
    )
    assert not result.hypothesis and result.previous_frame is None


def test_a_foreign_observer_checkpoint_is_explicitly_rejected():
    detector, _, _ = warmed()
    other = SceneContinuityDetector(analysis_width=320)
    with pytest.raises(ValueError, match="incompatible"):
        other.restore(detector.checkpoint())


def test_no_future_or_aliased_image_can_change_an_already_emitted_diagnostic():
    detector, frames, previous = warmed()
    image = frames(6)[0]
    current = detector.observe(6, image, previous_regions=previous, previous_view_valid=True, current_view_valid=True)
    image[:] = 0
    assert current.frame == 6 and current.authoritative is False
    reference, _, _ = warmed()
    reference.observe(6, frames(6)[0], previous_regions=previous, previous_view_valid=True, current_view_valid=True)
    actual = detector.observe(
        7, frames(7)[0], previous_regions=frames(6)[1], previous_view_valid=True, current_view_valid=True
    )
    expected = reference.observe(
        7, frames(7)[0], previous_regions=frames(6)[1], previous_view_valid=True, current_view_valid=True
    )
    assert actual == expected


@pytest.mark.parametrize("basis", ["appearance", "correspondence"])
def test_reversible_correspondence_and_appearance_are_independent_hypotheses(monkeypatch, basis):
    # Reversibility is not appearance/identity confidence: a match can return
    # to its starting point while its actual patch is very different. Conversely,
    # correspondence can fail even when the raw patch-error ratio was already high.
    import bai_badminton.perception.scene_change as module

    state = {"calls": 0, "error": 1.0 if basis == "appearance" else 15.0, "consistent": 1.0}

    def flow(*_):
        state["calls"] += 1
        if state["calls"] % 3 == 1:
            return 80, 1.0, 1.0, 0.0
        return 40, state["consistent"], state["error"], 0.1

    monkeypatch.setattr(module, "_flow", flow)
    detector = SceneContinuityDetector()
    source = source_pair()
    for frame in range(4):
        detector.observe(
            frame,
            source(frame)[0],
            previous_regions=source(frame - 1)[1] if frame else [],
            previous_view_valid=True,
            current_view_valid=True,
        )
    state.update(error=30.0, consistent=0.9 if basis == "appearance" else 0.2)
    result = detector.observe(
        4, source(4)[0], previous_regions=source(3)[1], previous_view_valid=True, current_view_valid=True
    )
    assert result.hypothesis and result.authoritative is False
    assert result.appearance_hypothesis is (basis == "appearance")
    assert result.correspondence_hypothesis is (basis == "correspondence")
