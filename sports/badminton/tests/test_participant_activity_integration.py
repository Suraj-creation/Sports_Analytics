"""Per-frame visual evidence reaches the event timeline without assuming match identity."""

from pathlib import Path

import numpy as np

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
from bai_badminton.testing.synth import make_match
from bai_engine.store import EventStore


def test_four_participants_and_activity_are_recorded_without_scoring(tmp_path: Path):
    m = make_match(["P1"])
    store = EventStore(tmp_path / "integration.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, m.homography)
    frames = []
    for index in range(6):
        people = [
            PersonObs(track_id=i, bbox=np.array([100.0 * i, y - 80.0, 100.0 * i + 30, y]), conf=0.95)
            for i, y in [(1, 250.0), (2, 270.0), (3, 550.0), (4, 570.0)]
        ]
        frames.append(FramePerception(frame_idx=index, shuttle_xy=None, shuttle_conf=0.0, persons=people))
    engine.ingest(ChunkPerception(start=0, end=5, frames=frames, models={"player_detector": "test"}))
    engine.flush()
    entries = store.query(types=["participant_observation"])
    ids = {e.payload["participant_id"] for e in entries}
    assert len(ids) == 4
    assert all(e.payload["certainty"] == "hypothesis" for e in entries)
    activity = store.query(types=["activity_interval"])
    assert activity and activity[0].payload["state"] == "unknown"
    assert activity[0].payload["match_intent"] == "unknown"
    assert not store.query(types=["point"])


def test_unavailable_detector_does_not_claim_participation(tmp_path: Path):
    m = make_match(["P1"])
    store = EventStore(tmp_path / "missing.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, m.homography)
    frames = [FramePerception(frame_idx=i, shuttle_xy=None, shuttle_conf=0.0, persons=[]) for i in range(4)]
    engine.ingest(ChunkPerception(start=0, end=3, frames=frames))
    engine.flush()
    assert not store.query(types=["participant_observation"])
    activity = store.query(types=["activity_interval"])
    assert activity and activity[0].payload["state"] in ("unknown", "reacquiring")


def test_activity_integration_handles_sustained_motion_then_view_loss(tmp_path: Path):
    match = make_match(["P1"])
    store = EventStore(tmp_path / "activity.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=10, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, match.homography)
    frames = []
    for i in range(50):
        people = [
            PersonObs(track_id=n, bbox=np.array([100.0 * n + 3 * i, y - 80, 100.0 * n + 3 * i + 30, y]), conf=0.9)
            for n, y in [(1, 250.0), (2, 550.0)]
        ]
        frames.append(
            FramePerception(
                frame_idx=i,
                shuttle_xy=(500.0, 300.0),
                shuttle_conf=0.9,
                persons=people,
                view="none" if i >= 45 else "main",
            )
        )
    engine.ingest(ChunkPerception(start=0, end=49, frames=frames, models={"player_detector": "test"}))
    engine.flush()
    events = store.query(types=["activity_interval"])
    assert any(event.payload["state"] == "active_play" for event in events)
    assert events[-1].payload["state"] == "reacquiring"
    assert all(event.payload["match_intent"] == "unknown" for event in events)


def test_four_people_do_not_create_singles_player_attribution_when_some_disappear(tmp_path: Path):
    from bai_engine.schema import TrackObject

    match = make_match(["P1"])
    store = EventStore(tmp_path / "doubles.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, match.homography)
    frames = []
    for index in range(8):
        sides = [(1, 250.0), (2, 270.0), (3, 550.0), (4, 570.0)] if index < 4 else [(1, 250.0), (3, 550.0)]
        people = [
            PersonObs(track_id=n, bbox=np.array([100.0 * n, y - 80, 100.0 * n + 30, y]), conf=0.95) for n, y in sides
        ]
        frames.append(FramePerception(frame_idx=index, shuttle_xy=None, shuttle_conf=0.0, persons=people))
    engine.ingest(ChunkPerception(start=0, end=7, frames=frames, models={"player_detector": "test"}))
    tracks = [x for x in engine.drain_tracks() if x.obj == TrackObject.PLAYER]
    assert tracks and all(t.player_id is None for t in tracks)
    assert len({t.track_id for t in tracks}) == 4


def test_geometry_cannot_assign_team_winner_when_multiple_people_are_ambiguous(tmp_path: Path):
    from dataclasses import replace

    from bai_engine.schema import Provenance

    match = make_match(["P1", "P2"])
    store = EventStore(tmp_path / "ambiguous_score.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=match.fps, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, match.homography)
    engine.set_match_start(0, Provenance(model="human"))
    for chunk in match.chunks:
        frames = []
        for frame in chunk.frames:
            extra = PersonObs(track_id=991, bbox=np.array([750.0, 400.0, 780.0, 650.0]), conf=0.95)
            frames.append(replace(frame, persons=[*frame.persons, extra]))
        engine.ingest(replace(chunk, frames=frames, models={"player_detector": "test"}))
    engine.flush()
    rallies = store.query(types=["rally_end"])
    assert rallies and all(r.payload["winner"] is None for r in rallies)
    assert not store.query(types=["point"])


def test_restart_uses_new_participant_epoch_instead_of_silent_reidentification(tmp_path: Path):
    match = make_match(["P1"])
    store = EventStore(tmp_path / "restart.sqlite", "S1")
    cfg = EngineConfig(fps=30, frame_width=1280, frame_height=720)

    def chunk(start):
        frames = [
            FramePerception(
                frame_idx=i,
                shuttle_xy=None,
                shuttle_conf=0.0,
                persons=[PersonObs(track_id=1, bbox=np.array([300.0, 400.0, 330.0, 650.0]), conf=0.95)],
            )
            for i in range(start, start + 4)
        ]
        return ChunkPerception(start=start, end=start + 3, frames=frames, models={"player_detector": "test"})

    first = BadmintonMatchEngine("S1", cfg, store)
    first.set_calibration(0, match.homography)
    first.ingest(chunk(0))
    first.flush()
    prior = {e.payload["participant_id"] for e in store.query(types=["participant_observation"])}
    resumed = BadmintonMatchEngine("S1", cfg, store)
    resumed.set_calibration(0, match.homography)
    resumed.restore_from_log(3)
    resumed.ingest(chunk(4))
    resumed.flush()
    all_ids = {e.payload["participant_id"] for e in store.query(types=["participant_observation"])}
    assert len(prior) == 1 and len(all_ids) == 2 and prior < all_ids


def test_strided_detections_still_capture_sustained_motion(tmp_path: Path):
    match = make_match(["P1"])
    store = EventStore(tmp_path / "strided.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=10, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, match.homography)
    frames = []
    for i in range(50):
        offset = (i // 3) * 9
        people = [
            PersonObs(track_id=n, bbox=np.array([100.0 * n + offset, y - 80, 100.0 * n + offset + 30, y]), conf=0.9)
            for n, y in [(1, 250.0), (2, 550.0)]
        ]
        frames.append(FramePerception(frame_idx=i, shuttle_xy=(500.0, 300.0), shuttle_conf=0.9, persons=people))
    engine.ingest(ChunkPerception(start=0, end=49, frames=frames, models={"player_detector": "test"}))
    engine.flush()
    assert any(e.payload["state"] == "active_play" for e in store.query(types=["activity_interval"]))


def test_carried_or_missing_detector_frames_do_not_assert_player_exit(tmp_path: Path):
    match = make_match(["P1"])
    store = EventStore(tmp_path / "absence.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, match.homography)
    frames = []
    for i in range(38):
        people = [PersonObs(track_id=1, bbox=np.array([300.0, 400.0, 330.0, 650.0]), conf=0.95)] if i < 4 else []
        frames.append(
            FramePerception(frame_idx=i, shuttle_xy=None, shuttle_conf=0.0, persons=people, detector_observed=i < 4)
        )
    engine.ingest(ChunkPerception(start=0, end=37, frames=frames, models={"player_detector": "test"}))
    engine.flush()
    assert any(
        e.payload["kind"] == "PARTICIPANT_FIRST_OBSERVED" for e in store.query(types=["participant_observation"])
    )
    assert not any(e.payload["kind"] == "PLAYER_EXITED" for e in store.query(types=["participant_observation"]))
