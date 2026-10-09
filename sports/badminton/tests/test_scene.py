from __future__ import annotations

import cv2
import numpy as np

from bai_badminton.court import fit_homography
from bai_badminton.perception.scene import propose_corners
from bai_badminton.testing.synth import broadcast_homography

MAT_BGR = (41, 49, 16)  # dark court green — inside the court HSV band
FLOOR_BGR = (40, 40, 60)  # surrounding floor, outside it


def _broadcast_frame(w: int = 1280, h: int = 720) -> tuple[np.ndarray, dict[str, tuple[float, float]]]:
    """Floor with a perspective court mat, corners from the synthetic broadcast homography."""
    hom = broadcast_homography()  # 1280×720 view
    corners = {
        n: tuple(float(v) for v in hom.court_to_image(np.array([[x, y]], float))[0])
        for n, (x, y) in {
            "far_left": (-3.05, 6.7),
            "far_right": (3.05, 6.7),
            "near_right": (3.05, -6.7),
            "near_left": (-3.05, -6.7),
        }.items()
    }
    img = np.full((h, w, 3), FLOOR_BGR, np.uint8)
    quad = np.array([corners[k] for k in ("far_left", "far_right", "near_right", "near_left")], np.int32)
    cv2.fillPoly(img, [quad], MAT_BGR)
    return img, corners


def test_proposes_the_mat_corners_on_a_broadcast_view() -> None:
    img, truth = _broadcast_frame()
    prop = propose_corners(img)
    assert prop is not None
    pts, score = prop
    assert score >= 0.6
    for k, (x, y) in truth.items():
        assert abs(pts[k][0] - x) < 6 and abs(pts[k][1] - y) < 6, k
    fit_homography(pts)  # a usable calibration


def test_rejects_a_frame_filled_by_court_colour() -> None:
    # close-ups, intro cards and blank frames: the "court" is the whole frame — its corners are
    # the image corners, not court corners, and must never become an automatic calibration
    img = np.full((360, 640, 3), MAT_BGR, np.uint8)
    img[120:130, 100:110] = 255
    assert propose_corners(img) is None


def test_rejects_a_region_cut_off_by_the_frame_edge() -> None:
    # camera zoomed so the mat runs off the bottom and both sides
    img = np.full((720, 1280, 3), FLOOR_BGR, np.uint8)
    cv2.fillPoly(img, [np.array([[300, 200], [980, 200], [1279, 719], [0, 719]], np.int32)], MAT_BGR)
    assert propose_corners(img) is None
