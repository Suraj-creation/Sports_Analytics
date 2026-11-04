"""Bounded diagnostic values; no observation or calibrated probability is created.

Heatmap summaries are computed after the unchanged decoder has made its choice.
The schema is independent of providers that only implement the legacy port.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any

import cv2
import numpy as np

DIAGNOSTIC_SCHEMA = "badminton-perception-diagnostics:v1"
MAX_DIAGNOSTIC_FRAMES = 3600
MAX_CANDIDATES = 8


def _copy_bounded_json(value: Any, depth: int = 0, budget: list[int] | None = None) -> Any:
    """Detach finite JSON values with explicit per-frame storage/work bounds."""
    budget = [512] if budget is None else budget
    budget[0] -= 1
    if budget[0] < 0 or depth > 6:
        raise ValueError("player diagnostics exceed the bounded JSON budget")
    if value is None or type(value) is bool:
        return value
    if type(value) in (int, float):
        if not isfinite(value):
            raise ValueError("player diagnostics require finite numeric values")
        return value
    if isinstance(value, str):
        if len(value) > 160:
            raise ValueError("player diagnostic text exceeds its bound")
        return value
    if isinstance(value, (list, tuple)):
        if len(value) > MAX_CANDIDATES:
            raise ValueError("player diagnostic lists exceed the candidate bound")
        return [_copy_bounded_json(item, depth + 1, budget) for item in value]
    if isinstance(value, dict):
        if len(value) > 32 or any(not isinstance(key, str) or len(key) > 64 for key in value):
            raise ValueError("invalid bounded player diagnostic mapping")
        return {key: _copy_bounded_json(item, depth + 1, budget) for key, item in value.items()}
    raise ValueError("player diagnostics must contain JSON values only")


@dataclass(frozen=True, slots=True)
class DiagnosticSelection:
    ranges: tuple[tuple[int, int], ...] = ()  # inclusive canonical frame indices
    top_k: int = 3
    candidate_floor: float = 0.1  # diagnostic support threshold, never an inference gate

    def __post_init__(self) -> None:
        if type(self.top_k) is not int or not 1 <= self.top_k <= MAX_CANDIDATES:
            raise ValueError("diagnostic top_k must be an integer in [1, 8]")
        if (
            type(self.candidate_floor) not in (int, float)
            or not isfinite(self.candidate_floor)
            or not 0 < self.candidate_floor <= 1
        ):
            raise ValueError("diagnostic candidate_floor must be finite in (0, 1]")
        previous = -1
        total = 0
        for bounds in self.ranges:
            if len(bounds) != 2 or any(type(i) is not int for i in bounds):
                raise ValueError("diagnostic ranges must contain integer frame pairs")
            first, last = bounds
            if not 0 <= first <= last or first <= previous:
                raise ValueError("diagnostic ranges must be sorted and disjoint")
            total += last - first + 1
            previous = last
        if total > MAX_DIAGNOSTIC_FRAMES:
            raise ValueError("diagnostic selection exceeds the 3600-frame budget")

    @classmethod
    def parse(cls, value: Any) -> DiagnosticSelection:
        if value is None:
            return cls()
        if not isinstance(value, dict) or value.keys() - {"ranges", "top_k", "candidate_floor"}:
            raise ValueError("unsupported diagnostic selection")
        ranges = value.get("ranges", [])
        if not isinstance(ranges, (list, tuple)) or any(not isinstance(v, (list, tuple)) for v in ranges):
            raise ValueError("diagnostic ranges must be frame pairs")
        return cls(tuple(tuple(v) for v in ranges), value.get("top_k", 3), value.get("candidate_floor", 0.1))

    def includes(self, frame: int) -> bool:
        return any(first <= frame <= last for first, last in self.ranges)


@dataclass(frozen=True, slots=True)
class HeatmapCandidate:
    rank: int
    peak_xy: tuple[float, float]  # analysis-image pixels
    centroid_xy: tuple[float, float]  # floor-component centroid; not the production centroid
    peak_support: float  # raw uncalibrated model output
    area_cells: int
    spread_px: float
    mask_allows_peak: bool
    above_inference_threshold: bool
    selected_peak: bool

    def __post_init__(self) -> None:
        if type(self.rank) is not int or not 1 <= self.rank <= MAX_CANDIDATES:
            raise ValueError("invalid diagnostic candidate rank")
        if type(self.area_cells) is not int or self.area_cells < 1:
            raise ValueError("invalid diagnostic component area")
        if any(
            type(v) is not bool for v in (self.mask_allows_peak, self.above_inference_threshold, self.selected_peak)
        ):
            raise ValueError("candidate admission flags must be booleans")
        if not all(isfinite(v) and v >= 0 for v in (self.peak_support, self.spread_px)):
            raise ValueError("invalid diagnostic candidate support/spread")
        for xy in (self.peak_xy, self.centroid_xy):
            if len(xy) != 2 or not all(isfinite(v) for v in xy):
                raise ValueError("invalid diagnostic candidate coordinates")


@dataclass(frozen=True, slots=True)
class ShuttleDiagnostic:
    candidates: tuple[HeatmapCandidate, ...]
    raw_peak: float
    masked_peak: float
    threshold: float
    candidate_floor: float
    reason: str
    window_votes: int
    background_sha256: str | None = None
    association: str = "global_max_component"
    support_semantics: str = "raw_model_support_uncalibrated"
    # Entropy of normalized positive heatmap mass is a descriptive statistic,
    # not entropy of a calibrated shuttle-location posterior.
    normalized_mass_entropy: float = 0.0
    selected_masked_peak_xy: tuple[float, float] | None = None
    decoded_xy: tuple[float, float] | None = None
    candidate_extraction: str = "top_k_components_above_diagnostic_floor"

    def __post_init__(self) -> None:
        if len(self.candidates) > MAX_CANDIDATES or [c.rank for c in self.candidates] != list(
            range(1, len(self.candidates) + 1)
        ):
            raise ValueError("unbounded or unordered diagnostic candidates")
        if type(self.window_votes) is not int or self.window_votes < 1:
            raise ValueError("invalid diagnostic window votes")
        if not all(
            isfinite(v)
            for v in (
                self.raw_peak,
                self.masked_peak,
                self.threshold,
                self.candidate_floor,
                self.normalized_mass_entropy,
            )
        ):
            raise ValueError("invalid diagnostic heatmap support")
        if (
            not 0 <= self.threshold <= 1
            or not 0 < self.candidate_floor <= 1
            or not 0 <= self.normalized_mass_entropy <= 1.0000001
        ):
            raise ValueError("invalid diagnostic thresholds/entropy")
        if self.reason not in {"accepted", "mask_rejected", "below_threshold", "no_positive_peak"}:
            raise ValueError("invalid heatmap diagnostic decision")
        if self.background_sha256 is not None and (
            len(self.background_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.background_sha256)
        ):
            raise ValueError("invalid diagnostic background digest")
        if self.association != "global_max_component" or self.support_semantics != "raw_model_support_uncalibrated":
            raise ValueError("unsupported diagnostic interpretation")
        if self.candidate_extraction != "top_k_components_above_diagnostic_floor":
            raise ValueError("unsupported diagnostic candidate extractor")
        for xy in (self.selected_masked_peak_xy, self.decoded_xy):
            if xy is not None and (len(xy) != 2 or not all(isfinite(v) for v in xy)):
                raise ValueError("invalid selected shuttle diagnostic coordinates")


@dataclass(frozen=True, slots=True)
class FrameDiagnostic:
    frame_idx: int
    canonical_time_sec: float
    shot_id: int
    view: str
    calibration_state: str | None
    shuttle: ShuttleDiagnostic | None
    acquisition_reason: str
    provider: str
    players: dict[str, Any] | None = None
    schema: str = DIAGNOSTIC_SCHEMA

    def __post_init__(self) -> None:
        if self.schema != DIAGNOSTIC_SCHEMA or type(self.frame_idx) is not int or self.frame_idx < 0:
            raise ValueError("invalid diagnostic schema/frame identity")
        if (
            type(self.canonical_time_sec) not in (int, float)
            or not isfinite(self.canonical_time_sec)
            or self.canonical_time_sec < 0
        ):
            raise ValueError("invalid diagnostic canonical timestamp")
        if type(self.shot_id) is not int or self.shot_id < 0:
            raise ValueError("invalid diagnostic shot identity")
        if self.view not in {"main", "alt", "none", "unknown"}:
            raise ValueError("invalid diagnostic view")
        if self.calibration_state not in {None, "VALID", "DEGRADED", "LOST", "REACQUIRING"}:
            raise ValueError("invalid diagnostic geometry state")
        if self.acquisition_reason not in {
            "model_ran",
            "view_excluded",
            "provider_unavailable",
            "provider_diagnostics_unsupported",
        }:
            raise ValueError("invalid diagnostic acquisition reason")
        if not isinstance(self.provider, str) or not self.provider or len(self.provider) > 128:
            raise ValueError("invalid diagnostic provider identity")
        if self.players is not None:
            if not isinstance(self.players, dict) or self.players.get("schema") != "player-tracking-diagnostics:v1":
                raise ValueError("invalid player diagnostic schema")
            if self.players.get("frame_idx") != self.frame_idx or type(self.players.get("frame_idx")) is not int:
                raise ValueError("player diagnostic frame identity differs from its frame")
            object.__setattr__(self, "players", _copy_bounded_json(self.players))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> FrameDiagnostic:
        if not isinstance(value, dict):
            raise ValueError("perception diagnostic must be a versioned mapping")
        if value.get("schema") != DIAGNOSTIC_SCHEMA:
            raise ValueError("unsupported perception diagnostic schema")
        value = dict(value)
        frame = value.get("frame_idx")
        stamp = value.get("canonical_time_sec")
        if type(frame) is not int or frame < 0 or type(stamp) not in (int, float) or not isfinite(stamp) or stamp < 0:
            raise ValueError("invalid diagnostic frame identity")
        shuttle = value.get("shuttle")
        if shuttle is not None:
            if not isinstance(shuttle, dict):
                raise ValueError("shuttle diagnostic must be a mapping")
            shuttle = dict(shuttle)
            candidates = shuttle.get("candidates", [])
            if len(candidates) > MAX_CANDIDATES:
                raise ValueError("unbounded shuttle diagnostic candidates")
            converted = []
            for item in candidates:
                if not isinstance(item, dict):
                    raise ValueError("shuttle candidate must be a mapping")
                item = dict(item)
                for key in ("peak_xy", "centroid_xy"):
                    xy = item.get(key)
                    if not isinstance(xy, (list, tuple)) or len(xy) != 2 or not np.isfinite(xy).all():
                        raise ValueError("invalid shuttle diagnostic coordinates")
                    item[key] = tuple(float(v) for v in xy)
                converted.append(HeatmapCandidate(**item))
            shuttle["candidates"] = tuple(converted)
            for key in ("selected_masked_peak_xy", "decoded_xy"):
                if shuttle.get(key) is not None:
                    shuttle[key] = tuple(shuttle[key])
            value["shuttle"] = ShuttleDiagnostic(**shuttle)
        return cls(**value)


def summarize_heatmap(
    heatmap: np.ndarray,
    threshold: float,
    mask: np.ndarray | None,
    *,
    scale: tuple[float, float],
    selection: DiagnosticSelection,
    window_votes: int,
    background_sha256: str | None = None,
    decoded_xy: tuple[float, float] | None = None,
) -> ShuttleDiagnostic:
    """Retain top-k positive components without modifying inputs or predictions.

    The diagnostic floor is fixed separately from the inference threshold.
    Connected components are ranked by their raw peak, with row-major ties.
    Masked-out candidates remain visible with an explicit rejection flag.
    """
    if heatmap.ndim != 2 or not heatmap.size or not np.isfinite(heatmap).all():
        raise ValueError("diagnostic heatmap must be finite nonempty 2D")
    if not isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("invalid inference threshold")
    if len(scale) != 2 or not all(isfinite(v) and v > 0 for v in scale):
        raise ValueError("invalid diagnostic image scale")
    if type(window_votes) is not int or window_votes < 1:
        raise ValueError("diagnostic window votes must be positive")
    if mask is not None and mask.shape != heatmap.shape:
        raise ValueError("diagnostic mask must match heatmap")
    masked = heatmap if mask is None else np.where(mask, heatmap, 0.0)
    raw_peak, masked_peak = float(heatmap.max()), float(masked.max())
    reason = (
        "accepted"
        if masked_peak > 0 and masked_peak >= threshold
        else "mask_rejected"
        if mask is not None and raw_peak > 0 and raw_peak >= threshold
        else "below_threshold"
        if raw_peak > 0
        else "no_positive_peak"
    )
    selected = np.unravel_index(int(masked.argmax()), heatmap.shape) if reason == "accepted" else None
    binary = (heatmap >= selection.candidate_floor).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    components = []
    for label in range(1, count):
        # Iterate each component only inside its bounding box. No tensors leave this call.
        x, y, width, height, area = (int(v) for v in stats[label])
        yy, xx = np.nonzero(labels[y : y + height, x : x + width] == label)
        yy, xx = yy + y, xx + x
        weights = heatmap[yy, xx].astype(np.float64)
        peak_index = int(weights.argmax())
        py, px = int(yy[peak_index]), int(xx[peak_index])
        total = float(weights.sum())
        cx, cy = float(xx @ weights / total), float(yy @ weights / total)
        spread = float(np.sqrt((((xx - cx) * scale[0]) ** 2 + ((yy - cy) * scale[1]) ** 2) @ weights / total))
        components.append((float(weights[peak_index]), py, px, cx, cy, area, spread))
    components.sort(key=lambda v: (-v[0], v[1], v[2]))
    candidates = tuple(
        HeatmapCandidate(
            rank=rank + 1,
            peak_xy=(px * scale[0], py * scale[1]),
            centroid_xy=(cx * scale[0], cy * scale[1]),
            peak_support=peak,
            area_cells=area,
            spread_px=spread,
            mask_allows_peak=mask is None or bool(mask[py, px]),
            above_inference_threshold=peak > 0 and peak >= threshold,
            selected_peak=selected == (py, px),
        )
        for rank, (peak, py, px, cx, cy, area, spread) in enumerate(components[: selection.top_k])
    )
    mass = np.maximum(heatmap.astype(np.float64), 0).ravel()
    total = float(mass.sum())
    entropy = 0.0
    if total > 0:
        normalized = mass[mass > 0] / total
        entropy = float(-(normalized * np.log(normalized)).sum() / np.log(max(2, mass.size)))
    return ShuttleDiagnostic(
        candidates,
        raw_peak,
        masked_peak,
        threshold,
        selection.candidate_floor,
        reason,
        window_votes,
        background_sha256,
        normalized_mass_entropy=entropy,
        selected_masked_peak_xy=None if selected is None else (selected[1] * scale[0], selected[0] * scale[1]),
        decoded_xy=decoded_xy,
    )
