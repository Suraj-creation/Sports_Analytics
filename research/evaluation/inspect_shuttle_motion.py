"""Run the real engine's motion estimator on a saved, unlabelled shuttle track.

Use isolated PYTHONPATHs to invoke different engine revisions on the SAME probe.
This measures numerical/availability changes, not physical speed or shot accuracy.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from bai_badminton.engine import BadmintonMatchEngine
from bai_badminton.events.stroke import RuleStrokeClassifier
from bai_badminton.perception.shuttle_post import Track


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def motion_report(probe: dict, engine_type: type, probe_sha: str, engine_sha: str) -> dict:
    source_sha = probe.get("source_video_sha256")
    for value in (source_sha, probe_sha, engine_sha):
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError("source, probe and engine hashes are required")
    frames, fps = probe.get("source_frames"), probe.get("fps")
    if (
        not isinstance(frames, list)
        or len(frames) != 2
        or any(not isinstance(f, int) or isinstance(f, bool) for f in frames)
        or frames[0] < 0
        or frames[1] < frames[0]
        or not _finite(fps)
        or fps <= 0
        or probe.get("resize") != "1280x720"
    ):
        raise ValueError("invalid source frame range or frame rate")
    rows = probe.get("shuttle_track")
    if not isinstance(rows, list) or len(rows) != frames[1] - frames[0] + 1:
        raise ValueError("processed shuttle observations must cover the contiguous probe")
    x, y, visible, interpolated, confidence = [], [], [], [], []
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or row.get("frame") != frames[0] + i:
            raise ValueError("processed shuttle observations must be contiguous")
        vis, interp = row.get("visible"), row.get("interpolated")
        if not isinstance(vis, bool) or not isinstance(interp, bool):
            raise ValueError("visibility and interpolation must be boolean")
        xval, yval, conf = row.get("x"), row.get("y"), row.get("confidence")
        if (vis and (not _finite(xval) or not _finite(yval))) or (not vis and (xval is not None or yval is not None)):
            raise ValueError("coordinates and visibility are inconsistent")
        if conf is not None and (not _finite(conf) or not 0 <= conf <= 1):
            raise ValueError("invalid shuttle confidence")
        x.append(float(xval) if vis else np.nan)
        y.append(float(yval) if vis else np.nan)
        visible.append(vis)
        interpolated.append(interp)
        confidence.append(float(conf) if conf is not None else 0.0)
    track = Track.from_arrays(np.array(x), np.array(y), np.array(visible), np.array(confidence))
    track.interp = np.asarray(interpolated, dtype=bool)
    context = SimpleNamespace(
        cfg=SimpleNamespace(fps=float(fps), frame_height=720),
        _shuttle_around=lambda frame: (track, frame - frames[0]),
    )
    candidates = probe.get("contact_candidates")
    if not isinstance(candidates, list):
        raise ValueError("contact candidate list missing")
    events, seen = [], set()
    for candidate in candidates:
        frame = candidate.get("frame") if isinstance(candidate, dict) else None
        if (
            not isinstance(frame, int)
            or isinstance(frame, bool)
            or frame in seen
            or not frames[0] <= frame <= frames[1]
        ):
            raise ValueError("invalid or duplicate candidate frame")
        seen.add(frame)
        i = frame - frames[0]
        indices = range(i + 1, min(i + 6, len(track)))
        observed = sum(bool(track.vis[j] and not track.interp[j]) for j in indices)
        interp = sum(bool(track.vis[j] and track.interp[j]) for j in indices)
        speed, vy = engine_type._post_contact_kinematics(context, frame)
        if (speed is None) != (vy is None) or (speed is not None and (not _finite(speed) or not _finite(vy))):
            raise ValueError("engine returned invalid motion estimate")
        events.append(
            {
                "frame": frame,
                "observed_samples": observed,
                "interpolated_samples": interp,
                "speed_px_s": speed,
                "vy_px_s": vy,
            }
        )
    return {
        "version": "unlabelled-shuttle-motion-v1",
        "accuracy_claim_eligible": False,
        "note": "Same processed observations; neither physical speed nor labelled shot accuracy.",
        "source_video_sha256": source_sha,
        "probe_sha256": probe_sha,
        "engine_sha256": engine_sha,
        "fps": float(fps),
        "frame_height_px": 720,
        "source_frames": frames,
        "events": sorted(events, key=lambda row: row["frame"]),
    }


def compare_motion(before: dict, after: dict) -> dict:
    shared = ("source_video_sha256", "probe_sha256", "fps", "frame_height_px", "source_frames")
    if any(before.get(key) != after.get(key) for key in shared):
        raise ValueError("reports must use the same probe and source")
    old, new = before.get("events"), after.get("events")
    if not isinstance(old, list) or not isinstance(new, list) or [e["frame"] for e in old] != [e["frame"] for e in new]:
        raise ValueError("reports must use the same candidate frames")
    return {
        "version": "paired-shuttle-motion-v1",
        "accuracy_claim_eligible": False,
        "note": "Unlabelled same-input comparison; changes are not measured improvements.",
        "source_video_sha256": before["source_video_sha256"],
        "probe_sha256": before["probe_sha256"],
        "source_frames": before["source_frames"],
        "before_engine_sha256": before["engine_sha256"],
        "before_stroke_sha256": before.get("stroke_sha256"),
        "after_stroke_sha256": after.get("stroke_sha256"),
        "after_engine_sha256": after["engine_sha256"],
        "candidate_count": len(old),
        "before_available": sum(row["speed_px_s"] is not None for row in old),
        "after_available": sum(row["speed_px_s"] is not None for row in new),
        "changes": [
            {
                "frame": a["frame"],
                "before_speed_px_s": a["speed_px_s"],
                "after_speed_px_s": b["speed_px_s"],
                "before_vy_px_s": a["vy_px_s"],
                "after_vy_px_s": b["vy_px_s"],
                "observed_samples": a["observed_samples"],
                "interpolated_samples": a["interpolated_samples"],
            }
            for a, b in zip(old, new, strict=True)
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--video", type=Path, required=True)
    args = parser.parse_args()
    try:
        probe = json.loads(args.probe.read_text(encoding="utf-8"))
        if _hash(args.video) != probe.get("source_video_sha256"):
            raise ValueError("provided video does not match probe digest")
        report = motion_report(
            probe, BadmintonMatchEngine, _hash(args.probe), _hash(Path(inspect.getfile(BadmintonMatchEngine)))
        )
        report["stroke_sha256"] = _hash(Path(inspect.getfile(RuleStrokeClassifier)))
        print(json.dumps(report, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
