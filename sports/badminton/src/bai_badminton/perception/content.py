"""Optional content-continuity provider and bounded evidence codec.

The explicit experimental barrier policy is a caller decision. Scene evidence
itself remains a hypothesis and never becomes authoritative camera geometry.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, fields
from math import isfinite
from typing import Any

import numpy as np
from numpy.typing import NDArray

from bai_badminton.perception.scene_change import (
    SCENE_CONTINUITY_VERSION,
    ForegroundRegion,
    RegionContinuity,
    SceneChangeEvidence,
    SceneContinuityDetector,
)

CONTENT_IMPLEMENTATION = "foreground-content-continuity-v1"
MAX_CONTENT_REGIONS = 8
MAX_CONTENT_REASONS = 8
MAX_CONTENT_TEXT = 160
_SCENE_FIELDS = {field.name for field in fields(SceneChangeEvidence)}
_REGION_FIELDS = {field.name for field in fields(RegionContinuity)}
_FOREGROUND_FIELDS = {field.name for field in fields(ForegroundRegion)}


def _number(value: Any, name: str, *, nonnegative: bool = False, fraction: bool = False) -> None:
    if value is None:
        return
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"{name} requires finite numeric evidence or unknown")
    if (nonnegative and value < 0) or (fraction and not 0 <= value <= 1):
        raise ValueError(f"invalid {name} range")


def _count(value: Any, name: str) -> None:
    if type(value) is not int or not 0 <= value <= 4096:
        raise ValueError(f"{name} exceeds the bounded feature-count contract")


def scene_change_from_dict(value: dict[str, Any], *, frame_idx: int | None = None) -> SceneChangeEvidence:
    """Validate exact version, source identity and finite bounded scene telemetry."""
    if not isinstance(value, dict) or set(value) != _SCENE_FIELDS:
        raise ValueError("invalid or unsupported scene evidence fields")
    row = dict(value)
    frame, previous = row["frame"], row["previous_frame"]
    if frame_idx is not None and (type(frame_idx) is not int or frame_idx < 0):
        raise ValueError("canonical scene frame identity must be a nonnegative integer")
    if type(frame) is not int or frame < 0 or (frame_idx is not None and frame != frame_idx):
        raise ValueError("scene evidence frame identity differs from its canonical frame")
    if previous is not None and (type(previous) is not int or not 0 <= previous < frame):
        raise ValueError("scene evidence cannot reference current/future source as previous")
    if (
        row["version"] != SCENE_CONTINUITY_VERSION
        or row["source_basis"] != "observed_pixels_and_previous_frame_regions"
    ):
        raise ValueError("unknown scene evidence version or source basis")
    if row["support_semantics"] != "raw_patch_intensity_and_adaptive_ratio_uncalibrated":
        raise ValueError("scene support is uncalibrated image evidence")
    for key in ("hypothesis", "authoritative", "correspondence_hypothesis", "appearance_hypothesis"):
        if type(row[key]) is not bool:
            raise ValueError("scene hypothesis flags require explicit booleans")
    if row["authoritative"] is not False:
        raise ValueError("scene diagnostics cannot acquire authoritative decision status")
    if (
        not isinstance(row["status"], str)
        or row["status"] not in {"unknown", "measured", "hypothesis"}
        or (row["status"] == "hypothesis") != row["hypothesis"]
    ):
        raise ValueError("scene status and hypothesis disagree")
    if (row["appearance_hypothesis"] or row["correspondence_hypothesis"]) and not row["hypothesis"]:
        raise ValueError("an active component hypothesis must remain visible")
    if row["status"] != "unknown" and previous != frame - 1:
        raise ValueError("measured scene evidence needs adjacent source frames")
    reasons = row["reasons"]
    if (
        not isinstance(reasons, (list, tuple))
        or not 1 <= len(reasons) <= MAX_CONTENT_REASONS
        or any(not isinstance(reason, str) or not 1 <= len(reason) <= MAX_CONTENT_TEXT for reason in reasons)
    ):
        raise ValueError("scene reasons exceed the bounded text contract")
    row["reasons"] = tuple(reasons)
    _count(row["background_features"], "background features")
    _number(row["background_consistent_fraction"], "background consistency", fraction=True)
    for key in ("background_patch_error", "discontinuity", "appearance_discontinuity"):
        _number(row[key], key, nonnegative=True)
    _number(row["photometric_gain"], "photometric gain")
    if row["photometric_gain"] is not None and row["photometric_gain"] <= 0:
        raise ValueError("photometric gain must be positive when observed")
    _number(row["photometric_offset"], "photometric offset")
    regions = row["regions"]
    if not isinstance(regions, (tuple, list)) or len(regions) > MAX_CONTENT_REGIONS:
        raise ValueError("scene regions exceed the bounded telemetry contract")
    converted = []
    for source in regions:
        if not isinstance(source, dict) or set(source) != _REGION_FIELDS:
            raise ValueError("invalid scene region continuity fields")
        item = dict(source)
        foreground = item["region"]
        if not isinstance(foreground, dict) or set(foreground) != _FOREGROUND_FIELDS:
            raise ValueError("invalid foreground region provenance fields")
        foreground = dict(foreground)
        if foreground["frame"] != frame - 1 or type(foreground["frame"]) is not int:
            raise ValueError("scene region must belong to the preceding source frame")
        key = foreground["key"]
        if not isinstance(key, str) or not 1 <= len(key) <= MAX_CONTENT_TEXT:
            raise ValueError("foreground episode key exceeds bounded provenance text")
        box = foreground["bbox"]
        if not isinstance(box, (tuple, list)) or len(box) != 4:
            raise ValueError("foreground box must contain exactly four image coordinates")
        for coordinate in box:
            if coordinate is None:
                raise ValueError("foreground coordinates cannot be unknown")
            _number(coordinate, "foreground coordinate")
        foreground["bbox"] = tuple(float(coordinate) for coordinate in box)
        item["region"] = ForegroundRegion(**foreground)
        _count(item["features"], "foreground features")
        _number(item["consistent_fraction"], "foreground consistency", fraction=True)
        for name in _REGION_FIELDS - {"region", "features", "consistent_fraction"}:
            _number(item[name], name, nonnegative=True)
        converted.append(RegionContinuity(**item))
    if len({item.region.key for item in converted}) != len(converted):
        raise ValueError("scene regions cannot duplicate an episode")
    row["regions"] = tuple(converted)
    return SceneChangeEvidence(**row)


def scene_change_to_dict(value: SceneChangeEvidence) -> dict[str, Any]:
    """Detach and validate before any diagnostic enters a cache or event."""
    if not isinstance(value, SceneChangeEvidence):
        raise TypeError("scene cache requires typed SceneChangeEvidence")
    return asdict(scene_change_from_dict(asdict(value)))


class ContentContinuityProvider:
    """Weightless optional provider; policy activation never rewrites evidence."""

    def __init__(self, *, mode: str = "diagnostic", **observer_parameters: Any) -> None:
        if not isinstance(mode, str) or mode not in {"diagnostic", "barrier_hypothesis_v1"}:
            raise ValueError("unsupported explicit content-continuity policy")
        allowed = {"analysis_width", "history_pairs", "adaptive_ratio", "minimum_discontinuity"}
        if observer_parameters.keys() - allowed:
            raise ValueError("unsupported content-continuity parameters")
        width = observer_parameters.get("analysis_width", 480)
        if type(width) is not int or not 96 <= width <= 1280:
            raise ValueError("content analysis width requires the bounded96..1280-pixel contract")
        self._mode = mode
        self._observer = SceneContinuityDetector(**observer_parameters)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def barrier_enabled(self) -> bool:
        return self._mode == "barrier_hypothesis_v1"

    def _open(self) -> SceneContinuityDetector:
        if self._observer is None:
            raise RuntimeError("content-continuity provider is closed")
        return self._observer

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
        return self._open().observe(
            frame,
            pixels,
            previous_regions=previous_regions,
            previous_view_valid=previous_view_valid,
            current_view_valid=current_view_valid,
            hard_cut=hard_cut,
        )

    def reset(self) -> None:
        self._open().reset()

    def close(self) -> None:
        if self._observer is not None:
            self._observer.reset()
            self._observer = None

    def checkpoint(self) -> object:
        return self._open().checkpoint()

    def restore(self, checkpoint: object) -> None:
        self._open().restore(checkpoint)
