"""
court_crop.py
-------------
Court geometry utilities.  Provides a standardised geometry dict that the
rest of the pipeline can use without knowing whether the source is a
hand-annotated JSON or auto-detected corners.

Hand-annotated JSON format (preferred — more accurate):
  {
    "corners": {"TL": [x, y], "TR": [x, y], "BR": [x, y], "BL": [x, y]},
    "net":     {"left": [x, y], "right": [x, y]}
  }

Alternate format (used by legacy player_detection.py):
  [[x, y], [x, y], [x, y], [x, y]]   — simple 4-point polygon

Map video stems to their JSON paths here.  Leave empty to always
auto-detect from the video.
"""

import json
import numpy as np

# Dict mapping video stem (filename without extension) to a court JSON path.
# Example:
#   COURT_JSON = {
#       "Test1_Full_rev": "Test1_Full_rev/court_annotated.json",
#   }
COURT_JSON = {}


def load_court_geometry(court_json_path):
    """
    Parse a hand-annotated court JSON and return standardised boundary coords.

    Returns
    -------
    dict with keys:
      net_y            - pixel Y of the net line
      net_x_left       - pixel X of left net post
      net_x_right      - pixel X of right net post
      near_baseline_y  - pixel Y of the near (bottom) baseline
      far_baseline_y   - pixel Y of the far (top) baseline
      left_sideline_x  - pixel X of the left sideline (min X)
      right_sideline_x - pixel X of the right sideline (max X)
    """
    with open(court_json_path) as f:
        data = json.load(f)

    # ── Format 1: full annotated dict ────────────────────────────────────
    if isinstance(data, dict) and "corners" in data:
        c  = data["corners"]
        TL = np.array(c["TL"], dtype=float)
        TR = np.array(c["TR"], dtype=float)
        BR = np.array(c["BR"], dtype=float)
        BL = np.array(c["BL"], dtype=float)

        if "net" in data:
            net_left  = np.array(data["net"]["left"],  dtype=float)
            net_right = np.array(data["net"]["right"], dtype=float)
            net_y        = float((net_left[1] + net_right[1]) / 2)
            net_x_left   = float(net_left[0])
            net_x_right  = float(net_right[0])
        else:
            net_y, net_x_left, net_x_right = _net_from_corners(TL, TR, BR, BL)

    # ── Format 2: simple 4-point polygon [[x,y], ...] ────────────────────
    elif isinstance(data, list):
        pts = np.array(data, dtype=float)
        s   = pts.sum(axis=1)
        d   = np.diff(pts, axis=1).flatten()
        TL  = pts[np.argmin(s)]
        TR  = pts[np.argmin(d)]
        BR  = pts[np.argmax(s)]
        BL  = pts[np.argmax(d)]
        net_y, net_x_left, net_x_right = _net_from_corners(TL, TR, BR, BL)

    else:
        raise ValueError(f"Unrecognised court JSON format in {court_json_path}")

    return {
        "net_y":            net_y,
        "net_x_left":       net_x_left,
        "net_x_right":      net_x_right,
        "near_baseline_y":  float(max(BL[1], BR[1])),
        "far_baseline_y":   float(min(TL[1], TR[1])),
        "left_sideline_x":  float(min(TL[0], BL[0])),
        "right_sideline_x": float(max(TR[0], BR[0])),
    }


def geometry_from_corners(corners, net_Y):
    """
    Derive the same standardised geometry dict directly from auto-detected
    court corners (np.float32 [TL, TR, BR, BL]) and the detected net_Y.

    Used as the fallback when no hand-annotated JSON is available.
    """
    TL, TR, BR, BL = corners.astype(float)

    # Interpolate where each sideline crosses net_Y
    t_l = (net_Y - TL[1]) / (BL[1] - TL[1]) if BL[1] != TL[1] else 0.5
    t_r = (net_Y - TR[1]) / (BR[1] - TR[1]) if BR[1] != TR[1] else 0.5
    net_x_left  = float(TL[0] + t_l * (BL[0] - TL[0]))
    net_x_right = float(TR[0] + t_r * (BR[0] - TR[0]))

    return {
        "net_y":            float(net_Y),
        "net_x_left":       net_x_left,
        "net_x_right":      net_x_right,
        "near_baseline_y":  float(max(BL[1], BR[1])),
        "far_baseline_y":   float(min(TL[1], TR[1])),
        "left_sideline_x":  float(min(TL[0], BL[0])),
        "right_sideline_x": float(max(TR[0], BR[0])),
    }


# ── internal helper ────────────────────────────────────────────────────────────

def _net_from_corners(TL, TR, BR, BL):
    """Estimate net Y and net post X by interpolating at the midpoint depth."""
    net_y   = float((min(TL[1], TR[1]) + max(BL[1], BR[1])) / 2)
    t_l     = (net_y - TL[1]) / (BL[1] - TL[1]) if BL[1] != TL[1] else 0.5
    t_r     = (net_y - TR[1]) / (BR[1] - TR[1]) if BR[1] != TR[1] else 0.5
    x_left  = float(TL[0] + t_l * (BL[0] - TL[0]))
    x_right = float(TR[0] + t_r * (BR[0] - TR[0]))
    return net_y, x_left, x_right
