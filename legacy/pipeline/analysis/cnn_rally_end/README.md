# Temporal rally-end classifier (`wins_by_landing` focus)

Replaces only the **winner + win-reason decision** (`analyze_rally_end` →
event + side) with a learned model. The tracker (TrackNetV3), player
detection (YOLO), rally segmentation, `determine_winner()`, and the shot-type
classifier are **untouched**.

Two model families were built and evaluated:
1. **Trajectory model** — shuttle + player coordinate sequences (no video).
2. **RGB clip model** — `r2plus1d_18` on the last ~1.3 s of video, optionally
   fused with a shuttle-heatmap channel and player-motion features.

## Headline — neither learned model beats the geometry baseline

Leave-one-match-out CV (each rally predicted by a model that never saw its
match). Head-to-head on the **131 rallies with `court.json`** (the only ones
the geometric baseline can score), same rallies, same `End_Frame`s:

| model | overall acc | macro-F1 | **wins_by_landing recall** |
|---|---|---|---|
| **Geometric baseline** (existing rule) | **0.672** | **0.657** | **0.583** |
| Trajectory CNN (shuttle+player) | 0.626 | 0.622 | 0.528 |
| Trajectory CNN (shuttle-only) | 0.534 | 0.532 | 0.528 |
| RGB CNN — rgb | 0.450 | 0.454 | 0.556 |
| RGB CNN — rgb+heat | 0.496 | 0.484 | 0.361 |
| RGB CNN — rgb+heat+player | 0.496 | 0.496 | 0.417 |

**Verdict: the geometry rule stays the default.** No learned model — trajectory
or RGB — beats it on `wins_by_landing` recall (best is RGB-rgb at 0.556 vs
0.583), and every RGB variant is far worse on overall accuracy (~0.45–0.50 vs
0.672). The spec's "raw pixels will carry the signal" hypothesis **did not pay
off at this data scale**. Nothing is wired into the live decision path.

## Why the pixel model underperformed (honest reading)

* **Tiny data for a 33M-param 3D CNN.** 72 landing clips total, ~8–14 per
  held-out match. Per-fold landing recall swings 0.14–0.86 — the pooled
  numbers are noisy point estimates, not stable measurements.
* **Reduced config to finish.** The first full run (16 frames / 30 epochs) was
  torn down mid-way after ~2 folds because it was multi-hour. The reported RGB
  numbers use **8 frames / 15 epochs**, which trains reliably (~90 s/fold) but
  is a lighter model; a full-length run might move a few points but is very
  unlikely to flip a ~0.12 accuracy gap.
* **Full-frame 112×112 shrinks the players** to ~15 px, so the "opponent
  lunged and missed" cue the hypothesis relied on is barely resolved. A
  court/player crop is the most promising next step if this is revisited.

### Modality ablation (which fusion helped)

Adding player-motion features gave the best RGB overall accuracy/macro-F1
(rgb+heat+player: 0.494 / 0.490 pooled on all 251) but did **not** improve
landing recall; the shuttle-heatmap channel alone *hurt* landing recall
(0.361). So no fusion input rescued the pixel model — the signal is weak
across the board, consistent with the data-scale and player-resolution limits.

## Data quirks handled (verified on disk)

* **Frame alignment:** every video's frame count == its CSV max frame + 1; the
  `_Rev` variants are the aligned ones. 30 fps, 1920×1080.
* **Mixed coordinate spaces (not in the original brief):** player detections
  are always 1280×720, but shuttle tracks are 1280×720 for Test1/3/6/7 and
  **1920×1080 for Test2/Test4**. Each match's spaces are detected empirically
  and normalised per-match (this was silently wrong for Test2/Test4 in the
  first trajectory run).
* **NaN player detections** sanitised (forward/back-fill + assert no NaN/Inf).
* **Labels** normalised to 3 canonical classes (case-insensitive substrings).
* **End_Frame** from `_T4` when it aligns 1:1 with GT rows, else
  `round(end_time*30)`; 1.3 s window absorbs the coarse end frame on Test2/4.
* **No test-label peeking:** epoch selection uses an inner **validation match**
  (one match held out from the training set) on macro-F1; the test match is
  scored once.

## Dataset (all 251 rallies)

| match | rallies | net | out | landing | video |
|---|---|---|---|---|---|
| Test1 | 36 | 17 | 11 | 8  | Test1_Full_rev.mp4 (in project) |
| Test2 | 75 | 21 | 32 | 22 | Downloads/Test2_Full_Rev.mp4 |
| Test3 | 22 | 5  | 12 | 5  | Downloads/Test3_Full_Rev.mp4 |
| Test4 | 45 | 15 | 16 | 14 | Downloads/Test4_Full_Rev.mp4 |
| Test6 | 42 | 12 | 16 | 14 | Downloads/Test6_Full.mp4 |
| Test7 | 31 | 8  | 14 | 9  | Downloads/Test7_Full.mp4 |
| **Total** | **251** | **78** | **101** | **72** | |

Geometric-baseline comparison uses only Test1/3/6/7 (131 rallies) — Test2/Test4
have no `court.json`.

## Files

| file | role |
|---|---|
| `build_dataset.py` / `model.py` / `train.py` / `evaluate.py` | trajectory model (coordinates) |
| `build_clip_dataset.py` | video → cached RGB clip + heatmap + player-feature tensors (`clips/`) |
| `clip_model.py` | r2plus1d_18, 2 heads, 4-ch stem inflation, optional player MLP |
| `train_clip.py` | leave-one-match-out CV; inner-val macro-F1 selection; focal + oversample + aug; `--frames` subsample; `--final` deployable model |
| `evaluate_clip.py` | per-class metrics, confusion, baseline head-to-head, modality ablation |
| `infer.py` | `classify_rally_end_cnn(...)` — dispatches trajectory vs RGB clip model |
| `README.md` | this file |

## Reproduce

```bash
cd new_VERSION_1
python analysis/cnn_rally_end/build_clip_dataset.py            # ~20 min, reads videos in place
python analysis/cnn_rally_end/train_clip.py --modality rgb_heat_player --epochs 15 --frames 8
python analysis/cnn_rally_end/train_clip.py --modality rgb              --epochs 15 --frames 8
python analysis/cnn_rally_end/train_clip.py --modality rgb_heat         --epochs 15 --frames 8
python analysis/cnn_rally_end/evaluate_clip.py
python analysis/cnn_rally_end/train_clip.py --modality rgb_heat_player --epochs 15 --frames 8 --final
```

## Integration contract (unchanged)

```python
from analysis.cnn_rally_end.infer import load_clip_model, classify_rally_end_cnn
model = load_clip_model()   # models/clip_rally_end_final.pt
event, side, confidence = classify_rally_end_cnn(
    video_path, end_frame, fps, shuttle_df, player_df, court_corners, H, model)
# event ∈ {hits_net, out_of_bounds, wins_by_landing, unknown}
# side  ∈ {near, far};  confidence ∈ {HIGH, MEDIUM, LOW}
```

The same wrapper serves the trajectory model (`load_model()`) too and
dispatches on model type. **Not enabled in the pipeline** — it loses to the
geometric baseline (see headline). Deployable model is provided only to keep
the contract runnable.
```
