"""Uncertain association must not silently credit a different visible player."""

from dataclasses import replace

import numpy as np
from test_participant_contact_evidence import _frames, _window

from bai_badminton.events.contact import ContactCandidate
from bai_badminton.participant_contact import participant_contact_evidence
from bai_engine.schema import TrackObject, TrackSample
from bai_engine.schema.tracks import samples_to_table, table_to_samples


def test_camera_stabilisation_preserves_unmatched_person_provenance():
    from bai_badminton.engine import _stabilise
    from bai_badminton.perception_types import PersonObs

    original = PersonObs(
        1,
        np.array([10.0, 20.0, 40.0, 80.0]),
        0.9,
        raw_track_id=7,
        detector_matched=False,
        identity_method="unobserved_raw_carry",
    )
    restored = _stabilise(original, np.eye(3))
    assert restored.raw_track_id == 7
    assert restored.detector_matched is False
    assert restored.identity_method == "unobserved_raw_carry"


def test_raw_and_canonical_identity_provenance_survives_columnar_storage():
    sample = TrackSample(
        frame_idx=8,
        obj=TrackObject.PLAYER,
        track_id=17,
        raw_track_id=4,
        detector_matched=True,
        identity_method="neural_motion_match",
        bbox=(10, 10, 40, 100),
    )
    restored = table_to_samples(samples_to_table([sample]))[0]
    assert (restored.track_id, restored.raw_track_id, restored.detector_matched, restored.identity_method) == (
        17,
        4,
        True,
        "neural_motion_match",
    )


def test_winning_unmatched_person_is_unresolved_without_reranking_a_teammate():
    frames = _frames([0, 100, 200, 300])
    pid = "participant-epoch-000001"
    for row in frames:
        row[pid] = replace(row[pid], detector_matched=False)
    result = participant_contact_evidence(_window(), frames, 3)
    assert result["status"] == "unresolved"
    assert result["participant_id"] is None and result["track_id"] is None
    assert result["reason"] == "player_not_detector_matched"


def test_any_unresolved_visual_identity_blocks_contact_credit_but_keeps_event(tmp_path):
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
    from bai_badminton.rules.bwf import MatchConfig
    from bai_engine.store import EventStore

    store = EventStore(tmp_path / "events.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.match_cfg = MatchConfig(discipline="doubles")
    frames = _frames([0, 100, 200, 300])
    engine._participant_frames = frames
    engine._participant_identity_unresolved = [False, False, False, True, False, False, False]
    candidate = ContactCandidate(frame=3, player_id=None, p=0.7, shuttle_xy=(100.0, 100.0))
    engine._on_contact(candidate, _window())
    contact = store.query(types=["contact"])[0]
    assert contact.payload["participant_hypothesis"]["status"] == "unresolved"
    assert contact.payload["participant_hypothesis"]["reason"] == "ambiguous_player_association"
    assert contact.actors.player_id is None


def test_uncertain_people_remain_visible_as_unidentified_track_boxes(tmp_path):
    from test_participant_epochs import setup

    from bai_badminton.perception.calibration_state import CalibrationState
    from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
    from bai_badminton.rules.bwf import MatchConfig

    engine, _, _ = setup(tmp_path)
    engine.match_cfg = MatchConfig(discipline="doubles")
    engine._multi_person_identity_ambiguous = True
    frame = FramePerception(
        0,
        None,
        0,
        persons=[
            PersonObs(
                -1,
                np.array([300.0, 400.0, 330.0, 650.0]),
                0.95,
                raw_track_id=7,
                detector_matched=True,
                identity_method="ambiguous_assignment",
            )
        ],
        calibration_state=CalibrationState.VALID,
        detector_observed=True,
    )
    engine.ingest(ChunkPerception(0, 0, [frame], models={"player_detector": "test"}))
    rows = [row for row in engine.drain_tracks() if row.obj == TrackObject.PLAYER]
    assert len(rows) == 1
    assert rows[0].track_id == -9 and rows[0].raw_track_id == 7
    assert rows[0].participant_observation_id is None and rows[0].player_id is None
    assert engine._participant_identity_unresolved == [True]


def test_explicit_doubles_never_binds_two_visible_people_to_singles_score_slots(tmp_path):
    from test_participant_epochs import setup

    from bai_badminton.perception.calibration_state import CalibrationState
    from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
    from bai_badminton.rules.bwf import MatchConfig

    engine, _, _ = setup(tmp_path)
    engine.match_cfg = MatchConfig(discipline="doubles")
    frames = [
        FramePerception(
            f,
            None,
            0,
            persons=[
                PersonObs(
                    i,
                    np.array([300.0 + i * 100, 300.0, 340.0 + i * 100, 500.0]),
                    0.95,
                    court_xy=(0.0, -3.0 if i == 1 else 3.0),
                )
                for i in (1, 2)
            ],
            calibration_state=CalibrationState.VALID,
            detector_observed=True,
        )
        for f in range(4)
    ]
    engine.ingest(ChunkPerception(0, 3, frames, models={"player_detector": "test"}))
    rows = [row for row in engine.drain_tracks() if row.obj == TrackObject.PLAYER]
    assert rows and all(row.player_id is None for row in rows)
    assert all(box is None for values in engine._players.values() for box in values["bbox"])


def test_unresolved_extra_person_withholds_established_doubles_teams(tmp_path):
    from types import SimpleNamespace

    from test_participant_epochs import setup

    from bai_badminton.events.activity import ActivityState
    from bai_badminton.perception.calibration_state import CalibrationState
    from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
    from bai_badminton.rules.bwf import MatchConfig
    from bai_badminton.teams import DoublesTeamTracker

    engine, store, _ = setup(tmp_path)
    engine.match_cfg = MatchConfig(discipline="doubles")
    # Supply independent active-play evidence so this test isolates identity admission.
    engine.activity = SimpleNamespace(update=lambda _: (SimpleNamespace(state=ActivityState.ACTIVE_PLAY), None))
    engine.doubles_teams = DoublesTeamTracker(fps=30, sustain_frames=1)

    def frame(index, *, unresolved=False):
        persons = [
            PersonObs(
                track_id=track,
                bbox=np.array([100.0 + 120 * track, 200.0, 150.0 + 120 * track, 400.0]),
                conf=0.9,
                court_xy=(track * 0.2, -3.0 if track < 3 else 3.0),
                raw_track_id=track,
                detector_matched=True,
            )
            for track in range(1, 5)
        ]
        if unresolved:
            persons.append(
                PersonObs(
                    track_id=-1,
                    bbox=np.array([900.0, 200.0, 940.0, 400.0]),
                    conf=0.9,
                    court_xy=(0.0, -2.0),
                    raw_track_id=9,
                    detector_matched=True,
                    identity_method="ambiguous_assignment",
                )
            )
        return FramePerception(
            frame_idx=index,
            shuttle_xy=None,
            shuttle_conf=0.0,
            persons=persons,
            calibration_state=CalibrationState.VALID,
            detector_observed=True,
        )

    try:
        engine.ingest(ChunkPerception(0, 2, [frame(i) for i in range(3)], models={"player_detector": "test"}))
        teams = store.query(types=["doubles_team_hypothesis"])
        assert teams and teams[-1].payload["status"] == "provisional"
        engine.ingest(ChunkPerception(3, 3, [frame(3, unresolved=True)], models={"player_detector": "test"}))
        assert engine._participant_identity_unresolved[-1] is True
        assert len(engine._participant_frames[-1]) == 4
        teams = store.query(types=["doubles_team_hypothesis"])
        assert teams[-1].frame_start == 3
        assert teams[-1].payload["status"] == "unknown"
        assert teams[-1].payload["teams"] == []
        assert engine._current_team_key is None
    finally:
        store.close()
