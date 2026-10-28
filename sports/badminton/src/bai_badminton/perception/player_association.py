"""Short-lived canonical visual identities from neural appearance and motion.

Descriptors stay private and bounded; no roster identity or shirt-colour inference
is made. Thresholds are uncalibrated matching heuristics, not probabilities.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import isfinite

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import linear_sum_assignment

MAX_TRACKS = 16
DESCRIPTOR_SIZE = 512
MIN_CONFIDENCE = 0.5
MIN_COSINE = 0.8
ASSIGNMENT_MARGIN = 0.05
OVERLAP_IOU = 0.3
RETENTION_SECONDS = 1.0
POLICY_FINGERPRINT = "neural-motion-v3:512:ttl1:cos0.8:margin0.05:iou0.3:gallery4:tracks16"

Box = NDArray[np.float64]
Descriptor = NDArray[np.float64]
RawTrack = tuple[int, Box, float]


def _feet(box: Box) -> Box:
    return np.array([(box[0] + box[2]) / 2, box[3]], dtype=np.float64)


def _iou(a: Box, b: Box) -> float:
    intersection = float(np.prod(np.maximum(0, np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2]))))
    union = float(np.prod(a[2:] - a[:2]) + np.prod(b[2:] - b[:2])) - intersection
    return intersection / union


@dataclass
class _Identity:
    frame: int
    box: Box
    previous: tuple[int, Box] | None = None
    gallery: deque[Descriptor] = field(default_factory=lambda: deque(maxlen=4))
    ambiguous: bool = False


class PersistentPlayerAssociator:
    """Associate at most sixteen fresh tracks; ``-1`` means unresolved.

    ``observed`` must mean a unique match to a current detector observation, not
    merely that the detector ran. Unobserved rows may carry an existing raw link
    but never extend its lifetime, teach appearance, create or relink identity.
    Call ``reset`` on cuts/calibration changes. Absolute frame indices continue
    increasing across reset, so birth IDs cannot collide with earlier output.
    """

    def __init__(self, fps: float) -> None:
        if isinstance(fps, bool) or not isinstance(fps, (int, float)) or not isfinite(fps) or fps <= 0:
            raise ValueError("a finite positive frame rate is required")
        self.fps = float(fps)
        self._tracks: dict[int, _Identity] = {}
        self._raw_links: dict[int, int] = {}
        self._last_frame = -1
        self.last_reason: list[str] = []

    @property
    def policy_fingerprint(self) -> str:
        return POLICY_FINGERPRINT

    def reset(self) -> None:
        self._tracks.clear()
        self._raw_links.clear()
        self.last_reason = []

    def _validate(
        self,
        frame_idx: int,
        tracks: list[RawTrack],
        embeddings: NDArray | None,
        observed: list[bool],
    ) -> tuple[list[RawTrack], list[Descriptor | None]]:
        if (
            isinstance(frame_idx, bool)
            or not isinstance(frame_idx, int)
            or frame_idx <= self._last_frame
            or frame_idx < 0
            or frame_idx * MAX_TRACKS + MAX_TRACKS > 2**31 - 1
        ):
            raise ValueError("increasing nonnegative frames with int32 birth IDs are required")
        if len(tracks) > MAX_TRACKS or len(observed) != len(tracks) or any(type(v) is not bool for v in observed):
            raise ValueError("at most sixteen tracks and matching boolean observation flags required")
        cleaned = []
        raw_ids = set()
        for raw_id, box, score in tracks:
            try:
                source = np.asarray(box)
                b = np.asarray(box, dtype=np.float64)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("invalid track box") from exc
            if (
                isinstance(raw_id, bool)
                or not isinstance(raw_id, int)
                or raw_id < 0
                or raw_id in raw_ids
                or source.dtype.kind == "b"
                or b.shape != (4,)
                or not np.isfinite(b).all()
                or np.any(b[2:] <= b[:2])
                or isinstance(score, bool)
                or not isinstance(score, (int, float))
                or not isfinite(score)
                or not 0 <= score <= 1
            ):
                raise ValueError("unique raw IDs, finite positive boxes and scores in [0, 1] required")
            raw_ids.add(raw_id)
            cleaned.append((raw_id, b.copy(), float(score)))
        features: list[Descriptor | None] = [None] * len(tracks)
        if embeddings is not None:
            try:
                matrix = np.asarray(embeddings, dtype=np.float64)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("invalid neural descriptors") from exc
            if len(tracks) == 0 and matrix.size == 0:
                matrix = matrix.reshape(0, DESCRIPTOR_SIZE)
            if matrix.shape != (len(tracks), DESCRIPTOR_SIZE) or not np.isfinite(matrix).all():
                raise ValueError("finite 512-dimensional neural descriptors required")
            for i, vector in enumerate(matrix):
                norm = float(np.linalg.norm(vector))
                if isfinite(norm) and norm > 1e-8:
                    features[i] = vector / norm
        return cleaned, features

    def _motion(self, state: _Identity, box: Box, frame_idx: int) -> tuple[float, float]:
        height = float(state.box[3] - state.box[1])
        other_height = float(box[3] - box[1])
        if max(height, other_height) / min(height, other_height) > 2:
            return float("inf"), 0.5
        predicted = _feet(state.box)
        if state.previous is not None:
            old_frame, old_box = state.previous
            velocity = (predicted - _feet(old_box)) / (state.frame - old_frame)
            speed = float(np.linalg.norm(velocity))
            cap = 3 * height / self.fps
            if speed > cap:
                velocity *= cap / speed
            predicted = predicted + velocity * (frame_idx - state.frame)
        distance = float(np.linalg.norm(_feet(box) - predicted)) / ((height + other_height) / 2)
        limit = max(0.5, 3 * (frame_idx - state.frame) / self.fps)
        return distance, limit

    def _bind(self, raw_id: int, canonical: int) -> None:
        self._raw_links = {raw: value for raw, value in self._raw_links.items() if value != canonical}
        self._raw_links[raw_id] = canonical

    def update(
        self,
        frame_idx: int,
        tracks: list[RawTrack],
        embeddings: NDArray | None,
        *,
        observed: list[bool],
    ) -> list[int]:
        tracks, features = self._validate(frame_idx, tracks, embeddings, observed)
        self._last_frame = frame_idx
        self._tracks = {
            key: value
            for key, value in self._tracks.items()
            if (frame_idx - value.frame) / self.fps <= RETENTION_SECONDS
        }
        self._raw_links = {raw: key for raw, key in self._raw_links.items() if key in self._tracks}
        output = [-1] * len(tracks)
        self.last_reason = ["not_observed"] * len(tracks)
        overlapping = [
            any(i != j and _iou(row[1], other[1]) >= OVERLAP_IOU for j, other in enumerate(tracks))
            for i, row in enumerate(tracks)
        ]
        for i, (raw, _, _) in enumerate(tracks):
            if overlapping[i] and (key := self._raw_links.get(raw)) is not None:
                self._tracks[key].ambiguous = True
        active = [i for i, row in enumerate(tracks) if observed[i] and row[2] >= MIN_CONFIDENCE]
        keys = sorted(self._tracks)
        scores = np.full((len(active), len(keys)), -1e6)
        plausible = np.zeros(scores.shape, dtype=bool)
        for row_idx, i in enumerate(active):
            raw, box, _ = tracks[i]
            feature = features[i]
            motion = [self._motion(self._tracks[key], box, frame_idx) for key in keys]
            similarities = [
                max((float(np.dot(feature, old)) for old in self._tracks[key].gallery), default=-1.0)
                if feature is not None
                else -1.0
                for key in keys
            ]
            for col, key in enumerate(keys):
                state = self._tracks[key]
                distance, limit = motion[col]
                if distance > limit:
                    continue
                same_raw = self._raw_links.get(raw) == key
                neural = feature is not None and bool(state.gallery)
                if neural and similarities[col] < MIN_COSINE:
                    continue
                if not neural and not same_raw:
                    continue
                plausible[row_idx, col] = True
                if not neural and (
                    state.ambiguous or overlapping[i] or sum(distance <= limit for distance, limit in motion) > 1
                ):
                    # A raw ID cannot distinguish multiple plausible prior people
                    # when no comparison with a trusted neural gallery is available.
                    continue
                if state.ambiguous or overlapping[i]:
                    # Once identity became ambiguous, separation cannot prove
                    # which person emerged. Require distinctive appearance
                    # against every still-live gallery, even outside motion gates.
                    alternatives = [
                        value
                        for j, value in enumerate(similarities)
                        if j != col and (state.ambiguous or motion[j][0] <= motion[j][1] * 2)
                    ]
                    unknown_competitor = any(
                        j != col
                        and not self._tracks[other].gallery
                        and (self._tracks[other].ambiguous or motion[j][0] <= motion[j][1] * 2)
                        for j, other in enumerate(keys)
                    )
                    if (
                        not neural
                        or unknown_competitor
                        or (alternatives and similarities[col] - max(alternatives) < ASSIGNMENT_MARGIN)
                    ):
                        continue
                appearance = similarities[col] if neural else 1.0
                scores[row_idx, col] = 0.65 * appearance + 0.35 * (1 - distance / limit) + 0.02 * same_raw
        accepted: list[tuple[int, int]] = []
        if active and keys:
            # Dummy columns make withholding an association a valid global choice.
            padded = np.concatenate([scores, np.zeros((len(active), len(active)))], axis=1)
            row_indices, col_indices = linear_sum_assignment(padded, maximize=True)
            for row_idx, col in zip(row_indices, col_indices, strict=True):
                if col >= len(keys) or scores[row_idx, col] <= 0:
                    continue
                value = scores[row_idx, col]
                row_alternatives = np.delete(scores[row_idx], col)
                col_alternatives = np.delete(scores[:, col], row_idx)
                if (
                    value - max(0.0, float(row_alternatives.max(initial=-1e6))) < ASSIGNMENT_MARGIN
                    or value - max(0.0, float(col_alternatives.max(initial=-1e6))) < ASSIGNMENT_MARGIN
                ):
                    continue
                accepted.append((active[row_idx], keys[col]))
        for i, key in accepted:
            raw, box, _ = tracks[i]
            state = self._tracks[key]
            used_neural = features[i] is not None and bool(state.gallery)
            state.previous = (state.frame, state.box.copy())
            state.frame, state.box, state.ambiguous = frame_idx, box, False
            if features[i] is not None and not overlapping[i]:
                state.gallery.append(features[i].copy())
            self._bind(raw, key)
            output[i], self.last_reason[i] = key, "neural_motion_match" if used_neural else "raw_continuity"
        # Ambiguous observations retain old hypotheses but never create duplicate people.
        births = []
        for row_idx, i in enumerate(active):
            if output[i] >= 0:
                continue
            candidates = [keys[col] for col in np.flatnonzero(plausible[row_idx])]
            if candidates:
                for key in candidates:
                    self._tracks[key].ambiguous = True
                self.last_reason[i] = "ambiguous_assignment"
            elif overlapping[i]:
                self.last_reason[i] = "overlapping_new_track"
            else:
                births.append(i)
        for rank, i in enumerate(sorted(births, key=lambda i: tracks[i][0])):
            if len(self._tracks) >= MAX_TRACKS:
                self.last_reason[i] = "identity_capacity"
                continue
            key = frame_idx * MAX_TRACKS + rank + 1
            raw, box, _ = tracks[i]
            state = _Identity(frame_idx, box)
            if features[i] is not None:
                state.gallery.append(features[i].copy())
            self._tracks[key] = state
            self._bind(raw, key)
            output[i], self.last_reason[i] = key, "new_visual_identity"
        used = set(output) - {-1}
        for i, (raw, _, _) in enumerate(tracks):
            if observed[i]:
                continue
            key = self._raw_links.get(raw)
            if key is not None and key not in used and not self._tracks[key].ambiguous:
                output[i], self.last_reason[i] = key, "unobserved_raw_carry"
                used.add(key)
        return output
