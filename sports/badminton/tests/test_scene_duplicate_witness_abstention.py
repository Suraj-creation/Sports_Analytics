"""Duplicated proposals may preserve every witness without establishing a cut.

Pure synthetic controls plus an opt-in source-bound selected-video cache fixture;
no video or neural model is opened by this module.
"""

import json
import os
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from bai_badminton.perception import scene_change as scene
from bai_badminton.perception.content import (
    AMBIGUOUS_POSITIVE_LAYOUT,
    ContentContinuityProviderV2,
    scene_change_from_dict,
    validate_scene_decision_binding,
)
from bai_badminton.perception.players import PlayerDetectionProbe, strict_court_indices


def changed_witnesses(monkeypatch, count):
    boxes = ((20.0, 50.0, 100.0, 240.0), (200.0, 50.0, 280.0, 240.0))
    if count == 4:
        boxes += ((350.0, 70.0, 420.0, 230.0), (470.0, 70.0, 540.0, 230.0))
    boxes += ((110.0, 0.0, 140.0, 35.0), (560.0, 0.0, 600.0, 35.0))
    state = {"frame": 0, "call": 0}

    def flow(_previous, _current, mask):
        index = state["call"] % (len(boxes) + 1)
        state["call"] += 1
        if not mask.any():
            return 0, None, None, None
        if index == 0:
            return 40, 1.0, 0.0, 0.0
        changed = state["frame"] == 3 and index in (1, 2)
        return min(20, np.count_nonzero(mask)), 1.0, 40.0 if changed else 1.0, 0.0

    monkeypatch.setattr(
        scene, "_flow_groups",
        lambda previous, current, masks: [flow(previous, current, mask) for mask in masks],
    )
    detector = scene.SceneContinuityDetectorV5(analysis_width=320)
    image = np.random.default_rng(7).integers(0, 256, (300, 640, 3), dtype=np.uint8)
    for frame in range(4):
        state.update(frame=frame, call=0)
        raw = detector.observe(
            frame, image,
            previous_regions=tuple(scene.ForegroundRegion(frame - 1, str(i), box, True, True)
                                   for i, box in enumerate(boxes)) if frame else (),
            previous_view_valid=frame > 0, current_view_valid=True,
        )
    assert raw.hypothesis and raw.supporting_region_keys == ("0", "1")
    return raw, boxes


def layout(raw, boxes, count, *, geometry=True):
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    polygon = ((0.0, 0.0), (640.0, 0.0), (640.0, 300.0), (0.0, 300.0))
    probe = PlayerDetectionProbe(raw.frame, (300, 640, 3), "a" * 64, tuple(boxes), (0.9,) * len(boxes),
                                 (0, 0, 640, 300), tuple(range(len(boxes))), polygon,
                                 strict_court_indices(boxes, polygon))
    decision = provider.layout_decision(
        raw, probe, detector_model="synthetic-detector@1", geometry_valid=geometry,
        expected_participants=count, previous_to_current=tuple(float(v) for v in np.eye(3).ravel()),
        previous_camera=tuple(float(v) for v in np.eye(3).ravel()),
    )
    return provider, decision


@pytest.mark.parametrize("count", [2, 4])
def test_partial_and_full_proposals_for_same_witness_abstain_from_reset(monkeypatch, count):
    raw, boxes = changed_witnesses(monkeypatch, count)
    # Both partial proposals overlap witness1 by >.3; their mutual IoU is only.267.
    current = (boxes[0], (200.0, 50.0, 280.0, 170.0), (200.0, 120.0, 280.0, 240.0), *boxes[2:])
    provider, decision = layout(raw, current, count)
    assert decision.decision == "unknown"  # Duplication cannot prove physical continuity either.
    assert not provider.tracking_barrier_for_decision(decision)
    assert not decision.matched_pairs  # No unique correspondences were manufactured.
    validate_scene_decision_binding(decision, raw)


@pytest.mark.parametrize("count", [2, 4])
def test_one_retained_witness_cannot_hide_missing_second_witness(monkeypatch, count):
    raw, boxes = changed_witnesses(monkeypatch, count)
    current = ((20.0, 50.0, 100.0, 170.0), (20.0, 120.0, 100.0, 240.0), *boxes[2:])
    provider, decision = layout(raw, current, count)
    assert decision.decision == "unknown"
    assert provider.tracking_barrier_for_decision(decision)


def test_geometry_loss_keeps_existing_raw_fallback(monkeypatch):
    raw, boxes = changed_witnesses(monkeypatch, 4)
    provider, decision = layout(raw, boxes, 4, geometry=False)
    assert decision.decision == "unknown" and provider.tracking_barrier_for_decision(decision)


def test_disjoint_witness_layout_still_establishes_barrier(monkeypatch):
    raw, _boxes = changed_witnesses(monkeypatch, 4)
    current = ((300.0, 0.0, 320.0, 40.0), (550.0, 50.0, 600.0, 240.0))
    provider, decision = layout(raw, current, 4)
    assert decision.decision == "barrier" and provider.tracking_barrier_for_decision(decision)
    validate_scene_decision_binding(decision, raw)


def test_unique_complete_witness_correspondence_keeps_existing_no_barrier(monkeypatch):
    raw, boxes = changed_witnesses(monkeypatch, 4)
    provider, decision = layout(raw, boxes, 4)
    assert decision.decision == "no_barrier" and not provider.tracking_barrier_for_decision(decision)
    assert len(decision.matched_pairs) == 2
    validate_scene_decision_binding(decision, raw)


@pytest.mark.parametrize("damage", ["missing_witness", "disjoint", "geometry"])
def test_forged_positive_ambiguity_reason_cannot_bypass_source_proof(monkeypatch, damage):
    raw, boxes = changed_witnesses(monkeypatch, 4)
    if damage == "missing_witness":
        current = ((20.0, 50.0, 100.0, 170.0), (20.0, 120.0, 100.0, 240.0), *boxes[2:])
    elif damage == "disjoint":
        current = ((300.0, 0.0, 320.0, 40.0), (550.0, 50.0, 600.0, 240.0))
    else:
        current = boxes
    _provider, decision = layout(raw, current, 4, geometry=damage != "geometry")
    forged = replace(decision, decision="unknown", reason=AMBIGUOUS_POSITIVE_LAYOUT)
    with pytest.raises(ValueError, match="ambiguous positive layout"):
        validate_scene_decision_binding(forged, raw)


def test_selected_source_retained_frame_fixture_when_explicitly_supplied():
    fixture_path = os.environ.get("BAI_SELECTED_SCENE_FIXTURE")
    if fixture_path is None:
        pytest.skip("source-bound selected-video fixture is optional and never downloaded by tests")
    fixture = json.loads(Path(fixture_path).read_text())
    assert fixture["source_sha256"] == "06a5cb888e58c64421114fecc582f60b85466900efec6db0bbf99420f4f6c010"
    original = fixture["decision"]
    raw = scene_change_from_dict(fixture["raw"])
    probe = PlayerDetectionProbe(
        raw.frame, tuple(original["detector_image_shape"]), original["detector_image_sha256"],
        tuple(tuple(box) for box in original["detector_boxes"]), tuple(original["detector_scores"]),
        (0, 0, original["detector_image_shape"][1], original["detector_image_shape"][0]),
        tuple(original["admitted_indices"]), tuple(tuple(point) for point in original["court_polygon"]),
        tuple(original["court_indices"]),
    )
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    decision = provider.layout_decision(
        raw, probe, detector_model=original["detector_model"], geometry_valid=original["geometry_valid"],
        expected_participants=original["expected_participants"],
        previous_to_current=tuple(original["previous_to_current"]),
        previous_camera=tuple(original["previous_camera"]),
    )
    assert decision.decision == "unknown"
    assert not provider.tracking_barrier_for_decision(decision)
    validate_scene_decision_binding(decision, raw)
