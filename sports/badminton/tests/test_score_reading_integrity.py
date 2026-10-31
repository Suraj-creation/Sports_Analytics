"""OCR noise and board resets cannot create extra sporting points."""

import pytest

from bai_badminton.perception_types import ScoreReading
from bai_badminton.score_ocr import ScoreReconciler


@pytest.mark.parametrize("confidence", [float("nan"), float("inf"), -0.1, 1.1])
def test_nonfinite_or_out_of_range_reading_is_not_evidence(confidence):
    score = ScoreReconciler()
    score.add(ScoreReading(0, (("A", 1), ("B", 0)), conf=confidence))
    assert score.readings == []


@pytest.mark.parametrize("previous", [(21, 19), (30, 29), (5, 21)])
def test_reset_from_an_already_completed_game_does_not_award_the_point_twice(previous):
    assert ScoreReconciler._winning_row(previous, (0, 0)) is None


def test_swapped_broadcast_rows_rebind_names_before_the_next_point():
    score = ScoreReconciler(player_names={"P1": "A", "P2": "B"})
    for frame in (0, 1):
        score.add(ScoreReading(frame, (("A", 2), ("B", 1)), conf=0.9))
    for frame in (3, 4):
        score.add(ScoreReading(frame, (("B", 2), ("A", 2)), conf=0.9))
    for frame in (7, 8):
        score.add(ScoreReading(frame, (("B", 3), ("A", 2)), conf=0.9))
    assert score.winner_from_ocr({"P1": 2, "P2": 2}, 5, 6, 9, None, 30) == ("P2", "ocr")


def test_changed_names_with_equal_numbers_do_not_corroborate_one_reading():
    score = ScoreReconciler()
    score.add(ScoreReading(0, (("A", 2), ("B", 1)), conf=0.9))
    score.add(ScoreReading(1, (("C", 2), ("D", 1)), conf=0.9))
    assert score.stable_before(2, 0) is None


def test_midgame_seed_uses_the_row_order_of_the_historic_reading(tmp_path):
    from types import SimpleNamespace

    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
    from bai_engine.store import EventStore

    with EventStore(tmp_path / "seed.sqlite", "S1") as store:
        engine = BadmintonMatchEngine(
            "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store, player_names={"P1": "A", "P2": "B"}
        )
        for frame in (0, 1):
            engine.ocr.add(ScoreReading(frame, (("A", 8), ("B", 3)), conf=0.9))
        for frame in (110, 111):
            engine.ocr.add(ScoreReading(frame, (("B", 4), ("A", 8)), conf=0.9))
        engine._rallies = [SimpleNamespace(record=SimpleNamespace(official=True, start=30))]
        engine._refold = lambda *args, **kwargs: None
        engine._maybe_seed_from_board()
        assert engine._base_state.score == {"P1": 8, "P2": 3}
        assert store.query(types=["match_phase"])[0].payload["base_state"]["score"] == {"P1": 8, "P2": 3}
