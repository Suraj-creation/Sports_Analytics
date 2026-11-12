"""Causal observed-motion requests for configured perception sampling rates.

This carries acquisition evidence only. It neither declares sporting activity nor
changes contact/rally authority. Call ``observe`` after registered association,
then ``complete_chunk`` only when that entire chunk has completed successfully.
Only a later chunk may request the resulting bounded sampling lease. The caller
must cancel an applied request at any camera/content/view/geometry invalidation.
"""

from __future__ import annotations

import copy
from collections import deque
from dataclasses import asdict, dataclass, fields
from itertools import pairwise
from math import hypot, isfinite

MOTION_ACQUISITION_VERSION = "observed-motion-acquisition:v1"


def _identity(value: int, name: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a canonical nonnegative integer")


@dataclass(frozen=True, slots=True)
class MotionAcquisitionProof:
    """Four actual selected observations supporting one chunk-start request."""

    decision_frame: int
    completed_chunk_start: int
    completed_chunk_end: int
    source_frames: tuple[int, int, int, int]
    reference_xy: tuple[tuple[float, float], ...]
    epoch: int
    minimum_motion_px_per_frame: float
    maximum_age_frames: int
    coordinate_basis: str = "registered_reference_pixels"
    authority: str = "configured_sampling_request_only"
    version: str = MOTION_ACQUISITION_VERSION

    def __post_init__(self) -> None:
        for name in ("decision_frame", "completed_chunk_start", "completed_chunk_end", "epoch"):
            _identity(getattr(self, name), name)
        if not (
            self.completed_chunk_start <= self.completed_chunk_end
            and self.completed_chunk_end + 1 == self.decision_frame
        ):
            raise ValueError("sampling evidence must come from a previously completed chunk")
        if type(self.source_frames) is not tuple or len(self.source_frames) != 4:
            raise ValueError("motion acquisition requires four source frames")
        for frame in self.source_frames:
            _identity(frame, "source frame")
        if any(b != a + 1 for a, b in pairwise(self.source_frames)):
            raise ValueError("motion acquisition source frames must be consecutive")
        if not 0 <= self.source_frames[0] <= self.source_frames[-1] <= self.completed_chunk_end:
            raise ValueError("motion source cannot be current or future data")
        if type(self.maximum_age_frames) is not int or self.maximum_age_frames <= 0:
            raise ValueError("a positive existing association age bound is required")
        if self.decision_frame - self.source_frames[-1] > self.maximum_age_frames:
            raise ValueError("motion acquisition proof has expired")
        if (
            type(self.minimum_motion_px_per_frame) not in (int, float)
            or not isfinite(self.minimum_motion_px_per_frame)
            or self.minimum_motion_px_per_frame <= 0
        ):
            raise ValueError("a positive existing association motion bound is required")
        if type(self.reference_xy) is not tuple:
            raise ValueError("motion coordinates must be an immutable tuple")
        points = tuple(_point(point) for point in self.reference_xy)
        if len(points) != 4 or not _coherent(points, self.minimum_motion_px_per_frame):
            raise ValueError("motion acquisition requires coherent observed displacement")
        object.__setattr__(self, "reference_xy", points)
        if (
            self.coordinate_basis != "registered_reference_pixels"
            or self.authority != "configured_sampling_request_only"
            or self.version != MOTION_ACQUISITION_VERSION
        ):
            raise ValueError("unsupported acquisition evidence contract")


    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict) -> MotionAcquisitionProof:
        expected = {item.name for item in fields(cls)}
        if type(value) is not dict or set(value) != expected:
            raise ValueError("acquisition proof requires its exact versioned fields")
        data = dict(value)
        if not isinstance(data["source_frames"], (list, tuple)) or not isinstance(
            data["reference_xy"], (list, tuple)
        ):
            raise ValueError("acquisition proof requires source and point arrays")
        data["source_frames"] = tuple(data["source_frames"])
        data["reference_xy"] = tuple(_point(point) for point in data["reference_xy"])
        return cls(**data)


def _point(value: object) -> tuple[float, float]:
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError("registered coordinates must be finite pixel pairs")
    if any(type(v) not in (int, float) or not isfinite(v) for v in value):
        raise ValueError("registered coordinates must be finite pixel pairs")
    return float(value[0]), float(value[1])


def _coherent(points: tuple[tuple[float, float], ...], minimum: float) -> bool:
    steps = tuple((b[0] - a[0], b[1] - a[1]) for a, b in pairwise(points))
    return (
        all(hypot(*step) > minimum for step in steps)
        and all(a[0] * b[0] + a[1] * b[1] > 0 for a, b in pairwise(steps))
        and hypot(points[-1][0] - points[0][0], points[-1][1] - points[0][1]) / 3 > minimum
    )


class ObservedMotionAcquisition:
    """Bounded acquisition-only state, independent of participants and format.

    ``reference_xy`` must be the fresh selected NN observation transformed into
    the stable reference-image basis. ``observed=False`` covers missing, carried,
    reconstructed, rejected and ambiguous observations; it breaks the run without
    renewing an earlier proof. Invalid view/geometry/context and epoch changes
    revoke all evidence. No coordinates are predicted or reconstructed here.
    """

    def __init__(self, *, minimum_motion_px_per_frame: float, maximum_age_frames: int) -> None:
        if (
            type(minimum_motion_px_per_frame) not in (int, float)
            or not isfinite(minimum_motion_px_per_frame)
            or minimum_motion_px_per_frame <= 0
        ):
            raise ValueError("a positive existing association motion bound is required")
        if type(maximum_age_frames) is not int or maximum_age_frames <= 0:
            raise ValueError("a positive existing association age bound is required")
        self.minimum_motion_px_per_frame = float(minimum_motion_px_per_frame)
        self.maximum_age_frames = maximum_age_frames
        self._owner = object()
        self.reset()

    def reset(self) -> None:
        self._run: deque[tuple[int, tuple[float, float]]] = deque(maxlen=4)
        self._candidate: tuple[tuple[int, ...], tuple[tuple[float, float], ...], int] | None = None
        self._published: tuple[tuple[int, ...], tuple[tuple[float, float], ...], int] | None = None
        self._epoch: int | None = None
        self._last_frame: int | None = None
        self._completed: tuple[int, int] | None = None
        self._pending_first: int | None = None

    def _revoke(self) -> None:
        self._run.clear()
        self._candidate = None
        self._published = None

    def observe(
        self,
        frame_idx: int,
        epoch: int,
        reference_xy: tuple[float, float] | None,
        *,
        context_valid: bool,
        observed: bool,
    ) -> None:
        _identity(frame_idx, "frame")
        _identity(epoch, "epoch")
        if type(context_valid) is not bool or type(observed) is not bool:
            raise ValueError("explicit context and observation validity are required")
        if self._last_frame is not None and frame_idx <= self._last_frame:
            raise ValueError("acquisition observations must be strictly chronological")
        point = _point(reference_xy) if reference_xy is not None else None
        if observed and point is None:
            raise ValueError("observed motion requires an actual selected coordinate")
        if self._pending_first is None:
            self._pending_first = frame_idx
        if self._epoch != epoch or not context_valid:
            self._revoke()
        if self._last_frame is not None and frame_idx != self._last_frame + 1:
            self._revoke()
        self._epoch, self._last_frame = epoch, frame_idx
        if not context_valid or not observed:
            self._run.clear()
            return
        self._run.append((frame_idx, point))
        if len(self._run) == 4:
            frames, points = zip(*self._run, strict=True)
            if _coherent(points, self.minimum_motion_px_per_frame):
                self._candidate = frames, points, epoch

    def complete_chunk(self, start_frame: int, end_frame: int) -> None:
        """Publish after successful completion; chunks and observations cannot overlap."""
        _identity(start_frame, "chunk start")
        _identity(end_frame, "chunk end")
        if (
            start_frame > end_frame
            or self._pending_first != start_frame
            or self._last_frame != end_frame
            or (self._completed is not None and start_frame <= self._completed[1])
        ):
            raise ValueError("completion must bind the exact pending chronological chunk")
        self._completed = start_frame, end_frame
        self._published = self._candidate
        self._pending_first = None

    def request(self, current_chunk_start: int, current_epoch: int) -> MotionAcquisitionProof | None:
        """Decide once at the next chunk start, without renewing the source lease."""
        _identity(current_chunk_start, "decision frame")
        _identity(current_epoch, "epoch")
        if self._pending_first is not None:
            raise ValueError("sampling cannot consume an incomplete chunk")
        if self._completed is None:
            return None
        if current_chunk_start <= self._completed[1]:
            raise ValueError("sampling decision must follow the completed chunk")
        if current_chunk_start != self._completed[1] + 1:
            self._revoke()
            return None
        if current_epoch != self._epoch:
            self._revoke()
            self._epoch = current_epoch
            return None
        if self._published is None:
            return None
        frames, points, epoch = self._published
        if current_chunk_start - frames[-1] > self.maximum_age_frames:
            self._revoke()
            return None
        return MotionAcquisitionProof(
            decision_frame=current_chunk_start,
            completed_chunk_start=self._completed[0],
            completed_chunk_end=self._completed[1],
            source_frames=frames,
            reference_xy=points,
            epoch=epoch,
            minimum_motion_px_per_frame=self.minimum_motion_px_per_frame,
            maximum_age_frames=self.maximum_age_frames,
        )

    def checkpoint(self) -> tuple[object, dict]:
        return self._owner, copy.deepcopy({k: v for k, v in self.__dict__.items() if k != "_owner"})

    def restore(self, checkpoint: object) -> None:
        if not isinstance(checkpoint, tuple) or len(checkpoint) != 2 or checkpoint[0] is not self._owner:
            raise ValueError("incompatible acquisition checkpoint")
        self.__dict__.update(copy.deepcopy(checkpoint[1]))
