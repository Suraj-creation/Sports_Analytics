"""
Shared, resolution-aware court file I/O.

Different scripts in this repo annotate the court against whatever video
they happen to be pointed at (video_raw is 1920x1080, video_fixed is
1280x720). A court file saved against one resolution is meaningless on a
video of a different resolution unless the corners are rescaled.

Every court JSON written through this module carries the frame size it was
measured against (`frame_size: {width, height}`). Loading always requires
the *current* video's target size and rescales the stored corners to it, so
callers never have to know or guess which resolution a file came from.
"""
import json
from typing import List, Tuple

from shapely.geometry import Polygon

CORNER_LABELS = ["TL", "TR", "BR", "BL"]


def _scale_points(
    points: List[Tuple[float, float]],
    src_size: Tuple[int, int],
    dst_size: Tuple[int, int],
) -> List[Tuple[float, float]]:
    sw, sh = src_size
    dw, dh = dst_size
    if (sw, sh) == (dw, dh):
        return [tuple(p) for p in points]
    sx, sy = dw / sw, dh / sh
    return [(x * sx, y * sy) for x, y in points]


def load_court_corners(
    path: str, target_size: Tuple[int, int]
) -> List[Tuple[float, float]]:
    """Load TL/TR/BR/BL corners from a court JSON, scaled to target_size.

    target_size is (width, height) of the video you're about to process.
    Raises ValueError if the file predates frame_size tracking, since the
    corners can't be scaled correctly without knowing their source
    resolution.
    """
    with open(path) as f:
        data = json.load(f)

    if "frame_size" not in data:
        raise ValueError(
            f"{path} has no 'frame_size' metadata - it predates "
            "resolution-aware court files and can't be safely rescaled. "
            "Re-annotate it or add frame_size manually before using it."
        )

    src_size = (data["frame_size"]["width"], data["frame_size"]["height"])

    corners = data["corners"]
    if isinstance(corners, dict):
        points = [tuple(corners[label]) for label in CORNER_LABELS]
    else:
        points = [tuple(p) for p in corners]

    return _scale_points(points, src_size, target_size)


def load_court_polygon(path: str, target_size: Tuple[int, int]) -> Polygon:
    return Polygon(load_court_corners(path, target_size))


def save_court_corners(
    path: str,
    corners: List[Tuple[float, float]],
    frame_size: Tuple[int, int],
) -> None:
    """Save TL/TR/BR/BL corners along with the frame size they were measured against."""
    width, height = frame_size
    data = {
        "frame_size": {"width": width, "height": height},
        "corners": [list(p) for p in corners],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
