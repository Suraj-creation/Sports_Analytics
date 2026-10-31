"""Track-episode hypotheses never silently become named-player attribution."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

from bai_badminton.events.contact import ContactCandidate
from bai_badminton.observations import WindowObs
from bai_badminton.perception.shuttle_post import Track


def _evidence_module():
    spec = importlib.util.find_spec("bai_badminton.participant_contact")
    assert spec is not None, "participant contact evidence is not yet implemented"
    from bai_badminton import participant_contact

    return participant_contact


def _window() -> WindowObs:
    t = Track.from_arrays(
        np.array([40, 60, 80, 100, 100, 100, 100], float),
        np.array([100, 100, 100, 100, 120, 140, 160], float),
        np.ones(7, bool),
    )
    return WindowObs(frame0=0, fps=30.0, shuttle=t, players={})


def _frames(offsets: list[int]):
    evidence = _evidence_module()
    snapshots = {}
    for i, offset in enumerate(offsets, 1):
        pid = f"participant-epoch-{i:06d}"
        snapshots[pid] = evidence.ParticipantSnapshot(
            track_id=i, bbox=np.array([90 + offset, 85, 110 + offset, 185], float), kps=None, court_xy=None
        )
    return [dict(snapshots) for _ in range(7)]


def test_four_episode_proximity_is_provisional_and_preserves_all_competitors():
    evidence = _evidence_module()
    value = evidence.participant_contact_evidence(_window(), _frames([0, 100, 200, 300]), 3)
    assert value["status"] == "provisional"
    assert value["participant_id"] == "participant-epoch-000001"
    assert value["track_id"] == 1
    assert value["reason"] == "nearest_proximity"
    assert value["components"]["proximity_candidates"] == 4
    assert value["policy"] == "relative_proximity_gap_v1"


def test_close_partners_and_missing_coverage_remain_unresolved():
    evidence = _evidence_module()
    tied = evidence.participant_contact_evidence(_window(), _frames([0, 0, 200, 300]), 3)
    assert tied["status"] == "unresolved"
    assert tied["participant_id"] is None and tied["track_id"] is None
    assert tied["reason"] == "ambiguous_proximity"
    frames = _frames([0, 100, 200, 300])
    frames[3] = {}
    missing = evidence.participant_contact_evidence(_window(), frames, 3)
    assert missing["status"] == "unresolved"
    assert missing["participant_id"] is None and missing["track_id"] is None
    assert missing["reason"] == "no_player_observation"


def test_contact_and_stroke_preserve_episode_hypothesis_without_naming_a_player(tmp_path: Path):
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
    from bai_engine.store import EventStore

    frames = _frames([0, 100, 200, 300])
    store = EventStore(tmp_path / "events.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine._participant_frames = frames
    candidate = ContactCandidate(
        frame=3, player_id=None, p=0.7, shuttle_xy=(100.0, 100.0), attribution_reason="no_player_observation"
    )
    engine._on_contact(candidate, _window())
    contact = store.query(types=["contact"])[0]
    assert contact.actors.player_id is None
    assert contact.payload["participant_hypothesis"]["participant_id"] == "participant-epoch-000001"
    engine._classify(engine._open_contacts[-1], next_frame=6, is_serve=False, receiver=None)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.actors.player_id is None
    assert stroke.payload["participant_hypothesis"] == contact.payload["participant_hypothesis"]


def test_engine_buffers_four_track_episodes_and_clears_uncovered_frames(tmp_path: Path):
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
    from bai_badminton.perception_types import FramePerception, PersonObs
    from bai_badminton.testing.synth import broadcast_homography
    from bai_engine.store import EventStore

    store = EventStore(tmp_path / "ingest.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, broadcast_homography())
    engine._provenance["player_detector"] = "synthetic"
    for frame in range(8):
        persons = [
            PersonObs(
                track_id=i,
                bbox=np.array([90 + 100 * i, 85, 110 + 100 * i, 185], float),
                conf=0.9,
                court_xy=(0.5 * i, -1.0 if i < 3 else 1.0),
            )
            for i in range(1, 5)
        ]
        engine._append(
            FramePerception(
                frame_idx=frame, shuttle_xy=(100.0, 100.0), shuttle_conf=0.9, persons=persons, replay=(frame == 7)
            )
        )
    assert len(engine._participant_frames) == 8
    assert len(engine._participant_frames[2]) == 4
    assert engine._participant_frames[7] == {}
    assert all(s.track_id in (1, 2, 3, 4) for s in engine._participant_frames[2].values())
    assert all(key.startswith("participant-") for key in engine._participant_frames[2])
    births = {
        e.payload["track_id"]: e.event_id
        for e in store.query(types=["participant_observation"])
        if e.payload["kind"] in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
    }
    samples = [s for s in engine.drain_tracks() if s.obj.value == "player" and s.frame_idx == 2]
    assert samples and all(s.participant_observation_id == births[s.track_id] for s in samples)


def test_real_engine_ingest_retains_episode_evidence_in_doubles(tmp_path: Path):
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
    from bai_badminton.perception_types import ChunkPerception, PersonObs
    from bai_badminton.rules import MatchConfig
    from bai_badminton.testing.synth import make_rally, to_frames
    from bai_engine.store import EventStore

    rally = make_rally(n_shots=5)
    frames = to_frames(rally, 0)
    for frame in frames:
        frame.persons.extend(
            [
                PersonObs(track_id=3, bbox=np.array([20, 400, 70, 500], float), conf=0.9, court_xy=(-2.0, -1.0)),
                PersonObs(track_id=4, bbox=np.array([1200, 150, 1250, 250], float), conf=0.9, court_xy=(2.0, 1.0)),
            ]
        )
    store = EventStore(tmp_path / "actual-ingest.sqlite", "S1")
    engine = BadmintonMatchEngine(
        "S1",
        EngineConfig(fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline="doubles")),
        store,
    )
    engine.set_calibration(0, rally.homography)
    engine.ingest(ChunkPerception(start=0, end=len(frames) - 1, frames=frames, models={"player_detector": "test"}))
    engine.flush()
    strokes = store.query(types=["stroke"])
    assert strokes
    assert all(e.actors.player_id is None for e in strokes)
    evidence = [e.payload.get("participant_hypothesis") for e in strokes]
    assert all(item is not None for item in evidence)
    assert any(item["status"] == "provisional" for item in evidence)
    assert all(item["participant_id"] is None or item["participant_id"].startswith("participant-") for item in evidence)


def test_engine_requires_consistent_observed_motion_before_classification(tmp_path: Path):
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
    from bai_engine.store import EventStore

    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), EventStore(tmp_path / "motion.sqlite", "S1")
    )
    track = Track.from_arrays(
        np.arange(6, dtype=float) * 10, np.arange(6, dtype=float) * 5, np.array([True, True, False, False, False, True])
    )
    engine._shuttle_around = lambda frame: (track, 0)
    assert engine._post_contact_kinematics(0) == (None, None)
