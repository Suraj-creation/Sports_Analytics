"""Racket–shuttle contact (hit) detection — deterministic multi-cue fusion (``contact_fusion_v0``).

No pretrained badminton hit detector exists (Report §5.5).  This baseline fuses four cues and
records every component score as evidence so the fusion can be calibrated (and later replaced
by the trained causal model T1) without changing the event contract:

* **redirect** — direction change of the smoothed shuttle velocity at the frame;
* **impulse** — speed increase after the frame (a hit adds energy; smashes most);
* **proximity** — distance from the shuttle to the nearest wrist (or upper bbox) of a player,
  normalised by that player's body height;
* **swing** — wrist speed peak of that player around the frame.

Post-processing: temporal non-maximum suppression and the singles alternation constraint
(consecutive contacts must be by different players).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray

from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.keypoints import KP

CONTACT_MODEL = "contact_fusion_v0"

# fusion weights (logistic); calibrated on FineBadminton hit frames in research/train/contact
W_BIAS = -4.2
W_REDIRECT = 3.2
W_IMPULSE = 1.4
W_PROX = 3.4
W_SWING = 1.1
P_MIN = 0.35
# Conservative ambiguity policy on the *relative difference of heuristic proximity scores*.
# This threshold is not a calibrated probability or evidence of contact accuracy.
ATTRIBUTION_POLICY = "relative_proximity_gap_v1"
ATTRIBUTION_PROXIMITY_GAP = 0.05
# Minimum proximity support is a conservative heuristic, not calibrated identity confidence.
ATTRIBUTION_MIN_PROXIMITY = 0.05


@dataclass
class ContactCandidate:
    frame: int
    player_id: str | None
    p: float
    scores: dict[str, float] = field(default_factory=dict)
    shuttle_xy: tuple[float, float] | None = None
    attribution_reason: str | None = None

    @property
    def components(self) -> dict[str, float]:
        return {k: round(v, 4) for k, v in self.scores.items()}


def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def _seg_velocity(
    x: NDArray[np.float64], y: NDArray[np.float64], ok: NDArray[np.bool_], lo: int, hi: int
) -> tuple[float, float] | None:
    """Mean velocity (px/frame) over visible points in [lo, hi] via least squares."""
    idx = np.arange(max(lo, 0), min(hi, len(x) - 1) + 1)
    idx = idx[ok[idx]]
    if len(idx) < 2:
        return None
    t = idx.astype(np.float64)
    tc = t - t.mean()
    den = float((tc**2).sum())
    if den == 0:
        return None
    return float((tc * (x[idx] - x[idx].mean())).sum() / den), float((tc * (y[idx] - y[idx].mean())).sum() / den)


def _player_point(s: PlayerSeries, i: int) -> list[NDArray[np.float64]]:
    """Candidate racket-hand points for player at frame i: wrists if posed, else upper box."""
    pts: list[NDArray[np.float64]] = []
    k = s.kps[i]
    for kp in (KP.L_WRIST, KP.R_WRIST):
        if np.isfinite(k[kp]).all() and k[kp, 2] >= 0.3:
            pts.append(k[kp, :2])
    if not pts and np.isfinite(s.bbox[i]).all():
        x1, y1, x2, y2 = s.bbox[i]
        # the racket head is typically above/beside the head at contact
        pts.append(np.array([(x1 + x2) / 2, y1 + 0.15 * (y2 - y1)]))
    return pts


def _wrist_speed(
    s: PlayerSeries, i: int, win: int = 3, *, frame0: int = 0,
    pose_stride: NDArray[np.int64] | None = None,
) -> float | None:
    """Observed wrist motion in body heights/frame, respecting pose scheduling.

    Sparse pairs can bridge only known unscheduled frames with continuous boxes.
    Missing scheduled observations and unknown/disabled cadence cannot bridge.
    """
    n = s.kps.shape[0]
    lo, hi = max(0, i - win - 1), min(n, i + win + 1)
    best = None
    for kp in (KP.L_WRIST, KP.R_WRIST):
        points = s.kps[lo:hi, kp]
        valid = np.isfinite(points).all(axis=1) & (points[:, 2] >= 0.3)
        observed = np.flatnonzero(valid) + lo
        for left, right in pairwise(observed):
            delta = int(right - left)
            if not np.isfinite(s.bbox[left : right + 1]).all():
                continue
            if pose_stride is None:
                if delta != 1:
                    continue
            else:
                cadence = pose_stride[left : right + 1]
                if (cadence == 0).any():
                    continue
                ends = np.array([left, right])
                end_cadence = pose_stride[ends]
                known = end_cadence > 0
                if ((ends[known] + frame0) % end_cadence[known] != 0).any():
                    continue
                if delta > 1:
                    if (cadence <= 0).any():
                        continue
                    intermediate = np.arange(left + 1, right) + frame0
                    if (intermediate % cadence[1:-1] == 0).any():
                        continue
            height = s.height[right]
            if not np.isfinite(height) or height <= 1:
                continue
            speed = float(np.linalg.norm(s.kps[right, kp, :2] - s.kps[left, kp, :2])) / delta / height
            best = speed if best is None else max(best, speed)
    return best


def score_frame(w: WindowObs, i: int, half: int = 3) -> ContactCandidate | None:
    t = w.shuttle
    ok = t.vis & ~t.interp
    if not ok[i]:
        return None
    vb = _seg_velocity(t.x, t.y, ok, i - half, i)
    va = _seg_velocity(t.x, t.y, ok, i, i + half)
    if vb is None or va is None:
        return None
    nb, na = math.hypot(*vb), math.hypot(*va)
    if nb < 0.5 and na < 0.5:
        return None
    cos = (vb[0] * va[0] + vb[1] * va[1]) / max(nb * na, 1e-9)
    angle = math.degrees(math.acos(max(-1.0, min(1.0, cos))))
    s_redirect = float(np.clip((angle - 25.0) / 70.0, 0.0, 1.0))
    ratio = na / max(nb, 1e-6)
    s_impulse = float(np.clip((ratio - 1.2) / 1.6, 0.0, 1.0))

    sx, sy = t.x[i], t.y[i]
    # Rank players, not their wrists: two wrists of one person are not competitors.
    ranked: list[tuple[str, float, float]] = []
    for pid, player in w.players.items():
        h = player.height[i]
        if not np.isfinite(h) or h <= 1:
            continue
        proximities = []
        for point in _player_point(player, i):
            distance = float(np.hypot(sx - point[0], sy - point[1])) / h
            if math.isfinite(distance):
                proximities.append(math.exp(-distance / 0.45))
        if proximities and max(proximities) > 0.0:
            ranked.append((pid, max(proximities), float(h)))
    # Python's stable sort preserves the prior best-candidate choice for exact ties,
    # keeping its swing cue for contact scoring while attribution abstains.
    ranked.sort(key=lambda item: item[1], reverse=True)
    best_pid, best_prox, best_h = ranked[0] if ranked else (None, 0.0, None)
    second_prox = ranked[1][1] if len(ranked) > 1 else 0.0
    gap = best_prox - second_prox
    relative_gap = gap / best_prox if best_prox > 0 else 0.0
    if not ranked:
        attributed_pid, attribution_reason = None, "no_player_observation"
    elif best_prox < ATTRIBUTION_MIN_PROXIMITY:
        attributed_pid, attribution_reason = None, "insufficient_proximity"
    elif len(ranked) > 1 and relative_gap <= ATTRIBUTION_PROXIMITY_GAP:
        attributed_pid, attribution_reason = None, "ambiguous_proximity"
    else:
        attributed_pid, attribution_reason = best_pid, "nearest_proximity"
    # On an attribution tie, aggregate swing over all near-tied candidates so
    # contact scoring does not depend on the order players entered the mapping.
    swing_players = [best_pid] if best_pid is not None and attribution_reason != "insufficient_proximity" else []
    if attribution_reason == "ambiguous_proximity":
        swing_players = [pid for pid, prox, _ in ranked if (best_prox - prox) / best_prox <= ATTRIBUTION_PROXIMITY_GAP]
    wrist_speeds = [
        _wrist_speed(w.players[pid], i, frame0=w.frame0, pose_stride=w.pose_stride) for pid in swing_players
    ]
    observed_speeds = [speed for speed in wrist_speeds if speed is not None]
    s_swing = float(np.clip((max(observed_speeds) - 0.05) / 0.25, 0.0, 1.0)) if observed_speeds else 0.0
    z = W_BIAS + W_REDIRECT * s_redirect + W_IMPULSE * s_impulse + W_PROX * best_prox + W_SWING * s_swing
    p = _sigmoid(z)
    return ContactCandidate(
        frame=w.frame0 + i,
        player_id=attributed_pid,
        p=p,
        scores={
            "redirect": s_redirect,
            "impulse": s_impulse,
            "proximity": best_prox,
            "proximity_runner_up": second_prox,
            "proximity_gap": gap,
            "proximity_relative_gap": relative_gap,
            "proximity_relative_gap_threshold": ATTRIBUTION_PROXIMITY_GAP,
            "proximity_minimum_threshold": ATTRIBUTION_MIN_PROXIMITY,
            "proximity_candidates": float(len(ranked)),
            "swing": s_swing,
            "angle_deg": angle,
            "speed_before": nb,
            "speed_after": na,
            "body_h": float(best_h) if best_h else 0.0,
        },
        shuttle_xy=(float(sx), float(sy)),
        attribution_reason=attribution_reason,
    )


def detect_contacts(
    w: WindowObs,
    *,
    p_min: float = P_MIN,
    nms_s: float = 0.2,
    min_same_player_gap_s: float = 0.9,
    start: int = 0,
    stop: int | None = None,
    enforce_alternation: bool = True,
) -> list[ContactCandidate]:
    """Detect contacts in window indices ``[start, stop)``; scoring may look ±3 frames around."""
    stop = w.n if stop is None else stop
    cands = [c for i in range(start, stop) if not w.replay[i] and (c := score_frame(w, i)) is not None and c.p >= p_min]
    # temporal NMS
    nms = max(1, int(round(nms_s * w.fps)))
    cands.sort(key=lambda c: -c.p)
    kept: list[ContactCandidate] = []
    for c in cands:
        if all(abs(c.frame - k.frame) > nms for k in kept):
            kept.append(c)
    kept.sort(key=lambda c: c.frame)
    if not enforce_alternation:
        return kept
    # singles alternation: the same player cannot hit twice in a row (within a short time)
    gap = int(round(min_same_player_gap_s * w.fps))
    out: list[ContactCandidate] = []
    for c in kept:
        if out and c.player_id is not None and c.player_id == out[-1].player_id and c.frame - out[-1].frame < gap:
            if c.p > out[-1].p:
                out[-1] = c
            continue
        out.append(c)
    return out
