"""Disjoint feature origins preserve full-layout geometry and legacy wire meaning."""

from copy import deepcopy
from dataclasses import asdict, replace

import numpy as np
import pytest

from bai_badminton.perception import scene_change as scene
from bai_badminton.perception.content import (
    ContentContinuityProviderV2,
    scene_change_from_dict,
    scene_change_to_dict,
    scene_decision_from_dict,
    scene_decision_to_dict,
    validate_scene_decision_binding,
)
from bai_badminton.perception.players import PlayerDetectionProbe, strict_court_indices

BOXES = ((20.0, 20.0, 150.0, 150.0), (100.0, 60.0, 220.0, 180.0))


def regions(frame, boxes=BOXES):
    return [scene.ForegroundRegion(frame, str(i), box, True, True) for i, box in enumerate(boxes)]


def controlled_observer(monkeypatch, cls=scene.SceneContinuityDetectorV5, boxes=BOXES, static=()):
    state = {"frame": 0, "call": 0}
    captured = []

    def flow(_previous, _current, mask):
        index = state["call"] % (len(boxes) + 1)
        state["call"] += 1
        captured.append(mask.copy())
        if not mask.any():
            return 0, None, None, None
        if index == 0:
            return 40, 1.0, 0.0, 0.0
        changed = state["frame"] == 3 and index - 1 not in static
        return (
            min(20, int(np.count_nonzero(mask))),
            0.0 if changed else 1.0,
            40.0 if changed else 1.0,
            10.0 if changed else 0.0,
        )

    monkeypatch.setattr(scene, "_flow", flow)
    detector = cls(analysis_width=240)
    image = np.random.default_rng(7).integers(0, 256, (240, 480, 3), dtype=np.uint8)
    raw = None
    for frame in range(4):
        state["frame"] = frame
        state["call"] = 0
        raw = detector.observe(
            frame,
            image,
            previous_regions=regions(frame - 1, boxes) if frame else (),
            previous_view_valid=frame > 0,
            current_view_valid=True,
        )
    return raw, captured[-(len(boxes) + 1) :]


def test_masks_remove_every_shared_origin_and_background_keeps_full_union(monkeypatch):
    raw, masks = controlled_observer(monkeypatch)
    assert raw.version == scene.SCENE_CONTINUITY_VERSION_V5 and raw.hypothesis
    assert raw.supporting_region_keys == ("0", "1")
    assert not np.any((masks[1] > 0) & (masks[2] > 0))
    assert np.all(masks[0][(masks[1] > 0) | (masks[2] > 0)] == 0)
    assert np.all(masks[0][30:75, 50:75] == 0)  # shared full-ROI pixels stay outside background
    expected, records = scene.exclusive_feature_origin_masks(regions(2), raw.source_frame_size, raw.analysis_frame_size)
    assert raw.origin_masks == records
    assert all(np.array_equal(a, b) for a, b in zip(masks[1:], expected, strict=True))
    assert scene_change_from_dict(scene_change_to_dict(raw)) == raw


def test_old_v4_full_box_overlap_does_not_gain_new_authority(monkeypatch):
    old, _ = controlled_observer(monkeypatch, scene.SceneContinuityDetectorV4)
    assert not old.hypothesis and old.supporting_region_keys == ()
    wire = scene_change_to_dict(old)
    assert not {"feature_origin_policy", "source_frame_size", "analysis_frame_size", "origin_masks"}.intersection(wire)
    assert scene_change_from_dict(wire) == old
    # asdict has empty newly optional defaults; these confer no origin authority.
    assert scene_change_from_dict(asdict(old)) == old


@pytest.mark.parametrize("boxes", [(BOXES[0], BOXES[0]), ((20.0, 20.0, 180.0, 200.0), (40.0, 40.0, 100.0, 100.0))])
def test_duplicate_or_nested_rois_cannot_supply_two_origin_pools(monkeypatch, boxes):
    raw, _ = controlled_observer(monkeypatch, boxes=boxes)
    assert not raw.hypothesis
    assert sum(record.pixels > 0 for record in raw.origin_masks) < 2
    for region, record in zip(raw.regions, raw.origin_masks, strict=True):
        if record.pixels == 0:
            assert region.features == 0 and region.discontinuity is None
    assert scene_change_from_dict(scene_change_to_dict(raw)) == raw


def test_static_third_roi_is_still_removed_from_all_other_origin_pools(monkeypatch):
    boxes = (*BOXES, (30.0, 30.0, 70.0, 70.0))
    raw, _ = controlled_observer(monkeypatch, boxes=boxes, static=(2,))
    assert raw.hypothesis and raw.supporting_region_keys == ("0", "1")
    assert raw.origin_masks[2].pixels == 0
    _, without_static = scene.exclusive_feature_origin_masks(
        regions(2, BOXES), raw.source_frame_size, raw.analysis_frame_size
    )
    assert raw.origin_masks[0].pixels < without_static[0].pixels


@pytest.mark.parametrize(
    "damage",
    ["area", "digest", "key", "order", "analysis_shape", "source_shape", "policy", "missing", "future", "legacy"],
)
def test_origin_records_and_geometry_cannot_be_forged_or_downgraded(monkeypatch, damage):
    raw, _ = controlled_observer(monkeypatch)
    wire = deepcopy(scene_change_to_dict(raw))
    if damage == "area":
        wire["origin_masks"][0]["pixels"] += 1
    elif damage == "digest":
        wire["origin_masks"][0]["sha256"] = "0" * 64
    elif damage == "key":
        wire["origin_masks"][0]["key"] = "different"
    elif damage == "order":
        wire["origin_masks"] = tuple(reversed(wire["origin_masks"]))
    elif damage == "analysis_shape":
        wire["analysis_frame_size"] = (241, 120)
    elif damage == "source_shape":
        wire["source_frame_size"] = (481, 240)
    elif damage == "policy":
        wire["feature_origin_policy"] = "unverified"
    elif damage == "missing":
        wire.pop("origin_masks")
    elif damage == "future":
        wire["regions"][0]["region"]["frame"] = wire["frame"]
    elif damage == "legacy":
        wire["version"] = scene.SCENE_CONTINUITY_VERSION_V4
    with pytest.raises(ValueError):
        scene_change_from_dict(wire)


def test_witness_flags_recomputed_under_new_basis_not_trusted(monkeypatch):
    raw, _ = controlled_observer(monkeypatch)
    wire = scene_change_to_dict(raw)
    wire["regions"][0]["adaptive_ratio"] = 0.0
    with pytest.raises(ValueError):
        scene_change_from_dict(wire)


def test_empty_origins_cannot_claim_features_or_current_innovation(monkeypatch):
    raw, _ = controlled_observer(monkeypatch, boxes=(BOXES[0], BOXES[0]))
    wire = scene_change_to_dict(raw)
    wire["regions"][0]["features"] = 6
    with pytest.raises(ValueError, match="feature count"):
        scene_change_from_dict(wire)


def test_new_basis_rejects_cross_channel_pooling(monkeypatch):
    raw, _ = controlled_observer(monkeypatch)
    # One correspondence-only and one appearance-only innovation remain below
    # the existing two-region same-channel requirement.
    r0 = replace(raw.regions[0], appearance_adaptive_ratio=1.0, appearance_previous_mean=40.0)
    r1 = replace(raw.regions[1], adaptive_ratio=1.0, previous_mean=40.0)
    raw = replace(
        raw,
        regions=(r0, r1),
        hypothesis=False,
        status="measured",
        correspondence_hypothesis=False,
        appearance_hypothesis=False,
        supporting_region_keys=(),
        relative_region_keys=(),
    )
    assert scene_change_from_dict(scene_change_to_dict(raw)) == raw


@pytest.mark.parametrize("count", [2, 4])
def test_full_boxes_still_supply_positive_layout_veto_singles_and_doubles(monkeypatch, count):
    boxes = BOXES if count == 2 else (*BOXES, (250.0, 20.0, 380.0, 150.0), (330.0, 60.0, 460.0, 180.0))
    raw, _ = controlled_observer(monkeypatch, boxes=boxes)
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    polygon = ((0.0, 0.0), (480.0, 0.0), (480.0, 240.0), (0.0, 240.0))
    probe = PlayerDetectionProbe(
        raw.frame,
        (240, 480, 3),
        "a" * 64,
        boxes,
        (0.9,) * count,
        (0, 0, 480, 240),
        tuple(range(count)),
        polygon,
        strict_court_indices(boxes, polygon),
    )
    decision = provider.layout_decision(
        raw,
        probe,
        detector_model="source-detector@1",
        geometry_valid=True,
        expected_participants=count,
        previous_to_current=tuple(float(v) for v in np.eye(3).ravel()),
        previous_camera=tuple(float(v) for v in np.eye(3).ravel()),
    )
    assert decision.version == "detector-layout-scene-decision:v4"
    assert decision.decision == "no_barrier" and len(decision.matched_pairs) == count
    validate_scene_decision_binding(decision, raw)
    assert not provider.tracking_barrier_for_decision(decision)
    assert scene_decision_from_dict(scene_decision_to_dict(decision)) == decision
    with pytest.raises(ValueError):
        validate_scene_decision_binding(replace(decision, version="detector-layout-scene-decision:v3"), raw)


def test_default_layout_provider_selects_new_observer_but_legacy_policy_stays_old():
    assert isinstance(
        ContentContinuityProviderV2(mode="barrier_detector_layout_v2")._observer, scene.SceneContinuityDetectorV5
    )
    assert isinstance(ContentContinuityProviderV2(mode="diagnostic")._observer, scene.SceneContinuityDetectorV2)


def test_metadata_uses_exact_producer_raster_float_operation_order():
    observer = scene.SceneContinuityDetectorV5(analysis_width=1189)
    raw = observer.observe(
        0,
        np.zeros((762, 508, 3), dtype=np.uint8),
        previous_regions=(),
        previous_view_valid=False,
        current_view_valid=True,
    )
    assert observer._previous.shape == (1783, 1189)
    assert raw.analysis_frame_size == (1189, 1783)
    assert scene_change_from_dict(scene_change_to_dict(raw)) == raw


def make_probe(raw, boxes):
    polygon = ((0.0, 0.0), (480.0, 0.0), (480.0, 240.0), (0.0, 240.0))
    return PlayerDetectionProbe(
        raw.frame,
        (240, 480, 3),
        "a" * 64,
        boxes,
        (0.9,) * len(boxes),
        (0, 0, 480, 240),
        tuple(range(len(boxes))),
        polygon,
        strict_court_indices(boxes, polygon),
    )


@pytest.mark.parametrize(
    "failure", ["single_actor", "missing_detector", "unknown_format", "partial_doubles", "camera_unknown"]
)
def test_new_overlap_only_authority_cannot_use_raw_unknown_fallback(monkeypatch, failure):
    raw, _ = controlled_observer(monkeypatch)
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    boxes = ((20.0, 20.0, 220.0, 180.0),) if failure == "single_actor" else BOXES
    probe = None if failure == "missing_detector" else make_probe(raw, boxes)
    expected = None if failure == "unknown_format" else 4 if failure == "partial_doubles" else 2
    camera = None if failure == "camera_unknown" else tuple(float(v) for v in np.eye(3).ravel())
    decision = provider.layout_decision(
        raw,
        probe,
        detector_model="source-detector@1",
        geometry_valid=True,
        expected_participants=expected,
        previous_to_current=camera,
        previous_camera=camera,
    )
    assert decision.feature_origin_overlap_dependent and decision.decision == "unknown"
    assert not provider.tracking_barrier_for_decision(decision)
    validate_scene_decision_binding(decision, raw)
    with pytest.raises(ValueError, match="overlap authority"):
        validate_scene_decision_binding(replace(decision, feature_origin_overlap_dependent=False), raw)


def test_nonoverlapping_old_basis_preserves_explicit_unknown_fallback(monkeypatch):
    boxes = ((20.0, 20.0, 120.0, 150.0), (180.0, 20.0, 280.0, 150.0))
    raw, _ = controlled_observer(monkeypatch, boxes=boxes)
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    decision = provider.layout_decision(raw, None, detector_model=None, geometry_valid=True)
    assert raw.hypothesis and not decision.feature_origin_overlap_dependent
    assert decision.decision == "unknown" and provider.tracking_barrier_for_decision(decision)


def test_camera_explaining_complete_layout_cannot_be_new_overlap_barrier(monkeypatch):
    raw, _ = controlled_observer(monkeypatch)
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    boxes = tuple((x0 + 180, y0, x1 + 180, y1) for x0, y0, x1, y1 in BOXES)
    probe = make_probe(raw, boxes)
    transform = (1.0, 0.0, 180.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
    previous = tuple(float(v) for v in np.eye(3).ravel())
    decision = provider.layout_decision(
        raw,
        probe,
        detector_model="source-detector@1",
        geometry_valid=True,
        expected_participants=2,
        previous_to_current=transform,
        previous_camera=previous,
    )
    assert decision.decision == "unknown" and not provider.tracking_barrier_for_decision(decision)
    validate_scene_decision_binding(decision, raw)
    forged = replace(decision, decision="barrier", reason="raw_change_and_current_layout_discontinuity")
    with pytest.raises(ValueError, match="camera-aligned"):
        validate_scene_decision_binding(forged, raw)


@pytest.mark.parametrize("camera_shift", [0.0, 40.0])
def test_two_fragments_of_one_actor_cannot_override_retained_other_court_actor(monkeypatch, camera_shift):
    boxes = (*BOXES, (300.0, 20.0, 430.0, 200.0))
    raw, _ = controlled_observer(monkeypatch, boxes=boxes, static=(2,))
    assert raw.supporting_region_keys == ("0", "1")
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    current = ((0.0, 20.0, 18.0, 180.0), (300.0 + camera_shift, 20.0, 430.0 + camera_shift, 200.0))
    probe = make_probe(raw, current)
    identity = tuple(float(v) for v in np.eye(3).ravel())
    transform = (1.0, 0.0, camera_shift, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
    decision = provider.layout_decision(
        raw,
        probe,
        detector_model="source-detector@1",
        geometry_valid=True,
        expected_participants=2,
        previous_to_current=transform,
        previous_camera=identity,
    )
    assert decision.feature_origin_overlap_dependent and decision.decision == "unknown"
    assert not provider.tracking_barrier_for_decision(decision)
    validate_scene_decision_binding(decision, raw)
    with pytest.raises(ValueError, match="nonwitness court"):
        validate_scene_decision_binding(replace(decision, decision="barrier"), raw)


def test_outside_bystander_cannot_veto_complete_changed_court_layout(monkeypatch):
    boxes = (*BOXES, (300.0, 0.0, 430.0, 20.0))
    raw, _ = controlled_observer(monkeypatch, boxes=boxes, static=(2,))
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    polygon = ((0.0, 40.0), (480.0, 40.0), (480.0, 240.0), (0.0, 240.0))
    current = ((0.0, 80.0, 18.0, 180.0), (240.0, 80.0, 280.0, 200.0), boxes[2])
    probe = PlayerDetectionProbe(
        raw.frame,
        (240, 480, 3),
        "a" * 64,
        current,
        (0.9,) * 3,
        (0, 0, 480, 240),
        (0, 1),
        polygon,
        strict_court_indices(current, polygon),
    )
    identity = tuple(float(v) for v in np.eye(3).ravel())
    decision = provider.layout_decision(
        raw,
        probe,
        detector_model="source-detector@1",
        geometry_valid=True,
        expected_participants=2,
        previous_to_current=identity,
        previous_camera=identity,
    )
    assert decision.feature_origin_overlap_dependent and decision.decision == "barrier"
    assert provider.tracking_barrier_for_decision(decision)
    validate_scene_decision_binding(decision, raw)
