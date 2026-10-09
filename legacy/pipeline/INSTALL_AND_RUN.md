# Badminton Analysis Pipeline — Installation & Quick Start

## What's Included

- **TrackNetV3/** — Shuttle detection (`predict.py`), noise filtering
  (`filter_trajectory.py`), gap-filling (`fill_gaps.py`)
  - Trained TrackNet checkpoint at `ckpts/TrackNet_best.pt`
- **analysis/** — Player detection, court/net annotation, rally detection,
  feature extraction, shot classification (rule-based)
- **win_predictor/** — Stage 7 winner/reason prediction (CNN ensemble + rule
  engine + trajectory RF meta-learner)
  - Trained r2plus1d_18 models (20-frame and 16-frame) and RF classifier
- **BadmintonAnalysis/** — Streamlit UI, PDF report generator, player knowledge base
- **fusion_layer.py** — Merges Stage 7 predictions with shot classifier output
- **run_full_pipeline.py** — True end-to-end orchestrator: raw video in, PDF report out (all preprocessing + Stage 7 -> fusion -> commentary -> PDF)
- **run_unified_pipeline.py** — Stage 7 -> fusion -> commentary -> PDF only (needs already-preprocessed match data)
- **Test1_Full_rev/** — Example match (shuttle trajectory CSVs, court geometry)

## System Requirements

- **Python 3.10+**
- **pip** package manager
- **~2.9 GB free disk space** (includes trained CNN + TrackNet models)
- **GPU strongly recommended** for TrackNetV3 shuttle detection (CPU works but is slow, minutes per match)
- **LM Studio** (optional, for AI match commentary; local Phi-3 inference)

## Installation

### Step 1: Set Up Python Environment

```bash
# Navigate to the extracted pipeline folder
cd badminton-pipeline

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Python Dependencies

```bash
pip install --upgrade pip

# Core dependencies
pip install pandas numpy opencv-python torch torchvision scikit-learn reportlab joblib

# TrackNetV3 shuttle detection (TrackNetV3/predict.py, filter_trajectory.py, fill_gaps.py)
pip install tqdm parse pycocotools

# Player detection (analysis/player_detection.py)
pip install ultralytics shapely

# Streamlit + LangChain (UI + LLM features)
pip install streamlit langchain langchain-community langchain-openai langchain-huggingface
pip install faiss-cpu sentence-transformers langgraph pyttsx3

# Networking (for LM Studio communication)
pip install requests
```

### Step 3: (Optional) Set Up LM Studio for AI Commentary

If you want **automated match summaries**, install LM Studio:

1. Download: https://lmstudio.ai
2. Open LM Studio, search for: **`Phi-3.1-mini-128k-instruct`**
3. Load the model (one-time, ~4 GB download)
4. Start the local server on **port 1234** (default, visible in the app)

**If LM Studio is offline:** The pipeline automatically falls back to a deterministic, stats-based summary (equally accurate, less narrative).

### Step 4: Verify Test Data

```bash
# Check that example match files exist
ls Test1_Full_rev/

# Should show:
# - Test1_Full_rev_ball_filled.csv (shuttle trajectory)
# - Test1_Full_rev_rally.csv (rally start/end frames -- what win_predictor reads)
# - Test1_Full_rev_court.json (court geometry)
# - player_detections.csv (player bounding boxes)
```

## Running the Pipeline

### Option A: Raw Video In, Report Out (Recommended)

`run_full_pipeline.py` chains every stage -- TrackNetV3 shuttle detection,
noise filtering, gap-filling, player detection, court/net geometry, rally
segmentation, Stage 7 win prediction, fusion, AI commentary, PDF -- in one
call. Each stage is skipped on re-run if its output file already exists, so
an interrupted run just picks back up.

```bash
python run_full_pipeline.py \
  --video /path/to/YourMatch.mp4 \
  --player_a "Player A Name" \
  --player_b "Player B Name"
```

By default this uses zero-click automatic court/net detection
(`--court_mode auto --court_type singles`), which snaps to the actual
painted white boundary lines (not just the green floor extent) and picks
the singles sideline specifically -- badminton courts paint both the
doubles and, 0.46m inside it, the singles sideline, so "outermost white
line" alone is the wrong one for a singles match. On our test video this
landed within ~3-16px of a manual annotation (net_Y off by 3px). It can
still fail on courts where the two sidelines aren't both cleanly visible
(occlusion, unusual camera angle) -- it prints a warning and falls back to
the cruder green-mask corners when it can't confidently tell singles from
doubles. Use `--court_type doubles` for doubles matches. For the exact
accuracy this pipeline is benchmarked at (81.8% win-reason / ~69% winner),
or if auto mode's fallback warning fires, annotate the court once per
camera angle instead:

```bash
python run_full_pipeline.py \
  --video /path/to/YourMatch.mp4 \
  --player_a "Player A Name" \
  --player_b "Player B Name" \
  --court_mode manual
```

`--width`/`--height` (default 1280x720) must match your video's actual
resolution. Run `python run_full_pipeline.py --help` for all options
(`--match_name`, `--player_model`).

**Outputs** land in `<match_name>/unified/`:
- `badminton_analysis_enhanced.csv` — Uploadable to Streamlit UI
- `analysis_report.txt` — Match summary (AI or deterministic)
- `*_highlights_*.pdf` — Match highlights PDF with top-5 rallies

### Option A2: Already-Preprocessed Match Data

If a match folder already has `<name>_ball_filled.csv`, `<name>_rally.csv`,
`<name>_court.json` and `player_detections.csv` (e.g. the bundled
`Test1_Full_rev/`), skip straight to Stage 7 + fusion + commentary + PDF:

```bash
python run_unified_pipeline.py \
  --match_folder Test1_Full_rev \
  --player_a "AN Se Young" \
  --player_b "Ratchanok Intanon"
```

### Option B: Interactive Streamlit UI

Explore the match data with a web interface:

```bash
cd BadmintonAnalysis
python -m streamlit run src/app.py
```

Then:
1. Open http://localhost:8501 in your browser
2. Upload `Test1_Full_rev/unified/badminton_analysis_enhanced.csv`
3. Enter player names
4. Choose analysis mode:
   - **Match Summary** — AI-generated narrative
   - **Highlights** — Longest/most intense rallies
   - **Q&A** — Ask free-form questions about the match

## How the Pipeline Works

```
Video Analysis Sequence
========================
0. Shuttle Detection (TrackNetV3/predict.py) -- bundled, uses ckpts/TrackNet_best.pt
   └─> Raw shuttle trajectory: output_shuttle/YourMatch_ball.csv

1. Noise Filtering (TrackNetV3/filter_trajectory.py) -- removes spike/teleport
   and post-smash fake detections BEFORE gap-filling
   └─> Output: output_shuttle/YourMatch_ball_clean.csv

2. Gap-Fill (TrackNetV3/fill_gaps.py) -- required, win_predictor and
   detect_rallies.py both need the gap-filled track
   └─> Output: YourMatch/YourMatch_ball_filled.csv

3. Player Detection (analysis/player_detection.py) -- optional but improves
   winner fault-side accuracy, and feeds fill_gaps'/detect_rallies' scene mask
   └─> YOLO11 person detection, filtered to a court polygon
   └─> Output: YourMatch/player_detections.csv (player_1_x/y/conf, player_2_x/y/conf)

4. Court + Net Annotation (analysis/annotate_court.py) -- required by Stage 7
   └─> Browser-based: click 8 points (4 court corners + net ground + net
       cable), once per camera angle
   └─> Output: YourMatch/YourMatch_court.json (corners + net_Y/net_top_Y)

5. Rally Segmentation (analysis/detect_rallies.py)
   └─> Output: YourMatch/YourMatch_rally.csv (Start_Frame, End_Frame)

6. Stage 7 (win_predictor/predict.py, run automatically by run_unified_pipeline.py)
   └─> CNN ensemble (r2plus1d_18 20f + 16f) + rule engine + trajectory RF
   └─> Output: winner, win_reason, fault_side, cnn_confidence
   └─> YourMatch/win_predictions.csv

7. Shot Classifier (analysis/extract_features.py) -- optional, only adds
   ball_types; Stage 7 is the canonical source for winner/win_reason
   └─> Rule-based shot type detection (drop, smash, clear, push, etc.)
   └─> Output: *_extended_v3.csv

8. Fusion Layer (fusion_layer.py)
   └─> Merges Stage 7 + shot classifier
   └─> Output: merged_analysis.csv, badminton_analysis_enhanced.csv

9. LLM Commentary (Phi-3 via LM Studio)
   └─> Narrative match summary (or deterministic fallback)
   └─> Output: analysis_report.txt

10. PDF Report (BadmintonAnalysis)
   └─> Top-5 highlights + commentary
   └─> Output: *_highlights_*.pdf
```

Steps 6-10 run automatically inside a single `run_unified_pipeline.py` call.
Steps 0-5 (getting from a raw video to `YourMatch_ball_filled.csv`,
`player_detections.csv`, `YourMatch_court.json` and `YourMatch_rally.csv`)
are separate, run-once-per-match preprocessing -- see below.

## Using Your Own Match

`run_full_pipeline.py` (Option A above) automates everything below in one
call and is the recommended path. The manual, step-by-step version here is
for debugging a specific stage or customizing a flag `run_full_pipeline.py`
doesn't expose (e.g. `filter_trajectory.py`'s speed thresholds).

Starting from just a raw video `YourMatch/YourMatch.mp4`:

```bash
# 0. Shuttle detection
python TrackNetV3/predict.py \
  --video_file YourMatch/YourMatch.mp4 \
  --tracknet_file ckpts/TrackNet_best.pt \
  --save_dir output_shuttle

# 1. Filter fake detections (spikes, post-smash misfires) BEFORE gap-filling
python TrackNetV3/filter_trajectory.py \
  --input  output_shuttle/YourMatch_ball.csv \
  --output output_shuttle/YourMatch_ball_clean.csv \
  --video_width 1280 --video_height 720   # match your video's resolution

# 2. Gap-fill the cleaned shuttle track
python TrackNetV3/fill_gaps.py \
  --input  output_shuttle/YourMatch_ball_clean.csv \
  --output YourMatch/YourMatch_ball_filled.csv \
  --player_csv YourMatch/player_detections.csv \
  --video_width 1280 --video_height 720   # same resolution as above

# 3. Player detection (run before step 2 if you want fill_gaps' scene-mask
#    gating; only the CSV path needs to exist by the time fill_gaps runs)
python analysis/player_detection.py \
  --match_folder YourMatch \
  --video YourMatch/YourMatch.mp4 \
  --court_file court.json      # simple 4-corner court_utils JSON;
                                # omit to annotate manually on first run

# 4. Court + net annotation for Stage 7 (different, richer format than
#    step 3's court.json -- includes net position). Browser-based: this
#    starts a local server and prints a URL -- open it, click the 8 points
#    (TL, TR, BR, BL court corners; NL, NR net-post ground points; CL, CR
#    net-cable-top points), hit Save, then Ctrl+C the server.
python analysis/annotate_court.py \
  --video YourMatch/YourMatch.mp4 \
  --out   YourMatch/YourMatch_court.json
#   -> open http://localhost:5050  (use --port to change it, or SSH-forward
#      it with `ssh -L 5050:localhost:5050 ...` if running on a remote box)

# 5. Rally segmentation
python analysis/detect_rallies.py --match_folder YourMatch
```

Click the **singles** sideline, not the doubles sideline, if that's what the
match is (badminton courts paint both -- the singles line sits ~0.46m
inside the doubles line). `--court_mode auto` (see Option A) tries to find
this line automatically via `analysis/auto_court.py`, but it can pick the
wrong one on a camera angle where both sidelines aren't clearly resolved;
manual annotation is the reliable fallback whenever that happens.

`--video_width`/`--video_height` must match the actual resolution of
`YourMatch.mp4` -- the win_predictor README assumes 1280x720; TrackNetV3
itself works at any resolution, just keep the flags consistent across
steps 1 and 2.

This leaves `YourMatch/` with `YourMatch_ball_filled.csv`,
`player_detections.csv`, `YourMatch_court.json` and `YourMatch_rally.csv` --
everything `win_predictor/predict.py` requires. Then run the main pipeline:

```bash
python run_unified_pipeline.py \
  --match_folder YourMatch \
  --player_a "Player A Name" \
  --player_b "Player B Name"
```

The pipeline auto-generates `YourMatch/unified/` with all outputs.

## Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'win_predictor'` | Ensure `win_predictor/` folder is in the same directory as `run_unified_pipeline.py` |
| `ModuleNotFoundError: No module named 'analysis'` | Ensure `analysis/` folder exists; check relative paths in scripts |
| `ERROR: missing required file: ..._rally.csv` | `win_predictor/predict.py` needs `<name>_rally.csv` in the match folder (same Start_Frame/End_Frame columns `detect_rallies.py` writes) -- run `analysis/detect_rallies.py --match_folder ...`, or rename an existing `_T.csv` if you already have one |
| `LM Studio unavailable` | Normal; pipeline falls back to deterministic summary. Start LM Studio on port 1234 to enable AI commentary |
| `Streamlit: Connection refused at localhost:8501` | Ensure you're running streamlit in a terminal on *this* machine (not remotely). Check that no other app uses port 8501 |
| `CUDA out of memory` | Reduce batch sizes in `win_predictor/config.py`, or run on CPU (slower but works) |
| `ModuleNotFoundError: No module named 'ultralytics'` / `'shapely'` | `pip install ultralytics shapely` (needed by `analysis/player_detection.py`) |
| `ModuleNotFoundError: No module named 'pycocotools'` / `'parse'` / `'tqdm'` | `pip install pycocotools parse tqdm` (needed by `TrackNetV3/predict.py`; `pycocotools` is a transitive import of `test.py`, unused at inference time but still required to import it) |
| `TrackNetV3/predict.py` runs but very slowly | No GPU detected -- it falls back to CPU automatically (`torch.cuda.is_available()`); expect several minutes per match on CPU |
| `analysis/player_detection.py` opens a manual-annotation window | No `--court_file` given (or the file doesn't exist yet) -- click the 4 court corners once, or pass an existing `court_utils`-format court JSON |

## Configuration (Advanced)

### Adjust AI Commentary Temperature

Edit `run_unified_pipeline.py`, line ~232:

```python
"temperature": 0.2,  # Lower = more factual; higher = more creative
```

### Disable LLM, Always Use Stats Summary

Edit `run_unified_pipeline.py`, line ~190:

```python
# factual_core = stats_summary(df, player_a, player_b)
# return factual_core, "STATS-VERIFIED"  # Uncomment to force stats mode
```

### Customize Player Bios

Edit `BadmintonAnalysis/input/badminton/` text files to add player background context. Phi-3 uses these for tone and accuracy.

## Architecture Notes

- **TrackNetV3 coordinate space**: All shuttle CSVs must be in **1280×720** pixels (not 1920×1080)
- **Player convention**: FAR=top of frame (Player A), NEAR=bottom (Player B)
- **Win-reason vocab**: "opponent goes out of bounds", "opponent hits the net", "wins_by_landing"
- **CNN models**: Trained on vk15b_dataset with leave-one-out CV; Test1 accuracy ~73% event detection, 75% net-hit recall, 56% winner

## Next Steps

1. **Run TrackNetV3** on your own match video (bundled, see "Using Your Own Match" above)
2. **Preprocess** through filter/gap-fill/player-detection/court-annotation/rally-detection
3. **Run the pipeline** on your match
4. **Adjust hyperparameters** as needed (thresholds in `analysis/extract_features.py`)
5. **Provide feedback** on shot classification and winner accuracy

## Support

For questions about specific modules:
- **Shuttle detection / filtering / gap-fill** → `TrackNetV3/predict.py`, `TrackNetV3/filter_trajectory.py`, `TrackNetV3/fill_gaps.py` (`--help` for CLI options; `TrackNetV3/README.md` for the model itself)
- **Player detection** → `analysis/player_detection.py` (`--help` for CLI options)
- **Shot classification** → `analysis/extract_features.py` docstring
- **CNN predictions** → `win_predictor/predict.py` docstring
- **Fusion logic** → `fusion_layer.py` docstring
- **Full pipeline orchestration** → `run_full_pipeline.py` docstring (`--help` for CLI options)
- **UI features** → `BadomintonAnalysis/src/app.py` docstring

---

**Happy analyzing!** 🏸
