"""Replay frozen perception into isolated events/tracks and unchanged reference labels.

No model inference, reference labels in prediction, or modification of the source
session. The full original frame timeline and every published rally denominator
are preserved. Explicit calibration and cache hashes bind the observations.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import shutil
import sqlite3
import sys
import time
from pathlib import Path


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    code = args.code_root.resolve()
    source = args.input.resolve()
    output = args.output.resolve()
    roots = ("engine/src", "sports/badminton/src", "agents/src", "apps/api/src")
    sys.path[:0] = [str(code / p) for p in roots] + [str(Path(__file__).resolve().parents[2])]
    import msgpack
    import numpy as np

    from bai_badminton.court import Homography
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
    from bai_badminton.perception.calibration_state import CalibrationState
    from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs, ScoreReading
    from bai_badminton.rules import MatchConfig
    from bai_engine.schema import Session, TrackObject
    from bai_engine.schema.tracks import samples_to_table
    from bai_engine.store import SessionRepository
    from research.evaluation.benchmark_reference_session import benchmark_session

    with sqlite3.connect(f"{(source / 'data/sessions.sqlite').as_uri()}?mode=ro", uri=True) as db:
        row = db.execute("select body from sessions").fetchall()
    if len(row) != 1:
        raise ValueError("exactly one isolated source session required")
    session = Session.model_validate_json(row[0][0])
    sid = session.session_id
    source_session = source / "data/sessions" / sid
    with sqlite3.connect(f"{(source_session / 'events.sqlite').as_uri()}?mode=ro", uri=True) as db:
        calibration = [
            json.loads(r[0]) for r in db.execute("select body from events where type='calibration' order by seq")
        ]
    if len(calibration) != 1 or calibration[0]["frame_start"] != 0:
        raise ValueError("this diagnostic requires one initial calibration; do not guess reference changes")
    files = sorted((source_session / "perception").glob("*.msgpack"))
    if not files:
        raise ValueError("no frozen perception")
    output.mkdir(parents=True, exist_ok=False)
    data = output / "data"
    repo = SessionRepository(data)
    repo.save(session)
    store = repo.events(sid)
    tracks = repo.tracks(sid)
    shutil.copytree(source / "data/media", data / "media", dirs_exist_ok=True)
    shutil.copytree(source / "annotations", output / "annotations")
    shutil.copytree(source_session / "perception", data / "sessions" / sid / "perception")
    code_hashes = {str(p.relative_to(code)): digest(p) for root in roots for p in sorted((code / root).rglob("*.py"))}
    cache_hashes = {p.name: digest(p) for p in files}
    dump(
        output / "run-manifest.json",
        {
            "kind": "same_observations_event_replay",
            "input": str(source),
            "code_root": str(code),
            "code_hashes": code_hashes,
            "cache_hashes": cache_hashes,
            "calibration": calibration,
            "annotations": {p.name: digest(p) for p in (source / "annotations").glob("*.json")},
        },
    )
    media = session.media
    fps = float(media.fps)
    engine = BadmintonMatchEngine(
        sid,
        EngineConfig(
            fps=fps,
            frame_width=media.width,
            frame_height=media.height,
            profile=session.profile,
            match=MatchConfig(discipline=session.roster.match_format if session.roster else "singles"),
        ),
        store,
    )
    cal = calibration[0]["payload"]
    net = cal.get("net_top") or [None, None]
    engine.set_camera_reference(cal.get("cam_ref"))
    engine.set_calibration(
        cal.get("shot_id", 0), Homography.from_json(cal), *net, cam_ref=cal.get("cam_ref"), extra=cal
    )
    started = time.monotonic()
    last = -1
    for path in files:
        d = msgpack.unpackb(path.read_bytes(), raw=False)
        if d["start"] != last + 1:
            raise ValueError("noncontiguous source cache")
        frames = [
            FramePerception(
                frame_idx=f["f"],
                shuttle_xy=tuple(f["s"]) if f["s"] else None,
                shuttle_conf=f["c"],
                replay=f["r"],
                shot_id=f["sh"],
                cam=np.asarray(f["g"]).reshape(3, 3) if f.get("g") else None,
                cam_lost=bool(f.get("l", False)),
                view=f.get("v"),
                head=f.get("h"),
                court_q=f.get("q"),
                calibration_state=CalibrationState(f["cs"]),
                detector_observed=f["do"],
                pose_stride=f["ps"],
                persons=[
                    PersonObs(
                        track_id=q["t"],
                        bbox=np.asarray(q["b"]),
                        conf=q["c"],
                        kps=np.asarray(q["k"]) if q["k"] is not None else None,
                        appearance=np.asarray(q["a"], np.float32) if q["a"] is not None else None,
                        raw_track_id=q["rt"],
                        detector_matched=q["dm"],
                        identity_method=q["im"],
                    )
                    for q in f["p"]
                ],
            )
            for f in d["frames"]
        ]
        ocr = [
            ScoreReading(frame_idx=o["f"], rows=tuple(tuple(x) for x in o["r"]), conf=o["c"]) for o in d.get("ocr", [])
        ]
        engine.ingest(
            ChunkPerception(
                start=d["start"], end=d["end"], frames=frames, models=d.get("models", {}), ocr=ocr, cam_ref=d.get("cr")
            )
        )
        samples = engine.drain_tracks()
        for obj in TrackObject:
            selected = [sample for sample in samples if sample.obj == obj]
            if selected:
                tracks.write_chunk(obj, d["start"], d["end"], samples_to_table(selected))
        last = d["end"]
    engine.flush()
    if last != session.media.n_frames - 1:
        raise ValueError("source cache does not cover full media")
    report = benchmark_session(data, sid, output / "annotations", tolerance_s=0.2)
    dump(output / "benchmark.json", report)
    contacts = store.query(types=["contact"])
    strokes = store.query(types=["stroke"])
    summary = {
        "frames": last + 1,
        "elapsed_s": time.monotonic() - started,
        "contacts": len(contacts),
        "strokes": len(strokes),
        "rallies": len(store.query(types=["rally_end"])),
        "classes": dict(collections.Counter(e.payload["stroke"] for e in strokes)),
        "contact_component_nonzero": {
            key: sum(
                any(evidence.scores and evidence.scores.get(key, 0) > 0 for evidence in event.evidence)
                for event in contacts
            )
            for key in ("proximity", "swing")
        },
        "benchmark": report["aggregate"],
    }
    dump(output / "summary.json", summary)
    changed = [name for name, sha in code_hashes.items() if digest(code / name) != sha]
    if changed:
        raise RuntimeError(f"source changed during replay: {changed}")
    print(
        json.dumps(
            {
                "elapsed_s": summary["elapsed_s"],
                "contacts": len(contacts),
                "benchmark": report["aggregate"]["contact_detection"],
            }
        ),
        flush=True,
    )
    repo.close()


if __name__ == "__main__":
    main()
