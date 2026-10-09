"""
auto_court.py
-------------
Non-interactive court + net detection for win_predictor's <name>_court.json.

Unlike analysis/annotate_court.py (manual 4-corner + net-cable click), this
reuses extract_features.py's HSV-based auto court detector so a match can
run through the pipeline with zero clicks.

Two-stage corner detection:
  1. Green-mask blob (extract_features.auto_detect_court) -- fast, but only
     the extent of the green playing surface, which commonly extends past
     the painted doubles sideline (sponsor mats, warm-up strip, etc).
  2. White-line refinement (this file) -- detects the actual painted
     boundary lines inside that green region and snaps to them. Badminton
     courts paint BOTH the doubles sideline and, 0.46m inside it, the
     singles sideline -- so "the outermost white line" is NOT automatically
     the right one for a singles match. This clusters left/right white
     lines into distinct physical lines and picks the one matching
     --court_type (default: singles, since this pipeline's benchmarked
     matches are singles).

The net GROUND line (net_Y) then comes from a real homography between the
selected corners and the known court dimensions for that court_type -- this
part is geometrically exact given correct corner detection.

net_top_Y (the net CABLE, ~1.55m above the court) can NOT be derived from a
flat-court homography -- that needs the camera's full 3D pose. Empirically
(see memory: production matches with manually-annotated courts), net_top_Y
sits within a few pixels of the FAR baseline in this camera convention, so
it's approximated as the mean Y of the TL/TR corners. This is a real
approximation, not a measurement -- for maximum win-reason accuracy, use
annotate_court.py's manual net-cable click instead. Override with
--net_top_y if you know the true value.

Usage:
    python analysis/auto_court.py --video YourMatch/YourMatch.mp4 \\
        --out YourMatch/YourMatch_court.json --court_type singles
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_features as ef
from extract_features import auto_detect_court, snap_net, _sort_corners, _try_detect_corners
from frame_picker import pick_frame_fast

SINGLES_WIDTH_M = 5.18
DOUBLES_WIDTH_M = 6.1


def _detect_white_lines(frame, approx_corners):
    """Long white line segments inside the green court area, split into
    horizontal (baselines) and diagonal (sidelines). Same HSV/Hough params
    as extract_features.refine_corners_with_lines."""
    h, w = frame.shape[:2]
    court_mask = np.zeros((h, w), dtype=np.uint8)
    import cv2
    cv2.fillPoly(court_mask, [approx_corners.astype(np.int32)], 255)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    white_mask = cv2.inRange(hsv, np.array([0, 0, 170]), np.array([180, 60, 255]))
    white_court = cv2.bitwise_and(white_mask, court_mask)

    min_len = int(min(h, w) * 0.20)
    lines = cv2.HoughLinesP(white_court, 1, np.pi / 180, threshold=40,
                             minLineLength=min_len, maxLineGap=20)
    horiz, diag = [], []
    if lines is None:
        return horiz, diag
    for ln in lines:
        x1, y1, x2, y2 = ln[0]
        angle  = abs(math.degrees(math.atan2(y2 - y1, x2 - x1))) % 180
        length = math.hypot(x2 - x1, y2 - y1)
        entry  = (x1, y1, x2, y2, length)
        if angle < 25 or angle > 155:
            horiz.append(entry)
        else:
            diag.append(entry)
    return horiz, diag


def _cluster_1d(values, gap_thresh=15.0):
    """Group sorted scalar values into clusters where consecutive gap <=
    gap_thresh (collapses Hough's many near-duplicate detections of the
    same physical line into one). Returns [(mean, count), ...] ascending."""
    values = np.sort(np.asarray(values, dtype=float))
    clusters, cur = [], [values[0]]
    for v in values[1:]:
        if v - cur[-1] <= gap_thresh:
            cur.append(v)
        else:
            clusters.append(cur)
            cur = [v]
    clusters.append(cur)
    return [(float(np.mean(c)), len(c)) for c in clusters]


def refine_corners_court_type(frame, approx_corners, court_type="singles"):
    """
    Snap green-mask corners to the actual painted boundary lines, picking
    the singles or doubles sideline as requested. Falls back to the
    green-mask corners (with a printed reason) whenever the line signal
    is too weak to trust.

    Returns (corners, ok) -- ok is False whenever the line signal wasn't
    trustworthy enough to confirm court_type, in which case corners falls
    back to the cruder (but honestly-labeled-approximate) green-mask blob
    rather than risk silently returning the wrong sideline.
    """
    h, w = frame.shape[:2]
    horiz, diag = _detect_white_lines(frame, approx_corners)
    if len(horiz) < 2 or len(diag) < 2:
        print("  Line refinement: not enough long white lines detected, "
              "keeping green-mask corners (less precise)")
        return approx_corners, False

    green_top_y    = min(approx_corners[0][1], approx_corners[1][1])
    green_bottom_y = max(approx_corners[2][1], approx_corners[3][1])
    green_left_x   = min(approx_corners[0][0], approx_corners[3][0])
    green_right_x  = max(approx_corners[1][0], approx_corners[2][0])
    center_x       = (green_left_x + green_right_x) / 2
    EDGE_MARGIN    = 20

    horiz_inside = [l for l in horiz if green_top_y + EDGE_MARGIN
                    < (l[1] + l[3]) / 2 < green_bottom_y - EDGE_MARGIN] or horiz
    diag_inside  = [l for l in diag  if green_left_x + EDGE_MARGIN
                    < (l[0] + l[2]) / 2 < green_right_x - EDGE_MARGIN] or diag

    far_baseline  = min(horiz_inside, key=lambda l: (l[1] + l[3]) / 2)
    near_baseline = max(horiz_inside, key=lambda l: (l[1] + l[3]) / 2)
    ref_y = near_baseline[1]  # sidelines are most separated near the camera

    def x_at_ref(l):
        x1, y1, x2, y2, _ = l
        if y2 == y1:
            return (x1 + x2) / 2
        t = (ref_y - y1) / (y2 - y1)
        return x1 + t * (x2 - x1)

    left_lines  = [l for l in diag_inside if x_at_ref(l) < center_x]
    right_lines = [l for l in diag_inside if x_at_ref(l) >= center_x]
    if not left_lines or not right_lines:
        print("  Line refinement: white lines found on only one side, "
              "keeping green-mask corners (less precise)")
        return approx_corners, False

    left_clusters  = sorted(_cluster_1d([x_at_ref(l) for l in left_lines]))
    right_clusters = sorted(_cluster_1d([x_at_ref(l) for l in right_lines]))

    # Physically, the singles sideline sits ~0.46m inside the doubles
    # sideline -- a small, bounded gap. Distinct-line separation outside
    # this range means the "inner" cluster is something else (a service
    # line remnant, noise), not the singles line.
    SEP_MIN_PX, SEP_MAX_PX = 15.0, 150.0

    if court_type == "doubles":
        left_target_x, right_target_x = left_clusters[0][0], right_clusters[-1][0]
    else:  # singles -- the line 0.46m INSIDE the doubles sideline
        left_sep  = left_clusters[-1][0]  - left_clusters[0][0]  if len(left_clusters)  >= 2 else 0
        right_sep = right_clusters[-1][0] - right_clusters[0][0] if len(right_clusters) >= 2 else 0
        left_ok  = len(left_clusters)  >= 2 and SEP_MIN_PX <= left_sep  <= SEP_MAX_PX
        right_ok = len(right_clusters) >= 2 and SEP_MIN_PX <= right_sep <= SEP_MAX_PX
        if not (left_ok and right_ok):
            # Can't confidently tell singles from doubles on this side --
            # do NOT silently keep whatever single line was found (it could
            # be the doubles line), that produces a wrong result mislabeled
            # as singles. Fall back all the way to the (clearly cruder,
            # honestly-approximate) green-mask corners instead.
            print("  Line refinement: could not distinguish singles from "
                  "doubles sideline (found "
                  f"{len(left_clusters)} left / {len(right_clusters)} right "
                  "distinct line(s)) -- keeping green-mask corners. "
                  "Use --court_mode manual for an accurate court on this video.")
            return approx_corners, False
        left_target_x, right_target_x = left_clusters[-1][0], right_clusters[0][0]

    left_side  = min(left_lines,  key=lambda l: abs(x_at_ref(l) - left_target_x))
    right_side = min(right_lines, key=lambda l: abs(x_at_ref(l) - right_target_x))

    def line_eq(l):
        x1, y1, x2, y2, _ = l
        dy, dx = float(y2 - y1), float(x2 - x1)
        return dy, -dx, dy * x1 - dx * y1

    def intersect(eq1, eq2):
        a1, b1, c1 = eq1
        a2, b2, c2 = eq2
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-9:
            return None
        return np.array([(c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det])

    TL = intersect(line_eq(far_baseline),  line_eq(left_side))
    TR = intersect(line_eq(far_baseline),  line_eq(right_side))
    BR = intersect(line_eq(near_baseline), line_eq(right_side))
    BL = intersect(line_eq(near_baseline), line_eq(left_side))
    if any(p is None for p in (TL, TR, BR, BL)):
        print("  Line refinement: line intersection failed, keeping green-mask corners")
        return approx_corners, False

    refined = _sort_corners(np.array([TL, TR, BR, BL])).astype(np.float32)
    max_shift = max(np.linalg.norm(refined[i] - approx_corners[i]) for i in range(4))
    # Singles corners sit further inside the green-mask blob than doubles
    # corners by construction (they're a smaller nested rectangle), so they
    # need a looser bound here -- this just catches wild misdetections, the
    # SEP_MIN/MAX check above is what actually validates the singles inset.
    shift_limit = h * 0.30 if court_type == "singles" else h * 0.15
    if max_shift > shift_limit:
        print(f"  Line refinement rejected (shift {max_shift:.0f}px > "
              f"{shift_limit:.0f}px limit), keeping green-mask corners")
        return approx_corners, False

    print(f"  {court_type} boundary: "
          f"TL={refined[0].astype(int).tolist()} TR={refined[1].astype(int).tolist()} "
          f"BR={refined[2].astype(int).tolist()} BL={refined[3].astype(int).tolist()}")
    return refined, True


def _pick_reference_frame(video_path, wide_search, search_step_sec, search_start_frame,
                          court_type='singles', verify_stable=True):
    """
    (corners, ref_frame) for the frame corners should be detected on.

    wide_search=False (default): extract_features.auto_detect_court's own
    5-candidate search in the first ~8s -- fast, correct for a pre-trimmed
    rally-only clip that starts right at court footage.

    wide_search=True: frame_picker's cheap midpoint-first, centered/margin-
    scored search (see run_full_pipeline.py --broadcast) -- a fixed early
    frame is usually still intro/graphics on a full broadcast, and this is
    the same picker annotate_court.py's --auto_frame uses, so both
    annotation paths agree on what "a good reference frame" means. Bounded
    cost (at most ~21 frame reads) rather than scanning the whole video.
    """
    if not wide_search:
        return auto_detect_court(video_path)

    import cv2
    ranked = pick_frame_fast(video_path, step_sec=search_step_sec,
                             start_frame=search_start_frame or None,
                             court_type=court_type, verify_stable=verify_stable)
    best_frame_no = ranked[0][0]
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, best_frame_no)
    ok, ref_frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Cannot read frame {best_frame_no} from {video_path}")
    frame_area = ref_frame.shape[0] * ref_frame.shape[1]
    corners, _area = _try_detect_corners(ref_frame, frame_area)
    if corners is None:
        raise RuntimeError(f"Frame {best_frame_no} scored well but corner "
                           f"detection failed on re-read -- try --court_mode manual")
    return corners, ref_frame, best_frame_no


def detect(video_path, refine_net=True, court_type="singles",
          wide_search=False, search_step_sec=5.0, search_start_frame=None,
          verify_stable=True):
    corners, ref_frame, frame_no = _pick_reference_frame(video_path, wide_search,
                                               search_step_sec, search_start_frame,
                                               court_type, verify_stable)
    corners, line_matched = refine_corners_court_type(ref_frame, corners, court_type)
    TL, TR, BR, BL = corners

    # compute_net() reads the module-level COURT_WIDTH global at call time --
    # patch it to the right court width before calling so the homography
    # (and therefore net_Y) is computed for the correct court, not always
    # extract_features.py's own doubles-width default.
    ef.COURT_WIDTH = SINGLES_WIDTH_M if court_type == "singles" else DOUBLES_WIDTH_M
    net_Y, net_left_px, net_right_px, H, H_inv = ef.compute_net(corners)
    if refine_net:
        net_Y = snap_net(ref_frame, net_Y, corners)

    net_top_Y = float((TL[1] + TR[1]) / 2)
    h, w = ref_frame.shape[:2]

    return {
        # court_utils.py (player_detection.py's loader) requires frame_size
        # to rescale corners -- include it so this file works as --court_file
        # there too, not just for win_predictor.
        "frame_size": {"width": int(w), "height": int(h)},
        "frame_no": int(frame_no) if frame_no is not None else None,
        "court_type": court_type,
        # False means the singles/doubles sideline could not be confidently
        # distinguished and corners fell back to the cruder green-mask blob
        # -- treat this file as low-confidence and prefer manual annotation.
        "court_type_matched": line_matched,
        "corners": {
            "TL": [float(TL[0]), float(TL[1])],
            "TR": [float(TR[0]), float(TR[1])],
            "BR": [float(BR[0]), float(BR[1])],
            "BL": [float(BL[0]), float(BL[1])],
        },
        "net": {
            "net_top_Y": net_top_Y,
            "net_Y": float(net_Y),
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True, help="Output court JSON path")
    ap.add_argument("--court_type", choices=["singles", "doubles"], default="singles",
                    help="Which sideline pair to snap to (default: singles)")
    ap.add_argument("--net_top_y", type=float, default=None,
                    help="Override the auto-approximated net cable Y (pixels)")
    ap.add_argument("--no_snap", action="store_true",
                    help="Skip blue-net-post refinement of net_Y")
    ap.add_argument("--wide_search", action="store_true",
                    help="Search the whole video (centered/margin-scored, "
                         "see frame_picker.py) for the reference frame "
                         "instead of just the first ~8s. Use for full "
                         "broadcasts -- a fixed early frame is usually "
                         "still intro/graphics there.")
    ap.add_argument("--search_step_sec", type=float, default=5.0,
                    help="--wide_search candidate spacing in seconds (default 5.0)")
    ap.add_argument("--search_start_frame", type=int, default=None,
                    help="--wide_search tries this frame first instead of "
                         "the video midpoint")
    ap.add_argument("--no_preprocess", action="store_true",
                    help="Skip the automatic codec/resolution/fps check+fix "
                         "(video_utils.ensure_preprocessed)")
    ap.add_argument("--no_stability_check", action="store_true",
                    help="--wide_search: skip verifying the candidate reference "
                         "frame is part of a sustained (>=3s) consistent court "
                         "view before accepting it -- only the single-frame "
                         "area/center/margin score decides. Faster search, but "
                         "risks picking a transitional frame (e.g. mid camera-pan) "
                         "that isn't representative of the real rally angle.")
    args = ap.parse_args()

    if not args.no_preprocess:
        from video_utils import ensure_preprocessed
        args.video = str(ensure_preprocessed(args.video))

    data = detect(args.video, refine_net=not args.no_snap, court_type=args.court_type,
                  wide_search=args.wide_search, search_step_sec=args.search_step_sec,
                  search_start_frame=args.search_start_frame,
                  verify_stable=not args.no_stability_check)
    if args.net_top_y is not None:
        data["net"]["net_top_Y"] = args.net_top_y

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(data, f, indent=2)

    print(f"  corners: TL={data['corners']['TL']} TR={data['corners']['TR']} "
          f"BR={data['corners']['BR']} BL={data['corners']['BL']}")
    print(f"  net: net_top_Y={data['net']['net_top_Y']:.1f} "
          f"net_Y={data['net']['net_Y']:.1f}")
    print(f"  Saved -> {args.out}")
    if not data["court_type_matched"]:
        print(f"  *** WARNING: could not confirm {args.court_type} sideline -- "
              f"this court is the cruder green-mask approximation, not a "
              f"reliable {args.court_type} boundary. Re-run with "
              f"analysis/annotate_court.py for an accurate one. ***")


if __name__ == "__main__":
    main()
