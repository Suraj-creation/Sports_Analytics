# Automatic Court & Net Keypoint Detection

This document explains the full pipeline for automatically detecting the
badminton **court corners** and **net** in any match video — from manual
ground-truth annotation, through dataset building and model training, to
testing on unseen videos and running inference on new footage.

---

## 1. Why this exists

The rally-analysis pipeline (player tracking, shuttle tracking, in/out
detection, win/lose reasoning) needs to know **where the court boundaries
and net are** in pixel coordinates for each video.

Previously this required **manually clicking 8 points once per video**
and hardcoding the result. That breaks whenever:
- A new video has a different camera angle/zoom
- You get new footage and have to re-annotate from scratch

**Goal:** train a model that detects these 8 points automatically from any
frame, so new videos work without manual setup.

---

## 2. The 8 keypoints

| Code | Meaning |
|---|---|
| TL | Top-Left court corner |
| TR | Top-Right court corner |
| BR | Bottom-Right court corner |
| BL | Bottom-Left court corner |
| NL | Net post base, left (ground level) |
| NR | Net post base, right (ground level) |
| CL | Net cable/tape top, left |
| CR | Net cable/tape top, right |

These define the full court rectangle and net plane. Everything
downstream (in/out detection, net-touch detection) is computed
geometrically from these 8 points.

---

## 3. Step 1 — Manual ground-truth annotation

**Script:** `analysis/annotate_court.py` (run locally, opens a GUI window)

For each source video, the camera is static for the whole match, so **one
annotation per video** is enough.

```powershell
python analysis/annotate_court.py --video dataset/Test1_Full_rev.mp4 --out dataset/Test1_Full_rev_court.json
```

A window opens on frame 90 of the video. Click the 8 points **in this
order** (on-screen instructions guide you):

1. TL — top-left court corner
2. TR — top-right court corner
3. BR — bottom-right court corner
4. BL — bottom-left court corner
5. NL — left net post base (ground)
6. NR — right net post base (ground)
7. CL — left net cable top
8. CR — right net cable top

Keys: `z` = undo, `r` = reset, `s`/Enter = save & exit, `q`/Esc = quit
without saving.

This was done for **5 training videos**: Test1, Test2, Test3, Test6, Test7
→ produces `dataset/<video>_court.json` files with pixel coordinates.

---

## 4. Step 2 — Building the training dataset

**Script:** `analysis/build_court_dataset.py`

```bash
python analysis/build_court_dataset.py
```

What it does, per video:
1. Samples **80 frames evenly** across the video (skips first/last 1% to
   avoid black/transition frames)
2. Saves each frame as a `.jpg`
3. Since the camera is static, applies the **same 8-point annotation** to
   every sampled frame from that video, writing a YOLO-pose label `.txt`
4. Splits each video's 80 frames into **train/val (85/15)**

**Result:** 5 videos × 80 frames = **400 images** → 340 train + 60 val.

**Label format (YOLO-pose)**, one line per image:
```
class_id  bbox_cx bbox_cy bbox_w bbox_h   x1 y1 v1  x2 y2 v2 ... x8 y8 v8
```
All values normalized 0-1. `class_id=0` ("court" — single class).
`bbox` = bounding box around all 8 points + padding. `v=2` = visible.

**Why this works:** because the camera doesn't move, one click-through
gives 80 different-looking training images (different rally moments,
players, lighting) for free — far cheaper than per-frame annotation, while
still giving the model variety.

Output: `court_dataset/images/{train,val}/`, `court_dataset/labels/{train,val}/`,
`court_dataset/data.yaml`.

> **Note:** `build_court_dataset.py` writes an *absolute* `path:` in
> `data.yaml` (your local Windows path). Before sending to a Linux server,
> edit `data.yaml` and change the `path:` line to `path: .`

---

## 5. Step 3 — Model: YOLOv8-pose

**Model:** `yolov8n-pose.pt` (Ultralytics, "nano" — smallest variant)

- YOLO-pose normally detects humans + body keypoints (elbows, knees, etc).
  Architecture is generic: detect an object's bounding box + N keypoints.
- Here "the object" = the court, "keypoints" = our 8 court/net points.
- **Why nano?** Small dataset (400 images), rigid/simple shape (a court
  doesn't deform) → small model trains fast without overfitting, and is
  fast enough for real-time use later.

`data.yaml`:
```yaml
path: .
train: images/train
val: images/val
kpt_shape: [8, 3]
names:
  0: court
```

---

## 6. Step 4 — Training

**Script:** `train_court_model.py`

```bash
python3 train_court_model.py --device 0
```

- Loads pretrained `yolov8n-pose.pt` (pretrained on COCO human-pose — gives
  a head start on "detect object + keypoints" in general)
- Fine-tunes on the 340 train images for 100 epochs, validates on 60
- Runs on GPU (GTX 1080 Ti) — **~10-25 minutes**

Useful flags:
```bash
python3 train_court_model.py --device 0 --epochs 150
python3 train_court_model.py --device 0 --model yolov8s-pose.pt --epochs 150
python3 train_court_model.py --device cpu --epochs 50 --imgsz 480   # no GPU
```

**Outputs** (in `runs/pose/court_dataset/`):
- `weights/best.pt` — trained model (use this for inference)
- `weights/last.pt` — last epoch checkpoint
- `results.csv` / `results.png` — training curves (loss ↓, mAP ↑ per epoch)

**Key metric:** `metrics/mAP50(P)` — mean Average Precision for pose
keypoints at IoU 0.5. Closer to 1.0 = better. >0.9 is very good for this
kind of static-camera dataset.

---

## 7. Step 5 — Testing on UNSEEN videos (the real validation)

**Why this matters:** the val set (60 images) comes from the **same 5
camera angles** as training — just different frames. A model could score
high on val by memorizing *"this looks like Test1's camera → output
Test1's fixed 8 points"* for 5 known angles, without learning to actually
detect court lines/net visually. That wouldn't generalize to new footage.

**The real test:** run the trained model on videos **never seen during
training** — e.g. `Test4_Full_Rev.mp4`, `Test_set_CA1.mp4`,
`TestcaseCA2.mp4` (different camera angles/zooms/resolutions).

**Script:** `court_test_model.py` (created in `court_dataset/court_dataset/`
on the server) — loads `best.pt`, runs on one frame, prints the 8 predicted
`(x, y)` + confidence, and saves a visualization image with:
- green polygon = court corners (TL/TR/BR/BL)
- red line = net base (NL-NR)
- orange line = net cable top (CL-CR)

```bash
cd ~/Badminton-Video-Analysis/court_dataset/court_dataset
BEST=$(find runs -name best.pt | head -1)

mkdir -p court_test_results
for v in Test_set_CA1 Test4_Full_Rev TestcaseCA2; do
  python3 court_test_model.py --video ../../video_raw/${v}.mp4 --model "$BEST" --frame 1000 --out court_test_results/${v}_f1000.jpg
done
```

Pull images to view locally:
```powershell
scp -r administrator@192.168.0.99:~/Badminton-Video-Analysis/court_dataset/court_dataset/court_test_results .
```

### Results obtained (retrained model, 100 epochs)

| Video | Confidence range | Notes |
|---|---|---|
| Test_set_CA1 | 0.995 – 1.000 | Stable across frames 500/1500 (≤3px drift) |
| Test4_Full_Rev | 0.987 – 1.000 | Stable across frames 1500/3000 (≤2px drift) |
| TestcaseCA2 | 0.988 – 1.000 | Different resolution/camera, still high confidence |

**Conclusions:**
1. **Confidence is very high (>0.98)** on all 3 unseen videos.
2. **Stable across frames** — same point moves only 1-3px between distant
   frames of the same (static-camera) video, confirming predictions aren't
   noisy.
3. **Geometrically sensible** — TL/TR above BL/BR, net points between left
   and right edges, forming a realistic court+net shape.
4. **Adapts to each video's actual framing** (different coordinate ranges
   per video) rather than repeating one of the 5 training videos' fixed
   coordinates → evidence of real generalization, not memorization.

---

## 8. Running on a NEW video (production use)

**Script:** `auto_annotate_court.py` (in `court_dataset/court_dataset/`)

Automatically produces a `court_annotation.json` for a new video — **no
manual clicking** — in the same format `annotate_court.py` produces, so it
plugs directly into the rest of the pipeline (`extract_features.py
--annotation ...`, etc.).

How it works:
1. Samples 15 frames spread across the new video
2. Runs the trained model on each, skipping any frame where any keypoint
   confidence < 0.5
3. Takes the **median** of each of the 8 keypoints across all confident
   detections (robust to any single bad/occluded frame)
4. Writes `<video_name>_court.json`

```bash
cd ~/Badminton-Video-Analysis/court_dataset/court_dataset
BEST=$(find runs -name best.pt | head -1)

python3 auto_annotate_court.py --video ../../video_raw/NewVideo.mp4 --model "$BEST"
```

---

## 9. Folder layout summary

```
Badminton-Video-Analysis/
├── video_raw/                          <- all videos (shared across project)
│   ├── Test1_Full_rev.mp4 ... Test7_Full.mp4
│   ├── Test4_Full_Rev.mp4, Test_set_CA1.mp4, TestcaseCA2.mp4  (unseen test videos)
└── court_dataset/
    └── court_dataset/                  <- everything for this sub-project
        ├── data.yaml
        ├── images/{train,val}/         (340 + 60 images)
        ├── labels/{train,val}/         (YOLO-pose .txt labels)
        ├── train_court_model.py
        ├── court_test_model.py         (visualize predictions)
        ├── auto_annotate_court.py       (auto-generate court_annotation.json)
        ├── runs/pose/court_dataset/
        │   ├── weights/best.pt          <- trained model
        │   └── results.csv / results.png
        └── court_test_results/          (output visualization images)
```

---

## 10. End-to-end command reference

```bash
# 1. (local, GUI) re-annotate ground truth for the 5 training videos
python analysis/annotate_court.py --video dataset/Test1_Full_rev.mp4 --out dataset/Test1_Full_rev_court.json
# ... repeat for Test2, Test3, Test6, Test7

# 2. (local) rebuild the dataset from annotations
python analysis/build_court_dataset.py
# fix data.yaml path: -> "path: ."

# 3. transfer to GPU server
scp -r court_dataset administrator@192.168.0.99:/home/administrator/Badminton-Video-Analysis/

# 4. (server) train
cd ~/Badminton-Video-Analysis/court_dataset/court_dataset
python3 train_court_model.py --device 0

# 5. (server) test on unseen videos
BEST=$(find runs -name best.pt | head -1)
python3 court_test_model.py --video ../../video_raw/Test4_Full_Rev.mp4 --model "$BEST" --frame 1000 --out court_test_results/test4.jpg

# 6. (server) auto-annotate any new video
python3 auto_annotate_court.py --video ../../video_raw/NewVideo.mp4 --model "$BEST"
```
