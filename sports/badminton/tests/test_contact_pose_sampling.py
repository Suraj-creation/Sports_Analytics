"""Only valid observed wrists may supply proximity and scheduled motion cues."""
import numpy as np
import pytest
from test_contact_attribution import contact_window

from bai_badminton.events.contact import _wrist_speed, score_frame
from bai_badminton.observations import PlayerSeries
from bai_badminton.perception.keypoints import KP


def test_visible_wrist_remains_usable_when_nose_is_occluded():
    window = contact_window([('P1', 100.)])
    window.players['P1'].kps[:, KP.L_WRIST] = [100., 100., 1.]
    contact = score_frame(window, 3)
    assert contact is not None
    assert contact.scores['proximity'] == pytest.approx(1.)


@pytest.mark.parametrize('column', [0, 1, 2])
@pytest.mark.parametrize('bad', [np.nan, np.inf])
def test_nonfinite_pose_cannot_poison_contact_probability(column, bad):
    window = contact_window([('P1', 0.)])
    pose = window.players['P1'].kps
    pose[:, 0] = [0., 0., 1.]
    pose[:, KP.L_WRIST] = [100., 100., 1.]
    pose[:, KP.L_WRIST, column] = bad
    pose[3, KP.L_WRIST] = [100., 100., 1.]
    contact = score_frame(window, 3)
    assert contact is not None and np.isfinite(contact.p)
    assert all(np.isfinite(v) for v in contact.scores.values())
    assert contact.scores['swing'] == 0.


def test_nonfinite_wrists_fall_back_to_observed_upper_box():
    window = contact_window([('P1', 0.)])
    pose = window.players['P1'].kps
    pose[:, 0] = [0., 0., 1.]
    pose[:, KP.L_WRIST] = [100., np.nan, 1.]
    contact = score_frame(window, 3)
    assert contact is not None
    assert contact.scores['proximity'] == pytest.approx(1.)


def motion_series(observed):
    series = PlayerSeries.empty(7)
    series.bbox[:] = [0., 0., 100., 100.]
    for i in observed:
        series.kps[i, KP.L_WRIST] = [10. * i, 100., 1.]
    return series


def test_strided_observed_motion_has_same_per_frame_speed_as_dense_motion():
    dense = motion_series(range(7))
    sparse = motion_series([0, 2, 4, 6])
    assert _wrist_speed(dense, 3) == pytest.approx(0.1)
    assert _wrist_speed(sparse, 3, pose_stride=np.full(7, 2)) == pytest.approx(0.1)


def test_absolute_pose_schedule_is_used_for_nonzero_window_start():
    sparse = motion_series([1, 3, 5])
    assert _wrist_speed(sparse, 3, frame0=1, pose_stride=np.full(7, 2)) == pytest.approx(0.1)


@pytest.mark.parametrize('cadence', [np.full(7, -1), np.zeros(7, dtype=int), np.full(7, 2)])
def test_sparse_motion_does_not_bridge_unknown_disabled_or_missing_scheduled_pose(cadence):
    sparse = motion_series([0, 4])  # scheduled observation at frame 2 is missing
    assert _wrist_speed(sparse, 3, pose_stride=cadence) is None


def test_sparse_motion_does_not_bridge_missing_track_or_newly_scheduled_pose():
    sparse = motion_series([0, 2])
    sparse.bbox[1] = np.nan
    assert _wrist_speed(sparse, 2, pose_stride=np.full(7, 2)) is None
    sparse = motion_series([0, 4])
    cadence = np.array([2, 2, 3, 3, 2, 2, 2])  # frame 3 is newly scheduled but missing
    assert _wrist_speed(sparse, 3, pose_stride=cadence) is None


@pytest.mark.parametrize('column', [0, 1, 2])
def test_nonfinite_keypoint_cannot_be_an_observed_motion_endpoint(column):
    sparse = motion_series([0, 2])
    sparse.kps[0, KP.L_WRIST, column] = np.nan
    assert _wrist_speed(sparse, 2, pose_stride=np.full(7, 2)) is None


def test_contact_fusion_consumes_scheduled_pose_motion():
    window = contact_window([('P1', 0.)])
    for i in (0, 2, 4, 6):
        window.players['P1'].kps[i, KP.L_WRIST] = [40. + 20. * i, 100., 1.]
    window.pose_stride = np.full(7, 2, dtype=np.int64)
    contact = score_frame(window, 3)
    assert contact is not None
    assert contact.scores['swing'] == pytest.approx(0.6)


def test_low_confidence_scheduled_pose_blocks_a_sparse_bridge():
    sparse = motion_series([0, 2, 4])
    sparse.kps[2, KP.L_WRIST, 2] = 0.1
    assert _wrist_speed(sparse, 3, pose_stride=np.full(7, 2)) is None


def test_known_schedule_rejects_off_schedule_pose_endpoints():
    sparse = motion_series([1, 3])
    assert _wrist_speed(sparse, 3, pose_stride=np.full(7, 2)) is None
