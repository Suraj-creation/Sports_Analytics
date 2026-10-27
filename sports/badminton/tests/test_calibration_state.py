"""Calibration transitions do not infer confidence from a single recovered fit."""

from bai_badminton.perception.calibration_state import CalibrationLifecycle, CalibrationState


def test_recovery_requires_consecutive_verified_geometry():
    state = CalibrationLifecycle(recovery_frames=3)
    assert state.update(verified=True) == CalibrationState.REACQUIRING
    assert state.update(verified=True) == CalibrationState.REACQUIRING
    assert state.update(verified=True) == CalibrationState.VALID
    assert state.update(verified=False, held=True) == CalibrationState.DEGRADED
    assert state.update(verified=False) == CalibrationState.LOST
    assert state.update(verified=True) == CalibrationState.REACQUIRING
    assert state.update(verified=False) == CalibrationState.LOST
    assert [state.update(verified=True) for _ in range(3)] == [
        CalibrationState.REACQUIRING,
        CalibrationState.REACQUIRING,
        CalibrationState.VALID,
    ]


def test_camera_cut_and_unverified_static_do_not_preserve_validity():
    state = CalibrationLifecycle(recovery_frames=2)
    state.update(verified=True)
    assert state.update(verified=True) == CalibrationState.VALID
    assert state.update(verified=True, cut=True) == CalibrationState.REACQUIRING
    assert state.update(verified=False, held=True) == CalibrationState.DEGRADED
    assert state.update(verified=True) == CalibrationState.REACQUIRING


def test_cache_roundtrip_and_missing_state_rejection():
    from types import SimpleNamespace

    import msgpack
    import pytest

    from bai_badminton.perception_types import ChunkPerception, FramePerception
    from bai_badminton.plugin import BadmintonSession, StaleCacheError

    session = BadmintonSession.__new__(BadmintonSession)
    session.perception = SimpleNamespace(ref_id=None, mode="static")
    session.calibration = None
    session._fixed_camera = None
    fp = FramePerception(
        frame_idx=0,
        shuttle_xy=None,
        shuttle_conf=0,
        calibration_state=CalibrationState.DEGRADED,
        detector_observed=True,
    )
    encoded = session.encode_perception(ChunkPerception(start=0, end=0, frames=[fp]))
    assert session.decode_perception(encoded).frames[0].calibration_state == CalibrationState.DEGRADED
    data = msgpack.unpackb(encoded, raw=False)
    del data["frames"][0]["cs"]
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(data, use_bin_type=True))
    data["v"] = 6
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(data, use_bin_type=True))


def test_perception_publishes_recovery_across_chunks(monkeypatch):
    from types import SimpleNamespace

    import numpy as np

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
    p.players = SimpleNamespace(on_cut=lambda: None, set_roi=lambda roi: None, process=lambda *args: [])
    p._rate = lambda *args: None
    p._read_scoreboard = lambda *args: []
    p.shuttle = None
    p.stats = PerceptionStats()
    p.models = {}
    p.calibration_lifecycle = CalibrationLifecycle()
    p._calibration_last_frame = None
    polygon = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]])

    def scene(chunk, cuts):
        n = len(chunk.frames)
        return _Scene(["main"] * n, [0] * n, [0.9] * n, [np.eye(3)] * n, [polygon] * n, [False] * n)

    p._scene = scene
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    first = p.process(DecodedChunk(start=0, frames=[frame, frame]), False)
    second = p.process(DecodedChunk(start=2, frames=[frame]), False)
    assert [x.calibration_state for x in first.frames] == [CalibrationState.REACQUIRING] * 2
    assert second.frames[0].calibration_state == CalibrationState.VALID
    # A non-contiguous seek must begin a new acquisition, not reuse prior state.
    assert (
        p.process(DecodedChunk(start=20, frames=[frame]), False).frames[0].calibration_state
        == CalibrationState.REACQUIRING
    )
