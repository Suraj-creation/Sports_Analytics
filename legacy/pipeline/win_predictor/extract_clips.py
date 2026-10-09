"""
extract_clips.py
================
Build the clip dataset from match folders.

Each clip is centred on the shuttle's last visible position in the
SEQ_LEN_20F-frame window before the rally end frame.

Output:
    clips/clips_3c/<Match>_r<idx>.npy   — (CLIP_FRAMES, 112, 112, 3) uint8
    labels_3c.csv

Run:
    cd win_predictor
    python3 extract_clips.py --dataset dataset/vk15b_dataset \
                              --video_dir ../video_fixed
"""

import os, argparse
from collections import Counter

import numpy as np
import pandas as pd
import cv2

from config import (
    SEQ_LEN_20F as SEQ_LEN,
    CLIP_FRAMES,
    CROP_FRAC,
    OUT_SIZE,
    CLASSES,
    CLIPS_20F_DIR,
    LABELS_20F,
)

CSV_W   = 1280
CSV_H   = 720
TOL_SEC = 2.0

GT_REASON_MAP = {
    'Opponent Out of Bounds':    'out_of_bounds',
    'Opponent Hit the Net':      'hits_net',
    'Winner Shot':               'wins_by_landing',
    'Opponent Failed to Return': 'wins_by_landing',
}


def _parse_time(s):
    s = str(s).strip()
    if ':' in s:
        parts = s.split(':')
        try:
            return int(parts[0]) * 60 + int(parts[1])
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def _shuttle_center(shu_df, end_frame, sx, sy):
    win = shu_df[
        (shu_df['Frame'] >= end_frame - SEQ_LEN) &
        (shu_df['Frame'] <= end_frame) &
        (shu_df['Visibility'] == 1)
    ].sort_values('Frame')
    if len(win) == 0:
        return None, None
    last = win.iloc[-1]
    return float(last['X']) * sx, float(last['Y']) * sy


def _extract_clip(cap, end_frame, cx, cy, vid_w, vid_h):
    crop_size = int(round(CROP_FRAC * vid_h))
    start_f   = max(0, end_frame - SEQ_LEN)
    sample_at = set(np.linspace(0, SEQ_LEN - 1, CLIP_FRAMES, dtype=int))

    half = crop_size // 2
    x1, y1 = int(cx) - half, int(cy) - half
    x2, y2 = x1 + crop_size, y1 + crop_size
    if x1 < 0:      x2 -= x1; x1 = 0
    if y1 < 0:      y2 -= y1; y1 = 0
    if x2 > vid_w:  x1 -= (x2 - vid_w); x2 = vid_w
    if y2 > vid_h:  y1 -= (y2 - vid_h); y2 = vid_h
    x1, y1 = max(0, x1), max(0, y1)

    cap.set(cv2.CAP_PROP_POS_FRAMES, int(start_f))
    sampled = []
    for offset in range(SEQ_LEN):
        ret, frame = cap.read()
        if not ret or frame is None:
            if offset in sample_at:
                sampled.append(None)
            continue
        if offset in sample_at:
            patch = frame[y1:y2, x1:x2]
            if patch.size == 0:
                sampled.append(None)
            else:
                r = cv2.resize(patch, (OUT_SIZE, OUT_SIZE),
                               interpolation=cv2.INTER_LINEAR)
                sampled.append(cv2.cvtColor(r, cv2.COLOR_BGR2RGB))

    clip = np.zeros((CLIP_FRAMES, OUT_SIZE, OUT_SIZE, 3), dtype=np.uint8)
    for i, img in enumerate(sampled[:CLIP_FRAMES]):
        if img is not None:
            clip[i] = img
    return clip


def _process_match(match_folder, video_path, clip_dir):
    name       = os.path.basename(match_folder)
    gt_path    = os.path.join(match_folder, f'{name}.csv')
    shu_path   = os.path.join(match_folder, f'{name}_ball_filled.csv')
    rally_path = os.path.join(match_folder, f'{name}_rally.csv')

    for p in [gt_path, shu_path, rally_path]:
        if not os.path.exists(p):
            print(f'  SKIP {name} — missing: {p}')
            return []

    gt_df    = pd.read_csv(gt_path)
    shu_df   = pd.read_csv(shu_path)
    rally_df = pd.read_csv(rally_path)

    gt_df['_end_sec'] = gt_df['end_time'].apply(_parse_time)
    valid_gt = gt_df['_end_sec'].notna()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f'  SKIP {name} — cannot open video: {video_path}')
        return []
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    sx, sy = vid_w / CSV_W, vid_h / CSV_H
    print(f'  {name}: {vid_w}×{vid_h}, scale {sx:.3f}×{sy:.3f}')

    rows = []
    for i, rrow in rally_df.iterrows():
        end_sec = _parse_time(rrow.get('End_Time', rrow.get('End_Time_sec', 0)))
        ef      = int(rrow['End_Frame'])

        diffs    = (gt_df.loc[valid_gt, '_end_sec'] - end_sec).abs()
        best_loc = diffs.idxmin()
        if pd.isna(best_loc) or diffs[best_loc] > TOL_SEC:
            continue
        gt_reason = GT_REASON_MAP.get(
            str(gt_df.loc[best_loc, 'win_reason']).strip(), None)
        if gt_reason is None:
            continue

        cx, cy = _shuttle_center(shu_df, ef, sx, sy)
        if cx is None:
            cx, cy = vid_w / 2.0, vid_h / 2.0

        clip      = _extract_clip(cap, ef, cx, cy, vid_w, vid_h)
        clip_name = f'{name}_r{i:03d}.npy'
        np.save(os.path.join(clip_dir, clip_name), clip)

        rows.append({
            'match':     name,
            'rally_idx': i,
            'label':     CLASSES.index(gt_reason),
            'gt_reason': gt_reason,
            'end_frame': ef,
            'cx':        round(cx, 1),
            'cy':        round(cy, 1),
            'clip_file': clip_name,
        })

    cap.release()
    dist = Counter(r['gt_reason'] for r in rows)
    print(f'  → {len(rows)} clips  '
          f'OOB={dist.get("out_of_bounds",0)}  '
          f'HN={dist.get("hits_net",0)}  '
          f'WBL={dist.get("wins_by_landing",0)}')
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset',   default='dataset/vk15b_dataset',
                    help='Folder containing TestN_Full match sub-folders')
    ap.add_argument('--video_dir', default='../video_fixed',
                    help='Folder containing .mp4 video files')
    ap.add_argument('--clip_dir',  default=None,
                    help='Override output clip directory (default: clips/clips_3c)')
    ap.add_argument('--labels',    default=None,
                    help='Override output labels CSV path')
    args = ap.parse_args()

    clip_dir    = args.clip_dir  or CLIPS_20F_DIR
    labels_path = args.labels    or LABELS_20F
    os.makedirs(clip_dir, exist_ok=True)

    matches = sorted([
        d for d in os.listdir(args.dataset)
        if d.startswith('Test') and os.path.isdir(os.path.join(args.dataset, d))
    ])

    if os.path.exists(labels_path):
        existing     = pd.read_csv(labels_path)
        done_matches = set(existing['match'].unique())
        all_rows     = existing.to_dict('records')
        print(f'Existing: {len(existing)} clips for {sorted(done_matches)}')
    else:
        done_matches = set()
        all_rows     = []

    for m in matches:
        if m in done_matches:
            print(f'  {m}: already extracted, skip')
            continue
        video_path = os.path.join(args.video_dir, f'{m}.mp4')
        if not os.path.exists(video_path):
            print(f'  {m}: video not found at {video_path}, skip')
            continue
        rows = _process_match(os.path.join(args.dataset, m), video_path, clip_dir)
        all_rows.extend(rows)

    pd.DataFrame(all_rows).to_csv(labels_path, index=False)

    dist = Counter(r['gt_reason'] for r in all_rows)
    print(f'\nTotal: {len(all_rows)} clips → {labels_path}')
    for cls in CLASSES:
        print(f'  {cls}: {dist.get(cls, 0)}')


if __name__ == '__main__':
    main()
