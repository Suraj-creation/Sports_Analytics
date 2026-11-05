"""Causal foreground-continuity hypotheses, separate from scene authority.

Image changes can arise from an edit, occlusion, motion or exposure. This
observer preserves that distinction: its uncalibrated signal NEVER authorizes a
camera reset, temporal barrier, coordinate, identity or rally decision itself.
It uses current pixels and regions sourced from the immediately preceding
frame. A caller owns court/view validity and any independently justified policy.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence
from copy import deepcopy
from dataclasses import dataclass
from math import isfinite

import cv2
import numpy as np
from numpy.typing import NDArray

SCENE_CONTINUITY_VERSION = "foreground-scene-hypothesis:v2"


@dataclass(frozen=True, slots=True)
class ForegroundRegion:
    frame: int
    key: str  # opaque track episode, never physical or named identity
    bbox: tuple[float, float, float, float]
    detector_matched: bool | None
    detector_observed: bool | None

    def __post_init__(self) -> None:
        if (
            type(self.frame) is not int
            or self.frame < 0
            or not isinstance(self.key, str)
            or not 1 <= len(self.key) <= 160
        ):
            raise ValueError("foreground regions require canonical frame and opaque episode provenance")
        if len(self.bbox) != 4 or not all(isfinite(v) for v in self.bbox):
            raise ValueError("foreground region requires finite image coordinates")
        if self.bbox[2] <= self.bbox[0] or self.bbox[3] <= self.bbox[1]:
            raise ValueError("foreground region must have positive extent")
        object.__setattr__(self, "bbox", tuple(float(value) for value in self.bbox))
        if any(
            value is not None and type(value) is not bool for value in (self.detector_matched, self.detector_observed)
        ):
            raise ValueError("freshness must be observed boolean provenance or unknown")


@dataclass(frozen=True, slots=True)
class RegionContinuity:
    region: ForegroundRegion
    features: int
    consistent_fraction: float | None
    median_patch_error: float | None
    median_forward_backward_error: float | None
    discontinuity: float | None
    previous_mean: float | None
    adaptive_ratio: float | None
    appearance_previous_mean: float | None = None
    appearance_adaptive_ratio: float | None = None


@dataclass(frozen=True, slots=True)
class SceneChangeEvidence:
    frame: int
    previous_frame: int | None
    status: str
    hypothesis: bool
    reasons: tuple[str, ...]
    regions: tuple[RegionContinuity, ...] = ()
    background_features: int = 0
    background_consistent_fraction: float | None = None
    background_patch_error: float | None = None
    discontinuity: float | None = None
    photometric_gain: float | None = None
    photometric_offset: float | None = None
    authoritative: bool = False
    source_basis: str = "observed_pixels_and_previous_frame_regions"
    support_semantics: str = "raw_patch_intensity_and_adaptive_ratio_uncalibrated"
    version: str = SCENE_CONTINUITY_VERSION
    correspondence_hypothesis: bool = False
    appearance_hypothesis: bool = False
    appearance_discontinuity: float | None = None


def _flow(previous, current, mask):
    points = cv2.goodFeaturesToTrack(previous, 80, 0.01, 3, mask=mask)
    if points is None:
        return 0, None, None, None
    forward, status, error = cv2.calcOpticalFlowPyrLK(previous, current, points, None, winSize=(21, 21), maxLevel=3)
    if forward is None or status is None or error is None:
        return len(points), None, None, None
    backward, back_status, _ = cv2.calcOpticalFlowPyrLK(current, previous, forward, None, winSize=(21, 21), maxLevel=3)
    if backward is None or back_status is None:
        return len(points), None, None, None
    finite = np.isfinite(forward[:, 0]).all(axis=1) & np.isfinite(backward[:, 0]).all(axis=1)
    good = (status[:, 0] > 0) & (back_status[:, 0] > 0) & finite & np.isfinite(error[:, 0])
    fb = np.linalg.norm(backward[:, 0] - points[:, 0], axis=1)
    consistent = good & (fb <= 1.0)  # one analysis pixel; a declared tracking tolerance
    return (
        len(points),
        float(consistent.mean()),
        float(np.median(error[good])) if good.any() else None,
        float(np.median(fb[good])) if good.any() else None,
    )


class SceneContinuityDetector:
    """Bounded prior-only adaptive screen; no calibrated scene probability.

    The 3x adaptive screen and 15/255 intensity floor are prespecified exploratory
    defaults motivated by the public adaptive-content detector, not fitted to
    rally labels or claimed equivalent to that detector's HSV score. Every
    participant region must exceed its OWN prior-only baseline; one occluder
    cannot establish a multi-region change. Unknown features/view/context abstain.
    """

    def __init__(self, *, analysis_width=480, history_pairs=2, adaptive_ratio=3.0, minimum_discontinuity=15.0):
        if type(analysis_width) is not int or analysis_width < 96:
            raise ValueError("analysis width must be an integer of at least96")
        if type(history_pairs) is not int or not 1 <= history_pairs <= 120:
            raise ValueError("prior history must contain between one and120 frame pairs")
        if (
            not isfinite(adaptive_ratio)
            or adaptive_ratio <= 1
            or not isfinite(minimum_discontinuity)
            or minimum_discontinuity <= 0
        ):
            raise ValueError("diagnostic ratio/intensity limits must be finite and positive")
        self.analysis_width = analysis_width
        self.history_pairs = history_pairs
        self.adaptive_ratio = float(adaptive_ratio)
        self.minimum_discontinuity = float(minimum_discontinuity)
        self._owner = object()
        self.reset()

    def reset(self) -> None:
        self._previous = None
        self._previous_frame = None
        self._history: dict[str, deque[float]] = {}
        self._appearance_history: dict[str, deque[float]] = {}

    def checkpoint(self) -> tuple:
        return self._owner, deepcopy((self._previous, self._previous_frame, self._history, self._appearance_history))

    def restore(self, checkpoint: tuple) -> None:
        if not isinstance(checkpoint, tuple) or len(checkpoint) != 2 or checkpoint[0] is not self._owner:
            raise ValueError("incompatible scene-continuity checkpoint")
        self._previous, self._previous_frame, self._history, self._appearance_history = deepcopy(checkpoint[1])

    def observe(
        self,
        frame: int,
        pixels: NDArray[np.uint8],
        *,
        previous_regions: Sequence[ForegroundRegion],
        previous_view_valid: bool,
        current_view_valid: bool,
        hard_cut: bool = False,
    ) -> SceneChangeEvidence:
        if type(frame) is not int or frame < 0:
            raise ValueError("source frame must be a nonnegative canonical integer")
        image = np.asarray(pixels)
        if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3 or min(image.shape[:2]) < 2:
            raise ValueError("scene input must be nonempty uint8 BGR pixels")
        if any(region.frame != frame - 1 for region in previous_regions):
            raise ValueError("regions must be sourced from the immediately preceding frame")
        if len({region.key for region in previous_regions}) != len(previous_regions):
            raise ValueError("foreground episode provenance must be distinct")
        scale = self.analysis_width / image.shape[1]
        gray = cv2.cvtColor(
            cv2.resize(image, (self.analysis_width, max(2, round(image.shape[0] * scale)))), cv2.COLOR_BGR2GRAY
        )
        previous, previous_frame = self._previous, self._previous_frame
        # Detach from caller-owned pixels before any result is published.
        self._previous, self._previous_frame = gray.copy(), frame
        if previous is None or previous_frame != frame - 1 or previous.shape != gray.shape or hard_cut:
            self._history.clear()
            self._appearance_history.clear()
            reason = "known_camera_cut" if hard_cut else "missing_adjacent_source_context"
            return SceneChangeEvidence(frame, previous_frame, "unknown", False, (reason,))
        if not previous_view_valid or not current_view_valid:
            self._history.clear()
            self._appearance_history.clear()
            return SceneChangeEvidence(frame, previous_frame, "unknown", False, ("excluded_view",))
        if not 2 <= len(previous_regions) <= 4:
            self._history.clear()
            self._appearance_history.clear()
            return SceneChangeEvidence(frame, previous_frame, "unknown", False, ("two_to_four_prior_regions_required",))
        # Robust global photometric normalization uses ONLY the two available
        # images. Flat/saturated images cannot verify continuity.
        p25, p50, p75 = np.percentile(previous, [25, 50, 75])
        q25, q50, q75 = np.percentile(gray, [25, 50, 75])
        if min(p75 - p25, q75 - q25) < 1:
            self._history.clear()
            self._appearance_history.clear()
            return SceneChangeEvidence(frame, previous_frame, "unknown", False, ("insufficient_image_dynamic_range",))
        gain = float((q75 - q25) / (p75 - p25))
        offset = float(q50 - gain * p50)
        normalized = np.clip((gray.astype(float) - offset) / gain, 0, 255).astype(np.uint8)
        masks = []
        background = np.full_like(gray, 255)
        for region in previous_regions:
            x1, y1, x2, y2 = np.asarray(region.bbox) * scale
            x1, x2 = np.clip([int(x1), int(np.ceil(x2))], 0, gray.shape[1])
            y1, y2 = np.clip([int(y1), int(np.ceil(y2))], 0, gray.shape[0])
            mask = np.zeros_like(gray)
            mask[y1:y2, x1:x2] = 255
            background[mask > 0] = 0
            masks.append(mask)
        bg_features, bg_consistent, bg_error, _ = _flow(previous, normalized, background)
        regions = []
        for region, mask in zip(previous_regions, masks, strict=True):
            features, consistent, error, fb_error = _flow(previous, normalized, mask)
            value = error * (1 - consistent) if error is not None and consistent is not None and features >= 6 else None
            history = self._history.get(region.key, deque(maxlen=self.history_pairs))
            baseline = float(np.mean(history)) if len(history) == self.history_pairs else None
            ratio = value / max(1.0, baseline) if value is not None and baseline is not None else None
            # Reversible flow is NOT appearance/identity confidence. Preserve a
            # separate raw photometric hypothesis instead of allowing high FB
            # consistency to erase a strongly mismatching patch.
            appearance = error if error is not None and features >= 6 else None
            appearance_history = self._appearance_history.get(region.key, deque(maxlen=self.history_pairs))
            appearance_baseline = (
                float(np.mean(appearance_history)) if len(appearance_history) == self.history_pairs else None
            )
            appearance_ratio = (
                appearance / max(1.0, appearance_baseline)
                if appearance is not None and appearance_baseline is not None
                else None
            )
            regions.append(
                RegionContinuity(
                    region,
                    features,
                    consistent,
                    error,
                    fb_error,
                    value,
                    baseline,
                    ratio,
                    appearance_baseline,
                    appearance_ratio,
                )
            )
            if value is not None:
                history.append(value)
            else:
                history.clear()
            self._history[region.key] = history
            if appearance is not None:
                appearance_history.append(appearance)
            else:
                appearance_history.clear()
            self._appearance_history[region.key] = appearance_history
        keys = {region.key for region in previous_regions}
        self._history = {key: value for key, value in self._history.items() if key in keys}
        self._appearance_history = {key: value for key, value in self._appearance_history.items() if key in keys}
        reliable = bg_features >= 6 and bg_consistent is not None and bg_consistent >= 0.5
        all_values = all(region.discontinuity is not None for region in regions)
        score = float(np.mean([region.discontinuity for region in regions])) if all_values else None
        all_ratios = all(region.adaptive_ratio is not None for region in regions)
        correspondence_hypothesis = bool(
            reliable
            and all_values
            and all_ratios
            and score >= self.minimum_discontinuity
            and all(region.adaptive_ratio >= self.adaptive_ratio for region in regions)
        )
        appearance_values = all(region.median_patch_error is not None and region.features >= 6 for region in regions)
        appearance_score = (
            float(np.mean([region.median_patch_error for region in regions])) if appearance_values else None
        )
        appearance_hypothesis = bool(
            reliable
            and appearance_values
            and appearance_score >= self.minimum_discontinuity
            and all(
                region.appearance_adaptive_ratio is not None and region.appearance_adaptive_ratio >= self.adaptive_ratio
                for region in regions
            )
        )
        hypothesis = correspondence_hypothesis or appearance_hypothesis
        reasons = (
            tuple(
                reason
                for reason, enabled in (
                    ("correspondence_discontinuity", correspondence_hypothesis),
                    ("appearance_discontinuity", appearance_hypothesis),
                    ("edit_or_multi_region_occlusion_not_independently_resolved", True),
                )
                if enabled
            )
            if hypothesis
            else ("insufficient_background_continuity",)
            if not reliable
            else ("insufficient_region_features",)
            if not all_values
            else ("insufficient_prior_pair_history",)
            if not all_ratios
            else ("no_joint_adaptive_discontinuity",)
        )
        return SceneChangeEvidence(
            frame,
            previous_frame,
            "hypothesis" if hypothesis else "measured" if all_values and reliable else "unknown",
            hypothesis,
            reasons,
            tuple(regions),
            bg_features,
            bg_consistent,
            bg_error,
            score,
            gain,
            offset,
            correspondence_hypothesis=correspondence_hypothesis,
            appearance_hypothesis=appearance_hypothesis,
            appearance_discontinuity=appearance_score,
        )
