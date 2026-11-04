"""A scoreboard value visible before an exchange cannot be its point evidence.

The frame pattern reproduces the India control trace, but these are software
association fixtures, not an independently reviewed video-accuracy measurement.
Names bind score competitors only; they do not bind physical hitter tracks.
"""

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_badminton.perception_types import ChunkPerception, FramePerception, ScoreReading
from bai_badminton.score_ocr import ScoreReconciler, ScoreTransitionRef
from bai_engine.store import EventStore


_NAMES = {"P1": "Lakshya Sen", "P2": "Loh Kean Yew"}


def _readings():
    return [
        ScoreReading(frame, (("LOH", 2), ("SEN", sen_points)), conf=.95)
        for frame, sen_points in (
            (2714, 0), (2744, 0), (3390, 0), (3420, 0),
            (3732, 1), (3762, 1), (3900, 1), (3930, 1),
        )
    ]


def _score():
    score = ScoreReconciler(player_names=_NAMES)
    for reading in _readings():
        score.add(reading)
    return score


def test_first_new_value_before_rally_start_cannot_become_its_delayed_changed_board():
    score = _score()
    # Confirmation is after start, but its first supporting observation is not.
    assert score.board_change(3735, 3821, 4000, 900) != "changed"
    assert score.winner_from_ocr({"P1": 1, "P2": 2}, 3735, 3821, 4000, None, 900)[0] is None


def test_the_earlier_rally_keeps_its_legitimate_delayed_source_increment():
    score = _score()
    assert score.board_change(2812, 3307, 4000, 900) == "changed"
    assert score.winner_from_ocr({"P1": 0, "P2": 2}, 2812, 3307, 4000, None, 900) == ("P1", "ocr")
    ref = score.source_transition(2812, 3307, 4000, 900)
    assert ref is not None
    assert ref.after_frames == (3732, 3762)


def test_new_value_first_observed_exactly_at_start_is_not_treated_as_preexisting():
    score = _score()
    assert score.board_change(3732, 3821, 4000, 900) == "changed"
    assert score.winner_from_ocr({"P1": 0, "P2": 2}, 3732, 3821, 4000, None, 900) == ("P1", "ocr")


def test_preexisting_value_does_not_steal_or_make_the_earlier_point_ambiguous_in_the_engine(tmp_path, monkeypatch):
    with EventStore(tmp_path / "score-onset.sqlite", "S1") as store:
        engine = BadmintonMatchEngine(
            "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store, player_names=_NAMES,
        )
        monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "terminal_not_observed", .2))
        monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(
            calibrated=False, scoreboard=engine.ocr.board_change(seg.start, seg.end, until, 900),
        ))
        engine._pending = [
            _PendingRally(RallySegment(start, end, None, "stationary"), [], None)
            for start, end in ((2812, 3307), (3735, 3821))
        ]
        # OCR is buffered before temporal processing, as in a production chunk.
        # Real ingest, rule folding, source claims and event persistence remain.
        engine.ingest(ChunkPerception(
            0, 4000, [FramePerception(i, None, 0.0) for i in range(4001)], ocr=_readings(),
        ))

        points = store.query(types=["point"])
        assert len(points) == 1
        assert points[0].frame_start == 3307
        assert points[0].payload["winner"] == "P1"
        assert engine.state.score == {"P1": 1, "P2": 2}
        rallies = store.query(types=["rally_end"])
        assert rallies[0].payload["winner"] == "P1"
        assert rallies[1].payload["winner"] is None
        ref = ScoreTransitionRef.from_public(rallies[0].payload["score_transition"])
        assert ref is not None and ref.after_frames == (3732, 3762)
