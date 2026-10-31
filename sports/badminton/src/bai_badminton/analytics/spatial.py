"""Conservative court-plane path estimates; policy, not a validated biomechanical measure.

Coordinates are metres at player feet. Never interpolate across missing observations,
camera rejection, duplicate identities or a track switch. Thresholds bound gross failure
modes and do not establish physical accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import pairwise

import numpy as np

from bai_badminton.court import HALF_LEN, WIDTH_DOUBLES

METHOD = "court_path_v2"
MIN_COURT_QUALITY = 0.6
MAX_GAP_S = 0.25
MAX_SPEED_M_S = 12.0
SAMPLE_S = 0.2
JITTER_M = 0.05


def court_point_valid(x: float, y: float) -> bool:
    return bool(np.isfinite([x, y]).all() and abs(x) <= WIDTH_DOUBLES / 2 + 0.35 and abs(y) <= HALF_LEN + 0.75)


@dataclass
class TravelSample:
    """Travel in court axes: 0 degrees is +x; 90 is +y (toward the far end).

    This is ground-plane direction of travel, never body orientation or facing.
    """

    frame_start: int
    frame_end: int
    track_id: int
    vx_m_s: float
    vy_m_s: float
    speed_m_s: float
    heading_deg: float | None

    def to_public(self, fps: float) -> dict[str, int | float | None]:
        return {
            "frame_start": self.frame_start,
            "frame_end": self.frame_end,
            "pts_us": round(self.frame_end * 1_000_000 / fps),
            "track_id": self.track_id,
            "vx_m_s": round(self.vx_m_s, 3),
            "vy_m_s": round(self.vy_m_s, 3),
            "speed_m_s": round(self.speed_m_s, 3),
            "heading_deg": round(self.heading_deg, 1) if self.heading_deg is not None else None,
        }


@dataclass
class Movement:
    xy: np.ndarray
    weights: list[float]
    accepted_samples: int = 0
    observed_s: float = 0
    segments: int = 0
    motion: list[TravelSample] = field(default_factory=list)

    @property
    def distance_m(self) -> float:
        return sum(self.weights)


def movement(
    xy: np.ndarray,
    frames: list[int],
    track_ids: list[int],
    valid: list[bool],
    fps: float,
) -> Movement:
    """Return a median-smoothed, 5 Hz path with explicit continuous observation support."""
    pts = np.asarray(xy, dtype=float).reshape(-1, 2)
    if not (len(pts) == len(frames) == len(track_ids) == len(valid)):
        raise ValueError("spatial sample arrays must have equal lengths")
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError("fps must be finite and positive")
    out = Movement(np.empty((0, 2)), [])
    destinations: list[np.ndarray] = []
    groups: list[list[int]] = []
    group: list[int] = []
    for i, (x, y) in enumerate(pts):
        accepted = valid[i] and track_ids[i] >= 0 and court_point_valid(x, y)
        if accepted:
            out.accepted_samples += 1
        if group:
            j = group[-1]
            dt = (frames[i] - frames[j]) / fps
            continuous = (
                accepted
                and track_ids[i] == track_ids[j]
                and frames[i] == frames[j] + 1
                and 0 < dt <= MAX_GAP_S
                and float(np.linalg.norm(pts[i] - pts[j])) <= MAX_SPEED_M_S * dt
            )
            if not continuous:
                groups.append(group)
                group = []
        if accepted:
            group.append(i)
    if group:
        groups.append(group)
    for indices in groups:
        if len(indices) < 2:
            continue
        # Local three-sample median reduces isolated foot-point jitter. No values
        # from another continuity group participate in smoothing.
        smoothed = np.array(
            [np.median(pts[indices[max(0, j - 1) : min(len(indices), j + 2)]], axis=0) for j in range(len(indices))]
        )
        smoothed[0], smoothed[-1] = pts[indices[0]], pts[indices[-1]]
        selected = [0]
        for j in range(1, len(indices)):
            if (frames[indices[j]] - frames[indices[selected[-1]]]) / fps >= SAMPLE_S:
                selected.append(j)
        if selected[-1] != len(indices) - 1:
            last_dt = (frames[indices[-1]] - frames[indices[selected[-1]]]) / fps
            if last_dt >= SAMPLE_S / 2:
                selected.append(len(indices) - 1)
        for left, right in pairwise(selected):
            dt = (frames[indices[right]] - frames[indices[left]]) / fps
            displacement = float(np.linalg.norm(smoothed[right] - smoothed[left]))
            if displacement > MAX_SPEED_M_S * dt:
                continue
            distance = displacement if displacement >= JITTER_M else 0.0
            delta = smoothed[right] - smoothed[left] if distance else np.zeros(2)
            vx, vy = (float(v) / dt for v in delta)
            heading = float(np.degrees(np.arctan2(vy, vx)) % 360) if distance else None
            out.motion.append(
                TravelSample(
                    frame_start=int(frames[indices[left]]),
                    frame_end=int(frames[indices[right]]),
                    track_id=int(track_ids[indices[right]]),
                    vx_m_s=vx,
                    vy_m_s=vy,
                    speed_m_s=distance / dt,
                    heading_deg=heading,
                )
            )
            destinations.append(smoothed[right])
            out.weights.append(distance)
            out.observed_s += dt
            out.segments += 1
    out.xy = np.asarray(destinations, dtype=float).reshape(-1, 2)
    return out
