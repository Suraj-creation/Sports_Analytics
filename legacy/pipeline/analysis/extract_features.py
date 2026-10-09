"""
extract_features.py
-------------------
Extends the rally CSV from detect_rallies.py with:
  - win_point_player       : who won each rally
  - win_reason / lose_reason: how it ended
  - ball_types             : winning shot type
  - roundscore_A/B         : cumulative score (auto, no scoreboard needed)
  - detection_confidence   : HIGH / MEDIUM / LOW per rally

CAMERA ASSUMPTION:
  End-on view (camera behind one baseline):
    TOP of image  = FAR player  = Player A
    BOTTOM of image = NEAR player = Player B
    Net = horizontal line at mid-depth of court

HOW TO RUN:
  python analysis/extract_features.py \\
      --video  path/to/video.mp4 \\
      --rally  path/to/rallies.csv \\
      --shuttle path/to/shuttle_filled.csv \\
      --player  path/to/player_detections.csv \\
      --out     path/to/output_extended.csv \\
      --player_a "Player A Name" \\
      --player_b "Player B Name"

  All flags except --video have defaults derived from the video path.
  Court corners and net position are detected automatically from the
  video — no manual annotation needed.  Works for any camera angle as
  long as the court surface is green.
"""

import os
import sys
import cv2
import math
import json
import argparse
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

# ============================================================
# FIXED CONSTANTS (same for every badminton video)
# ============================================================
COURT_LENGTH = 13.4   # metres — near -> far baseline
COURT_WIDTH  = 6.1    # metres — left -> right sideline
NET_DEPTH    = 6.7    # metres — distance from near baseline to net

# Detection thresholds (scale with resolution automatically)
ANALYSIS_SEC     = 3.0   # seconds before rally end to analyse (longer = more reliable trajectory)
STOP_SPEED       = 50    # px/s -> shuttle stopped
HIGH_SPEED       = 350   # px/s -> fast shot (smash)
MED_SPEED        = 150   # px/s -> medium shot
RELIABLE_SPD_MIN = 40    # px/s -> minimum speed to count as "reliably detected"
NET_TOL_FRAC     = 0.03  # net tolerance as fraction of image height (auto-scales)

# Court detection: sample multiple frames and pick the best one
SAMPLE_FRAMES   = [30, 60, 90, 150, 240]   # candidates to try
MIN_COURT_FRAC  = 0.10                      # court must be >10% of frame area
# HSV range for green court — covers standard indoor and outdoor courts
HSV_LOWER_GREEN = np.array([30, 35, 35])
HSV_UPPER_GREEN = np.array([90, 255, 255])

# ============================================================
# MODULE 1 — AUTO COURT DETECTION  (video-adaptive)
# ============================================================
def auto_detect_court(video_file):
    """
    Detect 4 court corners automatically from the video.

    Tries multiple candidate frames and picks the one that gives the
    largest, cleanest green court region.  This makes it robust to
    players standing near the boundary in some frames, advertising
    overlays at video start, and slight differences in lighting across
    videos.

    The court green color (HSV_LOWER/UPPER_GREEN) is fixed — it covers
    all standard indoor badminton courts.  Corner POSITIONS change per
    video because the camera angle differs, but the detection logic is
    the same.

    Returns:
      corners   : np.float32 [TL, TR, BR, BL] in pixel coords
      ref_frame : BGR frame used for detection (for debug image)
      frame_no  : index of ref_frame within video_file
    """
    cap        = cv2.VideoCapture(video_file)
    total      = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    h_frame    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w_frame    = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_area = h_frame * w_frame

    best_corners  = None
    best_area     = 0
    best_frame    = None
    best_frame_no = None

    candidates = [f for f in SAMPLE_FRAMES if f < total]
    if not candidates:
        candidates = [0]

    for fno in candidates:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fno)
        ret, frame = cap.read()
        if not ret:
            continue

        corners, area = _try_detect_corners(frame, frame_area)
        if corners is not None and area > best_area:
            best_area    = area
            best_corners = corners
            best_frame   = frame.copy()
            best_frame_no = fno
            print(f"  Frame {fno:>4}: court area={area/frame_area*100:.1f}%  "
                  f"-> TL={corners[0].astype(int).tolist()} "
                  f"TR={corners[1].astype(int).tolist()} "
                  f"BR={corners[2].astype(int).tolist()} "
                  f"BL={corners[3].astype(int).tolist()}")

    cap.release()

    if best_corners is None:
        raise RuntimeError(
            "Court not detected in any sample frame.\n"
            "Tip: check that the court surface is green and visible."
        )

    print(f"  Best corners selected (court area={best_area/frame_area*100:.1f}% of frame)")
    return best_corners.astype(np.float32), best_frame, best_frame_no


def _try_detect_corners(frame, frame_area):
    """
    Attempt to detect 4 court corners in a single frame.
    Returns (corners, court_pixel_area) or (None, 0) on failure.
    """
    hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, HSV_LOWER_GREEN, HSV_UPPER_GREEN)

    # Adaptive morphology: kernel scaled to image size
    k = max(5, frame.shape[0] // 150)
    kernel = np.ones((k, k), np.uint8)
    mask   = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, 0

    court_cnt  = max(contours, key=cv2.contourArea)
    court_area = cv2.contourArea(court_cnt)

    # Reject if court is too small (player occlusion / wrong frame)
    if court_area < frame_area * MIN_COURT_FRAC:
        return None, 0

    # Try progressively smaller epsilon until we get 4 corners
    for eps_frac in [0.02, 0.03, 0.015, 0.04, 0.01]:
        eps    = eps_frac * cv2.arcLength(court_cnt, True)
        approx = cv2.approxPolyDP(court_cnt, eps, True).reshape(-1, 2).astype(float)
        if len(approx) == 4:
            return _sort_corners(approx), court_area

    # Fallback: extreme points of convex hull
    hull = cv2.convexHull(court_cnt).reshape(-1, 2).astype(float)
    s    = hull.sum(axis=1)
    d    = np.diff(hull, axis=1).flatten()
    corners = np.array([
        hull[np.argmin(s)],   # TL
        hull[np.argmin(d)],   # TR
        hull[np.argmax(s)],   # BR
        hull[np.argmax(d)],   # BL
    ])
    return _sort_corners(corners), court_area


def refine_corners_with_lines(frame, approx_corners):
    """
    Refine court corners to the EXACT outermost white boundary lines.

    Strategy: detect LONG white line segments only (boundary lines are
    the longest lines in the court — longer than service box lines,
    center lines, or logos).  Classify into horizontal (baselines) and
    diagonal (sidelines), pick the outermost of each, then find their
    4 intersections as the precise court corners.

    Falls back to approx_corners if fewer than 4 boundary lines found.
    """
    h, w = frame.shape[:2]

    # Mask to inside the green region only
    court_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(court_mask, [approx_corners.astype(np.int32)], 255)

    # Isolate white pixels (low saturation + high value)
    hsv        = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    white_mask = cv2.inRange(hsv,
                              np.array([0,   0, 170]),
                              np.array([180, 60, 255]))
    white_court = cv2.bitwise_and(white_mask, court_mask)

    # Detect LONG line segments — boundary lines span at least 20% of image
    min_len = int(min(h, w) * 0.20)
    lines = cv2.HoughLinesP(white_court, 1, np.pi / 180,
                             threshold=40,
                             minLineLength=min_len,
                             maxLineGap=20)

    if lines is None or len(lines) < 4:
        print("  White-line refinement: not enough long lines, keeping green corners")
        return approx_corners

    # Classify each line as horizontal-ish (baseline) or diagonal (sideline)
    horiz, diag = [], []
    for ln in lines:
        x1, y1, x2, y2 = ln[0]
        angle  = abs(math.degrees(math.atan2(y2 - y1, x2 - x1))) % 180
        length = math.hypot(x2 - x1, y2 - y1)
        entry  = (x1, y1, x2, y2, length)
        if angle < 25 or angle > 155:   # nearly horizontal → baseline
            horiz.append(entry)
        else:                            # diagonal → sideline
            diag.append(entry)

    if len(horiz) < 2 or len(diag) < 2:
        print("  White-line refinement: missing baseline or sideline, keeping green corners")
        return approx_corners

    # Green polygon boundary — lines MUST be inside this, not at the paint edge
    green_top_y    = min(approx_corners[0][1], approx_corners[1][1])  # TL/TR Y
    green_bottom_y = max(approx_corners[2][1], approx_corners[3][1])  # BR/BL Y
    green_left_x   = min(approx_corners[0][0], approx_corners[3][0])  # TL/BL X
    green_right_x  = max(approx_corners[1][0], approx_corners[2][0])  # TR/BR X

    # Margin: white lines are painted INSIDE the green paint area.
    # Exclude lines that are at or beyond the green paint edge (those are
    # the paint boundary itself, not the white court lines).
    EDGE_MARGIN = 20  # px — lines within this of the green edge are excluded

    horiz_inside = [l for l in horiz
                    if green_top_y + EDGE_MARGIN
                       < (l[1]+l[3])/2
                       < green_bottom_y - EDGE_MARGIN]

    diag_inside  = [l for l in diag
                    if green_left_x + EDGE_MARGIN
                       < (l[0]+l[2])/2
                       < green_right_x - EDGE_MARGIN]

    # Fall back to all lines if filtered list is too small
    if len(horiz_inside) < 2:
        horiz_inside = horiz
    if len(diag_inside) < 2:
        diag_inside = diag

    # Pick OUTERMOST line in each direction (by position, inside the court):
    far_baseline  = min(horiz_inside, key=lambda l: (l[1] + l[3]) / 2)  # topmost
    near_baseline = max(horiz_inside, key=lambda l: (l[1] + l[3]) / 2)  # bottommost
    left_side     = min(diag_inside,  key=lambda l: (l[0] + l[2]) / 2)  # leftmost
    right_side    = max(diag_inside,  key=lambda l: (l[0] + l[2]) / 2)  # rightmost

    def line_eq(ln):
        x1, y1, x2, y2 = ln[0], ln[1], ln[2], ln[3]
        dy, dx = float(y2 - y1), float(x2 - x1)
        return dy, -dx, dy * x1 - dx * y1

    def intersect(eq1, eq2):
        a1, b1, c1 = eq1
        a2, b2, c2 = eq2
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-9:
            return None
        return np.array([(c1*b2 - c2*b1)/det, (a1*c2 - a2*c1)/det])

    TL = intersect(line_eq(far_baseline),  line_eq(left_side))
    TR = intersect(line_eq(far_baseline),  line_eq(right_side))
    BR = intersect(line_eq(near_baseline), line_eq(right_side))
    BL = intersect(line_eq(near_baseline), line_eq(left_side))

    if any(pt is None for pt in [TL, TR, BR, BL]):
        print("  White-line refinement: line intersection failed, keeping green corners")
        return approx_corners

    refined = _sort_corners(np.array([TL, TR, BR, BL])).astype(np.float32)

    # Sanity: corners must stay within reasonable distance of green corners
    max_shift = max(np.linalg.norm(refined[i] - approx_corners[i]) for i in range(4))
    if max_shift > h * 0.15:
        print(f"  White-line refinement rejected (shift {max_shift:.0f}px) -- keeping green corners")
        return approx_corners

    print(f"  White-line refined to boundary lines (shift {max_shift:.1f}px):")
    print(f"    TL={refined[0].astype(int).tolist()}  "
          f"TR={refined[1].astype(int).tolist()}  "
          f"BR={refined[2].astype(int).tolist()}  "
          f"BL={refined[3].astype(int).tolist()}")
    return refined


def _sort_corners(pts):
    """Sort 4 points into [TL, TR, BR, BL] order."""
    pts     = np.array(pts, dtype=float)
    by_y    = pts[np.argsort(pts[:, 1])]
    top2    = by_y[:2][np.argsort(by_y[:2, 0])]   # left/right among top
    bot2    = by_y[2:][np.argsort(by_y[2:, 0])]   # left/right among bottom
    TL, TR  = top2
    BL, BR  = bot2
    return np.array([TL, TR, BR, BL])


# ============================================================
# MODULE 2 — NET POSITION (derived from court corners)
# ============================================================
def compute_net(corners):
    """
    Compute net_Y in image space via homography.
    Net sits at NET_DEPTH metres from the near baseline.

    Returns:
      net_Y        : pixel Y of the net line
      net_left_px  : left endpoint of net in image
      net_right_px : right endpoint of net in image
      H            : homography image->real
      H_inv        : homography real->image
    """
    TL, TR, BR, BL = corners

    img_pts  = np.float32([TL, TR, BR, BL])
    real_pts = np.float32([
        [0,           0          ],   # TL -> far-left   (depth=0)
        [COURT_WIDTH, 0          ],   # TR -> far-right  (depth=0)
        [COURT_WIDTH, COURT_LENGTH],  # BR -> near-right (depth=13.4)
        [0,           COURT_LENGTH],  # BL -> near-left  (depth=13.4)
    ])

    H, _  = cv2.findHomography(img_pts, real_pts)
    H_inv = np.linalg.inv(H)

    # Project net ground-line from real -> image
    net_world = np.float32([
        [[0,           NET_DEPTH]],
        [[COURT_WIDTH, NET_DEPTH]],
    ])
    net_img = cv2.perspectiveTransform(net_world, H_inv)  # shape (2,1,2)

    net_left_px  = net_img[0][0]   # [x, y]
    net_right_px = net_img[1][0]
    net_Y        = float((net_left_px[1] + net_right_px[1]) / 2)

    print(f"  Net computed: net_Y={net_Y:.1f}px  "
          f"left={net_left_px.astype(int).tolist()}  "
          f"right={net_right_px.astype(int).tolist()}")
    return net_Y, net_left_px, net_right_px, H, H_inv


def snap_net(frame, net_Y, corners, band=60):
    """
    Refine net_Y using the BLUE NET POST STANDS visible on each side
    of the court.  The blue stands are the most reliable visual indicator
    of the exact net position — they sit at the net's Y depth on both
    left and right court edges.

    Falls back to Hough edge detection if blue stands not found.
    """
    h, w = frame.shape[:2]

    # ── Step 1: detect blue net post stands ───────────────
    # Blue HSV range (covers typical blue/teal net post covers)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    blue_mask = cv2.inRange(hsv,
                             np.array([90,  80,  60]),
                             np.array([130, 255, 255]))

    TL, TR, BR, BL = corners.astype(int)

    # Look only in a vertical band around the computed net_Y
    # and restrict to the LEFT and RIGHT edges of the court
    # (net posts are at the sidelines, not in the middle)
    y_lo = max(0,  int(net_Y - band))
    y_hi = min(h,  int(net_Y + band))

    court_width = max(TR[0], BR[0]) - min(TL[0], BL[0])
    side_w      = int(court_width * 0.12)   # look in outer 12% on each side

    x_left_lo   = max(0, min(TL[0], BL[0]) - side_w)
    x_left_hi   = min(w, min(TL[0], BL[0]) + side_w)
    x_right_lo  = max(0, max(TR[0], BR[0]) - side_w)
    x_right_hi  = min(w, max(TR[0], BR[0]) + side_w)

    left_blue  = blue_mask[y_lo:y_hi, x_left_lo:x_left_hi]
    right_blue = blue_mask[y_lo:y_hi, x_right_lo:x_right_hi]

    blue_ys = []
    for region in (left_blue, right_blue):
        pts = cv2.findNonZero(region)
        if pts is not None and len(pts) > 20:
            # Median Y of blue pixels in this region
            ys = pts[:, 0, 1]
            blue_ys.append(float(np.median(ys)) + y_lo)

    if blue_ys:
        refined = float(np.mean(blue_ys))
        print(f"  Net from blue stands: {net_Y:.1f} -> {refined:.1f}px")
        return refined

    # ── Step 2: fallback — strongest horizontal edge ──────
    y1    = max(0, int(net_Y - band))
    y2    = min(h, int(net_Y + band))
    roi   = frame[y1:y2, :]
    gray  = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180,
                             threshold=80,
                             minLineLength=int(w * 0.3),
                             maxLineGap=30)
    if lines is None:
        return float(net_Y)

    best, best_dist = net_Y, float('inf')
    for line in lines:
        x1, y_a, x2, y_b = line[0]
        angle = abs(math.degrees(math.atan2(y_b - y_a, x2 - x1)))
        if angle < 10:
            mid_y = y1 + (y_a + y_b) / 2
            if abs(mid_y - net_Y) < best_dist:
                best_dist = abs(mid_y - net_Y)
                best      = mid_y

    print(f"  Net snapped (edge fallback): {net_Y:.1f} -> {best:.1f}px")
    return float(best)


# ============================================================
# MODULE 3 — PLAYER SIDE ASSIGNMENT
# ============================================================
def assign_player_sides(player_csv):
    """
    Determine which detection slot (player_1 / player_2) is the FAR player
    (smaller average Y = top of image) and which is NEAR (larger avg Y).
    FAR = Player A,  NEAR = Player B.
    """
    df    = pd.read_csv(player_csv)
    avg1  = df['player_1_y'].dropna().mean()
    avg2  = df['player_2_y'].dropna().mean()
    if avg1 < avg2:
        far_slot, near_slot = 'player_1', 'player_2'
    else:
        far_slot, near_slot = 'player_2', 'player_1'

    print(f"  FAR  (Player A) = {far_slot}  avg_y={min(avg1,avg2):.0f}px")
    print(f"  NEAR (Player B) = {near_slot}  avg_y={max(avg1,avg2):.0f}px")
    return far_slot, near_slot


# ============================================================
# OUT-OF-BOUNDS HELPERS
# ============================================================
def get_court_edges(corners):
    """
    Return the 4 boundary line segments of the court as point pairs.
    corners = [TL, TR, BR, BL]
    """
    TL, TR, BR, BL = corners
    return [
        (TL, TR),   # far baseline
        (TR, BR),   # right sideline
        (BR, BL),   # near baseline
        (BL, TL),   # left sideline
    ]


def _ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])


def segments_cross(p1, p2, p3, p4):
    """True if line segment p1-p2 intersects line segment p3-p4."""
    return (_ccw(p1, p3, p4) != _ccw(p2, p3, p4) and
            _ccw(p1, p2, p3) != _ccw(p1, p2, p4))


def trajectory_crosses_boundary(positions, court_corners):
    """
    Check if the shuttle path (list of (frame,x,y)) crosses any court
    boundary edge.  Returns (crossed, fault_side) or (False, None).

    This catches the common case where tracking drops the shuttle just
    AFTER it exits — the last detected position is still inside the
    court, but the segment from the previous position to the last one
    visibly crossed the boundary line.
    """
    if len(positions) < 2:
        return False, None

    edges = get_court_edges(court_corners)

    for i in range(1, len(positions)):
        p1 = (positions[i-1][1], positions[i-1][2])   # (x, y)
        p2 = (positions[i][1],   positions[i][2])

        for edge in edges:
            if segments_cross(p1, p2, tuple(edge[0]), tuple(edge[1])):
                # Determine which side the exit was heading toward
                # The shuttle was at p1 (inside) and moving to p2 (outside)
                return True, (p1[0], p1[1], p2[0], p2[1])

    return False, None


def extrapolate_exit(last_x, last_y, avg_vx, avg_vy, court_poly_cv,
                     court_corners, fps, max_frames=25):
    """
    Extrapolate the shuttle trajectory forward for up to max_frames.
    If the predicted path exits the court polygon, return (True, exit_point).

    Only fires when shuttle is already near the boundary (within EXTRAP_MARGIN
    pixels) so we don't flag mid-court shots.
    """
    # Force Python float — cv2 rejects numpy float64
    last_x, last_y = float(last_x), float(last_y)

    dt = 1.0 / fps
    for t in range(1, max_frames + 1):
        ex = float(last_x + avg_vx * dt * t)
        ey = float(last_y + avg_vy * dt * t)
        in_court = cv2.pointPolygonTest(court_poly_cv, (ex, ey), False) >= 0
        if not in_court:
            return True, (ex, ey)

    return False, None


def fault_side_from_velocity(avg_vx, avg_vy, prev_y, net_Y):
    """Determine fault_side from shuttle velocity direction."""
    if abs(avg_vx) > abs(avg_vy):       # mainly sideways exit
        return 'near' if prev_y > net_Y else 'far'
    elif avg_vy > 0:                     # moving toward near baseline
        return 'far'
    else:                                # moving toward far baseline
        return 'near'


# ============================================================
# MODULE 4 — RALLY END EVENT DETECTION
# ============================================================
def _frame_col(df):
    for c in ("Frame", "frame_no", "frame", "index"):
        if c in df.columns:
            return c
    raise ValueError("No frame column in DataFrame")


def shuttle_dist_from_net_m(px, py, H):
    """
    Convert shuttle pixel position (px, py) to real-world court coordinates
    using homography H, then return distance from net in metres.
    Net is at NET_DEPTH = 6.7m from near baseline.
    """
    pt = np.array([[[float(px), float(py)]]], dtype=np.float32)
    world = cv2.perspectiveTransform(pt, H)
    world_y = float(world[0][0][1])            # depth in metres
    return abs(world_y - NET_DEPTH)            # distance from net


def _fault_side(vels, last_y, last_x, event, net_Y,
                near_baseline_y, far_baseline_y,
                court_left_x, court_right_x):
    """
    Determine which player caused the fault using velocity direction.

    PRIMARY signal: average vy across the middle of the trajectory.
      vy > 0  → shuttle moving toward near baseline (downward in image)
               → shot came FROM the far player → far player's fault
      vy < 0  → shuttle moving toward far baseline (upward in image)
               → shot came FROM the near player → near player's fault

    We use velocity direction rather than last-position proximity to
    baselines because the tracking data near rally end is often outside
    the physical court (fill_gaps artifacts place the shuttle above the
    far baseline), which causes position-based checks to misfire.

    Baseline proximity is used ONLY as a secondary confirmation when
    the shuttle genuinely reaches a boundary (margin kept tight).
    """
    if not vels:
        return 'unknown'

    # Use last few FAST velocity measurements — these represent the final
    # shot (fault shot) direction, not earlier shots in the rally.
    # Filtering by speed > RELIABLE_SPD_MIN avoids noisy near-zero
    # measurements from tracking gaps or shuttle almost stopped.
    reliable = [v for v in vels if v['speed'] > RELIABLE_SPD_MIN] or vels
    last_few = reliable[-3:] if len(reliable) >= 3 else reliable
    avg_vy   = float(np.mean([v['vy'] for v in last_few]))

    # ── Hits net: use approach direction ────────────────────────
    if event == 'hits_net':
        # vy > 0 → shuttle moving toward near side → came FROM far player
        return 'far' if avg_vy > 0 else 'near'

    # ── Out of bounds: velocity direction is primary ─────────────
    # Only override with position if the shuttle clearly crossed a
    # real boundary (tight margin to avoid tracking artifacts).
    TIGHT = 15   # px — only fires if shuttle is genuinely at the line
    if last_y > near_baseline_y - TIGHT:
        return 'far'    # clearly past near baseline → far player faulted
    if last_y < far_baseline_y + TIGHT:
        return 'near'   # clearly past far baseline → near player faulted

    # Primary: direction the shuttle was travelling
    return 'far' if avg_vy > 0 else 'near'


def analyze_rally_end(shuttle_df, end_frame, court_poly_cv, court_corners,
                      net_Y, fps, net_tol_px=30, H=None,
                      net_left_x=None, net_right_x=None):
    """
    Determine how a rally ended.

    Decision order (each level returns early if conclusive):

    1. STATIONARY CHECK (highest confidence)
       Shuttle settles near-still → resting position is definitive.

    2. GEOMETRIC CHECK (primary deterministic path)
       Uses the shuttle's last detected pixel position against court
       boundaries derived from the auto-detected (or JSON-supplied) corners.
         hits_net      : last_y within ±(5×net_tol_px) of net_Y AND
                         last_x within court sideline width
         out_of_bounds : last position outside any court boundary

       TrackNetV3 typically loses the shuttle 50-150px before a terminal
       event, so the net band is intentionally wide.

    3. EVIDENCE SCORING (fallback when position is ambiguous)
       Votes across 5 signals (speed crash, net proximity, polygon test,
       boundary exit, final speed) — used when the last detected position
       is mid-court and neither geometric check fires.

    Parameters
    ----------
    net_left_x, net_right_x : optional pixel X of the net posts.
       If not supplied, they are interpolated from court_corners at net_Y.

    Returns: event, fault_side, confidence, feats
    """
    fc  = _frame_col(shuttle_df)
    N   = int(fps * ANALYSIS_SEC)
    win = shuttle_df[
        (shuttle_df[fc] >= end_frame - N) &
        (shuttle_df[fc] <= end_frame) &
        (shuttle_df['Visibility'] == 1)
    ].sort_values(fc)

    n_vis = len(win)
    if n_vis < 3:
        return 'unknown', 'unknown', 'LOW', {}

    confidence = 'HIGH' if n_vis >= 10 else 'MEDIUM'
    pos = list(zip(win[fc].values, win['X'].values, win['Y'].values))

    actual_start = int(pos[0][0])
    actual_end   = int(pos[-1][0])

    # ── Velocities ────────────────────────────────────────────────
    vels = []
    for i in range(1, len(pos)):
        f0, x0, y0 = pos[i - 1]
        f1, x1, y1 = pos[i]
        dt = (f1 - f0) / fps
        if dt <= 0:
            continue
        vx = (x1 - x0) / dt
        vy = (y1 - y0) / dt
        vels.append(dict(vx=vx, vy=vy, speed=math.hypot(vx, vy),
                         x=x1, y=y1))

    if not vels:
        return 'unknown', 'unknown', 'LOW', {}

    last_x = float(pos[-1][1])
    last_y = float(pos[-1][2])
    prev_y = float(pos[-4][2]) if len(pos) >= 4 else float(pos[0][2])
    speeds = [v['speed'] for v in vels]

    # Fault velocity: last few RELIABLE (fast) frames = direction of final shot
    # This mirrors the original approach that achieved 33/36 correct winners.
    reliable  = [v for v in vels if v['speed'] > RELIABLE_SPD_MIN] or vels
    last_few  = reliable[-3:] if len(reliable) >= 3 else reliable
    fault_vx  = float(np.mean([v['vx'] for v in last_few]))
    fault_vy  = float(np.mean([v['vy'] for v in last_few]))

    TL, TR, BR, BL  = court_corners
    near_baseline_y = float(max(BL[1], BR[1]))
    far_baseline_y  = float(min(TL[1], TR[1]))
    court_left_x    = float(min(TL[0], BL[0]))
    court_right_x   = float(max(TR[0], BR[0]))

    # Net X extent: where each sideline intersects net_Y.
    # Computed here if not supplied by the caller (e.g. from court_crop.py).
    if net_left_x is None or net_right_x is None:
        t_l = (net_Y - TL[1]) / (BL[1] - TL[1]) if BL[1] != TL[1] else 0.5
        t_r = (net_Y - TR[1]) / (BR[1] - TR[1]) if BR[1] != TR[1] else 0.5
        net_left_x  = float(TL[0] + t_l * (BL[0] - TL[0]))
        net_right_x = float(TR[0] + t_r * (BR[0] - TR[0]))

    feats = dict(
        net_Y=net_Y, net_tol_px=net_tol_px,
        last_y=last_y, last_x=last_x,
        analysis_start_frame=actual_start,
        analysis_end_frame=actual_end,
    )

    # ── STATIONARY CHECK (highest confidence, unchanged) ──────────
    # If the shuttle settles completely, its resting position tells us
    # exactly what happened.
    static = [v for v in vels[-6:] if v['speed'] < 15]
    if len(static) >= 3:
        gx = float(np.mean([v['x'] for v in static]))
        gy = float(np.mean([v['y'] for v in static]))

        if abs(gy - net_Y) < net_tol_px * 5:
            # Settled at net depth → hits_net
            fault_side = 'near' if gy > net_Y else 'far'
            feats['ground_confirmed'] = True
            return 'hits_net', fault_side, 'HIGH', feats

        in_court = cv2.pointPolygonTest(court_poly_cv, (gx, gy), False) >= 0
        if in_court:
            # Net bounce check: settled in near half after coming off net?
            pre_static = [v for v in vels[:-len(static)]
                          if v['speed'] > RELIABLE_SPD_MIN]
            if pre_static:
                lf = pre_static[-1]
                if lf['y'] < net_Y and lf['vy'] > 30 and gy > net_Y:
                    feats['ground_confirmed'] = True
                    return 'hits_net', 'near', 'HIGH', feats
            landing_half = 'far' if gy < net_Y else 'near'
            feats['ground_confirmed'] = True
            return 'wins_by_landing', landing_half, 'HIGH', feats
        else:
            fs = fault_side_from_velocity(fault_vx, fault_vy, prev_y, net_Y)
            feats['ground_confirmed'] = True
            return 'out_of_bounds', fs, 'HIGH', feats

    # ── GEOMETRIC CHECKS (primary — deterministic, higher priority) ──────────
    # Use the shuttle's last detected position to decide the event.
    #
    # NET_GEOM_BAND: shuttle often disappears 50-150px before actual net contact
    # because TrackNetV3 loses it just before impact.  A band of ±5×net_tol_px
    # (~150px) catches most net hits while staying well clear of the baselines.
    #
    # OOB check has no extra margin: last position must be genuinely outside
    # a court boundary (not just near one).  This avoids misfiring on back-court
    # shots where the shuttle legitimately approaches a baseline mid-rally.
    NET_GEOM_BAND = net_tol_px * 5          # ±150px at default net_tol_px=30
    in_net_band  = abs(last_y - net_Y) < NET_GEOM_BAND
    in_court_x   = net_left_x - net_tol_px <= last_x <= net_right_x + net_tol_px
    past_far     = last_y < far_baseline_y
    past_near    = last_y > near_baseline_y
    past_side    = last_x < court_left_x or last_x > court_right_x
    geom_oob     = past_far or past_near or past_side

    feats.update(dict(
        net_left_x=net_left_x, net_right_x=net_right_x,
        in_net_band=in_net_band, geom_oob=geom_oob,
    ))

    # hits_net: last shuttle position is inside the net-depth band and within
    # the court's left-right span (not outside a sideline).
    if in_net_band and in_court_x and not geom_oob:
        fault_side = fault_side_from_velocity(fault_vx, fault_vy, prev_y, net_Y)
        feats['geom_decision'] = 'hits_net'
        return 'hits_net', fault_side, confidence, feats

    # out_of_bounds: shuttle is clearly outside a court boundary.
    if geom_oob:
        fs = fault_side_from_velocity(fault_vx, fault_vy, prev_y, net_Y)
        feats['geom_decision'] = 'out_of_bounds'
        return 'out_of_bounds', fs, confidence, feats

    # ── EVIDENCE SCORING (fallback — last position ambiguous) ─────────────
    net_score = 0
    oob_score = 0

    # --- Signal 1: Speed crash + post-crash downward drift --------
    # Physical basis: shuttle hits net → sudden momentum loss →
    # falls straight down (Y increases).  This is the user's insight.
    crash_idx = None
    for i in range(2, len(speeds)):
        if speeds[i - 2] > 80 and speeds[i] < speeds[i - 2] * 0.4:
            crash_idx = i
            break

    post_dy = 0.0
    if crash_idx is not None:
        post = vels[crash_idx:]
        if len(post) >= 2:
            post_dy = float(post[-1]['y'] - post[0]['y'])
            if post_dy > 120:      # strong downward fall → net hit
                net_score += 3
            elif post_dy > 50:
                net_score += 1
            elif post_dy < -30:    # moves upward after crash → OOB
                oob_score += 1
    feats['post_crash_dy'] = post_dy

    # --- Signal 2: Last detected position close to net_Y ----------
    dist_net_px = abs(last_y - net_Y)
    feats['dist_from_net_px'] = dist_net_px
    if dist_net_px < net_tol_px * 4:      # ~128px — very close
        net_score += 3
    elif dist_net_px < net_tol_px * 8:    # ~256px — moderately close
        net_score += 1

    # --- Signal 3: Last position inside / outside court polygon ---
    last_in_court = cv2.pointPolygonTest(
        court_poly_cv, (last_x, last_y), False) >= 0
    feats['last_in_court'] = last_in_court
    if not last_in_court:
        oob_score += 3      # clearly outside → OOB
    else:
        net_score += 1      # inside court → net hit more likely

    # --- Signal 4: Baseline / sideline exit in recent positions ---
    recent = vels[-8:]
    near_exit = any(v['y'] > near_baseline_y - 30 for v in recent)
    far_exit  = any(v['y'] < far_baseline_y  + 30 for v in recent)
    side_exit = any(v['x'] < court_left_x   - 30 or
                    v['x'] > court_right_x  + 30 for v in recent)
    feats['near_exit'] = near_exit
    feats['far_exit']  = far_exit
    feats['side_exit'] = side_exit
    if near_exit or far_exit or side_exit:
        oob_score += 3

    # --- Signal 5: Final speed (still moving fast = didn't stop) --
    avg_final = float(np.mean([v['speed'] for v in vels[-3:]])) \
        if len(vels) >= 3 else 0.0
    feats['avg_final_speed'] = avg_final
    if avg_final > 200:
        oob_score += 1     # still moving fast → probably OOB
    elif avg_final < 40:
        net_score += 1     # nearly stopped → consistent with net hit

    feats['net_score'] = net_score
    feats['oob_score'] = oob_score

    # ── DECISION ──────────────────────────────────────────────────
    if net_score > oob_score:
        event = 'hits_net'
    elif oob_score > net_score:
        event = 'out_of_bounds'
    else:
        # Tied: shuttle inside court → net hit; outside → OOB
        event = 'hits_net' if last_in_court else 'out_of_bounds'

    # Low-evidence case: shuttle decelerating inside court → landing
    if net_score < 2 and oob_score < 2 and last_in_court:
        all_speeds   = [v['speed'] for v in vels]
        mid_idx      = max(1, len(all_speeds) // 2)
        early_spd    = float(np.mean(all_speeds[:mid_idx]))
        late_spd     = float(np.mean(all_speeds[mid_idx:]))
        decelerating = (early_spd - late_spd) / max(early_spd, 1.0) > 0.4
        if decelerating:
            landing_half = 'far' if last_y < net_Y else 'near'
            return 'wins_by_landing', landing_half, confidence, feats

    fault_side = fault_side_from_velocity(fault_vx, fault_vy, prev_y, net_Y)
    return event, fault_side, confidence, feats


# ============================================================
# MODULE 5 — WIN / LOSE REASON STRINGS
# ============================================================
_WIN_STR = {
    'out_of_bounds':   'opponent goes out of bounds',
    'hits_net':        'opponent hits the net',
    'fails_to_clear':  'opponent hits the net',
    'wins_by_landing': 'shot landed as winner',
    'unknown':         'unknown',
}
_LOSE_STR = {
    'out_of_bounds':   'goes out of bounds',
    'hits_net':        'hits the net',
    'fails_to_clear':  'hits the net',
    'wins_by_landing': 'opponent wins by landing',
    'unknown':         'unknown',
}

def determine_winner(event, fault_side, name_a, name_b):
    """
    fault_side = 'near' | 'far'  (player who made the fault)
    FAR = Player A,  NEAR = Player B
    Winner = the OTHER player.
    """
    if event == 'unknown' or fault_side == 'unknown':
        return 'unknown'
    if fault_side == 'near':
        return name_a    # near player faulted -> far player (A) wins
    return name_b        # far player faulted -> near player (B) wins


# ============================================================
# MODULE 6 — CUMULATIVE SCORE TRACKING
# ============================================================
def track_scores(winners, name_a, name_b):
    """
    Returns list of (score_A, score_B) after each rally.
    Resets at game boundaries (first to 21 with 2-point lead, or 30).
    """
    sa, sb  = 0, 0
    scores  = []
    for w in winners:
        if w == name_a:
            sa += 1
        elif w == name_b:
            sb += 1
        scores.append((sa, sb))
        # Game reset
        a_wins = (sa >= 21 and sa - sb >= 2) or sa == 30
        b_wins = (sb >= 21 and sb - sa >= 2) or sb == 30
        if a_wins or b_wins:
            sa, sb = 0, 0
    return scores


# ============================================================
# MODULE 7 — WINNING SHOT CLASSIFICATION
# ============================================================

# Speed thresholds based on LAUNCH speed (first 6 frames), px/s.
# Using launch speed avoids contamination from the opponent's faster
# return shot which inflates peak_speed in the segment.
#
# Calibrated from observed data for this camera setup (end-on, 1080p):
#   court spans ~350-550 px vertically → 1 m ≈ 40-80 px depending on depth
#   Drop shots:  launch_speed  90 - 600 px/s  (~10-40 km/h)
#   Drives:      launch_speed 600 - 1200 px/s  (~40-80 km/h)
#   Smashes:     launch_speed > 1000 px/s       (>70 km/h)
_SMASH_LAUNCH = 450   # px/s launch speed → smash / net smash
_DROP_LAUNCH  = 380   # px/s launch speed → drop (below this = drop)
_DRIVE_LAUNCH = 400   # px/s launch speed → drive (flat, medium pace)
_HIGH_SPEED   = 2500  # px/s peak speed   → very fast (smash catch-all)
_MED_SPEED    = 1000  # px/s peak speed   → medium pace
_LOW_SPEED    =  400  # px/s peak speed   → slow
_FRONT_COURT  =  2.0  # metres from net — front court zone
_BACK_COURT   =  4.0  # metres from net — back court zone


def segment_shots(shuttle_df, start_frame, end_frame, fps):
    """
    Find contact frames (player-hit events) within a rally by detecting
    speed valleys in the shuttle trajectory.

    Speed valleys correspond to the moment the shuttle decelerates as it
    reaches a player and is struck again.

    Parameters
    ----------
    shuttle_df   : DataFrame with columns Frame, X, Y, Visibility
    start_frame  : first frame of the rally (inclusive)
    end_frame    : last frame of the rally (inclusive)
    fps          : frames per second of the video

    Returns
    -------
    list[int]  — sorted list of contact frame numbers
    """
    win = shuttle_df[
        (shuttle_df['Frame'] >= start_frame) &
        (shuttle_df['Frame'] <= end_frame) &
        (shuttle_df['Visibility'] == 1)
    ].copy().sort_values('Frame').reset_index(drop=True)

    if len(win) < 4:
        return []

    # Per-frame speed between consecutive visible detections (px/s)
    dx = win['X'].diff()
    dy = win['Y'].diff()
    dt = win['Frame'].diff() / fps
    speed = (np.sqrt(dx**2 + dy**2) / dt.replace(0, np.nan)).fillna(0)
    win['speed'] = speed

    # Short rolling average to smooth tracking noise
    smoothed = win['speed'].rolling(window=5, center=True, min_periods=1).mean().values

    # Find valleys (contacts) by inverting and finding peaks
    inverted = -smoothed
    min_dist = max(1, int(fps * 0.27))   # ~8 frames at 30 fps
    peaks, _ = find_peaks(inverted, prominence=80, distance=min_dist)

    contact_frames = sorted(win.iloc[i]['Frame'] for i in peaks)
    return [int(f) for f in contact_frames]


def extract_shot_features(shuttle_df, player_df, contact_frame,
                          next_contact_frame, net_Y, H, fps):
    """
    Extract trajectory features for a single shot segment
    (contact_frame → next_contact_frame).

    Parameters
    ----------
    shuttle_df         : full shuttle DataFrame
    player_df          : full player DataFrame
    contact_frame      : frame where the shot starts (player hits shuttle)
    next_contact_frame : frame where the shot ends (next contact / rally end)
    net_Y              : pixel Y of the net line
    H                  : homography matrix (image → real-world metres), or None
    fps                : frames per second

    Returns
    -------
    dict with keys: peak_speed, launch_vy, launch_vx, has_arc,
                    dist_net_m, hitter_side, lateral_ratio
    """
    seg = shuttle_df[
        (shuttle_df['Frame'] >= contact_frame) &
        (shuttle_df['Frame'] <= next_contact_frame) &
        (shuttle_df['Visibility'] == 1)
    ].copy().sort_values('Frame').reset_index(drop=True)

    # ── peak_speed ───────────────────────────────────────────────
    if len(seg) >= 2:
        dx = seg['X'].diff()
        dy = seg['Y'].diff()
        dt = seg['Frame'].diff() / fps
        speeds = (np.sqrt(dx**2 + dy**2) / dt.replace(0, np.nan)).fillna(0)
        peak_speed = float(speeds.max())
    else:
        peak_speed = 0.0

    # ── launch velocity (first 5 visible frames after contact) ───
    early = seg.head(6)   # up to 6 rows → 5 diffs
    if len(early) >= 2:
        dx_e = float(early['X'].iloc[-1] - early['X'].iloc[0])
        dy_e = float(early['Y'].iloc[-1] - early['Y'].iloc[0])
        dt_e = float((early['Frame'].iloc[-1] - early['Frame'].iloc[0])) / fps
        if dt_e > 0:
            launch_vx = dx_e / dt_e
            launch_vy = dy_e / dt_e   # +vy = toward camera (near baseline)
        else:
            launch_vx = launch_vy = 0.0
    else:
        launch_vx = launch_vy = 0.0

    # ── has_arc: vy changes sign during the shot ─────────────────
    # Threshold raised to 18px (was 10px) to avoid false arcs from
    # tracking jitter on fast, flat shots (drives, smashes).
    # Also require the sign change over at least 3 consecutive frames
    # so a single noisy detection doesn't flip the flag.
    has_arc = False
    if len(seg) >= 5:
        dy_series = seg['Y'].diff().dropna().values
        ARC_THR = 18   # px — minimum meaningful direction change
        # Require at least 2 consecutive frames moving in each direction
        pos_run = sum(1 for v in dy_series if v >  ARC_THR)
        neg_run = sum(1 for v in dy_series if v < -ARC_THR)
        has_arc = bool(pos_run >= 2 and neg_run >= 2)

    # ── dist_net_m at contact frame ──────────────────────────────
    dist_net_m = None
    if H is not None and len(seg) > 0:
        try:
            cx = float(seg.iloc[0]['X'])
            cy = float(seg.iloc[0]['Y'])
            dist_net_m = shuttle_dist_from_net_m(cx, cy, H)
        except Exception:
            dist_net_m = None

    # ── landing position (last detected shuttle position in segment) ──
    # This is where the shuttle ENDS UP after the shot, not where it
    # was hit from.  For a drop shot the shuttle lands close to the net
    # regardless of where the hitter was standing — this is a much
    # stronger drop signal than the contact position.
    landing_y        = float(seg.iloc[-1]['Y']) if len(seg) > 0 else 0.0
    landing_x        = float(seg.iloc[-1]['X']) if len(seg) > 0 else 0.0
    landing_dist_net_m = None
    if H is not None and len(seg) > 0:
        try:
            landing_dist_net_m = shuttle_dist_from_net_m(landing_x, landing_y, H)
        except Exception:
            landing_dist_net_m = None

    # ── final_vy: average vy in the last 4 visible frames ────────
    # Negative final_vy (in image coords) = shuttle moving toward far baseline.
    # Positive final_vy = moving toward near baseline.
    # For a drop the shuttle should be moving TOWARD the net (descending
    # toward net_Y) in the last frames, i.e. final_vy moves toward net_Y.
    final_vy = 0.0
    if len(seg) >= 3:
        tail = seg.tail(4)
        if len(tail) >= 2:
            dy_tail = float(tail['Y'].iloc[-1] - tail['Y'].iloc[0])
            dt_tail = float(tail['Frame'].iloc[-1] - tail['Frame'].iloc[0]) / fps
            if dt_tail > 0:
                final_vy = dy_tail / dt_tail

    # ── hitter_side: near vs far based on shuttle Y vs net_Y ─────
    if len(seg) > 0:
        shuttle_y_at_contact = float(seg.iloc[0]['Y'])
        hitter_side = 'near' if shuttle_y_at_contact > net_Y else 'far'
    else:
        hitter_side = 'unknown'

    # ── lateral_ratio ─────────────────────────────────────────────
    # Minimum denominator raised to 50 px/s (was 1.0) so nearly-horizontal
    # shots (launch_vy ≈ 0, e.g. a flat drive) don't blow the ratio up and
    # spuriously trigger hook/slice classification.
    lateral_ratio = abs(launch_vx) / max(abs(launch_vy), 50.0)

    return {
        'peak_speed':        peak_speed,
        'launch_vy':         launch_vy,
        'launch_vx':         launch_vx,
        'has_arc':           has_arc,
        'dist_net_m':        dist_net_m,
        'hitter_side':       hitter_side,
        'lateral_ratio':     lateral_ratio,
        'contact_y':         float(seg.iloc[0]['Y']) if len(seg) > 0 else 0.0,
        'landing_y':         landing_y,
        'landing_dist_net_m': landing_dist_net_m,
        'final_vy':          final_vy,
    }


def classify_shot(feats, event):
    """
    Classify the winning shot using features from extract_shot_features
    (enriched into feats before this call).

    Function signature is unchanged — drop-in replacement for Module 7.

    Returns one of: smash, net smash, clear, drop, lift, push, block,
                    slice, hook, drive, unknown

    Key design notes
    ----------------
    * All direction checks (launch_vy sign) are normalised relative to
      hitter_side so BOTH far and near player shots are handled correctly.
      "toward_net_vy" is POSITIVE when the shuttle moves toward the net
      regardless of which end the hitter stands on.
    * lift vs clear are separated by court zone: lift = front court hitting
      up toward back; clear = back court hitting up to opponent's back.
    * The fallback is 'unknown' (not 'push') so back-court unclassified
      shots are not mislabelled as a front-court shot type.
    """
    peak_speed    = feats.get('peak_speed',    feats.get('early_speed', feats.get('speed', 0)))
    launch_vy     = feats.get('launch_vy',     feats.get('vy', 0))
    launch_vx     = feats.get('launch_vx',     feats.get('vx', 0))
    has_arc       = feats.get('has_arc',       False)
    hitter_side   = feats.get('hitter_side',   'near')
    lateral_ratio = feats.get('lateral_ratio',
                               abs(launch_vx) / max(abs(launch_vy), 50.0))
    dist_net_m    = feats.get('dist_net_m',    None)

    # ── Launch speed (primary discriminator) ─────────────────────
    # Computed from first 6 frames so it reflects the actual shot,
    # not the opponent's faster return which inflates peak_speed.
    launch_speed = math.hypot(launch_vx, launch_vy)

    # ── Court-zone flags (contact position) ──────────────────────
    if dist_net_m is None:
        contact_y   = feats.get('contact_y', 0)
        net_Y_px    = feats.get('net_Y',     0)
        net_tol     = feats.get('net_tol_px', 60)
        front_court = abs(contact_y - net_Y_px) < net_tol * 3
        back_court  = not front_court
    else:
        front_court = dist_net_m <= _FRONT_COURT
        back_court  = dist_net_m >  _BACK_COURT

    # ── Normalised toward-net velocity ───────────────────────────
    # Positive = shuttle moving toward the net (regardless of hitter side).
    if hitter_side == 'near':
        toward_net_vy = -launch_vy   # near player: toward net = upward = vy < 0
    else:
        toward_net_vy = launch_vy    # far  player: toward net = downward = vy > 0

    # ── Decision tree ────────────────────────────────────────────
    # Primary discriminator: launch_speed (first 6 frames).
    # Peak_speed is a secondary check only — it catches smashes where
    # the shuttle leaves the frame before 6 frames are tracked.

    # 1. Smash — very fast launch toward net, back court
    if (launch_speed > _SMASH_LAUNCH or peak_speed > _HIGH_SPEED) \
            and toward_net_vy > 50 and back_court:
        return 'smash'

    # 2. Net smash — same but front court
    if (launch_speed > _SMASH_LAUNCH or peak_speed > _HIGH_SPEED) \
            and toward_net_vy > 50 and front_court:
        return 'net smash'

    # 3. Drop — slow launch, moving toward opponent's court.
    #    launch_speed < _DROP_LAUNCH is the key gate: drops are slow.
    #    toward_net_vy > 30 ensures the shuttle is heading toward the net
    #    (not a serve or a shot going sideways/backward).
    #    No front_court requirement — any court position can play a drop.
    if launch_speed < _DROP_LAUNCH and toward_net_vy > 30:
        return 'drop'

    # 4. Clear — arcing shot from back court, medium pace
    if has_arc and back_court:
        return 'clear'

    # 5. Lift — arcing shot from front court upward to opponent's back
    if has_arc and front_court:
        return 'lift'

    # 6. Drive — fast, flat (low vy relative to overall speed)
    if launch_speed > _DRIVE_LAUNCH and abs(launch_vy) < launch_speed * 0.5:
        return 'drive'

    # 7. Hook — strong cross-court angle at decent pace
    if lateral_ratio > 1.2 and launch_speed > _DRIVE_LAUNCH:
        return 'hook'

    # 8. Slice — moderate cross-court angle
    if lateral_ratio > 0.7 and launch_speed > 200:
        return 'slice'

    # 9. Block — very slow shot near net (no pace, front court)
    if front_court and launch_speed < 300:
        return 'block'

    # 10. Push — front court catch-all
    if front_court:
        return 'push'

    # 11. Fallback
    return 'unknown'


# ============================================================
# HELPERS
# ============================================================
def _mmss(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def _get_fps(video_file):
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps if fps > 0 else 30.0


def _save_debug_image(frame, court_poly, net_Y, net_left, net_right, out_path):
    """Save annotated frame showing detected court boundary and net line."""
    img = frame.copy()
    cv2.polylines(img, [court_poly.reshape(-1, 1, 2).astype(int)], True, (0, 255, 0), 3)
    cv2.line(img,
             (int(net_left[0]),  int(net_Y)),
             (int(net_right[0]), int(net_Y)),
             (0, 0, 255), 2)
    cv2.putText(img, f"NET Y={net_Y:.0f}px", (10, int(net_Y) - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    for label, pt in zip(["TL", "TR", "BR", "BL"], court_poly):
        cv2.circle(img, tuple(pt.astype(int)), 8, (0, 255, 255), -1)
        cv2.putText(img, label, tuple((pt + [6, -6]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.imwrite(out_path, img)
    print(f"  Debug image saved -> {out_path}")


# ============================================================
# COURT DEBUG VIDEO
# ============================================================
def generate_court_debug_video(video_file, court_poly, net_Y, net_left,
                                net_right, name_a, name_b, out_path):
    """
    Write a full output video with the auto-detected court boundary
    and net line drawn on every frame.

    Annotations drawn:
      - Court boundary  : green polygon (4 corners)
      - Corner labels   : TL / TR / BR / BL with yellow dots
      - Net line        : red horizontal line at net_Y
      - Player sides    : FAR label (top) and NEAR label (bottom)
      - Frame counter   : top-right corner
    """
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out    = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    poly_pts   = court_poly.reshape(-1, 1, 2).astype(np.int32)
    net_left_pt  = (int(net_left[0]),  int(net_Y))
    net_right_pt = (int(net_right[0]), int(net_Y))

    # Pre-compute corner label positions
    corner_labels = list(zip(
        ["TL", "TR", "BR", "BL"],
        court_poly.astype(int)
    ))

    frame_idx = 0
    print(f"  Writing court debug video ({total} frames)...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # ── Court boundary ─────────────────────────────────
        cv2.polylines(frame, [poly_pts], True, (0, 255, 0), 2)

        # ── Shaded court area (semi-transparent green fill) ─
        overlay = frame.copy()
        cv2.fillPoly(overlay, [poly_pts], (0, 80, 0))
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

        # ── Net line ────────────────────────────────────────
        cv2.line(frame, net_left_pt, net_right_pt, (0, 0, 255), 2)
        # Net label centred on the line
        net_cx = (net_left_pt[0] + net_right_pt[0]) // 2
        cv2.putText(frame, "NET", (net_cx - 18, int(net_Y) - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # ── Corner dots and labels ──────────────────────────
        for label, pt in corner_labels:
            cv2.circle(frame, tuple(pt), 6, (0, 255, 255), -1)
            offset = np.array([8, -8])
            cv2.putText(frame, label,
                        tuple((pt + offset).tolist()),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                        (0, 255, 255), 2)

        # ── Player side labels ──────────────────────────────
        # FAR player label — top centre of court
        TL, TR = court_poly[0].astype(int), court_poly[1].astype(int)
        far_cx  = (TL[0] + TR[0]) // 2
        far_cy  = (TL[1] + TR[1]) // 2 + 20
        cv2.putText(frame, f"FAR: {name_a}",
                    (far_cx - 60, far_cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

        # NEAR player label — bottom centre of court
        BL, BR = court_poly[3].astype(int), court_poly[2].astype(int)
        near_cx = (BL[0] + BR[0]) // 2
        near_cy = (BL[1] + BR[1]) // 2 - 10
        cv2.putText(frame, f"NEAR: {name_b}",
                    (near_cx - 65, near_cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

        # ── Frame counter ───────────────────────────────────
        cv2.putText(frame, f"Frame {frame_idx}",
                    (w - 140, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        out.write(frame)
        frame_idx += 1

        if frame_idx % 300 == 0:
            print(f"    {frame_idx}/{total} frames written...")

    cap.release()
    out.release()
    print(f"  Court debug video saved -> {out_path}")


# ============================================================
# ARGUMENT PARSING
# ============================================================
def parse_args():
    p = argparse.ArgumentParser(
        description="Badminton feature extraction: auto-annotates court/net "
                    "and adds win/score/shot columns to the rally CSV."
    )
    p.add_argument("--video",    required=True,
                   help="Input video file (.mp4)")
    p.add_argument("--rally",    default=None,
                   help="Rally CSV from detect_rallies.py "
                        "(default: <video>_T.csv in same folder)")
    p.add_argument("--shuttle",  default=None,
                   help="Shuttle tracking CSV (*_ball_filled.csv) "
                        "(default: <video>_ball_filled.csv)")
    p.add_argument("--player",   default=None,
                   help="Player detections CSV "
                        "(default: player_detections.csv in same folder)")
    p.add_argument("--out",      default=None,
                   help="Output extended CSV path "
                        "(default: <video>_extended.csv)")
    p.add_argument("--player_a", default="Player A",
                   help="Name for the FAR player (top of image, default: 'Player A')")
    p.add_argument("--player_b", default="Player B",
                   help="Name for the NEAR player (bottom of image, default: 'Player B')")
    p.add_argument("--vlm", action="store_true",
                   help="Use Gemini VLM for event + shot classification "
                        "(requires: pip install google-genai, and GOOGLE_API_KEY env var)")
    p.add_argument("--vlm-model", default="gemini-2.0-flash", dest="vlm_model",
                   help="Gemini model id (default: gemini-2.0-flash; "
                        "use gemini-2.0-pro / gemini-1.5-pro for higher accuracy)")
    p.add_argument("--vlm-quantize", action="store_true", dest="vlm_quantize",
                   help="(Ignored for cloud Gemini; kept for local-model compatibility)")
    p.add_argument("--vlm-timeout", type=int, default=60, dest="vlm_timeout",
                   help="Seconds before a VLM call times out and falls back "
                        "to rule-based (default: 60)")
    return p.parse_args()


# ============================================================
# MAIN
# ============================================================
def main():
    args = parse_args()

    video_file = args.video
    video_dir  = os.path.dirname(video_file) or "."
    video_stem = os.path.splitext(os.path.basename(video_file))[0]

    # Derive default paths from video location if not provided
    rally_csv   = args.rally   or os.path.join(video_dir, video_stem + "_T.csv")
    shuttle_csv = args.shuttle or os.path.join(video_dir, video_stem + "_ball_filled.csv")
    player_csv  = args.player  or os.path.join(video_dir, "player_detections.csv")
    out_csv     = args.out     or os.path.join(video_dir, video_stem + "_extended.csv")
    name_a      = args.player_a
    name_b      = args.player_b

    print("=" * 65)
    print("  BADMINTON FEATURE EXTRACTION PIPELINE")
    print("=" * 65)
    print(f"  Video   : {video_file}")
    print(f"  Rally   : {rally_csv}")
    print(f"  Shuttle : {shuttle_csv}")
    print(f"  Player  : {player_csv}")
    print(f"  Output  : {out_csv}")
    print(f"  Names   : FAR={name_a}  NEAR={name_b}")

    # ── Load ──────────────────────────────────────────────────
    print("\n[1/7] Loading inputs...")
    rally_df   = pd.read_csv(rally_csv)
    shuttle_df = pd.read_csv(shuttle_csv)
    player_df  = pd.read_csv(player_csv)
    fps        = _get_fps(video_file)
    print(f"  {len(rally_df)} rallies  |  {len(shuttle_df)} shuttle rows  |  FPS={fps:.1f}")

    # ── Court corners (video-adaptive) ────────────────────────
    print("\n[2/7] Auto-detecting court corners from video...")
    corners, ref_frame, _frame_no = auto_detect_court(video_file)

    # Refine using white boundary lines inside the court
    print("  Refining corners with white court lines...")
    corners = refine_corners_with_lines(ref_frame, corners)

    court_poly_cv   = corners.reshape(-1, 1, 2).astype(np.float32)
    court_poly_draw = corners.astype(np.int32)

    # ── Net position ──────────────────────────────────────────
    print("\n[3/7] Computing net position...")
    net_Y, net_left, net_right, H, _ = compute_net(corners)
    net_Y = snap_net(ref_frame, net_Y, corners)

    # Recompute net post X positions at the (possibly snapped) net_Y.
    # These are passed to analyze_rally_end for the geometric event check.
    TL_c, TR_c, BR_c, BL_c = corners
    _t_l    = (net_Y - TL_c[1]) / (BL_c[1] - TL_c[1]) if BL_c[1] != TL_c[1] else 0.5
    _t_r    = (net_Y - TR_c[1]) / (BR_c[1] - TR_c[1]) if BR_c[1] != TR_c[1] else 0.5
    net_left_x  = float(TL_c[0] + _t_l * (BL_c[0] - TL_c[0]))
    net_right_x = float(TR_c[0] + _t_r * (BR_c[0] - TR_c[0]))
    print(f"  Net X extent: left={net_left_x:.0f}px  right={net_right_x:.0f}px")

    # ── Player sides ──────────────────────────────────────────
    print("\n[4/7] Assigning player sides...")
    try:
        assign_player_sides(player_csv)
    except Exception as e:
        print(f"  Warning: {e}  -- using court position for player assignment")

    # Scale NET_TOL_PX to image height
    img_h      = ref_frame.shape[0]
    net_tol_px = img_h * NET_TOL_FRAC
    print(f"  Net tolerance: {net_tol_px:.0f}px  (image height={img_h}px)")

    # Save debug image (single frame)
    debug_img_path = os.path.join(video_dir, video_stem + "_court_debug.jpg")
    _save_debug_image(ref_frame, court_poly_draw, net_Y,
                      net_left, net_right, debug_img_path)

    # ── VLM model (optional) ─────────────────────────────────────────────────
    vlm_model = vlm_proc = None
    if getattr(args, 'vlm', False):
        try:                                  # run as module: python -m analysis.extract_features
            from analysis.vlm_rally_end import (
                load_vlm_model, extract_rally_frames, get_trajectory_coords,
                analyze_rally_with_vlm, vlm_to_pipeline as _vlm_to_pipeline,
            )
        except ModuleNotFoundError:           # run as script: python analysis/extract_features.py
            from vlm_rally_end import (
                load_vlm_model, extract_rally_frames, get_trajectory_coords,
                analyze_rally_with_vlm, vlm_to_pipeline as _vlm_to_pipeline,
            )
        print("\n[VLM] Initialising Gemini...")
        vlm_model, vlm_proc = load_vlm_model(
            model_id=getattr(args, 'vlm_model', 'gemini-2.0-flash'),
            quantize=getattr(args, 'vlm_quantize', False),
        )

    # Open per-rally VLM log (one JSON line per rally, written as we go)
    vlm_log = None
    if vlm_model is not None:
        vlm_log_path = out_csv.replace('.csv', '_vlm_log.jsonl')
        vlm_log = open(vlm_log_path, 'w', encoding='utf-8')
        print(f"  VLM log -> {vlm_log_path}")

    # ── Per-rally analysis ────────────────────────────────────
    print("\n[5/7] Analysing each rally...")
    results = []

    for idx, row in rally_df.iterrows():
        s_sec = float(row['Start_Time_sec'])
        e_sec = float(row['End_Time_sec'])
        ef    = int(row['End_Frame'])

        vlm_raw  = None
        vlm_shot = None
        if vlm_model is not None:
            _frames = extract_rally_frames(video_file, ef, n_frames=20)
            _traj   = get_trajectory_coords(shuttle_df, ef, n_positions=20)
            vlm_raw = analyze_rally_with_vlm(
                _frames, _traj, vlm_model, vlm_proc,
                timeout_sec=getattr(args, 'vlm_timeout', 60),
            )
            event, fault_side, conf, vlm_shot = _vlm_to_pipeline(vlm_raw)
            feats = {
                'analysis_end_frame':   ef,
                'analysis_start_frame': max(0, ef - 20),
                'net_Y':                net_Y,
                'net_tol_px':           net_tol_px,
            }
            # Low-confidence VLM result: run rule-based and let HIGH-conf override
            if conf == "LOW":
                rb_event, rb_fault, rb_conf, rb_feats = analyze_rally_end(
                    shuttle_df, ef, court_poly_cv, corners,
                    net_Y, fps, net_tol_px, H,
                    net_left_x=net_left_x, net_right_x=net_right_x,
                )
                if rb_conf == "HIGH":
                    event, fault_side, conf = rb_event, rb_fault, rb_conf
                    feats.update(rb_feats)
        else:
            event, fault_side, conf, feats = analyze_rally_end(
                shuttle_df, ef, court_poly_cv, corners,
                net_Y, fps, net_tol_px, H,
                net_left_x=net_left_x, net_right_x=net_right_x,
            )

        # ── Find the shot that ended the rally ───────────────────
        # We always classify the LAST contact → rally end.
        # This is the shot that directly finished the point:
        #   wins_by_landing → the winner's final shot (lands in)
        #   hits_net        → the fault player's shot that hit the net
        #   out_of_bounds   → the fault player's shot that went out
        #
        # Classifying the last contact matches what a human observer
        # naturally describes ("the drop hit the net", "the smash went
        # out") and avoids the confusion of labelling the setup shot
        # (second-to-last contact) which is a different shot entirely.
        contact_frames = segment_shots(
            shuttle_df, int(row['Start_Frame']), int(row['End_Frame']), fps
        )

        if len(contact_frames) >= 1:
            winning_contact = contact_frames[-1]
            next_contact    = int(row['End_Frame'])
        else:
            # No contacts detected — estimate from rally end
            winning_contact = int(row['End_Frame']) - int(fps * 1.5)
            next_contact    = int(row['End_Frame'])

        shot_feats = extract_shot_features(
            shuttle_df, player_df, winning_contact, next_contact,
            net_Y, H, fps
        )
        feats.update(shot_feats)

        winner   = determine_winner(event, fault_side, name_a, name_b)
        win_str  = _WIN_STR[event]
        lose_str = _LOSE_STR[event]
        # VLM shot type takes priority; fall back to rule-based when unknown
        shot = (vlm_shot if vlm_shot and vlm_shot != 'unknown'
                else classify_shot(feats, event))

        winning_shot_sec = winning_contact / fps

        results.append(dict(
            start_sec=s_sec, end_sec=e_sec,
            winner=winner, win_reason=win_str, lose_reason=lose_str,
            ball_type=shot, confidence=conf, feats=feats,
            winning_shot_frame=winning_contact,
            winning_shot_sec=winning_shot_sec,
        ))
        vlm_tag = " [VLM]" if vlm_raw is not None else ""
        print(f"  Rally {idx+1:>3}: {_mmss(s_sec)}->{_mmss(e_sec)}  "
              f"{event:<18}  fault={fault_side:<5}  "
              f"winner={winner:<14}  shot={shot:<22}  "
              f"winning_shot={_mmss(winning_shot_sec)}  [{conf}]{vlm_tag}")

        if vlm_log is not None:
            vlm_log.write(json.dumps({
                'rally':       idx + 1,
                'start_time':  _mmss(s_sec),
                'end_time':    _mmss(e_sec),
                'end_frame':   ef,
                'vlm_raw':     vlm_raw,
                'event':       event,
                'fault_side':  fault_side,
                'confidence':  conf,
                'shot':        shot,
                'winner':      winner,
            }) + '\n')
            vlm_log.flush()

    if vlm_log is not None:
        vlm_log.close()
        print(f"  VLM log written.")

    # ── Scores ────────────────────────────────────────────────
    print("\n[6/7] Tracking scores...")
    scores = track_scores([r['winner'] for r in results], name_a, name_b)

    # ── Output CSV ────────────────────────────────────────────
    print("\n[7/7] Writing output CSV...")
    rows = []
    for i, r in enumerate(results):
        sa, sb = scores[i]
        rows.append({
            'start_time':           _mmss(r['start_sec']),
            'end_time':             _mmss(r['end_sec']),
            'win_point_player':     r['winner'],
            'win_reason':           r['win_reason'],
            'ball_types':           r['ball_type'],
            'winning_shot_time':    _mmss(r['winning_shot_sec']),
            'winning_shot_frame':   r['winning_shot_frame'],
            'lose_reason':          r['lose_reason'],
            'roundscore_A':         sa,
            'roundscore_B':         sb,
            'detection_confidence': r['confidence'],
            'analysis_frames':      f"{r['feats'].get('analysis_start_frame', '')} - {r['feats'].get('analysis_end_frame', '')}",
        })

    os.makedirs(os.path.dirname(os.path.abspath(out_csv)), exist_ok=True)
    pd.DataFrame(rows).to_csv(out_csv, index=False)

    print(f"\n  Saved -> {out_csv}")
    hdr = f"{'#':>3}  {'Start':>6}  {'End':>6}  {'Winner':<16}  {'Win Reason':<37}  {'Shot':<24}  Score"
    print("\n" + hdr)
    print("-" * len(hdr))
    for i, r in enumerate(rows):
        print(f"{i+1:>3}  {r['start_time']:>6}  {r['end_time']:>6}  "
              f"{r['win_point_player']:<16}  {r['win_reason']:<37}  "
              f"{r['ball_types']:<24}  "
              f"{r['roundscore_A']}-{r['roundscore_B']}")

    unknowns = sum(1 for r in rows    if r['win_point_player'] == 'unknown')
    low_conf = sum(1 for r in results if r['confidence'] == 'LOW')
    print(f"\n  Total: {len(rows)} rallies  |  Unknown: {unknowns}  |  LOW confidence: {low_conf}")
    print("\nDone.")


if __name__ == "__main__":
    main()
