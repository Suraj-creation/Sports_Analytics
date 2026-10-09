"""Scene structure: camera cuts, court presence (main-camera gate) and court auto-proposal.

* :class:`CutDetector` — HSV-histogram correlation between consecutive downscaled frames; a
  sharp drop marks a camera cut.  Runs on every decoded frame at negligible cost (it reuses the
  frames already decoded for the models — no second decode pass).
* :class:`CourtPresence` — fraction of court-coloured pixels inside the calibrated court polygon
  (legacy ``court_presence.py`` idea).  Replays, close-ups and crowd shots fail the gate, so their
  frames are marked ``replay`` and perception events are suppressed there.
* :func:`propose_corners` — port of the legacy green-mat contour heuristic; used only as a
  *proposal* that the user confirms/adjusts in the calibration UI (no pretrained badminton court
  keypoint model exists; a trained one is planned — report T4).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np
from numpy.typing import NDArray

HSV_LOWER_COURT = np.array([30, 35, 35])
HSV_UPPER_COURT = np.array([90, 255, 255])
MIN_COURT_FRAC = 0.08
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
    _mask: NDArray[np.uint8] | None = field(default=None, repr=False)

    def score(self, frame: NDArray[np.uint8]) -> float:
        small = cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA)
        sx, sy = 320 / frame.shape[1], 180 / frame.shape[0]
        if self._mask is None:
            m = np.zeros((180, 320), np.uint8)
            cv2.fillPoly(m, [(self.polygon * [sx, sy]).astype(np.int32)], 255)
            self._mask = m
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        court = cv2.inRange(hsv, HSV_LOWER_COURT, HSV_UPPER_COURT)
        inside = self._mask > 0
        return float((court[inside] > 0).mean()) if inside.any() else 0.0

    def is_main_camera(self, frame: NDArray[np.uint8]) -> bool:
        return self.score(frame) >= self.min_fraction


def _sort_corners(pts: NDArray[np.float64]) -> NDArray[np.float64]:
    """Order 4 points as far-left, far-right, near-right, near-left (TL, TR, BR, BL)."""
    pts = pts[np.argsort(pts[:, 1])]
    top, bottom = pts[:2], pts[2:]
    tl, tr = top[np.argsort(top[:, 0])]
    bl, br = bottom[np.argsort(bottom[:, 0])]
    return np.array([tl, tr, br, bl])


def propose_corners(frame: NDArray[np.uint8]) -> tuple[dict[str, tuple[float, float]], float] | None:
    """Propose the 4 outer court corners from the court-coloured region; returns (points, score)."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, HSV_LOWER_COURT, HSV_UPPER_COURT)
    k = max(5, frame.shape[0] // 150)
    kernel = np.ones((k, k), np.uint8)
    mask = cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel), cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    cnt = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(cnt)
    frac = area / (frame.shape[0] * frame.shape[1])
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
    h, w = frame.shape[:2]
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
