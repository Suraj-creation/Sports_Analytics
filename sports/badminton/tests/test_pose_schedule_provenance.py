"""The configured pose cadence survives buffering, participant views and caching."""
from dataclasses import replace
from types import SimpleNamespace

import msgpack
import numpy as np
import pytest
from test_participant_epochs import setup
from test_plugin_discipline import make_session

from bai_badminton.participant_contact import participant_window
from bai_badminton.perception.calibration_state import CalibrationLifecycle, CalibrationState
from bai_badminton.perception.pipeline import BadmintonPerception, PerceptionStats, _Scene
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
from bai_badminton.plugin import StaleCacheError
from bai_engine.decode import DecodedChunk


def scheduled_chunk():
    frames = [FramePerception(
        frame_idx=i, shuttle_xy=None, shuttle_conf=0.,
        persons=[PersonObs(5, np.array([300., 400., 330., 650.]), .95)],
        calibration_state=CalibrationState.VALID, detector_observed=True,
        pose_stride=stride,
    ) for i, stride in enumerate((2, 2, 0, None))]
    return ChunkPerception(0, 3, frames, models={'player_detector': 'test'})


def test_pose_cadence_survives_engine_and_participant_windows(tmp_path):
    engine, _, _ = setup(tmp_path)
    engine.ingest(scheduled_chunk())
    window = engine._window(0, 3)
    assert window.pose_stride.tolist() == [2, 2, 0, -1]
    visual = participant_window(window, engine._participant_frames[:4])
    assert visual.pose_stride.tolist() == [2, 2, 0, -1]
    assert engine._window(2, 3).pose_stride.tolist() == [0, -1]


def test_pose_schedule_roundtrips_and_old_geometry_cache_is_rejected(tmp_path):
    session = make_session(tmp_path, 'doubles')
    payload = session.encode_perception(scheduled_chunk())
    assert [x.pose_stride for x in session.decode_perception(payload).frames] == [2, 2, 0, None]
    data = msgpack.unpackb(payload, raw=False)
    data['v'] = 7
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(data, use_bin_type=True))


@pytest.mark.parametrize('bad', [-1, 1.5, True, '2'])
def test_cache_does_not_accept_invalid_pose_schedule(tmp_path, bad):
    session = make_session(tmp_path, 'doubles')
    data = msgpack.unpackb(session.encode_perception(scheduled_chunk()), raw=False)
    data['frames'][0]['ps'] = bad
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(data, use_bin_type=True))


def test_pipeline_records_actual_idle_and_play_cadence_without_claiming_pose_observations():
    p = BadmintonPerception.__new__(BadmintonPerception)
    p.profile = SimpleNamespace(detector_rates=SimpleNamespace(in_play=1, idle=1),
        pose_rates=SimpleNamespace(in_play=2, idle=3))
    p.mode = 'lines'
    p._lines_id = 123
    p._H_ref = np.eye(3)
    p._ref_poly = None
    p.camera = SimpleNamespace(_st=None)
    p.cuts = SimpleNamespace(update=lambda frame: False, shot_id=0)
    p.players = SimpleNamespace(pose=object(), on_cut=lambda: None, set_roi=lambda roi: None,
        process=lambda *args: [], last_capacity_limited=False, last_detector_observed=False)
    p._rate = lambda *args: None
    p._read_scoreboard = lambda *args: []
    p.shuttle = None
    p.stats = PerceptionStats()
    p.models = {}
    p.degraded = []
    p.calibration_lifecycle = CalibrationLifecycle()
    p._calibration_last_frame = None
    polygon = np.array([[0., 0.], [10., 0.], [10., 10.], [0., 10.]])
    p._scene = lambda chunk, cuts: _Scene(['main'] * len(chunk.frames), [0] * len(chunk.frames),
        [.9] * len(chunk.frames), [np.eye(3)] * len(chunk.frames), [polygon] * len(chunk.frames),
        [False] * len(chunk.frames))
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    idle = p.process(DecodedChunk(0, [frame] * 3), False)
    playing = p.process(DecodedChunk(3, [frame] * 3), True)
    p.players.pose = None
    disabled = p.process(DecodedChunk(6, [frame] * 3), True)
    assert [f.pose_stride for f in idle.frames] == [3, 3, 3]
    assert [f.pose_stride for f in playing.frames] == [2, 2, 2]
    assert [f.pose_stride for f in disabled.frames] == [0, 0, 0]
    assert all(not f.persons for f in idle.frames + playing.frames + disabled.frames)


def test_pose_schedule_remains_aligned_after_engine_buffer_trim(tmp_path):
    engine, _, _ = setup(tmp_path)
    engine.cfg = replace(engine.cfg, history=6, context_back=3)
    frames = [FramePerception(
        frame_idx=i, shuttle_xy=None, shuttle_conf=0.,
        calibration_state=CalibrationState.VALID, detector_observed=True,
        pose_stride=2 if i < 20 else 3,
    ) for i in range(40)]
    engine.ingest(ChunkPerception(0, 39, frames, models={'player_detector': 'test'}))
    engine._final = 30
    engine._trim()
    assert engine._buf0 > 20
    assert engine._window(31, 39).pose_stride.tolist() == [3] * 9
