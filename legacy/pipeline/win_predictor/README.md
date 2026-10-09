# win_predictor

Predicts the **winner** and **win reason** of each rally in a badminton match.

Three win-reason classes:
- `out_of_bounds` — shuttle lands outside the court
- `hits_net` — shuttle hits the net
- `wins_by_landing` — shuttle lands unreturned inside the court

**Validated accuracy: 81.8% win-reason, ~69% winner** (380 rallies, 8-match LOMO-CV)

---

## Folder structure

```
win_predictor/
├── predict.py        ← main entry point: run this on a new match
├── setup_models.py   ← one-time training (CNN + RF)
├── rule_engine.py    ← court geometry, player side detection, rule-based fallback
├── traj_rf.py        ← trajectory Random Forest meta-learner (24 features)
├── config.py         ← all thresholds, paths, constants
└── models/
    ├── model_20f.pt        ← trained 20-frame r2plus1d_18 CNN
    ├── model_16f.pt        ← trained 16-frame r2plus1d_18 CNN
    └── rf_classifier.pkl   ← trained trajectory RF
```

---

## Requirements

```bash
pip install torch torchvision opencv-python pandas numpy scikit-learn joblib
```

---

## Predicting a new match

Each match folder must contain:

```
TestN_Full/
├── TestN_Full_ball_filled.csv   # shuttle trajectory (TrackNetV3 + fill_gaps)
├── TestN_Full_rally.csv         # rally start/end frames
├── TestN_Full_court.json        # court polygon (from court annotation tool)
└── player_detections.csv        # player bounding boxes (optional, improves winner side)
```

Run:

```bash
cd win_predictor

python3 predict.py \
    --match_folder /path/to/TestN_Full \
    --video        /path/to/TestN_Full.mp4 \
    --player_a     "Player A" \
    --player_b     "Player B"
```

`--player_a` is the **far-side** player (top of frame). `--player_b` is the **near-side** player (bottom of frame).

**Output files written into the match folder:**
- `win_predictions.csv` — one row per rally: winner, win_reason, fault_side, CNN probs, running score
- `rally_frames/rally_NNN.jpg` — annotated end-frame image for each rally

### Without a video file

```bash
python3 predict.py --match_folder /path/to/TestN_Full
```

CNN clip extraction is skipped. The trajectory RF still runs using ball CSV data alone (CNN probabilities default to uniform 0.33 each). Accuracy will be lower without CNN.

---

## First-time setup (train models)

The `models/` directory ships with pre-trained checkpoints. If you need to retrain from scratch (new dataset, new clips):

```bash
cd win_predictor

python3 setup_models.py \
    --clips_20f  ../vk15b2/netcnn/clips_3c_v3 \
    --labels_20f ../vk15b2/netcnn/labels_3c_v3.csv \
    --clips_16f  ../vk15b2/netcnn/clips_16f_v3 \
    --labels_16f ../vk15b2/netcnn/labels_16f_v3.csv \
    --cnn_preds  ../vk15b2/netcnn/ens_20r2_16r2.csv \
    --dataset    ../vk15b2/vk15b_dataset
```

This trains both CNN models (~10 min on GPU) then the RF meta-learner (~30 sec) and saves all three files into `models/`.

---

## How the pipeline works

For each rally, prediction runs in this order:

```
Video clip
    │
    ▼
CNN ensemble (20f + 16f r2plus1d_18)
    │  → prob_oob, prob_hn, prob_wbl
    ▼
Trajectory RF (24 features from ball CSV + CNN probs)
    │  → traj_pred: OOB or WBL  (HN excluded from RF — handled by gate below)
    ▼
Strategy decisions:
    ├─ Strategy I:  if shuttle in net zone → lower HN gate from 0.60 → 0.45
    ├─ HN gate:     if prob_hn ≥ threshold → predict hits_net ...
    │     └─ Strategy E: UNLESS RF says WBL and shuttle is inside court → wins_by_landing
    ├─ Strategy F:  if traj=WBL but rule=OOB and fast lateral shot → out_of_bounds
    └─ RF direct:   otherwise trust traj_pred
    ▼
Fault-side (who lost the point):
    ├─ WBL: shuttle last Y vs net floor line → far or near
    └─ OOB / HN: rule engine geometric partition
    ▼
Winner = player on the opposite side from the fault
```

### Decision source labels in output

| `reason_src` | Meaning |
|---|---|
| `ML_RF` | Trajectory RF made the call directly |
| `ML_STRAT_E` | CNN said net-hit but RF + court margin overrode to WBL |
| `ML_HN` | CNN net-hit gate fired and RF agreed (or no RF prediction) |
| `ML_HN_I` | Same as above but via the lowered net-zone threshold (Strategy I) |
| `ML_STRAT_F` | RF said WBL but rule engine + velocity pattern confirmed OOB |
| `RULE` | No RF features available, rule engine fallback |

---

## Key constants (config.py)

| Constant | Value | Description |
|---|---|---|
| `HN_THR` | 0.60 | CNN prob_hn threshold to trigger net-hit gate |
| `NET_ZONE_HN_THR` | 0.45 | Lowered threshold when shuttle is in net zone (Strategy I) |
| `NET_ZONE_DIST` | 40.0 px | Net zone: shuttle within 40px of net ground line |
| `CLIP_FRAMES` | 20 | Frames sampled per CNN clip |
| `SEQ_LEN_20F` | 45 | Look-back window for 20f model (1.5 s @ 30 fps) |
| `SEQ_LEN_16F` | 90 | Look-back window for 16f model (3.0 s @ 30 fps) |
