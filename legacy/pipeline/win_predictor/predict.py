"""
predict.py
==========
One-shot win/win_reason prediction for a new video using the
CNN 20f + 16f ensemble fused with the rule engine.

Expected inputs inside <match_folder>:
    <name>_ball_filled.csv   — shuttle trajectory (filled gaps)
    <name>_rally.csv         — rally start/end frames
    <name>_court.json        — court polygon
    player_detections.csv    — player bounding boxes (optional)

Optional:
    <name>.mp4               — video file (required for CNN clip extraction
                               and annotated frame output)

Output:
    <match_folder>/win_predictions.csv
    <match_folder>/rally_frames/rally_*.jpg  (when video is given)

Quick start:
    cd win_predictor

    # 1. Extract clips from your labeled dataset (first-time only):
    python3 extract_clips.py --dataset dataset/vk15b_dataset \\
                              --video_dir ../video_fixed

    # 2. Train deployment models on ALL labeled data (first-time only):
    python3 setup_models.py

    # 3. Predict on a new match:
    python3 predict.py --match_folder /path/to/TestN_Full \\
                        --video /path/to/TestN_Full.mp4

Without --video, only the rule engine runs (no CNN clips can be extracted).
"""

import os, sys, argparse
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import cv2
from torch.utils.data import Dataset, DataLoader
from torchvision.models.video import r2plus1d_18, R2Plus1D_18_Weights

from config import (
    CLASSES, MODEL_20F_PT, MODEL_16F_PT,
    CLIP_FRAMES, SEQ_LEN_20F, SEQ_LEN_16F, CROP_FRAC, OUT_SIZE,
    CNN_MEAN, CNN_STD, CNN_FIRST_THR,
    WBL_BALL_Y_THRESH, RULE_CONF_LOW,
    MODEL_RF_PKL, HN_THR, NET_ZONE_HN_THR, NET_ZONE_DIST,
)
from traj_rf import (
    extract_features as rf_extract_features,
    load_rf,
    predict_one as rf_predict_one,
)
from rule_engine import (
    load_court_from_json,
    analyze_rally_end,
    apply_overrides,
    assign_player_sides,
    extract_player_features,
)

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MEAN   = np.array(CNN_MEAN, dtype=np.float32)
STD    = np.array(CNN_STD,  dtype=np.float32)
SHORT  = {'out_of_bounds': 'OOB', 'hits_net': 'HN', 'wins_by_landing': 'WBL'}

_CLASS_COLOR = {
    'out_of_bounds':   ( 60,  60, 220),
    'hits_net':        (  0, 160, 240),
    'wins_by_landing': ( 30, 200,  60),
}


# ── model architecture ────────────────────────────────────────────────────────

def _build_model():
    """Same architecture used by setup_models.py — r2plus1d_18 backbone."""
    model = r2plus1d_18(weights=None)   # weights loaded from .pt, not pretrained
    for p in model.parameters():
        p.requires_grad = False
    in_f = model.fc.in_features
    model.fc = nn.Sequential(
        nn.BatchNorm1d(in_f),
        nn.Linear(in_f, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(0.30),
        nn.Linear(256, len(CLASSES)),
    )
    return model


def _load_model(path):
    if not os.path.exists(path):
        return None
    m = _build_model()
    m.load_state_dict(torch.load(path, map_location=DEVICE))
    return m.to(DEVICE).eval()


# ── clip extraction ───────────────────────────────────────────────────────────

def _extract_clip(cap, end_frame, cx, cy, vid_w, vid_h, seq_len):
    crop_sz  = int(round(CROP_FRAC * vid_h))
    start_f  = max(0, end_frame - seq_len)
    sample_at = set(np.linspace(0, seq_len - 1, CLIP_FRAMES, dtype=int))

    half = crop_sz // 2
    x1, y1 = int(cx) - half, int(cy) - half
    x2, y2 = x1 + crop_sz,   y1 + crop_sz
    if x1 < 0:      x2 -= x1;  x1 = 0
    if y1 < 0:      y2 -= y1;  y1 = 0
    if x2 > vid_w:  x1 -= (x2 - vid_w); x2 = vid_w
    if y2 > vid_h:  y1 -= (y2 - vid_h); y2 = vid_h
    x1, y1 = max(0, x1), max(0, y1)

    cap.set(cv2.CAP_PROP_POS_FRAMES, int(start_f))
    sampled = []
    for offset in range(seq_len):
        ok, frame = cap.read()
        if not ok or frame is None:
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


class _ClipList(Dataset):
    def __init__(self, arrays):
        self.arrays = arrays

    def __len__(self):
        return len(self.arrays)

    def __getitem__(self, idx):
        clip = self.arrays[idx].astype(np.float32) / 255.0
        clip = (clip - MEAN) / STD
        clip = clip.transpose(3, 0, 1, 2)
        return torch.from_numpy(clip.copy())


def _run_model(model, clips):
    """Return (N, 3) softmax probabilities or None."""
    if model is None:
        return None
    dl = DataLoader(_ClipList(clips), batch_size=8, shuffle=False)
    parts = []
    with torch.no_grad():
        for batch in dl:
            logits = model(batch.to(DEVICE))
            parts.append(torch.softmax(logits, dim=1).cpu().numpy())
    return np.concatenate(parts, axis=0)


# ── annotated frame output ────────────────────────────────────────────────────

def _draw_frames(results_df, shuttle_df, video_path, court, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    cap   = cv2.VideoCapture(video_path)
    vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    sx    = vid_w / 1280.0
    sy    = vid_h / 720.0
    saved = 0

    for _, row in results_df.iterrows():
        idx    = int(row.get('rally_idx', 0))
        ef     = int(row.get('end_frame', 0))
        winner = str(row.get('winner', '?'))
        reason = str(row.get('win_reason', ''))
        col    = _CLASS_COLOR.get(reason, (160, 160, 160))
        short  = SHORT.get(reason, reason[:3].upper() if reason else '?')
        conf   = float(row.get('cnn_conf', 0.0))

        cap.set(cv2.CAP_PROP_POS_FRAMES, ef)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue

        if court is not None:
            def _s(pt): return (int(pt[0] * sx), int(pt[1] * sy))
            cpts = np.array([_s(court['TL']), _s(court['TR']),
                             _s(court['BR']), _s(court['BL'])], dtype=np.int32)
            overlay = frame.copy()
            cv2.fillPoly(overlay, [cpts], (80, 220, 80))
            cv2.addWeighted(overlay, 0.07, frame, 0.93, 0, frame)
            cv2.polylines(frame, [cpts], isClosed=True, color=(80, 220, 80), thickness=2)
            nx1 = int(court['net_x_min'] * sx)
            nx2 = int(court['net_x_max'] * sx)
            cv2.line(frame, (nx1, int(court['net_top_Y'] * sy)),
                     (nx2, int(court['net_top_Y'] * sy)), (0, 220, 220), 2)

        trail = shuttle_df[
            (shuttle_df['Frame'] >= ef - 45) &
            (shuttle_df['Frame'] <= ef) &
            (shuttle_df['Visibility'] == 1)
        ].sort_values('Frame')
        pts = [(int(r['X'] * sx), int(r['Y'] * sy)) for _, r in trail.iterrows()]
        for pt in pts[:-1]:
            cv2.circle(frame, pt, 3, col, -1)
        if pts:
            cv2.circle(frame, pts[-1], 9, col, 2)
            cv2.circle(frame, pts[-1], 4, (255, 255, 255), -1)

        FONT, FSCL, PAD, LH = cv2.FONT_HERSHEY_DUPLEX, 0.60, 10, 28
        lines = [(f'Rally {idx + 1}',     (220, 220, 220)),
                 (f'{short}  {conf:.0%}', col),
                 (f'Winner: {winner}',    (220, 220, 220))]
        tx, ty = 14, 14
        mw = max(cv2.getTextSize(t, FONT, FSCL, 1)[0][0] for t, _ in lines)
        cv2.rectangle(frame, (tx-4, ty-4),
                      (tx+mw+PAD*2, ty+len(lines)*LH+PAD), (15,15,15), -1)
        cv2.rectangle(frame, (tx-4, ty-4),
                      (tx+mw+PAD*2, ty+len(lines)*LH+PAD), col, 2)
        for j, (text, color) in enumerate(lines):
            cv2.putText(frame, text, (tx+PAD, ty+PAD+(j+1)*LH-6),
                        FONT, FSCL, color, 1, cv2.LINE_AA)

        cv2.imwrite(os.path.join(out_dir, f'rally_{idx+1:03d}.jpg'), frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 92])
        saved += 1

    cap.release()
    print(f'  Saved {saved} annotated frames → {out_dir}')


# ── main prediction ───────────────────────────────────────────────────────────

def predict(match_folder, video_path=None, player_a='Player A', player_b='Player B',
            fps=30.0):
    """
    Run CNN + rule engine on a match folder.

    Parameters
    ----------
    match_folder : str
        Must contain <name>_ball_filled.csv, <name>_rally.csv, <name>_court.json.
    video_path : str or None
        If given, extracts CNN clips for 20f + 16f ensemble inference.
    player_a : str
        Name for the far-side player (court top half).
    player_b : str
        Name for the near-side player (court bottom half).
    fps : float
        Video frame rate (default 30).

    Returns
    -------
    pd.DataFrame  — one row per rally with winner, win_reason, scores.
    """
    name       = os.path.basename(match_folder.rstrip('/'))
    shu_path   = os.path.join(match_folder, f'{name}_ball_filled.csv')
    rally_path = os.path.join(match_folder, f'{name}_rally.csv')
    court_path = os.path.join(match_folder, f'{name}_court.json')
    player_csv = os.path.join(match_folder, 'player_detections.csv')

    for p in [shu_path, rally_path, court_path]:
        if not os.path.exists(p):
            sys.exit(f'ERROR: missing required file: {p}')

    shuttle_df = pd.read_csv(shu_path)
    rally_df   = pd.read_csv(rally_path)
    court      = load_court_from_json(court_path)

    # Load trajectory RF (trained by setup_models.py --cnn_preds)
    rf_model = load_rf(MODEL_RF_PKL)
    if rf_model is None:
        print('  NOTE: RF model not found — trajectory RF disabled. '
              'Run: python3 setup_models.py --cnn_preds <ens_csv> --dataset <dataset_dir>')

    far_slot  = 'player_1'
    player_df = None
    if os.path.exists(player_csv):
        player_df = pd.read_csv(player_csv)
        far_slot, _ = assign_player_sides(player_csv, court)

    ef_col = next((c for c in ('End_Frame', 'end_frame') if c in rally_df.columns), None)
    mid_y  = (court['court_top_y'] + court['court_bottom_y']) / 2.0

    # ── Clip extraction (if video provided) ───────────────────────────────────
    clips_20f = clips_16f = []
    if video_path and os.path.exists(video_path):
        print(f'  Extracting clips from {os.path.basename(video_path)} ...')
        cap   = cv2.VideoCapture(video_path)
        vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        sx    = vid_w / 1280.0
        sy    = vid_h / 720.0
        clips_20f, clips_16f = [], []
        for _, row in rally_df.iterrows():
            ef  = int(row[ef_col]) if ef_col else 0
            win = shuttle_df[
                (shuttle_df['Frame'] >= ef - SEQ_LEN_20F) &
                (shuttle_df['Frame'] <= ef) &
                (shuttle_df['Visibility'] == 1)
            ].sort_values('Frame')
            if len(win) > 0:
                last_frame     = int(win.iloc[-1]['Frame'])
                frames_missing = ef - last_frame
                cx = float(win.iloc[-1]['X']) * sx
                cy = float(win.iloc[-1]['Y']) * sy
                # Fix 2: extrapolate landing position when shuttle disappears early
                if frames_missing >= 5 and len(win) >= 3:
                    recent = win.tail(3)
                    frames = recent['Frame'].values
                    xs     = recent['X'].values * sx
                    ys     = recent['Y'].values * sy
                    vx = (xs[-1] - xs[0]) / max(frames[-1] - frames[0], 1)
                    vy = (ys[-1] - ys[0]) / max(frames[-1] - frames[0], 1)
                    steps = min(frames_missing, 15)
                    cx = float(np.clip(cx + vx * steps, 0, vid_w))
                    cy = float(np.clip(cy + vy * steps, 0, vid_h))
            else:
                cx, cy = vid_w / 2.0, vid_h / 2.0
            clips_20f.append(_extract_clip(cap, ef, cx, cy, vid_w, vid_h, SEQ_LEN_20F))
            clips_16f.append(_extract_clip(cap, ef, cx, cy, vid_w, vid_h, SEQ_LEN_16F))
        cap.release()
        print(f'  Extracted {len(clips_20f)} clips (20f window) + {len(clips_16f)} (16f window)')

    # ── CNN inference — 20f + 16f ensemble ────────────────────────────────────
    have_cnn = bool(clips_20f)
    if have_cnn:
        print('  Loading CNN models...')
        m20 = _load_model(MODEL_20F_PT)
        m16 = _load_model(MODEL_16F_PT)
        if m20 is None:
            print(f'  WARNING: {MODEL_20F_PT} not found — run setup_models.py first')
        if m16 is None:
            print(f'  WARNING: {MODEL_16F_PT} not found — '
                  'run setup_models.py with --model16 flag')
        p20 = _run_model(m20, clips_20f)
        p16 = _run_model(m16, clips_16f)

        if p20 is not None and p16 is not None:
            probs_all = (p20 + p16) / 2.0
            print(f'  CNN ensemble: 20f + 16f averaged')
        elif p20 is not None:
            probs_all = p20
            print(f'  CNN inference: 20f model only')
        elif p16 is not None:
            probs_all = p16
            print(f'  CNN inference: 16f model only')
        else:
            have_cnn  = False
            probs_all = np.full((len(rally_df), len(CLASSES)),
                                1.0 / len(CLASSES), dtype=np.float32)
            print('  WARNING: no CNN models loaded — using rule engine only')
    else:
        print('  No video — running rule engine only (no CNN clips)')
        probs_all = np.full((len(rally_df), len(CLASSES)),
                            1.0 / len(CLASSES), dtype=np.float32)

    # ── Fusion loop ───────────────────────────────────────────────────────────
    rows = []
    score_a, score_b = 0, 0

    for i, (_, row) in enumerate(rally_df.iterrows()):
        ef = int(row[ef_col]) if ef_col else 0

        pf = extract_player_features(player_df, ef, far_slot) \
             if player_df is not None else None
        event, fault_side, conf, feats = analyze_rally_end(
            shuttle_df, ef, court, fps, pf)
        event, fault_side = apply_overrides(
            event, fault_side, feats, shuttle_df, ef, court, fps,
            player_df=player_df, far_slot=far_slot)

        rule_conf_val = {'HIGH': 0.9, 'MED': 0.55, 'LOW': 0.2}.get(str(conf), 0.5)

        # Ball-Y proxy for fault-side
        win_ball = shuttle_df[(shuttle_df['Frame'] >= ef - 10) &
                               (shuttle_df['Frame'] <= ef) &
                               (shuttle_df['Visibility'] == 1)]
        if win_ball.empty:
            win_ball = shuttle_df[(shuttle_df['Frame'] >= ef - 10) &
                                   (shuttle_df['Frame'] <= ef)]
        ball_y_fault = (
            'near' if (not win_ball.empty and float(win_ball['Y'].iloc[-1]) > mid_y)
            else 'far'
        )

        probs     = probs_all[i]
        cnn_oob   = float(probs[0])
        cnn_hn    = float(probs[1])
        cnn_wbl   = float(probs[2])
        cnn_class = CLASSES[int(np.argmax(probs))]
        cnn_conf  = float(np.max(probs))

        # ── Trajectory RF + Strategies E/F/I/J ──────────────────────────────
        # size_df intentionally omitted here (defaults to None in
        # extract_features) -- nothing in the live pipeline has ever
        # produced a per-match shuttle-size CSV, so passing a path that
        # never resolves was dead weight. The RF's 6 size-based feature
        # slots still exist (rf_classifier.pkl was trained expecting
        # exactly 24 features; removing them would require retraining,
        # which needs the labeled dataset this checkout doesn't have) --
        # they just always take their neutral defaults now, same as they
        # always have in practice.
        rf_feats  = rf_extract_features(
            shuttle_df, ef, court,
            prob_oob=cnn_oob, prob_hn=cnn_hn, prob_wbl=cnn_wbl)
        traj_pred = rf_predict_one(rf_model, rf_feats)

        # Strategy I: lower HN threshold when shuttle ends in net zone
        in_net_zone = (rf_feats is not None
                       and rf_feats['in_net_x'] == 1.0
                       and rf_feats['net_dist_y_px'] <= NET_ZONE_DIST)
        eff_hn_thr = NET_ZONE_HN_THR if in_net_zone else HN_THR

        if cnn_hn >= eff_hn_thr:
            # Strategy E (removed): used to let the OOB/WBL-only traj RF
            # override a fired HN gate to 'wins_by_landing' whenever
            # margin_cm > 0. The RF is trained on OOB/WBL rallies only
            # (HN excluded -- see traj_rf.py), so for a genuine net-hit
            # rally it is structurally incapable of saying "hits_net" and
            # is forced to guess OOB or WBL; since net-hit shuttles
            # typically land just inside the court near the net,
            # margin_cm > 0 was true for most real HN rallies too, so the
            # override fired on ~90/380 rallies live and was right only
            # ~8% of the time (measured against vk15b_dataset GT), versus
            # the 87.8%-correct figure quoted for it in the offline
            # benchmark -- that number came from traj_classifier.py's
            # LOMO-CV harness, which builds its dataset by filtering to
            # GT in {out_of_bounds, wins_by_landing} *before* training/
            # predicting, so traj_pred is None for every real HN rally in
            # that harness by construction. That information isn't
            # available at real inference time, so the override cannot
            # safely fire there. Simplest fix: once the CNN's HN gate
            # fires, trust it -- do not let the OOB/WBL binary RF veto it.
            win_reason = 'hits_net'
            reason_src = 'ML_HN' + ('_I' if in_net_zone else '')
        elif traj_pred is not None:
            # Strategy F: traj=WBL but rule=OOB and fast lateral shot → trust OOB
            if (traj_pred == 'wins_by_landing'
                    and event == 'out_of_bounds'
                    and rf_feats is not None
                    and rf_feats['abs_vx'] > 2.0
                    and rf_feats['speed'] > 4.0):
                win_reason = 'out_of_bounds'
                reason_src = 'ML_STRAT_F'
            else:
                win_reason = traj_pred
                reason_src = 'ML_RF'
        else:
            # No RF prediction → rule engine fallback
            win_reason = event
            reason_src = 'RULE'

        # ── Fault-side: WBL uses shuttle Y vs net floor; others use rule engine ─
        if win_reason == 'wins_by_landing':
            net_gy   = float(court['net_ground_Y'])
            last_win = shuttle_df[(shuttle_df['Frame'] >= ef - 10) &
                                  (shuttle_df['Frame'] <= ef) &
                                  (shuttle_df['Visibility'] == 1)]
            if last_win.empty:
                last_win = shuttle_df[(shuttle_df['Frame'] >= ef - 10) &
                                       (shuttle_df['Frame'] <= ef)]
            if not last_win.empty:
                final_fault = 'far' if float(last_win['Y'].median()) < net_gy else 'near'
                fault_src   = 'WBL_Y'
            else:
                final_fault = fault_side
                fault_src   = 'RULE'
        else:
            final_fault = fault_side
            fault_src   = 'RULE'

        if final_fault == 'near':
            winner, loser = player_a, player_b
        elif final_fault == 'far':
            winner, loser = player_b, player_a
        else:
            winner = loser = 'unknown'

        if winner == player_a:
            score_a += 1
        elif winner == player_b:
            score_b += 1

        rows.append({
            'rally_idx':   i,
            'start_frame': int(row.get('Start_Frame', row.get('start_frame', 0))),
            'end_frame':   ef,
            'start_time':  row.get('Start_Time', row.get('Start_Time_sec', '')),
            'end_time':    row.get('End_Time',   row.get('End_Time_sec', '')),
            'winner':      winner,
            'loser':       loser,
            'win_reason':  win_reason,
            'reason_src':  reason_src,
            'fault_side':  final_fault,
            'fault_src':   fault_src,
            'cnn_class':   cnn_class,
            'cnn_conf':    round(cnn_conf, 4),
            'cnn_oob':     round(cnn_oob,  4),
            'cnn_hn':      round(cnn_hn,   4),
            'cnn_wbl':     round(cnn_wbl,  4),
            f'score_{player_a[:8]}': score_a,
            f'score_{player_b[:8]}': score_b,
        })

    # Explicit columns even when rows is empty (no rallies detected in this
    # clip) -- pd.DataFrame([]) has zero COLUMNS too, which .to_csv()s to a
    # ~1-byte file that pd.read_csv() downstream (fusion_layer.py) can't
    # parse at all (EmptyDataError), crashing the whole run instead of
    # correctly reporting "no rallies found". A header-only CSV is valid,
    # parses to a proper 0-row DataFrame, and lets callers check len(df).
    columns = ['rally_idx', 'start_frame', 'end_frame', 'start_time', 'end_time',
              'winner', 'loser', 'win_reason', 'reason_src', 'fault_side',
              'fault_src', 'cnn_class', 'cnn_conf', 'cnn_oob', 'cnn_hn', 'cnn_wbl',
              f'score_{player_a[:8]}', f'score_{player_b[:8]}']
    return pd.DataFrame(rows, columns=columns)


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='Predict rally winner and win-reason for a new badminton match')
    ap.add_argument('--match_folder', required=True,
                    help='Match folder with *_ball_filled.csv, *_rally.csv, *_court.json')
    ap.add_argument('--video',       default=None,
                    help='Video file for CNN clip extraction (optional; '
                         'rule engine runs without it)')
    ap.add_argument('--player_a',    default='Player A',
                    help='Far player name (default: Player A)')
    ap.add_argument('--player_b',    default='Player B',
                    help='Near player name (default: Player B)')
    ap.add_argument('--fps',         type=float, default=30.0)
    ap.add_argument('--no_frames',   action='store_true',
                    help='Skip saving annotated rally JPEG frames')
    args = ap.parse_args()

    print(f'\n{"="*60}')
    print(f'  win_predictor — {os.path.basename(args.match_folder)}')
    print(f'  Device  : {DEVICE}')
    print(f'  Players : {args.player_a} (far) vs {args.player_b} (near)')
    print(f'  CNN thr : CNN_FIRST_THR={CNN_FIRST_THR}  (20f r2plus1d + 16f r2plus1d ensemble)')
    print(f'{"="*60}')

    df = predict(args.match_folder, args.video, args.player_a, args.player_b, args.fps)

    score_a_col = f'score_{args.player_a[:8]}'
    score_b_col = f'score_{args.player_b[:8]}'

    print(f'\n  {"#":>3}  {"End":>8}  {"Reason":<5}  {"Src":>5}  '
          f'{"Conf":>6}  {"Fault":>5}  {"Winner":<15}  Score')
    print('  ' + '─' * 72)
    for _, r in df.iterrows():
        short = SHORT.get(str(r['win_reason']), str(r['win_reason'])[:3].upper())
        sa    = int(r.get(score_a_col, 0))
        sb    = int(r.get(score_b_col, 0))
        print(f"  {int(r['rally_idx']):>3}  "
              f"{str(r['end_time']):>8}  "
              f"{short:<5}  "
              f"{str(r['reason_src']):>5}  "
              f"{float(r['cnn_conf']):>5.0%}  "
              f"{str(r['fault_side']):>5}  "
              f"{str(r['winner']):<15}  "
              f"{args.player_a[:8]}:{sa}–{sb}:{args.player_b[:8]}")

    if len(df) > 0:
        fa = int(df[score_a_col].iloc[-1]) if score_a_col in df.columns else 0
        fb = int(df[score_b_col].iloc[-1]) if score_b_col in df.columns else 0
        print('  ' + '─' * 72)
        print(f'  Final: {args.player_a} {fa} — {fb} {args.player_b}')

    out_csv = os.path.join(args.match_folder, 'win_predictions.csv')
    df.to_csv(out_csv, index=False)
    print(f'\n  Saved → {out_csv}')

    if args.video and not args.no_frames:
        name       = os.path.basename(args.match_folder.rstrip('/'))
        court      = load_court_from_json(
            os.path.join(args.match_folder, f'{name}_court.json'))
        shuttle_df = pd.read_csv(
            os.path.join(args.match_folder, f'{name}_ball_filled.csv'))
        _draw_frames(df, shuttle_df, args.video, court,
                     os.path.join(args.match_folder, 'rally_frames'))


if __name__ == '__main__':
    main()
