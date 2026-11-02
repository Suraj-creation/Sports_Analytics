"""Raw overlay evidence cannot become motion in a different image coordinate frame."""

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.testing.synth import broadcast_homography
from bai_engine.schema import TrackObject
from bai_engine.store import EventStore


def _engine(tmp_path):
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), EventStore(tmp_path / "e.sqlite", "S1")
    )
    engine.set_calibration(0, broadcast_homography(), cam_ref=10)
    return engine


def _frame(i, *, lost=False, cam=None):
    if cam is None and not lost:
        cam = np.array([[1.0, 0, 100], [0, 1, 0], [0, 0, 1]])
    return FramePerception(
        frame_idx=i,
        shuttle_xy=(100.0 + i * 10, 200.0),
        shuttle_conf=0.9,
        cam=cam,
        cam_lost=lost,
        view="main",
        calibration_state=CalibrationState.VALID,
    )


def test_stabilization_loss_is_not_filled_or_used_as_observed_motion(tmp_path):
    engine = _engine(tmp_path)
    frames = [_frame(i, lost=i in (4, 5)) for i in range(10)]
    engine.ingest(ChunkPerception(0, 9, frames, cam_ref=10))
    window = engine._window(0, 9)
    assert not window.shuttle.vis[4:6].any()
    assert not window.shuttle.interp[4:6].any()
    assert window.break_before.tolist() == [False, False, False, False, True, False, True, False, False, False]
    assert window.shuttle.x[3] == pytest.approx(30)
    assert window.shuttle.x[6] == pytest.approx(60)
    raw = {sample.frame_idx: sample for sample in engine.drain_tracks() if sample.obj == TrackObject.SHUTTLE}
    assert raw[4].visible and raw[4].x == 140  # raw proxy pixels remain inspectable


def test_reference_mismatch_cannot_use_a_pose_from_another_reference(tmp_path):
    engine = _engine(tmp_path)
    engine.ingest(ChunkPerception(0, 3, [_frame(i) for i in range(4)], cam_ref=99))
    assert not engine._window(0, 3).shuttle.vis.any()
    cameras = [sample for sample in engine.drain_tracks() if sample.obj == TrackObject.CAMERA]
    assert len(cameras) == 4 and all(not sample.visible for sample in cameras)


@pytest.mark.parametrize("cam", [np.zeros((3, 3)), np.full((3, 3), np.nan), np.eye(2)])
def test_invalid_pose_is_unavailable_even_without_lost_flag(tmp_path, cam):
    engine = _engine(tmp_path)
    engine.ingest(ChunkPerception(0, 3, [_frame(i, cam=cam) for i in range(4)], cam_ref=10))
    assert not engine._window(0, 3).shuttle.vis.any()


def test_usable_poses_share_one_stabilized_reference(tmp_path):
    engine = _engine(tmp_path)
    frames = []
    for i in range(10):
        camera = np.array([[1.0, 0, 100 + i], [0, 1, 0], [0, 0, 1]])
        frame = _frame(i, cam=camera)
        frame.shuttle_xy = (100 + i * 11.0, 200.0)
        frames.append(frame)
    engine.ingest(ChunkPerception(0, 9, frames, cam_ref=10))
    window = engine._window(0, 9)
    assert not window.break_before.any()
    np.testing.assert_allclose(window.shuttle.x, np.arange(10) * 10)


def test_calibration_change_starts_a_new_temporal_context(tmp_path):
    engine = _engine(tmp_path)
    engine.ingest(ChunkPerception(0, 3, [_frame(i) for i in range(4)], cam_ref=10))
    engine.set_calibration(0, broadcast_homography(), cam_ref=10)
    engine.ingest(ChunkPerception(4, 7, [_frame(i) for i in range(4, 8)], cam_ref=10))
    assert engine._window(0, 7).break_before[4]


def test_uncalibrated_alternate_view_is_not_a_raw_motion_continuation(tmp_path):
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), EventStore(tmp_path / "raw.sqlite", "S1")
    )
    frames = [_frame(i) for i in range(10)]
    for frame in frames[4:6]:
        frame.view = "alt"
    engine.ingest(ChunkPerception(0, 9, frames))
    window = engine._window(0, 9)
    assert not window.shuttle.vis[4:6].any()
    assert window.break_before[4] and window.break_before[6]
