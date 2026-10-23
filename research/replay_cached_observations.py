"""Replay cached model observations into fresh isolated event stores.

This explicitly decodes historical cache versions for semantic regression only.
It does not bypass production cache invalidation or run perception/GPU models.
No resulting count is an accuracy measurement without independent annotations.

Run after sourcing ../gpu-env.sh and activating .venv:
  python research/replay_cached_observations.py --output-dir /tmp/new-replay
Use PYTHONPATH to select an archived badminton/engine implementation to compare.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import msgpack
import numpy as np

import bai_badminton.engine as engine_module
from bai_badminton.court import Homography
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs, ScoreReading
from bai_engine.store import EventStore


def decode_observations(data: bytes, n_frames: int) -> ChunkPerception | None:
    """Historical observation replay, intentionally separate from production codecs."""
    decoded = msgpack.unpackb(data, raw=False)
    frames = []
    for frame in decoded["frames"]:
        if frame["f"] >= n_frames:
            continue  # padded runner frontier is not decoded source footage
        persons = [
            PersonObs(
                track_id=p["t"],
                bbox=np.asarray(p["b"]),
                conf=p["c"],
                kps=np.asarray(p["k"]) if p["k"] is not None else None,
                appearance=np.asarray(p["a"], np.float32) if p.get("a") is not None else None,
            )
            for p in frame["p"]
        ]
        frames.append(
            FramePerception(
                frame_idx=frame["f"],
                shuttle_xy=tuple(frame["s"]) if frame["s"] else None,
                shuttle_conf=frame["c"],
                persons=persons,
                replay=frame["r"],
                shot_id=frame["sh"],
                cam=np.asarray(frame["g"], dtype=float).reshape(3, 3) if frame.get("g") else None,
                cam_lost=bool(frame.get("l", False)),
                view=frame.get("v"),
                head=frame.get("h"),
                court_q=frame.get("q"),
            )
        )
    if not frames:
        return None
    ocr = [
        ScoreReading(
            frame_idx=row["f"],
            rows=tuple(tuple(value) for value in row["r"]),
            conf=row["c"],
        )
        for row in decoded.get("ocr", [])
        if row["f"] < n_frames
    ]
    return ChunkPerception(
        start=frames[0].frame_idx,
        end=frames[-1].frame_idx,
        frames=frames,
        models=decoded.get("models", {}),
        ocr=ocr,
        cam_ref=decoded.get("cr"),
    )


def replay_session(session: dict[str, Any], data_dir: Path, output_dir: Path) -> dict[str, Any] | None:
    sid = session["session_id"]
    if not isinstance(sid, str) or not sid.isalnum():
        raise ValueError("invalid source session id")
    source = data_dir / "sessions" / sid
    files = sorted((source / "perception").glob("*.msgpack"))
    if not files:
        return None
    started = time.monotonic()
    media = session["media"]
    fps = media["fps_num"] / media["fps_den"]
    store = EventStore(output_dir / (sid + ".sqlite"), sid)
    engine = BadmintonMatchEngine(
        sid,
        EngineConfig(fps=fps, frame_width=media["width"], frame_height=media["height"]),
        store,
        player_names={player["player_id"]: player.get("name") for player in session["players"]},
    )
    with sqlite3.connect(f"{(source / 'events.sqlite').as_uri()}?mode=ro", uri=True) as original:
        calibration = original.execute(
            "SELECT body FROM events WHERE type='calibration' ORDER BY seq LIMIT 1"
        ).fetchone()
    # Preserve the recorded initial geometry and reference ownership. No model
    # recalibration or historical reviewer corrections are applied in this comparison.
    if calibration:
        payload = json.loads(calibration[0])["payload"]
        net = payload.get("net_top")
        engine.set_calibration(
            payload.get("shot_id", 0),
            Homography.from_json(payload),
            tuple(net[0]) if net else None,
            tuple(net[1]) if net else None,
            cam_ref=payload.get("cam_ref"),
            extra=payload,
        )
    versions: set[int] = set()
    frames_seen = 0
    cache_hash = hashlib.sha256()
    for path in files:
        content = path.read_bytes()
        cache_hash.update(path.name.encode())
        cache_hash.update(content)
        versions.add(msgpack.unpackb(content, raw=False).get("v", 1))
        chunk = decode_observations(content, media["n_frames"])
        if chunk is not None:
            engine.ingest(chunk)
            frames_seen += len(chunk.frames)
    engine.flush()
    rallies = store.query(types=["rally_end"])
    return {
        "session_id": sid,
        "title": session["title"],
        "cached_codec_versions": sorted(versions),
        "media_sha256": session["source"].get("sha256"),
        "cached_observations_sha256": cache_hash.hexdigest(),
        "frames": frames_seen,
        "expected_frames": media["n_frames"],
        "coverage_complete": frames_seen == media["n_frames"],
        "fps": fps,
        "seconds": round(time.monotonic() - started, 3),
        "rallies": len(rallies),
        "official": sum(e.payload.get("official", True) for e in rallies),
        "unresolved": sum(e.payload.get("winner") is None for e in rallies),
        "points": len(store.query(types=["point"])),
        "strokes": len(store.query(types=["stroke"])),
        "score": engine.public_state()["score"],
        "end_reasons": dict(Counter(e.payload["end_reason"] for e in rallies)),
        "phase_basis": dict(Counter(e.payload["phase_basis"] for e in rallies)),
        "intervals": [
            {
                "start": e.frame_start,
                "end": e.frame_end,
                "reason": e.payload["end_reason"],
                "official": e.payload["official"],
                "winner": e.payload["winner"],
                "check": e.payload["rule_check"],
            }
            for e in rallies
        ],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True, help="must not already exist")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--implementation-label", default="unspecified", help="caller-supplied revision label")
    args = parser.parse_args(argv)
    data_dir, output_dir = args.data_dir.resolve(), args.output_dir.resolve()
    session_root = (data_dir / "sessions").resolve()
    if output_dir == session_root or session_root in output_dir.parents:
        parser.error("output directory must be outside source sessions")
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error("output directory must be fresh; existing results are preserved")
    manifest: dict[str, Any] = {
        "kind": "cached_perception_semantic_replay",
        "implementation_label": args.implementation_label,
        "status": "running",
        "accuracy_claim": False,
        "gpu_inference": False,
        "source_data_dir": str(data_dir),
        "started_at_utc": datetime.now(UTC).isoformat(),
        "implementation_file": str(Path(engine_module.__file__).resolve()),
        "implementation_sha256": hashlib.sha256(Path(engine_module.__file__).read_bytes()).hexdigest(),
        "python": sys.version,
        "initial_calibration_only": True,
        "human_corrections_applied": False,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    results = []
    try:
        catalogue = data_dir / "sessions.sqlite"
        with sqlite3.connect(f"{catalogue.as_uri()}?mode=ro", uri=True) as db:
            sessions = [json.loads(row[0]) for row in db.execute("SELECT body FROM sessions ORDER BY session_id")]
        for session in sessions:
            result = replay_session(session, data_dir, output_dir)
            if result is not None:
                results.append(result)
                print(json.dumps({k: v for k, v in result.items() if k != "intervals"}), flush=True)
        manifest["status"] = "complete"
    except Exception as exc:
        manifest.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        manifest["finished_at_utc"] = datetime.now(UTC).isoformat()
        manifest_path.write_text(json.dumps(manifest, indent=2))
        (output_dir / "summary.json").write_text(json.dumps({"provenance": manifest, "sessions": results}, indent=2))


if __name__ == "__main__":
    main()
