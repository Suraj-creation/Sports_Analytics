"""
court_presence.py
------------------
Per-frame signal: is the main broadcast camera angle on screen right now?

Motivation: a broadcast match video is not one continuous rally-camera shot
-- it's intro graphics, player walk-ins, crowd cutaways, coach shots, and
replays, interleaved with the actual constant-angle rally footage. Every
downstream stage (court/net annotation, shuttle detection, rally
segmentation) implicitly assumes "the main camera angle," so knowing WHEN
that angle is on screen is a useful independent gate -- much more directly
than inferring it from shuttle speed or player counts alone.

Two-stage check, cheap-first:
  1. Green-fraction gate: does the region INSIDE the reference court polygon
     still look like a green court in this frame? Cheap (one masked pixel
     count), and rejects most non-court frames (crowd, closeups, graphics)
     immediately -- but NOT specific enough alone: a frame that's on a
     different-but-still-green shot (zoomed in, a different camera angle
     that happens to fill that same screen region with green, a different
     green surface entirely) can pass this even though the court is NOT
     actually in the same place. Verified against real segment output --
     this alone let through frames where the court was only partially
     visible, or not really there at all.
  2. Homography verification (only for frames that pass stage 1, so the
     expensive part only runs on the minority of candidates): detect this
     frame's OWN court corners (same green-blob contour detection
     extract_features.py's auto court detector uses), then reproject them
     through the REFERENCE frame's image-to-real-world-court homography.
     If the camera angle genuinely hasn't moved, those corners land right
     back on the real court rectangle (0,0)-(W,0)-(W,L)-(0,L); if it's a
     different framing, they land somewhere else in real-world space --
     directly, physically measurable in metres, not a pixel heuristic.

Usage:
    python analysis/court_presence.py \\
        --video YourMatch/YourMatch.mp4 \\
        --court_json YourMatch/YourMatch_court.json \\
        --out YourMatch/YourMatch_court_presence.csv

    # Then gate detect_rallies.py with it:
    python analysis/detect_rallies.py --match_folder YourMatch \\
        --court_mask_csv YourMatch/YourMatch_court_presence.csv
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np
import pandas as pd

HSV_LOWER_GREEN = np.array([30, 35, 35])
HSV_UPPER_GREEN = np.array([90, 255, 255])

SINGLES_WIDTH_M = 5.18
DOUBLES_WIDTH_M = 6.1
COURT_LENGTH_M  = 13.4


def load_court(court_json_path):
    with open(court_json_path) as f:
        data = json.load(f)
    c = data["corners"]
    if isinstance(c, dict):
        pts = np.array([c["TL"], c["TR"], c["BR"], c["BL"]], dtype=np.float32)
    else:
        pts = np.array(c, dtype=np.float32)
    court_type = data.get("court_type", "singles")
    return pts, court_type


def reference_homography(ref_corners, court_type):
    """Image-space TL/TR/BR/BL -> real-world court rectangle (metres),
    same convention as extract_features.compute_net / auto_court.py."""
    width = SINGLES_WIDTH_M if court_type == "singles" else DOUBLES_WIDTH_M
    real_rect = np.float32([[0, 0], [width, 0], [width, COURT_LENGTH_M], [0, COURT_LENGTH_M]])
    H, _ = cv2.findHomography(ref_corners, real_rect)
    return H, real_rect


def self_calibrated_reference(video_path, court_json_path, ref_corners, court_type,
                              try_detect_corners):
    """
    Build H_ref from the reference frame's OWN raw-blob-detected corners
    instead of the precisely clicked/auto-refined ones in the court JSON.

    Why: geometric_reproj_error_m() detects candidate frames' corners with
    the cheap raw green-blob contour detector (extract_features's
    _try_detect_corners), which is a systematically looser/wider box than
    a precisely clicked court boundary -- comparing it against the precise
    reference corners made the reference frame look ~1.5m "off" from
    itself. Detecting the reference frame with that SAME raw detector and
    calibrating H_ref against THAT cancels the bias out, so error becomes
    genuinely about camera position, not detector precision.

    Needs the JSON's "frame_no" (saved by annotate_court.py's manual tool;
    auto_court.py's output also now includes it) to know which frame in
    video_path to re-detect. Falls back to the JSON's own corners (with a
    printed warning) if frame_no is missing or that frame can't be read --
    matches the old, less-calibrated behaviour rather than failing.
    """
    with open(court_json_path) as f:
        data = json.load(f)
    frame_no = data.get("frame_no")
    if frame_no is None:
        print("  (court JSON has no frame_no -- skipping self-calibration, "
              "using annotated corners directly as the homography reference. "
              "May over-reject genuine same-position frames.)")
        return reference_homography(ref_corners, court_type)

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
    ok, ref_frame = cap.read()
    cap.release()
    if not ok:
        print(f"  (could not read reference frame {frame_no} from {video_path} "
              f"for self-calibration -- using annotated corners directly.)")
        return reference_homography(ref_corners, court_type)

    frame_area = ref_frame.shape[0] * ref_frame.shape[1]
    blob_corners, _area = try_detect_corners(ref_frame, frame_area)
    if blob_corners is None:
        print(f"  (raw court detector found nothing on reference frame "
              f"{frame_no} -- using annotated corners directly.)")
        return reference_homography(ref_corners, court_type)

    H, real_rect = reference_homography(blob_corners.astype(np.float32), court_type)
    print(f"  Self-calibrated homography reference from frame {frame_no}'s "
          f"own raw court detection (matches the detector candidate frames "
          f"get checked with).")
    return H, real_rect


def green_fraction(frame_bgr, mask):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    green = cv2.inRange(hsv, HSV_LOWER_GREEN, HSV_UPPER_GREEN)
    inside = cv2.bitwise_and(green, mask)
    denom = int(np.count_nonzero(mask))
    if denom == 0:
        return 0.0
    return float(np.count_nonzero(inside)) / denom


def geometric_reproj_error_m(frame_bgr, H_ref, real_rect, frame_area, try_detect_corners):
    """
    Detect this frame's own court corners (same green-blob contour detector
    used to calibrate H_ref -- see reference_homography_self_calibrated())
    and reproject them through the reference homography. Returns mean
    distance (metres) from where they land to the real court rectangle --
    near 0 if this frame's court is genuinely the same court in the same
    position as the reference frame, large otherwise (different
    angle/zoom/camera/surface). None if no plausible court blob was found
    in this frame at all (treated the same as "large error" by the caller).

    Deliberately uses the SAME raw blob detector on both sides (reference
    and candidate) rather than trying to match a precisely hand-clicked
    reference against an auto-detected candidate. Tried that first: it
    produced ~1.5m of "error" between the reference frame and ITSELF,
    because the raw green-blob detector is a looser, systematically wider
    box than precisely clicked/line-refined corners -- and the line
    refiner (auto_court.refine_corners_court_type) isn't reliable enough
    to close that gap on demand (it falls back to the raw blob whenever it
    can't confidently tell singles from doubles lines, which is common).
    Comparing raw-to-raw on both sides cancels that systematic bias out.
    """
    corners, area = try_detect_corners(frame_bgr, frame_area)
    if corners is None:
        return None
    pts = corners.reshape(-1, 1, 2).astype(np.float32)
    mapped = cv2.perspectiveTransform(pts, H_ref).reshape(-1, 2)
    return float(np.mean(np.linalg.norm(mapped - real_rect, axis=1)))


def compute_presence(video_path, court_json_path, stride=30, threshold=0.55,
                     smooth_window=5, max_reproj_error_m=0.6):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from extract_features import _try_detect_corners

    ref_corners, court_type = load_court(court_json_path)
    H_ref, real_rect = self_calibrated_reference(video_path, court_json_path,
                                                  ref_corners, court_type,
                                                  _try_detect_corners)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_area = w * h

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [ref_corners.astype(np.int32)], 255)

    frame_nos, fracs, reproj_errs = [], [], []
    frame_idx = 0
    n_gate_passed = 0
    print(f"  Scanning {total} frames (stride={stride}) for court presence "
         f"({court_type}, green-fraction gate + homography verification)...")
    while True:
        # Deliberately NOT cap.set()-seeking to frame_idx: for a long-GOP
        # H.264 file, seeking to an arbitrary non-keyframe position forces
        # ffmpeg to decode forward from the last keyframe anyway (often
        # nearly as much work as just reading sequentially), plus repeated
        # seek overhead on top -- measured close to zero speedup from
        # stride=1 to stride=30 with .set(). Instead: grab() (decode only,
        # no BGR conversion -- cheap) through the frames we're skipping,
        # retrieve() (the conversion) only for the one frame per stride we
        # actually check. Exactly stride=1 frame-accurate, no keyframe
        # dependency, and the frames that matter cost the same as before.
        if not cap.grab():
            break
        if frame_idx % stride != 0:
            frame_idx += 1
            continue
        ret, frame = cap.retrieve()
        if not ret:
            break

        frac = green_fraction(frame, mask)
        err = None
        if frac >= threshold:
            # Only pay for corner detection + homography check on frames
            # that already look plausible -- most frames get rejected here
            # for free.
            n_gate_passed += 1
            err = geometric_reproj_error_m(frame, H_ref, real_rect, frame_area,
                                           _try_detect_corners)

        frame_nos.append(frame_idx)
        fracs.append(frac)
        reproj_errs.append(err if err is not None else np.nan)

        if frame_idx % 2000 < stride:
            print(f"    {frame_idx}/{total}")
        frame_idx += 1
    cap.release()
    print(f"  {n_gate_passed} frame(s) passed the green-fraction gate and "
         f"got homography-checked")

    df = pd.DataFrame({"frame_no": frame_nos, "green_frac": fracs,
                       "reproj_error_m": reproj_errs})

    # Fill to every frame if strided (nearest-previous value between samples)
    if stride > 1:
        full = pd.DataFrame({"frame_no": np.arange(total)})
        df = pd.merge_asof(full, df, on="frame_no", direction="backward")
        df["green_frac"] = df["green_frac"].fillna(method="bfill").fillna(0.0)
        df["reproj_error_m"] = df["reproj_error_m"].fillna(method="bfill")

    # A frame only counts as present if it passed BOTH the green-fraction
    # gate (frac >= threshold) AND the homography check found a court in
    # essentially the same real-world position (error <= max_reproj_error_m).
    # NaN reproj_error_m means it never got homography-checked (failed the
    # gate) -> not present.
    raw_present = ((df["green_frac"] >= threshold)
                   & df["reproj_error_m"].notna()
                   & (df["reproj_error_m"] <= max_reproj_error_m)).astype(int)

    # Median-smooth to avoid single-frame flicker (player fully covering the
    # polygon for a moment, motion blur on a smash, one bad corner detection)
    # flipping the signal.
    if smooth_window > 1:
        df["court_present"] = (
            raw_present.rolling(smooth_window, center=True, min_periods=1)
            .median().round().astype(int)
        )
    else:
        df["court_present"] = raw_present

    return df


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--court_json", required=True,
                    help="Reference court corners (+ optional court_type) for "
                         "the main broadcast angle (from annotate_court.py or "
                         "auto_court.py)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--stride", type=int, default=30,
                    help="Check every Nth frame instead of every frame (faster; "
                         "gaps are filled with the nearest earlier sample). "
                         "Default 30 (~1 sample/second at 30fps) -- checking "
                         "every single frame is far more precision than the "
                         "presence signal needs and multiplies runtime for "
                         "no benefit; extract_segments.py's padding already "
                         "covers the up-to-1-sample-interval fill lag this "
                         "introduces at rally boundaries. Use 1 to check "
                         "every frame.")
    ap.add_argument("--threshold", type=float, default=0.55,
                    help="Stage-1 gate: min fraction of the court polygon that "
                         "must be green (default 0.55 -- players/shuttle/lines "
                         "cover the rest, so this isn't near 1.0 even on-camera)")
    ap.add_argument("--max_reproj_error_m", type=float, default=0.6,
                    help="Stage-2 gate: max allowed mean corner error, in "
                         "real-world metres, between this frame's detected "
                         "court and the reference court's position after "
                         "homography reprojection (default 0.6m)")
    ap.add_argument("--smooth_window", type=int, default=5,
                    help="Median filter window (frames) to remove flicker")
    ap.add_argument("--no_preprocess", action="store_true",
                    help="Skip the automatic codec/resolution/fps check+fix "
                         "(video_utils.ensure_preprocessed) -- a no-op if the "
                         "video already matches, so safe to leave on even "
                         "when called from run_full_pipeline.py")
    args = ap.parse_args()

    if not args.no_preprocess:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from video_utils import ensure_preprocessed
        args.video = str(ensure_preprocessed(args.video))

    df = compute_presence(args.video, args.court_json, args.stride,
                          args.threshold, args.smooth_window,
                          args.max_reproj_error_m)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    df[["frame_no", "green_frac", "reproj_error_m", "court_present"]].to_csv(args.out, index=False)

    on_frac = df["court_present"].mean()
    changes = int((df["court_present"].diff().fillna(0) != 0).sum())
    print(f"  court_present=1 for {on_frac*100:.1f}% of frames "
          f"({changes} on/off transitions)")
    print(f"  Saved -> {args.out}")


if __name__ == "__main__":
    main()
