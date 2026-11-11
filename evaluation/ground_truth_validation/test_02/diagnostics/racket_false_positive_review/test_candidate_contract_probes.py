"""Diagnostic controls for proposed evidence contracts, not production fixes."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from study_candidate_contracts import face_alias, scene, shaft_geometry, traced_detect


def selected(image, persons):
    trace = traced_detect(image, persons)
    return [p for p in trace["accepted_proposals"] if p["selected"]]


@pytest.mark.parametrize("angle", [0, 35, 75])
def test_clearly_separate_racket_and_face_remain_unaliased(angle):
    image, person = scene(angle=angle)
    proposals = selected(image, [person])
    assert len(proposals) == 1
    assert face_alias(proposals[0], [person]) == []


def test_near_overhead_racket_is_not_a_blanket_head_or_body_mask():
    image, person = scene(face="near_overhead")
    proposals = selected(image, [person])
    assert len(proposals) == 1
    assert face_alias(proposals[0], [person]) == []


def test_geometric_head_alias_is_explicitly_ambiguous():
    image, person = scene(face="overlap")
    proposals = selected(image, [person])
    assert len(proposals) == 1  # Existing geometry admits this controlled head/arm shape.
    assert face_alias(proposals[0], [person]) == [
        {"person_track_id": 7, "contained_face_joint_indices": [0, 1, 2, 3, 4]}
    ]


def test_same_pixels_cannot_disambiguate_head_from_racket_over_face():
    head_image, _ = scene(face="overlap")
    overlapping_racket_image, _ = scene(face="overlap")
    np.testing.assert_array_equal(head_image, overlapping_racket_image)
    # Hence an alias veto must mean uncertainty/abstention, not a physical head label.


def test_single_confident_face_joint_does_not_create_three_joint_alias():
    image, person = scene(face="overlap")
    proposal = selected(image, [person])[0]
    person.kps[1:5, 2] = 0.1
    assert face_alias(proposal, [person]) == []


def test_other_participants_face_is_also_an_equipment_alias():
    image, owner = scene(face="away")
    _, other = scene(face="overlap")
    other.track_id = 8
    other.kps[9:] = 0
    proposal = selected(image, [owner, other])[0]
    assert face_alias(proposal, [owner, other])[0]["person_track_id"] == 8


def test_fresh_person_match_is_required_for_alias_evidence():
    image, person = scene(face="overlap")
    proposal = selected(image, [person])[0]
    person.detector_matched = False
    assert face_alias(proposal, [person]) == []


def test_transverse_clutter_can_pass_current_dilation_without_straight_shaft():
    image, person = scene(transverse=True)
    proposals = selected(image, [person])
    assert len(proposals) == 1
    assert proposals[0]["dilated_shaft_support"] >= 0.65
    shaft = shaft_geometry(image, proposals[0])
    assert shaft["best_corridor_line_overlap_at_angle_20"] == 0


@pytest.mark.parametrize("blur", [False, True])
def test_straight_shaft_positive_has_independent_collinear_support(blur):
    image, person = scene(blur=blur)
    proposal = selected(image, [person])[0]
    shaft = shaft_geometry(image, proposal)
    assert shaft["best_corridor_line_overlap_at_angle_20"] > 0.9
