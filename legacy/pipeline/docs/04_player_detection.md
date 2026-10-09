# Stage 3 — Player Detection

File: `analysis/player_detection.py`.

**Input:** the video + (optionally) `court.json`.
**Output:** `player_detections.csv` — `frame_no, player_1_x, player_1_y,
player_1_conf, player_2_x, player_2_y, player_2_conf` — plus a matching
`.json` with full bounding-box detail, and (unless `--no_video`) an
annotated `detection_output.mp4`.

This is the schema every later stage expects
(`win_predictor/predict.py`, `rule_engine.py`,
`TrackNetV3/fill_gaps.py`'s scene mask, `detect_rallies.py`'s scene mask)
— any replacement detector has to produce exactly these column names to
slot in.

## How it works

**Detection** (`PersonDetector`): YOLO11 (`ultralytics.YOLO`, default
weights `yolo11x.pt` — the largest/most accurate variant; smaller
`yolo11n/s/m/l.pt` trade accuracy for speed), restricted to the `person`
class (`classes=[0]`), confidence threshold `0.4`.

**Court filtering** (`DetectionFilter`): three checks per detection —
confidence `>= min_conf` (0.4), bounding-box height `>= min_height` (60px
— filters out small/distant false positives like a linesperson or ball boy
in the background), and the box's **bottom-center point** (not its
centroid) falls inside the court polygon. Bottom-center is deliberate — it
approximates where a standing person's feet touch the ground, which is
the meaningful "is this player on the court" test; a bounding box's
geometric center is higher up (torso height) and would misjudge players
near the court edge.

**Court source**: `--court_file` (the same `court.json` every other stage
uses, rescaled to the video's actual resolution via `court_utils`), or
`--no_court_filter` (keep every YOLO person detection unconditionally —
needed for non-interactive/scripted runs where no court file exists yet),
or (neither given) an interactive OpenCV window opens for manual 4-point
click-annotation on the first frame — a fallback path, not the one
`run_full_pipeline.py` actually uses (it always has a `court.json` by this
point).

**Per-frame output**: whichever ≤2 filtered detections exist in a frame
become `player_1`/`player_2`, in whatever order YOLO returned them. **This
assignment is not stable across frames or semantically meaningful** — it's
just "detection index 0" and "detection index 1" for that frame. Figuring
out which slot consistently means "the far player" vs "the near player"
happens **later**, in `win_predictor/rule_engine.assign_player_sides()`
(see [06_win_prediction.md](06_win_prediction.md)) — by averaging each
slot's Y position across the whole match and comparing to the near
baseline. This two-step design (detect first, assign sides later from
aggregate statistics) is simpler and more robust than trying to track
player identity frame-to-frame during detection itself, which would need
its own tracker and failure modes.

## Parameters reference

| Parameter | Default | Meaning |
|---|---|---|
| `--model` | `yolo11x.pt` | YOLO11 weights; smaller = faster, less accurate |
| `conf_thresh` (detection) | 0.4 | YOLO confidence to keep a raw detection |
| `min_conf` (filter) | 0.4 | Confidence gate in `DetectionFilter` |
| `min_height` | 60px | Minimum bounding-box height |
| `--no_video` | off | Skip writing the annotated detection video (faster) |

## Why this file specifically (design note)

The whole file is deliberately simple relative to a "real" multi-object
tracker: no identity tracking, no re-identification model, no motion
model. Given the downstream need is just "two (x, y) points per frame,
later sorted into far/near by aggregate position," a per-frame detector
plus a separate side-assignment pass is enough, and avoids taking on a
tracker's own failure modes (ID switches, track loss on occlusion) for
information the pipeline doesn't actually need frame-to-frame.
