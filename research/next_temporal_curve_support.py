"""Research-only mature-event continuation from observed upper-flight curves.

Prespecified experiment: retain the original cue, then require observed moving
ascending/descending brackets under the existing 5-frame, 2-second and 3..120
pixel/frame budgets. A pixel-space quadratic must have its apex outside the
image in EVERY leave-one-out fit. No fit residual threshold is tuned; residuals
remain explicit diagnostics. This is not physical 3D tracking or calibrated
uncertainty. No reconstructed coordinates are emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass, replace
from math import isfinite
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.events.rally_motion import image_exit_return_supported  # noqa: E402
from bai_badminton.observations import WindowObs  # noqa: E402
from bai_badminton.perception.shuttle_post import ANCHOR, MAX_FILL_SPEED  # noqa: E402
from research.next_temporal_trajectory_probe import fit  # noqa: E402


@dataclass(frozen=True)
class CurveSupport:
    supported: bool
    reason: str
    gap_start: int | None = None
    gap_end: int | None = None
    before_frames: tuple[int, ...] = ()
    after_frames: tuple[int, ...] = ()
    curve: dict | None = None
    leave_one_out_apex_y: tuple[float, ...] = ()


def curve_exit_return_support(
    window: WindowObs,
    index: int,
    *,
    frame_height: float,
    raw_xy=None,
    max_gap_s: float = 2.0,
    top_fraction: float = 0.1,
    minimum_speed: float = 3.0,
) -> CurveSupport:
    # Original helper validates the shared public contract. Its positive
    # decision is handled by the caller without any new qualification rule.
    image_exit_return_supported(
        window,
        index,
        frame_height=frame_height,
        raw_xy=raw_xy,
        max_gap_s=max_gap_s,
        top_fraction=top_fraction,
        minimum_speed=minimum_speed,
    )
    track = window.shuttle
    observed = track.vis & ~track.interp & np.isfinite(track.x) & np.isfinite(track.y) & ~window.replay
    if observed[index] or window.replay[index]:
        return CurveSupport(False, "sample_is_observed_or_invalid")
    lo, hi = window.segment_bounds(index)
    start, end = index, index + 1
    while start > lo and not observed[start - 1]:
        start -= 1
    while end < hi and not observed[end]:
        end += 1
    if (end - start) / window.fps > max_gap_s:
        return CurveSupport(False, "existing_gap_budget_exceeded")
    brackets = (
        np.flatnonzero(observed[max(lo, start - ANCHOR) : start]) + max(lo, start - ANCHOR),
        np.flatnonzero(observed[end : min(hi, end + ANCHOR)]) + end,
    )
    positions = []
    for points in brackets:
        if len(points) < 2:
            return CurveSupport(False, "insufficient_observed_bracket")
        mapped = []
        for point in points:
            xy = float(track.x[point]), float(track.y[point])
            try:
                value = np.asarray(raw_xy(window.frame0 + int(point), xy) if raw_xy else xy, dtype=float)
            except (TypeError, ValueError, ArithmeticError):
                return CurveSupport(False, "image_mapping_failed")
            if value.shape != (2,) or not np.isfinite(value).all() or not 0 <= value[1] <= frame_height:
                return CurveSupport(False, "invalid_observed_image_point")
            mapped.append(value)
        xy = np.asarray(mapped)
        adjacent = np.diff(points) == 1
        steps = np.linalg.norm(np.diff(xy, axis=0)[adjacent], axis=1)
        speed = float(np.linalg.norm(xy[-1] - xy[0])) / int(points[-1] - points[0])
        if not minimum_speed <= speed <= MAX_FILL_SPEED or not np.any(steps >= minimum_speed):
            return CurveSupport(False, "moving_bracket_unreliable")
        if np.any(steps > MAX_FILL_SPEED):
            return CurveSupport(False, "observed_step_exceeds_existing_speed_budget")
        positions.append(xy)
    before, after = brackets
    first, last = positions
    if first[-1, 1] >= first[0, 1] or last[-1, 1] <= last[0, 1]:
        return CurveSupport(False, "ascending_and_descending_brackets_required")
    implied = float(np.linalg.norm(last[0] - first[-1])) / int(after[0] - before[-1])
    if implied > MAX_FILL_SPEED:
        return CurveSupport(False, "implied_step_exceeds_existing_speed_budget")
    absolute_before = tuple(window.frame0 + int(point) for point in before)
    absolute_after = tuple(window.frame0 + int(point) for point in after)
    points = [
        (frame, float(xy[0]), float(xy[1]))
        for frame, xy in zip(absolute_before + absolute_after, np.concatenate(positions), strict=True)
    ]
    curve = fit(points, absolute_before[-1], absolute_after[0])
    loo = [fit(points[:i] + points[i + 1 :], absolute_before[-1], absolute_after[0]) for i in range(len(points))]
    fits = [curve, *loo]
    reliable = all(
        item["apex_in_gap"] and item["apex_y"] is not None and isfinite(item["apex_y"]) and item["apex_y"] < 0
        for item in fits
    )
    return CurveSupport(
        reliable,
        "all_leave_one_out_apexes_outside_image" if reliable else "upper_exit_not_stable_under_anchor_omission",
        gap_start=window.frame0 + start,
        gap_end=window.frame0 + end,
        before_frames=absolute_before,
        after_frames=absolute_after,
        curve=curve,
        leave_one_out_apex_y=tuple(item["apex_y"] for item in loo if item["apex_y"] is not None),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-singleton", action="store_true")
    args = parser.parse_args()
    import bai_badminton.engine as engine
    import research.replay_rally_evidence as replay_module
    from bai_badminton.components import _EvidenceRally
    from research.next_temporal_association import associated_exit_return_supported, associated_loss_start

    extra = {}
    decisions = []
    proofs = {}
    blocked = []

    class QualifiedCurveRally(_EvidenceRally):
        def step_evidence(self, observation):
            loss_start = extra.get(observation.frame)
            start = self.closed.start if self.closed is not None else self.start
            if loss_start is not None and (start is None or loss_start - start < self.params.min_frames):
                blocked.append({"frame": observation.frame, "loss_start": loss_start, "interval_start": start})
                observation = replace(observation, exit_return_supported=False)
            return super().step_evidence(observation)

    def instrumented(window, index, **options):
        if image_exit_return_supported(window, index, **options):
            return True
        curve = curve_exit_return_support(window, index, **options)
        if curve.supported:
            loss_start = curve.gap_start
            key = str((curve.gap_start, curve.gap_end, curve.before_frames, curve.after_frames))
            from dataclasses import asdict

            proofs[key] = asdict(curve)
            method = "curve"
        elif args.include_singleton and associated_exit_return_supported(window, index, **options):
            loss_start = associated_loss_start(window, index)
            method = "singleton"
        else:
            return False
        frame = window.frame0 + index
        extra[frame] = loss_start
        decisions.append({"frame": frame, "window": [window.frame0, window.frame0 + window.n - 1], "method": method})
        return True

    replay_module._EvidenceRally = QualifiedCurveRally
    engine.image_exit_return_supported = instrumented
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    replay_module.replay(
        args.source.resolve(),
        args.output.resolve(),
        {"use_reconstruction": False, "motion_guard": False, "use_exit_recovery": True},
        implementation="rally-evidence-v2",
        candidate=True,
    )
    manifest = {
        "mode": "conditional semantic replay of cached observations; no fresh model inference",
        "intervention": "qualified upper-flight curve continuation"
        + (" plus singleton association" if args.include_singleton else ""),
        "script_sha256": script_hash,
        "script_unchanged": script_hash == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "maturity": "last pre-loss observed frame - interval start +1 >= existing min_frames",
        "fixed_budgets": {"anchor_frames": 5, "max_gap_s": 2, "moving_speed": [3, 120]},
        "residual_acceptance_threshold": None,
        "top_band_expanded": False,
        "changed_support_calls": decisions,
        "blocked_provisional_support_calls": blocked,
        "curve_proofs": proofs,
        "limits": [
            "No pixel/contact labels; no generalization claims",
            "Pixel-space curve is not physical3D or calibrated uncertainty",
            "No predictions or contacts manually edited",
        ],
    }
    (args.output / "curve_manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"alternate_calls": len(decisions), "blocked_provisional": len(blocked), "proofs": len(proofs)}))


if __name__ == "__main__":
    main()
