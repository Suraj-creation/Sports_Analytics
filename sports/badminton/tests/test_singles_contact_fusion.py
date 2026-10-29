"""Player cue availability must not depend on durable name assignment."""

from pathlib import Path

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import ContactCandidate, detect_contacts
from bai_badminton.observations import WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot
from bai_badminton.perception.shuttle_post import Track
from bai_engine.store import EventStore


def setup(tmp_path: Path, count: int = 2):
    n = 21
    t = np.arange(n) - 10
    window = WindowObs(
        0,
        30.0,
        Track.from_arrays(100 + np.minimum(t, 0) * 10.0, 100 + np.maximum(t, 0) * 10.0, np.ones(n, bool)),
        {},
    )
    frames = [
        {
            f"participant-test-{j:06d}": ParticipantSnapshot(
                track_id=j,
                bbox=np.array([90 + j * 250, 85, 110 + j * 250, 185], float),
                kps=None,
                court_xy=(0.5, -3 if j == 0 else 3),
                observation_id=f"birth-{j}",
                detector_observed=True,
                detector_matched=True,
            )
            for j in range(count)
        }
        for _ in range(n)
    ]
    store = EventStore(tmp_path / "events.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine._participant_frames = frames
    engine._last_frame = n - 1
    engine._window = lambda *_: window
    engine._handle_fsm = lambda *_: None
    seen = []
    engine._on_contact = lambda candidate, _: seen.append(candidate)
    return engine, window, seen, store


def test_two_anonymous_players_supply_contact_cues_without_names(tmp_path):
    engine, window, seen, store = setup(tmp_path)
    assert detect_contacts(window) == [], "redirect alone has insufficient support in this example"
    engine._advance(window.n - 1)
    assert [c.frame for c in seen] == [10]
    assert seen[0].scores["proximity_candidates"] == 2
    assert seen[0].scores["proximity"] > 0.9
    assert seen[0].player_id is None
    assert all(not any(v["track_id"]) for v in engine._players.values())
    store.close()


@pytest.mark.parametrize("count", [1, 3, 4])
def test_singles_missing_or_extra_people_do_not_enable_episode_cues(tmp_path, count):
    engine, window, seen, store = setup(tmp_path, count)
    engine._advance(window.n - 1)
    assert seen == []
    store.close()


@pytest.mark.parametrize("named", [False, True])
def test_anonymous_episode_does_not_trigger_named_player_alternation(tmp_path, monkeypatch, named):
    engine, window, seen, store = setup(tmp_path)
    if named:
        engine._players["P1"]["track_id"] = [0] * window.n
    monkeypatch.setattr(
        "bai_badminton.engine.detect_contacts",
        lambda *_args, **_kw: [
            ContactCandidate(frame=3, player_id="participant-test-000000", p=0.9, scores={"proximity": 0.8}),
            ContactCandidate(frame=10, player_id="participant-test-000000", p=0.9, scores={"proximity": 0.8}),
        ],
    )
    engine._advance(window.n - 1)
    assert [c.frame for c in seen] == ([3] if named else [3, 10])
    assert all(c.player_id == ("P1" if named else None) for c in seen)
    store.close()


def test_nonunique_named_track_mapping_cannot_assign_actor(tmp_path, monkeypatch):
    engine, window, seen, store = setup(tmp_path)
    for pid in ("P1", "P2"):
        engine._players[pid]["track_id"] = [0] * window.n
    monkeypatch.setattr(
        "bai_badminton.engine.detect_contacts",
        lambda *_args, **_kw: [
            ContactCandidate(frame=10, player_id="participant-test-000000", p=0.9, scores={"proximity": 0.8}),
        ],
    )
    engine._advance(window.n - 1)
    assert len(seen) == 1 and seen[0].player_id is None
    store.close()


@pytest.mark.parametrize("proximity, eligible", [(0.0, False), (0.049, False), (0.05, True), (0.8, True)])
def test_body_context_eligibility_retains_raw_turns_and_ambiguous_actors(tmp_path, monkeypatch, proximity, eligible):
    engine, window, seen, store = setup(tmp_path)
    monkeypatch.setattr(
        "bai_badminton.engine.detect_contacts",
        lambda *_args, **_kw: [
            ContactCandidate(
                frame=10, player_id=None, p=0.7, scores={"proximity": proximity, "redirect": 1.0, "impulse": 1.0}
            ),
        ],
    )
    engine._advance(window.n - 1)
    turns = store.query(types=["shuttle_turn"])
    assert len(seen) == int(eligible)
    assert len(turns) == int(not eligible)
    assert all(c.player_id is None for c in seen), "ambiguous side remains eligible evidence, never a named actor"
    if turns:
        assert turns[0].payload["contact_eligible"] is False
        assert turns[0].payload["reason"] == "insufficient_player_proximity"
        assert turns[0].evidence[0].scores["proximity"] == proximity
        assert turns[0].actors.player_id is None
        assert not store.query(types=["stroke"])
    store.close()
