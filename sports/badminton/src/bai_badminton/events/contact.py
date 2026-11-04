"""Estimated racket–shuttle hits — deterministic multi-cue fusion (``contact_fusion_v2``).

No trained racket-contact adapter is active in this runtime. This baseline fuses body/motion cues and
records every component score as evidence so the fusion can be calibrated (and later replaced
by the trained causal model T1) without changing the event contract:

* **redirect** — direction change of the smoothed shuttle velocity at the frame;
* **impulse** — speed increase after the frame (a hit adds energy; smashes most);
* **proximity** — distance from the shuttle to the nearest wrist (or upper bbox) of a player,
  normalised by that player's body height;
* **swing** — wrist speed peak of that player around the frame.
* **racket overlap** — optional actual ellipse/shaft observation from the current image.

Post-processing uses bounded temporal local maxima. Scores are uncalibrated
heuristic support, not probabilities of physical racket contact.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray

from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.keypoints import KP

CONTACT_MODEL = "contact_fusion_v2"
CONTACT_RELIABILITY_MODEL = "contact_motion_reliability_v1"

# Hand-set logistic fusion weights; no fitted calibration is supplied in this repository.
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
    model: str = CONTACT_MODEL

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


@dataclass(frozen=True)
class ContactMotionReliability:
    """Declared spatial sensitivity, not calibrated shuttle-error covariance.

    The caller supplies analysis-image pixels. An eight-frame TrackNet result
    resized from 512 to 1280 pixels has a 2.5-pixel cell; 2.5/sqrt(12) is one
    possible explicit sensitivity assumption, not a universal default.
    """

    spatial_sigma_px: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.spatial_sigma_px) or self.spatial_sigma_px <= 0:
            raise ValueError("spatial_sigma_px must be positive and finite")


def _velocity_reliability(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    ok: NDArray[np.bool_],
    lo: int,
    hi: int,
    spatial_sigma_px: float,
) -> tuple[float, int, int] | None:
    """Slope sensitivity from same-context observed samples and LS residuals."""
    idx = np.arange(max(lo, 0), min(hi, len(x) - 1) + 1)
    idx = idx[ok[idx] & np.isfinite(x[idx]) & np.isfinite(y[idx])]
    if len(idx) < 2:
        return None
    tc = idx.astype(np.float64) - idx.mean()
    denominator = float((tc**2).sum())
    values = np.column_stack((x[idx], y[idx]))
    velocity = np.sum(tc[:, None] * (values - values.mean(axis=0)), axis=0) / denominator
    residual = values - (values.mean(axis=0) + tc[:, None] * velocity)
    variance = float(np.sum(residual**2)) / max(1, 2 * (len(idx) - 2))
    return math.sqrt((spatial_sigma_px**2 + variance) / denominator), len(idx), int(idx[-1] - idx[0])


def _player_point(s: PlayerSeries, i: int) -> list[NDArray[np.float64]]:
    """Candidate racket-hand points for player at frame i: wrists if posed, else upper box."""
    pts: list[NDArray[np.float64]] = []
    if i < len(s.racket) and (racket := s.racket[i]) is not None:
        return [np.asarray(racket.center)]
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
    s: PlayerSeries,
    i: int,
    win: int = 3,
    *,
    frame0: int = 0,
    pose_stride: NDArray[np.int64] | None = None,
    context_bounds: tuple[int, int] | None = None,
) -> float | None:
    """Observed wrist motion in body heights/frame, respecting pose scheduling.

    Sparse pairs can bridge only known unscheduled frames with continuous boxes.
    Missing scheduled observations and unknown/disabled cadence cannot bridge.
    ``context_bounds`` restricts pose evidence to a half-open scene interval.
    """
    n = s.kps.shape[0]
    lo, hi = max(0, i - win - 1), min(n, i + win + 1)
    if context_bounds is not None:
        lo, hi = max(lo, context_bounds[0]), min(hi, context_bounds[1])
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


def _context_bounds(w: WindowObs, i: int, half: int) -> tuple[int, int]:
    """Bound the small velocity/pose neighborhood to the candidate's scene."""
    segment_lo, segment_hi = w.segment_bounds(i)
    # Wrist motion also looks one frame further back than shuttle velocity.
    return max(segment_lo, i - max(half, 4)), min(segment_hi, i + max(half, 3) + 1)


def score_frame(
    w: WindowObs, i: int, half: int = 3, *, motion_reliability: ContactMotionReliability | None = None
) -> ContactCandidate | None:
    t = w.shuttle
    ok = t.vis & ~t.interp
    if w.replay[i] or not ok[i]:
        return None
    lo, hi = _context_bounds(w, i, half)
    vb = _seg_velocity(t.x, t.y, ok, max(lo, i - half), i)
    va = _seg_velocity(t.x, t.y, ok, i, min(hi - 1, i + half))
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

    motion_scores: dict[str, float] = {}
    if motion_reliability is not None:
        before = _velocity_reliability(t.x, t.y, ok, max(lo, i - half), i, motion_reliability.spatial_sigma_px)
        after = _velocity_reliability(t.x, t.y, ok, i, min(hi - 1, i + half), motion_reliability.spatial_sigma_px)
        if before is None or after is None:
            return None
        sigma_before, count_before, span_before = before
        sigma_after, count_after, span_after = after
        qb = max(0.0, 1.0 - 3.0 * sigma_before / nb) if nb else 0.0
        qa = max(0.0, 1.0 - 3.0 * sigma_after / na) if na else 0.0
        margin = 3.0 * math.hypot(sigma_before, sigma_after)
        motion_scores = {
            "legacy_redirect": s_redirect,
            "legacy_impulse": s_impulse,
            "incoming_direction_reliability": qb,
            "outgoing_direction_reliability": qa,
            "incoming_slope_sigma_sensitivity": sigma_before,
            "outgoing_slope_sigma_sensitivity": sigma_after,
            "incoming_fit_samples": float(count_before),
            "outgoing_fit_samples": float(count_after),
            "incoming_fit_span_frames": float(span_before),
            "outgoing_fit_span_frames": float(span_after),
            "spatial_sigma_sensitivity_px": motion_reliability.spatial_sigma_px,
            "absolute_speed_gain_px_per_frame": na - nb,
            "speed_gain_sensitivity_margin": margin,
        }
        s_redirect *= min(qb, qa)
        s_impulse = max(0.0, (na - nb - margin) / (na + nb + margin))

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
    equipment = {
        pid: player.racket[i].overlap((float(sx), float(sy)))
        for pid, player in w.players.items()
        if i < len(player.racket) and player.racket[i] is not None
    }
    # An observed racket overlap is more specific than a second person's wrist
    # or body box. Multiple overlapping rackets still require attribution abstention.
    overlapping_rackets = {pid for pid, overlap in equipment.items() if overlap >= 0.5}
    if overlapping_rackets:
        ranked = [row for row in ranked if row[0] in overlapping_rackets]
    best_pid, best_prox, best_h = ranked[0] if ranked else (None, 0.0, None)
    second_prox = ranked[1][1] if len(ranked) > 1 else 0.0
    gap = best_prox - second_prox
    relative_gap = gap / best_prox if best_prox > 0 else 0.0
    if len(overlapping_rackets) > 1:
        attributed_pid, attribution_reason = None, "ambiguous_racket_overlap"
    elif not ranked:
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
    elif attribution_reason == "ambiguous_racket_overlap":
        swing_players = list(overlapping_rackets)
    wrist_speeds = [
        _wrist_speed(w.players[pid], i, frame0=w.frame0, pose_stride=w.pose_stride, context_bounds=(lo, hi))
        for pid in swing_players
    ]
    observed_speeds = [speed for speed in wrist_speeds if speed is not None]
    s_swing = float(np.clip((max(observed_speeds) - 0.05) / 0.25, 0.0, 1.0)) if observed_speeds else 0.0
    racket_overlap = max((equipment.get(pid, 0.0) for pid in swing_players), default=0.0)
    z = (
        W_BIAS
        + W_REDIRECT * s_redirect
        + W_IMPULSE * s_impulse
        + W_PROX * best_prox
        + W_SWING * s_swing
        + 1.4 * racket_overlap
    )
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
            "racket_observed": float(any(pid in equipment for pid in swing_players)),
            "racket_overlap": racket_overlap,
            "angle_deg": angle,
            "speed_before": nb,
            "speed_after": na,
            "body_h": float(best_h) if best_h else 0.0,
            **motion_scores,
        },
        shuttle_xy=(float(sx), float(sy)),
        attribution_reason=attribution_reason,
        model=CONTACT_RELIABILITY_MODEL if motion_reliability is not None else CONTACT_MODEL,
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
    proximity_split: float | None = None,
    motion_reliability: ContactMotionReliability | None = None,
) -> list[ContactCandidate]:
    """Return local score peaks in ``[start, stop)`` using observations outside it.

    Peak selection needs ``round(nms_s * fps) + 4`` frames of context on either
    side. Restricting the candidates to the output range before suppression
    emitted the same turn twice at processing-chunk boundaries. A bounded
    local maximum (earliest frame wins ties) has identical selection for every
    output partition with the same contextual observations. Unlike greedy NMS,
    its decision cannot depend on an arbitrarily long chain of distant peaks.

    Optional singles alternation is a causal heuristic over returned peaks;
    streaming callers must maintain that state across calls themselves.
    Peak suppression and alternation never compare candidates across a scene
    boundary supplied in ``w.break_before`` or inferred from replay changes.

    With ``proximity_split``, body-supported hits and trajectory-only diagnostic
    turns form separate groups BEFORE peak selection. A stronger unsupported
    turn cannot suppress a supported hit and then be discarded by the caller.
    Peaks from both groups are returned for separate contact/diagnostic handling.
    """
    stop = w.n if stop is None else stop
    nms = max(1, int(round(nms_s * w.fps)))
    assert w.break_before is not None
    segments = np.cumsum(w.break_before, dtype=np.int64)

    def score(i: int) -> ContactCandidate | None:
        if motion_reliability is None:
            return score_frame(w, i)
        return score_frame(w, i, motion_reliability=motion_reliability)

    cands = [
        c
        for i in range(max(0, start - nms), min(w.n, stop + nms))
        if not w.replay[i] and (c := score(i)) is not None and c.p >= p_min
    ]
    kept = [
        c
        for c in cands
        if start <= c.frame - w.frame0 < stop
        and not any(
            abs(c.frame - other.frame) <= nms
            and segments[c.frame - w.frame0] == segments[other.frame - w.frame0]
            and (
                proximity_split is None
                or (c.scores.get("proximity", 0.0) >= proximity_split)
                == (other.scores.get("proximity", 0.0) >= proximity_split)
            )
            and (other.p > c.p or (other.p == c.p and other.frame < c.frame))
            for other in cands
        )
    ]
    if not enforce_alternation:
        return kept
    # singles alternation: the same player cannot hit twice in a row (within a short time)
    gap = int(round(min_same_player_gap_s * w.fps))
    out: list[ContactCandidate] = []
    for c in kept:
        if (
            out
            and segments[c.frame - w.frame0] == segments[out[-1].frame - w.frame0]
            and c.player_id is not None
            and c.player_id == out[-1].player_id
            and c.frame - out[-1].frame < gap
        ):
            continue
        out.append(c)
    return out
