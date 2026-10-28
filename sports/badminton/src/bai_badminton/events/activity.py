"""Conservative, bounded temporal activity hypotheses from visual observations.

This layer describes observed activity, never whether an exchange is a match.
Frame inputs are tri-state: ``None`` means unavailable, not an absent object.
``absence_verified`` must be supplied by an independent reliable source; an
empty detector result alone is not proof that a shuttle is absent.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum
from itertools import pairwise
from math import isfinite


class ActivityState(StrEnum):
    UNKNOWN = "unknown"
    REACQUIRING = "reacquiring"
    RALLY = "rally"
    ACTIVE_PLAY = "active_play"
    INACTIVE = "inactive"


@dataclass(frozen=True)
class ActivityObservation:
    frame_idx: int
    view_valid: bool
    person_count: int | None = None
    moving: bool | None = None
    shuttle_visible: bool | None = None
    # Must come from a credible existing rally observation, not serve formation.
    rally_observed: bool = False
    # Strongly verified absence, not merely a detector miss.
    absence_verified: bool = False
    # Normalized image position from a visible, court-filtered shuttle detection.
    shuttle_position: tuple[float, float] | None = None


@dataclass(frozen=True)
class ActivityEstimate:
    frame_idx: int
    state: ActivityState
    basis: str
    # Fraction of the analysis window with required observations; not calibrated probability.
    evidence_coverage: float
    match_intent: str = "unknown"
    version: str = "temporal_activity_v3"


@dataclass(frozen=True)
class ActivityInterval:
    start_frame: int
    end_frame: int
    state: ActivityState
    basis: str
    evidence_coverage: float
    match_intent: str = "unknown"
    version: str = "temporal_activity_v3"


class ActivityTracker:
    """Emit non-overlapping intervals, with a fixed-size window and transition hold.

    Every input must be one decoded frame in increasing order. A gap ends the
    current interval and clears accumulated evidence, so stale activity cannot
    span missing frames. A caller must immediately consume each returned closed
    interval; no unbounded list of outputs is retained.
    """

    def __init__(self, fps: float, *, window_s: float = 2.0, hold_s: float = 1.0) -> None:
        if fps <= 0 or window_s <= 0 or hold_s <= 0:
            raise ValueError("fps, window_s, and hold_s must be positive")
        self.fps = fps
        self.window_frames = max(2, round(fps * window_s))
        self.hold_frames = max(1, round(fps * hold_s))
        self._window: deque[ActivityObservation] = deque(maxlen=self.window_frames)
        self._last: int | None = None
        self._start: int | None = None
        self._state = ActivityState.UNKNOWN
        self._basis = "insufficient"
        self._coverage = 0.0
        self._pending: ActivityState | None = None
        self._pending_frames = 0
        self._finished = False

    def _close(self, end: int) -> ActivityInterval | None:
        if self._start is None or end < self._start:
            return None
        return ActivityInterval(self._start, end, self._state, self._basis, self._coverage)

    def _candidate(self) -> tuple[ActivityState, str, float]:
        if len(self._window) < self.window_frames:
            return ActivityState.UNKNOWN, "insufficient", len(self._window) / self.window_frames
        samples = list(self._window)
        people = sum(s.person_count is not None and s.person_count >= 2 for s in samples)
        moving = sum(s.person_count is not None and s.person_count >= 2 and s.moving is True for s in samples)
        shuttle = sum(s.shuttle_visible is True for s in samples)
        rally = sum(s.rally_observed for s in samples)
        quiet = sum(
            s.person_count is not None
            and s.person_count >= 2
            and s.moving is False
            and s.shuttle_visible is False
            and s.absence_verified
            for s in samples
        )
        required = max(1, (3 * self.window_frames + 3) // 4)
        if rally >= required:
            return ActivityState.RALLY, "rally_observation", rally / self.window_frames
        # Visible stationary objects or one spurious shuttle detection cannot
        # establish play, even when people are walking nearby. Require several
        # valid observations whose motion survives removal of one outlier.
        trajectory = [
            (s.frame_idx, s.shuttle_position)
            for s in samples
            if s.shuttle_visible is True
            and s.shuttle_position is not None
            and len(s.shuttle_position) == 2
            and all(isfinite(v) and 0.0 <= v <= 1.0 for v in s.shuttle_position)
        ]
        if people >= required and moving >= required and len(trajectory) >= 4:
            first, last = trajectory[0][0], trajectory[-1][0]
            xs = sorted(position[0] for _, position in trajectory)
            ys = sorted(position[1] for _, position in trajectory)
            # The second extrema bound the span even if one point is bogus.
            displacement = max(xs[-2] - xs[1], ys[-2] - ys[1])
            # Require at least two temporally plausible moving steps; abrupt
            # jumps between far-away blobs do not form a credible trajectory.
            moving_steps = 0
            for (f0, p0), (f1, p1) in pairwise(trajectory):
                speed = max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])) * self.fps / (f1 - f0)
                if 0.005 <= speed <= 0.8:
                    moving_steps += 1
            if last - first >= max(2, self.window_frames // 4) and displacement >= 0.015 and moving_steps >= 2:
                basis = "movement_and_shuttle" if shuttle >= required else "sparse_shuttle_trajectory_and_movement"
                return (ActivityState.ACTIVE_PLAY, basis, min(people, moving, len(trajectory)) / self.window_frames)
        if quiet >= required:
            return ActivityState.INACTIVE, "observed_low_motion", quiet / self.window_frames
        return ActivityState.UNKNOWN, "insufficient", min(people, moving + quiet) / self.window_frames

    def update(self, observation: ActivityObservation) -> tuple[ActivityEstimate, ActivityInterval | None]:
        if self._finished:
            raise ValueError("tracker was flushed")
        if observation.frame_idx < 0 or (self._last is not None and observation.frame_idx <= self._last):
            raise ValueError("frame indices must be nonnegative and strictly increasing")
        if observation.person_count is not None and observation.person_count < 0:
            raise ValueError("person count must be nonnegative")
        frame = observation.frame_idx
        closed = None
        if self._last is not None and frame != self._last + 1:
            closed = self._close(self._last)
            self._window.clear()
            self._state = ActivityState.UNKNOWN
            self._basis = "frame_gap"
            self._coverage = 0.0
            self._start = frame
            self._pending = None
            self._pending_frames = 0
        if self._start is None:
            self._start = frame
        if not observation.view_valid:
            self._window.clear()
            self._pending = None
            self._pending_frames = 0
            candidate, basis, coverage = ActivityState.REACQUIRING, "view_unavailable", 0.0
        else:
            self._window.append(observation)
            candidate, basis, coverage = self._candidate()
        # Unknown and loss are immediate; positive states require persistence.
        if candidate != self._state and candidate not in (ActivityState.UNKNOWN, ActivityState.REACQUIRING):
            if self._pending == candidate:
                self._pending_frames += 1
            else:
                self._pending, self._pending_frames = candidate, 1
            if self._pending_frames < self.hold_frames:
                candidate, basis, coverage = self._state, self._basis, self._coverage
        else:
            self._pending, self._pending_frames = None, 0
        if candidate != self._state:
            # A frame-gap may already have closed an interval; no other interval
            # exists before the current frame in that case.
            if closed is None and self._last is not None:
                closed = self._close(self._last)
            self._start = frame
            self._state = candidate
            self._pending, self._pending_frames = None, 0
        self._basis, self._coverage = basis, coverage
        self._last = frame
        return ActivityEstimate(frame, self._state, basis, coverage), closed

    def flush(self) -> ActivityInterval | None:
        if self._finished:
            return None
        self._finished = True
        return self._close(self._last) if self._last is not None else None
