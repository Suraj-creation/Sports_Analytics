"""
server.py
---------
Flask backend for the end-to-end review UI: upload a video, watch
run_full_pipeline.py process it (real progress, parsed from its own stdout
via jobs.py), then review/correct the result against the real per-rally
output (win_predictions.csv) and the real annotated video.

Corrections are stored separately from the model's own output, in
<match_folder>/corrections.json -- win_predictions.csv itself is never
modified, so the model's original guess and your corrections both survive.

Usage:
    cd badminton-pipeline-v2-release/pipeline_release
    python3 webapp/server.py [--port 8000]
"""
import argparse
import json
import re
import time
import uuid
from pathlib import Path

import cv2
import pandas as pd
from flask import Flask, jsonify, request, send_file, send_from_directory, abort, session
from werkzeug.utils import secure_filename

import auth
import db
import frame_tasks
import jobs

PROJECT_ROOT = jobs.PROJECT_ROOT
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = Flask(__name__, static_folder=None)
app.secret_key = auth.get_secret_key()

REASON_TO_CODE = {"out_of_bounds": "oob", "hits_net": "net", "wins_by_landing": "land"}
CODE_TO_REASON = {v: k for k, v in REASON_TO_CODE.items()}
LOW_CONF_THRESHOLD = 0.6


# ── helpers ──────────────────────────────────────────────────────────────

def _sanitize_match_name(name):
    name = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_") or "match"
    candidate = name
    i = 1
    while (PROJECT_ROOT / candidate).exists() or candidate in {
        j.match_name for j in jobs.JOBS.values()
    }:
        i += 1
        candidate = f"{name}_{i}"
    return candidate


def _video_meta(video_path):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return {"fps": fps, "total_frames": total, "duration": total / fps if fps else 0}


def _rallies_from_predictions(match_folder, player_a, player_b, fps):
    csv_path = Path(match_folder) / "win_predictions.csv"
    if not csv_path.exists():
        return []
    df = pd.read_csv(csv_path)
    sa_col = f"score_{player_a[:8]}"
    sb_col = f"score_{player_b[:8]}"
    rallies = []
    for _, r in df.iterrows():
        winner_name = str(r.get("winner", ""))
        if winner_name == player_a:
            winner = "A"
        elif winner_name == player_b:
            winner = "B"
        else:
            winner = None
        conf = r.get("cnn_conf")
        conf = float(conf) if pd.notna(conf) else None
        flagged = conf is not None and conf < LOW_CONF_THRESHOLD
        rallies.append({
            "id": int(r["rally_idx"]),
            "start": round(int(r["start_frame"]) / fps, 2),
            "end": round(int(r["end_frame"]) / fps, 2),
            "winner": winner,
            "reason": REASON_TO_CODE.get(str(r.get("win_reason"))),
            "source": "auto",
            "flagged": flagged,
            "note": (f"Model confidence {conf:.0%} ({r.get('reason_src')}) -- worth a second look"
                    if flagged else None),
            "score_after": [
                int(r[sa_col]) if sa_col in df.columns and pd.notna(r[sa_col]) else None,
                int(r[sb_col]) if sb_col in df.columns and pd.notna(r[sb_col]) else None,
            ],
        })
    return rallies


def _corrections_path(match_folder):
    return Path(match_folder) / "corrections.json"


# ── static frontend ─────────────────────────────────────────────────────
# The React SPA (webapp/frontend/) owns all page routing client-side now --
# gating the HTML shell server-side would be theater once every page ships
# the same JS bundle to everyone regardless; the real boundary is (and
# always was) the @auth.login_required/@auth.admin_required decorators on
# the /api/* routes below, which are unchanged. ProtectedRoute/AdminRoute
# in the React app redirect for UX only.
#
# /static/<path:filename> stays pointed at the OLD vanilla frontend --
# unreferenced by anything now, kept only as an instant-rollback path
# (see docs/webapp frontend migration notes) until it's deleted for good.

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


FRONTEND_DIST = Path(__file__).resolve().parent / "frontend" / "dist"


# ── auth ─────────────────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def api_login():
    body = request.get_json(force=True, silent=True) or {}
    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    user = db.users_get_by_username(username)
    if not user or not user["active"] or not auth.verify_password(password, user["password_hash"]):
        return jsonify(error="Invalid username or password"), 401
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["username"] = user["username"]
    return jsonify(username=user["username"], role=user["role"])


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify(ok=True)


@app.route("/api/me")
def api_me():
    user = auth.current_user()
    if user is None:
        return jsonify(error="Not logged in"), 401
    return jsonify(username=user["username"], role=user["role"])


@app.route("/api/me/change-password", methods=["POST"])
@auth.login_required
def api_change_password():
    # Self-service: anyone (admin or intern) changes their own password by
    # proving they know the current one -- admin only sets the *initial*
    # password when creating an account (POST /api/admin/users); after
    # that it's the account owner's, not something an admin resets here.
    user = auth.current_user()
    body = request.get_json(force=True, silent=True) or {}
    old_password = body.get("old_password") or ""
    new_password = body.get("new_password") or ""
    if not auth.verify_password(old_password, user["password_hash"]):
        return jsonify(error="Current password is incorrect"), 400
    if len(new_password) < 8:
        return jsonify(error="New password must be at least 8 characters"), 400
    db.users_set_password(user["id"], auth.hash_password(new_password))
    return jsonify(ok=True)


# ── admin ────────────────────────────────────────────────────────────────

@app.route("/api/admin/jobs")
@auth.admin_required
def api_admin_jobs():
    # Username lookups done in Python, not SQL -- the users table is small
    # (a handful of accounts), so an in-memory dict merge is simpler here
    # than JOIN syntax against sqlite3.Row for three separate FK columns.
    users_by_id = {u["id"]: u["username"] for u in db.users_list()}

    def _name(uid):
        return users_by_id.get(uid)

    out = []
    for job in sorted(jobs.JOBS.values(), key=lambda j: j.created_at, reverse=True):
        d = job.to_dict()
        d["created_by"] = _name(job.created_by)
        d["court_task_assignee"] = job.court_task_assignee
        d["court_task_assignee_name"] = _name(job.court_task_assignee)
        d["review_task_assignee"] = job.review_task_assignee
        d["review_task_assignee_name"] = _name(job.review_task_assignee)
        d["court_task_flag_reason"] = job.court_task_flag_reason
        d["review_task_flag_reason"] = job.review_task_flag_reason
        d["court_mode"] = job.court_mode
        out.append(d)
    return jsonify(jobs=out)


@app.route("/api/admin/users")
@auth.admin_required
def api_admin_users_list():
    return jsonify(users=[
        {"id": u["id"], "username": u["username"], "role": u["role"], "active": bool(u["active"])}
        for u in db.users_list()
    ])


@app.route("/api/admin/users", methods=["POST"])
@auth.admin_required
def api_admin_users_create():
    body = request.get_json(force=True, silent=True) or {}
    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    if not username or not password:
        return jsonify(error="username and password are required"), 400
    if db.users_get_by_username(username):
        return jsonify(error="That username is already taken"), 400
    # Role is deliberately hard-coded to 'intern' here -- creating a
    # second admin stays a CLI-only action (manage.py) so there's no
    # unauthenticated-adjacent web surface for privilege escalation.
    uid = db.users_create(username, auth.hash_password(password), "intern")
    return jsonify(id=uid, username=username, role="intern")


@app.route("/api/admin/users/<int:user_id>/deactivate", methods=["POST"])
@auth.admin_required
def api_admin_users_deactivate(user_id):
    db.users_deactivate(user_id)
    return jsonify(ok=True)


def _assign_task(job_id, task, intern_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    intern = db.users_get(intern_id)
    if intern is None or not intern["active"]:
        return jsonify(error="Unknown or inactive user"), 400
    now = db.now()
    if task == "court":
        if job.court_task_status == "submitted":
            return jsonify(error="Court task already submitted"), 400
        if job.court_task_status == "not_needed":
            return jsonify(error="This job doesn't need a court-annotation task (court_mode=auto)"), 400
        job.court_task_assignee = intern_id
        job.court_task_assigned_at = now
        if job.court_task_status == "flagged":
            job.court_task_status = "pending"
            job.court_task_flag_reason = None
        elif job.court_task_status in ("extracting", "extraction_failed"):
            pass  # assignee recorded now, task shows up once extraction finishes
        else:
            job.court_task_status = "pending"
    else:
        if job.review_task_status == "submitted":
            return jsonify(error="Review task already submitted"), 400
        if job.review_task_status == "not_ready":
            return jsonify(error="Pipeline hasn't finished yet -- review isn't ready"), 400
        job.review_task_assignee = intern_id
        job.review_task_assigned_at = now
        if job.review_task_status == "flagged":
            job.review_task_flag_reason = None
        job.review_task_status = "pending"
    job.persist()
    return jsonify(job.to_dict())


@app.route("/api/admin/jobs/<job_id>/assign-court", methods=["POST"])
@auth.admin_required
def api_admin_assign_court(job_id):
    body = request.get_json(force=True, silent=True) or {}
    return _assign_task(job_id, "court", body.get("intern_id"))


@app.route("/api/admin/jobs/<job_id>/assign-review", methods=["POST"])
@auth.admin_required
def api_admin_assign_review(job_id):
    body = request.get_json(force=True, silent=True) or {}
    return _assign_task(job_id, "review", body.get("intern_id"))


# ── intern tasks ──────────────────────────────────────────────────────

@app.route("/api/my-tasks")
@auth.login_required
def api_my_tasks():
    uid = session["user_id"]

    def _job_summary(job, kind):
        return {
            "id": job.id, "match_name": job.match_name,
            "player_a": job.player_a, "player_b": job.player_b,
            "status": job.court_task_status if kind == "court" else job.review_task_status,
        }

    court = [_job_summary(j, "court") for j in jobs.JOBS.values()
             if j.court_task_assignee == uid and j.court_task_status in ("pending", "in_progress")]
    review = [_job_summary(j, "review") for j in jobs.JOBS.values()
              if j.review_task_assignee == uid and j.review_task_status in ("pending", "in_progress")]
    court.sort(key=lambda d: d["match_name"])
    review.sort(key=lambda d: d["match_name"])
    return jsonify(court_tasks=court, review_tasks=review)


def _can_access_job(job, user):
    return (user["role"] == "admin"
            or user["id"] in (job.created_by, job.court_task_assignee, job.review_task_assignee))


# ── native court-annotation task ────────────────────────────────────────
# Replaces analysis/annotate_court.py's standalone port-5050 tool for the
# task-based flow -- that tool is single-session (one live video, one
# blocking subprocess) and can't be "assigned" to a specific intern, so
# this reimplements the same 8-point click interaction against a
# pre-extracted candidate frame instead. LABELS/DESCS/COLORS and the
# _save() schema are copied from annotate_court.py, not imported -- that
# module does file/CLI/server work at module level (not gated by
# __main__), so importing it would try to start its own HTTP server.
# Keep these in sync with analysis/annotate_court.py if that ever changes.
COURT_LABELS = ['TL', 'TR', 'BR', 'BL', 'NL', 'NR', 'CL', 'CR']
COURT_DESCS = [
    'Top-Left court corner', 'Top-Right court corner',
    'Bottom-Right court corner', 'Bottom-Left court corner',
    'Left net post base (ground)', 'Right net post base (ground)',
    'Left net cable top', 'Right net cable top',
]
COURT_COLORS = ['#00ff64', '#00b4ff', '#ff0000', '#ff5000',
               '#b400ff', '#ff00b4', '#00ffff', '#ffff00']


def _court_task_job(job_id, user):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    if user["role"] != "admin" and job.court_task_assignee != user["id"]:
        abort(403)
    return job


@app.route("/api/court-task/<job_id>")
@auth.login_required
def api_court_task_get(job_id):
    job = _court_task_job(job_id, auth.current_user())
    if job.court_task_status not in ("pending", "in_progress"):
        return jsonify(error=f"Task not available (status: {job.court_task_status})"), 409
    if job.court_task_status == "pending":
        job.court_task_status = "in_progress"
        job.persist()
    return jsonify(
        match_name=job.match_name,
        candidates=job.court_task_candidates,
        selected_idx=job.court_task_selected_idx,
        labels=COURT_LABELS, descs=COURT_DESCS, colors=COURT_COLORS,
    )


@app.route("/api/court-task/<job_id>/frame/<int:idx>.jpg")
@auth.login_required
def api_court_task_frame(job_id, idx):
    job = _court_task_job(job_id, auth.current_user())
    if idx < 0 or idx >= len(job.court_task_candidates):
        abort(404)
    frame_no = job.court_task_candidates[idx]["frame_no"]
    path = frame_tasks.CANDIDATES_DIR / job_id / f"{frame_no}.jpg"
    if not path.exists():
        abort(404)
    return send_file(path, mimetype="image/jpeg")


@app.route("/api/court-task/<job_id>/select-candidate", methods=["POST"])
@auth.login_required
def api_court_task_select(job_id):
    job = _court_task_job(job_id, auth.current_user())
    body = request.get_json(force=True, silent=True) or {}
    idx = body.get("idx")
    if not isinstance(idx, int) or idx < 0 or idx >= len(job.court_task_candidates):
        return jsonify(error="Invalid candidate index"), 400
    job.court_task_selected_idx = idx
    job.persist()
    return jsonify(ok=True)


@app.route("/api/court-task/<job_id>/submit", methods=["POST"])
@auth.login_required
def api_court_task_submit(job_id):
    job = _court_task_job(job_id, auth.current_user())
    if job.court_task_status not in ("pending", "in_progress"):
        return jsonify(error=f"Task not available (status: {job.court_task_status})"), 409
    body = request.get_json(force=True, silent=True) or {}
    points = body.get("points")
    if not isinstance(points, list) or len(points) != 8 or \
       not all(isinstance(p, list) and len(p) == 2 for p in points):
        return jsonify(error="points must be a list of 8 [x, y] pairs"), 400

    cand = job.court_task_candidates[job.court_task_selected_idx]
    TL, TR, BR, BL, NL, NR, CL, CR = points
    data = {
        "frame_no": cand["frame_no"],
        "frame_size": {"width": cand["width"], "height": cand["height"]},
        "corners": {"TL": TL, "TR": TR, "BR": BR, "BL": BL},
        "net": {
            "net_Y": (NL[1] + NR[1]) / 2, "net_top_Y": (CL[1] + CR[1]) / 2,
            "left_bottom": NL, "right_bottom": NR,
            "cable_left": CL, "cable_right": CR,
        },
        "source": "manual",
    }
    match_folder = Path(job.match_folder)
    match_folder.mkdir(parents=True, exist_ok=True)
    court_json_path = match_folder / f"{job.match_name}_court.json"
    court_json_path.write_text(json.dumps(data, indent=2))

    job.court_task_status = "submitted"
    job.court_task_submitted_at = db.now()
    job.persist()
    jobs.enqueue_existing(job.id)
    return jsonify(ok=True)


@app.route("/api/court-task/<job_id>/flag", methods=["POST"])
@auth.login_required
def api_court_task_flag(job_id):
    job = _court_task_job(job_id, auth.current_user())
    if job.court_task_status not in ("pending", "in_progress"):
        return jsonify(error=f"Task not available (status: {job.court_task_status})"), 409
    body = request.get_json(force=True, silent=True) or {}
    reason = (body.get("reason") or "").strip()[:500]
    if not reason:
        return jsonify(error="A reason is required"), 400
    # Unassigned so it drops out of this intern's queue and shows up as
    # needs-attention for the admin to hand to someone else -- "forward
    # next" without a scheduling system, just a manual reassignment.
    job.court_task_status = "flagged"
    job.court_task_flag_reason = reason
    job.court_task_assignee = None
    job.persist()
    return jsonify(ok=True)


@app.route("/api/jobs/<job_id>/flag-review", methods=["POST"])
@auth.login_required
def api_job_flag_review(job_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    user = auth.current_user()
    if user["role"] != "admin" and job.review_task_assignee != user["id"]:
        abort(403)
    if job.review_task_status not in ("pending", "in_progress"):
        return jsonify(error=f"Task not available (status: {job.review_task_status})"), 409
    body = request.get_json(force=True, silent=True) or {}
    reason = (body.get("reason") or "").strip()[:500]
    if not reason:
        return jsonify(error="A reason is required"), 400
    job.review_task_status = "flagged"
    job.review_task_flag_reason = reason
    job.review_task_assignee = None
    job.persist()
    return jsonify(ok=True)


@app.route("/api/admin/jobs/<job_id>/retry-extraction", methods=["POST"])
@auth.admin_required
def api_admin_retry_extraction(job_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    if job.court_task_status != "extraction_failed":
        return jsonify(error="Only a failed extraction can be retried"), 400
    job.court_task_status = "extracting"
    job.error = None
    job.persist()
    frame_tasks.submit(job.id)
    return jsonify(job.to_dict())


# ── job lifecycle ───────────────────────────────────────────────────────

@app.route("/api/jobs", methods=["POST"])
@auth.login_required
def api_create_job():
    f = request.files.get("video")
    if not f or f.filename == "":
        return jsonify(error="No video file provided"), 400

    match_name = _sanitize_match_name(
        request.form.get("match_name") or Path(secure_filename(f.filename)).stem)
    player_a = (request.form.get("player_a") or "Player A").strip()[:40]
    player_b = (request.form.get("player_b") or "Player B").strip()[:40]
    court_mode = request.form.get("court_mode") or "auto"
    court_type = request.form.get("court_type") or "singles"
    broadcast = request.form.get("broadcast") in ("true", "1", "on")

    if court_mode not in ("auto", "manual"):
        return jsonify(error="court_mode must be auto or manual"), 400

    dest = jobs.UPLOAD_DIR / f"{uuid.uuid4().hex[:8]}_{secure_filename(f.filename)}"
    f.save(dest)

    job = jobs.create_job(dest, match_name, player_a, player_b, court_mode,
                          court_type, broadcast, created_by=session["user_id"])
    if job.status == "pending_court_task":
        frame_tasks.submit(job.id)
    return jsonify(job.to_dict())


@app.route("/api/jobs/batch", methods=["POST"])
@auth.admin_required
def api_create_jobs_batch():
    files = request.files.getlist("video")
    if not files:
        return jsonify(error="No video files provided"), 400

    # Shared settings for the whole batch (bulk intake, not per-match
    # metadata entry) -- match_name is derived per-file from its filename,
    # players default to generic names editable later from the review
    # screen's own player-name fields is out of scope here; this route is
    # for getting many videos queued for court-annotation quickly.
    player_a = (request.form.get("player_a") or "Player A").strip()[:40]
    player_b = (request.form.get("player_b") or "Player B").strip()[:40]
    court_mode = request.form.get("court_mode") or "auto"
    court_type = request.form.get("court_type") or "singles"
    broadcast = request.form.get("broadcast") in ("true", "1", "on")
    if court_mode not in ("auto", "manual"):
        return jsonify(error="court_mode must be auto or manual"), 400

    created = []
    errors = []
    for f in files:
        if not f or f.filename == "":
            continue
        try:
            match_name = _sanitize_match_name(Path(secure_filename(f.filename)).stem)
            dest = jobs.UPLOAD_DIR / f"{uuid.uuid4().hex[:8]}_{secure_filename(f.filename)}"
            f.save(dest)
            job = jobs.create_job(dest, match_name, player_a, player_b, court_mode,
                                  court_type, broadcast, created_by=session["user_id"])
            if job.status == "pending_court_task":
                frame_tasks.submit(job.id)
            created.append(job.to_dict())
        except Exception as e:
            # One bad file in a 50-file batch shouldn't abort the rest.
            errors.append({"filename": f.filename, "error": str(e)})
    return jsonify(created=created, errors=errors)


@app.route("/api/jobs/<job_id>")
@auth.login_required
def api_job_status(job_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    if not _can_access_job(job, auth.current_user()):
        abort(403)
    return jsonify(job.to_dict())


@app.route("/api/jobs/<job_id>/retry", methods=["POST"])
@auth.login_required
def api_job_retry(job_id):
    old = jobs.JOBS.get(job_id)
    if old is None:
        abort(404)
    if not _can_access_job(old, auth.current_user()):
        abort(403)
    if old.status != "failed":
        return jsonify(error="Only a failed job can be retried"), 400
    # Deliberately reuses old.match_name (not a fresh sanitized name) --
    # run_full_pipeline.py's own step-skip logic then picks up right where
    # it failed instead of redoing already-completed steps. This is the
    # whole reason NOT to route retries through /api/jobs (which always
    # avoids reusing an existing match_folder, correct for a genuinely new
    # upload but wrong here).
    new_job = jobs.create_job(old.video_path, old.match_name, old.player_a,
                              old.player_b, old.court_mode, old.court_type,
                              old.broadcast, created_by=old.created_by)
    return jsonify(new_job.to_dict())


@app.route("/api/jobs/<job_id>/cancel", methods=["POST"])
@auth.login_required
def api_job_cancel(job_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    if not _can_access_job(job, auth.current_user()):
        abort(403)
    if not jobs.cancel_job(job_id):
        return jsonify(error="Only a still-queued job can be cancelled "
                             "(this one is already running or finished)"), 400
    return jsonify(job.to_dict())


# ── review data ──────────────────────────────────────────────────────────

@app.route("/api/jobs/<job_id>/data")
@auth.login_required
def api_job_data(job_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    if not _can_access_job(job, auth.current_user()):
        abort(403)
    if job.status != "done":
        return jsonify(error="Job not finished yet", status=job.status), 409

    match_folder = Path(job.match_folder)
    video_path = match_folder / f"{job.match_name}_annotated.mp4"
    meta = _video_meta(video_path) or _video_meta(match_folder / f"{job.match_name}.mp4")
    if meta is None:
        return jsonify(error="Could not read output video"), 500

    corr_path = _corrections_path(match_folder)
    if corr_path.exists():
        saved = json.loads(corr_path.read_text())
        rallies = saved.get("rallies", [])
        comments = saved.get("comments", "")
        confirmed = saved.get("confirmed", False)
    else:
        rallies = _rallies_from_predictions(match_folder, job.player_a, job.player_b, meta["fps"])
        comments = ""
        confirmed = False

    presence_csv = match_folder / f"{job.match_name}_court_presence.csv"
    presence_pct = None
    if presence_csv.exists():
        pdf = pd.read_csv(presence_csv)
        if len(pdf):
            presence_pct = round(100 * pdf["court_present"].mean(), 1)

    unified_dir = match_folder / "unified"
    report_text = None
    report_txt_path = unified_dir / "analysis_report.txt"
    if report_txt_path.exists():
        report_text = report_txt_path.read_text(encoding="utf-8", errors="ignore")
    pdf_files = sorted(unified_dir.glob("*.pdf")) if unified_dir.exists() else []

    return jsonify(
        player_a=job.player_a,
        player_b=job.player_b,
        rallies=rallies,
        comments=comments,
        confirmed=confirmed,
        total_duration=meta["duration"],
        fps=meta["fps"],
        presence_pct=presence_pct,
        video_url=f"/api/jobs/{job_id}/video",
        has_corrections=corr_path.exists(),
        report_text=report_text,
        report_pdf_url=f"/api/jobs/{job_id}/report.pdf" if pdf_files else None,
    )


@app.route("/api/jobs/<job_id>/report.pdf")
@auth.login_required
def api_job_report_pdf(job_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    if not _can_access_job(job, auth.current_user()):
        abort(403)
    unified_dir = Path(job.match_folder) / "unified"
    pdf_files = sorted(unified_dir.glob("*.pdf")) if unified_dir.exists() else []
    if not pdf_files:
        abort(404)
    # Newest if somehow more than one (timestamped filenames, re-runs) --
    # not overwritten by run_unified_pipeline.py, so a retried job could
    # in principle leave more than one behind.
    return send_file(max(pdf_files, key=lambda p: p.stat().st_mtime),
                     mimetype="application/pdf", as_attachment=False,
                     download_name=f"{job.match_name}_report.pdf")


@app.route("/api/jobs/<job_id>/video")
@auth.login_required
def api_job_video(job_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    if not _can_access_job(job, auth.current_user()):
        abort(403)
    match_folder = Path(job.match_folder)
    video_path = match_folder / f"{job.match_name}_annotated.mp4"
    if not video_path.exists():
        video_path = match_folder / f"{job.match_name}.mp4"
    if not video_path.exists():
        abort(404)
    return send_file(video_path, conditional=True, mimetype="video/mp4")


@app.route("/api/jobs/<job_id>/corrections", methods=["GET", "POST"])
@auth.login_required
def api_job_corrections(job_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        abort(404)
    if not _can_access_job(job, auth.current_user()):
        abort(403)
    match_folder = Path(job.match_folder)
    corr_path = _corrections_path(match_folder)

    if request.method == "GET":
        if not corr_path.exists():
            return jsonify(exists=False)
        return jsonify(exists=True, **json.loads(corr_path.read_text()))

    body = request.get_json(force=True, silent=True) or {}
    rallies = body.get("rallies", [])
    comments = body.get("comments", "")
    confirmed = bool(body.get("confirmed", False))
    for r in rallies:
        if r.get("reason") not in (None, "oob", "net", "land"):
            return jsonify(error=f"invalid reason code: {r.get('reason')}"), 400
        if r.get("winner") not in (None, "A", "B"):
            return jsonify(error=f"invalid winner code: {r.get('winner')}"), 400

    payload = {
        "rallies": rallies,
        "comments": comments,
        "confirmed": confirmed,
        "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    match_folder.mkdir(parents=True, exist_ok=True)
    corr_path.write_text(json.dumps(payload, indent=2))

    # Task bookkeeping (separate from corrections.json's own `confirmed`
    # flag) -- who's working on the review task and whether it's done.
    if confirmed:
        job.review_task_status = "submitted"
        job.review_task_submitted_at = db.now()
    elif job.review_task_status == "pending":
        job.review_task_status = "in_progress"
    job.persist()

    return jsonify(ok=True, **payload)


# ── React SPA (must stay registered last so it never shadows /api/*) ──────

@app.route("/assets/<path:filename>")
def frontend_assets(filename):
    return send_from_directory(FRONTEND_DIST / "assets", filename)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def spa(path):
    # Serve a real file if one exists at this path (e.g. a favicon);
    # otherwise fall back to index.html so client-side routes like /admin
    # or /court-task/<id> survive a hard refresh or direct navigation.
    candidate = FRONTEND_DIST / path
    if path and candidate.is_file():
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, "index.html")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()
    if db.users_count() == 0:
        print("\n  No user accounts exist yet. Create the first admin with:\n"
             "    python3 manage.py create-admin --username <name> --password <pw>\n")
    print(f"\n  Rally Review server -- http://localhost:{args.port}\n")
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)


if __name__ == "__main__":
    main()
