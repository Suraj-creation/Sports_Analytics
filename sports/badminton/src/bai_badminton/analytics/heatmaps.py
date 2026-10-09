"""Court-coordinate heatmaps, updated incrementally from the canonical stream.

Kinds (per player):
* ``presence``  — where the player spends time (feet positions while in play),
* ``origin``    — where the player hits from (feet at their contacts),
* ``landing``   — where the player's shots land (next contact point / rally-end landing),
* ``movement``  — path segments between contacts (distance-weighted presence),
* ``targeting`` — where the *opponent* is made to play from (receiver position after a shot).

Grids cover the doubles court plus a 1 m margin at 0.25 m resolution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from bai_badminton.court import HALF_LEN, WIDTH_DOUBLES

CELL = 0.25
MARGIN = 1.0
X0, X1 = -WIDTH_DOUBLES / 2 - MARGIN, WIDTH_DOUBLES / 2 + MARGIN
Y0, Y1 = -HALF_LEN - MARGIN, HALF_LEN + MARGIN
NX = int(round((X1 - X0) / CELL))
NY = int(round((Y1 - Y0) / CELL))
KINDS = ("presence", "origin", "landing", "movement", "targeting")


def _cell(x: float, y: float) -> tuple[int, int] | None:
    if not (np.isfinite(x) and np.isfinite(y)):
        return None
    i = int((x - X0) / CELL)
    j = int((y - Y0) / CELL)
    if 0 <= i < NX and 0 <= j < NY:
        return i, j
    return None


@dataclass
class HeatmapSet:
    grids: dict[tuple[str, str], NDArray[np.float32]] = field(default_factory=dict)
    version: int = 0

    def _grid(self, player: str, kind: str) -> NDArray[np.float32]:
        key = (player, kind)
        if key not in self.grids:
            self.grids[key] = np.zeros((NY, NX), np.float32)
        return self.grids[key]

    def add(self, player: str, kind: str, x: float, y: float, w: float = 1.0) -> None:
        if kind not in KINDS:
            raise ValueError(kind)
        c = _cell(x, y)
        if c is None:
            return
        self._grid(player, kind)[c[1], c[0]] += w
        self.version += 1

    def add_many(self, player: str, kind: str, xy: NDArray[np.floating], w: float = 1.0) -> None:
        for x, y in np.asarray(xy, dtype=np.float64).reshape(-1, 2):
            self.add(player, kind, float(x), float(y), w)

    def add_path(self, player: str, xy: NDArray[np.floating]) -> float:
        """Add a movement path; returns its length in metres (NaN points skipped)."""
        pts = np.asarray(xy, dtype=np.float64).reshape(-1, 2)
        pts = pts[np.isfinite(pts).all(axis=1)]
        if len(pts) < 2:
            return 0.0
        seg = np.hypot(*np.diff(pts, axis=0).T)
        seg[seg > 1.5] = 0.0  # identity glitches / teleports are not movement
        for (x, y), d in zip(pts[1:], seg, strict=True):
            if d > 0:
                self.add(player, "movement", float(x), float(y), float(d))
        return float(seg.sum())

    def to_public(self, player: str, kind: str, normalize: bool = True) -> dict[str, object]:
        g = self.grids.get((player, kind))
        data = np.zeros((NY, NX), np.float32) if g is None else g.copy()
        total = float(data.sum())
        if normalize and total > 0:
            data /= data.max()
        return {
            "player": player,
            "kind": kind,
            "cell_m": CELL,
            "origin_m": [X0, Y0],
            "shape": [NY, NX],
            "total": total,
            "values": np.round(data, 4).tolist(),
            "version": self.version,
        }
