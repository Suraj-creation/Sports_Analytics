from bai_badminton.perception_types import ScoreReading
from bai_badminton.score_ocr import ScoreReconciler


def _read(rec: ScoreReconciler, frame: int, a: int, b: int) -> None:
    for k in (0, 5):  # a value counts once it is read identically twice
        rec.add(ScoreReading(frame_idx=frame + k, rows=(("AXELSEN", a), ("LEE", b)), conf=0.9))


def test_winner_row_from_board_delta_not_engine_score() -> None:
    rec = ScoreReconciler(player_names={"P1": "Viktor Axelsen", "P2": "Lee Zii Jia"})
    _read(rec, 0, 11, 9)
    _read(rec, 300, 11, 10)
    # the engine still thinks 0-0 (video started mid-game): the board delta decides
    assert rec.winner_from_ocr({"P1": 0, "P2": 0}, 100, 200, 400, "P1", lookback=900) == ("P2", "ocr")


def test_unchanged_board_and_game_reset() -> None:
    rec = ScoreReconciler(player_names={"P1": "Axelsen", "P2": "Lee"})
    _read(rec, 0, 20, 18)
    _read(rec, 300, 0, 0)  # new game: the row that led on game point won
    assert rec.winner_from_ocr({"P1": 20, "P2": 18}, 100, 200, 400, None, lookback=900) == ("P1", "ocr")
    _read(rec, 600, 0, 0)
    assert rec.board_change(500, 550, 700, lookback=900) == "unchanged"
    assert rec.board_change(100, 200, 400, lookback=900) == "changed"
    assert rec.board_change(10_000, 10_100, 10_200, lookback=900) is None  # no readings: no claim


def test_row_mapping_survives_one_wrong_geometry_vote() -> None:
    rec = ScoreReconciler()  # no names: learn rows from geometry agreement
    score = [0, 0]
    _read(rec, 0, 0, 0)
    geometry = ["P1", "P1", "P2", "P1", "P1"]  # third vote is wrong (row 0 incremented again)
    for k, g in enumerate(geometry):
        score[0] += 1
        _read(rec, 300 * (k + 1), *score)
        w, src = rec.winner_from_ocr({}, 300 * (k + 1) - 100, 300 * (k + 1) - 50, 300 * (k + 1) + 50, g, lookback=900)
    assert rec.row_map == {0: "P1", 1: "P2"}
    assert (w, src) == ("P1", "ocr")


def test_low_confidence_readings_are_ignored() -> None:
    rec = ScoreReconciler()
    rec.add(ScoreReading(frame_idx=0, rows=(("A", 1), ("B", 0)), conf=0.3))
    assert rec.readings == []
