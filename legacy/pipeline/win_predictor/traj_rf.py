"""
traj_rf.py
==========
Trajectory-based Random Forest meta-learner for win-reason classification.

Trains a binary RF (OOB vs WBL) using 24 features:
  - 11 trajectory features (velocity, shape, density, parabola)
  - 6  shuttle apparent-size features -- present in the trained
       rf_classifier.pkl's expected input shape, but currently always
       neutral defaults (size_mean=0.0, size_ratio=1.0, etc): nothing in
       the live pipeline (run_full_pipeline.py) produces a per-match
       apparent-size CSV, so extract_features() always falls back. Kept
       rather than removed because the already-trained model expects
       exactly 24 features -- dropping these would require retraining
       from labeled data, which this checkout doesn't have.
  - 3  CNN softmax probabilities (prob_oob, prob_hn, prob_wbl)
  - 4  net-geometry features (Strategy J)

HN rallies are NOT classified by the RF; they are handled upstream by the
Strategy I / HN-gate threshold check in predict.py.

Usage (from win_predictor/):
    from traj_rf import extract_features, load_rf, predict_one
"""

import os
import numpy as np
import pandas as pd
import cv2
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

COURT_W_CM = 610
COURT_L_CM = 1341

FEATURE_COLS = [
    'margin_cm', 'avg_vy', 'avg_vx', 'abs_vx', 'speed',
    'is_post', 'n_tight', 'para_extrap', 'dist_baseline', 'std_y', 'para_a',
    'size_mean', 'size_last5', 'size_slope', 'size_ratio', 'size_at_end', 'size_growing',
    'cnn_prob_oob', 'cnn_prob_wbl', 'cnn_prob_hn',
    'last_x_norm', 'last_y_norm', 'net_dist_y_px', 'in_net_x',
]


def _build_H_cm(court: dict) -> np.ndarray:
    """Pixel → cm homography from court corner dict (from load_court_from_json)."""
    src = np.float32([court['TL'], court['TR'], court['BR'], court['BL']])
    dst = np.float32([
        [0, 0], [COURT_W_CM, 0],
        [COURT_W_CM, COURT_L_CM], [0, COURT_L_CM],
    ])
    return cv2.getPerspectiveTransform(src, dst)


def extract_features(shu_df: pd.DataFrame, end_frame: int, court: dict,
                     size_df: pd.DataFrame = None,
                     prob_oob: float = 0.333,
                     prob_hn:  float = 0.333,
                     prob_wbl: float = 0.333) -> dict | None:
    """
    Extract the 24-feature vector for a single rally.

    Parameters
    ----------
    shu_df     : ball_filled DataFrame (columns: Frame, X, Y, Visibility)
    end_frame  : last frame of the rally
    court      : dict from rule_engine.load_court_from_json()
    size_df    : optional apparent-size DataFrame (columns: Frame, size/area).
                 Not produced anywhere in the live pipeline -- predict.py
                 never passes this, so it's always None there in practice.
                 Only meaningful if you're calling this directly with your
                 own precomputed size data.
    prob_oob/hn/wbl : CNN ensemble softmax probabilities

    Returns dict of named features, or None if <3 visible frames in window.
    Internal keys prefixed _ (abs_vx, speed, margin_cm) are exposed for
    Strategy E/F/I checks in predict.py without re-computing.
    """
    WIN = 45
    vis_col = 'Visibility' if 'Visibility' in shu_df.columns else None

    win = shu_df[(shu_df['Frame'] >= end_frame - WIN) & (shu_df['Frame'] <= end_frame)]
    if vis_col:
        win = win[win[vis_col] == 1]
    win = win.sort_values('Frame').copy()

    if len(win) < 3:
        return None

    win['vy'] = win['Y'].diff().fillna(0)
    win['vx'] = win['X'].diff().fillna(0)

    clean = win[(win['vy'].abs() < 80) & (win['vx'].abs() < 120)]
    if len(clean) < 3:
        clean = win

    lx = float(clean.iloc[-1]['X'])
    ly = float(clean.iloc[-1]['Y'])

    tail5  = clean.tail(5)
    avg_vy = float(tail5['vy'].mean()) if len(tail5) > 0 else 0.0
    avg_vx = float(tail5['vx'].mean()) if len(tail5) > 0 else 0.0
    speed  = float(np.hypot(avg_vx, avg_vy))
    std_y  = float(tail5['Y'].std()) if len(tail5) > 1 else 0.0

    t3vy    = clean.tail(3)['vy'].values.astype(float)
    is_post = 1.0 if np.sum(t3vy < 0) >= 2 else 0.0

    tight   = clean[clean['Frame'] >= end_frame - 25]
    n_tight = float(len(tight))

    para_a = 0.0; extrap = 0.0
    if n_tight >= 5:
        t  = tight['Frame'].values.astype(float)
        y  = tight['Y'].values.astype(float)
        t0 = t.mean()
        try:
            a, b, c = np.polyfit(t - t0, y, 2)
            para_a  = float(a)
            if a < 0:
                t_v    = -b / (2 * a) + t0
                extrap = float(t_v - t[-1])
        except Exception:
            pass

    # margin_cm: real-world distance from nearest court boundary (cm)
    H_cm   = _build_H_cm(court)
    pt     = np.array([[[lx, ly]]], dtype=np.float32)
    rw     = cv2.perspectiveTransform(pt, H_cm)[0][0]
    margin = float(min(rw[0], COURT_W_CM - rw[0], rw[1], COURT_L_CM - rw[1]))

    far_y         = float((court['TL'][1] + court['TR'][1]) / 2.0)
    dist_baseline = float(ly - far_y)

    # Shuttle apparent-size features
    size_feats = dict(size_mean=0.0, size_last5=0.0, size_slope=0.0,
                      size_ratio=1.0, size_at_end=0.0, size_growing=0.0)
    if size_df is not None and not size_df.empty:
        sz_col = next((c for c in ('size', 'area', 'Size', 'Area')
                       if c in size_df.columns), None)
        if sz_col:
            sw = size_df[(size_df['Frame'] >= end_frame - WIN) &
                         (size_df['Frame'] <= end_frame)].dropna(subset=[sz_col])
            if len(sw) >= 2:
                sv = sw[sz_col].values.astype(float)
                size_feats = dict(
                    size_mean    = float(sv.mean()),
                    size_last5   = float(sv[-5:].mean()) if len(sv) >= 5 else float(sv.mean()),
                    size_slope   = float(np.polyfit(np.arange(len(sv)), sv, 1)[0]),
                    size_ratio   = float(sv[-1] / sv[0]) if sv[0] > 0 else 1.0,
                    size_at_end  = float(sv[-1]),
                    size_growing = 1.0 if sv[-1] > sv[0] else 0.0,
                )

    # Net-geometry features (Strategy J)
    net_y  = float(court.get('net_ground_Y', 432))
    nx_min = float(court.get('net_x_min', 345))
    nx_max = float(court.get('net_x_max', 928))
    cw     = nx_max - nx_min if nx_max > nx_min else 583
    ch_top = float(court.get('court_top_y',    300))
    ch_bot = float(court.get('court_bottom_y', 655))
    ch     = (ch_bot - ch_top) if ch_bot > ch_top else 355

    return {
        # trajectory
        'margin_cm':     margin,
        'avg_vy':        avg_vy,
        'avg_vx':        avg_vx,
        'abs_vx':        abs(avg_vx),
        'speed':         speed,
        'is_post':       is_post,
        'n_tight':       n_tight,
        'para_extrap':   extrap,
        'dist_baseline': dist_baseline,
        'std_y':         std_y,
        'para_a':        para_a,
        # size
        **size_feats,
        # CNN probs
        'cnn_prob_oob':  prob_oob,
        'cnn_prob_wbl':  prob_wbl,
        'cnn_prob_hn':   prob_hn,
        # net geometry
        'last_x_norm':   (lx - nx_min) / cw,
        'last_y_norm':   (ly - ch_top) / ch,
        'net_dist_y_px': abs(ly - net_y),
        'in_net_x':      float(nx_min <= lx <= nx_max),
    }


def predict_one(rf, feats: dict) -> str | None:
    """
    Return 'out_of_bounds' or 'wins_by_landing', or None if RF not loaded.
    Only called for rallies that are NOT already handled by the HN gate.
    """
    if rf is None or feats is None:
        return None
    X = np.array([[feats[c] for c in FEATURE_COLS]], dtype=np.float32)
    return str(rf.predict(X)[0])


def train_rf(cnn_preds_csv: str, dataset_dir: str) -> Pipeline:
    """
    Train RF on labeled data. Returns a fitted sklearn Pipeline.

    cnn_preds_csv must have columns:
        match, rally_idx, gt, end_frame, prob_oob, prob_hn, prob_wbl
    where gt ∈ {'out_of_bounds', 'wins_by_landing', 'hits_net'}.
    HN rows are automatically excluded.

    dataset_dir must contain <match>/<match>_ball_filled.csv,
    <match>/<match>_court.json, and optionally <match>/<match>_shuttle_size.csv.
    """
    from rule_engine import load_court_from_json

    cnn    = pd.read_csv(cnn_preds_csv)
    subset = cnn[cnn['gt'].isin(['out_of_bounds', 'wins_by_landing'])].copy()
    print(f'  RF training: {len(subset)} rallies (OOB + WBL only, HN excluded)')

    rows = []
    for m in subset['match'].unique():
        court_p = os.path.join(dataset_dir, m, f'{m}_court.json')
        ball_p  = os.path.join(dataset_dir, m, f'{m}_ball_filled.csv')
        size_p  = os.path.join(dataset_dir, m, f'{m}_shuttle_size.csv')
        if not os.path.exists(court_p) or not os.path.exists(ball_p):
            print(f'  SKIP {m} — missing court or ball CSV')
            continue

        court   = load_court_from_json(court_p)
        shu     = pd.read_csv(ball_p)
        size_df = pd.read_csv(size_p) if os.path.exists(size_p) else None

        for _, r in subset[subset['match'] == m].iterrows():
            feats = extract_features(
                shu, int(r['end_frame']), court, size_df,
                prob_oob=float(r['prob_oob']),
                prob_hn =float(r['prob_hn']),
                prob_wbl=float(r['prob_wbl']),
            )
            if feats is None:
                continue
            rows.append({**{c: feats[c] for c in FEATURE_COLS}, 'label': r['gt']})

    if not rows:
        raise RuntimeError('No features extracted — check dataset_dir and cnn_preds_csv paths.')

    df = pd.DataFrame(rows)
    X  = df[FEATURE_COLS].values.astype(np.float32)
    y  = df['label'].values

    rf = Pipeline([
        ('scaler', StandardScaler()),
        ('rf', RandomForestClassifier(
            n_estimators=300, max_depth=8, min_samples_leaf=3,
            class_weight='balanced', random_state=42, n_jobs=-1)),
    ])
    rf.fit(X, y)
    oob_n = int((y == 'out_of_bounds').sum())
    wbl_n = int((y == 'wins_by_landing').sum())
    print(f'  RF fitted  OOB={oob_n}  WBL={wbl_n}  features={len(FEATURE_COLS)}')
    return rf


def save_rf(rf, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(rf, path)
    print(f'  RF saved → {path}')


def load_rf(path: str):
    """Load RF from path. Returns None (silently) if file not found."""
    if not os.path.exists(path):
        return None
    return joblib.load(path)
