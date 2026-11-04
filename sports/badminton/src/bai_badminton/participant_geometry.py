"""Opt-in body context between fresh detections from one participant episode.

This provider estimates box and floor-foot geometry only. It neither detects a
racket contact nor identifies a named player. Callers must keep these estimates
separate from model observations and retain the two canonical source frames.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from bai_badminton.observations import WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot, has_target_court_provenance

METHOD = "same_episode_detector_bracket_v1"


@dataclass(frozen=True)
class GeometryBracketPolicy:
    max_span_s: float = 0.2
    max_court_speed_m_s: float = 12.0
    max_scale_ratio: float = 1.5
    min_proximity: float = 0.05
    relative_gap: float = 0.05

    def __post_init__(self) -> None:
        values = (self.max_span_s, self.max_court_speed_m_s, self.max_scale_ratio,
                  self.min_proximity, self.relative_gap)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("geometry policy values must be finite")
        if self.max_span_s <= 0 or self.max_court_speed_m_s <= 0 or self.max_scale_ratio < 1:
            raise ValueError("geometry span/speed must be positive and scale ratio at least one")
        if not 0 < self.min_proximity <= 1 or not 0 <= self.relative_gap < 1:
            raise ValueError("geometry proximity must be positive and relative gap below one")


@dataclass(frozen=True)
class ParticipantGeometryEstimate:
    participant_id: str
    track_id: int
    observation_id: str
    source_frames: tuple[int, int]
    bbox_estimate: tuple[float, float, float, float]
    court_xy_estimate: tuple[float, float]
    proximity: float
    position_kind: Literal["estimated"] = "estimated"
    contact_above_head: None = None


@dataclass(frozen=True)
class ParticipantGeometryResult:
    status: Literal["estimated", "unresolved"]
    frame: int
    reason: str
    estimate: ParticipantGeometryEstimate | None = None
    candidates: tuple[ParticipantGeometryEstimate, ...] = ()
    support: dict[str, float] = field(default_factory=dict)
    player_id: None = None
    method: str = METHOD
    version: str = "1"
    support_semantics: str = "uncalibrated_body_proximity"


def _valid_geometry(snapshot: ParticipantSnapshot) -> bool:
    try:
        box = np.asarray(snapshot.bbox, dtype=float)
        return bool(
            box.shape == (4,) and np.isfinite(box).all()
            and box[2] > box[0] and box[3] > box[1]
            and has_target_court_provenance(snapshot)
        )
    except (TypeError, ValueError):
        return False


def estimate_participant_geometry(
    window: WindowObs,
    frames: list[dict[str, ParticipantSnapshot]],
    index: int,
    *,
    match_format: str,
    geometry_valid: NDArray[np.bool_],
    identity_unresolved: NDArray[np.bool_],
    visible_counts: NDArray[np.int64],
    policy: GeometryBracketPolicy = GeometryBracketPolicy(),
) -> ParticipantGeometryResult:
    """Estimate all competitor boxes before selecting one provisional episode.

    Only an explicitly unscheduled detector frame is eligible. The closest
    scheduled observations on both sides must match every current competitor;
    a failed/unknown scheduled observation is a barrier, not a gap to skip.
    No state or input observation is modified. Coordinates use the canonical
    window's image pixels and badminton court metres; a floor foot estimate is
    not an airborne shuttle measurement.
    """
    n = window.n
    if (len(frames) != n or isinstance(index, bool) or not isinstance(index, (int, np.integer))
            or not 0 <= index < n or not math.isfinite(window.fps) or window.fps <= 0):
        raise ValueError("geometry observations and index must align with a positive-FPS window")
    for mask in (geometry_valid, identity_unresolved, window.replay):
        value = np.asarray(mask)
        if value.shape != (n,) or value.dtype != np.bool_:
            raise ValueError("geometry/replay/identity masks require one boolean per frame")
    counts = np.asarray(visible_counts)
    if counts.shape != (n,) or not np.issubdtype(counts.dtype, np.integer) or (counts < 0).any():
        raise ValueError("visible competitor counts require one nonnegative integer per frame")
    frame = int(window.frame0 + index)

    def unresolved(reason: str) -> ParticipantGeometryResult:
        return ParticipantGeometryResult("unresolved", frame, reason)

    expected = {"singles": 2, "doubles": 4}.get(match_format)
    if expected is None:
        return unresolved("format_not_confirmed")
    current = frames[index]
    if len(current) != expected or counts[index] != expected:
        return unresolved("incomplete_or_extra_competitors")
    if any(item.detector_observed is not False or item.detector_matched is not False
           for item in current.values()):
        return unresolved("current_detector_not_explicitly_skipped")
    shuttle = window.shuttle
    if (window.replay[index] or not shuttle.vis[index] or shuttle.interp[index]
            or not np.isfinite([shuttle.x[index], shuttle.y[index]]).all()):
        return unresolved("shuttle_not_observed")
    lo, hi = window.segment_bounds(index)
    ids = set(current)

    def anchor(direction: int) -> int | None:
        for position in range(index + direction, hi if direction == 1 else lo - 1, direction):
            if abs(position - index) / window.fps > policy.max_span_s:
                return None
            people = frames[position]
            if set(people) != ids or counts[position] != expected:
                return None
            # Any executed/unknown detector flag makes this the nearest barrier.
            if any(item.detector_observed is not False for item in people.values()):
                return position
        return None

    left, right = anchor(-1), anchor(1)
    if left is None or right is None:
        return unresolved("missing_detector_bracket")
    duration = (right - left) / window.fps
    if duration > policy.max_span_s:
        return unresolved("detector_bracket_too_wide")
    interval = slice(left, right + 1)
    if (not np.asarray(geometry_valid)[interval].all() or np.asarray(identity_unresolved)[interval].any()
            or window.replay[interval].any() or not (counts[interval] == expected).all()):
        return unresolved("invalid_bracket_context")
    identities = {pid: (item.track_id, item.observation_id) for pid, item in current.items()}
    if (any(not birth for _, birth in identities.values())
            or len({track for track, _ in identities.values()}) != expected
            or len({birth for _, birth in identities.values()}) != expected):
        return unresolved("ambiguous_episode_identity")
    for position in range(left, right + 1):
        people = frames[position]
        if set(people) != ids:
            return unresolved("incomplete_episode_bracket")
        for pid, item in people.items():
            if (item.track_id, item.observation_id) != identities[pid]:
                return unresolved("episode_changed_inside_bracket")
            if not _valid_geometry(item):
                return unresolved("invalid_competitor_geometry")
            if position in (left, right):
                if item.detector_observed is not True or item.detector_matched is not True:
                    return unresolved("bracket_detector_not_matched")
            elif item.detector_observed is not False or item.detector_matched is not False:
                return unresolved("interior_detector_not_explicitly_skipped")

    alpha = (index - left) / (right - left)
    estimates: list[ParticipantGeometryEstimate] = []
    for pid in sorted(ids):
        before, after = frames[left][pid], frames[right][pid]
        start_box, end_box = np.asarray(before.bbox, float), np.asarray(after.bbox, float)
        start_court, end_court = np.asarray(before.court_xy, float), np.asarray(after.court_xy, float)
        # Every retained/intermediate episode must stay on its observed court side.
        sides = [float(frames[position][pid].court_xy[1]) for position in range(left, right + 1)]
        if any(side == 0 or math.copysign(1, side) != math.copysign(1, sides[0]) for side in sides):
            return unresolved("court_side_changed_inside_bracket")
        if float(np.linalg.norm(end_court - start_court)) / duration > policy.max_court_speed_m_s:
            return unresolved("implausible_court_motion")
        dimensions = np.stack([start_box[2:] - start_box[:2], end_box[2:] - end_box[:2]])
        if (dimensions.max(axis=0) / dimensions.min(axis=0) > policy.max_scale_ratio).any():
            return unresolved("implausible_body_scale_change")
        box = start_box + alpha * (end_box - start_box)
        court = start_court + alpha * (end_court - start_court)
        height = box[3] - box[1]
        # Same upper-box cue as contact_fusion_v2, with no synthesized wrist/pose.
        body_point = ((box[0] + box[2]) / 2, box[1] + 0.15 * height)
        distance = math.hypot(shuttle.x[index] - body_point[0], shuttle.y[index] - body_point[1]) / height
        proximity = math.exp(-distance / 0.45)
        estimates.append(ParticipantGeometryEstimate(
            participant_id=pid, track_id=int(before.track_id), observation_id=str(before.observation_id),
            source_frames=(int(window.frame0 + left), int(window.frame0 + right)),
            bbox_estimate=tuple(float(value) for value in box),
            court_xy_estimate=tuple(float(value) for value in court), proximity=proximity,
        ))
    ranked = sorted(estimates, key=lambda item: (-item.proximity, item.participant_id))
    best = ranked[0]
    runner_up = ranked[1].proximity
    relative_gap = (best.proximity - runner_up) / best.proximity if best.proximity else 0.0
    support = {"proximity": best.proximity, "proximity_runner_up": runner_up,
               "proximity_relative_gap": relative_gap, "proximity_minimum_threshold": policy.min_proximity,
               "proximity_relative_gap_threshold": policy.relative_gap}
    if best.proximity < policy.min_proximity or relative_gap <= policy.relative_gap:
        return ParticipantGeometryResult("unresolved", frame, "insufficient_or_ambiguous_body_proximity",
                                         candidates=tuple(ranked), support=support)
    return ParticipantGeometryResult("estimated", frame, "unique_body_proximity_from_detector_bracket",
                                     estimate=best, candidates=tuple(ranked), support=support)
