"""A broadcast score may remain unchanged before its delayed update appears."""

import pytest

from bai_badminton.perception_types import ScoreReading
from bai_badminton.score_ocr import ScoreReconciler


def _read(score, frame, points):
    for offset in (0, 5):
        score.add(ScoreReading(frame + offset, (("A", points[0]), ("B", points[1])), conf=0.9))


def test_stable_old_board_does_not_hide_a_delayed_point_within_the_wait_window():
    score = ScoreReconciler(player_names={"P1": "A", "P2": "B"})
    _read(score, 0, (3, 2))
    _read(score, 205, (3, 2))
    _read(score, 250, (3, 3))
    assert score.board_change(100, 200, 300, 900) == "changed"
    assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 300, None, 900) == ("P2", "ocr")


@pytest.mark.parametrize("readings", [
    [(4, 2), (4, 3)],  # two different points occurred inside one waiting window
    [(8, 8), (3, 3)],  # an incompatible stable value cannot be skipped to choose a convenient +1
])
def test_ambiguous_stable_board_changes_cannot_confirm_one_rally_winner(readings):
    score = ScoreReconciler(player_names={"P1": "A", "P2": "B"})
    _read(score, 0, (3, 2))
    for index, points in enumerate(readings):
        _read(score, 205 + 30 * index, points)
    assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 300, None, 900)[0] is None


def test_old_board_without_a_later_update_stays_unchanged():
    score = ScoreReconciler(player_names={"P1": "A", "P2": "B"})
    _read(score, 0, (3, 2))
    _read(score, 205, (3, 2))
    assert score.board_change(100, 200, 300, 900) == "unchanged"
    assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 300, None, 900)[0] is None


def test_completed_game_then_reset_still_represents_one_game_winning_point():
    score = ScoreReconciler(player_names={"P1": "A", "P2": "B"})
    _read(score, 0, (20, 18))
    _read(score, 205, (21, 18))
    _read(score, 250, (0, 0))
    assert score.board_change(100, 200, 300, 900) == "changed"
    assert score.winner_from_ocr({"P1": 20, "P2": 18}, 100, 200, 300, None, 900) == ("P1", "ocr")
