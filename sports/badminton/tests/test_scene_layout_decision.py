"""Raw scene hypotheses need current detector layout corroboration."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from bai_badminton.perception.content import (
    ContentContinuityProviderV2,
    scene_change_from_dict,
    scene_decision_from_dict,
    scene_decision_to_dict,
    validate_scene_decision_binding,
)
from bai_badminton.perception.players import PlayerDetectionProbe
from bai_badminton.perception.scene_change import ForegroundRegion, RegionContinuity, SceneChangeEvidence


def case(count=2, shift=0):
    boxes = tuple((20.0 + i * 55, 20.0, 50.0 + i * 55, 100.0) for i in range(count))
    regions = tuple(
        RegionContinuity(ForegroundRegion(11, str(i), box, False, False), 20, 0.95, 30.0, 0.1, 1.5, 1.0, 1.5, 3.0, 10.0)
        for i, box in enumerate(boxes)
    )
    raw = SceneChangeEvidence(
        12, 11, "hypothesis", True, ("appearance_discontinuity",), regions=regions, appearance_hypothesis=True
    )
    current = tuple((a + shift, b, c + shift, d) for a, b, c, d in boxes)
    probe = PlayerDetectionProbe(
        12, (180, 800, 3), "0" * 64, current, (0.9,) * count, (0, 0, 800, 180), tuple(range(count))
    )
    return raw, probe


def decide(raw, probe, *, geometry=True):
    return ContentContinuityProviderV2(mode="barrier_detector_layout_v2").layout_decision(
        raw, probe, detector_model="rfdetr_small@1", geometry_valid=geometry
    )


@pytest.mark.parametrize("count", [2, 4])
def test_complete_current_layout_suppresses_raw_hypothesis_without_claiming_physical_continuity(count):
    raw, probe = case(count, shift=2)
    result = decide(raw, probe)
    assert result.decision == "no_barrier" and len(result.matched_pairs) == count
    assert raw.hypothesis and not raw.authoritative
    assert result.detector_frame == raw.frame
    assert scene_decision_from_dict(scene_decision_to_dict(result), frame_idx=12) == result


@pytest.mark.parametrize("count", [2, 4])
def test_disjoint_current_layout_can_corroborate_tracking_reset(count):
    raw, probe = case(count, shift=300)
    result = decide(raw, probe)
    assert result.decision == "barrier" and result.matched_pairs == ()
    assert not raw.authoritative  # No sporting point/score authority was introduced.


def test_one_actor_loss_or_detector_occlusion_remains_unknown():
    raw, probe = case(2)
    probe = replace(probe, boxes=probe.boxes[:1], scores=probe.scores[:1], admitted_indices=(0,))
    assert decide(raw, probe).decision == "unknown"
    single, probe = case(1, shift=300)
    assert decide(single, probe).decision == "unknown"


def test_ambiguous_overlapping_actor_boxes_cannot_establish_an_edit():
    raw, probe = case(2)
    probe = replace(probe, boxes=(probe.boxes[0], probe.boxes[0]))
    assert decide(raw, probe).decision == "unknown"


def test_missing_detector_or_geometry_keeps_unknown_with_actual_source_metadata():
    raw, probe = case()
    assert decide(raw, None).decision == "unknown"
    result = decide(raw, probe, geometry=False)
    assert result.decision == "unknown" and result.detector_boxes == probe.boxes
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    assert provider.tracking_barrier_for_decision(result)
    assert "raw_barrier_fallback" in result.reason


def test_source_frame_and_evidence_codec_reject_misbound_or_fabricated_layout():
    raw, probe = case()
    with pytest.raises(ValueError, match="current source frame"):
        decide(raw, replace(probe, frame_idx=13))
    serialized = scene_decision_to_dict(decide(raw, probe))
    for field, value in (
        ("detector_frame", 13),
        ("detector_image_sha256", "bad"),
        ("detector_model", None),
        ("matched_pairs", [[0, 0], [0, 1]]),
    ):
        bad = {**serialized, field: value}
        with pytest.raises(ValueError):
            scene_decision_from_dict(bad, frame_idx=12)


def test_all_source_bound_fresh_probe_decisions_recompute_without_neural_or_label_access():
    source = Path(__file__).parent / "fixtures/scene_detector_layout_cases.json"
    cases = json.loads(source.read_text())["cases"]
    assert len(cases) == 51
    for item in cases:
        row = item["probe"]
        probe = PlayerDetectionProbe(
            row["frame_idx"],
            tuple(row["image_shape"]),
            row["image_sha256"],
            tuple(tuple(box) for box in row["boxes"]),
            tuple(row["scores"]),
            tuple(row["crop_box"]),
            tuple(row["admitted_indices"]),
        )
        raw = scene_change_from_dict(item["raw_scene_evidence"], frame_idx=item["source_frame"])
        result = decide(raw, probe)
        validate_scene_decision_binding(result, raw)
        assert result.decision == item["expected_decision"], (item["video"], item["source_frame"])
        if item["video"] == "Test1":
            assert result.decision == "barrier"


def test_positive_correspondence_cannot_survive_disjoint_source_boxes():
    raw, probe = case()
    decision = decide(raw, probe)
    changed = replace(decision, detector_boxes=((400.0, 20.0, 430.0, 100.0), (500.0, 20.0, 530.0, 100.0)))
    with pytest.raises(ValueError, match="source-region geometry"):
        validate_scene_decision_binding(changed, raw)


def test_claimed_barrier_cannot_ignore_complete_source_correspondence():
    raw, probe = case(shift=300)
    decision = decide(raw, probe)
    changed = replace(decision, detector_boxes=case()[1].boxes)
    with pytest.raises(ValueError, match="source-region geometry"):
        validate_scene_decision_binding(changed, raw)


def test_source_region_coordinates_and_ambiguous_matching_are_verified():
    raw, probe = case()
    decision = decide(raw, probe)
    changed_region = replace(raw.regions[0], region=replace(raw.regions[0].region, bbox=(400.0, 20.0, 430.0, 100.0)))
    changed_raw = replace(raw, regions=(changed_region, raw.regions[1]))
    with pytest.raises(ValueError, match="source-region geometry"):
        validate_scene_decision_binding(decision, changed_raw)
    duplicates = replace(decision, detector_boxes=(probe.boxes[0], probe.boxes[0]))
    with pytest.raises(ValueError, match="ambiguous"):
        validate_scene_decision_binding(duplicates, raw)
