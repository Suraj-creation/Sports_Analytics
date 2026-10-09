"""
db.py
-----
SQLite-backed persistence for users and jobs, so the task backlog survives
a server restart (the old jobs.py kept everything in an in-memory dict only).

WAL mode lets the pipeline worker thread write job progress while Flask
request threads read concurrently without SQLITE_BUSY errors. Connections
are short-lived (opened per call) -- volume here is tens of jobs and a
handful of users, so pooling would be complexity with no payoff.
"""
import json
import sqlite3
import threading
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "app.db"
_LOCK = threading.RLock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role          TEXT NOT NULL CHECK(role IN ('admin','intern')),
  active        INTEGER NOT NULL DEFAULT 1,
  created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
  id                          TEXT PRIMARY KEY,
  video_path                  TEXT NOT NULL,
  match_name                  TEXT NOT NULL,
  player_a                    TEXT NOT NULL,
  player_b                    TEXT NOT NULL,
  court_mode                  TEXT NOT NULL,
  court_type                  TEXT NOT NULL,
  broadcast                   INTEGER NOT NULL,
  match_folder                TEXT NOT NULL,
  created_at                  TEXT NOT NULL,
  created_by                  INTEGER REFERENCES users(id),

  status                      TEXT NOT NULL,
  current_step_json           TEXT,
  steps_seen_json             TEXT,
  skipped_json                TEXT,
  log_tail_json               TEXT,
  error                       TEXT,

  court_task_status           TEXT NOT NULL DEFAULT 'not_needed',
  court_task_assignee         INTEGER REFERENCES users(id),
  court_task_assigned_at      TEXT,
  court_task_candidates_json  TEXT,
  court_task_selected_idx     INTEGER DEFAULT 0,
  court_task_flag_reason      TEXT,
  court_task_submitted_at     TEXT,

  review_task_status          TEXT NOT NULL DEFAULT 'not_ready',
  review_task_assignee        INTEGER REFERENCES users(id),
  review_task_assigned_at     TEXT,
  review_task_flag_reason     TEXT,
  review_task_submitted_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_jobs_court_assignee  ON jobs(court_task_assignee, court_task_status);
CREATE INDEX IF NOT EXISTS idx_jobs_review_assignee ON jobs(review_task_assignee, review_task_status);
"""


def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _LOCK, conn() as c:
        c.execute("PRAGMA journal_mode=WAL")
        c.executescript(SCHEMA)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


# ── users ────────────────────────────────────────────────────────────────

def users_create(username, password_hash, role):
    with _LOCK, conn() as c:
        cur = c.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?,?,?,?)",
            (username, password_hash, role, now()))
        return cur.lastrowid


def users_get(user_id):
    with _LOCK, conn() as c:
        row = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def users_get_by_username(username):
    with _LOCK, conn() as c:
        row = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return dict(row) if row else None


def users_list(role=None, active_only=False):
    q = "SELECT * FROM users"
    conds, params = [], []
    if role:
        conds.append("role=?"); params.append(role)
    if active_only:
        conds.append("active=1")
    if conds:
        q += " WHERE " + " AND ".join(conds)
    q += " ORDER BY username"
    with _LOCK, conn() as c:
        return [dict(r) for r in c.execute(q, params).fetchall()]


def users_deactivate(user_id):
    with _LOCK, conn() as c:
        c.execute("UPDATE users SET active=0 WHERE id=?", (user_id,))


def users_set_password(user_id, password_hash):
    with _LOCK, conn() as c:
        c.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))


def users_count():
    with _LOCK, conn() as c:
        return c.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]


# ── jobs ─────────────────────────────────────────────────────────────────

_JOB_COLUMNS = [
    "id", "video_path", "match_name", "player_a", "player_b", "court_mode",
    "court_type", "broadcast", "match_folder", "created_at", "created_by",
    "status", "current_step_json", "steps_seen_json", "skipped_json",
    "log_tail_json", "error",
    "court_task_status", "court_task_assignee", "court_task_assigned_at",
    "court_task_candidates_json", "court_task_selected_idx", "court_task_flag_reason",
    "court_task_submitted_at",
    "review_task_status", "review_task_assignee", "review_task_assigned_at",
    "review_task_flag_reason", "review_task_submitted_at",
]


def jobs_upsert(row: dict):
    """row must contain every column in _JOB_COLUMNS (missing keys -> None)."""
    values = [row.get(c) for c in _JOB_COLUMNS]
    placeholders = ",".join("?" * len(_JOB_COLUMNS))
    updates = ",".join(f"{c}=excluded.{c}" for c in _JOB_COLUMNS if c != "id")
    with _LOCK, conn() as c:
        c.execute(
            f"INSERT INTO jobs ({','.join(_JOB_COLUMNS)}) VALUES ({placeholders}) "
            f"ON CONFLICT(id) DO UPDATE SET {updates}",
            values)


def jobs_get(job_id):
    with _LOCK, conn() as c:
        row = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None


def jobs_list_all():
    with _LOCK, conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()]


def jobs_list_for_assignee(column, user_id, statuses):
    placeholders = ",".join("?" * len(statuses))
    with _LOCK, conn() as c:
        rows = c.execute(
            f"SELECT * FROM jobs WHERE {column}=? AND court_task_status IN ({placeholders}) "
            f"ORDER BY court_task_assigned_at ASC" if column == "court_task_assignee" else
            f"SELECT * FROM jobs WHERE {column}=? AND review_task_status IN ({placeholders}) "
            f"ORDER BY review_task_assigned_at ASC",
            [user_id, *statuses]).fetchall()
        return [dict(r) for r in rows]
