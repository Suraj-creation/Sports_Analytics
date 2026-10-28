"""Doubles retains extra court candidates without pretending they are players."""
from types import SimpleNamespace

import numpy as np
import pytest
from test_plugin_discipline import make_session

from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.players import PlayerPerception
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import StaleCacheError


def _tracks(count):
    return [(i, np.array([10.0 + i * 8, 4.0, 16.0 + i * 8, 30.0]), 0.9) for i in range(count)]


def _perception(count, max_players):
    p = PlayerPerception(lambda image: (np.empty((0, 4)), np.empty(0)), None, fps=30, max_players=max_players)
    p.tracker = SimpleNamespace(update=lambda boxes, scores: _tracks(count))
    return p


def test_doubles_keeps_five_and_six_candidates_without_assigning_identity():
    image = np.zeros((80, 100, 3), dtype=np.uint8)
    for count in (5, 6):
        p = _perception(count, 4)
        results = p.process(0, image, (2, 0))
        assert len(results) == count
        assert {x.track_id for x in results} == set(range(count))
        assert p.last_detector_observed is True
        assert p.last_capacity_limited is False


def test_doubles_overflow_is_unavailable_not_silently_truncated():
    image = np.zeros((80, 100, 3), dtype=np.uint8)
    p = _perception(7, 4)
    assert p.process(0, image, (2, 0)) == []
    assert p.last_capacity_limited is True
    assert p.last_detector_observed is False
    assert p._admitted == {}
    assert p.process(1, image, (2, 0)) == []
    assert p.last_detector_observed is False


def test_singles_keeps_existing_four_candidate_limit():
    image = np.zeros((80, 100, 3), dtype=np.uint8)
    p = _perception(6, 2)
    assert len(p.process(0, image, (1, 0))) == 4


@pytest.mark.parametrize("match_format, expected", [(None, 2), ("singles", 2), ("doubles", 4)])
def test_session_format_reaches_perception(tmp_path, match_format, expected):
    session = make_session(tmp_path, match_format)
    assert session.perception.players.max_players == expected


def test_legacy_doubles_cache_is_stale_after_capacity_policy_change(tmp_path):
    session = make_session(tmp_path, "doubles")
    frame = FramePerception(frame_idx=0, shuttle_xy=None, shuttle_conf=0,
        calibration_state=CalibrationState.VALID, detector_observed=True)
    payload = session.encode_perception(ChunkPerception(start=0, end=0, frames=[frame]))
    import msgpack
    data = msgpack.unpackb(payload, raw=False)
    assert data["ci"]["player_candidate_limit"] == 6
    del data["ci"]["player_candidate_limit"]
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(data, use_bin_type=True))


def test_legacy_singles_cache_policy_is_still_readable(tmp_path):
    session = make_session(tmp_path, "singles")
    frame = FramePerception(frame_idx=0, shuttle_xy=None, shuttle_conf=0,
        calibration_state=CalibrationState.VALID, detector_observed=True)
    chunk = ChunkPerception(start=0, end=0, frames=[frame])
    payload = session.encode_perception(chunk)
    import msgpack
    data = msgpack.unpackb(payload, raw=False)
    assert "player_candidate_limit" not in data["ci"]
    assert session.decode_perception(payload).frames[0].detector_observed is True


def test_pipeline_reports_capacity_degradation_once_and_withholds_detector_coverage():
    from bai_badminton.perception.calibration_state import CalibrationLifecycle
    from bai_badminton.perception.pipeline import BadmintonPerception, PerceptionStats, _Scene
    from bai_engine.decode import DecodedChunk

    p = BadmintonPerception.__new__(BadmintonPerception)
    rates = SimpleNamespace(in_play=1, idle=1)
    p.profile = SimpleNamespace(detector_rates=rates, pose_rates=rates)
    p.mode = "lines"
    p._lines_id = 123
    p._H_ref = np.eye(3)
    p._ref_poly = None
    p.camera = SimpleNamespace(_st=None)
    p.cuts = SimpleNamespace(update=lambda frame: False, shot_id=0)
    p.players = SimpleNamespace(on_cut=lambda: None, set_roi=lambda roi: None,
        process=lambda *args: [], last_capacity_limited=True, last_detector_observed=False)
    p._rate = lambda *args: None
    p._read_scoreboard = lambda *args: []
    p.shuttle = None
    p.stats = PerceptionStats()
    p.models = {}
    p.degraded = []
    p.calibration_lifecycle = CalibrationLifecycle()
    p._calibration_last_frame = None
    polygon = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]])
    p._scene = lambda chunk, cuts: _Scene(["main"] * len(chunk.frames), [0] * len(chunk.frames),
        [0.9] * len(chunk.frames), [np.eye(3)] * len(chunk.frames), [polygon] * len(chunk.frames),
        [False] * len(chunk.frames))
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    result = p.process(DecodedChunk(start=0, frames=[frame, frame, frame]), False)
    assert all(f.detector_observed is False and not f.persons for f in result.frames)
    assert len([d for d in p.degraded if d.stage == "player_tracking"]) == 1
    assert "withheld" in p.degraded[0].reason
