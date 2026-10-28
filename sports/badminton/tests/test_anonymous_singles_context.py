"""Current singles geometry may classify a shot without identifying its player."""

from copy import deepcopy
from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.analytics.individual import build_individual_analytics
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import ContactCandidate
from bai_badminton.observations import WindowObs
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.shuttle_post import Track
from bai_badminton.perception_types import FramePerception, PersonObs
from bai_badminton.testing.synth import broadcast_homography
from bai_engine.schema import Event, EventStatus, Provenance
from bai_engine.schema.session import ParticipantInfo, ParticipantRoster
from bai_engine.store import EventStore


def setup(tmp_path, *, new_people=0):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, broadcast_homography(), emit=False)
    engine._provenance["player_detector"] = "test"
    x = np.array([40, 60, 80, 100, 100, 100, 100], dtype=float)
    y = np.array([100, 100, 100, 100, 120, 140, 160], dtype=float)
    for frame in range(7):
        people = [
            PersonObs(1, np.array([90.0, 85.0, 110.0, 185.0]), 0.9, court_xy=(0.5, -3.0), detector_matched=True),
            PersonObs(2, np.array([400.0, 85.0, 440.0, 185.0]), 0.9, court_xy=(0.5, 3.0), detector_matched=True),
        ]
        if frame >= 3:
            for newcomer in range(new_people):
                x0 = 600.0 + newcomer * 100
                people.append(
                    PersonObs(
                        3 + newcomer,
                        np.array([x0, 85.0, x0 + 40, 185.0]),
                        0.9,
                        court_xy=(1.5, 3.0),
                        detector_matched=True,
                    )
                )
        engine._append(
            FramePerception(
                frame_idx=frame,
                shuttle_xy=(x[frame], y[frame]),
                shuttle_conf=0.9,
                shot_id=0 if frame == 0 else 1,
                calibration_state=CalibrationState.VALID,
                detector_observed=True,
                persons=people,
            )
        )
    engine._post_contact_kinematics = lambda _, next_frame=None: (800.0, -30.0)
    window = WindowObs(frame0=0, fps=30, shuttle=Track.from_arrays(x, y, np.ones(7, dtype=bool)), players={})
    assert engine._multi_person_identity_ambiguous is True
    assert store.query(types=["identity_ambiguity"])[0].payload["reason"] == "visual_tracker_reset"
    assert engine._players["P1"]["bbox"][3] is None and engine._players["P2"]["bbox"][3] is None
    return engine, store, window


def contact(engine, window):
    engine._on_contact(
        ContactCandidate(
            frame=3, player_id=None, p=0.9, shuttle_xy=(100.0, 100.0), attribution_reason="no_player_observation"
        ),
        window,
    )
    item = engine._open_contacts[-1]
    assert item.event.payload["participant_hypothesis"]["status"] == "provisional"
    return item


def test_post_cut_singles_geometry_classifies_without_assigning_a_named_player(tmp_path):
    engine, store, window = setup(tmp_path)
    item = contact(engine, window)
    before = deepcopy(engine._players)
    engine._classify(item, next_frame=35, is_serve=False, receiver=None)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.payload["classification_context_source"] == "provisional_track_episode"
    assert stroke.payload["hitter_court_xy"] == [0.5, -3.0]
    assert stroke.payload["stroke"] != "unknown"
    assert stroke.actors.player_id is None and item.cand.player_id is None and item.event.actors.player_id is None
    for pid, fields in before.items():
        for field, values in fields.items():
            assert len(engine._players[pid][field]) == len(values)
            for actual, expected in zip(engine._players[pid][field], values, strict=True):
                if expected is None:
                    assert actual is None
                else:
                    np.testing.assert_array_equal(actual, expected)
    store.append(
        Event(
            session_id="S1",
            type="rally_end",
            frame_start=0,
            frame_end=40,
            pts_us=0,
            status=EventStatus.CONFIRMED,
            provenance=Provenance(model="test"),
            payload={"official": True, "shots": [{"event_id": stroke.event_id, "frame": 3}]},
        )
    )
    roster = ParticipantRoster(
        match_format="singles",
        participants=[
            ParticipantInfo(participant_id="U1"),
            ParticipantInfo(participant_id="U2"),
        ],
    )
    result = build_individual_analytics(store, roster, max_frame=40, fps=30)
    assert result["accounting"] == {"total_shots": 1, "attributed_shots": 0, "unattributed_shots": 1}
    assert all(person["total_shots"] == 0 for person in result["participants"].values())


@pytest.mark.parametrize("new_people", [1, 2])
def test_new_visual_people_block_singles_context_before_episode_admission(tmp_path, new_people):
    engine, store, window = setup(tmp_path, new_people=new_people)
    assert len(engine._participant_frames[3]) == 2
    assert engine._participant_visible_counts[3] == 2 + new_people
    assert engine._participant_identity_unresolved[3] is False
    item = contact(engine, window)
    engine._classify(item, next_frame=35, is_serve=False, receiver=None)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.actors.player_id is None
    assert stroke.payload["hitter_court_xy"] is None
    assert "classification_context_source" not in stroke.payload
    assert stroke.payload["stroke"] == "unknown"


def test_all_visual_counts_stay_aligned_after_history_trim(tmp_path):
    engine, _, _ = setup(tmp_path, new_people=1)
    engine.cfg = replace(engine.cfg, history=1, context_back=0)
    engine._final = 6
    engine._trim()
    assert engine._buf0 == 5
    assert engine._participant_visible_counts == [3, 3]
    assert len(engine._participant_frames) == len(engine._participant_visible_counts)


@pytest.mark.parametrize(
    "case",
    [
        "missing_person",
        "third_person",
        "missing_detector",
        "unknown_detector",
        "unmatched_person",
        "missing_court",
        "outside_court",
        "nonfinite_court",
        "missing_birth",
        "unverified_geometry",
        "unresolved_visual_identity",
        "changed_selected_birth",
        "changed_selected_track",
    ],
)
def test_singles_context_requires_two_supported_current_people_and_matching_birth(tmp_path, case):
    engine, store, window = setup(tmp_path)
    item = contact(engine, window)
    current = engine._participant_frames[3]
    selected = item.event.payload["participant_hypothesis"]["participant_id"]
    other = next(key for key in current if key != selected)
    if case == "missing_person":
        current.pop(other)
    elif case == "third_person":
        current["participant-extra-000003"] = replace(current[other], track_id=3, observation_id="extra-birth")
    elif case in ("missing_detector", "unknown_detector"):
        current[other] = replace(current[other], detector_observed=False if case == "missing_detector" else None)
    elif case == "unmatched_person":
        current[other] = replace(current[other], detector_matched=False)
    elif case in ("missing_court", "outside_court", "nonfinite_court"):
        court = {"missing_court": None, "outside_court": (10.0, 3.0), "nonfinite_court": (np.nan, 3.0)}[case]
        current[other] = replace(current[other], court_xy=court)
    elif case == "missing_birth":
        current[other] = replace(current[other], observation_id=None)
    elif case == "unverified_geometry":
        engine._geometry_valid[3] = False
    elif case == "unresolved_visual_identity":
        engine._participant_identity_unresolved[3] = True
    elif case == "changed_selected_birth":
        current[selected] = replace(current[selected], observation_id="another-birth")
    else:
        current[selected] = replace(current[selected], track_id=99)
    engine._classify(item, next_frame=35, is_serve=False, receiver=None)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.actors.player_id is None
    assert stroke.payload["hitter_court_xy"] is None
    assert "classification_context_source" not in stroke.payload
    assert stroke.payload["stroke"] == "unknown"
