"""Badminton court model and image↔court homography.

Court coordinates are metres with the origin at the centre of the net, ``x`` across the court
(left→right as seen from the near end) and ``y`` along it (``y < 0`` near half, ``y > 0`` far
half).  Dimensions follow the BWF Laws (doubles court 13.40 m × 6.10 m; singles sideline 0.46 m
inside; short service line 1.98 m from the net; doubles long service line 0.76 m inside the
back boundary line).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import cv2
import numpy as np
from numpy.typing import NDArray

LENGTH = 13.40
WIDTH_DOUBLES = 6.10
WIDTH_SINGLES = 5.18
HALF_LEN = LENGTH / 2
SHORT_SERVICE = 1.98
DOUBLES_LONG_SERVICE_INSET = 0.76
NET_HEIGHT_CENTRE = 1.524
NET_HEIGHT_POSTS = 1.55

# Named reference points (court metres) — the keypoint vocabulary for calibration.
REFERENCE_POINTS: dict[str, tuple[float, float]] = {
    # doubles outer corners
    "far_left": (-WIDTH_DOUBLES / 2, HALF_LEN),
    "far_right": (WIDTH_DOUBLES / 2, HALF_LEN),
    "near_right": (WIDTH_DOUBLES / 2, -HALF_LEN),
    "near_left": (-WIDTH_DOUBLES / 2, -HALF_LEN),
    # singles corners
    "far_left_singles": (-WIDTH_SINGLES / 2, HALF_LEN),
    "far_right_singles": (WIDTH_SINGLES / 2, HALF_LEN),
    "near_right_singles": (WIDTH_SINGLES / 2, -HALF_LEN),
    "near_left_singles": (-WIDTH_SINGLES / 2, -HALF_LEN),
    # net / centre line intersections (on the ground)
    "net_left": (-WIDTH_DOUBLES / 2, 0.0),
    "net_right": (WIDTH_DOUBLES / 2, 0.0),
    # short service line × centre line
    "far_short_centre": (0.0, SHORT_SERVICE),
    "near_short_centre": (0.0, -SHORT_SERVICE),
    "far_short_left": (-WIDTH_DOUBLES / 2, SHORT_SERVICE),
    "far_short_right": (WIDTH_DOUBLES / 2, SHORT_SERVICE),
    "near_short_left": (-WIDTH_DOUBLES / 2, -SHORT_SERVICE),
    "near_short_right": (WIDTH_DOUBLES / 2, -SHORT_SERVICE),
}

# Lines for rendering (pairs of reference names in court metres)
COURT_LINES: tuple[tuple[tuple[float, float], tuple[float, float]], ...] = (
    ((-WIDTH_DOUBLES / 2, -HALF_LEN), (WIDTH_DOUBLES / 2, -HALF_LEN)),
    ((-WIDTH_DOUBLES / 2, HALF_LEN), (WIDTH_DOUBLES / 2, HALF_LEN)),
    ((-WIDTH_DOUBLES / 2, -HALF_LEN), (-WIDTH_DOUBLES / 2, HALF_LEN)),
    ((WIDTH_DOUBLES / 2, -HALF_LEN), (WIDTH_DOUBLES / 2, HALF_LEN)),
    ((-WIDTH_SINGLES / 2, -HALF_LEN), (-WIDTH_SINGLES / 2, HALF_LEN)),
    ((WIDTH_SINGLES / 2, -HALF_LEN), (WIDTH_SINGLES / 2, HALF_LEN)),
    ((-WIDTH_DOUBLES / 2, -SHORT_SERVICE), (WIDTH_DOUBLES / 2, -SHORT_SERVICE)),
    ((-WIDTH_DOUBLES / 2, SHORT_SERVICE), (WIDTH_DOUBLES / 2, SHORT_SERVICE)),
    (
        (-WIDTH_DOUBLES / 2, -(HALF_LEN - DOUBLES_LONG_SERVICE_INSET)),
        (WIDTH_DOUBLES / 2, -(HALF_LEN - DOUBLES_LONG_SERVICE_INSET)),
    ),
    (
        (-WIDTH_DOUBLES / 2, HALF_LEN - DOUBLES_LONG_SERVICE_INSET),
        (WIDTH_DOUBLES / 2, HALF_LEN - DOUBLES_LONG_SERVICE_INSET),
    ),
    ((0.0, -HALF_LEN), (0.0, -SHORT_SERVICE)),
    ((0.0, SHORT_SERVICE), (0.0, HALF_LEN)),
    ((-WIDTH_DOUBLES / 2, 0.0), (WIDTH_DOUBLES / 2, 0.0)),  # net (ground projection)
)


class Half(StrEnum):
    NEAR = "near"
    FAR = "far"


@dataclass(frozen=True)
class Homography:
    """Image(px) ↔ court(m) mapping for one camera shot."""

    H: NDArray[np.float64]  # court → image (3×3)
    reprojection_error_px: float
    n_points: int

    @property
    def H_inv(self) -> NDArray[np.float64]:  # image → court
        return np.linalg.inv(self.H)

    def image_to_court(self, pts: NDArray[np.floating]) -> NDArray[np.float64]:
        pts = np.asarray(pts, dtype=np.float64).reshape(-1, 1, 2)
        return cv2.perspectiveTransform(pts, self.H_inv).reshape(-1, 2)

    def court_to_image(self, pts: NDArray[np.floating]) -> NDArray[np.float64]:
        pts = np.asarray(pts, dtype=np.float64).reshape(-1, 1, 2)
        return cv2.perspectiveTransform(pts, self.H).reshape(-1, 2)

    def to_json(self) -> dict[str, object]:
        return {"H": self.H.tolist(), "reprojection_error_px": self.reprojection_error_px, "n_points": self.n_points}

    @classmethod
    def from_json(cls, d: dict[str, object]) -> Homography:
        return cls(
            H=np.asarray(d["H"], dtype=np.float64),
            reprojection_error_px=float(d["reprojection_error_px"]),  # type: ignore[arg-type]
            n_points=int(d["n_points"]),  # type: ignore[call-overload]
        )


class CalibrationError(ValueError):
    pass


def fit_homography(correspondences: dict[str, tuple[float, float]], ransac_px: float = 6.0) -> Homography:
    """Fit court→image homography from named image points (≥4, RANSAC when ≥5)."""
    names = [n for n in correspondences if n in REFERENCE_POINTS]
    unknown = set(correspondences) - set(names)
    if unknown:
        raise CalibrationError(f"unknown reference points: {sorted(unknown)}")
    if len(names) < 4:
        raise CalibrationError("need at least 4 reference points")
    src = np.array([REFERENCE_POINTS[n] for n in names], dtype=np.float64)
    dst = np.array([correspondences[n] for n in names], dtype=np.float64)
    method = cv2.RANSAC if len(names) >= 5 else 0
    H, mask = cv2.findHomography(src, dst, method, ransac_px)
    if H is None:
        raise CalibrationError("degenerate point configuration")
    proj = cv2.perspectiveTransform(src.reshape(-1, 1, 2), H).reshape(-1, 2)
    inl = mask.ravel().astype(bool) if mask is not None else np.ones(len(names), bool)
    err = float(np.sqrt(((proj[inl] - dst[inl]) ** 2).sum(axis=1)).mean())
    if not np.isfinite(err):
        raise CalibrationError("non-finite reprojection error")
    return Homography(H=H, reprojection_error_px=err, n_points=int(inl.sum()))


def half_of(court_y: float) -> Half:
    return Half.NEAR if court_y < 0 else Half.FAR


def in_court(court_x: float, court_y: float, *, singles: bool = True, margin: float = 0.0) -> bool:
    w = (WIDTH_SINGLES if singles else WIDTH_DOUBLES) / 2 + margin
    return abs(court_x) <= w and abs(court_y) <= HALF_LEN + margin


def zone(court_x: float, court_y: float) -> tuple[str, str]:
    """(depth, width) zone from the perspective of the player standing on that half."""
    near = court_y < 0
    d = abs(court_y)
    depth = "front" if d < SHORT_SERVICE + 0.6 else ("mid" if d < HALF_LEN - 1.6 else "rear")
    # width from the player's own view (facing the net): near player's right = +x
    xr = court_x if near else -court_x
    third = WIDTH_SINGLES / 6
    width = "left" if xr < -third else ("right" if xr > third else "centre")
    return depth, width
