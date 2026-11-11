"""RED/GREEN diagnosis-local ambiguity contract; production code unchanged.

RACKET_ANATOMY_PROBE_IMPL=baseline bypasses the proposed policy to reproduce
contract failures. Default uses only the diagnosis-local proposed wrapper.
"""

from __future__ import annotations

import copy
import dataclasses
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anatomical_abstention_prototype import abstain_selected_owner, veto_then_rerank

from bai_badminton.perception_types import PersonObs, RacketObservation


def fixture(face="overlap"):
    observation = RacketObservation((200, 120), (44, 64), 0, 0.95, 9)
    joints = np.zeros((17, 3), float)
    face_center = {"overlap": (200, 120), "near_overhead": (200, 175)}[face]
    for index, (dx, dy) in enumerate(((0, 0), (-4, -3), (4, -3), (-9, 0), (9, 0))):
        joints[index] = [face_center[0] + dx, face_center[1] + dy, 0.9]
    joints[9] = [200, 205, 0.95]
    person = PersonObs(7, np.array([150, 180, 250, 380]), 0.95, kps=joints, detector_matched=True, pose_frame_idx=100)
    return {"7": dataclasses.asdict(observation)}, [person]


def policy(selected, persons):
    if os.environ.get("RACKET_ANATOMY_PROBE_IMPL") == "baseline":
        return {"retained": copy.deepcopy(selected), "ambiguity": []}
    return abstain_selected_owner(selected, persons, 100)


def test_selected_head_alias_abstains_and_preserves_candidate_reason():
    selected, persons = fixture()
    original = copy.deepcopy(selected)
    result = policy(selected, persons)
    assert result["retained"] == {}
    assert result["ambiguity"][0]["reason"] == "racket_anatomical_alias"
    assert result["ambiguity"][0]["candidate"] == original["7"]
    assert selected == original


@pytest.mark.parametrize("angle,scale", [(0, 0.5), (35, 1), (75, 2), (180, 3)])
def test_face_alias_contract_is_rigid_rotation_and_scale_covariant(angle, scale):
    selected, persons = fixture()
    matrix = np.eye(3)
    matrix[:2] = cv2.getRotationMatrix2D((200, 200), angle, scale)
    matrix[:2, 2] += 500
    obs = RacketObservation(**selected["7"]).transformed(matrix)
    selected["7"] = dataclasses.asdict(obs)
    xy = np.column_stack((persons[0].kps[:, :2], np.ones(17))) @ matrix.T
    persons[0].kps[:, :2] = xy[:, :2] / xy[:, 2:3]
    assert policy(selected, persons)["retained"] == {}


def test_near_face_overhead_racket_outside_face_landmarks_is_retained():
    selected, persons = fixture("near_overhead")
    assert policy(selected, persons)["retained"] == selected


def test_actual_racket_over_occluded_face_is_explicitly_ambiguous_not_a_head_label():
    selected, persons = fixture()
    persons[0].kps[3:5, 2] = 0.1  # Nose and two eyes still support an anatomical alias.
    result = policy(selected, persons)
    assert result["retained"] == {}
    assert result["ambiguity"][0]["status"] == "ambiguous"


@pytest.mark.parametrize(
    "missing",
    ["pose", "all_confidence", "only_two_reliable", "source_stamp", "stale_source", "stale_person", "collapsed_joints"],
)
def test_missing_or_unreliable_anatomy_does_not_invent_alias(missing):
    selected, persons = fixture()
    person = persons[0]
    if missing == "pose":
        person.kps = None
    elif missing == "all_confidence":
        person.kps[:5, 2] = 0.1
    elif missing == "only_two_reliable":
        person.kps[2:5, 2] = 0.1
    elif missing == "source_stamp":
        person.pose_frame_idx = None
    elif missing == "stale_source":
        person.pose_frame_idx = 99
    elif missing == "stale_person":
        person.detector_matched = False
    elif missing == "collapsed_joints":
        person.kps[:5, :2] = [200, 120]
    assert policy(selected, persons)["retained"] == selected


def test_other_person_head_alias_in_doubles_is_also_ambiguous():
    selected, persons = fixture("near_overhead")
    _, other = fixture()
    other[0].track_id = 8
    persons += other
    result = policy(selected, persons)
    assert result["retained"] == {}
    assert result["ambiguity"][0]["aliases"][0]["person_track_id"] == 8


def test_whole_owner_abstention_does_not_promote_lower_ranked_jersey():
    selected, persons = fixture()
    first = dict(selected["7"], track_id=7, uncalibrated_support=0.95, length_body_ratio=0.3)
    lower = dict(first, center=(240, 160), axes=(20, 30), uncalibrated_support=0.8)
    trace = {"accepted_proposals": [first, lower]}
    assert veto_then_rerank(trace, persons, 100)["7"]["center"] == (240, 160)
    assert policy(selected, persons)["retained"] == {}


def test_unrelated_owners_candidate_is_preserved():
    selected, persons = fixture()
    selected["8"] = dict(selected["7"], center=(300, 100))
    result = policy(selected, persons)
    assert set(result["retained"]) == {"8"}
