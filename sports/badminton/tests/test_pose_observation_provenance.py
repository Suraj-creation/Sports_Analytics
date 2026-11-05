"""Executed pose output provenance, distinct from scheduling and box carry."""

import numpy as np
import pytest

from bai_badminton.perception.players import PlayerPerception
from bai_badminton.perception_types import PersonObs


def keypoints():
    value = np.full((17, 3), np.nan)
    value[9] = [10, 20, 0.8]
    return value


class Pose:
    def __init__(self, output=None):
        self.output = keypoints() if output is None else output
        self.calls = []

    def __call__(self, image, boxes):
        self.calls.append((image.copy(), [box.copy() for box in boxes]))
        return [self.output for _ in boxes]


def person():
    return PersonObs(
        track_id=1, bbox=np.asarray([2.0, 2.0, 12.0, 22.0]), conf=0.9, raw_track_id=1, detector_matched=True
    )


def test_actual_valid_pose_call_records_its_exact_source_frame():
    pose = Pose()
    pipeline = PlayerPerception(None, pose, 30)
    detected = person()
    pipeline._attach(12, np.zeros((30, 30, 3), np.uint8), [detected], 3)
    assert len(pose.calls) == 1
    assert detected.pose_frame_idx == 12
    np.testing.assert_array_equal(detected.kps, pose.output)


@pytest.mark.parametrize("stride,frame", [(0, 12), (-1, 12), (3, 13)])
def test_disabled_or_unscheduled_pose_cannot_stamp_source_identity(stride, frame):
    pose = Pose()
    pipeline = PlayerPerception(None, pose, 30)
    detected = person()
    detected.kps = keypoints()  # Stale values do not prove a new pose execution.
    pipeline._attach(frame, np.zeros((30, 30, 3), np.uint8), [detected], stride)
    assert pose.calls == []
    assert detected.pose_frame_idx is None


def test_scheduled_tick_with_missing_provider_stays_unknown():
    pipeline = PlayerPerception(None, None, 30)
    detected = person()
    detected.kps = keypoints()
    pipeline._attach(12, np.zeros((30, 30, 3), np.uint8), [detected], 1)
    assert detected.pose_frame_idx is None


@pytest.mark.parametrize("output", [np.full((17, 3), np.nan), np.zeros((17, 3)), np.ones((16, 3)), np.ones((17, 2))])
def test_missing_or_invalid_person_pose_is_not_stamped_as_observed(output):
    pose = Pose(output)
    pipeline = PlayerPerception(None, pose, 30)
    detected = person()
    pipeline._attach(12, np.zeros((30, 30, 3), np.uint8), [detected], 1)
    assert len(pose.calls) == 1
    assert detected.pose_frame_idx is None


def test_pose_dropout_is_not_replaced_by_scheduled_frame_identity():
    class MissingPose:
        def __call__(self, _image, boxes):
            return [None for _ in boxes]

    pipeline = PlayerPerception(None, MissingPose(), 30)
    detected = person()
    pipeline._attach(12, np.zeros((30, 30, 3), np.uint8), [detected], 1)
    assert detected.kps is None and detected.pose_frame_idx is None


def test_detector_carried_box_can_still_have_actual_current_frame_pose():
    pose = Pose()
    pipeline = PlayerPerception(None, pose, 30)
    pipeline._last = [person()]
    pipeline._last_detection_frame = 10
    carried = pipeline._carry(11, np.zeros((30, 30, 3), np.uint8), 1, 2)
    assert len(carried) == len(pose.calls) == 1
    assert carried[0].detector_matched is False
    assert carried[0].pose_frame_idx == 11


def test_carried_box_does_not_inherit_previous_pose_on_unscheduled_frame():
    pose = Pose()
    pipeline = PlayerPerception(None, pose, 30)
    previous = person()
    pipeline._attach(10, np.zeros((30, 30, 3), np.uint8), [previous], 1)
    pipeline._last, pipeline._last_detection_frame = [previous], 10
    carried = pipeline._carry(11, np.zeros((30, 30, 3), np.uint8), 2, 2)
    assert carried[0].pose_frame_idx is None and carried[0].kps is None
    assert previous.pose_frame_idx == 10


def test_cut_reset_prevents_pose_or_box_evidence_reviving_from_last_track():
    pose = Pose()
    pipeline = PlayerPerception(None, pose, 30)
    pipeline._last, pipeline._last_detection_frame = [person()], 10
    pipeline.on_cut()
    assert pipeline._carry(11, np.zeros((30, 30, 3), np.uint8), 1, 2) == []
    assert pose.calls == []


def test_independent_legacy_observation_with_keypoints_has_unknown_pose_source():
    observation = person()
    observation.kps = keypoints()
    assert observation.pose_frame_idx is None


def test_reused_provider_output_buffer_cannot_rewrite_older_pose_observation():
    pose = Pose()
    pipeline = PlayerPerception(None, pose, 30)
    detected = person()
    pipeline._attach(12, np.zeros((30, 30, 3), np.uint8), [detected], 1)
    original = detected.kps.copy()
    pose.output[9, 0] = 999
    np.testing.assert_array_equal(detected.kps, original)


def test_four_person_pose_execution_records_each_success_independently():
    class MixedPose:
        def __call__(self, _image, boxes):
            assert len(boxes) == 4
            return [keypoints(), None, np.zeros((17, 3)), keypoints()]

    pipeline = PlayerPerception(None, MixedPose(), 30, max_players=4)
    people = [person() for _ in range(4)]
    pipeline._attach(12, np.zeros((30, 30, 3), np.uint8), people, 1)
    assert [p.pose_frame_idx for p in people] == [12, None, None, 12]


def test_reused_person_does_not_retain_old_frame_stamp_when_pose_does_not_run():
    pose = Pose()
    pipeline = PlayerPerception(None, pose, 30)
    detected = person()
    pipeline._attach(12, np.zeros((30, 30, 3), np.uint8), [detected], 1)
    assert detected.pose_frame_idx == 12
    pipeline._attach(13, np.zeros((30, 30, 3), np.uint8), [detected], 2)
    assert detected.pose_frame_idx is None
