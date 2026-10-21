from types import SimpleNamespace

import cv2
import numpy as np
import pytest

from bai_badminton.perception.scoreboard import ScoreboardReader, parse_scoreboard


def _box(x: float, y: float, w: float = 60, h: float = 20) -> list[list[float]]:
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]


def test_parse_two_rows_takes_last_number_as_current_points() -> None:
    boxes = [_box(0, 0), _box(100, 2), _box(140, 1), _box(0, 40), _box(100, 41), _box(140, 40)]
    txts = ["AXELSEN", "21", "14", "LEE Z.J.", "18", "9"]  # finished game then current game
    got = parse_scoreboard(boxes, txts, [0.99] * 6, frame_idx=7)
    assert got is not None
    r, bbox = got
    assert r.rows == (("AXELSEN", 14), ("LEE Z.J.", 9)) and r.frame_idx == 7
    assert bbox == (0.0, 0.0, 200.0, 61.0)


@pytest.mark.parametrize(
    "txts",
    [
        ["AXELSEN", "14"],  # one row
        ["12:45", "LIVE", "LEE", "9"],  # a clock is not a score; only one valid row
        ["AXELSEN", "45", "LEE", "9"],  # 45 is not a badminton game score
    ],
)
def test_parse_rejects_non_scoreboards(txts: list[str]) -> None:
    boxes = [_box(i % 2 * 100, i // 2 * 40) for i in range(len(txts))]
    assert parse_scoreboard(boxes, txts, [0.9] * len(txts), 0) is None


class _FakeOCR:
    """Reports a board only when the crop contains the white-text region at the top-left."""

    def __init__(self) -> None:
        self.shapes: list[tuple[int, ...]] = []

    def __call__(self, crop: np.ndarray) -> SimpleNamespace:
        self.shapes.append(crop.shape)
        if crop.mean() < 1:
            return SimpleNamespace(boxes=None, txts=None, scores=None)
        return SimpleNamespace(
            boxes=[_box(10, 10), _box(120, 10, 30), _box(10, 50), _box(120, 50, 30)],
            txts=["AXELSEN", "3", "LEE", "2"],
            scores=[0.95] * 4,
        )


def test_reader_searches_corners_then_locks_and_respects_rate() -> None:
    img = np.zeros((720, 1280, 3), np.uint8)
    img[0:150, 0:300] = 255
    ocr = _FakeOCR()
    r = ScoreboardReader(ocr, every=10)
    assert r.maybe_read(0, img) is not None  # top-left corner first
    assert r.roi is not None and r.roi[2] < 400 and r.roi[3] < 150
    assert r.maybe_read(5, img) is None and ocr.shapes.__len__() == 1  # rate limited
    assert r.maybe_read(10, img) is not None
    assert ocr.shapes[-1][:2] == (r.roi[3] - r.roi[1], r.roi[2] - r.roi[0])  # only the crop is read
    blank = np.zeros_like(img)
    for k in range(4):  # board disappears: after repeated misses the lock is dropped
        r.maybe_read(20 + 10 * k, blank)
    assert r.roi is None


def test_real_ocr_reads_a_rendered_scoreboard() -> None:
    pytest.importorskip("rapidocr")
    img = np.zeros((720, 1280, 3), np.uint8)
    img[:] = (40, 110, 40)
    cv2.rectangle(img, (20, 20), (380, 130), (20, 20, 20), -1)
    cv2.putText(img, "AXELSEN    14", (35, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2)
    cv2.putText(img, "LEE ZII JIA  9", (35, 115), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2)
    r = ScoreboardReader.load(every=1).maybe_read(0, img)
    assert r is not None
    assert [p for _, p in r.rows] == [14, 9]
    assert "AXELSEN" in r.rows[0][0].upper()
