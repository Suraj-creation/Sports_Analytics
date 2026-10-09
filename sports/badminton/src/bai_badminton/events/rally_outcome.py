"""Rally outcome: how a rally ended and which side was at fault.

Port of the validated core of the legacy ``win_predictor/rule_engine.py::analyze_rally_end``
(85.7 % win-reason accuracy on 399 rallies, legacy docs/10).  The decision cascade (CHECK 0–7)
and thresholds are preserved; inputs are generalised from pandas frames and a manually annotated
``court.json`` to numpy trajectories and a :class:`CourtImageGeometry` derived from the session's
homography.

Semantics: ``fault`` is the side (``near``/``far``) of the player who lost the rally.
``out`` → that player hit it out; ``net`` → that player hit the net; ``winner`` → the shuttle
landed in that player's half (they failed to return it).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum

import cv2
import numpy as np
from numpy.typing import NDArray

from bai_badminton.court import HALF_LEN, WIDTH_DOUBLES, Homography

RELIABLE_SPD_MIN = 40.0  # px/s
HIGH_SPEED = 600.0  # px/s
ANALYSIS_SEC = 3.0


class Outcome(StrEnum):
    OUT = "out"
    NET = "net"
    WINNER = "winner"  # landed in (opponent failed to return)
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CourtImageGeometry:
    """Image-space court description used by the outcome cascade (analysis-proxy pixels)."""

    corners: NDArray[np.float32]  # (4,2) doubles outer corners: far-left, far-right, near-right, near-left
    net_ground_y: float  # image y of the net's floor line (at court centre)
    net_top_y: float  # image y of the net cable (top), from calibration or approximation
    net_x_min: float
    net_x_max: float
    net_tol_px: float  # ≈ line width + tracking error, in px near the net

    @property
    def poly(self) -> NDArray[np.float32]:
        return self.corners.reshape(-1, 1, 2).astype(np.float32)

    @property
    def court_top_y(self) -> float:
        return float(min(self.corners[0, 1], self.corners[1, 1]))

    @property
    def court_bottom_y(self) -> float:
        return float(max(self.corners[2, 1], self.corners[3, 1]))

    def signed_dist(self, x: float, y: float) -> float:
        """>0 inside the court polygon, <0 outside (px)."""
        return float(cv2.pointPolygonTest(self.poly, (float(x), float(y)), True))

    @classmethod
    def from_homography(
        cls,
        h: Homography,
        net_top_left: tuple[float, float] | None = None,
        net_top_right: tuple[float, float] | None = None,
        tol_m: float = 0.15,
    ) -> CourtImageGeometry:
        hw = WIDTH_DOUBLES / 2
        corners = h.court_to_image(np.array([[-hw, HALF_LEN], [hw, HALF_LEN], [hw, -HALF_LEN], [-hw, -HALF_LEN]]))
        net = h.court_to_image(np.array([[-hw, 0.0], [hw, 0.0], [0.0, 0.0], [0.0, tol_m]]))
        net_ground_y = float(net[2, 1])
        if net_top_left is not None and net_top_right is not None:
            net_top_y = (net_top_left[1] + net_top_right[1]) / 2
        else:
            # Approximation used by the legacy auto-court mode: the cable projects close to the
            # far baseline in a behind-the-baseline broadcast view.
            net_top_y = float((corners[0, 1] + corners[1, 1]) / 2)
        tol_px = max(4.0, float(abs(net[3, 1] - net[2, 1])))
        return cls(
            corners=corners.astype(np.float32),
            net_ground_y=net_ground_y,
            net_top_y=float(net_top_y),
            net_x_min=float(min(net[0, 0], net[1, 0])),
            net_x_max=float(max(net[0, 0], net[1, 0])),
            net_tol_px=tol_px,
        )


@dataclass
class OutcomeResult:
    outcome: Outcome
    fault: str  # "near" | "far" | "unknown"
    confidence: str  # HIGH | MEDIUM | LOW
    check: str  # which cascade rule fired (provenance)
    features: dict[str, float | str | bool] = field(default_factory=dict)


def _velocities(pos: NDArray[np.float64], fps: float) -> list[dict[str, float]]:
    out = []
    for i in range(1, len(pos)):
        f0, x0, y0 = pos[i - 1]
        f1, x1, y1 = pos[i]
        dt = (f1 - f0) / fps
        if dt <= 0:
            continue
        vx, vy = (x1 - x0) / dt, (y1 - y0) / dt
        out.append({"vx": vx, "vy": vy, "speed": math.hypot(vx, vy), "x": x1, "y": y1})
    return out


def _smoothed_velocities(pos: NDArray[np.float64], fps: float, win: int = 3) -> list[tuple[float, float, int]]:
    out = []
    for i in range(win, len(pos)):
        f0, x0, y0 = pos[i - win]
        f1, x1, y1 = pos[i]
        dt = (f1 - f0) / fps
        out.append(((x1 - x0) / dt, (y1 - y0) / dt, i) if dt > 0 else (0.0, 0.0, i))
    return out


def last_hit_index(
    pos: NDArray[np.float64], fps: float, win: int = 3, angle_deg: float = 60, min_disp: float = 8
) -> int:
    """Index of the most recent sharp direction change (racket redirect) in ``pos``."""
    sv = _smoothed_velocities(pos, fps, win)
    last = 0
    for i in range(1, len(sv)):
        ax, ay, _ = sv[i - 1]
        bx, by, idx = sv[i]
        na, nb = math.hypot(ax, ay), math.hypot(bx, by)
        if na * (win / fps) < min_disp or nb * (win / fps) < min_disp:
            continue
        cos = max(-1.0, min(1.0, (ax * bx + ay * by) / (na * nb)))
        if math.degrees(math.acos(cos)) > angle_deg:
            last = idx
    return last


def _oob_fault(last_y: float, g: CourtImageGeometry) -> str:
    if last_y > g.court_bottom_y:
        return "far"  # past the near baseline → far player hit it
    if last_y < g.court_top_y:
        return "near"
    return "far" if last_y > g.net_ground_y else "near"


def _near_net_x(x: float, g: CourtImageGeometry) -> bool:
    return g.net_x_min - g.net_tol_px <= x <= g.net_x_max + g.net_tol_px


def _extrapolate_exit(
    lx: float, ly: float, vx: float, vy: float, g: CourtImageGeometry, fps: float, max_frames: int = 45
) -> tuple[bool, tuple[float, float] | None]:
    dt = 1.0 / fps
    for t in range(1, max_frames + 1):
        ex, ey = lx + vx * dt * t, ly + vy * dt * t
        if g.signed_dist(ex, ey) < -g.net_tol_px:
            return True, (ex, ey)
    return False, None


def analyze_rally_end(
    frames: NDArray[np.integer],
    xs: NDArray[np.floating],
    ys: NDArray[np.floating],
    visible: NDArray[np.bool_],
    end_frame: int,
    g: CourtImageGeometry,
    fps: float,
) -> OutcomeResult:
    """Decide the rally outcome from the last ``ANALYSIS_SEC`` of the shuttle track."""
    n_back = int(fps * ANALYSIS_SEC)
    sel = (frames >= end_frame - n_back) & (frames <= end_frame) & visible.astype(bool)
    if sel.sum() < 3:
        return OutcomeResult(Outcome.UNKNOWN, "unknown", "LOW", "insufficient_track")
    order = np.argsort(frames[sel])
    pos = np.stack([frames[sel][order], xs[sel][order], ys[sel][order]], axis=1).astype(np.float64)
    conf = "HIGH" if len(pos) >= 10 else "MEDIUM"
    vels = _velocities(pos, fps)
    if not vels:
        return OutcomeResult(Outcome.UNKNOWN, "unknown", "LOW", "no_velocity")

    last_x, last_y = float(pos[-1, 1]), float(pos[-1, 2])
    spd = [v["speed"] for v in vels]
    mid_all = max(1, len(spd) // 2)
    decel = (np.mean(spd[:mid_all]) - np.mean(spd[mid_all:])) / max(float(np.mean(spd[:mid_all])), 1.0)
    reliable = [v for v in vels if v["speed"] > RELIABLE_SPD_MIN] or vels
    early = reliable[: max(1, len(reliable) // 2)]
    pred_vx = float(np.mean([v["vx"] for v in early]))
    pred_vy = float(np.mean([v["vy"] for v in early]))
    last_few = reliable[-3:]
    fault_vy = float(np.mean([v["vy"] for v in last_few]))
    rel_x = float(next((v["x"] for v in reversed(vels) if v["speed"] > RELIABLE_SPD_MIN), last_x))
    rel_y = float(next((v["y"] for v in reversed(vels) if v["speed"] > RELIABLE_SPD_MIN), last_y))

    feats: dict[str, float | str | bool] = {
        "speed": float(np.mean([v["speed"] for v in early])),
        "vx": pred_vx,
        "vy": pred_vy,
        "last_x": last_x,
        "last_y": last_y,
        "decel_rate": float(decel),
    }
    lh_idx = last_hit_index(pos, fps)
    seg = pos[lh_idx:]
    feats["last_hit_side"] = "far" if len(seg) and seg[0, 2] < g.net_top_y else "near"

    # net-fault side from approach velocity towards the cable (fallback: landing side)
    net_mid = (g.net_top_y + g.net_ground_y) / 2
    net_fault = "near" if last_y < net_mid else "far"
    if len(seg) >= 3:
        d = np.abs(seg[:, 2] - g.net_top_y)
        i_nc = int(np.argmin(d))
        if i_nc > 0 and d[i_nc] < 80:
            vys = [
                (seg[j + 1, 2] - seg[j, 2]) / ((seg[j + 1, 0] - seg[j, 0]) / fps)
                for j in range(max(0, i_nc - 4), i_nc)
                if seg[j + 1, 0] > seg[j, 0]
            ]
            if vys and abs(float(np.mean(vys))) > 20:
                net_fault = "near" if float(np.mean(vys)) < 0 else "far"
    feats["net_fault"] = net_fault
    tol = g.net_tol_px

    # CHECK 0 — shuttle stationary (landed)
    static = [v for v in vels[-6:] if v["speed"] < 15]
    if len(static) >= 3:
        gx = float(np.mean([v["x"] for v in static]))
        gy = float(np.mean([v["y"] for v in static]))
        if g.signed_dist(gx, gy) < -tol or gy > g.court_bottom_y or gy < g.court_top_y:
            return OutcomeResult(Outcome.OUT, _oob_fault(gy, g), "HIGH", "c0_static_out", feats)
        if abs(gy - g.net_ground_y) < tol * 2 and _near_net_x(gx, g):
            return OutcomeResult(Outcome.NET, net_fault, "HIGH", "c0_static_net", feats)
        return OutcomeResult(Outcome.WINNER, "far" if gy < g.net_ground_y else "near", "HIGH", "c0_static_in", feats)

    # CHECK 1/2 — final flight segment after the last redirect
    if len(seg) >= 2:
        fv = _velocities(seg, fps)
        if fv:
            seg_speed = float(np.mean([v["speed"] for v in fv]))
            s_side = "far" if seg[0, 2] < g.net_top_y else "near"
            e_side = "far" if seg[-1, 2] < g.net_top_y else "near"
            if s_side != e_side:
                near_cable = int(np.sum(np.abs(seg[:, 2] - g.net_top_y) < tol * 3))
                lingered = near_cable >= max(8, len(seg) * 0.4)
                if (
                    lingered
                    and abs(seg[-1, 2] - g.net_ground_y) < tol * 2
                    and seg_speed < HIGH_SPEED
                    and _near_net_x(last_x, g)
                ):
                    return OutcomeResult(Outcome.NET, net_fault, conf, "c1_linger_net", feats)
                if g.signed_dist(last_x, last_y) >= -tol:
                    return OutcomeResult(Outcome.WINNER, e_side, conf, "c1_crossed_in", feats)
                return OutcomeResult(Outcome.OUT, _oob_fault(last_y, g), conf, "c1_crossed_out", feats)
            min_y = float(seg[:, 2].min())
            if min_y < g.net_top_y + tol:
                if min_y < g.net_top_y and g.signed_dist(last_x, last_y) < -tol:
                    return OutcomeResult(Outcome.OUT, _oob_fault(last_y, g), conf, "c2a_cable_bounce_out", feats)
                if abs(last_y - g.net_ground_y) < tol * 2.5 and _near_net_x(last_x, g):
                    i_top = int(np.argmin(seg[:, 2]))
                    fvx, fvy = [], []
                    for k in range(i_top, len(seg) - 1):
                        dt = (seg[k + 1, 0] - seg[k, 0]) / fps
                        if dt > 0:
                            fvx.append(abs((seg[k + 1, 1] - seg[k, 1]) / dt))
                            fvy.append((seg[k + 1, 2] - seg[k, 2]) / dt)
                    if fvy and float(np.mean(fvy)) / max(float(np.mean(fvx)) if fvx else 1.0, 1.0) > 2.0:
                        return OutcomeResult(Outcome.NET, net_fault, conf, "c2b_steep_fall_net", feats)
            if (
                abs(seg[-1, 2] - g.net_ground_y) < tol * 2.5
                and seg_speed < HIGH_SPEED
                and _near_net_x(last_x, g)
                and min_y < g.net_top_y + tol * 2
            ):
                return OutcomeResult(Outcome.NET, net_fault, conf, "c2c_died_at_net", feats)

    # CHECK 2b — clear baseline OOB
    if last_y > g.court_bottom_y:
        return OutcomeResult(Outcome.OUT, "far", conf, "c2b_past_near_baseline", feats)
    if last_y < g.court_top_y:
        return OutcomeResult(Outcome.OUT, "near", conf, "c2b_past_far_baseline", feats)

    # CHECK 3 — OOB via extrapolation (guarded against backward extrapolation)
    backward = pred_vy < 0 and last_y > g.net_top_y and g.signed_dist(rel_x, rel_y) >= -tol * 2
    if decel < 0.35 and not backward:
        hit, pt = _extrapolate_exit(rel_x, rel_y, pred_vx, pred_vy, g, fps)
        if hit:
            ex, ey = pt if pt else (rel_x, rel_y)
            if abs(ey - g.net_top_y) < tol * 3 and _near_net_x(ex, g):
                return OutcomeResult(Outcome.NET, net_fault, conf, "c3_extrap_net", feats)
            return OutcomeResult(Outcome.OUT, _oob_fault(ey, g), conf, "c3_extrap_out", feats)

    # CHECK 4 — baseline proximity
    if decel < 0.35:
        if fault_vy > 10 and last_y > g.court_bottom_y - 40:
            return OutcomeResult(Outcome.OUT, "far", conf, "c4_near_baseline", feats)
        if fault_vy < -10 and last_y < g.court_top_y + 40:
            return OutcomeResult(Outcome.OUT, "near", conf, "c4_far_baseline", feats)

    # CHECK 5 — above cable and inside court
    if last_y < g.net_top_y and g.signed_dist(last_x, last_y) > -30:
        return OutcomeResult(
            Outcome.WINNER, "far" if last_y < g.net_ground_y else "near", conf, "c5_in_above_cable", feats
        )

    # CHECK 6 — OOB fallback
    if not backward and g.signed_dist(rel_x, rel_y) < -tol:
        if abs(rel_y - g.net_top_y) < tol * 3 and _near_net_x(rel_x, g):
            return OutcomeResult(Outcome.NET, net_fault, conf, "c6_net", feats)
        return OutcomeResult(Outcome.OUT, _oob_fault(last_y, g), conf, "c6_out", feats)

    # CHECK 7 — final fallback
    apex = float(seg[:, 2].min()) if len(seg) else last_y
    if abs(last_y - g.net_ground_y) < tol * 2 and _near_net_x(last_x, g) and apex < g.net_ground_y:
        return OutcomeResult(Outcome.NET, net_fault, conf, "c7_net", feats)
    return OutcomeResult(Outcome.WINNER, "far" if last_y < g.net_ground_y else "near", conf, "c7_landing", feats)


def outcome_confidence(res: OutcomeResult) -> float:
    return {"HIGH": 0.85, "MEDIUM": 0.7, "LOW": 0.4}[res.confidence] if res.outcome is not Outcome.UNKNOWN else 0.2
