"""Offline end-to-end benchmark; source sessions are opened read-only and never reset."""

import argparse
import collections
import hashlib
import json
import os
import pathlib
import shutil
import sqlite3
import subprocess
import threading
import time

import msgpack

from bai_engine.bus import LocalBus
from bai_engine.config import Settings
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.runtime.runner import SessionRunner
from bai_engine.schema import Event, Session, SessionStatus
from bai_engine.store import SessionRepository

p = argparse.ArgumentParser()
p.add_argument("--source-data", type=pathlib.Path, required=True)
p.add_argument("--session-id", required=True)
p.add_argument("--output", type=pathlib.Path, required=True)
p.add_argument("--label", required=True)
p.add_argument("--profile", help="Explicit profile override for an isolated candidate run")
p.add_argument("--runtime-root", type=pathlib.Path, help="Existing model/config root when source data is a backup")
args = p.parse_args()
source = args.source_data.resolve()
out = args.output.resolve()
if out.exists() or out.is_relative_to(source) or source.is_relative_to(out):
    raise ValueError("Output must be fresh and outside source data")
if not args.session_id.isalnum():
    raise ValueError("Invalid session ID")
with sqlite3.connect(f"file:{source}/sessions.sqlite?mode=ro", uri=True) as con:
    row = con.execute("select body from sessions where session_id=?", (args.session_id,)).fetchone()
    if row is None:
        raise ValueError("Unknown session")
    session = Session.model_validate_json(row[0])
with sqlite3.connect(f"file:{source}/sessions/{args.session_id}/events.sqlite?mode=ro", uri=True) as con:
    row = con.execute(
        "select body from events where type='calibration' and status != 'retracted' "
        "and event_id not in (select supersedes from events where supersedes is not null) "
        "order by seq desc limit 1"
    ).fetchone()
    if row is None:
        raise ValueError("Source has no current calibration")
    calibration = Event.model_validate_json(row[0])
media_source = source / "media" / session.source.sha256
out.mkdir(parents=True)
data = out / "data"
(data / "media").mkdir(parents=True)
shutil.copytree(media_source, data / "media" / session.source.sha256)
proxy = data / "media" / session.source.sha256 / "proxy.mp4"
with proxy.open("rb") as stream:
    proxy_sha = hashlib.file_digest(stream, "sha256").hexdigest()
repo = SessionRepository(data)
meta = {"frames_per_segment": session.meta["frames_per_segment"], "encoder": "existing"}
repo.save(
    session.model_copy(
        update={
            "status": SessionStatus.CREATED,
            "status_detail": "Isolated benchmark",
            "analysed_frames": 0,
            "frontier_frame": 0,
            "profile": args.profile or session.profile,
            "meta": meta,
        }
    )
)
repo.events(session.session_id).append(Event.model_validate(calibration.model_dump(exclude={"seq", "supersedes"})))
primary = args.runtime_root.resolve() if args.runtime_root else source.parent
settings = Settings(
    _env_file=None,
    data_dir=data,
    models_dir=primary / "models",
    profiles_dir=primary / "config/profiles",
    profile=args.profile or session.profile,
)
runner = SessionRunner(session.session_id, repo, LocalBus(), settings, ModelRegistry(settings.models_dir))
gpu_executable = shutil.which("nvidia-smi")
peak = [0]
stop = threading.Event()


def monitor():
    last = None
    while not stop.is_set():
        state = repo.get(session.session_id)
        key = (state.status.value, state.analysed_frames)
        if key != last:
            print("progress", args.label, *key, flush=True)
            last = key
        try:
            if gpu_executable is None:
                raise FileNotFoundError("nvidia-smi unavailable")
            # Resolved executable and fixed arguments, with no shell.
            rows = subprocess.check_output(  # noqa: S603
                [gpu_executable, "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
                text=True,
                timeout=4,
            )
            for row in rows.splitlines():
                pid, mem = row.split(",")
                if int(pid.strip()) == os.getpid():
                    peak[0] = max(peak[0], int(mem.strip()))
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
        stop.wait(5)


worker = threading.Thread(target=monitor, daemon=True)
worker.start()
start = time.monotonic()
try:
    runner._ensure_media()
    runner._analyse()
finally:
    stop.set()
    worker.join(timeout=6)
state = repo.get(session.session_id)
events = repo.events(session.session_id).query()
families = collections.Counter(e.payload.get("stroke", "unknown") for e in events if e.type == "stroke")
court = collections.Counter()
pose = collections.Counter()
detector = collections.Counter()
shuttle = 0
for file in repo.paths(session.session_id).root.joinpath("perception").glob("*.msgpack"):
    for f in msgpack.unpackb(file.read_bytes(), raw=False)["frames"]:
        court[str(f.get("cs"))] += 1
        pose[str(f.get("ps"))] += 1
        detector[str(f.get("do"))] += 1
        shuttle += bool(f.get("s"))
activity = collections.Counter()
for e in events:
    if e.type == "activity_interval":
        activity[e.payload.get("state")] += e.frame_end - e.frame_start + 1
report = {
    "label": args.label,
    "profile": args.profile or session.profile,
    "status": state.status.value,
    "source_session": session.session_id,
    "source_sha256": session.source.sha256,
    "proxy_sha256": proxy_sha,
    "calibration_sha256": hashlib.sha256(json.dumps(calibration.payload, sort_keys=True).encode()).hexdigest(),
    "media_frames": session.media.n_frames,
    "analysed_frames": state.analysed_frames,
    "analysis_wall_s": round(time.monotonic() - start, 3),
    "sampled_peak_gpu_mib": peak[0],
    "event_counts": dict(collections.Counter(e.type for e in events)),
    "stroke_families": dict(families),
    "calibration_state_frames": dict(court),
    "pose_stride_frames": dict(pose),
    "detector_run_frames": dict(detector),
    "visible_shuttle_frames": shuttle,
    "activity_state_frames": dict(activity),
    "accuracy_claim": False,
    "measurement_note": (
        "Fresh perception and semantic analysis, including model loading and seeding; copied source media/calibration. "
        "Timing is one run, not a controlled performance study. No labelled contact, family or identity accuracy."
    ),
}
(out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2), flush=True)
repo.close()
if state.status is not SessionStatus.ANALYSED:
    raise RuntimeError("Benchmark did not complete")
