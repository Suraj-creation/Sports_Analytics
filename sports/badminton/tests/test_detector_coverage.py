"""Detector coverage means an actual call, not a carried or missing detection."""

from types import SimpleNamespace

import msgpack
import numpy as np
import pytest

from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.players import PlayerPerception
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import BadmintonSession, StaleCacheError


def test_detector_call_is_distinguished_from_carry_and_unavailable():
    calls = []

    def detect(img):
        calls.append(img.shape)
        return np.empty((0, 4)), np.empty((0,))

    players = PlayerPerception(detect, None, fps=30)
    image = np.zeros((40, 40, 3), np.uint8)
    players.process(0, image, (2, 0))
    assert players.last_detector_observed is True
    players.process(1, image, (2, 0))
    assert players.last_detector_observed is False
    players.process(2, image, (0, 0))
    assert players.last_detector_observed is False
    assert len(calls) == 1


def test_detector_coverage_roundtrip_and_missing_metadata_is_stale():
    session = BadmintonSession.__new__(BadmintonSession)
    session.perception = SimpleNamespace(ref_id=None, mode="static")
    session.calibration = None
    session._fixed_camera = None
    f = FramePerception(
        frame_idx=0, shuttle_xy=None, shuttle_conf=0, calibration_state=CalibrationState.VALID, detector_observed=True
    )
    encoded = session.encode_perception(ChunkPerception(start=0, end=0, frames=[f]))
    assert session.decode_perception(encoded).frames[0].detector_observed is True
    decoded = msgpack.unpackb(encoded, raw=False)
    del decoded["frames"][0]["do"]
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(decoded, use_bin_type=True))
