"""Cache and consumer provenance survives registration; legacy sources stay unknown."""

from dataclasses import replace

import msgpack
import numpy as np
import pytest

from bai_badminton.engine import _stabilise
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs, RacketObservation
from bai_badminton.plugin import StaleCacheError


def person():
    return PersonObs(
        1,
        np.array([0.0, 0.0, 100.0, 200.0]),
        0.9,
        kps=np.ones((17, 3)),
        pose_frame_idx=25,
        racket=RacketObservation((20.0, 20.0), (10.0, 20.0), 0.0, 0.8, 9),
        racket_frame_idx=25,
    )


def test_camera_registration_preserves_actual_observation_sources():
    result = _stabilise(person(), np.array([[1.0, 0.0, 12.0], [0.0, 1.0, 25.0], [0.0, 0.0, 1.0]]))
    assert result.pose_frame_idx == result.racket_frame_idx == 25
    assert result.kps[0, 0] == 13.0


@pytest.mark.parametrize("source", ["pose_frame_idx", "racket_frame_idx"])
def test_frame_rejects_future_source_metadata(source):
    with pytest.raises(ValueError, match="source frame"):
        FramePerception(25, None, 0.0, persons=[replace(person(), **{source: 26})])


def test_current_pose_and_racket_sources_roundtrip_without_inventing_legacy_freshness(tmp_path):
    from test_perception_diagnostic_provenance import _non30_cache_session

    session = _non30_cache_session(tmp_path)
    frame = FramePerception(
        25,
        None,
        0.0,
        persons=[person()],
        calibration_state=CalibrationState.VALID,
        detector_observed=True,
        pose_stride=1,
    )
    encoded = session.encode_perception(ChunkPerception(25, 25, [frame]))
    current = session.decode_perception(encoded, diagnostic=True).frames[0].persons[0]
    assert current.pose_frame_idx == current.racket_frame_idx == 25
    record = msgpack.unpackb(encoded, raw=False)
    record["v"] = 18
    del record["frames"][0]["p"][0]["pf"]
    del record["frames"][0]["p"][0]["rf"]
    legacy = session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True).frames[0].persons[0]
    assert legacy.kps is not None and legacy.racket is not None
    assert legacy.pose_frame_idx is legacy.racket_frame_idx is None
    session.close()


@pytest.mark.parametrize("key", ["pf", "rf"])
def test_cache_rejects_detached_future_observation_source(tmp_path, key):
    from test_perception_diagnostic_provenance import _non30_cache_session

    session = _non30_cache_session(tmp_path)
    frame = FramePerception(
        25,
        None,
        0.0,
        persons=[person()],
        calibration_state=CalibrationState.VALID,
        detector_observed=True,
        pose_stride=1,
    )
    record = msgpack.unpackb(session.encode_perception(ChunkPerception(25, 25, [frame])), raw=False)
    record["frames"][0]["p"][0][key] = 26
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
    session.close()
