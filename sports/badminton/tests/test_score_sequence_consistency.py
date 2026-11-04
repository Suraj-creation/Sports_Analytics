"""A new observation-run ID is not proof of another sporting point.

Synthetic source sequences isolate legal score anchoring from perception. A
backward board or missing source points stays reviewable; no point padding or
current-state jump repairs the discrepancy. Human decisions remain independent.
"""

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_badminton.perception_types import ScoreReading
from bai_badminton.rules import MatchConfig
from bai_engine.schema import Provenance
from bai_engine.store import EventStore


def _engine(tmp_path, monkeypatch, discipline):
    if discipline == "singles":
        players = {"P1": "Alice", "P2": "Bob"}
        names = ("ALICE", "BOB")
    else:
        players = {"P1": "Alex Reed / Morgan Chen", "P2": "Robin Singh / Taylor Park"}
        names = ("REED A. / CHEN M.", "SINGH R. / PARK T.")
    cfg = EngineConfig(fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline=discipline))
    store = EventStore(tmp_path / "source-sequence.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", cfg, store, player_names=players)
    monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "terminal_not_observed", .2))
    monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(
        calibrated=False, scoreboard=engine.ocr.board_change(seg.start, seg.end, until, 900),
    ))
    return engine, store, names


def _board(engine, frame, points, names):
    for offset in (0, 5):
        engine.on_ocr(ScoreReading(frame + offset, ((names[0], points[0]), (names[1], points[1])), conf=.95))


def _finalize(engine, start, end, until):
    engine._pending = [_PendingRally(RallySegment(start, end, None, "stationary"), [], None)]
    engine._finalize_pending(until)


def _first_point(engine, store, names):
    _board(engine, 0, (3, 2), names)
    _board(engine, 300, (4, 2), names)
    _finalize(engine, 100, 200, 400)
    assert len(store.query(types=["point"])) == 1
    assert engine.state.score == {"P1": 4, "P2": 2}


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
def test_first_midgame_source_increment_is_not_blocked_before_initial_score_seeding(tmp_path, monkeypatch, discipline):
    engine, store, names = _engine(tmp_path, monkeypatch, discipline)
    with store:
        _first_point(engine, store, names)
        point = store.query(types=["point"])[0]
        assert point.payload["state_before"]["score"] == {"P1": 3, "P2": 2}
        assert point.payload["state_after"]["score"] == {"P1": 4, "P2": 2}


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
@pytest.mark.parametrize("operation", ["live", "refold", "restart"])
def test_regressed_board_cannot_award_a_repeated_increment_even_with_a_new_source_id(
    tmp_path, monkeypatch, discipline, operation,
):
    engine, store, names = _engine(tmp_path, monkeypatch, discipline)
    with store:
        _first_point(engine, store, names)
        # A replay, stable OCR error or correction can repeat an earlier board.
        # Its later +1 observation must not increment an already anchored 4-2.
        _board(engine, 600, (3, 2), names)
        _board(engine, 800, (4, 2), names)
        _finalize(engine, 700, 750, 900)
        assert len(store.query(types=["point"])) == 1
        if operation == "restart":
            engine = BadmintonMatchEngine("S1", engine.cfg, store)
            engine.restore_from_log(900)
        if operation != "live":
            engine.set_reviewed_match_intervals([(100, 200), (700, 750)], Provenance(model="human"))

        assert len(store.query(types=["point"])) == 1
        assert engine.state.score == {"P1": 4, "P2": 2}
        rallies = store.query(types=["rally_end"])
        assert len({r.payload["score_transition"]["transition_id"] for r in rallies}) == 2
        assert rallies[-1].payload["winner"] is None
        assert rallies[-1].payload["score_transition_status"] in {
            "source_score_regression", "score_sequence_conflict",
        }
        assert store.query(types=["broadcast_score"])[-1].payload["rows"] == [
            {"name": names[0], "points": 4}, {"name": names[1], "points": 2},
        ]


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
def test_missing_source_points_do_not_become_a_fabricated_partial_score_or_state_jump(tmp_path, monkeypatch, discipline):
    engine, store, names = _engine(tmp_path, monkeypatch, discipline)
    with store:
        _first_point(engine, store, names)
        _board(engine, 600, (6, 2), names)
        _board(engine, 800, (7, 2), names)
        _finalize(engine, 700, 750, 900)

        assert len(store.query(types=["point"])) == 1
        assert engine.state.score == {"P1": 4, "P2": 2}
        rally = store.query(types=["rally_end"])[-1]
        assert rally.payload["winner"] is None
        assert rally.payload["score_transition_status"] in {"source_score_gap", "score_sequence_conflict"}
        assert store.query(types=["broadcast_score"])[-1].payload["rows"][0]["points"] == 7


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
def test_a_legitimate_increment_with_swapped_broadcast_rows_uses_the_named_winner_not_row_index(
    tmp_path, monkeypatch, discipline,
):
    engine, store, names = _engine(tmp_path, monkeypatch, discipline)
    with store:
        _first_point(engine, store, names)
        _board(engine, 600, (2, 4), names[::-1])
        _board(engine, 800, (3, 4), names[::-1])
        _finalize(engine, 700, 750, 900)

        assert len(store.query(types=["point"])) == 2
        assert store.query(types=["point"])[-1].payload["winner"] == "P2"
        assert engine.state.score == {"P1": 4, "P2": 3}


def test_an_explicit_human_winner_is_independent_of_a_conflicting_observed_score_sequence(tmp_path, monkeypatch):
    engine, store, names = _engine(tmp_path, monkeypatch, "singles")
    with store:
        _first_point(engine, store, names)
        _board(engine, 600, (3, 2), names)
        _board(engine, 800, (4, 2), names)
        _finalize(engine, 700, 750, 900)
        assert len(store.query(types=["point"])) == 1
        second = store.query(types=["rally_end"])[-1]
        engine.correct_rally_winner(second.event_id, "P1", Provenance(model="human"))

        assert len(store.query(types=["point"])) == 2
        assert engine.state.score == {"P1": 5, "P2": 2}
        assert store.query(types=["point"])[-1].payload["source"] == "human"
