"""Frame-aligned participant and reconstructed-trajectory continuation cues.

These are uncalibrated support, never evidence that a rally exists. Participant
motion uses past observations only. Trajectory support can use the engine's
available lookahead; interpolation remains reconstructed, never observed.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from math import ceil, isfinite

import numpy as np
from numpy.typing import NDArray

from bai_badminton.observations import WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot, has_target_court_provenance
from bai_badminton.perception.keypoints import KP
from bai_badminton.perception.shuttle_post import ANCHOR, MAX_FILL_SPEED, MAX_GAP

_JOINTS = (KP.L_SHOULDER, KP.R_SHOULDER, KP.L_WRIST, KP.R_WRIST, KP.L_HIP, KP.R_HIP)


def _valid_box(snapshot: ParticipantSnapshot) -> bool:
    box = np.asarray(snapshot.bbox)
    return bool(box.shape == (4,) and np.isfinite(box).all() and (box[2:] > box[:2]).all())


def _pose(snapshot: ParticipantSnapshot, window: WindowObs, index: int) -> NDArray[np.float64] | None:
    assert window.pose_stride is not None
    stride = int(window.pose_stride[index])
    if stride <= 0 or (window.frame0 + index) % stride or snapshot.kps is None:
        return None
    pose = np.asarray(snapshot.kps)
    if pose.shape != (17, 3):
        return None
    return np.asarray(pose[np.asarray(_JOINTS)], dtype=np.float64)


def _pair_motion(window: WindowObs, snapshots: list[ParticipantSnapshot], left: int, right: int) -> float | None:
    first, last = snapshots[0], snapshots[-1]
    height = (float(first.bbox[3] - first.bbox[1]) + float(last.bbox[3] - last.bbox[1])) / 2
    if height <= 0:
        return None
    measures = []
    # A scheduled detector miss may not be bridged by a stale box.
    if all(s.detector_observed is True and s.detector_matched is True for s in (first, last)) and all(
        s.detector_observed is not True or s.detector_matched is True for s in snapshots
    ):
        center0 = (first.bbox[:2] + first.bbox[2:]) / 2
        center1 = (last.bbox[:2] + last.bbox[2:]) / 2
        measures.append(float(np.linalg.norm(center1 - center0)) / height)
    pose0, pose1 = _pose(first, window, left), _pose(last, window, right)
    if pose0 is not None and pose1 is not None:
        assert window.pose_stride is not None
        usable = np.isfinite(pose0).all(axis=1) & np.isfinite(pose1).all(axis=1)
        usable &= (pose0[:, 2] >= 0.3) & (pose1[:, 2] >= 0.3)
        # At least two joints must remain supported through every scheduled pose.
        for offset, snapshot in enumerate(snapshots):
            index = left + offset
            stride = int(window.pose_stride[index])
            if stride <= 0:
                usable[:] = False
                break
            if (window.frame0 + index) % stride == 0:
                pose = _pose(snapshot, window, index)
                if pose is None:
                    usable[:] = False
                    break
                usable &= np.isfinite(pose).all(axis=1) & (pose[:, 2] >= 0.3)
        if usable.sum() >= 2:
            displacement = np.linalg.norm(pose1[usable, :2] - pose0[usable, :2], axis=1) / height
            # One jittering wrist cannot establish independent body motion.
            measures.append(float(np.partition(displacement, -2)[-2]))
    return max(measures) if measures else None


def observed_participant_motion(
    window: WindowObs,
    frames: list[dict[str, ParticipantSnapshot]],
    index: int,
    *,
    window_s: float = 0.25,
    min_body_fraction: float = 0.1,
) -> bool | None:
    """Return observed motion, observed sub-threshold motion, or unknown.

    Two to four current target-court episodes are required. Pairs span at least
    half the configured window and share uninterrupted episode/track/birth and
    court provenance. Fresh matched boxes or actually scheduled confident poses
    support displacement; carried boxes alone never do. ``False`` means adequate
    observed displacement below the guard, not proof of inactivity or rally end.
    The defaults are prespecified exploratory guards, not calibrated confidence.
    """
    if len(frames) != window.n or not 0 <= index < window.n:
        raise ValueError("participant frames must align with the observation window")
    if not isfinite(window.fps) or window.fps <= 0:
        raise ValueError("FPS must be positive and finite")
    if not isfinite(window_s) or window_s <= 0 or not isfinite(min_body_fraction) or min_body_fraction <= 0:
        raise ValueError("motion window and body fraction must be positive and finite")
    span = max(1, ceil(window.fps * window_s))
    minimum_span = max(1, ceil(span / 2))
    segment_start, _ = window.segment_bounds(index)
    lo = max(segment_start, index - span)
    if index - lo < minimum_span or window.replay[index]:
        return None
    current = frames[index]
    if not 2 <= len(current) <= 4:
        return None
    if len({s.track_id for s in current.values()}) != len(current):
        return None
    if any(
        participant_id not in window.players or snapshot.track_id < 0 or not has_target_court_provenance(snapshot)
        for participant_id, snapshot in current.items()
    ):
        return None
    adequate = 0
    for participant_id, last in current.items():
        known = False
        for left in range(lo, index - minimum_span + 1):
            snapshots = [frame.get(participant_id) for frame in frames[left : index + 1]]
            if any(
                s is None
                or s.track_id != last.track_id
                or s.observation_id != last.observation_id
                or not has_target_court_provenance(s)
                or not _valid_box(s)
                for s in snapshots
            ):
                continue
            motion = _pair_motion(window, [s for s in snapshots if s is not None], left, index)
            if motion is not None:
                known = True
                if motion >= min_body_fraction:
                    return True
        adequate += int(known)
    return False if adequate == len(current) else None


def trajectory_continuation_supported(window: WindowObs, index: int, *, minimum_speed: float = 3.0) -> bool:
    """Require observed moving brackets on BOTH sides of a reconstructed gap.

    Reuse the existing trajectory fill's five-frame anchor, maximum gap and
    speed bounds. Each bracket needs two finite observed points, an adjacent
    observed moving pair, and displacement speed within the existing bounds.
    A stationary/pickup bracket cannot support continuation merely because the
    opposite bracket moves. No observed/start/contact provenance is fabricated.
    """
    if not 0 <= index < window.n:
        raise ValueError("trajectory index must lie in the observation window")
    if not isfinite(minimum_speed) or not 0 < minimum_speed <= MAX_FILL_SPEED:
        raise ValueError("minimum motion speed must be finite and within the fill-speed bound")
    track = window.shuttle
    if not track.interp[index] or window.replay[index]:
        return False
    lo, hi = window.segment_bounds(index)
    start, end = index, index + 1
    while start > lo and track.interp[start - 1]:
        start -= 1
    while end < hi and track.interp[end]:
        end += 1
    if end - start > MAX_GAP or not track.vis[start:end].all():
        return False
    if not np.isfinite(track.x[start:end]).all() or not np.isfinite(track.y[start:end]).all():
        return False
    observed = track.vis & ~track.interp & np.isfinite(track.x) & np.isfinite(track.y) & ~window.replay
    brackets = (
        np.flatnonzero(observed[max(lo, start - ANCHOR) : start]) + max(lo, start - ANCHOR),
        np.flatnonzero(observed[end : min(hi, end + ANCHOR)]) + end,
    )
    for points in brackets:
        if len(points) < 2:
            return False
        dx, dy = np.diff(track.x[points]), np.diff(track.y[points])
        adjacent = np.diff(points) == 1
        steps = np.hypot(dx[adjacent], dy[adjacent])
        speed = float(
            np.hypot(track.x[points[-1]] - track.x[points[0]], track.y[points[-1]] - track.y[points[0]])
        ) / int(points[-1] - points[0])
        if not minimum_speed <= speed <= MAX_FILL_SPEED or not np.any(steps >= minimum_speed):
            return False
        if np.any(steps > MAX_FILL_SPEED):
            return False
    left, right = brackets[0][-1], brackets[1][0]
    implied_speed = float(np.hypot(track.x[right] - track.x[left], track.y[right] - track.y[left])) / int(right - left)
    return implied_speed <= MAX_FILL_SPEED


def image_exit_return_supported(
    window: WindowObs,
    index: int,
    *,
    frame_height: float,
    raw_xy: Callable[[int, tuple[float, float]], tuple[float, float]] | None = None,
    max_gap_s: float = 2.0,
    top_fraction: float = 0.1,
    minimum_speed: float = 3.0,
) -> bool:
    """Bounded uncertainty support for an observed top exit and observed return.

    Both observed moving brackets must exist in the available temporal segment.
    Exit/reentry endpoints lie in the top image band, with upward motion before
    and downward motion afterwards. ``raw_xy`` maps stabilized anchor positions
    back to their own absolute image frames; without it, coordinates must already
    be image coordinates. Missing/reconstructed positions are never filled or
    promoted to observed. This exploratory cue does not itself establish play.
    """
    if not 0 <= index < window.n:
        raise ValueError("trajectory index must lie in the observation window")
    if not isfinite(frame_height) or frame_height <= 0 or not isfinite(window.fps) or window.fps <= 0:
        raise ValueError("image height and FPS must be positive and finite")
    if not isfinite(max_gap_s) or max_gap_s <= 0 or not isfinite(top_fraction) or not 0 < top_fraction < 1:
        raise ValueError("gap duration and top-image fraction must be finite and valid")
    if not isfinite(minimum_speed) or not 0 < minimum_speed <= MAX_FILL_SPEED:
        raise ValueError("minimum motion speed must be finite and within the fill-speed bound")
    track = window.shuttle
    observed = track.vis & ~track.interp & np.isfinite(track.x) & np.isfinite(track.y) & ~window.replay
    if observed[index] or window.replay[index]:
        return False
    lo, hi = window.segment_bounds(index)
    start, end = index, index + 1
    while start > lo and not observed[start - 1]:
        start -= 1
    while end < hi and not observed[end]:
        end += 1
    if (end - start) / window.fps > max_gap_s:
        return False
    brackets = (
        np.flatnonzero(observed[max(lo, start - ANCHOR) : start]) + max(lo, start - ANCHOR),
        np.flatnonzero(observed[end : min(hi, end + ANCHOR)]) + end,
    )
    coordinates: dict[int, NDArray[np.float64]] = {}
    for points in brackets:
        if len(points) < 2:
            return False
        for point in points:
            xy = (float(track.x[point]), float(track.y[point]))
            try:
                mapped = np.asarray(raw_xy(window.frame0 + int(point), xy) if raw_xy else xy, dtype=np.float64)
            except (TypeError, ValueError, ArithmeticError):
                return False
            if mapped.shape != (2,) or not np.isfinite(mapped).all() or not 0 <= mapped[1] <= frame_height:
                return False
            coordinates[int(point)] = mapped
        positions = np.asarray([coordinates[int(point)] for point in points])
        adjacent = np.diff(points) == 1
        steps = np.linalg.norm(np.diff(positions, axis=0)[adjacent], axis=1)
        speed = float(np.linalg.norm(positions[-1] - positions[0])) / int(points[-1] - points[0])
        if not minimum_speed <= speed <= MAX_FILL_SPEED or not np.any(steps >= minimum_speed):
            return False
        if np.any(steps > MAX_FILL_SPEED):
            return False
    before, after = brackets
    exit_xy, return_xy = coordinates[int(before[-1])], coordinates[int(after[0])]
    if max(exit_xy[1], return_xy[1]) > frame_height * top_fraction:
        return False
    if exit_xy[1] >= coordinates[int(before[0])][1] or coordinates[int(after[-1])][1] <= return_xy[1]:
        return False
    implied_speed = float(np.linalg.norm(return_xy - exit_xy)) / int(after[0] - before[-1])
    return implied_speed <= MAX_FILL_SPEED


@dataclass(frozen=True, slots=True)
class ImageFlightCurve:
    """Pixel-space fit diagnostics; neither physical 3D nor calibrated error."""

    origin_frame: float
    x_coefficients: tuple[float, float]
    y_coefficients: tuple[float, float, float]
    residual_rmse_px: float
    residual_max_px: float
    apex_frame: float | None
    apex_y: float | None
    apex_in_gap: bool


@dataclass(frozen=True, slots=True)
class ImageExitReturnSupport:
    """Uncalibrated support proof, never a reconstructed/observed coordinate.

    ``[gap_start,gap_end)`` is the association hypothesis span and can contain
    the explicitly unassociated observation. The actual stream is unchanged.
    All frame values use the absolute canonical timeline.
    """

    supported: bool
    basis: str
    reason: str
    gap_start: int | None = None
    gap_end: int | None = None
    ignored_frame: int | None = None
    before_frames: tuple[int, ...] = ()
    after_frames: tuple[int, ...] = ()
    curve: ImageFlightCurve | None = None
    leave_one_out_apex_y: tuple[float, ...] = ()
    sensitivity_semantics: str | None = None


def image_exit_return_tracklet_support(
    window: WindowObs,
    index: int,
    *,
    frame_height: float,
    raw_xy: Callable[[int, tuple[float, float]], tuple[float, float]] | None = None,
    max_gap_s: float = 2.0,
    top_fraction: float = 0.1,
    minimum_speed: float = 3.0,
    minimum_exit_frame: int | None = None,
) -> ImageExitReturnSupport:
    """Original observed exit/return proof with one bounded association option.

    At most one singleton lacking observed neighbors on BOTH sides may be
    unassociated inside a local proof. Two adjacent floor/static observations
    are never skipped. The unchanged helper must then verify BOTH coherent
    moving upper-image brackets with the same gap/speed/context budgets.

    ``minimum_exit_frame`` optionally requires that the last pre-loss coherent
    observation is late enough. A caller can use interval_start+min_frames-1
    to restrict this extension to an already qualified event. Waiting through
    missingness never earns this qualification. No new start/contact or output
    coordinate is created, and the input window and track are never mutated.
    """
    if minimum_exit_frame is not None and (type(minimum_exit_frame) is not int or minimum_exit_frame < 0):
        raise ValueError("minimum exit frame must be a nonnegative canonical integer or unavailable")
    options = {
        "frame_height": frame_height,
        "raw_xy": raw_xy,
        "max_gap_s": max_gap_s,
        "top_fraction": top_fraction,
        "minimum_speed": minimum_speed,
    }
    # Keep original validation and positive behavior in a single source.
    original = image_exit_return_supported(window, index, **options)
    track = window.shuttle
    observed = track.vis & ~track.interp & np.isfinite(track.x) & np.isfinite(track.y) & ~window.replay
    lo, hi = window.segment_bounds(index)
    ignored = None
    if not original:
        if observed[index] or window.replay[index]:
            return ImageExitReturnSupport(False, "none", "current_sample_is_observed_or_invalid")
        left, right = index - 1, index + 1
        while left >= lo and not observed[left]:
            left -= 1
        while right < hi and not observed[right]:
            right += 1

        def isolated(point: int) -> bool:
            return lo < point < hi - 1 and observed[point] and not observed[point - 1] and not observed[point + 1]

        singletons = [int(point) for point in (left, right) if isolated(point)]
        if len(singletons) != 1:
            return ImageExitReturnSupport(False, "none", "exactly_one_isolated_alternative_required")
        ignored = singletons[0]
        associated = track.vis.copy()
        associated[ignored] = False
        alternative = replace(window, shuttle=replace(track, vis=associated))
        if not image_exit_return_supported(alternative, index, **options):
            return ImageExitReturnSupport(
                False,
                "single_unassociated_observation",
                "coherent_exit_return_brackets_rejected",
                ignored_frame=window.frame0 + ignored,
            )
        observed = observed.copy()
        observed[ignored] = False
    start, end = index, index + 1
    while start > lo and not observed[start - 1]:
        start -= 1
    while end < hi and not observed[end]:
        end += 1
    before = np.flatnonzero(observed[max(lo, start - ANCHOR) : start]) + max(lo, start - ANCHOR)
    after = np.flatnonzero(observed[end : min(hi, end + ANCHOR)]) + end
    proof = {
        "gap_start": window.frame0 + start,
        "gap_end": window.frame0 + end,
        "ignored_frame": window.frame0 + ignored if ignored is not None else None,
        "before_frames": tuple(window.frame0 + int(point) for point in before),
        "after_frames": tuple(window.frame0 + int(point) for point in after),
    }
    basis = "observed_top_exit_return" if original else "single_unassociated_observation"
    if minimum_exit_frame is not None and window.frame0 + int(before[-1]) < minimum_exit_frame:
        return ImageExitReturnSupport(False, basis, "event_not_qualified_before_loss", **proof)
    return ImageExitReturnSupport(True, basis, "coherent_observed_exit_return", **proof)


def _fit_image_flight_curve(
    frames: NDArray[np.float64], positions: NDArray[np.float64], exit_frame: int, return_frame: int
) -> ImageFlightCurve:
    origin = (exit_frame + return_frame) / 2
    times = frames - origin
    cx = np.polyfit(times, positions[:, 0], 1)
    cy = np.polyfit(times, positions[:, 1], 2)
    predicted = np.column_stack((np.polyval(cx, times), np.polyval(cy, times)))
    residuals = np.linalg.norm(predicted - positions, axis=1)
    apex_t = float(-cy[1] / (2 * cy[0])) if cy[0] > 0 else None
    apex_frame = origin + apex_t if apex_t is not None else None
    return ImageFlightCurve(
        origin_frame=origin,
        x_coefficients=(float(cx[0]), float(cx[1])),
        y_coefficients=(float(cy[0]), float(cy[1]), float(cy[2])),
        residual_rmse_px=float(np.sqrt(np.mean(residuals**2))),
        residual_max_px=float(residuals.max()),
        apex_frame=apex_frame,
        apex_y=float(np.polyval(cy, apex_t)) if apex_t is not None else None,
        apex_in_gap=bool(apex_frame is not None and exit_frame < apex_frame < return_frame),
    )


def image_exit_return_curve_support(
    window: WindowObs,
    index: int,
    *,
    frame_height: float,
    raw_xy: Callable[[int, tuple[float, float]], tuple[float, float]] | None = None,
    max_gap_s: float = 2.0,
    top_fraction: float = 0.1,
    minimum_speed: float = 3.0,
    minimum_exit_frame: int | None = None,
) -> ImageExitReturnSupport:
    """Observed upper-flight support with explicit omission sensitivity.

    Use only the supplied same-context observed moving brackets and the existing
    anchor/gap/speed budgets. Both a joint pixel-space quadratic and EVERY
    leave-one-anchor-out fit must place the apex outside the image, between the
    brackets. This is an opt-in research cue, not a physical 3D model or calibrated
    uncertainty estimate. Residuals are reported, without a fitted threshold.

    The optional minimum exit frame qualifies the event BEFORE observation loss.
    No missing position, contact, start or future observation is generated.
    """
    if minimum_exit_frame is not None and (type(minimum_exit_frame) is not int or minimum_exit_frame < 0):
        raise ValueError("minimum exit frame must be a nonnegative canonical integer or unavailable")
    # Reuse the existing parameter-validation contract; its positive decision is
    # handled independently by the provider, preserving provisional v2 behavior.
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
        return ImageExitReturnSupport(False, "none", "current_sample_is_observed_or_invalid")
    lo, hi = window.segment_bounds(index)
    start, end = index, index + 1
    while start > lo and not observed[start - 1]:
        start -= 1
    while end < hi and not observed[end]:
        end += 1
    proof = {"gap_start": window.frame0 + start, "gap_end": window.frame0 + end}
    if (end - start) / window.fps > max_gap_s:
        return ImageExitReturnSupport(False, "none", "existing_gap_budget_exceeded", **proof)
    brackets = (
        np.flatnonzero(observed[max(lo, start - ANCHOR) : start]) + max(lo, start - ANCHOR),
        np.flatnonzero(observed[end : min(hi, end + ANCHOR)]) + end,
    )
    positions = []
    for points in brackets:
        if len(points) < 2:
            return ImageExitReturnSupport(False, "none", "insufficient_observed_bracket", **proof)
        mapped = []
        for point in points:
            xy = float(track.x[point]), float(track.y[point])
            try:
                value = np.asarray(raw_xy(window.frame0 + int(point), xy) if raw_xy else xy, dtype=np.float64)
            except (TypeError, ValueError, ArithmeticError):
                return ImageExitReturnSupport(False, "none", "image_mapping_failed", **proof)
            if value.shape != (2,) or not np.isfinite(value).all() or not 0 <= value[1] <= frame_height:
                return ImageExitReturnSupport(False, "none", "invalid_observed_image_point", **proof)
            mapped.append(value)
        xy = np.asarray(mapped)
        adjacent = np.diff(points) == 1
        steps = np.linalg.norm(np.diff(xy, axis=0)[adjacent], axis=1)
        speed = float(np.linalg.norm(xy[-1] - xy[0])) / int(points[-1] - points[0])
        if not minimum_speed <= speed <= MAX_FILL_SPEED or not np.any(steps >= minimum_speed):
            return ImageExitReturnSupport(False, "none", "moving_bracket_unreliable", **proof)
        if np.any(steps > MAX_FILL_SPEED):
            return ImageExitReturnSupport(False, "none", "observed_step_exceeds_speed_budget", **proof)
        positions.append(xy)
    before, after = brackets
    first, last = positions
    proof.update(
        before_frames=tuple(window.frame0 + int(point) for point in before),
        after_frames=tuple(window.frame0 + int(point) for point in after),
    )
    if minimum_exit_frame is not None and proof["before_frames"][-1] < minimum_exit_frame:
        return ImageExitReturnSupport(False, "observed_bracket_curve_exit", "event_not_qualified_before_loss", **proof)
    if first[-1, 1] >= first[0, 1] or last[-1, 1] <= last[0, 1]:
        return ImageExitReturnSupport(False, "none", "ascending_and_descending_brackets_required", **proof)
    implied = float(np.linalg.norm(last[0] - first[-1])) / int(after[0] - before[-1])
    if implied > MAX_FILL_SPEED:
        return ImageExitReturnSupport(False, "none", "implied_step_exceeds_speed_budget", **proof)
    frames = np.asarray(proof["before_frames"] + proof["after_frames"], dtype=np.float64)
    coordinates = np.concatenate(positions)
    exit_frame, return_frame = int(frames[len(before) - 1]), int(frames[len(before)])
    curve = _fit_image_flight_curve(frames, coordinates, exit_frame, return_frame)
    omissions = [
        _fit_image_flight_curve(np.delete(frames, i), np.delete(coordinates, i, axis=0), exit_frame, return_frame)
        for i in range(len(frames))
    ]
    supported = all(
        fit.apex_in_gap and fit.apex_y is not None and isfinite(fit.apex_y) and fit.apex_y < 0
        for fit in (curve, *omissions)
    )
    return ImageExitReturnSupport(
        supported,
        "observed_bracket_curve_exit",
        "all_anchor_omissions_support_upper_exit" if supported else "upper_exit_unstable_under_anchor_omission",
        **proof,
        curve=curve,
        leave_one_out_apex_y=tuple(fit.apex_y for fit in omissions if fit.apex_y is not None),
        sensitivity_semantics="leave_one_anchor_out_sensitivity_not_calibrated_uncertainty",
    )
