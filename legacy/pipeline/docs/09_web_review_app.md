# Web Review App

Files: `webapp/jobs.py`, `webapp/server.py`, `webapp/static/index.html`,
`webapp/static/app.js`.

A local Flask + vanilla-JS app: upload a video in the browser, watch the
real pipeline (`run_full_pipeline.py`) process it with live progress, then
review the actual detected rallies against the actual annotated video and
correct anything wrong — without ever modifying the pipeline's own output
files.

**Run it:**
```bash
cd pipeline_release
python3 webapp/server.py --port 8000
```

---

## `jobs.py` — running the real pipeline as a background job

Does **not** reimplement any pipeline logic. It shells out to the exact
same `run_full_pipeline.py` a terminal user would run, and gets live
progress by parsing its existing stdout — no changes needed to the
pipeline script itself.

**One job at a time**, by design: a single background worker thread pulls
job IDs from a `queue.Queue`. The pipeline stages are GPU/CPU-heavy, and
manual court annotation briefly needs an exclusive port (5050) for
`annotate_court.py`'s own browser tool — concurrent jobs aren't something
this local, single-user tool is built to support.

### Progress parsing

`run_full_pipeline.py` already prints structured step headers for every
stage: `"2b/7  Court-presence mask"`, etc. (see
[00_overview.md](00_overview.md)). `STEP_RE = re.compile(r'^\s*([0-9]+[a-z]?/7)\s+(.+?)\s*$')`
matches these directly from the subprocess's live stdout, updating
`job.current_step` and appending to `job.steps_seen` as they arrive.
`SKIP_RE` and `DONE_RE` catch the `[skip]` lines and the final
`DONE -- <path>` line the same way.

**A real bug found via live testing:** the child process's stdout is
piped (not a TTY), so CPython defaults to fully block-buffered output —
`run_full_pipeline.py`'s own `print()` calls, and everything it in turn
shells out to (TrackNetV3, YOLO), sat in an internal buffer and never
reached the parser until a buffer's worth accumulated or the process
exited. Fixed by setting `PYTHONUNBUFFERED=1` in the **environment**
passed to the top-level `subprocess.Popen` call — not just a `-u` flag on
that one process, since the environment variable is what actually
propagates down through every further `subprocess.run()` call
`run_full_pipeline.py` makes internally (which inherit the parent's
environment by default, but would *not* inherit a `-u` flag applied only
to the immediate child's own invocation). Verified: before the fix,
`steps_seen` stayed empty for the entire run despite the subprocess doing
real, visible work; after, individual steps and their live sub-process
output (`Using device: cuda`, frame counts, etc.) streamed through in
real time.

### The manual-annotation wait state

If `--court_mode manual` is used, the pipeline blocks on
`annotate_court.py`'s own browser server until a human clicks 4 points —
correctly so, but a naive progress parser would just show the job "stuck"
with no explanation. Detected by step *label* (`MANUAL_ANNOTATION_HINT =
"Court + net annotation (manual"` — deliberately by label, not by step ID,
since the ID `"2/7"` is shared with the automatic-mode label too), setting
`job.status = "waiting_for_annotation"`. The frontend shows explicit
instructions to open port 5050 rather than a spinner with no explanation.

### Retry — reusing the pipeline's own resumability

`POST /api/jobs/<id>/retry` on a failed job creates a **new** job with the
**same** `match_name` as the failed one (not a fresh sanitized name).
This matters: `run_full_pipeline.py` already skips any stage whose output
file exists, so retrying with the same match name picks up exactly where
it failed instead of redoing completed work. This was added after live
testing hit a real failure partway through a run — a naive re-upload
through the normal upload form would have gotten a *new*, differently-named
match folder (the upload endpoint's collision-avoidance logic exists for a
different reason — see below — and would have actively defeated the
pipeline's own resumability here).

---

## `server.py` — the Flask API

| Route | Method | Purpose |
|---|---|---|
| `/` , `/static/<file>` | GET | Serve the frontend |
| `/api/jobs` | POST | Upload a video, create + enqueue a job |
| `/api/jobs/<id>` | GET | Job status (polled by the frontend every 2s) |
| `/api/jobs/<id>/retry` | POST | Re-run a failed job, same match name |
| `/api/jobs/<id>/data` | GET | Parsed rally data for the review screen |
| `/api/jobs/<id>/video` | GET | The annotated video (range-request enabled) |
| `/api/jobs/<id>/corrections` | GET/POST | Load/save human review edits |
| `/api/jobs/<id>/report.pdf` | GET | The generated PDF report |

### Match-name collision avoidance (upload only, not retry)

`_sanitize_match_name()` strips to `[A-Za-z0-9_-]`, and if a folder with
that name already exists, appends `_2`, `_3`, etc. until it finds a free
one. This exists specifically for the **upload** path — reusing an
existing match folder there would make `run_full_pipeline.py` treat old,
unrelated data as if it were the fresh upload's own output (every stage
would just skip itself, "completing instantly" with someone else's
numbers). Deliberately **not** applied to `/retry`, which needs the
opposite behavior (see above).

### `/data` — converting `win_predictions.csv` into the review schema

Reads the real CSV schema directly (see
[06_win_prediction.md](06_win_prediction.md) for the source columns):
`winner`/`loser` (real player-name strings) mapped to `'A'`/`'B'` by
comparing against the job's own `player_a`/`player_b`; `win_reason`
mapped to short internal codes (`out_of_bounds→oob, hits_net→net,
wins_by_landing→land`); frame numbers converted to seconds via the
video's actual fps (read fresh with `cv2.VideoCapture`, not assumed);
score columns looked up by name with the same `[:8]`-truncation
`predict.py` uses when writing them (`f"score_{player_a[:8]}"`), since a
long player name gets truncated in the CSV's own column header. A rally
is flagged `low-confidence` if `cnn_conf < 0.6` — reusing a real model
confidence signal already present in the data, not a separate heuristic.

**Corrections are layered on top, never overwriting the source.** If
`corrections.json` exists in the match folder, `/data` returns *its*
rally list (a full snapshot, not a diff) instead of re-deriving from
`win_predictions.csv`. The CSV itself is never written to — corrections
live in a completely separate file, so the model's original output and a
human's corrections both survive independently.

### `/video` — range-request serving

`send_file(path, conditional=True)` — Flask/Werkzeug's built-in support
for HTTP `Range` requests, required for a browser `<video>` element to
seek/scrub through a large file without downloading all of it first.
Verified directly: a `Range: bytes=0-1023` request against a real 1.25GB
annotated video correctly returned `206 Partial Content` with a matching
`Content-Range` header.

### `/report.pdf`

Globs `<match>/unified/*.pdf` rather than reconstructing the exact
filename — the real filename includes a generation timestamp
(`<players>_badminton_highlights_<timestamp>.pdf`, see
[07_fusion_commentary_pdf.md](07_fusion_commentary_pdf.md)), which this
endpoint doesn't need to know in advance. Picks the newest by mtime if
more than one exists.

---

## Frontend — `index.html` + `app.js`

Three screens, one page, `goStep(n)` toggles visibility:

**1. Upload** — file picker (drag-drop or click-to-browse), player names,
match name (optional), court-mode radio (auto/manual), broadcast
checkbox. Submits via `XMLHttpRequest` (not `fetch`) specifically to get
upload-progress events for large video files.

**2. Processing** — polls `GET /api/jobs/<id>` every 2 seconds. Renders
the step checklist **directly from the server's `steps_seen` array** —
not a hardcoded local list — since the real step sequence differs between
direct and `--broadcast` mode (see
[00_overview.md](00_overview.md)) and the server is the only thing that
actually knows which one is running. Shows the manual-annotation
instructions or a failure box (with a **Retry** button, see above) based
on `job.status`.

**3. Review** — fetches `/data` once processing completes, then:
- A real `<video controls preload="auto">` element (**not** a custom
  player — an earlier version had neither `controls` nor real preload,
  which rendered as a black box with nothing playable; found via direct
  user testing, not caught by any automated check).
- A rally timeline: draggable-edge blocks per rally, click a >14-second
  gap to insert a new rally there (`addRally`), click a block to select +
  seek the video to it.
- A rally-by-rally table: every field (start, end, winner, reason)
  directly editable inline, a live-computed running score column
  (recomputed client-side on every edit, not read from the server's
  stale `score_after`), a delete button per row, an explicit "+ Add
  missed rally" button independent of the timeline's gap-click affordance.
- A "How points were won" bar chart, computed client-side from whatever
  the current (possibly-edited) rally reasons are.
- A Match Report card — the same `analysis_report.txt` commentary text
  the PDF contains, plus a direct PDF download link.
- Save Draft / Confirm & Finalize, both `POST /api/jobs/<id>/corrections`
  with the full current rally list + comments text; the only difference
  is the `confirmed` flag.

### Winner is computed, not independently settable

An earlier version had a separate match-level winner override (A/B
toggle) *in addition to* the per-rally table — which could disagree with
the rally tally, producing a confusing "your override disagrees with the
score" warning. Removed: winner is now purely `aCount vs bCount` from the
rally table, with a small note pointing back to the table as the only
place to change it. One source of truth, not two that can drift apart.

### Bugs found via real end-to-end testing (not caught by unit checks)

Each was caught because the app was run against a **real** upload through
the real pipeline, not mocked data — worth listing because they're the
kind of bug that only shows up under real conditions:

- **Empty `win_predictions.csv` crash** — a clip with zero detected
  rallies made `predict.py`'s `pd.DataFrame(rows)` produce a 0-column
  (not just 0-row) frame, which `.to_csv()`'d to an effectively empty
  file that `pd.read_csv()` downstream couldn't parse at all
  (`EmptyDataError`). Fixed by always passing an explicit `columns=`
  list to `pd.DataFrame()`, so even zero rallies produces a valid,
  header-only CSV.
- **`idxmax()` on an empty rally set** — see
  [07_fusion_commentary_pdf.md](07_fusion_commentary_pdf.md)'s zero-rally
  guard; same root cause (a genuinely rally-free clip) as the bug above,
  caught one stage later.
- **`stitch_segments.py`'s segment-index regex** — see
  [02_court_presence_and_segmentation.md](02_court_presence_and_segmentation.md);
  found because a real test upload happened to produce a match folder
  whose *name* looked like a segment filename.
- **`nextTempId` collision on a resumed session** — a newly-added rally's
  temporary ID always started at `-1` on page load; if a *previous*
  session's saved corrections already used `-1` for a user-added rally,
  a new addition in a later session would collide with it. Fixed by
  computing the starting ID from the lowest existing negative ID already
  present in loaded corrections, not always resetting to `-1`.

## Parameters reference

| Parameter | Value | Meaning |
|---|---|---|
| Poll interval | 2000ms | Processing-screen status check frequency |
| `LOW_CONF_THRESHOLD` | 0.6 | `cnn_conf` below this flags a rally as low-confidence |
| Gap-to-addable threshold | 14s | Timeline gaps wider than this show an "add missed rally" affordance |
| PYTHONUNBUFFERED | `1` | Set in the pipeline subprocess's environment for live progress |
