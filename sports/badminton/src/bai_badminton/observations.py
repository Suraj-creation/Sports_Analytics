"""Dense per-window observation arrays consumed by the temporal engine.

Perception emits per-frame results; the temporal engine assembles them into a ``WindowObs`` —
dense numpy arrays over a contiguous frame range — so every temporal component is a vectorised,
deterministic function of arrays (easy to test, to replay from recorded fixtures, and to run on
recorded perception without a GPU).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from bai_badminton.perception.shuttle_post import Track

PLAYER_IDS = ("P1", "P2")


@dataclass
class PlayerSeries:
    """Per-frame observations of one *identified* player (``player_id``) over a window."""

    bbox: NDArray[np.float64]  # (n, 4) x1,y1,x2,y2 — NaN rows when not observed
    kps: NDArray[np.float64]  # (n, 17, 3) — NaN when pose not run / not observed
    court_xy: NDArray[np.float64]  # (n, 2) feet position in court metres — NaN without calibration

    @classmethod
    def empty(cls, n: int) -> PlayerSeries:
        return cls(
            bbox=np.full((n, 4), np.nan),
            kps=np.full((n, 17, 3), np.nan),
            court_xy=np.full((n, 2), np.nan),
        )

    @property
    def present(self) -> NDArray[np.bool_]:
        return np.isfinite(self.bbox[:, 0])

    @property
    def height(self) -> NDArray[np.float64]:
        return self.bbox[:, 3] - self.bbox[:, 1]

    def feet(self) -> NDArray[np.float64]:
        """Bottom-centre of the box (ground contact point in the image)."""
        return np.stack([(self.bbox[:, 0] + self.bbox[:, 2]) / 2, self.bbox[:, 3]], axis=1)


@dataclass
class WindowObs:
    frame0: int
    fps: float
    shuttle: Track
    players: dict[str, PlayerSeries]
    replay: NDArray[np.bool_] = field(default_factory=lambda: np.zeros(0, bool))
    pose_stride: NDArray[np.int64] | None = None  # -1 unknown; 0 disabled; >0 actual schedule

    def __post_init__(self) -> None:
        n = len(self.shuttle)
        if self.replay.shape[0] == 0:
            self.replay = np.zeros(n, bool)
        if self.pose_stride is None:
            self.pose_stride = np.full(n, -1, dtype=np.int64)
        elif (
            self.pose_stride.shape != (n,)
            or not np.issubdtype(self.pose_stride.dtype, np.integer)
            or (self.pose_stride < -1).any()
        ):
            raise ValueError("pose schedule must contain one integer >= -1 per frame")
        for pid, s in self.players.items():
            if s.bbox.shape[0] != n:
                raise ValueError(f"player {pid} series length {s.bbox.shape[0]} != {n}")

    @property
    def n(self) -> int:
        return len(self.shuttle)

    @property
    def frames(self) -> NDArray[np.int64]:
        return np.arange(self.frame0, self.frame0 + self.n, dtype=np.int64)

    def idx(self, frame: int) -> int:
        return frame - self.frame0
