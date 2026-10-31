"""Per-frame perception results handed from the perception stage to the match engine."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from bai_badminton.perception.calibration_state import CalibrationState


@dataclass(frozen=True)
class RacketObservation:
    """Observed image ellipse and shaft support; never a wrist-derived substitute."""

    center: tuple[float, float]
    axes: tuple[float, float]  # ellipse diameters in image pixels
    angle: float
    confidence: float  # uncalibrated geometric support
    wrist: int
    method: str = "opencv_ellipse_shaft_v1"

    def __post_init__(self) -> None:
        values = [*self.center, *self.axes, self.angle, self.confidence]
        if (
            len(self.center) != 2
            or len(self.axes) != 2
            or not np.isfinite(values).all()
            or min(self.axes) <= 0
            or not 0 <= self.confidence <= 1
            or self.wrist not in (9, 10)
            or self.method != "opencv_ellipse_shaft_v1"
        ):
            raise ValueError("invalid observed racket geometry")
        object.__setattr__(self, "center", tuple(float(value) for value in self.center))
        object.__setattr__(self, "axes", tuple(float(value) for value in self.axes))

    def overlap(self, point: tuple[float, float]) -> float:
        delta = np.asarray(point) - self.center
        angle = np.deg2rad(self.angle)
        rotation = np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]])
        distance = float(np.linalg.norm((rotation @ delta) / (np.asarray(self.axes) / 2)))
        return max(0.0, 1.0 - max(0.0, distance - 0.75) / 0.5)

    def transformed(self, matrix: NDArray[np.float64]) -> RacketObservation | None:
        import cv2

        phase = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        local = np.column_stack((np.cos(phase), np.sin(phase))) * (np.asarray(self.axes) / 2)
        angle = np.deg2rad(self.angle)
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        points = local @ rotation.T + self.center
        homogeneous = np.column_stack((points, np.ones(len(points)))) @ np.asarray(matrix).T
        if not np.isfinite(homogeneous).all() or np.any(np.abs(homogeneous[:, 2]) < 1e-8):
            return None
        mapped = (homogeneous[:, :2] / homogeneous[:, 2, None]).astype(np.float32)
        center, axes, orientation = cv2.fitEllipse(mapped)
        return RacketObservation(tuple(center), tuple(axes), orientation, self.confidence, self.wrist)


@dataclass
class PersonObs:
    track_id: int
    bbox: NDArray[np.float64]  # (4,) x1,y1,x2,y2 in analysis-proxy px
    conf: float
    kps: NDArray[np.float64] | None = None  # (17, 3)
    court_xy: tuple[float, float] | None = None  # feet in court metres (if calibrated)
    appearance: NDArray[np.float32] | None = None  # colour signature for re-identification
    raw_track_id: int | None = None  # ByteTrack ID before optional neural/motion association
    detector_matched: bool | None = None  # unique match to this frame's person detection
    identity_method: str | None = None  # uncalibrated association policy/reason, never a person name
    racket: RacketObservation | None = None


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
    # None is reserved for pre-v7/synthetic observations, not current perception.
    calibration_state: CalibrationState | None = None
    # True only for a frame where the person detector actually ran.
    detector_observed: bool | None = None
    # Scheduled pose cadence, not a claim of successful keypoint observation.
    pose_stride: int | None = None  # None legacy/unknown, 0 disabled

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
