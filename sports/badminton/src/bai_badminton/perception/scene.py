"""Scene structure: camera cuts, court presence (main-camera gate) and court auto-proposal.

* :class:`CutDetector` — HSV-histogram correlation between consecutive downscaled frames; a
  sharp drop marks a camera cut.  Runs on every decoded frame at negligible cost (it reuses the
  frames already decoded for the models — no second decode pass).
* :class:`CourtPresence` — fraction of court-coloured pixels inside the calibrated court polygon
  (legacy ``court_presence.py`` idea).  Replays, close-ups and crowd shots fail the gate, so their
  frames are marked ``replay`` and perception events are suppressed there.  The mat colour is
  *learned* from keyframes inside the calibrated court (validation DEF-06: a hard-coded green band
  marked every frame of blue / purple / wood courts as a replay and stopped perception).
* :func:`propose_corners` — port of the legacy mat contour heuristic, tried for each mat colour
  family; used only as a *proposal* that the user confirms/adjusts in the calibration UI (no
  pretrained badminton court keypoint model exists; a trained one is planned — report T4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

MIN_COURT_FRAC = 0.08


@dataclass(frozen=True)
class MatBand:
    """An HSV colour family for court mats (OpenCV hue 0–179; ranges may wrap through red)."""

    name: str
    hues: tuple[tuple[int, int], ...]
    s_min: int = 35
    v_min: int = 35

    def mask(self, hsv: NDArray[Any]) -> NDArray[np.uint8]:
        out = np.zeros(hsv.shape[:2], np.uint8)
        for lo, hi in self.hues:
            out |= cv2.inRange(  # type: ignore[arg-type]  # cv2 stubs: uint8 mask
                hsv, np.array([lo, self.s_min, self.v_min]), np.array([hi, 255, 255])
            )
        return out


GREEN = MatBand("green", ((30, 90),))
MAT_BANDS: tuple[MatBand, ...] = (
    GREEN,
    MatBand("blue", ((90, 130),)),
    MatBand("purple_red", ((130, 179), (0, 7))),
    MatBand("wood", ((8, 29),), s_min=60),
)
SMALL = (320, 180)
HUE_TOL = 12


def small_hsv(frame: NDArray[np.uint8]) -> tuple[NDArray[Any], tuple[int, int]]:
    """Downscaled HSV copy (cheap to keep for colour learning) and the original (w, h)."""
    small = cv2.resize(frame, SMALL, interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(small, cv2.COLOR_BGR2HSV), (frame.shape[1], frame.shape[0])


MAX_COURT_FRAC = 0.85  # more than this and the court boundary is not in view


@dataclass
class CutDetector:
    threshold: float = 0.55  # histogram correlation below this → cut
    min_gap: int = 8  # frames; ignore flicker
    _prev: NDArray[np.float32] | None = None
    _since: int = 10**9
    shot_id: int = 0

    def _hist(self, frame: NDArray[np.uint8]) -> NDArray[np.float32]:
        small = cv2.resize(frame, (96, 54), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        h = cv2.calcHist([hsv], [0, 1], None, [16, 8], [0, 180, 0, 256])
        return cv2.normalize(h, h).flatten()

    def update(self, frame: NDArray[np.uint8]) -> bool:
        """Feed one frame; returns True when this frame starts a new camera shot."""
        h = self._hist(frame)
        cut = False
        if self._prev is not None:
            corr = float(cv2.compareHist(self._prev, h, cv2.HISTCMP_CORREL))
            if corr < self.threshold and self._since >= self.min_gap:
                cut = True
                self.shot_id += 1
                self._since = 0
        self._prev = h
        self._since += 1
        return cut


@dataclass
class CourtPresence:
    polygon: NDArray[np.float32]  # court polygon in analysis px
    min_fraction: float = 0.45
    band: MatBand = GREEN
    _masks: dict[tuple[int, int], NDArray[np.bool_]] = field(default_factory=dict, repr=False)

    def _inside(self, size: tuple[int, int]) -> NDArray[np.bool_]:
        if size not in self._masks:
            sx, sy = SMALL[0] / size[0], SMALL[1] / size[1]
            m = np.zeros((SMALL[1], SMALL[0]), np.uint8)
            cv2.fillPoly(m, [(self.polygon * [sx, sy]).astype(np.int32)], 255)
            self._masks[size] = m > 0
        return self._masks[size]

    def _fraction(self, hsv: NDArray[Any], size: tuple[int, int], band: MatBand) -> float:
        inside = self._inside(size)
        return float((band.mask(hsv)[inside] > 0).mean()) if inside.any() else 0.0

    def score(self, frame: NDArray[np.uint8]) -> float:
        hsv, size = small_hsv(frame)
        return self._fraction(hsv, size, self.band)

    def is_main_camera(self, frame: NDArray[np.uint8]) -> bool:
        return self.score(frame) >= self.min_fraction

    def learn(self, samples: list[tuple[NDArray[Any], tuple[int, int]]]) -> MatBand | None:
        """Pick the mat colour family that fills the calibrated court in most keyframes (most
        broadcast keyframes show the main camera). Keeps the current band if none qualifies."""
        if not samples:
            return None
        med = {b: float(np.median([self._fraction(h, sz, b) for h, sz in samples])) for b in MAT_BANDS}
        best = max(med, key=lambda b: med[b])
        if med[best] < self.min_fraction:
            return None
        # narrow the family to the mat's own hue (±HUE_TOL, wrapping through red): a family is
        # broad enough that e.g. a red close-up would pass a purple-mat gate
        hist = np.zeros(180)
        for h, sz in samples:
            px = h[self._inside(sz) & (best.mask(h) > 0)]
            hist += np.bincount(px[:, 0], minlength=180)[:180]
        peak = int(np.argmax(hist))  # mode of the mat's hue
        lo, hi = peak - HUE_TOL, peak + HUE_TOL
        if lo < 0:
            hues: tuple[tuple[int, int], ...] = ((0, hi), (180 + lo, 179))
        elif hi > 179:
            hues = ((lo, 179), (0, hi - 180))
        else:
            hues = ((lo, hi),)
        self.band = MatBand(f"{best.name}@{peak}", hues, best.s_min, best.v_min)
        return self.band


def _sort_corners(pts: NDArray[np.float64]) -> NDArray[np.float64]:
    """Order 4 points as far-left, far-right, near-right, near-left (TL, TR, BR, BL)."""
    pts = pts[np.argsort(pts[:, 1])]
    top, bottom = pts[:2], pts[2:]
    tl, tr = top[np.argsort(top[:, 0])]
    bl, br = bottom[np.argsort(bottom[:, 0])]
    return np.array([tl, tr, br, bl])


def propose_corners(
    frame: NDArray[np.uint8], bands: tuple[MatBand, ...] = MAT_BANDS
) -> tuple[dict[str, tuple[float, float]], float] | None:
    """Propose the 4 outer court corners from the court-coloured region; returns (points, score).
    Every mat colour family is tried; the best-scoring plausible court wins."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    best = None
    for band in bands:
        prop = _propose_from_mask(band.mask(hsv), frame.shape[:2])
        if prop is not None and (best is None or prop[1] > best[1]):
            best = prop
    return best


def _propose_from_mask(
    mask: NDArray[Any], shape: tuple[int, ...]
) -> tuple[dict[str, tuple[float, float]], float] | None:
    k = max(5, shape[0] // 150)
    kernel = np.ones((k, k), np.uint8)
    mask = cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel), cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    cnt = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(cnt)
    frac = area / (shape[0] * shape[1])
    if frac < MIN_COURT_FRAC:
        return None
    quad = None
    for eps_frac in (0.02, 0.03, 0.015, 0.04, 0.01):
        approx = cv2.approxPolyDP(cnt, eps_frac * cv2.arcLength(cnt, True), True).reshape(-1, 2).astype(float)
        if len(approx) == 4:
            quad = _sort_corners(approx)
            break
    if quad is None:
        hull = cv2.convexHull(cnt).reshape(-1, 2).astype(float)
        s, d = hull.sum(axis=1), np.diff(hull, axis=1).ravel()
        quad = np.array([hull[np.argmin(s)], hull[np.argmin(d)], hull[np.argmax(s)], hull[np.argmax(d)]])
    # a region that runs off the frame has the *image* corners, not the court's: close-ups, intro
    # cards and blank frames would otherwise become a confident (and wrong) automatic calibration
    h, w = shape[:2]
    margin = max(2.0, 0.01 * min(h, w))
    on_edge = sum(x <= margin or y <= margin or x >= w - 1 - margin or y >= h - 1 - margin for x, y in quad)
    if on_edge >= 2 or frac > MAX_COURT_FRAC:
        return None
    names = ("far_left", "far_right", "near_right", "near_left")
    pts = {n: (float(x), float(y)) for n, (x, y) in zip(names, quad, strict=True)}
    # score: how rectangular-in-perspective is it (parallel near/far edges, convex)
    convex = cv2.isContourConvex(quad.astype(np.float32).reshape(-1, 1, 2))
    score = min(1.0, frac / 0.35) * (1.0 if convex else 0.5)
    return pts, float(score)
