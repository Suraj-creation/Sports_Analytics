"""Shuttle trajectory post-processing (vectorised port of legacy ``filter_trajectory.py`` and
``fill_gaps.py``).

Inputs are dense per-frame arrays over a contiguous frame window (one entry per frame):
``x, y`` (px, NaN when not detected), ``vis`` (bool), ``conf`` (0–1).  All functions are pure and
return new arrays; ``interp`` marks frames whose position was synthesised by gap filling (used to
lower confidence and to exclude them from contact detection).

Look-ahead: gap filling needs the anchor after the gap, so the temporal engine runs these stages
on a window that extends ``MAX_GAP + ANCHOR`` frames beyond the frames it finalises.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import CubicSpline

F = NDArray[np.float64]
B = NDArray[np.bool_]

SPIKE_BACK = 300.0  # px/frame — impossible single-frame jump
SPIKE_BOTH = 130.0  # px/frame — isolated outlier (both neighbours far)
MAX_GAP = 25  # frames — occlusion gap that may be filled
MAX_FILL_SPEED = 120.0  # px/frame — implied speed gate
ANCHOR = 5  # frames of context on each side of a gap


@dataclass
class Track:
    x: F
    y: F
    vis: B
    conf: F
    interp: B

    @classmethod
    def from_arrays(cls, x: F, y: F, vis: B, conf: F | None = None) -> Track:
        x = np.asarray(x, np.float64).copy()
        y = np.asarray(y, np.float64).copy()
        vis = np.asarray(vis, bool) & np.isfinite(x) & np.isfinite(y)
        x[~vis] = np.nan
        y[~vis] = np.nan
        c = np.zeros_like(x) if conf is None else np.asarray(conf, np.float64).copy()
        c[~vis] = 0.0
        return cls(x=x, y=y, vis=vis, conf=c, interp=np.zeros_like(vis))

    def __len__(self) -> int:
        return len(self.x)


def remove_spikes(t: Track, back: float = SPIKE_BACK, both: float = SPIKE_BOTH) -> Track:
    """Drop single-frame outliers: a point whose step from the previous visible point exceeds
    ``back`` px/frame, or whose distances to *both* adjacent visible points exceed ``both``.
    Only adjacent frames (dt == 1) are judged, as in the legacy filter."""
    x, y, vis = t.x.copy(), t.y.copy(), t.vis.copy()
    n = len(x)
    if n < 3:
        return t
    idx = np.flatnonzero(vis)
    drop = np.zeros(n, bool)
    for k, i in enumerate(idx):
        prev_i = idx[k - 1] if k > 0 else -1
        next_i = idx[k + 1] if k + 1 < len(idx) else -1
        d_prev = np.hypot(x[i] - x[prev_i], y[i] - y[prev_i]) if prev_i >= 0 and i - prev_i == 1 else None
        d_next = np.hypot(x[i] - x[next_i], y[i] - y[next_i]) if next_i >= 0 and next_i - i == 1 else None
        impossible_jump = d_prev is not None and d_prev > back and (d_next is None or d_next > both)
        isolated = d_prev is not None and d_next is not None and d_prev > both and d_next > both
        if impossible_jump or isolated:
            drop[i] = True
    vis &= ~drop
    x[drop] = np.nan
    y[drop] = np.nan
    conf = t.conf.copy()
    conf[drop] = 0.0
    return Track(x=x, y=y, vis=vis, conf=conf, interp=t.interp.copy())


def _gaps(vis: B) -> list[tuple[int, int]]:
    """Inclusive (start, end) index ranges of interior invisible runs."""
    out: list[tuple[int, int]] = []
    n = len(vis)
    i = 0
    while i < n:
        if not vis[i]:
            j = i
            while j + 1 < n and not vis[j + 1]:
                j += 1
            if i > 0 and j < n - 1:
                out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def fill_gaps(
    t: Track,
    max_gap: int = MAX_GAP,
    max_speed: float = MAX_FILL_SPEED,
    anchor: int = ANCHOR,
    min_anchor_pts: int = 2,
    filled_conf: float = 0.35,
) -> Track:
    """Fill short occlusion gaps with a cubic spline (or linear with too few anchors).

    Gates (all must pass): gap length ≤ ``max_gap``; at least ``min_anchor_pts`` visible points in
    the ``anchor`` frames on each side; the implied speed across the gap ≤ ``max_speed`` px/frame;
    and the anchors themselves are moving (a stationary shuttle on the floor is not bridged).
    """
    x, y, vis, conf, interp = t.x.copy(), t.y.copy(), t.vis.copy(), t.conf.copy(), t.interp.copy()
    for s, e in _gaps(t.vis):
        length = e - s + 1
        if length > max_gap:
            continue
        before = [i for i in range(max(0, s - anchor), s) if t.vis[i]]
        after = [i for i in range(e + 1, min(len(x), e + 1 + anchor)) if t.vis[i]]
        if len(before) < min_anchor_pts or len(after) < min_anchor_pts:
            continue
        b, a = before[-1], after[0]
        span = a - b
        if np.hypot(x[a] - x[b], y[a] - y[b]) / span > max_speed:
            continue
        move_b = np.hypot(x[before[-1]] - x[before[0]], y[before[-1]] - y[before[0]]) / max(1, before[-1] - before[0])
        move_a = np.hypot(x[after[-1]] - x[after[0]], y[after[-1]] - y[after[0]]) / max(1, after[-1] - after[0])
        if move_b < 1.0 and move_a < 1.0:
            continue
        ks = np.array(before + after, dtype=np.float64)
        targets = np.arange(s, e + 1, dtype=np.float64)
        if len(ks) >= 4:
            fx = CubicSpline(ks, t.x[before + after], bc_type="natural")(targets)
            fy = CubicSpline(ks, t.y[before + after], bc_type="natural")(targets)
        else:
            fx = np.interp(targets, ks, t.x[before + after])
            fy = np.interp(targets, ks, t.y[before + after])
        x[s : e + 1] = fx
        y[s : e + 1] = fy
        vis[s : e + 1] = True
        interp[s : e + 1] = True
        conf[s : e + 1] = filled_conf
    return Track(x=x, y=y, vis=vis, conf=conf, interp=interp)


def velocity(t: Track, fps: float, win: int = 2) -> tuple[F, F, F]:
    """Central-difference velocity (px/s) over ±``win`` frames; NaN where not computable."""
    n = len(t)
    vx = np.full(n, np.nan)
    vy = np.full(n, np.nan)
    for i in range(n):
        lo, hi = max(0, i - win), min(n - 1, i + win)
        if hi - lo < 1 or not (t.vis[lo] and t.vis[hi]):
            continue
        dt = (hi - lo) / fps
        vx[i] = (t.x[hi] - t.x[lo]) / dt
        vy[i] = (t.y[hi] - t.y[lo]) / dt
    return vx, vy, np.hypot(vx, vy)


def process(t: Track) -> Track:
    """Default chain used by the engine: spike removal → gap filling."""
    return fill_gaps(remove_spikes(t))
