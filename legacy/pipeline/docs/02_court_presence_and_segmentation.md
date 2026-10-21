# Stage 2b–2e — Court Presence Detection and Segmentation (`--broadcast` mode only)

Files: `analysis/court_presence.py`, `analysis/extract_segments.py`,
`analysis/stitch_segments.py`.

Skip this whole stage if you're not running `--broadcast` — a pre-trimmed
rally-only clip goes straight from court annotation to shuttle/player
detection on the whole video.

## Why this exists

A full broadcast isn't one continuous rally-camera shot. It's intro
graphics, player walk-ins, crowd cutaways, coach shots, and replays,
interleaved with the actual constant-angle rally footage. Running
TrackNetV3 and YOLO player detection on all of it wastes most of the
compute on footage that isn't even the match. This stage answers one
question per frame — "is the main broadcast camera angle on screen right
now?" — then uses the answer to cut out just the relevant time ranges.

---

## `court_presence.py` — the per-frame signal

**Input:** the video + the reference `court.json` from stage 2.
**Output:** `<match>_court_presence.csv` — one row per frame:
`frame_no, green_frac, reproj_error_m, court_present`.

### Two-stage check, cheap first

**Stage 1 — green-fraction gate.** What fraction of the pixels *inside the
reference court polygon* are green (HSV range `[30,35,35]`–`[90,255,255]`)?
One masked pixel count. Rejects most non-court frames (crowd, closeups,
graphics) for free. Threshold `0.55`, not near 1.0, because players/shuttle/
lines legitimately cover part of the polygon even during real rally play.

Not specific enough alone — verified against real segment output: a frame
on a *different* but still-green shot (zoomed in, a different camera angle
that happens to fill the same screen region with green) passes this even
though the court is not actually in the same place there.

**Stage 2 — homography verification, only for frames that pass stage 1**
(so the expensive part runs on a minority of candidates). Detect this
frame's own court corners with the same raw green-blob detector
`auto_court.py` uses, reproject them through a homography, and measure the
mean distance (in real-world metres) from where they land to where they
should. Small error = genuinely the same court in the same position; large
error = different framing.

### The self-calibration fix (why this isn't naive)

The homography needs a reference. The obvious choice — the precisely
clicked/line-refined corners in `court.json` — is **wrong** for this
purpose: comparing a raw green-blob-detected candidate against precisely
clicked reference corners produces a large *systematic* error even between
the reference frame and **itself** (measured: ~1.5m, well above any
sensible tolerance), because the raw blob detector is a looser, wider box
than a precise click, not because the camera moved.

The fix (`self_calibrated_reference()`): re-read the *exact* reference
frame from the video (using `frame_no`, saved in `court.json` by both
`annotate_court.py` and `auto_court.py`), run the **same raw detector**
on it, and build the homography from *that* blob instead of the precise
corners. Now both sides of every comparison use the same detector, and the
systematic bias cancels out. Verified: the same reference frame checked
against itself now measures ~0m error (down from ~1.5m); genuine rally
frames nearby measure ~0.02–0.6m; a temporally-unstable candidate frame
(mid camera-pan) correctly measures much higher.

Falls back to the uncalibrated (precise-corner) homography, with a printed
warning, if `frame_no` is missing from the JSON or that frame can't be
read — matches the older, less-accurate behavior rather than failing
outright.

### Sampling: every 30th frame, not every frame

`--stride 30` by default (~1 sample/second at 30fps) — checking every
single frame is far more precision than the presence signal needs, and
`extract_segments.py`'s padding (1.5s each side) already absorbs the
resulting fill lag at segment boundaries.

**Implementation detail that matters for speed:** the scan does **not**
`cap.set()`-seek to each sampled frame. For a long-GOP H.264 file, seeking
to an arbitrary non-keyframe position forces the decoder to decode forward
from the last keyframe anyway — measured close to zero speedup going from
stride=1 to stride=30 with `.set()`. Instead it calls `cap.grab()` (decode
only, no BGR conversion — cheap) through every frame, and only
`cap.retrieve()` (the actual conversion) on the one frame per stride
that's checked. Verified: 6.6x faster (28.6s vs 3m9s on an 18-minute
broadcast) with byte-identical output to a full stride=1 scan.

Gaps between samples are filled forward (`pd.merge_asof(..., direction=
"backward")`) to produce one row per frame in the output CSV regardless of
stride — downstream consumers never need to know the sampling rate.

### Final decision + smoothing

```
court_present = 1  iff  green_frac >= threshold
                    AND  reproj_error_m is not NaN (i.e. it passed stage 1)
                    AND  reproj_error_m <= max_reproj_error_m
```
Then a centered rolling **median** filter (`smooth_window=5`) removes
single-frame flicker — a player fully covering the polygon for a moment, a
smash's motion blur, one bad corner detection — from flipping the signal.

---

## `extract_segments.py` — turning the signal into clips

**Input:** the presence CSV + the video. **Output:** `segments/seg_NNN.mp4`
per segment + `manifest.csv` (`seg_idx, start_frame, end_frame, n_frames,
clip_path`).

1. **Find contiguous runs** of `court_present == 1`.
2. **Merge runs separated by a short gap** (`min_gap_sec=2.0`) — a brief
   cutaway or graphic mid-rally shouldn't split one rally's footage into
   two segments.
3. **Pad each merged run** (`pad_sec=1.5`, clamped to valid frame range) —
   rally starts/ends often dip near the presence threshold as players
   cross the polygon boundary; re-merge afterward in case padding caused
   adjacent segments to overlap.
4. **Drop anything still too short** (`min_duration_sec=3.0`) — not a real
   rally-length span.
5. **Cut each survivor out with ffmpeg's `select` filter**, not `-ss/-to`
   timestamp seeking — frame-accurate, so segment N's local frame 0 is
   *exactly* global frame `start_frame`, which the stitching step depends
   on for correctness. `-c:v libx264 -preset veryfast -crf 18`, no audio.

Errors loudly (`sys.exit`) if zero segments survive — pointing at the two
most likely causes (presence threshold, or the court annotation not
actually matching this video's camera angle) rather than silently
producing an empty pipeline run.

---

## Per-segment processing (`run_full_pipeline.py`, not a separate file)

For each `seg_NNN.mp4` in the manifest: TrackNetV3 shuttle detection →
trajectory filtering → YOLO player detection — the exact same stages as
[03_shuttle_tracking.md](03_shuttle_tracking.md) and
[04_player_detection.md](04_player_detection.md), just run on the short
clip instead of the whole broadcast. Segment output filenames are renamed
to the `seg_NNN` pattern `stitch_segments.py` matches on (TrackNetV3 names
its output after the input clip file, not the segment tag).

---

## `stitch_segments.py` — remapping back to one global timeline

**Input:** the manifest + a glob pattern matching each segment's local
output CSV. **Output:** one CSV with frame numbers remapped to the
original video's global numbering, concatenated.

For each matched file: extract its segment index, look up that segment's
`start_frame` in the manifest, add it to every local frame number in the
file (`df[frame_col] += start_frame`), concatenate.

**Extracting the segment index is the one genuinely tricky part of this
file**, and it was wrong twice before landing on the current
implementation:

- **First bug:** searching for `seg_(\d+)` in the *first match found in
  the full path* — if the match folder itself happens to be named
  something like `seg_009` (e.g. from an uploaded file called
  `seg_009.mp4`), every file's path starts with `.../seg_009/...`, which
  matches *before* the real `seg_000` ever appears in the path. Silently
  stitches under the wrong segment index.
- **Second bug (the "fix" that broke a different case):** restricting the
  search to the filename only. Fixes the match-folder-name collision, but
  breaks player-detection CSVs specifically — their segment index lives in
  the **parent directory** name (`segments/players/seg_000/
  player_detections.csv`), not the filename (`player_detections.csv`,
  fixed, no index in it at all). Shuttle CSVs (`seg_000_ball_clean.csv`)
  have it in the filename; player CSVs don't.
- **Actual fix:** take the **last** `seg_NNN` match anywhere in the full
  path (`list(seg_re.finditer(path))[-1]`), not the first, and not
  filename-restricted. The match-folder name — whichever form it takes —
  always appears *earlier* in the path than the real segment reference, so
  "last match" is correct for both the filename-encoded and
  directory-encoded layouts simultaneously. Verified directly against both
  real shuttle and player CSVs from the same failing match folder.

`run_full_pipeline.py` calls this twice — once for shuttle
(`--frame_col Frame`), once for player detections (`--frame_col
frame_no`) — writing into the same paths the non-broadcast mode would
have produced directly, so every stage after this point (gap-filling,
rally detection, win prediction) doesn't need to know or care whether
`--broadcast` was used.

---

## Parameters reference

| Parameter | Default | File | Meaning |
|---|---|---|---|
| `threshold` | 0.55 | court_presence | Stage-1 green-fraction gate |
| `max_reproj_error_m` | 0.6 | court_presence | Stage-2 homography error gate (metres) |
| `stride` | 30 | court_presence | Frames between samples (~1/sec at 30fps) |
| `smooth_window` | 5 | court_presence | Median-filter window to remove flicker |
| `min_gap_sec` | 2.0 | extract_segments | Merge runs separated by less than this |
| `pad_sec` | 1.5 | extract_segments | Padding added to each side of a segment |
| `min_duration_sec` | 3.0 | extract_segments | Drop segments shorter than this after padding |
