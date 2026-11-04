"""Diagnostic competing-association proofs; never an automatic rally decision.

A retained compact static cluster may be a painted line, spare shuttle, real
landing or another object. This helper preserves every raw observation and asks
only whether one alternative association also has coherent observed upper-flight
brackets. Even a positive geometric counterfactual remains AMBIGUOUS. It is not
converted into MISSING, a contact, a position or an FSM input.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from math import ceil, isfinite
from typing import Literal

import numpy as np

from bai_badminton.events.rally_motion import image_exit_return_supported
from bai_badminton.observations import WindowObs
from bai_badminton.perception.shuttle_post import ANCHOR


@dataclass(frozen=True, slots=True)
class StaticClusterCounterfactual:
    """Association hypothesis with its actual raw member-frame provenance."""

    gap_start: int
    gap_end: int
    unassociated_frames: tuple[int, ...]
    before_frames: tuple[int, ...]
    after_frames: tuple[int, ...]
    cluster_centroid_xy: tuple[float, float]  # descriptor, never a shuttle position
    maximum_radius_cells: float
    qualified_frames_before_loss: int


@dataclass(frozen=True, slots=True)
class StaticClusterReview:
    status: Literal["abstain_no_supported_alternative", "abstain_ambiguous_association"]
    reasons: tuple[str, ...]
    counterfactuals: tuple[StaticClusterCounterfactual, ...] = ()
    accepted_continuity: Literal[False] = False
    requires_independent_context_evidence: Literal[True] = True
    scale_semantics: str = "heatmap_cell_sensitivity_not_calibrated_localization_uncertainty"
    raw_observation_policy: str = "unchanged; retain coordinates, support, visibility and interpolation flags"


def static_cluster_exit_counterfactual(
    window: WindowObs,
    index: int,
    *,
    frame_height: float,
    interval_start: int | None,
    minimum_event_frames: int,
    heatmap_cell_px: tuple[float, float],
    maximum_cluster_radius_cells: float = 1.0,
    max_gap_s: float = 2.0,
    top_fraction: float = 0.1,
    minimum_speed: float = 3.0,
    maximum_proofs: int = 3,
    raw_xy: Callable[[int, tuple[float, float]], tuple[float, float]] | None = None,
) -> StaticClusterReview:
    """Review one bounded competing static-cluster association, without action.

    Spatial compactness is prespecified in actual heatmap cells; the default one
    cell is a sensitivity assumption, not an estimated noise covariance. A
    candidate needs at least two consecutive observed frames and must be below
    the existing upper-image band. This protects a directly observed slow apex
    from being relabeled as a distractor. A coherent moving tracklet is retained.

    The original upper-exit helper must still pass with only ONE local static
    cluster unassociated, under the same context, temporal, direction, speed
    and anchor limits. Qualification uses the last exit anchor BEFORE loss.
    The returned proof is descriptive; real floor-stop-plus-launch and an
    unflagged same-camera edit can remain observationally ambiguous.
    """
    if interval_start is not None and (type(interval_start) is not int or interval_start < 0):
        raise ValueError("interval start must be a nonnegative canonical integer or unavailable")
    if type(minimum_event_frames) is not int or minimum_event_frames < 1:
        raise ValueError("minimum event frames must be the existing positive duration contract")
    if len(heatmap_cell_px) != 2 or not all(isfinite(v) and v > 0 for v in heatmap_cell_px):
        raise ValueError("heatmap cell dimensions must be positive finite image-pixel scales")
    if not isfinite(maximum_cluster_radius_cells) or maximum_cluster_radius_cells <= 0:
        raise ValueError("cluster radius must be positive and finite")
    if type(maximum_proofs) is not int or not 1 <= maximum_proofs <= 8:
        raise ValueError("diagnostic proof budget must be between one and eight")
    options = {
        "frame_height": frame_height,
        "raw_xy": raw_xy,
        "max_gap_s": max_gap_s,
        "top_fraction": top_fraction,
        "minimum_speed": minimum_speed,
    }
    # Reuse original validation, without treating an existing continuation cue
    # as new evidence that a competing static cluster is a physical distractor.
    original = image_exit_return_supported(window, index, **options)
    if interval_start is None:
        return StaticClusterReview("abstain_no_supported_alternative", ("existing_event_start_unknown",))
    if original:
        return StaticClusterReview("abstain_no_supported_alternative", ("existing_noncluster_exit_cue_suffices",))
    track = window.shuttle
    observed = track.vis & ~track.interp & np.isfinite(track.x) & np.isfinite(track.y) & ~window.replay
    if window.replay[index]:
        return StaticClusterReview("abstain_no_supported_alternative", ("current_context_invalid",))
    lo, hi = window.segment_bounds(index)
    budget = ceil(max_gap_s * window.fps)
    local_lo, local_hi = max(lo, index - budget - ANCHOR), min(hi, index + budget + ANCHOR + 1)
    frames = np.flatnonzero(observed[local_lo:local_hi]) + local_lo
    positions = {}
    for point in frames:
        xy = float(track.x[point]), float(track.y[point])
        try:
            mapped = np.asarray(raw_xy(window.frame0 + int(point), xy) if raw_xy else xy, dtype=float)
        except (TypeError, ValueError, ArithmeticError):
            continue
        if mapped.shape == (2,) and np.isfinite(mapped).all() and 0 <= mapped[1] <= frame_height:
            positions[int(point)] = mapped
    frames = [int(point) for point in frames if int(point) in positions]
    cells = np.asarray(heatmap_cell_px, dtype=float)
    clusters = []
    cursor = 0
    while cursor < len(frames) - 1:
        if frames[cursor + 1] != frames[cursor] + 1:
            cursor += 1
            continue
        members = [frames[cursor]]
        stop = cursor + 1
        while stop < len(frames) and frames[stop] == members[-1] + 1:
            proposed = [*members, frames[stop]]
            xy = np.asarray([positions[point] for point in proposed])
            center = np.median(xy, axis=0)
            radius = float(np.linalg.norm((xy - center) / cells, axis=1).max())
            if radius > maximum_cluster_radius_cells or len(proposed) > budget:
                break
            members = proposed
            stop += 1
        if len(members) >= 2:
            clusters.append(members)
        cursor = max(cursor + 1, stop)
    proofs = []
    reasons = []
    for members in clusters:
        xy = np.asarray([positions[point] for point in members])
        center = np.median(xy, axis=0)
        if center[1] <= frame_height * top_fraction:
            reasons.append("observed_upper_band_stationarity_is_not_a_distractor_proof")
            continue
        alternative_vis = track.vis.copy()
        alternative_vis[members] = False
        alternative = replace(window, shuttle=replace(track, vis=alternative_vis))
        if not image_exit_return_supported(alternative, index, **options):
            continue
        associated = observed.copy()
        associated[members] = False
        start, end = index, index + 1
        while start > lo and not associated[start - 1]:
            start -= 1
        while end < hi and not associated[end]:
            end += 1
        before = np.flatnonzero(associated[max(lo, start - ANCHOR) : start]) + max(lo, start - ANCHOR)
        after = np.flatnonzero(associated[end : min(hi, end + ANCHOR)]) + end
        qualified = window.frame0 + int(before[-1]) - interval_start + 1
        if qualified < minimum_event_frames:
            reasons.append("event_not_qualified_before_loss")
            continue
        radius = float(np.linalg.norm((xy - center) / cells, axis=1).max())
        proofs.append(
            StaticClusterCounterfactual(
                gap_start=window.frame0 + start,
                gap_end=window.frame0 + end,
                unassociated_frames=tuple(window.frame0 + point for point in members),
                before_frames=tuple(window.frame0 + int(point) for point in before),
                after_frames=tuple(window.frame0 + int(point) for point in after),
                cluster_centroid_xy=(float(center[0]), float(center[1])),
                maximum_radius_cells=radius,
                qualified_frames_before_loss=qualified,
            )
        )
        if len(proofs) >= maximum_proofs:
            break
    if proofs:
        return StaticClusterReview(
            "abstain_ambiguous_association",
            (
                "coherent_upper_flight_is_one_competing_association",
                "physical_static_object_and_scene_identity_unresolved",
            ),
            tuple(proofs),
        )
    return StaticClusterReview(
        "abstain_no_supported_alternative",
        tuple(dict.fromkeys(reasons))[:maximum_proofs] or ("no_single_compact_cluster_exposes_coherent_exit_return",),
    )
