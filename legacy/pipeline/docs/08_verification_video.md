# Stage 7 — Verification Video

File: `analysis/annotate_video.py`.

**Input:** the video, shuttle CSV, player CSV, court JSON, optionally the
court-presence CSV and the rally CSV.
**Output:** `<name>_annotated.mp4` — one combined visual sanity check:
court boundary + net line + both players + shuttle trail, all drawn on the
actual footage, real H.264 so it plays in a browser.

## Why it exists

Every other stage's output is a CSV — useful for the algorithms downstream,
useless for a human trying to spot-check whether the pipeline actually got
something right. This renders everything at once onto one video so a
human reviewer can watch it and immediately see, e.g., the court boundary
drawn in the wrong place, a player marker drifting off a person, or a
rally that visibly happened with no detection.

## Two purpose-built modes

**`--rallies_only`** — trimmed and joined: skip straight to the frame
windows from `<name>_rally.csv` (padded `±rally_pad_sec`, default 1.0s),
concatenated into one short output. Fast, good for checking each
*detected* rally really is one continuous rally. Structural blind spot: a
rally the model missed entirely is just silently absent — there's nothing
to see.

**`--mark_rallies`** — full-length, untrimmed: every frame of the original
video is kept, with a "RALLY DETECTED" marker (thick green border +
label) drawn only during frames inside a detected rally window. Scrubbing
the whole thing and finding a real rally playing out *without* the marker
on screen is a missed detection — structurally impossible to see with
`--rallies_only`. This was an explicit choice: the model isn't 100%
accurate, and a trimmed video makes a missed rally invisible by
construction rather than something a reviewer can notice. `run_full_pipeline.py`
uses this mode by default.

Mutually exclusive — both modes need `<name>_rally.csv` to exist first.

## Overlay gating — court/net only where the court actually is

If a court-presence CSV exists (broadcast mode), the court/net overlay is
only drawn on frames where `court_present == 1` — otherwise, since
`--mark_rallies` renders the *whole* video including intro/crowd/replay
cutaways, the court outline would be superimposed over footage where the
real court genuinely isn't there, which is actively misleading rather than
just imprecise. If no presence CSV exists (a pre-trimmed clip, not
`--broadcast`), the overlay draws on every frame — the correct assumption
there, since the whole clip *is* court footage. Verified directly: a
synthetic test with a known presence mask showed the overlay's corner
markers present exactly on the marked-present frames and absent
elsewhere, byte-for-byte.

## Rendering

For each frame in the active window(s): court polygon
(`cv2.polylines` + corner dots) and net line, both players (colored dots
— blue = the "P1" detection slot, orange = "P2", **not** semantically
far/near, same caveat as [04_player_detection.md](04_player_detection.md)
— this is a raw visualization of the detector's slots, not the rule
engine's far/near assignment), a shrinking-radius shuttle trail (last
`--trail` frames, default 10, skipping invisible ones), the rally marker
if applicable, and a frame counter label.

## Output codec — the one non-obvious part

`cv2.VideoWriter` only reliably writes `mp4v` (MPEG-4 Part 2) in this
environment. That plays fine in VLC/most desktop players and in OpenCV
itself, but **no modern browser supports it in a `<video>` tag** — only
H.264/VP9/AV1. A file written directly with `mp4v` would just show as a
black box with no error in the web review app.

Fixed by writing to a temporary file with `cv2.VideoWriter` as before,
then transcoding to the real output path via `ffmpeg -c:v libx264 -preset
fast -crf 23 -pix_fmt yuv420p` (the same encoding convention
`video_utils.py` uses elsewhere), and deleting the temp file. Verified
directly: `ffprobe` on a regenerated file confirmed `codec_name=h264`
where it previously reported `mpeg4`.

## Parameters reference

| Parameter | Default | Meaning |
|---|---|---|
| `--trail` | 10 frames | Shuttle trail length |
| `--rally_pad_sec` | 1.0s | Padding around each rally window (`--rallies_only` only) |
| Output codec | H.264, CRF 23 | Browser-compatible, via a post-write ffmpeg transcode |
