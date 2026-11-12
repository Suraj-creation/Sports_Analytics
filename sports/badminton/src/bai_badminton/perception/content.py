"""Optional content-continuity provider and bounded evidence codec.

The explicit experimental barrier policy is a caller decision. Scene evidence
itself remains a hypothesis and never becomes authoritative camera geometry.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, fields
from math import isclose, isfinite
from typing import Any

import numpy as np
from numpy.typing import NDArray

from bai_badminton.perception.scene_change import (
    SCENE_CONTINUITY_VERSION,
    SCENE_CONTINUITY_VERSION_V3,
    SCENE_CONTINUITY_VERSION_V4,
    SCENE_CONTINUITY_VERSION_V5,
    FeatureOriginMask,
    ForegroundRegion,
    RegionContinuity,
    SceneChangeEvidence,
    SceneContinuityDetector,
    SceneContinuityDetectorV2,
    SceneContinuityDetectorV5,
    independent_scene_witnesses,
    scene_relative_cohorts,
    validate_feature_origin_basis,
)

CONTENT_IMPLEMENTATION = "foreground-content-continuity-v1"
CONTENT_IMPLEMENTATION_V2 = "foreground-content-continuity-v2"
MAX_CONTENT_REGIONS = 8
MAX_CONTENT_REASONS = 8
MAX_CONTENT_TEXT = 160
_SCENE_FIELDS = {field.name for field in fields(SceneChangeEvidence)}
_ORIGIN_FIELDS = {"feature_origin_policy", "source_frame_size", "analysis_frame_size", "origin_masks"}
_REGION_FIELDS = {field.name for field in fields(RegionContinuity)}
_FOREGROUND_FIELDS = {field.name for field in fields(ForegroundRegion)}


@dataclass(frozen=True, slots=True)
class SceneDecisionEvidence:
    """Current-detector corroboration of a tracking boundary, never a point."""

    frame: int
    previous_frame: int
    decision: str
    reason: str
    raw_hypothesis: bool
    detector_frame: int | None
    detector_model: str | None
    detector_image_sha256: str | None
    detector_image_shape: tuple[int, int, int] | None
    detector_boxes: tuple[tuple[float, float, float, float], ...]
    detector_scores: tuple[float, ...]
    admitted_indices: tuple[int, ...]
    matched_pairs: tuple[tuple[int, int], ...]
    iou_threshold: float = 0.3
    previous_region_count: int = 0
    version: str = "detector-layout-scene-decision:v1"
    supporting_region_keys: tuple[str, ...] = ()
    layout_indices: tuple[int, ...] = ()
    acquisition_region_keys: tuple[str, ...] = ()
    relative_region_keys: tuple[str, ...] = ()
    court_polygon: tuple[tuple[float, float], ...] = ()
    court_indices: tuple[int, ...] = ()
    expected_participants: int | None = None
    geometry_valid: bool | None = None
    previous_to_current: tuple[float, ...] | None = None
    previous_camera: tuple[float, ...] | None = None
    feature_origin_overlap_dependent: bool = False

    def __post_init__(self) -> None:
        if (
            type(self.frame) is not int
            or self.frame < 1
            or type(self.previous_frame) is not int
            or self.previous_frame != self.frame - 1
        ):
            raise ValueError("scene decision requires adjacent canonical source frames")
        if type(self.feature_origin_overlap_dependent) is not bool or (
            self.feature_origin_overlap_dependent
            and (self.version != "detector-layout-scene-decision:v4" or not self.raw_hypothesis)
        ):
            raise ValueError("exclusive-origin overlap authority requires the new strong decision contract")
        if (
            self.version
            not in {
                "detector-layout-scene-decision:v1",
                "detector-layout-scene-decision:v2",
                "detector-layout-scene-decision:v3",
                "detector-layout-scene-decision:v4",
            }
            or self.decision not in {"barrier", "no_barrier", "unknown"}
            or not isinstance(self.reason, str)
            or not 1 <= len(self.reason) <= MAX_CONTENT_TEXT
            or type(self.raw_hypothesis) is not bool
        ):
            raise ValueError("unsupported scene decision evidence")
        if (
            type(self.previous_region_count) is not int
            or not 0 <= self.previous_region_count <= 8
            or type(self.iou_threshold) not in (int, float)
            or self.iou_threshold != 0.3
        ):
            raise ValueError("scene decision must retain the existing observed-box continuity gate")
        if (
            len(set(self.supporting_region_keys)) != len(self.supporting_region_keys)
            or len(self.supporting_region_keys) > self.previous_region_count
            or any(
                not isinstance(key, str) or not 1 <= len(key) <= MAX_CONTENT_TEXT for key in self.supporting_region_keys
            )
            or (self.version.endswith(":v1") and self.supporting_region_keys)
        ):
            raise ValueError("invalid scene decision witness provenance")
        if (
            (self.version.endswith(":v1") and self.layout_indices)
            or len(set(self.layout_indices)) != len(self.layout_indices)
            or any(type(i) is not int or not 0 <= i < len(self.detector_boxes) for i in self.layout_indices)
            or (
                self.version
                in {
                    "detector-layout-scene-decision:v2",
                    "detector-layout-scene-decision:v3",
                    "detector-layout-scene-decision:v4",
                }
                and self.layout_indices != tuple(range(len(self.detector_boxes)))
            )
        ):
            raise ValueError("scene layout candidates must preserve the full raw image proposals")
        modern = self.version in {"detector-layout-scene-decision:v3", "detector-layout-scene-decision:v4"}
        if modern:
            if type(self.geometry_valid) is not bool or (
                self.expected_participants is not None
                and (type(self.expected_participants) is not int or self.expected_participants not in (2, 4))
            ):
                raise ValueError("new scene acquisition requires explicit geometry/format evidence")
            for keys in (self.acquisition_region_keys, self.relative_region_keys):
                if (
                    len(keys) > self.previous_region_count
                    or len(set(keys)) != len(keys)
                    or any(not isinstance(key, str) or not 1 <= len(key) <= MAX_CONTENT_TEXT for key in keys)
                ):
                    raise ValueError("invalid relative image witness provenance")
            if self.previous_to_current is not None:
                _camera_matrix(self.previous_to_current)
            if self.previous_camera is not None:
                _camera_matrix(self.previous_camera)
            if not set(self.relative_region_keys) <= set(self.acquisition_region_keys):
                raise ValueError("relative scene quorum must retain acquisition witnesses")
        elif (
            self.acquisition_region_keys
            or self.relative_region_keys
            or self.court_polygon
            or self.court_indices
            or self.expected_participants is not None
            or self.geometry_valid is not None
            or self.previous_to_current is not None
            or self.previous_camera is not None
        ):
            raise ValueError("legacy scene decision cannot acquire new court-replacement authority")
        if len(self.detector_boxes) != len(self.detector_scores) or len(self.detector_boxes) > 4096:
            raise ValueError("scene detector outputs exceed their bounded contract")
        if self.detector_frame is None:
            if (
                self.detector_model is not None
                or self.detector_image_sha256 is not None
                or self.detector_image_shape is not None
                or self.detector_boxes
                or self.detector_scores
                or self.admitted_indices
                or self.matched_pairs
                or self.layout_indices
                or self.court_polygon
                or self.court_indices
                or self.decision != "unknown"
            ):
                raise ValueError("missing detector source cannot support a layout decision")
            return
        if type(self.detector_frame) is not int or self.detector_frame != self.frame:
            raise ValueError("scene detector must observe the exact current source frame")
        if not isinstance(self.detector_model, str) or not 1 <= len(self.detector_model) <= MAX_CONTENT_TEXT:
            raise ValueError("scene detector model provenance is required")
        digest = self.detector_image_sha256
        shape = self.detector_image_shape
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
            or shape is None
            or len(shape) != 3
            or any(type(v) is not int or v <= 0 for v in shape)
            or shape[2] != 3
        ):
            raise ValueError("invalid scene detector image provenance")
        for box, score in zip(self.detector_boxes, self.detector_scores, strict=True):
            if (
                len(box) != 4
                or any(type(v) not in (int, float) or not isfinite(v) for v in (*box, score))
                or not 0 <= score <= 1
                or not 0 <= box[0] < box[2] <= shape[1]
                or not 0 <= box[1] < box[3] <= shape[0]
            ):
                raise ValueError("invalid scene detector coordinates or supports")
        if len(set(self.admitted_indices)) != len(self.admitted_indices) or any(
            type(i) is not int or not 0 <= i < len(self.detector_boxes) for i in self.admitted_indices
        ):
            raise ValueError("invalid scene detector ROI admission")
        if modern:
            from bai_badminton.perception.players import strict_court_indices

            if (
                len(set(self.court_indices)) != len(self.court_indices)
                or any(type(i) is not int or not 0 <= i < len(self.detector_boxes) for i in self.court_indices)
                or self.court_indices != strict_court_indices(self.detector_boxes, self.court_polygon)
            ):
                raise ValueError("scene court membership differs from its recorded polygon")
        previous, current = set(), set()
        for pair in self.matched_pairs:
            if (
                len(pair) != 2
                or any(type(i) is not int for i in pair)
                or not 0 <= pair[0] < self.previous_region_count
                or pair[1]
                not in (
                    self.layout_indices
                    if self.version
                    in {
                        "detector-layout-scene-decision:v2",
                        "detector-layout-scene-decision:v3",
                        "detector-layout-scene-decision:v4",
                    }
                    else self.admitted_indices
                )
                or pair[0] in previous
                or pair[1] in current
            ):
                raise ValueError("scene correspondence must be one-to-one and source bound")
            previous.add(pair[0])
            current.add(pair[1])
        if (
            self.feature_origin_overlap_dependent
            and self.decision != "unknown"
            and not _complete_court_layout(
                self.detector_boxes,
                self.court_indices,
                self.expected_participants,
                self.previous_region_count,
                self.geometry_valid,
                self.court_polygon,
                self.previous_to_current,
                self.previous_camera,
            )
        ):
            raise ValueError("overlap-dependent authority requires complete confirmed current court/camera proof")
        if self.decision != "unknown":
            witness_count = (
                len(self.supporting_region_keys)
                if self.version
                in {
                    "detector-layout-scene-decision:v2",
                    "detector-layout-scene-decision:v3",
                    "detector-layout-scene-decision:v4",
                }
                else self.previous_region_count
            )
            maximum = 4 if self.version.endswith(":v1") else 8
            weak = modern and not self.raw_hypothesis
            if weak:
                if (
                    self.decision != "barrier"
                    or self.reason != "relative_change_and_complete_court_replacement"
                    or not self.geometry_valid
                    or self.previous_to_current is None
                    or self.previous_camera is None
                    or self.expected_participants not in (2, 4)
                    or self.previous_region_count < self.expected_participants
                    or len(self.relative_region_keys) < 2
                    or not self.court_polygon
                    or len(self.court_indices) != self.expected_participants
                    or self.matched_pairs
                ):
                    raise ValueError("weak scene reset requires complete independent court replacement")
                return
            if not self.raw_hypothesis or not 2 <= witness_count <= maximum:
                raise ValueError("layout decisions need a raw hypothesis and multiple prior regions")
            if self.version.endswith(":v1") and len(self.admitted_indices) != self.previous_region_count:
                raise ValueError("changed/unknown person count cannot prove layout discontinuity")
            if (self.decision == "no_barrier") != (len(self.matched_pairs) == witness_count):
                raise ValueError("scene decision disagrees with current layout correspondence")


def scene_decision_from_dict(value: dict[str, Any], *, frame_idx: int | None = None) -> SceneDecisionEvidence:
    if isinstance(value, dict) and value.get("version") != "detector-layout-scene-decision:v4":
        if value.get("feature_origin_overlap_dependent", False) is not False:
            raise ValueError("legacy decisions cannot acquire exclusive-origin overlap authority")
        value = {"feature_origin_overlap_dependent": False, **value}
    if (
        isinstance(value, dict)
        and value.get("version") == "detector-layout-scene-decision:v1"
        and "supporting_region_keys" not in value
    ):
        value = {**value, "supporting_region_keys": ()}
    if isinstance(value, dict) and value.get("version") == "detector-layout-scene-decision:v1":
        value = {"layout_indices": (), **value}
    if isinstance(value, dict) and value.get("version") in {
        "detector-layout-scene-decision:v1",
        "detector-layout-scene-decision:v2",
    }:
        value = {
            "acquisition_region_keys": (),
            "relative_region_keys": (),
            "court_polygon": (),
            "court_indices": (),
            "expected_participants": None,
            "geometry_valid": None,
            "previous_to_current": None,
            "previous_camera": None,
            **value,
        }
    if not isinstance(value, dict) or set(value) != {f.name for f in fields(SceneDecisionEvidence)}:
        raise ValueError("invalid or unsupported scene decision fields")
    row = dict(value)
    if frame_idx is not None and (type(frame_idx) is not int or row["frame"] != frame_idx):
        raise ValueError("scene decision differs from its canonical source frame")
    for name in (
        "detector_boxes",
        "detector_scores",
        "admitted_indices",
        "matched_pairs",
        "supporting_region_keys",
        "layout_indices",
        "acquisition_region_keys",
        "relative_region_keys",
        "court_polygon",
        "court_indices",
    ):
        if not isinstance(row[name], (tuple, list)):
            raise ValueError("scene decision requires bounded array evidence")
        row[name] = tuple(row[name])
    for name in ("detector_boxes", "matched_pairs", "court_polygon"):
        if any(not isinstance(item, (tuple, list)) for item in row[name]):
            raise ValueError("scene decision requires explicit coordinate/index rows")
        row[name] = tuple(tuple(item) for item in row[name])
    if row["detector_image_shape"] is not None:
        if not isinstance(row["detector_image_shape"], (tuple, list)):
            raise ValueError("scene detector image shape requires an array")
        row["detector_image_shape"] = tuple(row["detector_image_shape"])
    for name in ("previous_to_current", "previous_camera"):
        if row[name] is not None:
            if not isinstance(row[name], (tuple, list)):
                raise ValueError("scene camera transform requires an explicit bounded array")
            row[name] = tuple(row[name])
    return SceneDecisionEvidence(**row)


def scene_decision_to_dict(value: SceneDecisionEvidence) -> dict[str, Any]:
    if not isinstance(value, SceneDecisionEvidence):
        raise TypeError("scene decision cache requires typed evidence")
    result = asdict(scene_decision_from_dict(asdict(value)))
    if value.version != "detector-layout-scene-decision:v4":
        result.pop("feature_origin_overlap_dependent")
    return result


def validate_scene_decision_binding(decision: SceneDecisionEvidence, raw: SceneChangeEvidence) -> None:
    """Verify source identity and recompute each claimed layout correspondence.

    Index validity alone cannot establish that two boxes overlap. Unknown
    decisions deliberately make no correspondence claim; nonunknown decisions
    must reproduce the unique existing0.3-IoU gate from the recorded pixels'
    previous/current detector regions.
    """
    if not isinstance(decision, SceneDecisionEvidence) or not isinstance(raw, SceneChangeEvidence):
        raise TypeError("scene decision binding requires typed source evidence")
    if raw.version in {SCENE_CONTINUITY_VERSION_V4, SCENE_CONTINUITY_VERSION_V5}:
        raw = scene_change_from_dict(scene_change_to_dict(raw))
    expected_version = (
        "detector-layout-scene-decision:v4"
        if raw.version == SCENE_CONTINUITY_VERSION_V5
        else "detector-layout-scene-decision:v3"
        if raw.version in {SCENE_CONTINUITY_VERSION_V4, SCENE_CONTINUITY_VERSION_V5}
        else "detector-layout-scene-decision:v2"
        if raw.version == SCENE_CONTINUITY_VERSION_V3
        else "detector-layout-scene-decision:v1"
    )
    if decision.version != expected_version:
        raise ValueError("scene decision contract differs from the raw evidence version")
    if decision.feature_origin_overlap_dependent != feature_origin_overlap_dependent(raw):
        raise ValueError("scene overlap authority differs from its raw full-box witness geometry")
    if (
        decision.frame != raw.frame
        or decision.previous_frame != raw.previous_frame
        or decision.raw_hypothesis != raw.hypothesis
        or decision.previous_region_count != len(raw.regions)
    ):
        raise ValueError("scene decision differs from its exact source-frame raw hypothesis")
    modern = decision.version in {
        "detector-layout-scene-decision:v2",
        "detector-layout-scene-decision:v3",
        "detector-layout-scene-decision:v4",
    }
    if modern and decision.supporting_region_keys != raw.supporting_region_keys:
        raise ValueError("scene decision witnesses differ from its raw image hypothesis")
    if decision.version in {"detector-layout-scene-decision:v3", "detector-layout-scene-decision:v4"} and (
        decision.acquisition_region_keys != raw.acquisition_region_keys
        or decision.relative_region_keys != raw.relative_region_keys
    ):
        raise ValueError("relative decision witnesses differ from their raw image evidence")
    if decision.decision == "unknown":
        return
    if (
        decision.version in {"detector-layout-scene-decision:v3", "detector-layout-scene-decision:v4"}
        and not raw.hypothesis
    ):
        if not _weak_court_replacement(
            raw,
            decision.detector_boxes,
            decision.court_indices,
            decision.expected_participants,
            geometry_valid=decision.geometry_valid,
            court_polygon=decision.court_polygon,
            previous_to_current=decision.previous_to_current,
            previous_camera=decision.previous_camera,
        ):
            raise ValueError("weak scene reset is not supported by complete source-bound court replacement")
        return
    from bai_badminton.perception.players import _box_iou

    indices = (
        [i for i, item in enumerate(raw.regions) if item.region.key in decision.supporting_region_keys]
        if modern
        else list(range(len(raw.regions)))
    )
    previous = np.asarray([raw.regions[i].region.bbox for i in indices], dtype=np.float64)
    candidates = decision.layout_indices if modern else decision.admitted_indices
    current = np.asarray([decision.detector_boxes[i] for i in candidates], dtype=np.float64)
    overlap = _box_iou(previous, current) >= decision.iou_threshold
    if (overlap.sum(axis=0) > 1).any() or (overlap.sum(axis=1) > 1).any():
        raise ValueError("ambiguous scene detector layout cannot support a nonunknown decision")
    expected = tuple((indices[a], int(candidates[b])) for a, b in zip(*np.nonzero(overlap), strict=True))
    if decision.matched_pairs != expected:
        raise ValueError("scene detector correspondences disagree with recorded source-region geometry")
    if (
        decision.feature_origin_overlap_dependent
        and decision.decision == "barrier"
        and _camera_explains_witness_layout(raw, decision.detector_boxes, decision.previous_to_current)
    ):
        raise ValueError("overlap-dependent barrier contradicts complete camera-aligned source correspondence")
    if (
        decision.feature_origin_overlap_dependent
        and decision.decision == "barrier"
        and _positive_nonwitness_court_correspondence(
            raw, decision.detector_boxes, decision.court_indices, decision.previous_to_current
        )
    ):
        raise ValueError("overlap-dependent barrier contradicts positive nonwitness court correspondence")


def feature_origin_overlap_dependent(raw):
    """New authority is needed only if the old full-box rule cannot qualify."""
    if raw.version != SCENE_CONTINUITY_VERSION_V5 or not raw.hypothesis:
        return False
    ratio, floor = raw.witness_parameters
    reliable = (
        raw.background_features >= 6
        and raw.background_consistent_fraction is not None
        and raw.background_consistent_fraction >= 0.5
    )
    for ratio_name, value_name in (
        ("adaptive_ratio", "discontinuity"),
        ("appearance_adaptive_ratio", "median_patch_error"),
    ):
        if independent_scene_witnesses(
            raw.regions,
            reliable=reliable,
            adaptive_ratio=ratio,
            minimum_discontinuity=floor,
            ratio_name=ratio_name,
            value_name=value_name,
        ):
            return False
    return True


def _complete_court_layout(
    boxes, court_indices, expected, previous_count, geometry_valid, polygon, previous_to_current, previous_camera
):
    from bai_badminton.perception.players import _box_iou, strict_court_indices

    if (
        geometry_valid is not True
        or type(expected) is not int
        or expected not in (2, 4)
        or previous_count < expected
        or len(court_indices) != expected
        or not polygon
        or previous_to_current is None
        or previous_camera is None
    ):
        return False
    _camera_matrix(previous_to_current)
    _camera_matrix(previous_camera)
    if court_indices != strict_court_indices(boxes, polygon):
        return False
    current = np.asarray([boxes[i] for i in court_indices], dtype=np.float64)
    overlap = _box_iou(current, current) >= 0.3
    np.fill_diagonal(overlap, False)
    return not overlap.any()


def _camera_matrix(values):
    if (
        not isinstance(values, (tuple, list))
        or len(values) != 9
        or any(type(v) not in (int, float) or not isfinite(v) for v in values)
    ):
        raise ValueError("scene camera transform requires nine finite numbers")
    matrix = np.asarray(values, dtype=np.float64).reshape(3, 3)
    try:
        inverse = np.linalg.inv(matrix)
    except np.linalg.LinAlgError as error:
        raise ValueError("scene camera transform must be invertible") from error
    if not np.isfinite(inverse).all():
        raise ValueError("scene camera transform inverse is not finite")
    return matrix


def _camera_aligned_boxes(previous, values):
    matrix = _camera_matrix(values)
    aligned = []
    for x0, y0, x1, y1 in previous:
        corners = np.asarray(((x0, y0, 1.0), (x1, y0, 1.0), (x1, y1, 1.0), (x0, y1, 1.0))) @ matrix.T
        denominator = corners[:, 2]
        if (
            not np.isfinite(corners).all()
            or (denominator == 0).any()
            or not ((denominator > 0).all() or (denominator < 0).all())
        ):
            return None
        xy = corners[:, :2] / denominator[:, None]
        if not np.isfinite(xy).all():
            return None
        box = (*xy.min(axis=0), *xy.max(axis=0))
        if box[2] <= box[0] or box[3] <= box[1]:
            return None
        aligned.append(box)
    return np.asarray(aligned, dtype=np.float64)


def _camera_explains_witness_layout(raw, boxes, previous_to_current):
    from bai_badminton.perception.players import _box_iou

    previous = [r.region.bbox for r in raw.regions if r.region.key in raw.supporting_region_keys]
    aligned = _camera_aligned_boxes(previous, previous_to_current)
    if aligned is None or not len(previous) or not len(boxes):
        return False
    overlap = _box_iou(aligned, np.asarray(boxes, dtype=np.float64)) >= 0.3
    return bool((overlap.sum(axis=1) == 1).all() and (overlap.sum(axis=0) <= 1).all())


def _positive_nonwitness_court_correspondence(raw, boxes, court_indices, previous_to_current):
    """A retained court actor may expose multiple innovations as one actor's parts.

    Only current strict-court boxes matter here; outside static officials cannot
    veto. Nonwitness means unavailable innovation, not verified static identity.
    This conservative ambiguity gate applies only to new overlap authority.
    """
    from bai_badminton.perception.players import _box_iou

    previous = [r.region.bbox for r in raw.regions if r.region.key not in raw.supporting_region_keys]
    if not previous or not court_indices:
        return False
    current = np.asarray([boxes[i] for i in court_indices], dtype=np.float64)
    if (_box_iou(np.asarray(previous, dtype=np.float64), current) >= 0.3).any():
        return True
    aligned = _camera_aligned_boxes(previous, previous_to_current)
    return bool(aligned is not None and (_box_iou(aligned, current) >= 0.3).any())


def _weak_court_replacement(
    raw,
    boxes,
    court_indices,
    expected_participants,
    *,
    geometry_valid,
    court_polygon,
    previous_to_current,
    previous_camera,
):
    """Corroborated replacement proof, never an image-only threshold fallback."""
    from bai_badminton.perception.players import _box_iou, strict_court_indices

    if (
        geometry_valid is not True
        or type(expected_participants) is not int
        or expected_participants not in (2, 4)
        or len(raw.relative_region_keys) < 2
        or len(raw.regions) < expected_participants
        or not court_polygon
        or previous_to_current is None
        or previous_camera is None
        or len(court_indices) != expected_participants
    ):
        return False
    _camera_matrix(previous_camera)
    if court_indices != strict_court_indices(boxes, court_polygon):
        return False
    previous = np.asarray([region.region.bbox for region in raw.regions], dtype=np.float64)
    current = np.asarray([boxes[i] for i in court_indices], dtype=np.float64)
    # All prior image regions matter, including a non-innovating static witness:
    # weak acquisition cannot select away positive current correspondence.
    if (_box_iou(previous, current) >= 0.3).any():
        return False
    aligned = _camera_aligned_boxes(previous, previous_to_current)
    if aligned is None or (_box_iou(aligned, current) >= 0.3).any():
        return False
    mutually_same = _box_iou(current, current) >= 0.3
    np.fill_diagonal(mutually_same, False)
    return not mutually_same.any()


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
    if isinstance(value, dict) and value.get("version") in {SCENE_CONTINUITY_VERSION, SCENE_CONTINUITY_VERSION_V3}:
        value = {"acquisition_region_keys": (), "relative_region_keys": (), **value}
    if isinstance(value, dict) and value.get("version") == SCENE_CONTINUITY_VERSION:
        value = {"supporting_region_keys": (), "witness_parameters": None, **value}
    if isinstance(value, dict) and value.get("version") != SCENE_CONTINUITY_VERSION_V5:
        # In-process dataclasses expose newly added optional fields through
        # asdict(). Empty defaults grant no measurement authority; historical
        # wire serialization below still omits them exactly.
        if any(value.get(key) is not None for key in _ORIGIN_FIELDS - {"origin_masks"}) or value.get("origin_masks"):
            raise ValueError("legacy scene measurements cannot acquire exclusive feature-origin authority")
        value = {
            "feature_origin_policy": None,
            "source_frame_size": None,
            "analysis_frame_size": None,
            "origin_masks": (),
            **value,
        }
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
        row["version"]
        not in {
            SCENE_CONTINUITY_VERSION,
            SCENE_CONTINUITY_VERSION_V3,
            SCENE_CONTINUITY_VERSION_V4,
            SCENE_CONTINUITY_VERSION_V5,
        }
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
    exclusive_origins = row["version"] == SCENE_CONTINUITY_VERSION_V5
    if exclusive_origins:
        records = row["origin_masks"]
        if not isinstance(records, (tuple, list)) or len(records) != len(converted):
            raise ValueError("exclusive feature origins require a record for every measured prior ROI")
        parsed = []
        for record in records:
            if (
                not isinstance(record, dict)
                or set(record) != {"key", "pixels", "sha256"}
                or not isinstance(record["key"], str)
                or type(record["pixels"]) is not int
                or record["pixels"] < 0
                or not isinstance(record["sha256"], str)
                or len(record["sha256"]) != 64
                or any(c not in "0123456789abcdef" for c in record["sha256"])
            ):
                raise ValueError("invalid exclusive feature-origin mask record")
            parsed.append(FeatureOriginMask(**record))
        row["origin_masks"] = tuple(parsed)
        validate_feature_origin_basis(
            converted,
            row["feature_origin_policy"],
            row["source_frame_size"],
            row["analysis_frame_size"],
            row["origin_masks"],
        )
        row["source_frame_size"] = tuple(row["source_frame_size"])
        row["analysis_frame_size"] = tuple(row["analysis_frame_size"])
    keys = row["supporting_region_keys"]
    if (
        not isinstance(keys, (tuple, list))
        or any(not isinstance(key, str) for key in keys)
        or len(set(keys)) != len(keys)
        or any(key not in {item.region.key for item in converted} for key in keys)
        or (row["version"] == SCENE_CONTINUITY_VERSION and keys)
        or (
            row["version"] in {SCENE_CONTINUITY_VERSION_V3, SCENE_CONTINUITY_VERSION_V4, SCENE_CONTINUITY_VERSION_V5}
            and row["hypothesis"] != (len(keys) >= 2)
        )
    ):
        raise ValueError("invalid independent scene witness provenance")
    row["supporting_region_keys"] = tuple(keys)
    parameters = row["witness_parameters"]
    if row["version"] in {SCENE_CONTINUITY_VERSION_V3, SCENE_CONTINUITY_VERSION_V4, SCENE_CONTINUITY_VERSION_V5}:
        if (
            not isinstance(parameters, (tuple, list))
            or len(parameters) != 2
            or any(type(v) not in (int, float) or not isfinite(v) for v in parameters)
            or parameters[0] <= 1
            or parameters[1] <= 0
        ):
            raise ValueError("missing valid recorded scene witness parameters")
        reliable = (
            row["background_features"] >= 6
            and row["background_consistent_fraction"] is not None
            and row["background_consistent_fraction"] >= 0.5
        )
        policy = dict(
            reliable=reliable,
            adaptive_ratio=parameters[0],
            minimum_discontinuity=parameters[1],
            exclusive_feature_origins=exclusive_origins,
        )
        correspondence = independent_scene_witnesses(
            converted, **policy, ratio_name="adaptive_ratio", value_name="discontinuity"
        )
        appearance = independent_scene_witnesses(
            converted, **policy, ratio_name="appearance_adaptive_ratio", value_name="median_patch_error"
        )
        if (
            tuple(keys)
            != tuple(item.region.key for item in converted if item.region.key in set(correspondence) | set(appearance))
            or row["correspondence_hypothesis"] != bool(correspondence)
            or row["appearance_hypothesis"] != bool(appearance)
        ):
            raise ValueError("scene witnesses disagree with recorded region measurements and policy")
        row["witness_parameters"] = tuple(float(v) for v in parameters)
    elif parameters is not None:
        raise ValueError("legacy scene evidence cannot acquire new witness-policy authority")
    for name in ("acquisition_region_keys", "relative_region_keys"):
        keys = row[name]
        if (
            not isinstance(keys, (tuple, list))
            or len(set(keys)) != len(keys)
            or any(not isinstance(key, str) or key not in {r.region.key for r in converted} for key in keys)
        ):
            raise ValueError("invalid relative scene cohort")
        row[name] = tuple(keys)
    if row["version"] in {SCENE_CONTINUITY_VERSION_V4, SCENE_CONTINUITY_VERSION_V5}:
        # A claimed ratio without a recorded history baseline cannot authorize
        # even a detector request; check arithmetic on this new evidence schema.
        for region in converted:
            if region.features < 6 and any(
                value is not None
                for value in (region.discontinuity, region.adaptive_ratio, region.appearance_adaptive_ratio)
            ):
                raise ValueError("relative scene ratios require sufficient current feature support")
            for ratio_name, value_name, history_name in (
                ("adaptive_ratio", "discontinuity", "previous_mean"),
                ("appearance_adaptive_ratio", "median_patch_error", "appearance_previous_mean"),
            ):
                ratio = getattr(region, ratio_name)
                value, history = getattr(region, value_name), getattr(region, history_name)
                # LK may retain a raw patch residual with too few features to
                # support appearance continuity. Preserve that measurement,
                # but match the observer's existing six-feature support gate:
                # an unsupported current value has no adaptive ratio even
                # when a sufficient prior history is still recorded.
                if value_name == "median_patch_error" and region.features < 6:
                    value = None
                if (ratio is None) != (value is None or history is None) or (
                    ratio is not None and not isclose(ratio, value / max(1.0, history), rel_tol=1e-9, abs_tol=1e-9)
                ):
                    raise ValueError("relative scene ratio disagrees with recorded prior history")
        acquisition, relative = scene_relative_cohorts(
            converted, reliable=reliable, adaptive_ratio=parameters[0], exclusive_feature_origins=exclusive_origins
        )
        if row["acquisition_region_keys"] != acquisition or row["relative_region_keys"] != relative:
            raise ValueError("relative scene cohorts disagree with channel measurements")
    elif row["acquisition_region_keys"] or row["relative_region_keys"]:
        raise ValueError("legacy scene evidence cannot acquire weak-layout reset authority")
    return SceneChangeEvidence(**row)


def scene_change_to_dict(value: SceneChangeEvidence) -> dict[str, Any]:
    """Detach and validate before any diagnostic enters a cache or event."""
    if not isinstance(value, SceneChangeEvidence):
        raise TypeError("scene cache requires typed SceneChangeEvidence")
    wire = asdict(value)
    if value.version != SCENE_CONTINUITY_VERSION_V5:
        if (
            value.feature_origin_policy is not None
            or value.source_frame_size is not None
            or value.analysis_frame_size is not None
            or value.origin_masks
        ):
            raise ValueError("legacy typed scene evidence cannot carry exclusive feature-origin fields")
        wire = {key: item for key, item in wire.items() if key not in _ORIGIN_FIELDS}
    result = asdict(scene_change_from_dict(wire))
    return (
        result
        if value.version == SCENE_CONTINUITY_VERSION_V5
        else {key: item for key, item in result.items() if key not in _ORIGIN_FIELDS}
    )


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

    def barrier_for(self, evidence: SceneChangeEvidence) -> bool:
        """Keep the historical explicit policy separate from raw hypotheses."""
        return self.barrier_enabled and evidence.hypothesis

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


class ContentContinuityProviderV2(ContentContinuityProvider):
    """Explicit experimental scene policies with retained rejected controls.

    Actor articulation, blur, compression and repeated source images can raise
    intensity residuals while feature correspondence remains intact. A raw
    appearance spike alone therefore cannot erase tracking/temporal continuity.
    Joint correspondence loss over at least two observed regions is still only
    a conservative tracking boundary; it does not confirm a point or camera.
    """

    def __init__(self, *, mode: str = "diagnostic", **observer_parameters: Any) -> None:
        if not isinstance(mode, str) or mode not in {
            "diagnostic",
            "barrier_correspondence_v2",
            "barrier_hypothesis_cadence_v2",
            "barrier_detector_layout_v2",
        }:
            raise ValueError("unsupported explicit v2 content-continuity policy")
        # Reuse every bounded parameter check before constructing the v2 observer.
        super().__init__(mode="diagnostic", **observer_parameters)
        self._mode = mode
        self._observer = (
            SceneContinuityDetectorV5(**observer_parameters)
            if self.requires_detector_layout
            else SceneContinuityDetectorV2(**observer_parameters)
        )

    @property
    def barrier_enabled(self) -> bool:
        return self._mode != "diagnostic"

    @property
    def supports_relative_layout(self) -> bool:
        return self.requires_detector_layout

    @property
    def requires_detector_layout(self) -> bool:
        return self._mode == "barrier_detector_layout_v2"

    def barrier_for(self, evidence: SceneChangeEvidence) -> bool:
        if self._mode == "barrier_hypothesis_cadence_v2":
            return evidence.hypothesis and len(evidence.regions) >= 2
        return (
            self._mode == "barrier_correspondence_v2"
            and evidence.correspondence_hypothesis
            and len(evidence.regions) >= 2
        )

    def layout_decision(
        self,
        evidence: SceneChangeEvidence,
        probe: Any,
        *,
        detector_model: str | None,
        geometry_valid: bool,
        expected_participants: int | None = None,
        previous_to_current: tuple[float, ...] | None = None,
        previous_camera: tuple[float, ...] | None = None,
    ) -> SceneDecisionEvidence:
        """Corroborate raw image changes without advancing tracking state.

        The0.3 box-IoU gate is exactly the existing observed court-membership
        continuity gate. Count changes, missing geometry and overlapping matches
        abstain; neither a missing person nor a detector ID proves an edit.
        """
        from bai_badminton.perception.players import _box_iou

        metadata = dict(
            frame=evidence.frame,
            previous_frame=evidence.frame - 1,
            raw_hypothesis=evidence.hypothesis,
            detector_frame=None,
            detector_model=None,
            detector_image_sha256=None,
            detector_image_shape=None,
            detector_boxes=(),
            detector_scores=(),
            admitted_indices=(),
            matched_pairs=(),
            previous_region_count=len(evidence.regions),
        )
        v4 = evidence.version in {SCENE_CONTINUITY_VERSION_V4, SCENE_CONTINUITY_VERSION_V5}
        v3 = evidence.version in {SCENE_CONTINUITY_VERSION_V3, SCENE_CONTINUITY_VERSION_V4, SCENE_CONTINUITY_VERSION_V5}
        indices = (
            [i for i, item in enumerate(evidence.regions) if item.region.key in evidence.supporting_region_keys]
            if v3
            else list(range(len(evidence.regions)))
        )
        if v3:
            metadata.update(
                version="detector-layout-scene-decision:v2", supporting_region_keys=evidence.supporting_region_keys
            )
        if v4:
            metadata.update(
                version=(
                    "detector-layout-scene-decision:v4"
                    if evidence.version == SCENE_CONTINUITY_VERSION_V5
                    else "detector-layout-scene-decision:v3"
                ),
                acquisition_region_keys=evidence.acquisition_region_keys,
                relative_region_keys=evidence.relative_region_keys,
                expected_participants=expected_participants,
                geometry_valid=geometry_valid,
                feature_origin_overlap_dependent=feature_origin_overlap_dependent(evidence),
                previous_to_current=previous_to_current,
                previous_camera=previous_camera,
            )
        if probe is None or detector_model is None:
            return SceneDecisionEvidence(
                decision="unknown", reason="current_detector_unavailable_raw_barrier_fallback", **metadata
            )
        if probe.frame_idx != evidence.frame:
            raise ValueError("scene layout probe differs from the current source frame")
        metadata.update(
            detector_frame=probe.frame_idx,
            detector_model=detector_model,
            detector_image_sha256=probe.image_sha256,
            detector_image_shape=probe.image_shape,
            detector_boxes=probe.boxes,
            detector_scores=probe.scores,
            admitted_indices=probe.admitted_indices,
        )
        candidates = tuple(range(len(probe.boxes))) if v3 else probe.admitted_indices
        if v3:
            metadata["layout_indices"] = candidates
        if v4:
            metadata.update(court_polygon=probe.court_polygon, court_indices=probe.court_indices)
        if not geometry_valid:
            return SceneDecisionEvidence(
                decision="unknown", reason="geometry_unavailable_raw_barrier_fallback", **metadata
            )
        if metadata.get("feature_origin_overlap_dependent") and not _complete_court_layout(
            probe.boxes,
            probe.court_indices,
            expected_participants,
            len(evidence.regions),
            geometry_valid,
            probe.court_polygon,
            previous_to_current,
            previous_camera,
        ):
            return SceneDecisionEvidence(
                decision="unknown", reason="overlap_origins_require_complete_current_court_layout", **metadata
            )
        if v4 and not evidence.hypothesis:
            if _weak_court_replacement(
                evidence,
                probe.boxes,
                probe.court_indices,
                expected_participants,
                geometry_valid=geometry_valid,
                court_polygon=probe.court_polygon,
                previous_to_current=previous_to_current,
                previous_camera=previous_camera,
            ):
                return SceneDecisionEvidence(
                    decision="barrier", reason="relative_change_and_complete_court_replacement", **metadata
                )
            return SceneDecisionEvidence(
                decision="unknown", reason="relative_acquisition_without_complete_court_replacement", **metadata
            )
        if not 2 <= len(indices) <= 8 or (not v3 and len(probe.admitted_indices) != len(indices)) or not candidates:
            return SceneDecisionEvidence(
                decision="unknown", reason="participant_count_unresolved_raw_barrier_fallback", **metadata
            )
        previous = np.asarray([evidence.regions[i].region.bbox for i in indices], dtype=np.float64)
        current = np.asarray([probe.boxes[i] for i in candidates], dtype=np.float64)
        overlap = _box_iou(previous, current) >= 0.3
        if (overlap.sum(axis=0) > 1).any() or (overlap.sum(axis=1) > 1).any():
            return SceneDecisionEvidence(
                decision="unknown", reason="ambiguous_layout_correspondence_raw_barrier_fallback", **metadata
            )
        metadata["matched_pairs"] = tuple(
            (indices[a], int(candidates[b])) for a, b in zip(*np.nonzero(overlap), strict=True)
        )
        same = len(metadata["matched_pairs"]) == len(indices)
        if (
            metadata.get("feature_origin_overlap_dependent")
            and not same
            and _positive_nonwitness_court_correspondence(
                evidence, probe.boxes, probe.court_indices, previous_to_current
            )
        ):
            return SceneDecisionEvidence(
                decision="unknown", reason="nonwitness_court_region_preserves_overlap_continuity", **metadata
            )
        if (
            metadata.get("feature_origin_overlap_dependent")
            and not same
            and _camera_explains_witness_layout(evidence, probe.boxes, previous_to_current)
        ):
            return SceneDecisionEvidence(
                decision="unknown", reason="camera_aligned_layout_preserves_overlap_continuity", **metadata
            )
        return SceneDecisionEvidence(
            decision="no_barrier" if same else "barrier",
            reason="complete_current_layout_correspondence" if same else "raw_change_and_current_layout_discontinuity",
            **metadata,
        )

    def tracking_barrier_for_decision(self, decision: SceneDecisionEvidence) -> bool:
        """Suppress only positive complete correspondence; retain raw fallback.

        An unresolved detector layout does not confirm an edit. It preserves the
        existing experimental raw-hypothesis reset rather than silently losing
        previously detected edits. The explicit reason and content epoch retain
        both the uncertainty and the actual tracking action.
        """
        if decision.feature_origin_overlap_dependent:
            return self.requires_detector_layout and decision.decision == "barrier"
        return self.requires_detector_layout and (
            (decision.raw_hypothesis and decision.decision != "no_barrier")
            or (
                decision.version in {"detector-layout-scene-decision:v3", "detector-layout-scene-decision:v4"}
                and decision.decision == "barrier"
            )
        )
