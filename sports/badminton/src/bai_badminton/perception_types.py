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
    # Camera pose: ``cam`` maps the calibration's reference-frame px to this frame's px (3×3), so the
    # court → image homography here is ``cam @ H``.  ``None`` with ``cam_lost`` means the camera is being
    # tracked but the court is not (verifiably) in view — a close-up, another camera; with neither set
    # the camera is not tracked at all (a fixed calibration is assumed, as before).
    cam: NDArray[np.float64] | None = None
    cam_lost: bool = False
    # Scene: which camera shot this frame — "main" (the calibration's camera: analysed), "alt" (another camera
    # that shows the court: calibrated for display, not analysed — replays, reverse angles), "none" (no court
    # in view: close-ups, crowd, graphics).  ``head`` numbers the physical cameras (0 = main); ``court_q`` is
    # the court-line fit's precision (fraction of the projected court lines found painted in the frame).
    view: str | None = None
    head: int | None = None
    court_q: float | None = None

    @property
    def scene(self) -> str:
        """The frame's view, inferred for perception made before scenes were recorded."""
        if self.view is not None:
            return self.view
        return "none" if self.replay else "main"


@dataclass
class ChunkPerception:
    """Contiguous frames [start, end] (inclusive) in order."""

    start: int
    end: int
    frames: list[FramePerception]
    models: dict[str, str] = field(default_factory=dict)  # stage → model@version (provenance)
    ocr: list[ScoreReading] = field(default_factory=list)  # scoreboard readings inside the chunk
    cam_ref: int | None = None  # id of the reference view ``FramePerception.cam`` is relative to (None: untracked)

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
