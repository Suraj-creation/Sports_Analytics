"""Broadcast scoreboard (score bug) reading with RapidOCR (validation DEF-03: OCR was declared in
the profiles but never run, so rally winners relied on landing geometry alone).

Cost is the constraint: PP-OCR on CPU takes seconds per full 720p frame.  So the reader

* only runs between rallies (the score cannot change during one) at ``every`` frames;
* searches the four frame corners for the bug, one corner per call, and then *locks* onto the
  region where a two-row "name … points" board was read (later calls OCR only that crop);
* drops the lock after repeated misses (graphics change, close-ups) and searches again.

Parsing is pure (:func:`parse_scoreboard`) so it is tested without the OCR model.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from bai_badminton.perception_types import ScoreReading

_NAME = re.compile(r"[A-Za-z][A-Za-z.'\-]*")
_NUM = re.compile(r"(?<![\d:])\d{1,2}(?![\d:])")  # 1-2 digit numbers, not clock times
# (x0, y0, x1, y1) as fractions of the frame: score bugs live in the corners
CORNERS: tuple[tuple[float, float, float, float], ...] = (
    (0.0, 0.0, 0.45, 0.25),
    (0.0, 0.75, 0.45, 1.0),
    (0.55, 0.0, 1.0, 0.25),
    (0.55, 0.75, 1.0, 1.0),
)


def parse_scoreboard(
    boxes: Sequence[Any], txts: Sequence[str], scores: Sequence[float], frame_idx: int
) -> tuple[ScoreReading, tuple[float, float, float, float]] | None:
    """Two text rows, each with a name and a current-game score (the last 1–2 digit number; bugs
    often also list finished games before it). Returns the reading and its pixel bounding box."""
    items = []
    for box, t, sc in zip(boxes, txts, scores, strict=False):
        pts = np.asarray(box, dtype=float).reshape(-1, 2)
        y0, y1 = pts[:, 1].min(), pts[:, 1].max()
        items.append((pts[:, 0].min(), (y0 + y1) / 2, y1 - y0, str(t).strip(), float(sc), pts))
    items.sort(key=lambda i: i[1])
    rows: list[list[Any]] = []
    for it in items:  # group boxes into text rows by vertical centre
        if rows and abs(rows[-1][-1][1] - it[1]) <= 0.6 * max(it[2], rows[-1][-1][2]):
            rows[-1].append(it)
        else:
            rows.append([it])
    parsed = []
    for row in rows:
        row.sort(key=lambda i: i[0])
        text = " ".join(i[3] for i in row)
        name = " ".join(_NAME.findall(text))
        nums = [int(n) for n in _NUM.findall(text)]
        if name and nums:
            parsed.append((name, nums[-1], min(i[4] for i in row), row))
    if len(parsed) != 2 or any(p[1] > 30 for p in parsed):
        return None
    pts = np.concatenate([i[5] for p in parsed for i in p[3]])
    bbox = (float(pts[:, 0].min()), float(pts[:, 1].min()), float(pts[:, 0].max()), float(pts[:, 1].max()))
    reading = ScoreReading(
        frame_idx=frame_idx,
        rows=((parsed[0][0], parsed[0][1]), (parsed[1][0], parsed[1][1])),
        conf=min(p[2] for p in parsed),
    )
    return reading, bbox


@dataclass
class ScoreboardReader:
    ocr: Any  # callable image -> result with .boxes/.txts/.scores (rapidocr.RapidOCR)
    every: int  # frames between reads
    max_misses: int = 4
    roi: tuple[int, int, int, int] | None = None  # locked crop (pixels)
    _corner: int = 0
    _misses: int = 0
    _last: int = field(default=-(10**9))
    calls: int = 0

    @classmethod
    def load(cls, every: int) -> ScoreboardReader:
        from rapidocr import RapidOCR

        return cls(RapidOCR(), every)

    def maybe_read(self, frame_idx: int, img: NDArray[np.uint8]) -> ScoreReading | None:
        if frame_idx - self._last < self.every:
            return None
        self._last = frame_idx
        h, w = img.shape[:2]
        if self.roi is not None:
            x0, y0, x1, y1 = self.roi
        else:
            fx0, fy0, fx1, fy1 = CORNERS[self._corner]
            self._corner = (self._corner + 1) % len(CORNERS)
            x0, y0, x1, y1 = int(fx0 * w), int(fy0 * h), int(fx1 * w), int(fy1 * h)
        crop = img[y0:y1, x0:x1]
        self.calls += 1
        res = self.ocr(crop)
        got = None
        if res is not None and getattr(res, "txts", None):
            got = parse_scoreboard(res.boxes, res.txts, res.scores, frame_idx)
        if got is None:
            self._misses += 1
            if self.roi is not None and self._misses >= self.max_misses:
                self.roi, self._misses = None, 0
            return None
        reading, (bx0, by0, bx1, by1) = got
        self._misses = 0
        if self.roi is None:  # lock onto the board with a margin
            m = int(0.25 * max(by1 - by0, 20))
            self.roi = (
                max(0, x0 + int(bx0) - m),
                max(0, y0 + int(by0) - m),
                min(w, x0 + int(bx1) + m),
                min(h, y0 + int(by1) + m),
            )
        return reading
