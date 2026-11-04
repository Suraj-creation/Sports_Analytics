"""Broadcast scoreboard (score bug) reading with RapidOCR (validation DEF-03: OCR was declared in
the profiles but never run, so rally winners relied on landing geometry alone).

Cost is the constraint: PP-OCR on CPU takes seconds per full 720p frame.  So the reader

* reads at configured ``every`` frames on eligible main views, independently of rally state;
* searches the four frame corners for the bug, one corner per call, and then *locks* onto the
  region where a two-row "name … points" board was read (later calls OCR only that crop);
* drops the lock after repeated misses (graphics change, close-ups) and searches again.

Parsing is pure (:func:`parse_scoreboard`) so it is tested without the OCR model.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from importlib.metadata import version
from pathlib import Path
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


@dataclass(frozen=True)
class _ScoreText:
    index: int
    pts: NDArray[np.float64]
    text: str
    name: str
    numbers: tuple[int, ...]
    conf: float
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def centre(self) -> float:
        return (self.y0 + self.y1) / 2


@dataclass(frozen=True)
class _ScoreRow:
    name: str
    points: int
    conf: float
    members: frozenset[int]
    pts: NDArray[np.float64]
    name_left: float
    name_right: float
    score_right: float
    centre: float
    height: float


def _same_baseline(left: _ScoreText, right: _ScoreText) -> bool:
    # Font/geometry gates are conservative uncalibrated layout checks.
    small, large = min(left.height, right.height), max(left.height, right.height)
    return large <= 1.8 * small and abs(left.centre - right.centre) <= 0.6 * small


def _score_rows(items: list[_ScoreText]) -> list[_ScoreRow]:
    names = [item for item in items if item.name]
    groups: list[list[_ScoreText]] = []
    # Join adjacent name fragments only. A distant sponsor on the same scanline
    # must not become part of a competitor's name; a number separates fields.
    remaining = {item.index: item for item in names}
    while remaining:
        seed = remaining.pop(min(remaining))
        group, pending = [seed], [seed]
        while pending:
            anchor = pending.pop()
            for key, other in list(remaining.items()):
                left, right = sorted((anchor, other), key=lambda item: item.x0)
                gap = right.x0 - left.x1
                separated = any(not item.name and item.numbers and left.x1 <= item.x0 < right.x0
                                and _same_baseline(left, item) for item in items)
                if (_same_baseline(left, right) and not left.numbers and not separated
                        and -0.25 * min(left.height, right.height) <= gap <= 1.5 * min(left.height, right.height)):
                    group.append(other)
                    pending.append(other)
                    del remaining[key]
        groups.append(sorted(group, key=lambda item: (item.x0, item.index)))
    rows = []
    for group in groups:
        name_left, name_right = min(item.x0 for item in group), max(item.x1 for item in group)
        height = float(np.median([item.height for item in group]))
        centre = float(np.median([item.centre for item in group]))
        anchor = group[0]
        numbers: list[_ScoreText] = []
        for item in group:
            name_matches = list(_NAME.finditer(item.text))
            number_matches = list(_NUM.finditer(item.text))
            if item.numbers and name_matches and number_matches and number_matches[-1].start() >= name_matches[-1].end():
                numbers.append(item)
        numbers.extend(item for item in items if not item.name and item.numbers and ':' not in item.text
                       and item.x0 >= name_right - 0.25 * height and _same_baseline(anchor, item))
        if not numbers:
            continue
        numbers.sort(key=lambda item: (item.x1, item.x0, item.index))
        current = numbers[-1]
        if current.numbers[-1] > 30:
            continue
        # A close clock/text field to the right of an old game value is not
        # permission to treat that completed-game value as the current score.
        if any(item.index not in {part.index for part in group + numbers}
               and item.x0 > current.x0 and item.x0 - current.x1 <= 2 * height
               and _same_baseline(anchor, item) for item in items):
            continue
        used = {item.index: item for item in group + numbers}
        pts = np.concatenate([item.pts for item in used.values()])
        rows.append(_ScoreRow(
            name=' '.join(item.name for item in group), points=current.numbers[-1],
            conf=min(item.conf for item in used.values()), members=frozenset(used), pts=pts,
            name_left=name_left, name_right=name_right, score_right=current.x1,
            centre=centre, height=height,
        ))
    return sorted(rows, key=lambda row: (row.centre, row.name_left))


def parse_scoreboard(
    boxes: Sequence[Any], txts: Sequence[str], scores: Sequence[float], frame_idx: int
) -> tuple[ScoreReading, tuple[float, float, float, float]] | None:
    """Find one coherent two-row name-left/score-right board among OCR boxes.

    The returned names and points remain model observations. Layout support is
    uncalibrated and does not establish identity or an accepted point. Preserve
    the rightmost current-game number and abstain on multiple plausible boards,
    including three aligned competitor rows. Unrelated corner text is excluded
    from the board bounds so a subsequent locked crop does not retain sponsors.
    """
    items = []
    for index, (box, text, score) in enumerate(zip(boxes, txts, scores, strict=False)):
        try:
            pts = np.asarray(box, dtype=float)
            conf = float(score)
            if pts.shape != (4, 2) or not np.isfinite(pts).all() or not np.isfinite(conf) or not 0 <= conf <= 1:
                return None
            x0, y0 = pts.min(axis=0)
            x1, y1 = pts.max(axis=0)
            if x1 <= x0 or y1 <= y0:
                return None
        except (TypeError, ValueError):
            return None
        raw = str(text).strip()
        items.append(_ScoreText(index, pts, raw, ' '.join(_NAME.findall(raw)),
                                tuple(int(number) for number in _NUM.findall(raw)), conf,
                                float(x0), float(y0), float(x1), float(y1)))
    rows = _score_rows(items)
    pairs = []
    for index, first in enumerate(rows):
        for second in rows[index + 1:]:
            low, high = min(first.height, second.height), max(first.height, second.height)
            if (first.members & second.members or high > 1.6 * low
                    or not 0.65 * low <= second.centre - first.centre <= 3.5 * high):
                continue
            align = max(2.0, 0.75 * high)
            name_aligned = (abs(first.name_left - second.name_left) <= align
                            or abs(first.name_right - second.name_right) <= align)
            if name_aligned and abs(first.score_right - second.score_right) <= align:
                pairs.append((first, second))
    if len(pairs) != 1:
        return None
    first, second = pairs[0]
    pts = np.concatenate((first.pts, second.pts))
    bounds = (float(pts[:, 0].min()), float(pts[:, 1].min()),
              float(pts[:, 0].max()), float(pts[:, 1].max()))
    return ScoreReading(frame_idx=frame_idx, rows=((first.name, first.points), (second.name, second.points)),
                        conf=min(first.conf, second.conf)), bounds


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
    runtime: dict[str, Any] = field(default_factory=dict)

    @property
    def model_ref(self) -> str:
        """Actual package and weights, not the historical rapidocr_v4 alias."""
        if not self.runtime:
            return "rapidocr@unknown"
        weights = {stage: info["sha256"] for stage, info in self.runtime["stages"].items()}
        fingerprint = hashlib.sha256(json.dumps(weights, sort_keys=True).encode()).hexdigest()[:12]
        return f"rapidocr@{self.runtime['package_version']}+{fingerprint}"

    @classmethod
    def load(cls, every: int, *, backend: str = "onnx-cpu") -> ScoreboardReader:
        if backend not in ("onnx-cpu", "onnx-cuda"):
            raise ValueError(f"unsupported RapidOCR backend: {backend}")
        from rapidocr import RapidOCR

        # Keep package-selected weights, thresholds and image preprocessing intact.
        ocr = RapidOCR(params={"EngineConfig.onnxruntime.use_cuda": backend == "onnx-cuda"})
        runtime: dict[str, Any] = {"package_version": version("rapidocr"), "requested_backend": backend, "stages": {}}
        for stage, section in (("det", "Det"), ("cls", "Cls"), ("rec", "Rec")):
            # RapidOCR 3.10 loads lazily. Initialize before claiming a loaded
            # model, checking actual providers rather than assuming the flag won.
            loader = getattr(ocr, f"_load_{stage}_model", None)
            if loader is not None:
                loader()
            component = getattr(ocr, f"text_{stage}", None)
            engine = getattr(component, "session", None)
            session = getattr(engine, "session", None)
            if session is None or not hasattr(session, "get_providers"):
                raise RuntimeError(f"RapidOCR {stage} ONNX session unavailable for provider verification")
            # ONNX Runtime retains the loaded artifact path on its Python session.
            # Refuse unknown artifacts instead of claiming a configured filename.
            model_path = getattr(session, "_model_path", None)
            if not model_path:
                raise RuntimeError(f"RapidOCR {stage} artifact path unavailable")
            path = Path(model_path)
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            config = getattr(ocr.cfg, section)
            configured_version = getattr(config, "ocr_version", "unknown")
            ocr_version = getattr(configured_version, "value", str(configured_version))
            runtime["stages"][stage] = {
                "model_file": path.name,
                "sha256": digest,
                "configured_ocr_version": ocr_version,
                "providers": session.get_providers(),
                "provider_options": session.get_provider_options(),
            }
        expected = "CUDAExecutionProvider" if backend == "onnx-cuda" else "CPUExecutionProvider"
        runtime["backend_fallback"] = any(
            not info["providers"] or info["providers"][0] != expected for info in runtime["stages"].values()
        )
        return cls(ocr, every, runtime=runtime)

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
