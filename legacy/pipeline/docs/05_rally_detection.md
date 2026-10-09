# Stage 5 — Rally Detection

File: `analysis/detect_rallies.py`.

**Input:** the gap-filled shuttle CSV + `player_detections.csv` (+
optionally the court-presence CSV from broadcast mode).
**Output:** `<name>_rally.csv` — `Start_Frame, End_Frame, Start_Time_sec,
End_Time_sec, Duration_sec, Start_Time, End_Time`, one row per detected
rally.

## The core idea

A rally is "the shuttle moving with real speed, for a sustained stretch,
while both players are actually on screen." The state machine
(`segment_rallies`) tracks two states — not-in-a-rally, in-a-rally — and
moves between them based on shuttle speed and visibility, with the scene
mask pre-applied so frames where the camera isn't even on the match don't
count at all.

## Pipeline, in order

1. **Scene mask** (`generate_scene_mask` + `_dilate_mask`) — both players
   detected with confidence `> 0.5`, dilated by `SCENE_MASK_DILATION=100`
   frames. That's a large dilation, deliberately: a high smash can make
   YOLO miss the jumping hitter for 50-90 frames, and with a smaller
   dilation (45 was tried and found insufficient) those gaps weren't
   bridged — `apply_scene_mask` zeroed the pre-smash shuttle data, making
   the rally appear to start 2-3 seconds late. Between-rally periods have
   both players standing and detected throughout, so this large dilation
   doesn't falsely bridge across a real gap.
2. **Court mask** (broadcast mode only, `--court_mask_csv`) — ANDed with
   the scene mask, so a frame only counts if both the players *and* the
   main broadcast camera angle are present (see
   [02_court_presence_and_segmentation.md](02_court_presence_and_segmentation.md)).
3. **Apply the combined mask** — any frame that fails it gets its shuttle
   data zeroed (`X=0, Y=0, Visibility=0`), same as an undetected frame.
4. **`segment_rallies()`** — the state machine (below).
5. **`filter_pickup_rallies()`** — drop false positives.
6. **Duration filter** — drop anything `< MIN_RALLY_DURATION_SEC=2.0`
   (shortest real ground-truth rally observed was 4s; 2.0s comfortably
   removes 1-2s noise blips without risking a real rally).
7. **`merge_close_rallies()`** — residual safety net for splits fill_gaps
   didn't catch.
8. **`apply_lookback()`** — recover the true rally start, which the state
   machine's `MIN_START_VISIBLE` requirement systematically delays.

## The state machine

**Starting a rally:** need `MIN_START_VISIBLE=3` consecutive frames with
`Visibility==1` and `speed > START_SPEED=3.0 px/frame`. Speed is
explicitly zeroed at any invisible→visible transition — a `diff()` from
`(0,0)` to a real position produces a huge fake speed that must not count
as "the shuttle moving." A duplicate-position guard also carries the last
real speed forward across frames where X/Y repeat exactly (a tracking
artifact that would otherwise register as speed=0 mid-rally).

**Ending a rally**, two independent conditions:
- **Gap-based:** `END_GAP_FRAMES=10` consecutive invisible frames.
- **Stationary-based:** an N-of-M window (`STATIONARY_WINDOW=10`,
  `STATIONARY_MIN_SLOW=7`) where at least 7 of the last 10 *visible*
  frames are slow (`speed < STATIONARY_SPEED_TH=3.0`) **and** below the
  smash apex (`Y > STATIONARY_MIN_Y=50` — filters out a slow-motion
  interpolation artifact near the top of frame from being mistaken for a
  genuine ground landing). N-of-M instead of a simple consecutive counter
  because real "stopped" speed jitters around the 3.0 threshold — a
  strict consecutive-frame counter would keep resetting on noise.

**Lookahead before confirming an end** (`END_LOOKAHEAD_FRAMES=15`): peek
15 frames past a candidate end condition — if fast movement resumes within
that window, the rally hasn't actually ended (a brief tracking dropout,
not a real end); clear the end condition and keep going instead of
splitting one rally into two.

## `filter_pickup_rallies()` — floor-pickup and static-noise rejection

Two independent checks on a candidate rally's first second:
- **Pure noise:** if total 2D travel in that window is
  `< MIN_NOISE_TRAVEL_PX=15` and duration `< 4.0s`, it's a static blob,
  not a rally — drop it.
- **True pickup:** if the shuttle starts within `MAX_FEET_DIST_PX=40` of
  whichever player is nearer (vertically, `-50 < Δy < 40`, and
  horizontally, `Δx < 150`), **and** horizontal travel stays under
  `MAX_PICKUP_X_TRAVEL=80` — a floor pickup lifts the shuttle mostly
  vertically at the feet, unlike a real serve or rally shot — drop it.
  Only applied to candidates under 4s (a real pickup never lasts that
  long).

## `apply_lookback()` — recovering the true start

`MIN_START_VISIBLE=3` means the state machine's detected start is always
*at least* 3 frames later than the shuttle actually started moving —
worse if the first few frames of real motion happened to have gaps. This
walks backward from the confirmed start (up to `LOOKBACK_MAX_FRAMES=150`,
capped at the previous rally's end so lookback can never steal frames from
an adjacent rally), looking for a "rest period" — `LOOKBACK_REST_MIN_LEN=5`
consecutive frames that are either invisible or low-confidence
(`< LOOKBACK_REST_CONF_TH=0.40`) — and moves the rally's recorded start to
just after that rest period, i.e. back to where the shuttle first stirred
out of its pre-serve stillness.

## `merge_close_rallies()` — residual split repair

Most rally-splitting occlusion gaps are already fixed at the
`fill_gaps.py` level (see
[03_shuttle_tracking.md](03_shuttle_tracking.md)); this is a lightweight
safety net for whatever slips through — very brief net-exchange dropouts
under a second. Two consecutive detected rallies merge if the gap between
them is `<= MERGE_GAP_SEC=0.75s`, with a wider allowance
(`<= 4.0s`) specifically for a smash-exit case: the previous rally was
short (`<= 2.0s`) and ended with the shuttle high in frame (`Y < 250`) —
i.e. it plausibly exited camera view mid-smash rather than genuinely
ending.

## Parameters reference

| Parameter | Default | Meaning |
|---|---|---|
| `START_SPEED` | 3.0 px/frame | Min speed to begin a rally |
| `MIN_START_VISIBLE` | 3 frames | Consecutive fast frames to confirm a start |
| `END_GAP_FRAMES` | 10 frames | Invisible frames before ending (gap-based) |
| `END_LOOKAHEAD_FRAMES` | 15 frames | Peek window before confirming an end |
| `SCENE_MASK_DILATION` | 100 frames | Bridges brief YOLO misses during smashes |
| `MIN_RALLY_DURATION_SEC` | 2.0s | Drop anything shorter after detection |
| `STATIONARY_SPEED_TH` / `_WINDOW` / `_MIN_SLOW` | 3.0 / 10 / 7 | N-of-M stationary-shuttle end condition |
| `STATIONARY_MIN_Y` | 50px | Excludes smash-apex false stationary reads |
| `MIN_NOISE_TRAVEL_PX` | 15px | Static-noise rejection threshold |
| `MAX_FEET_DIST_PX` / `MAX_PICKUP_X_TRAVEL` | 40 / 80px | Floor-pickup rejection thresholds |
| `LOOKBACK_MAX_FRAMES` | 150 (~5s) | Max backward search for true rally start |
| `LOOKBACK_REST_CONF_TH` / `_MIN_LEN` | 0.40 / 5 | Rest-period detection for lookback |
| `MERGE_GAP_SEC` | 0.75s (4.0s for smash exits) | Residual split-merge threshold |
