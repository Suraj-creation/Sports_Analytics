"""Participant identity must not silently survive broken observation continuity."""

from pathlib import Path

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
from bai_badminton.testing.synth import make_match
from bai_engine.schema import TrackObject
from bai_engine.store import EventStore


def setup(tmp_path: Path):
    match = make_match(["P1"])
    store = EventStore(tmp_path / "epochs.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, match.homography)
    return engine, store, match


def send(engine, start, end, *, shot=0, valid=True):
    frames = []
    for i in range(start, end + 1):
        person = PersonObs(track_id=5, bbox=np.array([300.0, 400.0, 330.0, 650.0]), conf=0.95)
        frames.append(
            FramePerception(
                frame_idx=i,
                shuttle_xy=None,
                shuttle_conf=0.0,
                persons=[person] if valid else [],
                shot_id=shot,
                calibration_state=CalibrationState.VALID if valid else CalibrationState.LOST,
                detector_observed=valid,
            )
        )
    engine.ingest(ChunkPerception(start=start, end=end, frames=frames, models={"player_detector": "test"}))


def assert_new_episode_without_singles_assignment(engine, store, first_id, cutoff):
    events = store.query(types=["participant_observation"])
    ids = {e.payload["participant_id"] for e in events}
    assert first_id in ids and len(ids) == 2
    assert store.query(types=["identity_ambiguity"])
    tracks = [t for t in engine.drain_tracks() if t.obj == TrackObject.PLAYER and t.frame_idx >= cutoff]
    assert all(t.player_id is None for t in tracks)


def first_episode(tmp_path):
    engine, store, match = setup(tmp_path)
    send(engine, 0, 3)
    events = store.query(types=["participant_observation"])
    assert len(events) == 1
    first_id = events[0].payload["participant_id"]
    engine.drain_tracks()
    return engine, store, match, first_id


def test_same_numeric_track_after_shot_change_is_not_same_participant(tmp_path: Path):
    engine, store, _, first_id = first_episode(tmp_path)
    send(engine, 4, 7, shot=1)
    assert_new_episode_without_singles_assignment(engine, store, first_id, 4)


def test_long_invalid_coverage_requires_new_participant_episode(tmp_path: Path):
    engine, store, _, first_id = first_episode(tmp_path)
    send(engine, 4, 64, valid=False)  # more than two seconds at 30 fps
    send(engine, 65, 68)
    assert_new_episode_without_singles_assignment(engine, store, first_id, 65)


def test_recalibration_requires_new_participant_episode(tmp_path: Path):
    engine, store, match, first_id = first_episode(tmp_path)
    engine.set_calibration(0, match.homography, cam_ref=123)
    send(engine, 4, 7)
    assert_new_episode_without_singles_assignment(engine, store, first_id, 4)


def test_brief_invalid_coverage_preserves_same_track(tmp_path: Path):
    engine, store, _, first_id = first_episode(tmp_path)
    send(engine, 4, 8, valid=False)
    send(engine, 9, 12)
    ids = {e.payload["participant_id"] for e in store.query(types=["participant_observation"])}
    assert ids == {first_id}
    assert not store.query(types=["identity_ambiguity"])


def send_detector_frames(engine, start, end, *, detector, carried):
    frames = [FramePerception(
        frame_idx=i, shuttle_xy=None, shuttle_conf=0.,
        persons=[PersonObs(5, np.array([300., 400., 330., 650.]), .95)] if carried else [],
        calibration_state=CalibrationState.VALID, detector_observed=detector,
    ) for i in range(start, end + 1)]
    engine.ingest(ChunkPerception(start, end, frames, models={'player_detector': 'test'}))


@pytest.mark.parametrize('detector', [False, None])
def test_long_empty_detector_outage_starts_new_epoch_only_when_observations_return(tmp_path, detector):
    engine, store, _, first_id = first_episode(tmp_path)
    send_detector_frames(engine, 4, 64, detector=detector, carried=False)
    assert not store.query(types=['identity_ambiguity'])
    assert not any(e.payload['kind'] == 'PLAYER_EXITED' for e in store.query(types=['participant_observation']))
    send(engine, 65, 68)
    births = [e for e in store.query(types=['participant_observation'])
        if e.payload['participant_id'] != first_id
        and e.payload['kind'] in ('PLAYER_ENTERED', 'PARTICIPANT_FIRST_OBSERVED')]
    assert len(births) == 1
    returned = [t for t in engine._track_out if t.obj == TrackObject.PLAYER and t.frame_idx in (67, 68)]
    assert {t.frame_idx for t in returned} == {67, 68}
    assert all(t.participant_observation_id == births[0].event_id for t in returned)
    assert_new_episode_without_singles_assignment(engine, store, first_id, 65)
    reset = store.query(types=['identity_ambiguity'])
    assert len(reset) == 1 and reset[0].frame_start == 65
    assert reset[0].payload['reason'] == 'prolonged_coverage_loss'


def test_long_carried_detector_outage_cannot_refresh_identity_coverage(tmp_path):
    engine, store, _, first_id = first_episode(tmp_path)
    send_detector_frames(engine, 4, 64, detector=False, carried=True)
    carried = engine._participant_frames[4:65]
    assert carried and all(first_id in frame for frame in carried)
    assert all(frame[first_id].detector_observed is False for frame in carried)
    assert all(frame[first_id].observation_id is not None for frame in carried)
    assert not store.query(types=['identity_ambiguity'])
    assert {e.payload['participant_id'] for e in store.query(types=['participant_observation'])} == {first_id}
    send(engine, 65, 68)
    assert_new_episode_without_singles_assignment(engine, store, first_id, 65)


def test_detector_continuity_has_the_existing_two_second_boundary(tmp_path):
    engine, store, _, first_id = first_episode(tmp_path)
    send_detector_frames(engine, 4, 62, detector=False, carried=True)
    send(engine, 63, 66)  # last observed frame 3 -> 63 is exactly two seconds
    assert {e.payload['participant_id'] for e in store.query(types=['participant_observation'])} == {first_id}
    assert not store.query(types=['identity_ambiguity'])
