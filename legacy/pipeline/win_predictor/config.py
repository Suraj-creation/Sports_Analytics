"""
win_predictor/config.py
========================
All thresholds and constants for CNN + rule-based fusion.
"""

import os

DIR = os.path.dirname(os.path.abspath(__file__))

# ── CNN models (trained by setup_models.py) ───────────────────────────────────
MODELS_DIR   = os.path.join(DIR, 'models')
MODEL_20F_PT = os.path.join(MODELS_DIR, 'model_20f.pt')
MODEL_16F_PT = os.path.join(MODELS_DIR, 'model_16f.pt')

# ── Training data (extracted by extract_clips.py) ─────────────────────────────
DATASET_DIR   = os.path.join(DIR, 'dataset')          # vk15b_dataset folder
NETCNN_DIR    = os.path.join(DIR, 'clips')             # clip .npy files
LABELS_20F    = os.path.join(DIR, 'labels_3c.csv')
CLIPS_20F_DIR = os.path.join(DIR, 'clips', 'clips_3c')
LABELS_16F    = os.path.join(DIR, 'labels_16f.csv')
CLIPS_16F_DIR = os.path.join(DIR, 'clips', 'clips_16f')

# ── CNN clip constants ─────────────────────────────────────────────────────────
CLIP_FRAMES = 20          # frames sampled per clip
SEQ_LEN_20F = 45          # look-back window (1.5 s × 30 fps)
SEQ_LEN_16F = 90          # look-back window (3.0 s × 30 fps)
CROP_FRAC   = 480 / 1080  # crop size as fraction of video height (~44 %)
OUT_SIZE    = 112          # r3d_18 input resolution

CNN_MEAN = [0.43216, 0.394666, 0.37645]
CNN_STD  = [0.22803, 0.22145,  0.216989]

CLASSES = ['out_of_bounds', 'hits_net', 'wins_by_landing']

# ── Fusion thresholds ─────────────────────────────────────────────────────────
# CNN-first: trust CNN ensemble when max confidence >= CNN_FIRST_THR,
# else fall back to rule engine.
# 20f r2plus1d_18 + 16f r2plus1d_18 ensemble → 74.7% CNN, 74.7% fused @ thr=0.55
CNN_FIRST_THR = 0.55
GLOBAL_THR    = 0.52   # kept for backward compat

# ── Training hyper-parameters (used by setup_models.py) ───────────────────────
EPOCHS     = 30
BATCH_SIZE = 8
LR         = 5e-5
SEED       = 42

# ── Rule engine thresholds ────────────────────────────────────────────────────
WBL_BALL_Y_THRESH = 0.70
RULE_CONF_LOW     = 0.35

# ── Trajectory RF meta-learner ────────────────────────────────────────────────
MODEL_RF_PKL = os.path.join(MODELS_DIR, 'rf_classifier.pkl')

# ── Strategy E/F/I thresholds ─────────────────────────────────────────────────
HN_THR          = 0.60   # CNN prob_hn gate (Strategy I/E)
NET_ZONE_HN_THR = 0.45   # lowered HN gate when shuttle is in net zone (Strategy I)
NET_ZONE_DIST   = 40.0   # net zone: |Y - net_ground_Y| ≤ 40 px
