# Stage 0, 1, 4 — Shuttle Detection, Filtering, Gap-Filling

Files: `TrackNetV3/predict.py`, `TrackNetV3/filter_trajectory.py`,
`TrackNetV3/fill_gaps.py`.

Three-stage pipeline, each stage cleaning up what the previous one
produced, applied in this order every time:

```
raw video → predict.py → _ball.csv (raw detections + noise)
         → filter_trajectory.py → _ball_clean.csv (fake detections removed)
         → fill_gaps.py → _ball_filled.csv (real occlusion gaps interpolated)
```

---

## Stage 0 — `TrackNetV3/predict.py`: shuttle detection

**Input:** a video file + a TrackNet checkpoint (`ckpts/TrackNet_best.pt`).
**Output:** `<name>_ball.csv` — `Frame, X, Y, Visibility, Confidence` per
frame.

This wraps a pretrained TrackNet model (heatmap-based shuttle detector,
architecture and training defined outside this pipeline — loaded here as a
checkpoint dependency, not re-derived). What this file owns:

**Sliding-window streaming inference.** `Video_IterableDataset` reads the
video in overlapping sequences (`seq_len` frames per window, `sliding_step
=1`) rather than loading the whole video into memory — necessary for
full-length broadcasts. Because windows overlap, **the same frame gets
predicted multiple times** (once per window it appears in).

**Heatmap → position.** For each frame's predicted heatmap: binarize at
`0.5`, and only accept a detection at all if the raw (pre-binarize) max
value clears `CONF_TH = 0.25`. If it does, `predict_location()` (from
`test.py`, not re-derived here) extracts a bounding box from the binary
heatmap; the shuttle position is that box's center, rescaled from the
model's fixed input resolution (`WIDTH × HEIGHT`, from `utils.general`)
back to the source video's actual resolution via `img_scaler = (w/WIDTH,
h/HEIGHT)`. Below the confidence threshold: `(0, 0, Visibility=0)`.

**Deduplication.** Because of the sliding-window overlap, multiple rows
can exist for the same `Frame`. Resolved by sorting
`[Frame, Visibility desc, Confidence desc]` and keeping the first row per
frame — i.e., always prefer a visible detection over an invisible one for
the same frame, and among visible ones, the highest-confidence prediction.

---

## Stage 1 — `TrackNetV3/filter_trajectory.py`: removing fake detections

**Input:** `_ball.csv`. **Output:** `_ball_clean.csv`, same schema, some
rows zeroed (`X=0, Y=0, Visibility=0`).

The raw detector produces real position spikes and misidentified objects
(racket heads, player limbs, court-line intersections) that look like
plausible single-frame detections but aren't physically consistent with
shuttle motion. Three filters, applied in sequence, each catching a
different failure shape:

### Filter 1 — bidirectional spike (`filter_bidirectional_spike`)
For every visible frame, compute speed to the nearest visible neighbor
before and after it (using an *original*-value snapshot, so zeroing one
frame doesn't cascade and inflate its neighbors' apparent speed). Two
independent triggers zero the frame:
- **Hard threshold:** backward speed `> 300 px/frame` with a direct
  (`dt==1`) neighbor — a single-frame 300+px teleport is physically
  impossible for *any* shuttle regardless of what follows it.
- **Bilateral threshold:** *both* backward and forward speed `> 130
  px/frame`, both direct neighbors — a single-frame spike sitting inside
  an otherwise-real trajectory.

### Filter 2 — internal cluster break (`filter_internal_break`, iterative)
Within a run of consecutive visible frames, scan consecutive pairs for a
jump `> 300 px/frame` — physically impossible within one continuous
detection cluster. At the break, the segment *before* the jump is the fake
part if the speed entering that segment was also high (`> 100 px/frame`,
or no prior anchor at all). Zeroing a fake segment can expose a new break
further back, so this iterates to a fixed point.

### Filter 3 — smash direction (`filter_smash_direction`)
After a detection in the smash zone (top 20% of frame) immediately
followed by the shuttle going invisible (it exited the top of frame), any
subsequent visible detection that lands *below* the top-20% re-entry zone
before a genuine top re-entry is fake — almost always the hitter's racket
head or body, picked up while the real shuttle is still above the camera.

Two guards prevent this from destroying real trajectory:
- **`MIN_SMASH_GAP=4`** — only fires if the shuttle was invisible for at
  least 4 frames first. A 1-3 frame gap means it barely left the frame and
  came straight back — real, not a fake mid-frame blob.
- **Serve-toss guard (`SERVE_TOSS_SPEED_TH=5.0`)** — if the cluster just
  before the smash-zone detection was nearly stationary (shuttle held for
  a serve), this isn't a smash exit at all; skip the filter entirely so
  the real serve trajectory that follows isn't zeroed.

---

## Stage 4 — `TrackNetV3/fill_gaps.py`: filling real occlusion gaps

**Input:** `_ball_clean.csv` (+ optional `player_detections.csv`).
**Output:** `_ball_filled.csv`, gap frames now interpolated (cubic spline,
linear fallback), anchor frames never modified.

### Why not just use InpaintNet's own gap-filling
InpaintNet's own mask generator only checks `Y[before] > threshold AND
Y[after] > threshold` — "shuttle in-court." But "shuttle in-court" is not
the same as "a rally is happening": right after a rally ends, the shuttle
is still physically in-court while being picked up or held for the next
serve — both anchors pass that check, so InpaintNet incorrectly bridges
the *between-rally* gap as if it were a mid-rally occlusion. This file
adds two gates InpaintNet lacks, plus several more found necessary in
practice, before filling anything.

### The gates, in order

A gap is filled only if **all** of these hold:

1. **Both anchors visible and in-court** (`Y > y_threshold`; the threshold
   is `0.0`, i.e. disabled, by default — the other gates already prevent
   between-rally fills, and a non-zero Y threshold incorrectly rejects
   legitimate anchors during high smashes/clears where Y genuinely
   approaches 0).
2. **Scene mask** — both players detected (YOLO confidence
   `> PLAYER_CONF_TH=0.5`) at both anchor frames. During pickup/service
   prep, typically one player is walking or crouching → mask=0 → not
   filled. Dilated by `FILL_SCENE_DILATION=10` frames first, since a fast
   smash can make YOLO drop a player for a few frames even mid-rally.
   Exception: the smash *before*-anchor check is skipped, since the
   hitter is mid-jump and often missed by YOLO regardless.
3. **Gap length within an adaptive limit** — `MAX_GAP_SMASH=90` frames
   (3s @ 30fps) if the anchor is in a high smash (top 20% of frame, or
   moving upward fast: `dy < -8px` and speed `> 8px/frame` in the frame
   just before), else `MAX_GAP_OCCLUSION=25` frames (0.83s) for a regular
   occlusion.
4. **Implied speed sane** — straight-line distance between anchors divided
   by frame gap must be `<= MAX_FILL_SPEED=120 px/frame`. A real shuttle
   at ~300km/h in a 1920px-wide frame at 30fps is ~130px/frame, so
   anything implying more than that is two anchors from *different*
   rallies, not one continuous flight.
5. **Anchor-before trajectory quality** — the frames just before the gap
   must show real motion (`TRAJ_WINDOW=5` frames, need `>= 3` visible with
   mean speed `> MIN_ANCHOR_SPEED=2.0 px/frame`), not an isolated
   single-frame detection or a stationary shuttle. Relaxed to 1 visible
   frame for a smash-start anchor — a genuine high smash can leave only
   one frame of trajectory before the shuttle exits above the camera, with
   no earlier history to measure a speed from.
6. **Anchor-after resume speed** (non-smash gaps only) — the first visible
   frame *after* the gap must itself be moving at
   `>= MIN_RESUME_SPEED=5.0 px/frame`. Blocks fills into a slow/stationary
   between-rally cluster even when everything else looks plausible.

### The smash-reentry pre-check

Separate from Filter 3 above (same idea, applied here because gap-filling
sees pre-zeroed data Filter 3 already touched). If the anchor before a gap
is in the smash zone and the gap is long enough (or the implied speed to
`anchor_after` is impossibly high), scan forward and zero any detection
that doesn't land back in the top-20% re-entry zone, extending the gap's
real end to the genuine re-entry point before interpolating.

### Interpolation
Cubic spline (`scipy.interpolate.CubicSpline`) using a small context window
around the gap, if `gap_len >= 3` and at least 4 known points are
available — falls back to pure linear otherwise. If a cubic fit overshoots
frame bounds (a wild anchor context from a fast smash can force the spline
outside `[0, width/height)`), the gap is retried with linear
interpolation; if that *also* overshoots, the gap is left unfilled rather
than writing an impossible position.

---

## Parameters reference

**filter_trajectory.py**

| Parameter | Default | Meaning |
|---|---|---|
| `SPEED_BOTH_TH` | 130 px/frame | Bilateral spike threshold (Filter 1) |
| `SPEED_HARD_TH` | 300 px/frame | One-directional impossible-teleport threshold |
| `SPEED_INTERNAL_TH` | 300 px/frame | Impossible internal cluster jump (Filter 2) |
| `ENTRY_TH` | 100 px/frame | Entry speed confirming a fake segment |
| `SMASH_Y_FRACTION` | 0.20 | Top fraction of frame = smash zone |
| `SMASH_REENTRY_FRAC` | 0.20 | Re-entry must land in top fraction |
| `MIN_SMASH_GAP` | 4 frames | Min invisible frames before Filter 3 fires |
| `SERVE_TOSS_SPEED_TH` | 5.0 px/frame | Stationary-cluster threshold → skip Filter 3 |

**fill_gaps.py**

| Parameter | Default | Meaning |
|---|---|---|
| `MAX_GAP_SMASH` | 90 frames (3s) | Max fillable gap after a high smash |
| `MAX_GAP_OCCLUSION` | 25 frames (0.83s) | Max fillable gap for regular occlusion |
| `MAX_FILL_SPEED` | 120 px/frame | Max implied speed between anchors |
| `PLAYER_CONF_TH` | 0.5 | YOLO confidence for the scene mask |
| `FILL_SCENE_DILATION` | 10 frames | Scene-mask gap bridging |
| `TRAJ_WINDOW` / `MIN_TRAJ_VISIBLE` | 5 / 3 | Anchor-before quality check window/threshold |
| `MIN_ANCHOR_SPEED` | 2.0 px/frame | Anchor-before must be genuinely moving |
| `MIN_RESUME_SPEED` | 5.0 px/frame | Anchor-after must resume at real speed |
| `SMASH_REENTRY_MIN_GAP` | 15 frames | Min gap before the reentry pre-check fires |
