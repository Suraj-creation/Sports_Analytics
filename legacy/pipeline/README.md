# Badminton Rally Analysis Pipeline

An end-to-end system that takes a raw badminton match video and produces, fully
automatically, a per-rally breakdown of the match: when every rally happened,
who won each one, *why* they won it (opponent hit out of bounds / hit the net /
opponent failed to return), the running score, and a written match report —
plus a web app that lets a small team (an admin + interns) upload matches,
annotate court geometry, and review/correct the model's output without
touching a command line.

This repo is the pipeline + web app source code only. Match videos, generated
per-match output (CSVs, JSON, annotated video, reports), and trained model
weight files are **not** included — see [Setup](#setup) for where to get the
weights and how output gets generated when you actually run it.

---

## Table of contents

1. [Architecture at a glance](#architecture-at-a-glance)
2. [Setup](#setup)
3. [The full flow, end to end](#the-full-flow-end-to-end)
4. [Backend, in detail](#backend-in-detail)
5. [Frontend, in detail](#frontend-in-detail)
6. [The pipeline stages, in detail](#the-pipeline-stages-in-detail)
7. [Repo structure](#repo-structure)
8. [Further reading](#further-reading)

---

## Architecture at a glance

```
                    ┌─────────────────────────────────────────────┐
                    │              Browser (React SPA)             │
                    │  webapp/frontend/  — Vite + React Router      │
                    │  /login /admin /tasks /court-task/:id /       │
                    └───────────────────┬───────────────────────────┘
                                        │  fetch() JSON over /api/*
                                        │  (same-origin, session cookie)
                    ┌───────────────────▼───────────────────────────┐
                    │           Flask backend (webapp/)              │
                    │  server.py   — routes + auth gating             │
                    │  auth.py     — session login, password hashing  │
                    │  db.py       — SQLite: users, jobs, tasks        │
                    │  jobs.py     — background pipeline queue/worker │
                    │  frame_tasks.py — async court-frame extraction  │
                    └───────┬───────────────────────┬─────────────────┘
                            │ subprocess               │ subprocess
                            ▼                           ▼
                    run_full_pipeline.py      analysis/frame_picker.py
                    (the actual CV/ML          (candidate-frame ranking
                     pipeline, chained          for the court-annotation
                     stage by stage)            task, no video needed
                                                 after extraction)
```

Two things run at once: the **Flask process** (serves the web app, always
listening) and, inside it, a **single background worker thread** that pulls
jobs off a queue and shells out to `run_full_pipeline.py` — the same script
you'd run by hand from a terminal. The web app doesn't reimplement any
pipeline logic; it drives the real CLI pipeline and parses its own stdout for
progress.

---

## Setup

**1. Python dependencies** (pipeline + backend):
```bash
pip install torch torchvision opencv-python pandas numpy scikit-learn joblib \
            flask werkzeug ultralytics
```
(TrackNetV3 and the YOLO player detector pull in a few more — see each
subfolder's own README if `pip install` complains about a missing package.)

**2. Model weight files** — excluded from this repo (too large for a normal
git push / not source code). Place these at the exact paths below before
running anything:

| File | Goes at | Used by |
|---|---|---|
| `TrackNet_best.pt` | `ckpts/TrackNet_best.pt` | Shuttle detection (TrackNetV3) |
| `yolo11x.pt` | `yolo11x.pt` (repo root) | Player detection |
| `clip_rally_end_final.pt` | `analysis/cnn_rally_end/models/clip_rally_end_final.pt` | Rally-end CNN |
| `model_20f.pt`, `model_16f.pt` | `win_predictor/models/` | Win-reason CNN ensemble |
| `rf_classifier.pkl` | `win_predictor/models/rf_classifier.pkl` | Trajectory Random Forest |

**3. Node.js** (frontend build) — needs Node ≥18:
```bash
cd webapp/frontend
npm install
npm run build      # produces dist/, which Flask serves directly
```

**4. First admin account:**
```bash
cd webapp
python3 manage.py create-admin --username admin --password <your-password>
```

**5. Run it:**
```bash
cd webapp
python3 server.py --port 8000
```
Open `http://localhost:8000`, log in, done. Frontend dev mode (hot reload,
`npm run dev` + Vite proxy) is described in `webapp/frontend/README.md` if
you're actively changing frontend code.

---

## The full flow, end to end

### 1. Admin uploads a match
Admin logs in (`/admin`) and either uploads a single video or **batch-uploads**
several at once. Per video, they choose:
- **Player names**
- **Court mode** — `auto` (zero-click court detection) or `manual` (a human
  clicks 8 points — 4 court corners + net posts + net cable — on a still frame)
- **Broadcast vs. pre-trimmed clip** — whether the video has intro/crowd/replay
  cutaways that need to be filtered out first, or is already just rally footage

### 2. Court annotation (manual mode only)
The instant a manual-mode video is uploaded, the backend extracts a handful of
candidate still frames in the background (`frame_tasks.py`, ranked by how
clearly they show a centered, stable view of the court — see
[`analysis/frame_picker.py`](analysis/frame_picker.py)). The job sits as
"awaiting court task" until an admin assigns it to someone (an intern, or
themselves).

The assignee opens `/tasks` → the task shows up under "Court annotation" →
they click the 8 points in order on the frame shown (switching to a different
candidate frame first if the one shown is obscured) → submit. This never
touches the live video — just one still image — so it takes seconds, not
minutes.

**The moment they submit**, the backend writes `<match>_court.json` and pushes
the job onto the pipeline queue *in that same request*. No admin action, no
second login needed — the multi-hour pipeline run starts on its own.

### 3. The pipeline runs, unattended
A single background worker thread (one job at a time — the stages are
GPU/CPU-heavy) shells out to `run_full_pipeline.py`, which chains every stage
in order (shuttle detection → gap-filling/filtering → court geometry →
player detection → rally segmentation → win prediction/fusion/report → 
verification video). See [pipeline stages](#the-pipeline-stages-in-detail)
below for what each one actually does. Progress streams back to the admin
dashboard live (parsed from the subprocess's own stdout, not reimplemented).

Each stage is skipped if its output already exists — an interrupted or failed
run can just be retried and picks up where it left off, rather than starting
over.

### 4. Review task appears automatically
The moment the pipeline finishes, the job's review task flips from "not
ready" to "pending" on its own. Admin assigns it (same person or someone
else) via the dashboard.

### 5. Review & correct
The assignee opens `/tasks` → "Review" → lands on the review screen: the
annotated video, a rally timeline (drag edges to trim a rally's boundaries,
click a gap to mark a rally the model missed), a full editable table (winner,
win-reason, start/end time per rally), a live-updating winner/score summary,
and the generated match report. They fix whatever's wrong, "Save draft" as
they go, "Confirm & finalize" when done. Corrections are stored in a separate
`corrections.json` next to the match's other output — the model's original
guess is never overwritten, so both survive.

### 6. If someone gets stuck
At either the court-annotation or review step, the assignee can flag the task
with a reason instead of leaving it stuck — it unassigns automatically and
jumps to the top of the admin dashboard (marked "needs attention") for
reassignment. Nothing silently stalls.

---

## Backend, in detail

Everything lives in `webapp/`. Flask, no ORM, no task queue library —
deliberately minimal:

- **`db.py`** — SQLite (stdlib `sqlite3`, WAL mode). Two tables: `users`
  (username, hashed password, role — `admin` or `intern`) and `jobs` (one row
  per uploaded match: pipeline status, court-task status/assignee/candidates,
  review-task status/assignee, flag reasons). Chosen over a generic key-value
  or NoSQL store because the query patterns are simple, fixed-shape lookups —
  no schema flexibility needed.

- **`auth.py`** — session-cookie auth via Flask's built-in signed sessions +
  `werkzeug.security` password hashing. Two decorators, `@login_required` and
  `@admin_required`, gate every `/api/*` route. This is the *real* access-control
  boundary — the frontend's route guards are UX only (instant redirect),
  not security, since a compiled JS bundle isn't a secret regardless of who
  can fetch it.

- **`jobs.py`** — an in-memory dict (`JOBS`) that mirrors the `jobs` DB table
  (loaded at startup, written back on every state change), a `queue.Queue`,
  and one background worker thread that pulls a job id off the queue, shells
  out to `run_full_pipeline.py` as a real subprocess, and parses its stdout
  line-by-line (matching the `N/7  Step name` headers the pipeline script
  already prints) into structured progress the frontend polls for. On a
  server crash/restart, any job caught mid-run is marked `failed` cleanly —
  the existing Retry button reuses the same match name, so the pipeline's own
  step-skip logic resumes correctly rather than starting over.

- **`frame_tasks.py`** — a *separate*, small thread pool (not the pipeline
  queue) that extracts and ranks candidate court-annotation frames right
  after upload. Kept separate deliberately: ranking frames is cheap CPU work,
  not GPU inference, and sharing the pipeline's single-item queue would mean
  a batch of 50 uploaded videos each waiting behind every prior video's
  multi-hour pipeline run just to get a still frame extracted.

- **`server.py`** — every `/api/*` route (auth, admin CRUD, job lifecycle,
  the native court-annotation click endpoints, review data/corrections), plus
  (in production) a catch-all route that serves the built React app for every
  non-API path, so client-side routes like `/admin` or `/court-task/<id>`
  survive a hard refresh.

---

## Frontend, in detail

`webapp/frontend/` — a Vite + React app (plain JS/JSX, no TypeScript, no
CSS-in-JS framework — matches this project's general preference for minimal
tooling), `react-router-dom` for client-side routing.

**Pages** (`src/routes/`):
- `LoginPage` — username/password, redirects by role on success.
- `MatchFlowPage` (`/`) — the admin's upload → processing → review flow, as
  one route with internal step state (it's a linear wizard, not independently
  bookmarkable pages). Also handles `/?job=<id>` deep links, used when an
  intern opens a review task from `/tasks` — jumps straight to the review
  step for that job.
- `AdminDashboardPage` (`/admin`) — jobs table (live-polled), batch upload,
  intern account management.
- `TasksPage` (`/tasks`) — the logged-in user's own court-annotation and
  review task queues.
- `CourtTaskPage` (`/court-task/:jobId`) — the 8-point click UI.

**Shared infrastructure** (`src/hooks/`, `src/components/`):
- `useCurrentUser` — fetches `/api/me` once, exposes the logged-in user +
  a logout function via React context; `ProtectedRoute`/`AdminRoute` wrap
  routes and redirect based on it.
- `usePolling` — the one hook every live-updating screen uses: fetch once,
  then re-fetch on an interval, cleaned up on unmount. Deliberately no
  React Query/SWR — the app's entire async surface is five independent
  polling loops with no shared cache/invalidation needs, so a caching
  library would be a dependency for no real benefit.
- `Topbar`, `Modal` (rendered via a React portal — the topbar has a CSS
  `backdrop-filter`, which creates a containing block that would otherwise
  clip a naively-nested `position: fixed` modal), `ChangePasswordModal`,
  `ConfirmDialog`, `ReasonDialog`, `ToastProvider`.

**The review screen** (`src/features/match/`) is the largest single piece —
a `useReducer`-backed context (`ReviewContext`) holds the rally list and every
edit action (`SET_WINNER`, `SET_REASON`, `SET_TIME`, `ADD_RALLY`,
`DELETE_RALLY`, drag-in-progress vs. drag-committed for the timeline), with
`RallyTimeline`, `RallyTable`, `WinnerSummaryCard`, `ReportCard`,
`CommentsCard`, and `ActionBar` all reading from and dispatching to it —
the one place in the app a context is clearly worth the complexity, given how
many sibling components need the same shared, frequently-edited state.

**Styling**: one global `styles/theme.css` (CSS custom properties for the
whole color palette, including a `prefers-color-scheme: dark` variant) plus
one plain `.css` file per feature area — no CSS Modules, since there are no
cross-page class name collisions to guard against, and plain global classes
keep the visual design a direct, easy-to-diff port.

**Talking to the backend**: `src/lib/api.js` wraps `fetch()` with consistent
error handling; `src/lib/xhrUpload.js` deliberately keeps `XMLHttpRequest`
(not `fetch`) for the video upload specifically, since `fetch` still can't
reliably report upload-progress percentage across browsers.

In dev, `vite.config.js` proxies `/api/*` to the Flask backend so the browser
only ever talks to one origin (session cookies stay correctly scoped, no CORS
setup needed). In production, there's no separate frontend server at all —
`npm run build` produces static files and Flask serves them directly.

---

## The pipeline stages, in detail

`run_full_pipeline.py` is the real entry point — everything below is exactly
what it runs, in order, for a given video. Each numbered doc in
[`docs/`](docs/) covers its stage in full technical depth (inputs, outputs,
every parameter, the reasoning behind each threshold); this is the summary:

| Stage | Script | What it does |
|---|---|---|
| 0 | `TrackNetV3/predict.py` | Shuttle detection — heatmap-based CNN, frame by frame across the whole video |
| 1 | `TrackNetV3/filter_trajectory.py` | Removes spike/teleport/post-smash noise from the raw shuttle track |
| 2 | `analysis/auto_court.py` / `analysis/annotate_court.py` | Court + net geometry — automatic detection, or the manual click UI (now also reachable natively through the web app, not just this standalone tool) |
| 3 | `analysis/player_detection.py` | YOLO11-based player bounding boxes, whole video |
| 4 | `TrackNetV3/fill_gaps.py` | Gap-fills the cleaned shuttle track |
| 5 | `analysis/detect_rallies.py` | Rally segmentation — turns the continuous shuttle track into discrete rally start/end boundaries |
| 6 | `run_unified_pipeline.py` | Win prediction (CNN ensemble + trajectory Random Forest + rule-engine fusion — see `docs/06_win_prediction.md` and `docs/10_evaluation.md` for the real, measured accuracy of this stage), commentary, PDF report |
| 7 | `analysis/annotate_video.py` | Produces the verification video with court/net/players/shuttle overlaid and "RALLY DETECTED" markers |

For a full broadcast (not a pre-trimmed clip), an extra pass happens first:
`analysis/court_presence.py` checks every frame against the annotated camera
angle, `analysis/extract_segments.py` cuts out just the court-present time
ranges, and the expensive stages (0/1/3) run only on those short clips instead
of the entire broadcast — `docs/02_court_presence_and_segmentation.md` covers
why and how.

`fusion_layer.py` and `win_predictor/` (rule engine + trajectory RF + CNN
ensemble) are what actually decide, per rally, who won and why — this is the
single most-tuned part of the system; `docs/10_evaluation.md` documents its
measured accuracy against real ground truth and a real bug found and fixed
this way (a fusion strategy that was actively hurting accuracy, not helping).

---

## Repo structure

```
run_full_pipeline.py       Top-level pipeline entry point
run_unified_pipeline.py    Stage 6 (win prediction + fusion + report) entry point
fusion_layer.py            Combines rule-engine + ML win-reason signals

analysis/                  Court detection, rally segmentation, player detection,
                            frame ranking, verification video
TrackNetV3/                Shuttle detection + trajectory cleaning
win_predictor/             Win-reason prediction (CNN + trajectory RF + rule engine)
BadmintonAnalysis/         AI commentary / highlights / RAG-based match Q&A

webapp/                    The multi-role web app
  server.py  auth.py  db.py  jobs.py  frame_tasks.py    Backend
  frontend/                                             React frontend (source)
  manage.py                                             CLI: create admin/intern accounts

docs/                       Per-stage deep-dive documentation + combined PDF
```

## Further reading

- [`docs/00_overview.md`](docs/00_overview.md) through
  [`docs/08_verification_video.md`](docs/08_verification_video.md) — full
  technical detail per pipeline stage (every function, input, output,
  parameter, and the reasoning behind it).
- [`docs/09_web_review_app.md`](docs/09_web_review_app.md) — covers an
  earlier, single-user iteration of the web app, predating the multi-role
  auth/task-assignment system and the React frontend described above; kept
  for historical context.
- [`docs/10_evaluation.md`](docs/10_evaluation.md) — real, measured accuracy
  of the win-reason/winner prediction against ground truth, methodology, and
  a documented bug fix (a fusion strategy that was quietly hurting accuracy).
- [`INSTALL_AND_RUN.md`](INSTALL_AND_RUN.md) — original CLI-only setup/run
  instructions (predates the web app).
