"""Causal co-observation of competing shuttle hypotheses.

A compact peak repeatedly co-observed with a different moving selection cannot
silently become the same airborne object's landing. It remains ambiguous when
it later wins the heatmap. This is an association support rule, not a calibrated
object classifier. Real floor objects without contradictory co-observation are
retained. Forecast coordinates and physical contact decisions are never emitted.
"""

from __future__ import annotations

import copy
from collections import deque
from dataclasses import asdict, dataclass, field
from itertools import pairwise
from math import ceil, isfinite
from typing import Any

import numpy as np

from bai_badminton.perception.diagnostics import MAX_CANDIDATES, HeatmapCandidate, ShuttleDiagnostic
from bai_badminton.perception.shuttle_post import MAX_FILL_SPEED

ASSOCIATION_SCHEMA = "badminton-shuttle-association:v2"
ASSOCIATION_METHOD = "coobserved-static-hypotheses-v1"


def _point(value: Any) -> tuple[float, float] | None:
    if value is None:
        return None
    if len(value) != 2 or any(type(v) not in (int, float) or not isfinite(v) for v in value):
        raise ValueError("association coordinates must be finite image-pixel pairs")
    return float(value[0]), float(value[1])


@dataclass(frozen=True, slots=True)
class ShuttleObservationEvidence:
    frame_idx: int
    epoch: int
    status: str
    association_status: str
    raw_xy: tuple[float, float] | None
    selected_xy: tuple[float, float] | None
    raw_model_support: float
    candidates: tuple[HeatmapCandidate, ...] = ()
    competing_motion_frames: tuple[int, ...] = ()
    hypothesis_id: int | None = None
    coordinate_basis: str = "analysis_image_pixels"
    reasons: tuple[str, ...] = ()
    method: str = ASSOCIATION_METHOD
    support_semantics: str = "association_support_not_calibrated_probability"
    schema: str = ASSOCIATION_SCHEMA
    association_coordinate_basis: str = "analysis_image_pixels"

    def __post_init__(self) -> None:
        if self.schema != ASSOCIATION_SCHEMA or self.method != ASSOCIATION_METHOD:
            raise ValueError("unsupported shuttle association schema/method")
        if type(self.frame_idx) is not int or self.frame_idx < 0 or type(self.epoch) is not int or self.epoch < 0:
            raise ValueError("association requires canonical frame and epoch identity")
        if self.status not in {"observed", "ambiguous", "missing", "invalid"}:
            raise ValueError("invalid shuttle observation status")
        if self.association_status not in {"tracked", "static_candidate", "reacquisition", "unknown", "rejected"}:
            raise ValueError("invalid association status")
        raw, selected = _point(self.raw_xy), _point(self.selected_xy)
        if self.status == "observed":
            if raw is None or selected != raw:
                raise ValueError("association may emit only the fresh input coordinate")
        elif selected is not None:
            raise ValueError("ambiguous/missing/invalid association cannot emit a coordinate")
        if self.status == "missing" and raw is not None:
            raise ValueError("a physically recorded input must not be labelled missing")
        if self.status == "ambiguous" and raw is None:
            raise ValueError("ambiguous selection requires its retained raw observation")
        if type(self.raw_model_support) not in (int, float) or not isfinite(self.raw_model_support):
            raise ValueError("association requires finite raw model support")
        if len(self.candidates) > MAX_CANDIDATES or len(self.competing_motion_frames) > 8:
            raise ValueError("association evidence exceeds its bounded hypothesis budget")
        if any(type(f) is not int or not 0 <= f < self.frame_idx for f in self.competing_motion_frames):
            raise ValueError("competing motion proof must precede the current frame")
        if self.support_semantics != "association_support_not_calibrated_probability":
            raise ValueError("association support is not a calibrated probability")
        if self.coordinate_basis != "analysis_image_pixels":
            raise ValueError("raw and selected coordinates must remain analysis-image pixels")
        if self.association_coordinate_basis not in {"analysis_image_pixels", "registered_reference_pixels"}:
            raise ValueError("unknown association coordinate basis")
        object.__setattr__(self, "raw_xy", raw)
        object.__setattr__(self, "selected_xy", selected)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ShuttleObservationEvidence:
        row = dict(value)
        candidates = []
        for item in row.get("candidates", ()):
            item = dict(item)
            item["peak_xy"], item["centroid_xy"] = tuple(item["peak_xy"]), tuple(item["centroid_xy"])
            candidates.append(HeatmapCandidate(**item))
        row["candidates"] = tuple(candidates)
        row["competing_motion_frames"] = tuple(row.get("competing_motion_frames", ()))
        row["reasons"] = tuple(row.get("reasons", ()))
        return cls(**row)


@dataclass
class _Hypothesis:
    identity: int
    samples: deque[tuple[int, float, float, float]]
    witnesses: deque[int] = field(default_factory=lambda: deque(maxlen=8))

    @property
    def last_frame(self) -> int:
        return self.samples[-1][0]

    def descriptor(self) -> tuple[np.ndarray, float]:
        points = np.asarray([(x, y) for _, x, y, _ in self.samples])
        return np.median(points, axis=0), float(np.median([s for _, _, _, s in self.samples]))

    def compact(self, minimum_samples: int) -> bool:
        if len(self.samples) < minimum_samples:
            return False
        centre, spread = self.descriptor()
        # Use the actual component's spatial mass spread, not a radius fitted
        # to a court marking. This is a sensitivity scale, not Gaussian error.
        return all(float(np.hypot(x - centre[0], y - centre[1])) <= spread for _, x, y, _ in self.samples)


class CausalShuttleAssociation:
    """Bounded concurrent candidate memory, with explicit lifecycle and abstention.

    Movement uses the existing rally start-speed convention. Static support
    requires ten samples and three independently co-observed moving selections;
    no stationary point is rejected merely for being slow. The optional image
    transform is current-frame registration, never stale floor projection.
    """

    def __init__(
        self,
        *,
        fps: float,
        maximum_tracks: int = 32,
        minimum_motion_px_per_frame: float = 3.0,
        stationary_samples: int = 10,
        witness_samples: int = 3,
    ) -> None:
        if not isfinite(fps) or fps <= 0 or type(maximum_tracks) is not int or not 1 <= maximum_tracks <= 64:
            raise ValueError("invalid association frame rate or hypothesis budget")
        if not isfinite(minimum_motion_px_per_frame) or minimum_motion_px_per_frame <= 0:
            raise ValueError("association motion sensitivity must be positive")
        if type(stationary_samples) is not int or not 3 <= stationary_samples <= 120:
            raise ValueError("invalid static observation budget")
        if type(witness_samples) is not int or not 3 <= witness_samples <= 8:
            raise ValueError("invalid co-observation witness budget")
        self.fps, self.maximum_tracks = fps, maximum_tracks
        self.minimum_motion_px_per_frame = minimum_motion_px_per_frame
        self.stationary_samples, self.witness_samples = stationary_samples, witness_samples
        self.history_frames = max(stationary_samples, min(120, ceil(fps)))
        self.maximum_age_frames = ceil(2 * fps)
        self._owner = object()
        self.reset()

    @property
    def retained_tracks(self) -> int:
        return len(self._tracks)

    @property
    def retained_samples(self) -> int:
        return sum(len(track.samples) for track in self._tracks)

    def reset(self) -> None:
        self._tracks: list[_Hypothesis] = []
        self._primary: deque[tuple[int, np.ndarray]] = deque(maxlen=4)
        self._last_frame: int | None = None
        self._context: tuple[int, bool] | None = None
        self._next_id = 0
        self._unavailable = False

    def checkpoint(self) -> tuple[object, dict[str, Any]]:
        return self._owner, copy.deepcopy({k: v for k, v in self.__dict__.items() if k != "_owner"})

    def restore(self, checkpoint: object) -> None:
        if not isinstance(checkpoint, tuple) or len(checkpoint) != 2 or checkpoint[0] is not self._owner:
            raise ValueError("incompatible association checkpoint")
        state = copy.deepcopy(checkpoint[1])
        self.__dict__.update(state)

    def close(self) -> None:
        self.reset()

    def update(
        self,
        frame: int,
        *,
        epoch: int,
        raw_xy: tuple[float, float] | None,
        raw_support: float,
        diagnostic: ShuttleDiagnostic | None,
        image_valid: bool,
        image_to_reference: np.ndarray | None = None,
    ) -> ShuttleObservationEvidence:
        raw = _point(raw_xy)
        if type(frame) is not int or frame < 0 or type(epoch) is not int or epoch < 0:
            raise ValueError("canonical association identity is required")
        if type(image_valid) is not bool or not isfinite(raw_support):
            raise ValueError("association validity and raw support are required")
        if self._last_frame is not None and frame <= self._last_frame:
            raise ValueError("association requires increasing frame order or explicit rollback")
        transform = None
        if image_to_reference is not None:
            transform = np.asarray(image_to_reference, dtype=float)
            if transform.shape != (3, 3) or not np.isfinite(transform).all() or abs(np.linalg.det(transform)) < 1e-12:
                raise ValueError("association registration must be finite and invertible")

        def mapped(point: tuple[float, float]) -> np.ndarray:
            if transform is None:
                return np.asarray(point, dtype=float)
            out = transform @ np.r_[point, 1.0]
            if abs(out[2]) < 1e-12:
                raise ValueError("association registration maps a point to infinity")
            return out[:2] / out[2]

        context = epoch, transform is not None
        if self._context != context or (self._last_frame is not None and frame != self._last_frame + 1):
            self.reset()
        self._context, self._last_frame = context, frame
        basis = "registered_reference_pixels" if transform is not None else "analysis_image_pixels"
        candidates = diagnostic.candidates if diagnostic is not None else ()

        def result(status: str, association: str, *, proof: _Hypothesis | None = None, reason: str):
            return ShuttleObservationEvidence(
                frame,
                epoch,
                status,
                association,
                raw,
                raw if status == "observed" else None,
                raw_support,
                candidates,
                tuple(f for f in proof.witnesses if f < frame) if proof else (),
                proof.identity if proof else None,
                "analysis_image_pixels",
                (reason,),
                association_coordinate_basis=basis,
            )

        if not image_valid:
            self._tracks.clear()
            self._primary.clear()
            self._unavailable = True
            return result("invalid", "rejected", reason="image_view_invalid")
        self._tracks = [t for t in self._tracks if frame - t.last_frame <= self.maximum_age_frames]
        if diagnostic is None:
            self._tracks.clear()
            self._primary.clear()
            self._unavailable = True
            return result("observed" if raw else "missing", "unknown", reason="candidate_evidence_unavailable")
        for track in self._tracks:
            while track.samples and frame - track.samples[0][0] > self.history_frames:
                track.samples.popleft()
            while track.witnesses and frame - track.witnesses[0] > self.maximum_age_frames:
                track.witnesses.popleft()
        self._tracks = [track for track in self._tracks if track.samples]
        allowed = [c for c in candidates if c.mask_allows_peak and c.peak_support > 0]
        candidate_points = [mapped(c.peak_xy) for c in allowed]

        def mapped_spread(candidate: HeatmapCandidate, point: np.ndarray) -> float:
            spread = max(candidate.spread_px, 1e-6)
            if transform is None:
                return spread
            return max(
                float(np.linalg.norm(mapped((candidate.peak_xy[0] + spread, candidate.peak_xy[1])) - point)),
                float(np.linalg.norm(mapped((candidate.peak_xy[0], candidate.peak_xy[1] + spread)) - point)),
                1e-6,
            )

        candidate_spreads = [mapped_spread(c, point) for c, point in zip(allowed, candidate_points, strict=True)]
        pairs = []
        for ci, point in enumerate(candidate_points):
            for ti, track in enumerate(self._tracks):
                centre, spread = track.descriptor()
                scale = candidate_spreads[ci]
                distance = float(np.linalg.norm(point - centre))
                radius = float(np.hypot(spread, max(scale, 1e-6)))
                if distance <= radius:
                    pairs.append((distance / radius, ci, ti))
        assigned: dict[int, _Hypothesis] = {}
        used = set()
        for _, ci, ti in sorted(pairs):
            if ci not in assigned and ti not in used:
                assigned[ci] = self._tracks[ti]
                used.add(ti)
        for ci, point in enumerate(candidate_points):
            track = assigned.get(ci)
            if track is None:
                if len(self._tracks) >= self.maximum_tracks:
                    replaceable = [t for t in self._tracks if t not in assigned.values()]
                    if not replaceable:
                        continue
                    self._tracks.remove(min(replaceable, key=lambda t: (t.last_frame, t.identity)))
                track = _Hypothesis(self._next_id, deque(maxlen=self.history_frames))
                self._next_id += 1
                self._tracks.append(track)
                assigned[ci] = track
            spread = candidate_spreads[ci]
            track.samples.append((frame, float(point[0]), float(point[1]), spread))
        selected = None
        if raw is not None and diagnostic.selected_masked_peak_xy is not None:
            target = mapped(diagnostic.selected_masked_peak_xy)
            distances = [(float(np.linalg.norm(point - target)), ci) for ci, point in enumerate(candidate_points)]
            if distances:
                distance, ci = min(distances)
                if distance <= candidate_spreads[ci]:
                    selected = assigned.get(ci)
        if (
            selected is not None
            and selected.compact(self.stationary_samples)
            and len(selected.witnesses) >= self.witness_samples
        ):
            self._primary.clear()
            self._unavailable = True
            return result(
                "ambiguous", "static_candidate", proof=selected, reason="coobserved_competing_static_hypothesis"
            )
        if raw is None:
            self._primary.clear()
            self._unavailable = True
            return result("missing", "unknown", reason="no_accepted_raw_observation")
        point = mapped(raw)
        self._primary.append((frame, point))
        if len(self._primary) == 4 and self._primary[-1][0] - self._primary[0][0] == 3:
            displacement = float(np.linalg.norm(self._primary[-1][1] - self._primary[0][1])) / 3
            steps = [b[1] - a[1] for a, b in pairwise(self._primary)]
            speeds = np.asarray([np.linalg.norm(step) for step in steps])
            # Three moving, directionally compatible observations are required.
            # One jump between competing peaks cannot certify a separate flight.
            coherent = (
                bool((speeds > self.minimum_motion_px_per_frame).all())
                and bool((speeds <= MAX_FILL_SPEED).all())
                and all(float(np.dot(a, b)) > 0 for a, b in pairwise(steps))
            )
            if coherent and displacement > self.minimum_motion_px_per_frame:
                for ci, track in assigned.items():
                    if track is selected:
                        continue
                    other = candidate_points[ci]
                    if float(np.linalg.norm(other - point)) > candidate_spreads[ci]:
                        track.witnesses.append(frame)
        state = "reacquisition" if self._unavailable else "tracked"
        self._unavailable = False
        return result("observed", state, reason="fresh_selection_retained")
