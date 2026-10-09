"""
jobs.py
-------
Background job runner for run_full_pipeline.py, driven from the web UI.

Design: this does NOT reimplement any pipeline logic -- it shells out to the
exact same run_full_pipeline.py a terminal user would run, and parses its
existing stdout (the "====== N/7  Step name ======" headers it already
prints) to report structured progress to the browser. One job runs at a
time (a single background worker thread pulling from a queue) -- the
pipeline stages are GPU/CPU-heavy, and --court_mode manual briefly needs a
free port 5050 for annotate_court.py's own browser tool, so running two
jobs concurrently isn't something this local, single-user tool supports.

Jobs persist to SQLite (db.py) so the task backlog survives a server
restart. JOBS stays the in-memory read cache everything else in the app
already uses -- it's just populated from the DB at startup now instead of
starting empty.
"""
import json
import queue
import re
import subprocess
import sys
import threading
import time
import uuid
from collections import deque
from pathlib import Path

import db

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Matches run_full_pipeline.py's own _run() step header, e.g. "2b/7  Court-presence mask"
STEP_RE = re.compile(r'^\s*([0-9]+[a-z]?/7)\s+(.+?)\s*$')
DONE_RE = re.compile(r'^\s*DONE\s+--\s+(.+?)\s*$')
FAILED_RE = re.compile(r'^\[FAILED\]\s+(.+)$')
SKIP_RE = re.compile(r'^\[skip\]\s+(.+)$')

class Job:
    def __init__(self, job_id, video_path, match_name, player_a, player_b,
                court_mode, court_type, broadcast, created_by=None,
                status="queued", court_task_status=None):
        self.id = job_id
        self.video_path = video_path
        self.match_name = match_name
        self.player_a = player_a
        self.player_b = player_b
        self.court_mode = court_mode
        self.court_type = court_type
        self.broadcast = broadcast
        self.created_by = created_by

        self.status = status  # pending_court_task | queued | running | done | failed | cancelled
        self.current_step = None  # {"id": "2b/7", "label": "..."}
        self.steps_seen = []
        self.skipped = []
        self.log_tail = deque(maxlen=300)
        self.error = None
        self.created_at = time.time()
        self.match_folder = str(PROJECT_ROOT / match_name)
        self._lock = threading.Lock()
        self._last_persist = 0.0

        # court-annotation task (only meaningful when court_mode == 'manual')
        self.court_task_status = court_task_status or (
            "not_needed" if court_mode != "manual" else "pending")
        self.court_task_assignee = None
        self.court_task_assigned_at = None
        self.court_task_candidates = []  # [{frame_no, score, image_url}, ...]
        self.court_task_selected_idx = 0
        self.court_task_flag_reason = None
        self.court_task_submitted_at = None

        # review task (relevant once status == 'done')
        self.review_task_status = "not_ready"
        self.review_task_assignee = None
        self.review_task_assigned_at = None
        self.review_task_flag_reason = None
        self.review_task_submitted_at = None

    def append_log(self, line):
        with self._lock:
            self.log_tail.append(line)
            m = STEP_RE.match(line)
            if m:
                step = {"id": m.group(1), "label": m.group(2)}
                self.current_step = step
                self.steps_seen.append(step)
            else:
                m = SKIP_RE.match(line)
                if m:
                    self.skipped.append(m.group(1))
                else:
                    m = DONE_RE.match(line)
                    if m:
                        self.status = "done"
                        if self.review_task_status == "not_ready":
                            self.review_task_status = "pending"
        # Persist at most every ~2s while chatty (status changes always
        # persist immediately via their own call sites in jobs.py/server.py;
        # this covers log_tail/steps_seen updates during a run).
        now = time.time()
        if now - self._last_persist > 2:
            self._last_persist = now
            self.persist()

    def to_row(self):
        with self._lock:
            return {
                "id": self.id, "video_path": str(self.video_path),
                "match_name": self.match_name, "player_a": self.player_a,
                "player_b": self.player_b, "court_mode": self.court_mode,
                "court_type": self.court_type, "broadcast": int(self.broadcast),
                "match_folder": self.match_folder,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.created_at)),
                "created_by": self.created_by,
                "status": self.status,
                "current_step_json": json.dumps(self.current_step),
                "steps_seen_json": json.dumps(self.steps_seen),
                "skipped_json": json.dumps(self.skipped),
                "log_tail_json": json.dumps(list(self.log_tail)[-300:]),
                "error": self.error,
                "court_task_status": self.court_task_status,
                "court_task_assignee": self.court_task_assignee,
                "court_task_assigned_at": self.court_task_assigned_at,
                "court_task_candidates_json": json.dumps(self.court_task_candidates),
                "court_task_selected_idx": self.court_task_selected_idx,
                "court_task_flag_reason": self.court_task_flag_reason,
                "court_task_submitted_at": self.court_task_submitted_at,
                "review_task_status": self.review_task_status,
                "review_task_assignee": self.review_task_assignee,
                "review_task_assigned_at": self.review_task_assigned_at,
                "review_task_flag_reason": self.review_task_flag_reason,
                "review_task_submitted_at": self.review_task_submitted_at,
            }

    def persist(self):
        db.jobs_upsert(self.to_row())

    @classmethod
    def from_row(cls, row):
        job = cls(row["id"], row["video_path"], row["match_name"], row["player_a"],
                  row["player_b"], row["court_mode"], row["court_type"],
                  bool(row["broadcast"]), created_by=row["created_by"],
                  status=row["status"], court_task_status=row["court_task_status"])
        job.match_folder = row["match_folder"]
        job.current_step = json.loads(row["current_step_json"]) if row["current_step_json"] else None
        job.steps_seen = json.loads(row["steps_seen_json"]) if row["steps_seen_json"] else []
        job.skipped = json.loads(row["skipped_json"]) if row["skipped_json"] else []
        if row["log_tail_json"]:
            job.log_tail = deque(json.loads(row["log_tail_json"]), maxlen=300)
        job.error = row["error"]
        job.court_task_assignee = row["court_task_assignee"]
        job.court_task_assigned_at = row["court_task_assigned_at"]
        job.court_task_candidates = (json.loads(row["court_task_candidates_json"])
                                     if row["court_task_candidates_json"] else [])
        job.court_task_selected_idx = row["court_task_selected_idx"] or 0
        job.court_task_flag_reason = row["court_task_flag_reason"]
        job.court_task_submitted_at = row["court_task_submitted_at"]
        job.review_task_status = row["review_task_status"]
        job.review_task_assignee = row["review_task_assignee"]
        job.review_task_assigned_at = row["review_task_assigned_at"]
        job.review_task_flag_reason = row["review_task_flag_reason"]
        job.review_task_submitted_at = row["review_task_submitted_at"]
        return job

    def to_dict(self):
        with self._lock:
            return {
                "id": self.id,
                "status": self.status,
                "match_name": self.match_name,
                "player_a": self.player_a,
                "player_b": self.player_b,
                "current_step": self.current_step,
                "steps_seen": list(self.steps_seen),
                "skipped": list(self.skipped),
                "log_tail": list(self.log_tail)[-40:],
                "error": self.error,
                "match_folder": self.match_folder if self.status == "done" else None,
                "queue_position": (_queue_position(self.id)
                                   if self.status == "queued" else None),
                "court_task_status": self.court_task_status,
                "review_task_status": self.review_task_status,
            }


JOBS = {}
_QUEUE = queue.Queue()
# Submission order, oldest first -- queue.Queue doesn't support peeking/
# iterating its contents, and the frontend needs to show "waiting behind N
# other job(s)" rather than a silent queued status with no indication of
# how long that might take (the gap that let 4 duplicate uploads queue up
# unnoticed behind a still-running job in practice).
_pending_order = []
_order_lock = threading.Lock()


def _queue_position(job_id):
    """0 = next up, 1 = one job ahead, etc. Counts only jobs still actually
    ahead in line (queued or running) -- a cancelled/done/failed job ahead
    of this one doesn't make you wait any longer, so it's excluded."""
    with _order_lock:
        try:
            idx = _pending_order.index(job_id)
        except ValueError:
            return None
        ahead = 0
        for jid in _pending_order[:idx]:
            j = JOBS.get(jid)
            if j is not None and j.status in ("queued", "running"):
                ahead += 1
        return ahead


def create_job(video_path, match_name, player_a, player_b, court_mode,
              court_type, broadcast, created_by=None):
    job_id = uuid.uuid4().hex[:12]
    job = Job(job_id, video_path, match_name, player_a, player_b,
             court_mode, court_type, broadcast, created_by=created_by)

    # Manual court mode with no annotation on disk yet needs a human court
    # task before the (multi-hour) pipeline should even be queued -- frame
    # extraction (webapp/frame_tasks.py, called by the route after this
    # returns, to avoid a jobs.py<->frame_tasks.py import cycle) handles
    # that. If court.json already exists (e.g. a retry of a job that
    # already got past annotation), skip straight to queuing exactly like
    # auto mode -- run_full_pipeline.py's own _ensure_court() would skip
    # annotation anyway, so redoing the task here would be pure waste.
    court_json = PROJECT_ROOT / match_name / f"{match_name}_court.json"
    needs_court_task = court_mode == "manual" and not court_json.exists()

    if needs_court_task:
        job.status = "pending_court_task"
        job.court_task_status = "extracting"
        JOBS[job_id] = job
        job.persist()
    else:
        JOBS[job_id] = job
        job.persist()
        with _order_lock:
            _pending_order.append(job_id)
        _QUEUE.put(job_id)
    return job


def enqueue_existing(job_id):
    """Push an already-created job onto the pipeline queue -- the tail end
    of create_job(), factored out so the court-task submit route can
    trigger a run the same way an auto-court upload does."""
    job = JOBS.get(job_id)
    if job is None:
        return False
    job.status = "queued"
    job.persist()
    with _order_lock:
        _pending_order.append(job_id)
    _QUEUE.put(job_id)
    return True


def cancel_job(job_id):
    """Only a job that hasn't started yet can be cancelled -- once
    run_full_pipeline.py is actually running as a subprocess, stopping it
    mid-stage would leave partial/corrupt output files behind, which is a
    bigger problem than just waiting. Returns True if cancelled, False if
    the job doesn't exist or is past the point of no return."""
    job = JOBS.get(job_id)
    if job is None:
        return False
    with job._lock:
        if job.status != "queued":
            return False
        job.status = "cancelled"
    job.persist()
    return True


def _build_cmd(job):
    cmd = [sys.executable, "run_full_pipeline.py",
           "--video", str(job.video_path),
           "--match_name", job.match_name,
           "--player_a", job.player_a,
           "--player_b", job.player_b,
           "--court_mode", job.court_mode,
           "--court_type", job.court_type]
    if job.broadcast:
        cmd.append("--broadcast")
    return cmd


def _run_job(job):
    job.status = "running"
    job.persist()
    cmd = _build_cmd(job)
    job.append_log("  $ " + " ".join(cmd))
    # PYTHONUNBUFFERED, not just bufsize=1 on our end of the pipe: run_full_pipeline.py
    # (and everything IT shells out to in turn -- TrackNetV3/predict.py, etc, which
    # inherit our stdout fd directly rather than being separately piped) is a
    # separate process whose own stdout isn't a tty once piped, so CPython
    # block-buffers it by default and our progress reader sees nothing until a
    # buffer's worth accumulates or the process exits. Setting this in the
    # environment (inherited down through every subprocess in the chain, not
    # just the immediate child) is what actually fixes it -- a plain `-u` on
    # just this one Popen call would not reach the grandchildren.
    import os
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    try:
        proc = subprocess.Popen(cmd, cwd=str(PROJECT_ROOT), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
    except Exception as e:
        job.status = "failed"
        job.error = f"Could not start pipeline: {e}"
        return

    for line in proc.stdout:
        job.append_log(line.rstrip("\n"))
    proc.wait()

    if proc.returncode == 0:
        job.status = "done"
        if job.review_task_status == "not_ready":
            job.review_task_status = "pending"
    else:
        job.status = "failed"
        job.error = "\n".join(list(job.log_tail)[-25:])
    job.persist()


def _worker_loop():
    while True:
        job_id = _QUEUE.get()
        job = JOBS.get(job_id)
        if job is None or job.status == "cancelled":
            continue
        try:
            _run_job(job)
        except Exception as e:
            job.status = "failed"
            job.error = f"Internal error running job: {e}"
            job.persist()


def _load_jobs_from_db():
    """Populate the in-memory JOBS cache from SQLite at startup. Any job
    caught mid-run when the server last stopped can't be resumed (its
    subprocess is gone) -- mark it failed so the existing Retry button
    (which already reuses match_name, so run_full_pipeline.py's own
    step-skip logic picks up where it left off) can recover it."""
    for row in db.jobs_list_all():
        job = Job.from_row(row)
        if job.status in ("queued", "running"):
            job.status = "failed"
            job.error = "Server restarted while this job was running"
            job.persist()
        JOBS[job.id] = job


db.init_db()
_load_jobs_from_db()

_worker_thread = threading.Thread(target=_worker_loop, daemon=True)
_worker_thread.start()
