"""
fill_gaps.py
------------
Post-process a TrackNet _ball.csv to fill in-rally occlusion gaps.

WHY InpaintNet fills post-rally positions (and why this is different):
  InpaintNet's generate_inpaint_mask only checks:
      y[before_gap] > threshold  AND  y[after_gap] > threshold
  But "shuttle in-court" is NOT the same as "rally is happening".
  After a rally ends, the shuttle is still physically in-court while
  being picked up or held for service → both anchors pass the check →
  InpaintNet incorrectly fills the between-rally gap.

This script adds two additional gates that InpaintNet lacks:

  GATE 1 — Scene mask:
      Both anchor frames must have both players visible (conf > threshold).
      During ball-pickup or service prep, typically one player is walking/
      crouching → scene_mask = 0 → gap is NOT filled.

  GATE 2 — Speed sanity:
      The average speed implied by interpolating anchor_before → anchor_after
      must be <= MAX_FILL_SPEED px/frame in original video coords.
      Two detections belonging to different rallies will be far apart →
      implied speed is physically impossible → gap is NOT filled.

Fill method: cubic spline (smooth arc) or linear fallback.
Only GAP frames are written. Anchor frames are never modified.

Usage:
        python3 TrackNetV3/fill_gaps.py \
            --input  shuttle_tracking/Test10_Full_ball_clean.csv \
            --output shuttle_tracking/Test10_Full_ball_filled.csv \
            --player_csv  Test10_Full_ball/player_detections.csv \
            --video_width 1280  --video_height 720
"""

import argparse
import numpy as np
import pandas as pd

try:
    from scipy.interpolate import CubicSpline
    USE_CUBIC = True
except ImportError:
    USE_CUBIC = False


# ---------------------------------------------------------------
# DEFAULT CONFIG
# ---------------------------------------------------------------

# Shuttle must be below this fraction of frame height.
# Set to 0.0 to disable — the scene mask + speed gates already prevent
# between-rally fills. A non-zero threshold incorrectly rejects anchors
# during high smashes/clears where the shuttle legitimately reaches Y≈5px.
Y_FRACTION_THRESHOLD = 0.0       # disabled

# Adaptive gap limits (frames).
# High smash: shuttle exits top of frame → TrackNet loses it for up to ~90 frames.
# Occlusion:  shuttle hidden mid-court   → short gaps only, keep it tight.
MAX_GAP_SMASH     = 90    # 3 s at 30 fps — high smash off top of frame
MAX_GAP_OCCLUSION = 25    # 0.83 s at 30 fps — regular occlusion (raised from 15 to fill 23-frame mid-court gaps)
# Y threshold (fraction of frame height) below which anchor is considered a smash.
# If anchor_before Y < video_height * SMASH_Y_FRACTION → treat as high smash.
SMASH_Y_FRACTION  = 0.20  # top 20% of frame

# After a high smash the shuttle exits the TOP of frame.
# When it re-enters it MUST come back from the top (small Y).
# Any Visibility=1 detection with Y >= video_height * SMASH_REENTRY_Y_FRACTION
# immediately after a smash exit is FAKE (player racket / body mid-frame while
# the real shuttle is still above the camera).  Those frames are zeroed out and
# the gap is extended to the real re-entry anchor.
SMASH_REENTRY_Y_FRACTION = 0.20  # re-entry must land in top 20% of frame

# Minimum gap length (frames) before the smash reentry pre-check fires.
# A shuttle above the frame for a real high smash takes ≥ 0.5 s = 15 frames.
# Shorter gaps mean the shuttle is still inside the frame (descending after
# a smash or near the top during a rally) — NOT a real smash exit.
# Firing on a 1-frame gap destroys real downstream trajectory.
SMASH_REENTRY_MIN_GAP = 15

# Maximum average speed (px/frame, original video coords) that
# a filled trajectory is allowed to have.
# A badminton shuttle at 300 km/h in a 1920px-wide frame at 30fps ≈ 130 px/frame.
# If two anchors imply a higher speed, they are from different rallies.
MAX_FILL_SPEED = 120.0           # px/frame

# YOLO player confidence threshold for scene mask
PLAYER_CONF_TH = 0.5

# Scene mask dilation for gap-filling anchor check.
# During a fast smash YOLO may drop one player for 1-5 frames; without dilation
# the anchor frame (last visible before the gap) fails the scene mask gate and
# the gap is not filled.  10 frames is conservative — inter-rally fills are
# still blocked by the speed gate (gate 4) and trajectory-quality gate (gate 5).
FILL_SCENE_DILATION = 10

# GATE 5 — anchor-before trajectory quality
# The shuttle must have been part of a MOVING trajectory before the gap.
# Blocks fills from:
#   (a) isolated single-frame detections (warmup noise, random blobs)
#   (b) stationary shuttle (lying on ground / held for service)
# Both cause false between-rally fills that the scene mask cannot catch.
TRAJ_WINDOW      = 5    # look at last N frames before gap
MIN_TRAJ_VISIBLE = 3    # need at least this many visible in that window.
                        # 6 was too strict: a smash approach has only 3-4 visible
                        # frames before the shuttle exits the top of frame.
                        # The avg-speed check below still rejects stationary shuttles.
MIN_ANCHOR_SPEED = 2.0  # px/frame — stationary shuttle ≈ 0, slow rally ≈ 3-5

# GATE 5B — anchor_after resume speed (non-smash only).
# After the gap, the first visible frame following anchor_after must show
# meaningful shuttle motion.  If the speed is < MIN_RESUME_SPEED the gap is
# between two slow/stationary clusters (between-rally period) and must NOT
# be filled.  Real mid-rally occlusions always resume at > 5 px/frame.
# Example: between-rally gap resume = 2 px/frame → blocked.
#          real lob gap resume = 45 px/frame → allowed.
MIN_RESUME_SPEED = 5.0  # px/frame — min speed of first visible frame after gap


# ---------------------------------------------------------------
# SCENE MASK — require both players present at anchor frames
# ---------------------------------------------------------------
def _dilate_mask(mask: np.ndarray, dilation: int) -> np.ndarray:
    """Fill gaps <= dilation frames wide that have mask=1 on BOTH sides."""
    dilated = mask.copy()
    n = len(mask)
    i = 0
    while i < n:
        if mask[i]:
            i += 1
            continue
        gap_start = i
        j = i
        while j < n and not mask[j]:
            j += 1
        gap_end = j
        gap_len = gap_end - gap_start
        has_before = gap_start > 0 and mask[gap_start - 1]
        has_after  = gap_end < n  and mask[gap_end]
        if has_before and has_after and gap_len <= dilation:
            dilated[gap_start:gap_end] = True
        i = gap_end if gap_end > i else i + 1
    return dilated


def build_scene_mask(player_csv: str, total_frames: int, player_conf_th: float = PLAYER_CONF_TH) -> np.ndarray:
    """
    Returns a boolean array of length total_frames.
    mask[f] = True  iff both player_1 and player_2 are detected
              with confidence > player_conf_th at frame f.
    """
    mask = np.zeros(total_frames, dtype=bool)
    if not player_csv:
        # No player CSV supplied -- disable scene-mask gate
        mask[:] = True
        return mask

    try:
        df = pd.read_csv(player_csv)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        print(f"Warning: player_csv '{player_csv}' is empty or missing — scene-mask gate disabled.")
        mask[:] = True
        return mask

    # find frame column
    fc = next((c for c in ["Frame", "frame_no", "frame", "index"] if c in df.columns), None)
    if fc is None:
        mask[:] = True
        return mask

    for _, row in df.iterrows():
        f = int(row[fc])
        if f >= total_frames:
            continue
        p1 = (not pd.isna(row.get("player_1_x"))) and row.get("player_1_conf", 0) > player_conf_th
        p2 = (not pd.isna(row.get("player_2_x"))) and row.get("player_2_conf", 0) > player_conf_th
        if p1 and p2:
            mask[f] = True

    if FILL_SCENE_DILATION > 0:
        mask = _dilate_mask(mask, FILL_SCENE_DILATION)

    return mask


# ---------------------------------------------------------------
# CORE GAP-FILLING
# ---------------------------------------------------------------
def fill_gaps(
    df: pd.DataFrame,
    video_height: int,
    video_width: int,
    scene_mask: np.ndarray,
    max_gap_smash: int = MAX_GAP_SMASH,
    max_gap_occlusion: int = MAX_GAP_OCCLUSION,
    smash_y_fraction: float = SMASH_Y_FRACTION,
    smash_reentry_y_fraction: float = SMASH_REENTRY_Y_FRACTION,
    smash_reentry_min_gap: int = SMASH_REENTRY_MIN_GAP,
    max_fill_speed: float = MAX_FILL_SPEED,
    y_fraction_threshold: float = Y_FRACTION_THRESHOLD,
) -> pd.DataFrame:
    """
    Fill occlusion gaps in the shuttle trajectory.

    Gap limit is adaptive:
      - anchor_before Y < video_height * smash_y_fraction → high smash → max_gap_smash
      - otherwise → occlusion → max_gap_occlusion

    A gap is filled ONLY when ALL conditions hold:
      1. Both anchors have Visibility = 1
      2. Both anchor Y values are in-court   (Y > y_threshold)
      3. Both anchor frames have scene_mask = True  (both players visible)
      4. Gap length <= adaptive limit (smash or occlusion)
      5. Implied average speed <= max_fill_speed
    """
    y_threshold = video_height * y_fraction_threshold

    # Collapse multiple predictions per frame into one.
    # TrackNetV3 sliding window produces N predictions per frame.
    # Sort so Visibility=1 rows come first, then keep first → always
    # prefer a visible prediction over an invisible one for the same frame.
    df = df.sort_values(["Frame", "Visibility"], ascending=[True, False])
    df = df.drop_duplicates(subset="Frame", keep="first").reset_index(drop=True)

    df = df.sort_values("Frame").reset_index(drop=True)
    frames = df["Frame"].values.astype(int)
    x   = df["X"].values.astype(float)
    y   = df["Y"].values.astype(float)
    vis = df["Visibility"].values.copy()

    filled_count = 0

    i = 0
    while i < len(vis):
        # skip visible frames
        if vis[i] == 1:
            i += 1
            continue

        # --- found start of a gap ---
        gap_start = i
        j = i
        while j < len(vis) and vis[j] == 0:
            j += 1
        gap_end = j          # index of first visible frame after gap
        gap_len = gap_end - gap_start

        anchor_before = gap_start - 1
        anchor_after  = gap_end

        # -------------------------------------------------------
        # GATE 0: anchors must exist
        # -------------------------------------------------------
        anchors_exist = (anchor_before >= 0) and (anchor_after < len(vis))

        if anchors_exist:
            # -----------------------------------------------------------
            # SMASH REENTRY PRE-CHECK  (must run before fb/fa are set)
            #
            # After a high smash the shuttle exits the top of frame and
            # can only re-enter from the top (small Y).  Any Visibility=1
            # detection with large Y immediately after the gap is FAKE —
            # typically the hitter's racket head or body while the real
            # shuttle is still above the camera.
            #
            # We scan forward, zero every such fake detection, and extend
            # anchor_after to the first frame where Y < reentry_y.
            #
            # GUARD: fire when gap is long enough (≥ smash_reentry_min_gap),
            # OR when the implied speed to anchor_after exceeds max_fill_speed
            # (physically impossible for a real detection → it is a fake).
            # Pure gap-length guard was too conservative: a shuttle can exit
            # the top of frame after just 1 invisible frame yet still produce
            # a fake mid-frame detection (racket/body) at anchor_after.
            # Speed-based bypass catches exactly that case while leaving
            # short gaps with legitimate anchor_after positions untouched.
            # -----------------------------------------------------------
            _dist_aa = np.sqrt((x[anchor_after] - x[anchor_before]) ** 2
                               + (y[anchor_after] - y[anchor_before]) ** 2)
            _tg_aa   = frames[anchor_after] - frames[anchor_before]
            _speed_aa = _dist_aa / _tg_aa if _tg_aa > 0 else float('inf')

            # Serve-toss guard: if the cluster immediately before the
            # smash-zone anchor was stationary (server holding shuttle),
            # skip the reentry pre-check — the frames that follow are the
            # real rally, not fake post-smash blobs.
            _sc_start = anchor_before
            while _sc_start > 0 and vis[_sc_start - 1] == 1:
                _sc_start -= 1
            _prev_anch = next((j for j in range(_sc_start - 1, -1, -1) if vis[j] == 1), None)
            _is_serve_toss = False
            if _prev_anch is not None:
                _pcs = _prev_anch
                while _pcs > 0 and vis[_pcs - 1] == 1:
                    _pcs -= 1
                _win = max(_pcs, _prev_anch - 7)
                _spd_list = []
                for _m in range(_win, _prev_anch):
                    if vis[_m] == 1 and vis[_m + 1] == 1:
                        _dt = max(int(frames[_m + 1]) - int(frames[_m]), 1)
                        _spd_list.append(
                            float(np.sqrt((x[_m+1]-x[_m])**2 + (y[_m+1]-y[_m])**2)) / _dt
                        )
                if _spd_list and float(np.mean(_spd_list)) < 5.0:
                    _is_serve_toss = True

            if (not _is_serve_toss
                    and y[anchor_before] < video_height * smash_y_fraction
                    and (gap_len >= smash_reentry_min_gap
                         or _speed_aa > max_fill_speed)):
                reentry_y = video_height * smash_reentry_y_fraction
                if anchor_after < len(vis) and y[anchor_after] >= reentry_y:
                    scan = anchor_after
                    real_reentry = -1
                    while scan < len(vis) and (scan - gap_start) <= max_gap_smash:
                        if vis[scan] == 1:
                            if y[scan] < reentry_y:
                                real_reentry = scan
                                break
                            else:
                                x[scan] = 0.0
                                y[scan] = 0.0
                                vis[scan] = 0
                        scan += 1
                    if real_reentry >= 0:
                        gap_end      = real_reentry
                        anchor_after = real_reentry
                        gap_len      = gap_end - gap_start

            fb = frames[anchor_before]
            fa = frames[anchor_after]

            # -------------------------------------------------------
            # GATE 3: gap short enough (adaptive: smash vs occlusion)
            # Computed first so is_smash is available for GATE 2 below.
            #
            # is_smash is True when the shuttle was exiting the top of
            # frame — either already in the top-20% zone, OR moving
            # upward fast (clear/smash exit where the last visible frame
            # happens to be just above the 20% line).
            # Using only Y position missed cases where the anchor sits at
            # Y=22-30% while still moving upward at 20+ px/frame, causing
            # those gaps to be capped at max_gap_occlusion (25 frames)
            # instead of max_gap_smash (90 frames) → rally split.
            # -------------------------------------------------------
            _is_upward_fast = False
            if anchor_before >= 1 and vis[anchor_before - 1] == 1:
                _dy = y[anchor_before] - y[anchor_before - 1]  # negative = moving up
                _dx = x[anchor_before] - x[anchor_before - 1]
                _spd_local = float(np.sqrt(_dx ** 2 + _dy ** 2))
                # dy < -8: shuttle moved up ≥8px in one frame (catches gentle clears too)
                # spd_local > 8: not a jitter — genuinely fast upward motion
                _is_upward_fast = (_dy < -8) and (_spd_local > 8)

            is_smash = (y[anchor_before] < video_height * smash_y_fraction) or _is_upward_fast
            limit = max_gap_smash if is_smash else max_gap_occlusion
            short_enough = gap_len <= limit

            # -------------------------------------------------------
            # GATE 1: both anchors visible and in-court (Y check)
            # -------------------------------------------------------
            in_court = (
                vis[anchor_before] == 1
                and y[anchor_before] > y_threshold
                and vis[anchor_after] == 1
                and y[anchor_after] > y_threshold
            )

            # -------------------------------------------------------
            # GATE 2: scene mask — both players must be visible.
            # Smash exception: the hitter is mid-jump at anchor_before
            # so YOLO often misses them; we skip the before-check for
            # smash gaps (the receiver still must pass at anchor_after).
            # -------------------------------------------------------
            sm_len = len(scene_mask)
            after_scene_ok  = fa < sm_len and scene_mask[fa]
            before_scene_ok = fb < sm_len and scene_mask[fb]
            scene_ok = after_scene_ok and (before_scene_ok or is_smash)

            # -------------------------------------------------------
            # GATE 4: speed sanity
            #   distance between anchors / time between them
            # -------------------------------------------------------
            dist = np.sqrt((x[anchor_after] - x[anchor_before])**2
                           + (y[anchor_after] - y[anchor_before])**2)
            time_gap = fa - fb   # frame count (includes the gap)
            implied_speed = dist / time_gap if time_gap > 0 else float('inf')
            speed_ok = implied_speed <= max_fill_speed

            # -------------------------------------------------------
            # GATE 5: anchor-before must be part of a moving trajectory
            # Check the last TRAJ_WINDOW frames before the gap.
            # Blocks fills from isolated detections and stationary shuttle.
            #
            # SMASH-START RELAXATION (Change D):
            # When a rally starts with a high smash, the shuttle is only
            # visible for 1-2 frames near the top of the frame before going
            # above the camera entirely.  There is no multi-frame trajectory
            # to measure before the gap — the anchor is an isolated flash at
            # low Y (smash apex).  The other gates (scene mask, speed, smash Y)
            # already protect against false fills, so we allow a single-frame
            # smash anchor.  Require only 1 visible frame when is_smash=True.
            # -------------------------------------------------------
            look_back  = max(0, anchor_before - TRAJ_WINDOW)
            recent_vis = [t for t in range(look_back, anchor_before + 1) if vis[t] == 1]
            min_vis_gate5 = 1 if is_smash else MIN_TRAJ_VISIBLE
            if len(recent_vis) < min_vis_gate5:
                anchor_active = False   # isolated non-smash detection — block
            elif len(recent_vis) == 1:
                anchor_active = True    # isolated smash flash — allow (other gates protect)
            else:
                pre_speeds = [
                    np.sqrt((x[recent_vis[k]] - x[recent_vis[k-1]])**2
                            + (y[recent_vis[k]] - y[recent_vis[k-1]])**2)
                    for k in range(1, len(recent_vis))
                ]
                anchor_active = (len(pre_speeds) > 0 and
                                 np.mean(pre_speeds) > MIN_ANCHOR_SPEED)

            # -------------------------------------------------------
            # GATE 5B: anchor_after resume speed (non-smash only).
            # The first visible frame AFTER anchor_after must move at
            # >= MIN_RESUME_SPEED.  Blocks between-rally fills where the
            # "next cluster" is a slow/stationary between-rally detection.
            # Skipped for smash gaps: smash reentry is already protected
            # by the smash reentry pre-check above.
            # -------------------------------------------------------
            resume_ok = True
            if not is_smash and anchor_active:
                _look = range(anchor_after + 1,
                              min(anchor_after + TRAJ_WINDOW + 1, len(vis)))
                _nv = next((k for k in _look if vis[k] == 1), None)
                if _nv is not None:
                    _dt = max(int(frames[_nv]) - int(frames[anchor_after]), 1)
                    _spd = (np.sqrt((x[_nv] - x[anchor_after]) ** 2 +
                                    (y[_nv] - y[anchor_after]) ** 2) / _dt)
                    if _spd < MIN_RESUME_SPEED:
                        resume_ok = False

            if in_court and scene_ok and short_enough and speed_ok and anchor_active and resume_ok:
                _interpolate(x, y, vis, anchor_before, gap_start, gap_end, anchor_after)
                # If the cubic spline overshot frame bounds (wild anchor context
                # from a fast smash forces the spline through Y<0 or Y>=height),
                # retry with linear interpolation before giving up entirely.
                out_of_bounds = any(
                    x[k] < 0 or x[k] >= video_width or
                    y[k] < 0 or y[k] >= video_height
                    for k in range(gap_start, gap_end)
                )
                if out_of_bounds:
                    # Reset and retry with linear
                    for k in range(gap_start, gap_end):
                        x[k] = 0.0; y[k] = 0.0; vis[k] = 0
                    _interpolate_linear(x, y, vis, anchor_before, gap_start, gap_end, anchor_after)
                    out_of_bounds = any(
                        x[k] < 0 or x[k] >= video_width or
                        y[k] < 0 or y[k] >= video_height
                        for k in range(gap_start, gap_end)
                    )
                    if out_of_bounds:
                        for k in range(gap_start, gap_end):
                            x[k] = 0.0; y[k] = 0.0; vis[k] = 0
                    else:
                        filled_count += gap_len
                else:
                    filled_count += gap_len

        i = gap_end if gap_end > i else i + 1

    print(f"  Gaps evaluated | filled frames: {filled_count}")

    df = df.copy()
    df["X"]          = np.round(x).astype(int)
    df["Y"]          = np.round(y).astype(int)
    df["Visibility"] = vis
    return df


def _interpolate(x, y, vis, before, gap_start, gap_end, after):
    """Cubic spline if possible, otherwise linear."""
    gap_len = gap_end - gap_start

    if USE_CUBIC and gap_len >= 3:
        # Use a small context window for a smoother curve
        left  = max(0, before - 2)
        right = min(len(vis) - 1, after + 2)
        known_t = [t for t in range(left, right + 1) if vis[t] == 1]

        if len(known_t) >= 4:
            kx = [x[t] for t in known_t]
            ky = [y[t] for t in known_t]
            cs_x = CubicSpline(known_t, kx)
            cs_y = CubicSpline(known_t, ky)
            for k in range(gap_start, gap_end):
                x[k]   = float(cs_x(k))
                y[k]   = float(cs_y(k))
                vis[k] = 1
            return

    # fallback: linear
    _interpolate_linear(x, y, vis, before, gap_start, gap_end, after)


def _interpolate_linear(x, y, vis, before, gap_start, gap_end, after):
    """Pure linear interpolation between two anchor frames."""
    x0, y0 = x[before], y[before]
    x1, y1 = x[after],  y[after]
    for k in range(gap_start, gap_end):
        t      = (k - before) / (after - before)
        x[k]   = x0 + t * (x1 - x0)
        y[k]   = y0 + t * (y1 - y0)
        vis[k] = 1


# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",        required=True,
                        help="Path to _ball.csv from TrackNet predict.py")
    parser.add_argument("--output",       required=True,
                        help="Path to save the gap-filled CSV")
    parser.add_argument("--player_csv",   default="",
                        help="Path to player_detections.csv (enables scene-mask gate)")
    parser.add_argument("--video_width",  type=int, default=1920)
    parser.add_argument("--video_height", type=int, default=1080)
    parser.add_argument("--max_gap_smash",     type=int,   default=MAX_GAP_SMASH,
                        help="Max gap frames for high-smash (default 90 = 3s at 30fps)")
    parser.add_argument("--max_gap_occlusion", type=int,   default=MAX_GAP_OCCLUSION,
                        help="Max gap frames for occlusion (default 15 = 0.5s at 30fps)")
    parser.add_argument("--smash_y_fraction",  type=float, default=SMASH_Y_FRACTION,
                        help="Top Y fraction of frame treated as smash zone (default 0.20)")
    parser.add_argument("--smash_reentry_fraction", type=float, default=SMASH_REENTRY_Y_FRACTION,
                        help="After smash exit, anchor_after Y must be below height*this; "
                             "higher Y = fake detection, zeroed out (default 0.20)")
    parser.add_argument("--smash_reentry_min_gap", type=int, default=SMASH_REENTRY_MIN_GAP,
                        help="Min gap frames before smash reentry pre-check fires (default 15)")
    parser.add_argument("--max_speed",    type=float, default=MAX_FILL_SPEED,
                        help="Max implied speed in px/frame (default 120)")
    parser.add_argument("--y_fraction",   type=float, default=Y_FRACTION_THRESHOLD,
                        help="Top fraction of frame = out-of-court zone (default 0.10)")
    parser.add_argument("--player_conf",  type=float, default=PLAYER_CONF_TH)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    total_frames = int(df["Frame"].max()) + 1
    print(f"Loaded {len(df)} rows | max frame: {total_frames - 1}")
    print(f"Before -- visible frames: {int(df['Visibility'].sum())}")

    scene_mask = build_scene_mask(args.player_csv, total_frames, player_conf_th=args.player_conf)
    print(f"Scene mask: {scene_mask.sum()} / {total_frames} frames have both players")

    df_filled = fill_gaps(
        df,
        video_height=args.video_height,
        video_width=args.video_width,
        scene_mask=scene_mask,
        max_gap_smash=args.max_gap_smash,
        max_gap_occlusion=args.max_gap_occlusion,
        smash_y_fraction=args.smash_y_fraction,
        smash_reentry_y_fraction=args.smash_reentry_fraction,
        smash_reentry_min_gap=args.smash_reentry_min_gap,
        max_fill_speed=args.max_speed,
        y_fraction_threshold=args.y_fraction,
    )

    after_vis = int(df_filled["Visibility"].sum())
    print(f"After  — visible frames: {after_vis}")
    print(f"Net gain: +{after_vis - int(df['Visibility'].sum())} frames filled")

    df_filled.to_csv(args.output, index=False)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()