"""Image-space flight region for one selected court.

Floor geometry gates feet, not airborne objects. Sweep the visible floor upwards
to retain clears and jumps. This is an image-space prior, not a 3-D attribution:
overlapping airborne trajectories from neighboring courts can remain ambiguous.
"""

import cv2
import numpy as np


def is_fixed_camera(frames: list[np.ndarray]) -> bool:
    """Require textured background correspondences, not identical court fits."""
    from bai_badminton.perception.court_lines import _flow, downscale

    if len(frames) < 4:
        return False
    gray = [cv2.cvtColor(downscale(f, 640)[0], cv2.COLOR_BGR2GRAY) for f in frames]
    h, w = gray[0].shape
    points = np.array([[[w * x, h * y] for x in (0.2, 0.5, 0.8) for y in (0.2, 0.5, 0.8)]], np.float64)
    stationary = 0
    for frame in gray[1:]:
        motion = _flow(gray[0], frame)
        if motion is None:
            continue
        moved = cv2.perspectiveTransform(points, motion)
        stationary += bool(np.max(np.linalg.norm(moved - points, axis=-1)) < 0.004 * w)
    return stationary / (len(frames) - 1) >= 0.85


def flight_mask(polygon: np.ndarray, frame_size: tuple[int, int], size: tuple[int, int]) -> np.ndarray:
    w, h = frame_size
    mw, mh = size
    out = np.zeros((mh, mw), np.uint8)
    poly = np.asarray(polygon, np.float32).reshape(-1, 2)
    if len(poly) < 3 or not np.isfinite(poly).all():
        return out
    # Clip before extrusion: off-screen extrapolated corners must not expand
    # the accepted image region to cover the neighboring courts.
    rect = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
    area, clipped = cv2.intersectConvexConvex(cv2.convexHull(poly), rect)
    if area <= 0 or clipped is None:
        return out
    floor = clipped.reshape(-1, 2)
    air = floor - np.array([0, 0.35 * h], np.float32)
    hull = cv2.convexHull(np.concatenate([floor, air]))
    scaled = hull * np.array([mw / w, mh / h], np.float32)
    cv2.fillConvexPoly(out, np.round(scaled).astype(np.int32), 1)
    # Small, resolution-independent tolerance at line edges.
    r = max(1, round(0.008 * mw))
    return cv2.dilate(out, np.ones((2 * r + 1, 2 * r + 1), np.uint8))
