"""Unavailable court geometry must not erase current image detections."""

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
from bai_engine.schema import TrackObject
from bai_engine.store import EventStore


@pytest.mark.parametrize("replay", [False, True])
def test_image_observations_survive_reacquisition_without_projected_facts(tmp_path, replay):
    with EventStore(tmp_path / "events.sqlite", "S1") as store:
        engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=762, frame_height=720), store)
        frames = [FramePerception(
            frame_idx=frame, shuttle_xy=None, shuttle_conf=0,
            persons=[PersonObs(
                track_id=person, raw_track_id=person, bbox=np.array([10, 20, 50, 100], dtype=float),
                conf=0.9, detector_matched=True,
            ) for person in range(4)],
            detector_observed=True, replay=replay, calibration_state=CalibrationState.REACQUIRING,
        ) for frame in range(2)]
        engine.ingest(ChunkPerception(0, 1, frames))
        rows = [r for r in engine.drain_tracks() if r.obj is TrackObject.PLAYER]
        assert len(rows) == (0 if replay else 8)
        assert all(r.player_id is None and r.participant_observation_id is None for r in rows)
        assert all(r.court_x is None and r.court_y is None for r in rows)
        assert all(r.detector_matched is True and r.context_id is not None for r in rows)
        assert not store.query(types=["participant_observation", "point", "stroke"])
