"""A pre-start board can be corroborated later, within the decision horizon."""

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_badminton.perception_types import ChunkPerception, FramePerception, ScoreReading
from bai_badminton.rules import MatchConfig
from bai_badminton.score_ocr import ScoreReconciler
from bai_engine.store import EventStore


def _add(score, readings):
    for frame, value in readings:
        score.add(ScoreReading(frame, (("LOH", 2), ("SEN", value)), conf=.95))


def _score(readings):
    score = ScoreReconciler(player_names={"P1": "Lakshya Sen", "P2": "Loh Kean Yew"})
    _add(score, readings)
    return score


def test_before_value_onset_precedes_start_even_when_its_confirmation_follows_start():
    score = _score([(3390, 0), (3420, 0), (3732, 1), (3762, 1), (4530, 2), (4560, 2)])
    assert score.board_change(3735, 4466, 4586, 900) == "changed"
    assert score.winner_from_ocr({"P1": 1, "P2": 2}, 3735, 4466, 4586, None, 900) == ("P1", "ocr")
    ref = score.source_transition(3735, 4466, 4586, 900)
    assert ref is not None
    assert ref.before_frames == (3732, 3762)
    assert ref.after_frames == (4530, 4560)


def test_future_corroboration_cannot_retroactively_supply_a_baseline_to_an_earlier_decision():
    readings = [(3390, 0), (3420, 0), (3732, 1), (4530, 2), (4560, 2)]
    past = _score(readings)
    future = _score([*readings, (4700, 1), (4730, 1)])
    for score in (past, future):
        assert score.winner_from_ocr({"P1": 1, "P2": 2}, 3735, 4466, 4586, None, 900)[0] is None
        assert score.source_transition(3735, 4466, 4586, 900) is None


def test_a_value_first_seen_after_start_is_not_reclassified_as_a_before_state():
    score = _score([(3390, 0), (3420, 0), (3740, 1), (3770, 1), (4530, 2), (4560, 2)])
    assert score.winner_from_ocr({"P1": 1, "P2": 2}, 3735, 4466, 4586, None, 900)[0] is None
    assert score.source_transition(3735, 4466, 4586, 900) is None


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
def test_retrospective_before_state_allows_only_the_next_legal_point_for_individual_or_team(
    tmp_path, monkeypatch, discipline,
):
    names = ("LOH", "SEN") if discipline == "singles" else ("TEAM SOUTH", "TEAM NORTH")
    players = {"P1": "Lakshya Sen", "P2": "Loh Kean Yew"} if discipline == "singles" else {
        "P1": "Team North", "P2": "Team South",
    }
    with EventStore(tmp_path / "retrospective-before.sqlite", "S1") as store:
        engine = BadmintonMatchEngine(
            "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline=discipline)),
            store, player_names=players,
        )
        monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "terminal_not_observed", .2))
        monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(
            calibrated=False, scoreboard=engine.ocr.board_change(seg.start, seg.end, until, 900),
        ))

        def reading(frame, value):
            return ScoreReading(frame, ((names[0], 2), (names[1], value)), conf=.95)

        engine._pending = [_PendingRally(RallySegment(2812, 3307, None, "stationary"), [], None)]
        engine.ingest(ChunkPerception(
            0, 4000, [FramePerception(i, None, 0.0) for i in range(4001)],
            ocr=[reading(frame, value) for frame, value in (
                (2714, 0), (2744, 0), (3390, 0), (3420, 0),
                (3732, 1), (3762, 1), (3900, 1), (3930, 1),
            )],
        ))
        assert engine.state.score == {"P1": 1, "P2": 2}
        assert [point.frame_start for point in store.query(types=["point"])] == [3307]

        engine._pending = [_PendingRally(RallySegment(3735, 4466, None, "stationary"), [], None)]
        engine.ingest(ChunkPerception(
            4001, 4700, [FramePerception(i, None, 0.0) for i in range(4001, 4701)],
            ocr=[reading(4530, 2), reading(4560, 2)],
        ))
        points = store.query(types=["point"])
        assert [point.frame_start for point in points] == [3307, 4466]
        assert points[-1].payload["state_before"]["score"] == {"P1": 1, "P2": 2}
        assert engine.state.score == {"P1": 2, "P2": 2}


def test_first_official_midgame_rally_seeds_from_its_corroborated_pre_start_onset(tmp_path, monkeypatch):
    with EventStore(tmp_path / 'first-retrospective.sqlite', 'S1') as store:
        engine = BadmintonMatchEngine('S1', EngineConfig(fps=30, frame_width=1280, frame_height=720),
                                      store, player_names={'P1': 'Lakshya Sen', 'P2': 'Loh Kean Yew'})
        monkeypatch.setattr(engine, '_outcome', lambda seg: ('unknown', 'unknown', 'terminal_not_observed', .2))
        monkeypatch.setattr(engine, '_phase_evidence', lambda seg, until: RallyEvidence(
            calibrated=False, scoreboard=engine.ocr.board_change(seg.start, seg.end, until, 900)))
        for frame, value in ((3390, 0), (3420, 0), (3732, 1), (3762, 1), (4530, 2), (4560, 2)):
            engine.on_ocr(ScoreReading(frame, (('LOH', 2), ('SEN', value)), conf=.95))
        engine._pending = [_PendingRally(RallySegment(3735, 4466, None, 'stationary'), [], None)]
        engine._finalize_pending(4700)
        points = store.query(types=['point'])
        assert len(points) == 1
        assert points[0].payload['state_before']['score'] == {'P1': 1, 'P2': 2}
        assert engine.state.score == {'P1': 2, 'P2': 2}
