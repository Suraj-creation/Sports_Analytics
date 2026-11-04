"""Opt-in detector-bracket context cannot become a named contact or point.

Controlled observations isolate the engine evidence boundary. These are not
labelled contact or shot-accuracy measurements; model kinematics are held fixed.
"""

import json
from copy import deepcopy
from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import ContactCandidate
from bai_badminton.events.stroke import StrokePrediction
from bai_badminton.observations import WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot
from bai_badminton.participant_geometry import GeometryBracketPolicy
from bai_badminton.perception.shuttle_post import Track
from bai_badminton.rules import MatchConfig
from bai_engine.store import EventStore


class _CaptureClassifier:
    name = "test:context-boundary"

    def __init__(self):
        self.contexts = []

    def predict(self, context):
        self.contexts.append(context)
        if context.hitter_court_xy is None:
            return StrokePrediction({"unknown": 0.0}, self.name, "missing_required_evidence")
        return StrokePrediction({"drive": 0.6, "unknown": 0.4}, self.name)


def _setup(tmp_path, match_format, *, enabled):
    count = 4 if match_format == "doubles" else 2
    options = {"participant_geometry_policy": GeometryBracketPolicy()} if enabled else {}
    config = EngineConfig(
        fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline=match_format), **options
    )
    store = EventStore(tmp_path / "events.sqlite", "S1")
    classifier = _CaptureClassifier()
    engine = BadmintonMatchEngine("S1", config, store, stroke_classifier=classifier)
    frames = []
    for index in range(7):
        fresh = index % 2 == 0
        source = index if fresh else index - 1
        people = {}
        for number in range(1, count + 1):
            if number == 1:
                box, court = [70 + 10 * source, 85, 90 + 10 * source, 185], (0.1 * source - 0.2, -3.0)
            else:
                x = 100 + 250 * (number - 1)
                near_partner = match_format == "doubles" and number == 2
                box, court = [x, 85, x + 20, 185], (1.0 if number % 2 == 0 else -1.0, -3.0 if near_partner else 3.0)
            people[f"participant-test-{number:06d}"] = ParticipantSnapshot(
                track_id=number,
                bbox=np.asarray(box, dtype=float),
                kps=None,
                court_xy=court,
                observation_id=f"birth-{number}",
                detector_observed=fresh,
                detector_matched=fresh,
            )
        frames.append(people)
    window = WindowObs(
        100,
        30.0,
        Track.from_arrays(
            np.array([80, 90, 100, 110, 100, 90, 80], dtype=float),
            np.full(7, 100.0),
            np.ones(7, bool),
        ),
        {},
    )
    engine._buf0, engine._last_frame = 100, 106
    engine._participant_frames = frames
    engine._geometry_valid = [True] * 7
    engine._participant_visible_counts = [count] * 7
    engine._participant_identity_unresolved = [False] * 7
    engine._multi_person_identity_ambiguous = True
    engine._window = lambda *_: window
    engine._post_contact_kinematics = lambda *_: (800.0, -30.0)
    return engine, store, window, classifier


def _contact(engine, window):
    engine._on_contact(
        ContactCandidate(
            frame=103, player_id=None, p=0.8, shuttle_xy=(110.0, 100.0), attribution_reason="no_player_observation"
        ),
        window,
    )
    return engine._open_contacts[-1]


@pytest.mark.parametrize("match_format,count", [("singles", 2), ("doubles", 4)])
def test_enabled_bracket_context_reaches_classifier_without_named_actor_or_point(tmp_path, match_format, count):
    engine, store, window, classifier = _setup(tmp_path, match_format, enabled=True)
    before = deepcopy(engine._participant_frames)
    score_before = engine.public_state()["score"]
    item = _contact(engine, window)
    context = item.event.payload.get("participant_geometry_context")
    assert context is not None, "opt-in geometry must be inspectable on the contact"
    assert context["status"] == "estimated"
    assert context["method"] == "same_episode_detector_bracket_v1"
    assert context["support_semantics"] == "uncalibrated_body_proximity"
    assert context["player_id"] is None
    assert len(context["candidates"]) == count
    assert list(context["estimate"]["source_frames"]) == [102, 104]
    assert context["estimate"]["position_kind"] == "estimated"
    assert context["estimate"]["participant_id"] == "participant-test-000001"
    # This separate detector-bracket estimate must not relabel a carried box
    # as a matched current detector observation.
    assert item.event.payload["participant_hypothesis"]["status"] == "unresolved"
    engine._classify(item, next_frame=135, is_serve=False, receiver=None)
    captured = classifier.contexts[-1]
    np.testing.assert_allclose(captured.hitter_court_xy, [0.1, -3.0])
    assert captured.hitter_side == "near"  # current geometric side, never a named team or score slot
    assert captured.player_id is None and captured.contact_above_head is None
    stroke = store.query(types=["stroke"])[0]
    assert stroke.payload["classification_context_source"] == "detector_bracket_geometry"
    assert stroke.payload["participant_geometry_context"] == json.loads(json.dumps(context))
    assert stroke.payload["stroke"] == "drive"
    assert stroke.actors.player_id is None and stroke.actors.track_id is None and stroke.actors.opponent_id is None
    assert item.event.actors.player_id is None and item.cand.player_id is None
    assert store.query(types=["point"]) == []
    assert engine.public_state()["score"] == score_before
    for index, people in enumerate(engine._participant_frames):
        for key, value in people.items():
            prior = before[index][key]
            np.testing.assert_equal(value.bbox, prior.bbox)
            assert value.detector_observed is prior.detector_observed
            assert value.detector_matched is prior.detector_matched
    assert all(not values["bbox"] for values in engine._players.values())


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
def test_geometry_context_is_disabled_by_default(tmp_path, match_format):
    engine, store, window, classifier = _setup(tmp_path, match_format, enabled=False)
    item = _contact(engine, window)
    assert "participant_geometry_context" not in item.event.payload
    engine._classify(item, next_frame=135, is_serve=False, receiver=None)
    assert classifier.contexts[-1].hitter_court_xy is None
    assert classifier.contexts[-1].contact_above_head is None
    assert store.query(types=["stroke"])[0].payload["stroke"] == "unknown"


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
def test_failed_current_detector_is_not_rescued_by_nearby_good_brackets(tmp_path, match_format):
    engine, store, window, classifier = _setup(tmp_path, match_format, enabled=True)
    engine._participant_frames[3] = {
        key: replace(value, detector_observed=True, detector_matched=False)
        for key, value in engine._participant_frames[3].items()
    }
    item = _contact(engine, window)
    assert item.event.payload["participant_geometry_context"]["status"] == "unresolved"
    engine._classify(item, next_frame=135, is_serve=False, receiver=None)
    assert classifier.contexts[-1].hitter_court_xy is None
    assert store.query(types=["stroke"])[0].payload["stroke"] == "unknown"


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
@pytest.mark.parametrize("change", ["birth", "calibration", "extra_person"])
def test_delayed_classification_revalidates_bracket_context(tmp_path, match_format, change):
    engine, store, window, classifier = _setup(tmp_path, match_format, enabled=True)
    item = _contact(engine, window)
    assert item.event.payload["participant_geometry_context"]["status"] == "estimated"
    if change == "birth":
        key = "participant-test-000001"
        engine._participant_frames[4][key] = replace(engine._participant_frames[4][key], observation_id="new-birth")
    elif change == "calibration":
        engine._geometry_valid[4] = False
    else:
        engine._participant_visible_counts[4] += 1
    engine._classify(item, next_frame=135, is_serve=False, receiver=None)
    assert classifier.contexts[-1].hitter_court_xy is None
    assert classifier.contexts[-1].contact_above_head is None
    stroke = store.query(types=["stroke"])[0]
    assert stroke.payload["stroke"] == "unknown"
    assert stroke.actors.player_id is None
    assert stroke.payload.get("classification_context_source") != "detector_bracket_geometry"


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
def test_fresh_anonymous_court_side_is_geometric_not_a_named_actor(tmp_path, match_format):
    engine, store, window, classifier = _setup(tmp_path, match_format, enabled=False)
    engine._participant_frames[3] = {
        key: replace(value, detector_observed=True, detector_matched=True)
        for key, value in engine._participant_frames[3].items()
    }
    item = _contact(engine, window)
    assert item.event.payload["participant_hypothesis"]["status"] == "provisional"
    engine._classify(item, next_frame=135, is_serve=False, receiver=None)
    assert classifier.contexts[-1].hitter_side == "near"
    assert classifier.contexts[-1].player_id is None
    assert store.query(types=["stroke"])[0].actors.player_id is None
    assert store.query(types=["point"]) == []
