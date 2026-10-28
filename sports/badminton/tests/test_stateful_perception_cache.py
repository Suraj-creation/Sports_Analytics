"""Opt-in ReID caches are diagnostic output, never a replacement for matcher state."""

from types import SimpleNamespace

import numpy as np
import pytest

from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.player_association import PersistentPlayerAssociator
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
from bai_badminton.plugin import BadmintonSession, StaleCacheError
from bai_engine.config import ModelChoice


def session(match_format, requested_model, state):
    value = BadmintonSession.__new__(BadmintonSession)
    choice = None if requested_model is None else ModelChoice(model=requested_model, backend="torch-cpu")
    value.perception = SimpleNamespace(
        match_format=match_format,
        profile=SimpleNamespace(player_reid=choice),
        identity_policy={"state": state},
        mode="static",
        ref_id=None,
    )
    value.calibration = None
    value._fixed_camera = None
    return value


@pytest.mark.parametrize("state", ["enabled", "degraded", "disabled"])
def test_requested_doubles_identity_requires_fresh_ordered_perception_even_when_degraded(state):
    value = session("doubles", "osnet_ain_x0_25", state)
    assert value.requires_sequential_perception is True
    frame = FramePerception(0, None, 0, calibration_state=CalibrationState.VALID, detector_observed=True)
    encoded = value.encode_perception(ChunkPerception(0, 0, [frame]))
    assert encoded  # Diagnostic writes remain available without persisting galleries.
    with pytest.raises(StaleCacheError, match="sequential"):
        value.decode_perception(encoded)


@pytest.mark.parametrize("match_format,model", [("singles", "osnet_ain_x0_25"), ("doubles", None), ("doubles", "none")])
def test_default_and_disabled_identity_modes_keep_cache_roundtrips(match_format, model):
    value = session(match_format, model, "disabled")
    assert value.requires_sequential_perception is False
    frame = FramePerception(0, None, 0, calibration_state=CalibrationState.VALID, detector_observed=True)
    assert value.decode_perception(value.encode_perception(ChunkPerception(0, 0, [frame]))).start == 0


def test_cache_reuse_is_rejected_when_a_cold_birth_collides_with_another_cached_person():
    tracks = [(1, np.array([10.0, 10.0, 40.0, 110.0]), 0.9), (2, np.array([100.0, 10.0, 130.0, 110.0]), 0.9)]
    features = np.eye(2, 512)
    continuous = PersistentPlayerAssociator(fps=30)
    for frame in (0, 20, 40, 60):
        assert continuous.update(frame, tracks[:1], features[:1], observed=[True]) == [1]
    assert continuous.update(64, tracks, features, observed=[True, True]) == [1, 1025]
    for frame in (84, 104, 124):
        continuous.update(frame, tracks, features, observed=[True, True])
    cached_b = continuous.update(128, tracks[1:], features[1:], observed=[True])[0]
    cold = PersistentPlayerAssociator(fps=30)
    cold_a = cold.update(64, tracks, features, observed=[True, True])[0]
    assert cold_a == cached_b == 1025  # These IDs identify different physical people.

    value = session("doubles", "osnet_ain_x0_25", "enabled")
    person = PersonObs(cached_b, tracks[1][1], 0.9, raw_track_id=2, detector_matched=True)
    frame = FramePerception(
        128, None, 0, persons=[person], calibration_state=CalibrationState.VALID, detector_observed=True
    )
    payload = value.encode_perception(ChunkPerception(128, 128, [frame]))
    with pytest.raises(StaleCacheError, match="sequential"):
        value.decode_perception(payload)
