"""Per-frame perception results handed from the perception stage to the match engine."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray


@dataclass
class PersonObs:
    track_id: int
    bbox: NDArray[np.float64]  # (4,) x1,y1,x2,y2 in analysis-proxy px
    conf: float
    kps: NDArray[np.float64] | None = None  # (17, 3)
    court_xy: tuple[float, float] | None = None  # feet in court metres (if calibrated)
    appearance: NDArray[np.float32] | None = None  # colour signature for re-identification


@dataclass
class FramePerception:
    frame_idx: int
    shuttle_xy: tuple[float, float] | None
    shuttle_conf: float
    persons: list[PersonObs] = field(default_factory=list)
    replay: bool = False
    shot_id: int = 0  # camera shot (cut index); calibration is per shot


@dataclass
class ChunkPerception:
    """Contiguous frames [start, end] (inclusive) in order."""

    start: int
    end: int
    frames: list[FramePerception]
    models: dict[str, str] = field(default_factory=dict)  # stage → model@version (provenance)

    def __post_init__(self) -> None:
        if len(self.frames) != self.end - self.start + 1:
            raise ValueError("chunk frames must cover [start, end] exactly")
        if any(f.frame_idx != self.start + i for i, f in enumerate(self.frames)):
            raise ValueError("chunk frames out of order")


@dataclass
class ScoreReading:
    """A scoreboard OCR reading (broadcast score bug)."""

    frame_idx: int
    rows: tuple[tuple[str, int], tuple[str, int]]  # (name, points) top row, bottom row
    games: tuple[int, int] | None = None
    conf: float = 0.0
