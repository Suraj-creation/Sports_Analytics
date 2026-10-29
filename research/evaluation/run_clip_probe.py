"""Run the real pipeline on one clip in an isolated data dir and print per-component diagnostics.

Coverage/consistency diagnostics only: no ground truth is used, so nothing here is precision or
recall. Use it to find components that emit nothing, emit physically implausible output, or
force a label where the evidence is missing.

  python research/evaluation/run_clip_probe.py --source clip.mp4 --output /tmp/probe-x [--format doubles]
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import shutil
import site
import sys
import time
from pathlib import Path

import numpy as np


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def summarize(rows: list[dict], state, events: list) -> dict:
    players = [r for r in rows if r["obj"] == "player" and r["visible"]]
    shuttle = sorted((r for r in rows if r["obj"] == "shuttle"), key=lambda r: r["frame_idx"])
    per_frame = collections.Counter(r["frame_idx"] for r in players)
    tracks: dict[int, list[int]] = collections.defaultdict(list)
    for r in players:
        tracks[r["track_id"]].append(r["frame_idx"])
    # A track that restarts after >1 s is a fragment of one body, not a new one.
    fps = float(state.media.fps)
    gaps = sum(1 for f in tracks.values() for a, b in zip(f, f[1:], strict=False) if b - a > fps)
    pose = [np.asarray(r["keypoints"], float).reshape(-1, 3) for r in players if r["keypoints"] is not None]
    pose_conf = [float(np.nanmean(p[:, 2])) for p in pose if p.size]
    # Persisted shuttle rows are raw detector output; gap interpolation stays inside the engine.
    vis = [r for r in shuttle if r["visible"]]
    jumps = []
    for a, b in zip(vis, vis[1:], strict=False):
        dt = b["frame_idx"] - a["frame_idx"]
        if 0 < dt <= 3:
            jumps.append(np.hypot(b["x"] - a["x"], b["y"] - a["y"]) / dt / state.media.height)
    strokes = collections.Counter(
        e.payload.get("stroke", "?") for e in events if e.type == "stroke" and e.status.value != "retracted"
    )
    return {
        "frames": state.frontier_frame,
        "fps": fps,
        "player_boxes_per_frame": dict(sorted(collections.Counter(per_frame.values()).items())),
        "frames_with_any_player_pct": round(100 * len(per_frame) / max(1, state.frontier_frame), 1),
        "distinct_track_ids": len(tracks),
        "track_fragments_gt_1s": gaps,
        "pose_rows": len(pose),
        "pose_rows_wrong_shape": sum(1 for p in pose if p.shape != (17, 3)),
        "pose_nonfinite_rows": sum(1 for p in pose if not np.isfinite(p).all()),
        "pose_mean_kp_conf_median": round(float(np.median(pose_conf)), 3) if pose_conf else None,
        "shuttle_visible_pct": round(100 * len(vis) / max(1, state.frontier_frame), 1),
        "shuttle_jump_gt_0.25_frame_heights_per_frame": int(sum(j > 0.25 for j in jumps)),
        "shuttle_adjacent_steps": len(jumps),
        "event_counts": dict(collections.Counter(e.type for e in events)),
        "stroke_labels": dict(strokes),
        "stroke_unknown_pct": round(100 * strokes.get("unknown", 0) / max(1, sum(strokes.values())), 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--runtime-root", type=Path, default=Path())
    ap.add_argument("--profile", default="gpu-rtx4000")
    ap.add_argument("--format", choices=("singles", "doubles"), default="singles")
    args = ap.parse_args()
    rt, out = args.runtime_root.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(rt / p) for p in ("engine/src", "sports/badminton/src", "agents/src", "apps/api/src")] + [str(rt)]

    from bai_engine.bus import LocalBus
    from bai_engine.config import Settings
    from bai_engine.runtime.registry import ModelRegistry
    from bai_engine.runtime.runner import SessionRunner
    from bai_engine.schema import Session, SessionStatus, Source, SourceKind, TrackObject
    from bai_engine.schema.events import current_view
    from bai_engine.schema.session import ParticipantRoster
    from bai_engine.store import SessionRepository

    sha = digest(args.source)
    data = out / "data"
    media = data / "media" / sha
    media.mkdir(parents=True)
    shutil.copy2(args.source, media / "source.mp4")
    profiles = out / "profiles"
    profiles.mkdir()
    shutil.copy2(rt / "config/profiles" / f"{args.profile}.yaml", profiles / f"{args.profile}.yaml")
    repo = SessionRepository(data)
    sid = "probe" + sha[:8]
    repo.save(
        Session(
            session_id=sid,
            title="probe",
            source=Source(kind=SourceKind.UPLOAD, uri=str(media / "source.mp4"), sha256=sha, original_name="clip.mp4"),
            roster=ParticipantRoster(match_format=args.format),
            profile=args.profile,
        )
    )
    settings = Settings(
        _env_file=None,
        data_dir=data,
        models_dir=rt / "models",
        profiles_dir=profiles,
        profile=args.profile,
        proxy_height=720,
    )
    runner = SessionRunner(sid, repo, LocalBus(), settings, ModelRegistry(settings.models_dir))
    t0 = time.monotonic()
    try:
        runner._ensure_media()
        runner._analyse()
        if runner._transcode_thread is not None:
            runner._transcode_thread.join(timeout=60)
        state = repo.get(sid)
        rows = repo.tracks(sid).read([TrackObject.PLAYER, TrackObject.SHUTTLE], 0, state.frontier_frame).to_pylist()
        events = current_view(repo.events(sid).query())
        report = {
            "status": state.status.value,
            "detail": state.status_detail,
            "elapsed_s": round(time.monotonic() - t0, 1),
            "degraded": runner.sport.degraded(),
            **summarize(rows, state, events),
        }
    finally:
        runner.stop()
        repo.close()
    (out / "probe.json").write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    if sys.platform == "linux":
        libs = []
        for pkg in map(Path, site.getsitepackages()):
            libs.extend(sorted(pkg.glob("nvidia/*/lib")))
            if (pkg / "torch/lib").is_dir():
                libs.append(pkg / "torch/lib")
        cur = os.environ.get("LD_LIBRARY_PATH", "").split(":")
        missing = [str(p) for p in libs if str(p) not in cur]
        if missing:
            env = dict(os.environ, LD_LIBRARY_PATH=":".join(missing + [p for p in cur if p]))
            os.execve(sys.executable, [sys.executable, *sys.argv], env)  # noqa: S606 - same trusted interpreter
    main()
