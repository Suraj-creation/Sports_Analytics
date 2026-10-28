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
from typing import Any, Literal

import msgpack
import numpy as np

import bai_badminton.engine as engine_module
from bai_badminton.court import Homography
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs, ScoreReading
from bai_badminton.rules.bwf import MatchConfig
from bai_engine.schema.tracks import TrackObject, samples_to_table
from bai_engine.store import EventStore, TrackStore


def _identity_metadata(person: dict) -> dict:
    """Keep uncertainty on current replays while supporting archived dataclasses."""
    values = {
        "raw_track_id": person.get("rt"),
        "detector_matched": person.get("dm"),
        "identity_method": person.get("im"),
    }
    raw, matched, method = values.values()
    if raw is not None and (type(raw) is not int or raw < 0):
        raise ValueError("invalid raw identity track id")
    if matched is not None and not isinstance(matched, bool):
        raise ValueError("invalid identity detector match")
    if method is not None and (not isinstance(method, str) or len(method) > 96):
        raise ValueError("invalid identity method")
    return {key: value for key, value in values.items() if key in PersonObs.__dataclass_fields__}


def decode_observations(data: bytes, n_frames: int) -> ChunkPerception | None:
    """Historical observation replay, intentionally separate from production codecs."""
    decoded = msgpack.unpackb(data, raw=False)
    frames = []
    for frame in decoded["frames"]:
        if frame["f"] >= n_frames:
            continue  # padded runner frontier is not decoded source footage
        detector_observed = frame.get("do")
        if detector_observed is not None and not isinstance(detector_observed, bool):
            raise ValueError("invalid detector observation flag")
        pose_stride = frame.get("ps")
        if pose_stride is not None and (type(pose_stride) is not int or pose_stride < 0):
            raise ValueError("invalid pose schedule")
        pose_kwargs = {"pose_stride": pose_stride} if "pose_stride" in FramePerception.__dataclass_fields__ else {}
        calibration_state = frame.get("cs")
        if calibration_state is not None:
            calibration_state = CalibrationState(calibration_state)
        persons = [
            PersonObs(
                track_id=p["t"],
                bbox=np.asarray(p["b"]),
                conf=p["c"],
                kps=np.asarray(p["k"]) if p["k"] is not None else None,
                appearance=np.asarray(p["a"], np.float32) if p.get("a") is not None else None,
                **_identity_metadata(p),
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
                calibration_state=calibration_state,
                detector_observed=detector_observed,
                **pose_kwargs,
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


def replay_session(
    session: dict[str, Any],
    data_dir: Path,
    output_dir: Path,
    *,
    discipline: Literal["singles", "doubles"] = "singles",
    persist_tracks: bool = False,
) -> dict[str, Any] | None:
    sid = session["session_id"]
    if not isinstance(sid, str) or not sid.isalnum():
        raise ValueError("invalid source session id")
    source = data_dir / "sessions" / sid
    files = sorted((source / "perception").glob("*.msgpack"))
    if not files:
        return None
    track_store = None
    last_written: dict[TrackObject, int] = {}
    tracks_persisted = 0
    if persist_tracks:
        session_root = (data_dir / "sessions").resolve()
        destination = output_dir.resolve()
        if destination == session_root or session_root in destination.parents:
            raise ValueError("track replay output must be outside source sessions")
        track_dir = output_dir / (sid + "-tracks")
        track_dir.mkdir(exist_ok=False)
        track_store = TrackStore(track_dir)
    started = time.monotonic()
    media = session["media"]
    fps = media["fps_num"] / media["fps_den"]
    store = EventStore(output_dir / (sid + ".sqlite"), sid)
    engine = BadmintonMatchEngine(
        sid,
        EngineConfig(
            fps=fps, frame_width=media["width"], frame_height=media["height"], match=MatchConfig(discipline=discipline)
        ),
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

    def persist_track_batch() -> None:
        nonlocal tracks_persisted
        if track_store is None:
            return
        samples = engine.drain_tracks()
        for obj in {sample.obj for sample in samples}:
            batch = [sample for sample in samples if sample.obj == obj]
            start, end = min(sample.frame_idx for sample in batch), max(sample.frame_idx for sample in batch)
            if start <= last_written.get(obj, -1):
                raise ValueError("replayed track batches overlap")
            track_store.write_chunk(obj, start, end, samples_to_table(batch))
            last_written[obj] = end
            tracks_persisted += len(batch)

    versions: set[int] = set()
    frame_metadata = Counter()
    frames_seen = 0
    cache_hash = hashlib.sha256()
    for path in files:
        content = path.read_bytes()
        cache_hash.update(path.name.encode())
        cache_hash.update(content)
        encoded = msgpack.unpackb(content, raw=False)
        versions.add(encoded.get("v", 1))
        for frame in encoded["frames"]:
            if frame["f"] < media["n_frames"]:
                cs_key = "calibration_state_present" if frame.get("cs") is not None else "calibration_state_missing"
                do_key = "detector_observed_present" if frame.get("do") is not None else "detector_observed_missing"
                ps_key = "pose_schedule_present" if frame.get("ps") is not None else "pose_schedule_missing"
                frame_metadata[ps_key] += 1
                frame_metadata[cs_key] += 1
                frame_metadata[do_key] += 1
        chunk = decode_observations(content, media["n_frames"])
        if chunk is not None:
            engine.ingest(chunk)
            persist_track_batch()
            frames_seen += len(chunk.frames)
    engine.flush()
    persist_track_batch()
    rallies = store.query(types=["rally_end"])
    return {
        "session_id": sid,
        "title": session["title"],
        "discipline": discipline,
        "tracks_persisted": persist_tracks,
        "track_samples_persisted": tracks_persisted,
        "cached_frame_metadata": dict(frame_metadata),
        "pose_schedule_supported": "pose_stride" in FramePerception.__dataclass_fields__,
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
    parser.add_argument(
        "--doubles-session-id",
        action="append",
        default=[],
        metavar="ID",
        help="repeat for each session to replay with doubles court bounds",
    )
    parser.add_argument(
        "--persist-tracks", action="store_true", help="write replayed tracks only into the fresh output directory"
    )
    parser.add_argument(
        "--session-id", action="append", default=[], metavar="ID", help="limit replay to the named sessions"
    )
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
        "persist_tracks": args.persist_tracks,
        "selected_session_ids": sorted(set(args.session_id)),
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_data_dir": str(data_dir),
        "started_at_utc": datetime.now(UTC).isoformat(),
        "implementation_file": str(Path(engine_module.__file__).resolve()),
        "implementation_sha256": hashlib.sha256(Path(engine_module.__file__).read_bytes()).hexdigest(),
        "python": sys.version,
        "initial_calibration_only": True,
        "human_corrections_applied": False,
        "doubles_session_ids": sorted(set(args.doubles_session_id)),
        "default_discipline": "singles",
        "discipline_scope": "Doubles changes court bounds; full doubles service/scoring rules are not implemented.",
        "cache_validity": "Historical cache replay; missing calibration and detector metadata remains unknown.",
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    results = []
    try:
        catalogue = data_dir / "sessions.sqlite"
        with sqlite3.connect(f"{catalogue.as_uri()}?mode=ro", uri=True) as db:
            sessions = [json.loads(row[0]) for row in db.execute("SELECT body FROM sessions ORDER BY session_id")]
        doubles_ids = set(args.doubles_session_id)
        unknown = doubles_ids - {session["session_id"] for session in sessions}
        if unknown:
            raise ValueError(f"unknown doubles session: {', '.join(sorted(unknown))}")
        requested = set(args.session_id)
        unknown_selected = requested - {session["session_id"] for session in sessions}
        if unknown_selected:
            raise ValueError(f"unknown selected session: {', '.join(sorted(unknown_selected))}")
        for session in sessions:
            if requested and session["session_id"] not in requested:
                continue
            discipline = "doubles" if session["session_id"] in doubles_ids else "singles"
            result = replay_session(
                session, data_dir, output_dir, discipline=discipline, persist_tracks=args.persist_tracks
            )
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
