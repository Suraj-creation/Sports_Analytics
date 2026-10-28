"""Doubles contact inference must use all visible episodes without naming players."""
from pathlib import Path

import numpy as np

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import ContactCandidate, detect_contacts
from bai_badminton.observations import WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot
from bai_badminton.perception.shuttle_post import Track
from bai_badminton.rules.bwf import MatchConfig
from bai_engine.store import EventStore


def window() -> WindowObs:
    track = Track.from_arrays(
        np.array([40, 60, 80, 100, 100, 100, 100], float),
        np.array([100, 100, 100, 100, 120, 140, 160], float),
        np.ones(7, bool),
    )
    return WindowObs(frame0=0, fps=30.0, shuttle=track, players={})


def frames(*, tie=False):
    rows = {}
    for i in range(1, 5):
        offset = 0 if i == 1 or (tie and i == 2) else i * 100
        rows[f"participant-epoch-{i:06d}"] = ParticipantSnapshot(
            track_id=i, bbox=np.array([90 + offset, 85, 110 + offset, 185], float),
            kps=None, court_xy=(0.5, -3.0), observation_id=f"birth-{i}",
        )
    return [dict(rows) for _ in range(7)]


def test_advance_uses_four_episodes_for_contact_scoring_without_named_actor(tmp_path: Path):
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720,
                                               match=MatchConfig(discipline="doubles")),
                                  EventStore(tmp_path / "events.sqlite", "S1"))
    engine._multi_person_identity_ambiguous = True
    engine._participant_frames = frames()
    engine._last_frame = 6
    engine._window = lambda *_: window()
    engine._handle_fsm = lambda *_: None
    seen = []
    engine._on_contact = lambda candidate, _: seen.append(candidate)
    engine._advance(6)
    assert seen, "four-player proximity should contribute to contact detection"
    assert any(c.scores["proximity_candidates"] == 4 for c in seen)
    assert all(c.player_id is None for c in seen)


def test_doubles_contact_detection_does_not_apply_singles_alternation(monkeypatch):
    def score(_, i):
        return ContactCandidate(frame=i, player_id="episode", p=0.9) if i in (2, 5) else None
    monkeypatch.setattr("bai_badminton.events.contact.score_frame", score)
    found = detect_contacts(window(), p_min=0.3, nms_s=0.01, min_same_player_gap_s=1,
                            enforce_alternation=False)
    assert [item.frame for item in found] == [2, 5]


def test_classification_uses_unique_episode_context_without_naming_hitter(tmp_path: Path):
    store = EventStore(tmp_path / "classify.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720,
                                                 match=MatchConfig(discipline="doubles")), store)
    engine._participant_frames = frames()
    engine._post_contact_kinematics = lambda _: (800.0, -30.0)
    engine._on_contact(ContactCandidate(frame=3, player_id=None, p=0.9, shuttle_xy=(100., 100.)), window())
    engine._classify(engine._open_contacts[-1], next_frame=35, is_serve=False, receiver=None)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.actors.player_id is None
    assert stroke.payload["participant_hypothesis"]["participant_id"] == "participant-epoch-000001"
    assert stroke.payload["hitter_court_xy"] == [0.5, -3.0]
    assert stroke.payload["classification_context_source"] == "provisional_track_episode"
    assert stroke.payload["stroke"] != "unknown"


def test_ambiguous_episode_never_supplies_classifier_context(tmp_path: Path):
    store = EventStore(tmp_path / "ambiguous.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720,
                                                 match=MatchConfig(discipline="doubles")), store)
    engine._participant_frames = frames(tie=True)
    engine._post_contact_kinematics = lambda _: (800.0, -30.0)
    engine._on_contact(ContactCandidate(frame=3, player_id=None, p=0.9, shuttle_xy=(100., 100.)), window())
    engine._classify(engine._open_contacts[-1], next_frame=35, is_serve=False, receiver=None)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.payload["participant_hypothesis"]["status"] == "unresolved"
    assert stroke.payload["hitter_court_xy"] is None
    assert stroke.payload["stroke"] == "unknown"


def test_track_id_change_within_episode_is_not_attributed():
    from bai_badminton.participant_contact import participant_contact_evidence, participant_window

    snapshots = frames()
    key = "participant-epoch-000001"
    old = snapshots[0][key]
    snapshots[0][key] = ParticipantSnapshot(track_id=99, bbox=old.bbox, kps=None, court_xy=old.court_xy)
    result = participant_contact_evidence(window(), snapshots, 3)
    assert result["participant_id"] != key
    assert key not in participant_window(window(), snapshots).players



def test_ambiguous_singles_does_not_enable_doubles_contact_fusion(tmp_path: Path):
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720),
        EventStore(tmp_path / "single.sqlite", "S1"),
    )
    engine._multi_person_identity_ambiguous = True
    engine._participant_frames = frames()
    engine._last_frame = 6
    engine._window = lambda *_: window()
    engine._handle_fsm = lambda *_: None
    seen = []
    engine._on_contact = lambda candidate, _: seen.append(candidate)
    engine._advance(6)
    assert seen == [], "extra court-side people must not enable doubles scoring in singles"


def test_ambiguous_singles_does_not_enable_doubles_classification_context(tmp_path: Path):
    store = EventStore(tmp_path / "single-context.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine._participant_frames = frames()
    engine._post_contact_kinematics = lambda _: (800.0, -30.0)
    engine._on_contact(ContactCandidate(frame=3, player_id=None, p=0.9, shuttle_xy=(100., 100.)), window())
    engine._classify(engine._open_contacts[-1], next_frame=35, is_serve=False, receiver=None)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.actors.player_id is None
    assert stroke.payload["participant_hypothesis"]["participant_id"] == "participant-epoch-000001"
    assert stroke.payload["hitter_court_xy"] is None
    assert stroke.payload["stroke"] == "unknown"


def test_declared_doubles_never_bind_two_visible_tracks_to_individual_score_slots(tmp_path: Path):
    from bai_badminton.perception_types import FramePerception, PersonObs
    from bai_badminton.testing.synth import broadcast_homography

    store = EventStore(tmp_path / "two-tracks.sqlite", "S1")
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720,
                           match=MatchConfig(discipline="doubles")), store,
    )
    engine.set_calibration(0, broadcast_homography())
    engine._provenance["player_detector"] = "synthetic"
    for frame in range(4):
        people = [
            PersonObs(track_id=1, bbox=np.array([100, 300, 140, 500], float), conf=0.9, court_xy=(0.5, -2)),
            PersonObs(track_id=2, bbox=np.array([800, 100, 840, 300], float), conf=0.9, court_xy=(0.5, 2)),
        ]
        engine._append(FramePerception(frame_idx=frame, shuttle_xy=None, shuttle_conf=0.0, persons=people))
    assert all(value is None for value in engine._players["P1"]["track_id"])
    assert all(value is None for value in engine._players["P2"]["track_id"])


def test_outside_court_or_unknown_geometry_never_supplies_doubles_candidate():
    from bai_badminton.participant_contact import participant_contact_evidence

    snapshots = frames()
    key = "participant-epoch-000001"
    for row in snapshots:
        old = row[key]
        row[key] = ParticipantSnapshot(track_id=old.track_id, bbox=old.bbox, kps=None, court_xy=(10.0, 1.0),
                                       observation_id="birth-one")
        for other, item in list(row.items()):
            if other != key:
                row[other] = ParticipantSnapshot(track_id=item.track_id, bbox=item.bbox, kps=None, court_xy=None,
                                                 observation_id="birth-other")
    result = participant_contact_evidence(window(), snapshots, 3, restrict_target_court=True)
    assert result["status"] == "unresolved"
    assert result["participant_id"] is None
    assert result["track_id"] is None


def test_doubles_hypothesis_binds_to_birth_event_and_rejects_missing_birth():
    from bai_badminton.participant_contact import participant_contact_evidence

    snapshots = frames()
    for row in snapshots:
        for key, item in list(row.items()):
            row[key] = ParticipantSnapshot(track_id=item.track_id, bbox=item.bbox, kps=None,
                                           court_xy=item.court_xy, observation_id=f"birth-{item.track_id}")
    result = participant_contact_evidence(window(), snapshots, 3, restrict_target_court=True)
    assert result["participant_id"] == "participant-epoch-000001"
    assert result["observation_id"] == "birth-1"
    for row in snapshots:
        item = row["participant-epoch-000001"]
        row["participant-epoch-000001"] = ParticipantSnapshot(
            track_id=item.track_id, bbox=item.bbox, kps=None, court_xy=item.court_xy, observation_id=None
        )
    result = participant_contact_evidence(window(), snapshots, 3, restrict_target_court=True)
    assert result["participant_id"] != "participant-epoch-000001"


def test_real_doubles_ingest_emits_birth_bound_on_court_hypotheses(tmp_path: Path):
    from bai_badminton.perception_types import ChunkPerception, PersonObs
    from bai_badminton.testing.synth import make_rally, to_frames

    rally = make_rally(n_shots=5)
    frame_data = to_frames(rally, 0)
    for frame in frame_data:
        frame.persons.extend([
            PersonObs(track_id=3, bbox=np.array([20, 400, 70, 500], float), conf=0.9, court_xy=(-2.0, -1.0)),
            PersonObs(track_id=4, bbox=np.array([1200, 150, 1250, 250], float), conf=0.9, court_xy=(2.0, 1.0)),
        ])
    store = EventStore(tmp_path / "doubles-ingest.sqlite", "S1")
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720,
                           match=MatchConfig(discipline="doubles")), store,
    )
    engine.set_calibration(0, rally.homography)
    engine.ingest(ChunkPerception(start=0, end=len(frame_data) - 1, frames=frame_data,
                                  models={"player_detector": "test"}))
    engine.flush()
    births = {event.event_id: event for event in store.query(types=["participant_observation"])}
    hypotheses = [event.payload["participant_hypothesis"] for event in store.query(types=["stroke"])
                  if event.payload.get("participant_hypothesis", {}).get("status") == "provisional"]
    assert hypotheses
    for hypothesis in hypotheses:
        birth = births[hypothesis["observation_id"]]
        assert birth.payload["participant_id"] == hypothesis["participant_id"]
        assert birth.payload["track_id"] == hypothesis["track_id"]


def test_anonymous_track_court_coordinates_require_bound_target_geometry(tmp_path: Path):
    from bai_badminton.perception_types import FramePerception, PersonObs
    from bai_badminton.testing.synth import broadcast_homography

    store = EventStore(tmp_path / "court-positions.sqlite", "S1")
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720,
                           match=MatchConfig(discipline="doubles")), store,
    )
    engine.set_calibration(0, broadcast_homography())
    engine._provenance["player_detector"] = "synthetic"
    people = [
        PersonObs(track_id=1, bbox=np.array([100, 300, 140, 500], float), conf=0.9, court_xy=(0.5, -2)),
        PersonObs(track_id=2, bbox=np.array([800, 100, 840, 300], float), conf=0.9, court_xy=(10., 1)),
    ]
    for frame in range(3):
        engine._append(FramePerception(frame_idx=frame, shuttle_xy=None, shuttle_conf=0.0, persons=people))
    engine._append(FramePerception(frame_idx=3, shuttle_xy=None, shuttle_conf=0.0, persons=people, cam_lost=True))
    samples = [item for item in engine.drain_tracks() if item.obj.value == "player"]
    target = next(item for item in samples if item.frame_idx == 2 and item.track_id == 1)
    adjacent = next(item for item in samples if item.frame_idx == 2 and item.track_id == 2)
    assert target.participant_observation_id
    assert (target.court_x, target.court_y) == (0.5, -2.0)
    assert adjacent.court_x is None and adjacent.court_y is None
    assert all(item.court_x is None and item.court_y is None for item in samples if item.frame_idx == 3)


def test_ambiguous_duplicate_track_never_supplies_court_coordinates(tmp_path: Path):
    from bai_badminton.perception_types import FramePerception, PersonObs
    from bai_badminton.testing.synth import broadcast_homography

    store = EventStore(tmp_path / "duplicate.sqlite", "S1")
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720,
                           match=MatchConfig(discipline="doubles")), store,
    )
    engine.set_calibration(0, broadcast_homography())
    engine._provenance["player_detector"] = "synthetic"
    person = PersonObs(track_id=1, bbox=np.array([100, 300, 140, 500], float), conf=0.9, court_xy=(0.5, -2))
    for frame in range(3):
        engine._append(FramePerception(frame_idx=frame, shuttle_xy=None, shuttle_conf=0.0, persons=[person]))
    engine._append(FramePerception(frame_idx=3, shuttle_xy=None, shuttle_conf=0.0, persons=[person, person]))
    rows = [s for s in engine.drain_tracks() if s.obj.value == "player" and s.frame_idx == 3]
    assert rows and all(item.court_x is None and item.court_y is None for item in rows)
