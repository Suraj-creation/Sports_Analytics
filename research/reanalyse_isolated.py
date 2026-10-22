"""Explicit operator command: back up/reanalyse, or only restart the application."""

import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import httpx

from bai_engine.config import get_settings

ROOT = Path(__file__).resolve().parents[1]
SID = "01M5EXGZNEVGYAJ3AR6CJS5ZG9"
backup = ROOT / "data/court-evaluation/before-fixing-one"
restart_only = "--restart-only" in sys.argv
if restart_only:
    with sqlite3.connect(ROOT / "data/sessions.sqlite") as repository:
        if repository.execute("select 1 from sessions where status='analysing' limit 1").fetchone():
            raise RuntimeError("Wait for active analysis before restarting the application")
if not restart_only and backup.exists() and "--keep-original-backup" not in sys.argv:
    raise RuntimeError("Backup already exists; do not repeat the reanalysis command accidentally")
if not restart_only and not backup.exists():
    shutil.copytree(ROOT / "data/sessions" / SID, backup)
    with (
        sqlite3.connect(ROOT / "data/sessions" / SID / "events.sqlite") as src,
        sqlite3.connect(backup / "events.sqlite") as dst,
    ):
        src.backup(dst)
    with (
        sqlite3.connect(ROOT / "data/sessions.sqlite") as src,
        sqlite3.connect(backup / "sessions-repository.sqlite") as dst,
    ):
        src.backup(dst)
pid_path = ROOT.parent / "server.pid"
pid = int(pid_path.read_text().strip())
cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode()
if str(ROOT / ".venv/bin/bai") not in cmd or "serve --port 8010" not in cmd:
    raise RuntimeError("Server PID no longer matches the expected application")
os.kill(pid, signal.SIGTERM)
for _ in range(100):
    if not Path(f"/proc/{pid}").exists():
        break
    time.sleep(0.2)
else:
    raise RuntimeError("Server did not shut down cleanly")
with (ROOT.parent / "server.log").open("ab") as log:
    child = subprocess.Popen(
        ["bash", str(ROOT.parent / "start-server.sh")],
        cwd=ROOT,
        stdout=log,
        stderr=log,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
pid_path.write_text(str(child.pid) + "\n")
with httpx.Client(base_url="http://127.0.0.1:8010", timeout=15) as client:
    for _ in range(100):
        try:
            if client.get("/").status_code == 200:
                break
        except httpx.TransportError:
            pass
        time.sleep(0.2)
    else:
        raise RuntimeError("Restarted server did not become ready")
    secret = get_settings().passphrase
    auth = client.post("/api/auth/login", json={"passphrase": secret.get_secret_value() if secret else ""})
    auth.raise_for_status()
    if restart_only:
        response = client.get(f"/api/sessions/{SID}")
        response.raise_for_status()
        session = response.json()
        checks = {}
        for path in ("events?types=calibration", "state", "analytics", "tracks?from=22000&to=22060"):
            checked = client.get(f"/api/sessions/{SID}/{path}")
            checked.raise_for_status()
            checks[path] = {"status": checked.status_code, "bytes": len(checked.content)}
        print(
            json.dumps(
                {
                    "server_pid": child.pid,
                    "session_status": session["status"],
                    "analysed_frames": session["analysed_frames"],
                    "api_checks": checks,
                }
            )
        )
        sys.exit(0)
    csrf = auth.json().get("csrf")
    response = client.post(f"/api/sessions/{SID}/reanalyse", headers={"X-CSRF-Token": csrf} if csrf else {})
    response.raise_for_status()
    print(json.dumps({"server_pid": child.pid, "backup": str(backup), "reanalysis": response.json()}))
