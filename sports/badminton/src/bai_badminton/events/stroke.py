"""Stroke classification at a contact.

Two classifiers share one interface (``StrokeClassifier``):

* :class:`RuleStrokeClassifier` (``stroke_rules_v0``) — a deterministic fallback from the hitter's
  court zone, the shuttle's post-contact speed and its flight time.  Always available; confidence
  is capped so its labels surface as ``probable``/``uncertain``.
* ``BSTStrokeClassifier`` (``bai_badminton.perception.bst``) — the BST-CG-AP transformer with
  released ShuttleSet weights (pose + shuttle + court), used when its weights are installed.

Both return a probability distribution over the canonical strokes of the ontology.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Protocol

import numpy as np

from bai_badminton.court import HALF_LEN
from bai_badminton.ontology import get_ontology


@dataclass
class StrokeContext:
    """Everything a stroke classifier may use about one contact."""

    frame: int
    player_id: str | None
    is_serve: bool
    hitter_court_xy: tuple[float, float] | None  # feet position (m) at contact
    speed_after_px_s: float | None  # initial shuttle speed after contact (image px/s)
    frame_height_px: float
    flight_time_s: float | None  # until the next contact or rally end
    vy_after_px_s: float | None  # image-space vertical velocity after contact (+ = down)
    hitter_side: str | None  # near | far
    contact_above_head: bool | None
    extra: dict[str, object] = field(default_factory=dict)


@dataclass
class StrokePrediction:
    probs: dict[str, float]
    model: str

    @property
    def top(self) -> tuple[str, float]:
        k = max(self.probs, key=self.probs.__getitem__)
        return k, self.probs[k]

    @property
    def margin(self) -> float:
        v = sorted(self.probs.values(), reverse=True)
        return v[0] - (v[1] if len(v) > 1 else 0.0)


class StrokeClassifier(Protocol):
    name: str

    def predict(self, ctx: StrokeContext) -> StrokePrediction: ...


def _softmax(scores: dict[str, float], temp: float = 1.0) -> dict[str, float]:
    m = max(scores.values())
    e = {k: math.exp((v - m) / temp) for k, v in scores.items()}
    s = sum(e.values())
    return {k: v / s for k, v in e.items()}


class RuleStrokeClassifier:
    name = "stroke_rules_v0"
    MAX_CONF = 0.7  # never "confirmed" from rules alone

    def predict(self, ctx: StrokeContext) -> StrokePrediction:
        strokes = [s for s in get_ontology().strokes if s != "unknown"]
        scores = dict.fromkeys(strokes, 0.0)
        v = (ctx.speed_after_px_s or 0.0) / max(ctx.frame_height_px, 1.0)  # frame heights per second
        ft = ctx.flight_time_s
        depth = abs(ctx.hitter_court_xy[1]) if ctx.hitter_court_xy else None

        if ctx.is_serve:
            long = ft is not None and ft > 0.9
            scores["long_serve" if long else "short_serve"] += 3.0
            scores["short_serve" if long else "long_serve"] += 1.0
        else:
            fast = v > 1.6
            very_fast = v > 2.6
            long_flight = ft is not None and ft > 1.0
            short_flight = ft is not None and ft < 0.6
            front = depth is not None and depth < 2.6
            rear = depth is not None and depth > HALF_LEN - 1.8
            if front:
                if fast and not long_flight:
                    scores["rush"] += 2.5
                elif long_flight:
                    scores["lift"] += 2.5
                else:
                    scores["net_shot"] += 2.2
                    scores["cross_net"] += 0.8
                    scores["block"] += 0.6
            elif rear:
                if very_fast or (fast and short_flight):
                    scores["smash"] += 2.8
                    if ctx.contact_above_head:
                        scores["smash"] += 0.6
                elif long_flight:
                    scores["clear"] += 2.5
                else:
                    scores["drop"] += 2.2
            else:  # mid court
                if fast:
                    scores["drive"] += 2.0
                    scores["smash"] += 0.8 if ctx.contact_above_head else 0.0
                elif long_flight:
                    scores["lift"] += 1.8
                else:
                    scores["push"] += 1.6
                    scores["block"] += 1.2
        probs = _softmax(scores, temp=0.8)
        # cap confidence: redistribute mass above MAX_CONF uniformly
        top = max(probs, key=probs.__getitem__)
        if probs[top] > self.MAX_CONF:
            excess = probs[top] - self.MAX_CONF
            probs[top] = self.MAX_CONF
            others = [k for k in probs if k != top]
            for k in others:
                probs[k] += excess / len(others)
        return StrokePrediction(probs=probs, model=self.name)


# ---------------------------------------------------------------------- smash / jump smash
@dataclass
class SmashAssessment:
    p_smash: float
    p_jump: float | None
    components: dict[str, float]


def _sig(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


def jump_features(
    ankles_y: np.ndarray, hips_y: np.ndarray, heights: np.ndarray, contact_idx: int
) -> dict[str, float] | None:
    """Jump evidence from pose around a contact.

    ``ankles_y``: (n, 2) left/right ankle image y; ``hips_y``: (n,) hip-centre y; ``heights``: (n,)
    body heights (px). Window convention: baseline = frames [-20, -8] before contact, jump window
    = [-6, +6].  Image y grows downward, so a lift is ``baseline_y - y``.
    """
    n = len(hips_y)
    b0, b1 = max(0, contact_idx - 20), max(0, contact_idx - 8)
    w0, w1 = max(0, contact_idx - 6), min(n, contact_idx + 7)
    if b1 - b0 < 3 or w1 - w0 < 3:
        return None
    h = float(np.nanmedian(heights[b0:w1]))
    if not np.isfinite(h) or h <= 1:
        return None
    base_l = np.nanmedian(ankles_y[b0:b1, 0])
    base_r = np.nanmedian(ankles_y[b0:b1, 1])
    lift_l = (base_l - np.nanmin(ankles_y[w0:w1, 0])) / h
    lift_r = (base_r - np.nanmin(ankles_y[w0:w1, 1])) / h
    if not (np.isfinite(lift_l) and np.isfinite(lift_r)):
        return None
    hip_base = np.nanmedian(hips_y[b0:b1])
    hip_lift = (hip_base - np.nanmin(hips_y[w0:w1])) / h
    return {
        "lift_min": float(min(lift_l, lift_r)),
        "lift_max": float(max(lift_l, lift_r)),
        "hip_lift": float(hip_lift) if np.isfinite(hip_lift) else 0.0,
    }


def assess_smash(
    p_smash_cls: float,
    speed_after_px_s: float | None,
    frame_height_px: float,
    contact_above_head: bool | None,
    jump: dict[str, float] | None,
) -> SmashAssessment:
    v = (speed_after_px_s or 0.0) / max(frame_height_px, 1.0)
    s_speed = float(np.clip((v - 1.4) / 1.6, 0.0, 1.0))
    s_height = 1.0 if contact_above_head else (0.5 if contact_above_head is None else 0.0)
    p_kin = s_speed * (0.6 + 0.4 * s_height)
    p_smash = float(np.clip(0.6 * p_smash_cls + 0.4 * p_kin, 0.0, 1.0))
    p_jump = None
    comps = {"cls": p_smash_cls, "speed": s_speed, "height": s_height, "kinematic": p_kin}
    if jump is not None:
        s_lift = float(np.clip((jump["lift_min"] - 0.03) / 0.10, 0.0, 1.0))  # both feet left the ground
        s_lift_max = float(np.clip((jump["lift_max"] - 0.05) / 0.12, 0.0, 1.0))
        s_hip = float(np.clip((jump["hip_lift"] - 0.03) / 0.10, 0.0, 1.0))
        p_jump = _sig(-3.0 + 3.5 * s_lift + 1.5 * s_lift_max + 2.0 * s_hip)
        comps.update({"lift_min": s_lift, "lift_max": s_lift_max, "hip": s_hip})
    return SmashAssessment(p_smash=p_smash, p_jump=p_jump, components=comps)
