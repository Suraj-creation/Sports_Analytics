# Stage 0 & 2 — Video Preprocessing and Court/Net Setup

Files: `analysis/video_utils.py`, `analysis/annotate_court.py`,
`analysis/auto_court.py`, `analysis/frame_picker.py`,
`analysis/extract_features.py` (corner/net functions only — the rest of
that file is covered where it's actually used, in
[06_win_prediction.md](06_win_prediction.md)).

## Why this exists

Everything downstream — court-presence detection, player filtering, the
fault-side rule engine, the trajectory RF's `margin_cm` feature — depends on
one thing being right: 4 pixel coordinates for the court corners, plus
where the net is. Get this wrong and every later stage is wrong in a way
that's hard to notice, because the pipeline will still *run* and produce
plausible-looking numbers. So this stage gets disproportionate engineering
attention relative to how simple it sounds ("click 4 points").

---

## Stage 0 — `video_utils.ensure_preprocessed()`

**Input:** any video file. **Output:** a path to a video that's guaranteed
H.264, 1280×720, 30fps.

**Why:** `cv2.VideoCapture` cannot reliably decode AV1 (common for YouTube
downloads — yt-dlp often defaults to it). It doesn't raise an exception —
`.read()` just returns `False` on every single frame. A script scanning for
something (a good annotation frame, court presence) then silently finds
nothing and fails with a confusing error far from the real cause ("no frame
with a centered court view found" when the actual problem is "this video
never decoded a single frame"). Wrong resolution or frame rate is worse —
it doesn't fail at all, it silently breaks every pixel-coordinate and
frame-count assumption downstream (a `court.json` clicked at 1280×720
applied to a 1920×1080 video, rally duration math off by whatever the fps
ratio is).

**How it works:**
1. `probe_video(path)` — one `ffprobe` call, reads `codec_name`, `width`,
   `height`, `r_frame_rate`.
2. `_matches(path, w, h, fps)` — `codec == "h264" and width==w and
   height==h and abs(fps_diff) < 0.1`.
3. If it already matches: return the original path, untouched, zero cost.
4. If not: check for a cached transcode next to it
   (`<stem>_prepared.mp4`) — reused across repeated calls instead of
   re-transcoding every time a script touches the same video.
5. Otherwise transcode: `ffmpeg -vf scale=1280:720 -r 30 -c:v libx264
   -preset fast -crf 23 -an`. Audio is dropped (`-an`) — nothing downstream
   ever reads it.

**Where it's called:** `run_full_pipeline.py` calls it once, up front,
before any stage runs. But `annotate_court.py`, `auto_court.py`, and
`court_presence.py` **also** call it themselves (each has a `--no_preprocess`
opt-out flag) — because those three scripts are also meant to be runnable
standalone, not just through the orchestrator, and standalone runs don't
get the orchestrator's up-front normalization for free.

---

## Reference-frame selection — `frame_picker.py`

Both annotation paths (manual and automatic) need to pick **which single
frame** to show/detect on. This module is shared between them so they agree
on what "a good frame" means.

### The problem with a fixed frame number

A fixed early frame (e.g. frame 90, ~3s in) is fine for a pre-trimmed
rally-only clip, but wrong for a full broadcast — verified on a real
31-minute match: frame 90 was a drone shot of the arena exterior, not the
court.

### `center_score()` / `margin_score()`

Two pure scoring functions on a candidate frame's detected court corners:
- `center_score`: 1.0 if the court's centroid is dead-center in frame, 0
  at the edge.
- `margin_score`: 1.0 if there's clear breathing room on all sides (the
  standard wide broadcast shot); drops toward 0 as the court approaches
  touching a frame edge (a zoomed/cropped shot).

Combined as `score = center * margin * min(1, area_frac / 0.30)` — area is
a **gate** (`min_area_frac`, default 0.15 of frame area — must be a
substantial, plausible court view) not the ranking signal; center/margin
decide between candidates that all clear that bar. This deliberately
rewards the standard centered wide shot over a bigger but zoomed/cropped
one.

### `pick_frame_fast()` — the actual search used in practice

Full-video scanning (`rank_candidate_frames`, below) can be hundreds of
frame reads on a long broadcast — minutes of wall time. `pick_frame_fast`
is the practical default:

1. Try **one** candidate first: the video midpoint (a strong prior —
   broadcasts are front/back-loaded with intro, walk-ins, post-match
   ceremony, so the middle is very likely mid-match play), or
   `start_frame` if the caller already knows roughly where play starts.
2. If that frame's score clears `GOOD_ENOUGH_SCORE = 0.5`, return
   immediately — one frame read total.
3. Otherwise step forward `step_sec` (default 5.0s) at a time, up to
   `max_fallback_frames` (default 20) more candidates, and return the best
   scored one found.

Bounded cost: at most `1 + max_fallback_frames` frame reads, vs. up to
hundreds for the full scan. Measured on a real 31-minute broadcast: ~8
seconds instead of 1-2 minutes.

### `_stable_enough()` — the temporal-stability gate

A frame can score well on area/center/margin while still being a *bad*
reference — e.g. one well-composed frame mid-camera-pan. Since every later
frame in the video gets checked against this one reference via homography
(see [02_court_presence_and_segmentation.md](02_court_presence_and_segmentation.md)),
an unrepresentative reference silently causes the real match footage to
fail a check it should pass.

**How it works:** given a candidate frame's own detected corners, build a
homography from *those* corners (self-referential — not the eventual
manually-clicked or line-refined corners, which don't exist yet at this
point), then sample a window (`window_sec=8.0`, `sample_stride_sec=1.0`)
of frames around the candidate. For each sample: green-fraction gate
(`green_threshold=0.55`) then homography reprojection-error check
(`max_reproj_error_m=0.6`). Find the longest contiguous run of "passing"
samples that includes the candidate itself, convert to seconds. Require
`>= min_present_sec = 3.0` seconds of genuine surrounding consistency
before accepting the candidate at all.

This is wired as a **hard gate**, not just an informational score — inside
`_score_one()`, a candidate that fails stability is treated identically to
"no court detected," and the search moves to the next candidate. Verified
on real footage: the video's midpoint frame (previously always accepted)
correctly got rejected once for only 1.0s of surrounding consistency, and
the search kept going until it found a genuinely stable one.

Escape hatch: `--no_stability_check` on both `annotate_court.py` and
`auto_court.py` skips this and falls back to the single-frame score alone
— faster, but risks exactly the failure mode above.

### `rank_candidate_frames()` — the exhaustive alternative

Same scoring, but scans the **whole** video at `step_sec` intervals
(default 400 candidates max) and returns every one that clears the area
gate, sorted best-first. Used when `pick_frame_fast` can't find anything
good nearby (`--full_scan` flag), or to populate the "Try Different Frame"
button's full alternative list in the manual annotation UI.

---

## Manual annotation — `analysis/annotate_court.py`

A self-contained browser tool: no dependency on the rest of the codebase's
web stack, just Python's `http.server`.

**Flow:**
1. Pick the frame to show (see above): `--frame N` (exact), `--auto_frame`
   (search via `frame_picker`), or default frame 90.
2. Serve one HTML page with the frame embedded as a base64 JPEG. Click 8
   points in order — `TL, TR, BR, BL` (court corners), `NL, NR` (net post
   bases — ground-level, gives `net_Y`), `CL, CR` (net cable top — gives
   `net_top_Y`).
3. Each click POSTs to `/click`; "Save" POSTs the full 8-point list to
   `/save`, which writes the JSON and shuts the server down.

**Output schema** (`<match>_court.json`):
```json
{
  "frame_no": 8634,
  "frame_size": {"width": 1280, "height": 720},
  "corners": {"TL": [...], "TR": [...], "BR": [...], "BL": [...]},
  "net": {
    "net_Y": ..., "net_top_Y": ...,
    "left_bottom": [...], "right_bottom": [...],
    "cable_left": [...], "cable_right": [...]
  },
  "source": "manual"
}
```
`frame_no` matters beyond record-keeping — `court_presence.py`'s
self-calibration re-reads exactly this frame (see next doc) to remove a
systematic detector-precision bias.

**Why this specific implementation (`ThreadingHTTPServer` + lock + per-request
timeout), not the obvious `http.server.HTTPServer`:** the plain
single-threaded server handles one request at a time on the main thread. If
a client's connection stalls mid-response (flaky network, a browser tab
that stops reading), `wfile.write()` can block indefinitely with **no
timeout**, freezing the entire server for every subsequent request —
including Save, from the *same* browser tab. This is not a hypothetical:
it hung a real session for 5+ minutes, process alive, socket still
accepting connections, never responding. `ThreadingHTTPServer` puts each
request on its own thread; `Handler.timeout = 30` bounds how long any one
of them can block; `STATE_LOCK` serializes the shared-state mutations
(`points`, `bgr`, `args.frame`, `candidate_idx`) since multiple request
threads can now genuinely run concurrently.

---

## Automatic annotation — `analysis/auto_court.py`

Zero-click alternative. Two-stage corner detection:

**Stage 1 — green-mask blob** (`extract_features._try_detect_corners`):
HSV-threshold for the court's green surface, adaptive morphological
close+open (kernel scaled to image size), take the largest contour, try
`cv2.approxPolyDP` at progressively looser epsilons until it collapses to
4 points, sort into `[TL, TR, BR, BL]` order by Y then X
(`_sort_corners`). Fast, but this typically extends *past* the painted
sideline (sponsor mats, warm-up strip) — it's the extent of the green
surface, not the boundary line.

**Stage 2 — white-line refinement** (`refine_corners_court_type`): detect
long white line segments inside that green region (`cv2.HoughLinesP`,
`minLineLength = 20% of min(h,w)`), classify each as horizontal (baseline,
angle < 25° or > 155°) or diagonal (sideline), cluster near-duplicate
detections of the same physical line (`_cluster_1d`, gap threshold 15px).

The genuinely hard part: **a badminton court paints both the doubles
sideline and, 0.46m inside it, the singles sideline.** "The outermost
white line" is not automatically the right one for a singles match. The
code checks the separation between the two clusters on each side
(`SEP_MIN_PX=15, SEP_MAX_PX=150` — the physically-plausible range for a
0.46m gap at this camera's typical scale) and only proceeds if **both**
sides show a confidently-separable inner/outer pair. If it can't tell —
only one line detected, or the separation is outside the plausible
range — it does **not** guess. It falls back to the green-mask corners
with `court_type_matched: false` in the output and a printed warning
telling you to use manual mode instead. This was a deliberate fix for a
real failure mode: silently returning doubles corners mislabeled as
singles.

**Net position, two very different derivations:**
- `net_Y` (ground line): geometrically exact. `compute_net()` builds a
  homography from the 4 detected corners to the real-world court rectangle
  (5.18×13.4m singles / 6.1×13.4m doubles), projects the known net depth
  (6.7m from baseline) back into image space.
- `net_top_Y` (the elevated cable, ~1.55m up): **cannot** be derived from a
  flat ground-plane homography at all — that needs the camera's full 3D
  pose, which isn't being solved for. It's approximated as the mean Y of
  the TL/TR corners, based on an empirical observation (from
  manually-annotated production matches) that the cable sits within a few
  pixels of the far baseline in this camera convention. This is a real
  approximation, not a measurement — `--net_top_y` lets you override it,
  and manual annotation (which clicks the actual cable) is more accurate.
- `snap_net()` refines `net_Y` further by detecting the blue net-post
  stands' pixels in HSV (they sit at exactly the net's depth on both
  sidelines) within a vertical band around the computed `net_Y`; falls
  back to `cv2.Canny` + `HoughLinesP` strongest nearby horizontal edge if
  the blue-post detection finds nothing.

**Reference-frame picking** for `--wide_search` reuses `pick_frame_fast`
and the stability check above — this is the same picker
`annotate_court.py --auto_frame` uses, so both annotation paths agree.

---

## Parameters reference

| Parameter | Default | File | Meaning |
|---|---|---|---|
| `width, height, fps` | 1280, 720, 30.0 | video_utils | Target normalization |
| `GOOD_ENOUGH_SCORE` | 0.5 | frame_picker | Score threshold to accept a candidate without further search |
| `min_area_frac` | 0.15 | frame_picker | Court must cover ≥15% of frame area to be a plausible candidate |
| `window_sec` | 8.0 | frame_picker (`_stable_enough`) | ± window checked around a candidate for temporal stability |
| `sample_stride_sec` | 1.0 | frame_picker | Sampling interval within the stability window |
| `min_present_sec` | 3.0 | frame_picker | Minimum contiguous stable duration required |
| `max_reproj_error_m` | 0.6 | frame_picker | Max homography reprojection error (metres) counted as "same position" |
| `SEP_MIN_PX, SEP_MAX_PX` | 15, 150 | auto_court | Plausible pixel separation range for doubles↔singles sideline gap |
| `EDGE_MARGIN` | 20px | auto_court, extract_features | Excludes lines right at the green-paint edge (paint boundary, not court line) |
| `shift_limit` | 30%/15% of frame height (singles/doubles) | auto_court | Max allowed corner shift from line-refinement before rejecting it |
