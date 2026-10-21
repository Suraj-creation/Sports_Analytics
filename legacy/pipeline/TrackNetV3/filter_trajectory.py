"""
filter_trajectory.py
--------------------
Remove fake shuttle detections from a raw _ball.csv BEFORE running fill_gaps.py.

THREE FILTERS in sequence:

  FILTER 1 — Bidirectional spike filter
    For every visible frame, compute the speed to the nearest visible
    frame BEFORE it and the nearest visible frame AFTER it.
    If BOTH are above SPEED_BOTH_TH AND both are direct neighbors
    (dt == 1 frame) the frame is a 1-frame spike/teleport → fake.
    Catches: single-frame position spikes inside a real trajectory.

  FILTER 2 — Cluster internal break filter (iterative)
    Within every cluster of consecutive visible frames, scan for any
    consecutive pair whose speed exceeds SPEED_INTERNAL_TH.
    Such a jump is physically impossible for any real shuttle motion.
    At the break point the segment BEFORE the jump is the fake part
    (if the entry speed to that segment is also high → confirmed fake).
    Zeroing the fake segment may expose a new break → iterate.
    Catches: wrong-position clusters glued to the real trajectory.

  FILTER 3 — Smash direction filter
    After a detection in the smash zone (Y < smash_y * height) that
    is immediately followed by an invisible frame (shuttle exited top
    of frame), any Visibility=1 frame with Y >= reentry_y * height
    before the shuttle genuinely re-enters from the top is a fake
    mid-frame detection.
    Catches: post-smash fake clusters (racket head / player body).

Usage (run BEFORE fill_gaps.py):
    python3 TrackNetV3/filter_trajectory.py \
        --input  shuttle_tracking/Test10_Full_ball.csv \
        --output shuttle_tracking/Test10_Full_ball_clean.csv \
        --video_height 720 --video_width 1280


        python3 TrackNetV3/filter_trajectory.py \
        --input  shuttle_tracking/Test7_Full_ball.csv \
        --output shuttle_tracking/Test6_Full_ball_clean.csv \
        --player_csv  Test6_Full/player_detections.csv \
        --video_width 1920  --video_height 1080


        
"""

import argparse
import numpy as np
import pandas as pd


# ---------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------
SPEED_BOTH_TH       = 130.0  # px/frame — BOTH neighbors above this → spike
SPEED_HARD_TH       = 300.0  # px/frame — impossible in 1 frame regardless of forward speed
SPEED_INTERNAL_TH   = 300.0  # px/frame — impossible internal jump within cluster
ENTRY_TH            = 100.0  # px/frame — entry speed above this confirms fake segment
SMASH_Y_FRACTION    = 0.20   # top 20% of frame = smash zone
SMASH_REENTRY_FRAC  = 0.20   # re-entry must land in top 20%
SMASH_SCAN_FRAMES   = 90     # look ahead up to 90 frames after smash exit
MIN_SMASH_GAP       = 4      # shuttle must be invisible for at least this many frames
                             # before we treat mid-frame detections as fakes.
                             # A 1-3 frame gap means the shuttle barely left the
                             # frame and came straight back — those are real.
                             # 4 catches the case where Filter 1 already zeroed frame
                             # N+1 (speed > 300), leaving frames N+2..N+4 invisible = 3
                             # raw + 1 pre-zeroed = 4 total → fake at N+5 is caught.
SERVE_TOSS_SPEED_TH = 5.0    # px/frame — if the cluster just before the smash-zone
                             # detection has average speed below this, the shuttle was
                             # stationary (being held for serve) → serve toss, not a
                             # smash → skip Filter 3 to preserve the real rally.


# ---------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------
def _vis_clusters(vis):
    """Return list of (start_idx, end_idx_exclusive) for every vis=1 run."""
    clusters, i = [], 0
    while i < len(vis):
        if vis[i] == 1:
            s = i
            while i < len(vis) and vis[i] == 1:
                i += 1
            clusters.append((s, i))
        else:
            i += 1
    return clusters


def _spd(x, y, frames, a, b):
    dt = abs(int(frames[b]) - int(frames[a]))
    if dt == 0:
        return float('inf')
    return float(np.sqrt((x[b] - x[a])**2 + (y[b] - y[a])**2) / dt)


def _nearest_before(vis, idx):
    for j in range(idx - 1, -1, -1):
        if vis[j] == 1:
            return j
    return None


def _nearest_after(vis, idx):
    for j in range(idx, len(vis)):
        if vis[j] == 1:
            return j
    return None


# ---------------------------------------------------------------
# FILTER 1 — Bidirectional spike (works inside large clusters too)
# ---------------------------------------------------------------
def filter_bidirectional_spike(vis, x, y, frames, speed_th=SPEED_BOTH_TH,
                               hard_th=SPEED_HARD_TH):
    """
    Two cases both zero the frame:
      1. Hard threshold: backward speed > hard_th AND dt_back == 1.
         A single-frame teleport of 300+ px is physically impossible
         for any shuttle regardless of what comes after it.
         Catches: fake frame sitting between a real smash exit and the
         invisible gap (e.g. Y=16 -> fake Y=352 -> vis=0 ...).
      2. Bilateral threshold: BOTH backward AND forward speed > speed_th
         AND both neighbors are direct (dt == 1).
         Catches: single-frame spikes inside a real trajectory.

    Uses original coordinates for all speed checks (snapshot taken before
    any frame is zeroed) so that zeroing one frame does not cascade and
    inflate the apparent speed of its neighbours.
    """
    removed = 0

    # Snapshot original arrays so zeroing one frame does not affect
    # the speed computation for any subsequent frame in this pass.
    x_orig = x.copy()
    y_orig = y.copy()
    vis_idx = [i for i in range(len(vis)) if vis[i] == 1]

    for k, i in enumerate(vis_idx):
        # Walk backwards to find the nearest neighbour that is still
        # alive in the ORIGINAL data (not zeroed in a previous run).
        prev_i = None
        for j in range(k - 1, -1, -1):
            if vis_idx[j] is not None:
                prev_i = vis_idx[j]
                break

        if prev_i is None:
            continue

        dt_back = int(frames[i]) - int(frames[prev_i])
        sb = float(np.sqrt((x_orig[i] - x_orig[prev_i])**2 +
                           (y_orig[i] - y_orig[prev_i])**2))
        if dt_back > 0:
            sb /= dt_back

        # Case 1 — hard one-directional threshold
        if dt_back == 1 and sb > hard_th:
            x[i] = 0.0; y[i] = 0.0; vis[i] = 0
            removed += 1
            continue

        # Case 2 — bilateral threshold
        next_i = None
        for j in range(k + 1, len(vis_idx)):
            if vis_idx[j] is not None:
                next_i = vis_idx[j]
                break

        if next_i is None:
            continue

        dt_fwd = int(frames[next_i]) - int(frames[i])
        sf = float(np.sqrt((x_orig[next_i] - x_orig[i])**2 +
                           (y_orig[next_i] - y_orig[i])**2))
        if dt_fwd > 0:
            sf /= dt_fwd

        if sb > speed_th and sf > speed_th and dt_back == 1 and dt_fwd == 1:
            x[i] = 0.0; y[i] = 0.0; vis[i] = 0
            removed += 1

    return removed


# ---------------------------------------------------------------
# FILTER 2 — Internal break filter (iterative)
# ---------------------------------------------------------------
def filter_internal_break(vis, x, y, frames,
                          internal_th=SPEED_INTERNAL_TH,
                          entry_th=ENTRY_TH):
    """
    Find impossible internal jumps (> internal_th) within visible clusters.
    At each jump the segment BEFORE the jump is fake if the entry speed
    to that segment is also high (> entry_th).
    Iterate until no more breaks are found.
    """
    total_removed = 0
    changed = True
    while changed:
        changed = False
        for s, e in _vis_clusters(vis):
            # Scan consecutive pairs within the cluster
            for k in range(s, e - 1):
                sp = _spd(x, y, frames, k, k + 1)
                if sp <= internal_th:
                    continue

                # Found impossible internal jump at (k → k+1)
                # The segment [s .. k] is the suspect (before the jump).
                prev_cluster = _nearest_before(vis, s)
                entry_spd = _spd(x, y, frames, prev_cluster, s) if prev_cluster is not None else 0.0

                if entry_spd > entry_th or prev_cluster is None:
                    # Fake segment confirmed — zero frames s..k
                    for m in range(s, k + 1):
                        x[m] = 0.0; y[m] = 0.0; vis[m] = 0
                    total_removed += k - s + 1
                    changed = True
                break  # re-scan clusters after modification

    return total_removed


# ---------------------------------------------------------------
# FILTER 3 — Smash direction filter
# ---------------------------------------------------------------
def filter_smash_direction(vis, x, y, frames, video_height,
                           smash_y_fraction=SMASH_Y_FRACTION,
                           reentry_fraction=SMASH_REENTRY_FRAC,
                           scan_limit=SMASH_SCAN_FRAMES,
                           min_gap=MIN_SMASH_GAP,
                           serve_toss_th=SERVE_TOSS_SPEED_TH):
    """
    After a smash-zone detection (Y < smash_y * height) where the shuttle
    immediately goes invisible (next frame is vis=0), scan forward and zero
    any visible frame with Y >= reentry_y until genuine top-frame re-entry.

    min_gap guard: only scan if the shuttle was invisible for at least
    min_gap consecutive frames.  A 1-2 frame gap means the shuttle barely
    left the frame and the first detection after it is the real trajectory
    coming back — not a fake mid-frame blob.

    serve_toss guard: if the cluster just before the smash-zone detection
    was nearly stationary (avg speed < serve_toss_th), the shuttle was being
    held for a serve toss — not a rally smash — so the detections that follow
    are the real rally and must not be zeroed.
    """
    smash_y   = video_height * smash_y_fraction
    reentry_y = video_height * reentry_fraction
    removed   = 0

    for i in range(len(vis)):
        if vis[i] != 1 or y[i] >= smash_y:
            continue
        # Shuttle must go invisible immediately → it exited the frame
        if i + 1 < len(vis) and vis[i + 1] == 1:
            continue

        # Count consecutive invisible frames before the first visible one
        invis_count = 0
        j = i + 1
        while j < len(vis) and vis[j] == 0:
            invis_count += 1
            j += 1

        # Too short a gap → shuttle barely left the frame, skip fake scan
        if invis_count < min_gap:
            continue

        # Serve-toss guard: find the cluster ending at the nearest visible
        # frame before i and compute its average speed.  If it is stationary
        # the shuttle was held by the server — this is a serve toss, not a
        # smash — so do NOT zero the frames that follow.
        # Walk back to the START of the smash-zone cluster containing i,
        # then look for the cluster that precedes it.
        smash_cluster_start = i
        while smash_cluster_start > 0 and vis[smash_cluster_start - 1] == 1:
            smash_cluster_start -= 1
        prev_vis = _nearest_before(vis, smash_cluster_start)
        if prev_vis is not None:
            cs = prev_vis
            while cs > 0 and vis[cs - 1] == 1:
                cs -= 1
            # Only check the last 8 frames of the preceding cluster —
            # the shuttle's state immediately before the toss.
            # Using the whole cluster would include earlier rally motion
            # and inflate the average above the stationary threshold.
            window_start = max(cs, prev_vis - 7)
            spds = []
            for m in range(window_start, prev_vis):
                if vis[m] == 1 and vis[m + 1] == 1:
                    dt = max(int(frames[m + 1]) - int(frames[m]), 1)
                    spds.append(
                        float(np.sqrt((x[m + 1] - x[m]) ** 2 +
                                      (y[m + 1] - y[m]) ** 2)) / dt
                    )
            if spds and float(np.mean(spds)) < serve_toss_th:
                continue  # stationary preceding cluster → serve toss, skip

        # Scan forward for fake mid-frame detections
        scan = i + 1
        while scan < len(vis) and (frames[scan] - frames[i]) <= scan_limit:
            if vis[scan] == 1:
                if y[scan] < reentry_y:
                    break  # genuine re-entry, stop
                else:
                    x[scan] = 0.0; y[scan] = 0.0; vis[scan] = 0
                    removed += 1
            scan += 1

    return removed


# ---------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------
def filter_trajectory(df, video_height, video_width=1920):
    df = df.sort_values('Frame').reset_index(drop=True)

    frames = df['Frame'].values.astype(int)
    x      = df['X'].values.astype(float)
    y      = df['Y'].values.astype(float)
    vis    = df['Visibility'].values.copy()

    before = int(vis.sum())

    r1 = filter_bidirectional_spike(vis, x, y, frames)
    r2 = filter_internal_break(vis, x, y, frames)
    r3 = filter_smash_direction(vis, x, y, frames, video_height)

    after = int(vis.sum())
    print(f"  Filter 1 (bidirectional spike)  : -{r1} detections")
    print(f"  Filter 2 (internal break)       : -{r2} detections")
    print(f"  Filter 3 (smash direction)      : -{r3} detections")
    print(f"  Total removed: {before - after}  |  Remaining vis=1: {after}")

    df = df.copy()
    df['X']          = np.round(x).astype(int)
    df['Y']          = np.round(y).astype(int)
    df['Visibility'] = vis
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',         required=True)
    parser.add_argument('--output',        required=True)
    parser.add_argument('--video_height',  type=int,   default=1080)
    parser.add_argument('--video_width',   type=int,   default=1920)
    parser.add_argument('--speed_both',    type=float, default=SPEED_BOTH_TH,
                        help='Bidirectional spike threshold px/frame (default 130)')
    parser.add_argument('--speed_internal',type=float, default=SPEED_INTERNAL_TH,
                        help='Impossible internal jump threshold px/frame (default 300)')
    parser.add_argument('--entry_th',      type=float, default=ENTRY_TH,
                        help='Entry speed to confirm fake segment (default 100)')
    parser.add_argument('--smash_y',       type=float, default=SMASH_Y_FRACTION,
                        help='Smash zone top fraction (default 0.20)')
    parser.add_argument('--smash_reentry', type=float, default=SMASH_REENTRY_FRAC,
                        help='Re-entry zone top fraction (default 0.20)')
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    print(f"Loaded {len(df)} rows | vis=1 before: {int(df['Visibility'].sum())}")
    df_clean = filter_trajectory(df, args.video_height, args.video_width)
    df_clean.to_csv(args.output, index=False)
    print(f"Saved: {args.output}")


if __name__ == '__main__':
    main()