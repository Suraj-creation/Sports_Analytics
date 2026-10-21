"""
detect_rallies.py
-----------------
Segment badminton rallies from a (gap-filled) shuttle trajectory CSV.

PARAMETERS REMOVED vs old version:
  - TOP_Y_TH          (fill_gaps.py handles height-aware gap filling)
  - MAX_AIR_FRAMES    (removed with height split)
  - SHORT_GAP_FRAMES  (replaced by single END_GAP_FRAMES)
  - MAX_JUMP_DIST     (interpolation removed hard jumps)
  - MIN_RESTART_GAP   (removed -- scene mask dilation fixes the root cause)

WHY MIN_RESTART_GAP IS REMOVED:
  It was compensating for brief scene-mask dropouts: when YOLO missed a
  player for a moment, apply_scene_mask zeroed the shuttle data, which
  ended the rally early and started a new one seconds later.
  The fix is to dilate the scene mask by SCENE_MASK_DILATION frames so
  short detection gaps don't punch holes in valid rally data.
  With that fixed at the source, two separate detections close together
  are genuinely separate rallies -- no post-hoc merging needed.

RELATIONSHIP WITH fill_gaps.py:
  All 5 previously-split smash rallies (R7, R25, R30, R33, R42) are fixed
  entirely inside fill_gaps.py.  The updated fill_gaps now bridges the
  invisible gaps those smashes caused before this script ever runs.
  detect_rallies therefore never sees the invisible frames and never
  incorrectly splits the rally.

  ALL parameters in this file are unchanged from the previous version.
  The parameter comments are kept to explain the design intent.

PARAMETERS KEPT (minimal set):
  - START_SPEED            : minimum shuttle speed (px/frame) to start rally
  - MIN_START_VISIBLE      : consecutive fast frames needed to confirm start
  - END_GAP_FRAMES         : invisible frames that end a rally
  - SCENE_MASK_DILATION    : frames to bridge brief player-detection gaps
  - MIN_RALLY_DURATION_SEC : discard very short spurious detections
  - FPS                    : inferred from video
"""

import os
import argparse
import cv2
import pandas as pd
import numpy as np
from collections import deque

# ============================================================
# FILE PATHS -- defaults derived from --match_folder; override via CLI
# ============================================================
PLAYER_CSV  = None
SHUTTLE_CSV = None
VIDEO_FILE  = None
OUT_CSV     = None
# ============================================================
# PARAMETERS
# ============================================================
START_SPEED            = 3.0   # px/frame -- min shuttle speed to start rally
MIN_START_VISIBLE      = 3     # consecutive fast frames needed to confirm start
END_GAP_FRAMES         = 10    # invisible frames before rally is ended (~0.33s at 30fps)

# Lookahead: before confirming a rally end (gap or stationary), peek this many
# frames ahead. If the shuttle resumes fast movement within this window, the
# rally is NOT ended — avoids false splits without needing merge_close_rallies.
END_LOOKAHEAD_FRAMES   = 15    # frames (~0.5s at 30fps) to peek before ending
                               # NOTE: fill_gaps.py now fills smash gaps up to 90 frames
                               # so invisible bursts during smashes no longer reach this
                               # threshold.  Value intentionally unchanged.

SCENE_MASK_DILATION    = 100   # frames -- bridge player-detection gaps in scene mask.
                               # 45 was too small: high smashes cause YOLO to miss the
                               # jumping hitter for 50-90 frames.  With dilation=45 those
                               # gaps were NOT bridged → apply_scene_mask zeroed pre-smash
                               # shuttle data → rally appeared to start 2-3s late.
                               # 100 bridges all smash gaps (max 90 frames) safely.
                               # Between-rally periods: both players ARE detected (standing)
                               # so scene_mask=1 throughout → no false bridging.

MIN_RALLY_DURATION_SEC = 2.0   # drop spurious detections shorter than this.
                               # Shortest real GT rally = 4s. Setting to 2.0 removes
                               # 1-2s false positives (random blobs, shuttle toss)
                               # without affecting any genuine rally.
PLAYER_CONF_TH         = 0.5   # YOLO confidence threshold for player detection

# Rally merge: if a new rally starts within this many seconds of the previous
# rally ending, merge them into one.  Handles cases where brief 2D tracking
# dropouts (shuttle moves but TrackNet misses it) cause a single real rally to
# be split into two consecutive detections.
# Set to 0.0 to disable merging.
MERGE_GAP_SEC = 0.75   # seconds -- strict threshold to avoid cascade merges.
                       # fill_gaps bridges smash gaps up to 90 frames (3s).
                       # Any remaining splits have gaps of 1.0-1.5s; MERGE_GAP_SEC
                       # set to 0.5s safely bridges tracking flicker without merging rallies
                       # without merging genuinely separate rallies (inter-rally
                       # breaks are typically > 3s).

# Stationary-shuttle end condition:
# After a rally ends the shuttle lies still on the ground but remains visible.
# If it moves slower than STATIONARY_SPEED_TH for STATIONARY_END_FRAMES
# consecutive frames while visible -> treat as rally over.
STATIONARY_SPEED_TH    = 3.0   # px/frame -- shuttle on ground moves < this
STATIONARY_WINDOW      = 10   # look at last N visible frames for stationary check
STATIONARY_MIN_SLOW    = 7    # at least this many of STATIONARY_WINDOW must be slow
                               # N-of-M approach: robust to jitter where speed oscillates
                               # around 3.0 and resets a simple consecutive counter

# Only fire the stationary detector when shuttle Y > this value (pixels from top).
# A shuttle at Y < STATIONARY_MIN_Y is near the smash apex -- slow motion there
# is a filled interpolation artifact, NOT a stationary landing on the ground.
STATIONARY_MIN_Y      = 50    # pixels; ground-level shuttles are always Y > 200

# Pickup filtering parameters (Approach 1 & 4)
MIN_NOISE_TRAVEL_PX   = 15.0  # px -- minimum 2D travel distance to not be considered static noise
MAX_FEET_DIST_PX      = 40.0  # px -- if shuttle starts within this many pixels of feet, it's a floor pickup
MAX_PICKUP_X_TRAVEL   = 80.0  # px -- a pickup is mostly vertical, so horizontal travel should be small

# Retroactive lookback parameters
LOOKBACK_MAX_FRAMES    = 150    # never look back more than this many frames (~5 sec)
LOOKBACK_REST_CONF_TH  = 0.40   # confidence below this = between-rally / shuttle above frame
LOOKBACK_REST_MIN_LEN  = 5      # consecutive "rest" frames needed to call it a genuine gap


# ============================================================
# HELPERS
# ============================================================
def get_fps(video_file):
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps if fps > 0 else 30.0


def get_frame_col(df):
    for c in ["Frame", "frame_no", "frame", "index"]:
        if c in df.columns:
            return c
    raise ValueError("No frame column found in DataFrame")


def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


# ============================================================
# SCENE MASK -- both players detected, then dilated
# ============================================================
def generate_scene_mask(player_csv, video_file):
    df  = pd.read_csv(player_csv)
    fc  = get_frame_col(df)

    cap          = cv2.VideoCapture(video_file)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    mask = np.zeros(total_frames, dtype=np.int8)

    for _, row in df.iterrows():
        f = int(row[fc])
        if f >= total_frames:
            continue
        p1 = not pd.isna(row.get("player_1_x")) and row.get("player_1_conf", 0) > PLAYER_CONF_TH
        p2 = not pd.isna(row.get("player_2_x")) and row.get("player_2_conf", 0) > PLAYER_CONF_TH
        if p1 and p2:
            mask[f] = 1

    # Dilation: if a frame has mask=0 but is within SCENE_MASK_DILATION frames
    # of a mask=1 frame on BOTH sides, fill it in.
    # This bridges brief YOLO misses (player crouching, turning) without
    # extending the mask into genuine between-rally breaks.
    if SCENE_MASK_DILATION > 0:
        mask = _dilate_mask(mask, SCENE_MASK_DILATION)

    return mask


def _dilate_mask(mask, dilation):
    """
    Fill gaps in mask that are <= dilation frames wide AND
    have mask=1 on both sides (bilateral dilation).
    One-sided dilation at edges is not applied.
    """
    dilated = mask.copy()
    n = len(mask)
    i = 0
    while i < n:
        if mask[i] == 1:
            i += 1
            continue
        gap_start = i
        j = i
        while j < n and mask[j] == 0:
            j += 1
        gap_end = j
        gap_len = gap_end - gap_start

        has_before = gap_start > 0 and mask[gap_start - 1] == 1
        has_after  = gap_end < n   and mask[gap_end] == 1

        if has_before and has_after and gap_len <= dilation:
            dilated[gap_start:gap_end] = 1

        i = gap_end if gap_end > i else i + 1
    return dilated


def apply_scene_mask(shuttle_df, scene_mask):
    df = shuttle_df.copy()
    fc = get_frame_col(df)
    oob = df[fc].apply(lambda f: f >= len(scene_mask) or scene_mask[int(f)] == 0)
    df.loc[oob, ["X", "Y", "Visibility"]] = [0, 0, 0]
    return df


def load_court_mask(court_mask_csv, total_frames):
    """
    Load a per-frame court-presence mask from analysis/court_presence.py's
    output CSV, aligned to frame indices. Frames beyond the CSV's range
    default to 0 (not present) -- safer than assuming presence for footage
    that was never actually checked.
    """
    df = pd.read_csv(court_mask_csv)
    mask = np.zeros(total_frames, dtype=np.int8)
    valid = df[df["frame_no"] < total_frames]
    mask[valid["frame_no"].values.astype(int)] = valid["court_present"].values.astype(np.int8)
    return mask


# ============================================================
# RALLY SEGMENTATION -- simple state machine, no height split
# ============================================================
def segment_rallies(df):
    fc = get_frame_col(df)

    # Prefer visible predictions when multiple rows exist per frame (sliding window output)
    df     = df.sort_values([fc, "Visibility"], ascending=[True, False])
    df     = df.drop_duplicates(subset=fc, keep="first").reset_index(drop=True)
    speed  = np.sqrt(df["X"].diff() ** 2 + df["Y"].diff() ** 2).fillna(0).values
    vis    = df["Visibility"].values
    y_vals = df["Y"].values
    x_vals = df["X"].values.astype(float)
    frames = df[fc].values.astype(int)

    # Zero out speed at invisible->visible transitions.
    # diff() from (X=0,Y=0) to a real position gives a huge fake speed;
    # that is NOT shuttle movement and must not count toward rally start.
    for _i in range(1, len(vis)):
        if vis[_i] == 1 and vis[_i - 1] == 0:
            speed[_i] = 0.0
            
    # Change A: Duplicate-position guard (Fixes 0-speed tracking artifacts)
    last_real_spd = 0.0
    for _i in range(1, len(vis)):
        if vis[_i] == 1 and vis[_i - 1] == 1:
            if x_vals[_i] == x_vals[_i - 1] and y_vals[_i] == y_vals[_i - 1]:
                speed[_i] = last_real_spd   # carry forward
            else:
                last_real_spd = speed[_i]
        else:
            last_real_spd = 0.0

    rallies        = []
    active         = False
    start_f        = None
    gap_cnt        = 0
    fast_cnt       = 0
    slow_win       = deque(maxlen=STATIONARY_WINDOW)   # 1=slow, 0=fast, for last N visible frames
    slow_win_f     = deque(maxlen=STATIONARY_WINDOW)   # frame numbers for those visible frames

    for idx in range(len(df)):
        v = vis[idx]
        s = speed[idx]

        if not active:
            if v == 1 and s > START_SPEED:
                fast_cnt += 1
            else:
                fast_cnt = 0

            if fast_cnt >= MIN_START_VISIBLE:
                active   = True
                start_f  = frames[idx - MIN_START_VISIBLE + 1]
                gap_cnt  = 0
                fast_cnt = 0
                slow_win.clear()
                slow_win_f.clear()
        else:
            if v == 1:
                gap_cnt = 0
                is_slow = s < STATIONARY_SPEED_TH and y_vals[idx] > STATIONARY_MIN_Y
                slow_win.append(1 if is_slow else 0)
                slow_win_f.append(frames[idx])
            else:
                gap_cnt += 1

            end_by_gap        = gap_cnt >= END_GAP_FRAMES
            end_by_stationary = (len(slow_win) == STATIONARY_WINDOW and
                                  sum(slow_win) >= STATIONARY_MIN_SLOW)

            if end_by_gap or end_by_stationary:
                # ── LOOKAHEAD: peek END_LOOKAHEAD_FRAMES ahead ──────
                # If the shuttle resumes fast movement within the window,
                # the rally has not truly ended — reset and continue.
                peek_start = idx + 1
                peek_end   = min(idx + 1 + END_LOOKAHEAD_FRAMES, len(df))
                resumed    = any(
                    vis[pi] == 1 and speed[pi] > START_SPEED
                    for pi in range(peek_start, peek_end)
                )
                if resumed:
                    # Movement resumes — clear end condition and keep rally going
                    gap_cnt  = 0
                    slow_win.clear()
                    slow_win_f.clear()
                else:
                    # Confirmed end — no movement in lookahead window
                    if end_by_gap:
                        end_f = frames[idx - gap_cnt]
                    else:
                        end_f = slow_win_f[0]
                    if end_f > start_f:
                        rallies.append((start_f, end_f))
                    active   = False
                    gap_cnt  = 0
                    fast_cnt = 0
                    slow_win.clear()
                    slow_win_f.clear()

    if active:
        end_f = frames[-1]
        if end_f > start_f:
            rallies.append((start_f, end_f))

    return rallies


# ============================================================
# RALLY MERGE -- fuse consecutive rallies with a small gap
# ============================================================
def merge_close_rallies(rallies, shuttle_df, fps, merge_gap_sec=MERGE_GAP_SEC):
    """
    Merge consecutive rallies whose inter-rally gap is <= merge_gap_sec.

    WHY: 2D shuttle tracking sometimes loses the shuttle for a very brief
    window even while the rally is ongoing (fast net exchanges, shuttle near
    court boundary, lighting flicker).  That dropout ends the current rally
    and starts a fresh one a moment later, splitting a single real rally in
    two.  Merging by gap length is a lightweight fix that does not require
    re-running fill_gaps.

    The 5 previously-split smash rallies are now fixed at the fill_gaps level.
    This function acts as a residual safety net for any dropout that slips
    through fill_gaps (e.g. very brief net-exchange dropouts <= 1.0s).
    """
    if not rallies or merge_gap_sec <= 0.0:
        return rallies

    merge_gap_frames = merge_gap_sec * fps
    merged = [list(rallies[0])]
    fc = get_frame_col(shuttle_df)

    for start_f, end_f in rallies[1:]:
        prev_start = merged[-1][0]
        prev_end = merged[-1][1]
        gap = start_f - prev_end
        prev_dur = prev_end - prev_start
        
        # Smart merge for high smashes: Only bridge a large gap if the previous flash exited near the TOP of the frame
        prev_y = shuttle_df.loc[shuttle_df[fc] == prev_end, "Y"].values
        end_y = prev_y[0] if len(prev_y) > 0 else 1000
        is_smash_exit = (prev_dur <= 2.0 * fps) and (end_y < 250)
        
        if gap <= merge_gap_frames or (is_smash_exit and gap <= 4.0 * fps):
            merged[-1][1] = end_f
        else:
            merged.append([start_f, end_f])

    return [tuple(r) for r in merged]


# ============================================================
# RETROACTIVE LOOKBACK -- find true rally start
# ============================================================
def apply_lookback(rallies, shuttle_df):
    if not rallies:
        return rallies

    fc       = get_frame_col(shuttle_df)
    has_conf = "Confidence" in shuttle_df.columns

    df_s = (shuttle_df
            .sort_values(fc)
            .drop_duplicates(subset=fc)
            .reset_index(drop=True))

    frames_arr = df_s[fc].values.astype(int)
    vis_arr    = df_s["Visibility"].values.astype(int)
    conf_arr   = (df_s["Confidence"].values.astype(float)
                  if has_conf else None)

    frame_to_idx = {int(f): i for i, f in enumerate(frames_arr)}

    def is_rest(i):
        if vis_arr[i] != 0:
            return False
        if has_conf:
            return float(conf_arr[i]) < LOOKBACK_REST_CONF_TH
        return True

    new_rallies    = []
    prev_end_frame = -1

    for rally_start, rally_end in rallies:
        start_idx = frame_to_idx.get(rally_start)
        if start_idx is None:
            new_rallies.append((rally_start, rally_end))
            prev_end_frame = rally_end
            continue

        lower_frame = max(prev_end_frame + 1, rally_start - LOOKBACK_MAX_FRAMES)
        lower_idx   = frame_to_idx.get(lower_frame, 0)

        true_start_idx  = start_idx
        consec_rest     = 0
        rest_period_end = start_idx

        for back_i in range(start_idx - 1, lower_idx - 1, -1):
            if is_rest(back_i):
                consec_rest += 1
                if consec_rest == 1:
                    rest_period_end = back_i
                if consec_rest >= LOOKBACK_REST_MIN_LEN:
                    true_start_idx = rest_period_end + 1
                    break
            else:
                consec_rest = 0

        ts_scan = true_start_idx
        while ts_scan < start_idx and vis_arr[ts_scan] == 0:
            ts_scan += 1
        true_start_idx = ts_scan

        true_start_f = int(frames_arr[min(true_start_idx, len(frames_arr) - 1)])
        true_start_f = max(true_start_f, prev_end_frame + 1)

        new_rallies.append((true_start_f, rally_end))
        prev_end_frame = rally_end

    return new_rallies


# ============================================================
# PICKUP FILTERING -- Reject floor pickups and false tosses
# ============================================================
def filter_pickup_rallies(rallies, shuttle_df, player_csv, fps):
    """
    Filters out "shuttle pickup" false positives by checking:
      1. Approach 4: The shuttle must travel a minimum horizontal distance.
      2. Approach 1: The shuttle must not start near the player's feet.
    """
    try:
        player_df = pd.read_csv(player_csv)
        has_players = True
        fc = get_frame_col(player_df)
    except Exception as e:
        has_players = False
        print(f"  [Filter] Warning: Could not load player CSV for pickup filtering: {e}")

    valid_rallies = []
    
    for start_f, end_f in rallies:
        # Check window: First 1 second of the rally
        window_end = min(end_f, start_f + int(fps))
        window_df = shuttle_df[(shuttle_df[get_frame_col(shuttle_df)] >= start_f) & 
                               (shuttle_df[get_frame_col(shuttle_df)] <= window_end)]
        vis_window = window_df[window_df["Visibility"] == 1]
        
        if len(vis_window) > 0:
            # Approach 4: Pure Noise Check
            delta_x = vis_window["X"].max() - vis_window["X"].min()
            delta_y = vis_window["Y"].max() - vis_window["Y"].min()
            travel_2d = np.sqrt(delta_x**2 + delta_y**2)
            rally_dur = (end_f - start_f) / fps
            
            if travel_2d < MIN_NOISE_TRAVEL_PX and rally_dur < 4.0:
                print(f"  [Filter] Dropped rally {start_f}-{end_f}: Pure static noise ({travel_2d:.1f}px < {MIN_NOISE_TRAVEL_PX}px)")
                continue # Drop this rally
            
            # Approach 1: True Pickup Check (Near feet + Vertical lift)
            if has_players and rally_dur < 4.0: # A real pickup never lasts 4+ seconds
                s_frame = int(vis_window.iloc[0][get_frame_col(shuttle_df)])
                s_x, s_y = float(vis_window.iloc[0]["X"]), float(vis_window.iloc[0]["Y"])
                
                p_row = player_df[player_df[fc] == s_frame]
                if not p_row.empty:
                    p_row = p_row.iloc[0]
                    
                    # Find distance to both players to determine the nearest one (the server/pickup person)
                    dist1 = abs(p_row.get("player_1_x", float('inf')) - s_x)
                    dist2 = abs(p_row.get("player_2_x", float('inf')) - s_x)
                    if dist1 < dist2:
                        p_x, p_y = p_row.get("player_1_x"), p_row.get("player_1_y")
                    else:
                        p_x, p_y = p_row.get("player_2_x"), p_row.get("player_2_y")
                        
                    if pd.notna(p_y) and pd.notna(p_x):
                        feet_dist_y = p_y - s_y 
                        feet_dist_x = abs(p_x - s_x)
                        
                        # A pickup is at the feet (Y diff is small) AND near the player (X diff is small)
                        if -50 < feet_dist_y < MAX_FEET_DIST_PX and feet_dist_x < 150:
                            # A pickup is lifted vertically, so horizontal travel (delta_x) is small
                            if delta_x < MAX_PICKUP_X_TRAVEL:
                                print(f"  [Filter] Dropped rally {start_f}-{end_f}: Floor pickup detected (Starts at feet, vertical lift)")
                                continue # Drop this rally
                            
        valid_rallies.append((start_f, end_f))
        
    return valid_rallies

# ============================================================
# MAIN
# ============================================================
def _parse_args():
    ap = argparse.ArgumentParser(
        description="Segment rallies from a gap-filled shuttle trajectory CSV. "
                    "Writes <match_folder>/<name>_rally.csv -- the filename "
                    "win_predictor/predict.py requires.")
    ap.add_argument("--match_folder", required=True,
                    help="Match folder; also the default location for all "
                         "inputs/outputs below")
    ap.add_argument("--video", default=None,
                    help="Default: <match_folder>/<name>.mp4")
    ap.add_argument("--shuttle_csv", default=None,
                    help="Gap-filled shuttle CSV (see TrackNetV3/fill_gaps.py). "
                         "Default: <match_folder>/<name>_ball_filled.csv")
    ap.add_argument("--player_csv", default=None,
                    help="Default: <match_folder>/player_detections.csv")
    ap.add_argument("--court_mask_csv", default=None,
                    help="Optional per-frame court-presence CSV from "
                         "analysis/court_presence.py. ANDed with the player "
                         "scene mask -- use for broadcast videos with "
                         "cutaways/replays where the camera angle isn't "
                         "constant throughout (see that script's docstring).")
    ap.add_argument("--out", default=None,
                    help="Default: <match_folder>/<name>_rally.csv")
    return ap.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    match_folder = args.match_folder.rstrip("/")
    name = os.path.basename(match_folder)

    VIDEO_FILE  = args.video       or os.path.join(match_folder, f"{name}.mp4")
    SHUTTLE_CSV = args.shuttle_csv or os.path.join(match_folder, f"{name}_ball_filled.csv")
    PLAYER_CSV  = args.player_csv  or os.path.join(match_folder, "player_detections.csv")
    OUT_CSV     = args.out         or os.path.join(match_folder, f"{name}_rally.csv")

    fps = get_fps(VIDEO_FILE)
    print(f"Detected FPS: {fps:.1f}")

    shuttle_df = pd.read_csv(SHUTTLE_CSV)
    scene_mask = generate_scene_mask(PLAYER_CSV, VIDEO_FILE)
    if args.court_mask_csv:
        court_mask = load_court_mask(args.court_mask_csv, len(scene_mask))
        n_before = int(scene_mask.sum())
        scene_mask = scene_mask & court_mask
        print(f"  Court mask applied: scene_mask frames {n_before} -> "
              f"{int(scene_mask.sum())} (dropped frames off the main "
              f"broadcast angle)")
    shuttle_df = apply_scene_mask(shuttle_df, scene_mask)

    rallies = segment_rallies(shuttle_df)

    # 1. Drop pickup false positives (jitter spikes, static noise) before anything else
    rallies = filter_pickup_rallies(rallies, shuttle_df, PLAYER_CSV, fps)

    # 2. Duration filter BEFORE merge — drops short jitter rallies (< 2s) so they
    #    cannot be merged with a real rally that starts just after the gap.
    #    e.g. ground-jitter rally (0.2s) followed by 8-frame gap then real rally:
    #    without this step, merge_close_rallies would join them wrongly.
    if rallies:
        temp_df = pd.DataFrame(rallies, columns=["Start_Frame", "End_Frame"])
        temp_df["Duration_sec"] = (temp_df["End_Frame"] - temp_df["Start_Frame"]) / fps
        rallies = list(zip(
            temp_df.loc[temp_df["Duration_sec"] >= MIN_RALLY_DURATION_SEC, "Start_Frame"],
            temp_df.loc[temp_df["Duration_sec"] >= MIN_RALLY_DURATION_SEC, "End_Frame"],
        ))

    # 3. Merge close rallies (residual tracking drops that fill_gaps didn't bridge)
    rallies = merge_close_rallies(rallies, shuttle_df, fps)

    # 4. Apply lookback to recover true rally start from pre-confirmation frames
    final_rallies = apply_lookback(rallies, shuttle_df)

    rally_df = pd.DataFrame(final_rallies, columns=["Start_Frame", "End_Frame"])
    rally_df["Start_Time_sec"] = rally_df["Start_Frame"] / fps
    rally_df["End_Time_sec"]   = rally_df["End_Frame"]   / fps
    rally_df["Duration_sec"]   = rally_df["End_Time_sec"] - rally_df["Start_Time_sec"]

    rally_df["Start_Time"] = rally_df["Start_Time_sec"].apply(format_time)
    rally_df["End_Time"]   = rally_df["End_Time_sec"].apply(format_time)

    os.makedirs(os.path.dirname(OUT_CSV) or ".", exist_ok=True)
    rally_df.to_csv(OUT_CSV, index=False)

    print(f"\n{'#':>3}  {'Start':>8}  {'End':>8}  {'Duration':>8}  {'Start_Fr':>8}  {'End_Fr':>8}")
    print("-" * 57)
    for i, row in rally_df.iterrows():
        print(
            f"{i+1:>3}  {row['Start_Time']:>8}  {row['End_Time']:>8}  "
            f"{row['Duration_sec']:>7.2f}s  {int(row['Start_Frame']):>8}  {int(row['End_Frame']):>8}"
        )
    print("-" * 57)
    print(f"\nSaved {len(rally_df)} rallies -> {OUT_CSV}")
