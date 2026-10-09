# Pipeline Documentation — Overview

This is the technical reference for the full badminton video analysis pipeline:
raw video in, winner + win-reason + PDF report out, with a human review step in
between. Each stage has its own doc file; this page explains how they fit
together, the two run modes, and where to look for what.

## Contents

| File | Stage(s) | What it covers |
|---|---|---|
| [01_video_preprocessing_and_court_setup.md](01_video_preprocessing_and_court_setup.md) | 0, 2 | Codec/resolution normalization, manual + automatic court/net annotation, the temporal-stability reference-frame picker |
| [02_court_presence_and_segmentation.md](02_court_presence_and_segmentation.md) | 2b–2e | Broadcast-mode only: detecting which time ranges show the real court, cutting/stitching segments |
| [03_shuttle_tracking.md](03_shuttle_tracking.md) | 0–1, 4 | TrackNetV3 shuttle detection, the 3-filter trajectory cleaner, gap-filling |
| [04_player_detection.md](04_player_detection.md) | 3 | YOLO11 player detection + court-boundary filtering |
| [05_rally_detection.md](05_rally_detection.md) | 5 | Segmenting the cleaned shuttle trajectory into individual rallies |
| [06_win_prediction.md](06_win_prediction.md) | 6 | Rule engine + CNN ensemble + trajectory Random Forest → winner, win-reason, score |
| [07_fusion_commentary_pdf.md](07_fusion_commentary_pdf.md) | 6 (cont.) | Merging with the shot classifier, deterministic stats summary, LLM commentary, PDF report |
| [08_verification_video.md](08_verification_video.md) | 7 | The combined court+net+player+shuttle annotated video, rally-detected markers |
| [09_web_review_app.md](09_web_review_app.md) | — | The Flask + vanilla-JS app: upload → watch it process → review/correct → save |

## The two run modes

Everything is orchestrated by `run_full_pipeline.py`. It has two modes,
chosen by `--broadcast`:

**Default (pre-trimmed clip)** — assumes the whole input video is rally
footage, no intro/crowd/replay cutaways. Runs shuttle detection and player
detection on the *entire* video, once each.

```
preprocess → [0] shuttle detect → [1] filter trajectory → [2] court+net
→ [3] player detect → [4] gap-fill → [5] rally segment → [6] win predict
+ fusion + PDF → [7] verification video
```

**`--broadcast`** — for a full match broadcast where the camera cuts away to
intro graphics, crowd shots, replays, and coach close-ups between rallies.
Running shuttle/player detection on the *whole* video would waste most of
the compute on footage that isn't even the match. Instead:

```
preprocess → [2] court+net (wide-search reference frame)
→ [2b] court-presence scan → [2c] extract court-present segments
→ [2d] per-segment: shuttle detect + filter + player detect
→ [2e] stitch segments back into one global timeline
→ [4] gap-fill → [5] rally segment (gated by court-presence too)
→ [6] win predict + fusion + PDF → [7] verification video
```

The step numbers above (`0/7`, `2b/7`, etc.) are exactly what
`run_full_pipeline.py` prints to stdout for each stage — useful for
matching a log line back to the code that produced it, and it's what the
web review app's progress parser watches for (see
[09_web_review_app.md](09_web_review_app.md)).

Every stage checks whether its output file already exists and skips itself
if so — a failed or interrupted run can just be re-invoked with the same
`--match_name` and it picks up where it left off, without redoing finished
work.

## Where output lives

Everything for one match lands in a single folder, `<match_name>/`, at the
repo root (`pipeline_release/<match_name>/`):

```
<match_name>/
  <match_name>.mp4                     preprocessed input video
  <match_name>_court.json              court corners + net position
  <match_name>_court_presence.csv      per-frame court-visible signal (broadcast mode only)
  <match_name>_ball_filled.csv         final shuttle trajectory (gap-filled)
  player_detections.csv                player positions per frame
  <match_name>_rally.csv               rally start/end frames
  win_predictions.csv                  per-rally winner/reason/score (the core output)
  <match_name>_annotated.mp4           verification video
  segments/                            broadcast mode only: per-segment clips + intermediate CSVs
  unified/
    merged_analysis.csv                win_predictions + shot classifier merged
    badminton_analysis_enhanced.csv    fixed 8-column schema for the BadmintonAnalysis viewer
    analysis_report.txt                deterministic stats + AI commentary
    <players>_badminton_highlights_<timestamp>.pdf
  corrections.json                     human review edits (web app only; never overwrites the above)
```

## Design threads that run through every stage

A few decisions repeat across multiple files, worth knowing up front rather
than re-explaining in each doc:

- **Homography, not raw pixels, for anything "real-world."** Court corners
  define an image→metres transform (`cv2.findHomography` /
  `cv2.getPerspectiveTransform`, singles court = 5.18m × 13.4m). Boundary
  checks, the trajectory RF's `margin_cm` feature, and the court-presence
  geometric check all go through this rather than comparing raw pixel
  coordinates, because pixel distance means something different depending on
  where on the court you are (perspective).
- **A homography only correctly maps points on the plane it was built
  from.** The court corners are on the ground; the shuttle is airborne for
  almost its whole trajectory. Transforming a mid-flight pixel position
  through the ground homography gives a real but *wrong* answer — where a
  ground-level point at that pixel would be, not where the actual 3D shuttle
  is. Every place this matters (fault-side detection, the RF's landing
  features) deliberately uses positions near actual ground contact, not
  arbitrary in-flight frames.
- **Cheap gate before expensive check, everywhere there's a two-stage
  filter.** Court presence checks green-fraction before running homography
  verification; win prediction checks CNN confidence before running the RF;
  gap-filling checks a scene mask before computing interpolation. The
  pattern shows up because it's usually 10-100x cheaper to reject on the
  first signal than to always run the expensive one.
- **Self-consistency over absolute precision when the reference is
  uncertain.** The court-presence homography check calibrates against the
  *same* detector's output on the reference frame, not hand-clicked
  ground-truth corners — a raw contour-blob detector and a human click
  disagree systematically even on the identical frame, so comparing
  detector-to-detector (not detector-to-click) is what actually measures
  "did the camera move," not "how sloppy is the detector."
- **Everything that touches a video file re-validates it first.**
  `video_utils.ensure_preprocessed()` — codec, resolution, fps — because
  `cv2.VideoCapture` silently fails to decode some real-world inputs (AV1 in
  particular) with no exception, just `.read()` returning `False` forever,
  which otherwise surfaces as a confusing unrelated error far from the real
  cause.
