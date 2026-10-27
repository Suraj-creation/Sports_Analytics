"""Camera loss must also invalidate the camera row used by analytics."""

import numpy as np

from bai_badminton.engine import camera_sample
from bai_badminton.perception_types import FramePerception


def test_camera_lost_rejects_even_a_stale_pose():
    sample = camera_sample(
        FramePerception(
            frame_idx=0, shuttle_xy=None, shuttle_conf=0, cam=np.eye(3), cam_lost=True, head=0, court_q=0.99
        )
    )
    assert sample.visible is False
    assert sample.cam is None


def test_nonvalid_calibration_cannot_mark_camera_sample_visible():
    from bai_badminton.perception.calibration_state import CalibrationState

    sample = camera_sample(
        FramePerception(
            frame_idx=0,
            shuttle_xy=None,
            shuttle_conf=0,
            cam=np.eye(3),
            head=0,
            court_q=0.99,
            calibration_state=CalibrationState.REACQUIRING,
        )
    )
    assert sample.visible is False
    assert sample.cam is None


def test_singular_or_nonfinite_camera_pose_is_never_valid():
    from bai_badminton.perception.calibration_state import CalibrationState

    for pose in (np.zeros((3, 3)), np.full((3, 3), np.nan)):
        sample = camera_sample(
            FramePerception(
                frame_idx=0,
                shuttle_xy=None,
                shuttle_conf=0,
                cam=pose,
                head=0,
                court_q=0.99,
                calibration_state=CalibrationState.VALID,
            )
        )
        assert sample.visible is False
        assert sample.cam is None


def test_alternate_view_without_head_never_becomes_main_camera():
    from bai_badminton.perception.calibration_state import CalibrationState

    sample = camera_sample(
        FramePerception(
            frame_idx=0,
            shuttle_xy=None,
            shuttle_conf=0,
            cam=np.eye(3),
            view="alt",
            head=None,
            court_q=0.99,
            calibration_state=CalibrationState.LOST,
        )
    )
    assert sample.visible and sample.track_id == -1


def test_alternate_view_with_contradictory_main_head_cannot_contaminate_main_camera():
    from bai_badminton.perception.calibration_state import CalibrationState

    sample = camera_sample(
        FramePerception(
            frame_idx=0,
            shuttle_xy=None,
            shuttle_conf=0,
            cam=np.eye(3),
            view="alt",
            head=0,
            court_q=0.99,
            calibration_state=CalibrationState.LOST,
        )
    )
    assert sample.track_id != 0
