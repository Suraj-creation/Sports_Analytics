"""Read-only BST evaluation on every detected stroke in a completed snapshot.

No contacts, poses, court positions or timing boundaries come from labels.
Ineligible windows remain unknown predictions; misses and false contacts remain
in the end-to-end confusion matrix. This does not alter the source session.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

import msgpack
import numpy as np
import torch

from bai_badminton.court import Homography
from bai_badminton.events.bst import (
    CHECKPOINT_SHA256,
    BSTClassifier,
    BSTFrame,
    BSTPlayer,
    contact_window,
    prepare_sequence,
)
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema.events import Event, EventStatus, current_view
from bai_engine.schema.session import Session, SessionStatus
from research.evaluation.benchmark_reference_session import (
    _aggregate,
    _catalogue,
    _court_side,
    _event_rows,
    _source_binding,
)
from research.shot_benchmark import evaluate


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def extract_frames(directory: Path, calibrations: list[Event]) -> tuple[dict[int, BSTFrame], dict]:
    frames, hashes, reasons, versions = {}, {}, Counter(), Counter()
    for path in sorted(directory.glob("seg_*.msgpack")):
        raw = path.read_bytes()
        hashes[path.name] = hashlib.sha256(raw).hexdigest()
        chunk = msgpack.unpackb(raw, raw=False)
        versions[chunk["v"]] += 1
        if chunk["v"] not in (9, 10):
            raise ValueError(f"unsupported diagnostic cache codec {chunk['v']}")
        for row in chunk["frames"]:
            index = row["f"]
            if index in frames:
                raise ValueError(f"duplicate cached frame {index}")
            eligible = [
                e for e in calibrations if e.frame_start <= index and e.payload.get("cam_ref") == chunk.get("cr")
            ]
            calib = max(eligible, key=lambda e: (e.frame_start, e.seq or 0)) if eligible else None
            h, reason = None, None
            if row.get("cs") != "VALID":
                reason = "calibration_not_valid"
            elif row.get("r") or row.get("v") != "main" or row.get("l"):
                reason = "replay_alternate_or_camera_lost"
            elif calib is None:
                reason = "calibration_reference_unavailable"
            else:
                h_ref = np.asarray(calib.payload["H"], dtype=float)
                if row.get("g") is not None:
                    matrix = np.asarray(row["g"], dtype=float).reshape(3, 3) @ h_ref
                    h = Homography(matrix, 0.0, 4)
                elif chunk.get("cr") is None and calib.payload.get("cam_ref") is None:
                    h = Homography(h_ref, 0.0, 4)
                else:
                    reason = "tracked_camera_pose_unavailable"
            reasons[reason or "valid"] += 1
            persons = [BSTPlayer(np.asarray(p["b"]), np.asarray(p["k"])) for p in row["p"] if p.get("k") is not None]
            # Cached kps are actual scheduled inference; _carry never copies them.
            frames[index] = BSTFrame(index, persons, tuple(row["s"]) if row.get("s") else None, h, row["sh"])
    return frames, {"cache_sha256": hashes, "codec_chunks": dict(versions), "frame_calibration": dict(reasons)}


def detected_context(events: list[Event], strokes: list[Event]) -> dict[str, tuple[int | None, int | None]]:
    """Neighbors from completed machine rallies, never annotation windows."""
    groups: dict[str, str] = {}
    for event in events:
        if event.type == "rally_end":
            for shot in event.payload.get("shots", []):
                if isinstance(shot.get("event_id"), str):
                    groups[shot["event_id"]] = event.event_id
    grouped = defaultdict(list)
    for event in strokes:
        grouped[groups.get(event.event_id, event.event_id)].append(event)
    neighbors = {}
    for group in grouped.values():
        group.sort(key=lambda event: event.frame_start)
        for i, event in enumerate(group):
            neighbors[event.event_id] = (
                group[i - 1].frame_start if i else None,
                group[i + 1].frame_start if i + 1 < len(group) else None,
            )
    return neighbors


def infer_strokes(session: Session, events: list[Event], frames: dict[int, BSTFrame], classifier: BSTClassifier):
    """The same label-free inference policy for a session and a benchmark."""
    if session.media is None:
        raise ValueError("session media required")
    if session.roster is not None and session.roster.match_format != "singles":
        raise ValueError("BST-CG-AP supports singles only")
    strokes = sorted(
        (e for e in events if e.type == "stroke" and e.status == EventStatus.CONFIRMED), key=lambda e: e.frame_start
    )
    neighbors = detected_context(events, strokes)
    predictions, reasons = {}, Counter()
    for event in strokes:
        previous, following = neighbors[event.event_id]
        start, end = contact_window(event.frame_start, session.media.fps, previous, following)
        item = {
            "event_id": event.event_id,
            "frame": event.frame_start,
            "context": [start, end],
            "previous_detected_contact": previous,
            "following_detected_contact": following,
            "family": "unknown",
            "court_side": None,
            "status": "skipped",
        }
        try:
            if end > session.media.n_frames or any(index not in frames for index in range(start, end)):
                raise ValueError("incomplete temporal context")
            sequence = prepare_sequence(
                [frames[index] for index in range(start, end)],
                (session.media.width, session.media.height),
                match_format="singles",
            )
            started = time.perf_counter()
            result = classifier.predict_sequence(sequence)
            family, confidence = result.prediction.top
            side = max(result.side_probabilities, key=result.side_probabilities.__getitem__)
            item.update(
                {
                    "status": "inferred",
                    "family": "net_shot" if family == "cross_net" else family,
                    "original_family": family,
                    "confidence": confidence,
                    "court_side": {"far": "top", "near": "bottom"}.get(side),
                    "side_probabilities": result.side_probabilities,
                    "class_probabilities": result.class_probabilities,
                    "family_probabilities": result.prediction.probs,
                    "usable_pose_frames": sequence.usable_frames,
                    "video_len": sequence.video_len,
                    "source_frames": sequence.source_frames,
                    "cpu_seconds": time.perf_counter() - started,
                }
            )
        except ValueError as error:
            item["reason"] = str(error)
        reasons[item.get("reason", item["status"])] += 1
        predictions[event.event_id] = item
    return predictions, reasons


def run(snapshot: Path, output: Path, models: Path) -> dict:
    if output.exists():
        raise ValueError("shadow output must be new")
    base = json.loads((snapshot / "benchmark.json").read_text())
    session_id = base["session_id"]
    data = snapshot / "data"
    catalogue = _catalogue(data, session_id)
    session = Session.model_validate_json(catalogue)
    if session.status != SessionStatus.ANALYSED or session.media is None:
        raise ValueError("completed snapshot required")
    # This initial development script cannot inspect the reserved test recording.
    if any(r["source_reference"]["split"] != "development" for r in base["rallies"]):
        raise ValueError("development-only BST comparison; held-out protocol needs a frozen policy")
    rows = _event_rows(data, session_id)
    event_hash = hashlib.sha256("\n".join(body for _, body in rows).encode()).hexdigest()
    if event_hash != base["provenance"]["event_log_sha256"]:
        raise ValueError("benchmark/event snapshot mismatch")
    events = current_view([Event.model_validate_json(body).with_seq(seq) for seq, body in rows])
    frames, cache_provenance = extract_frames(
        data / "sessions" / session_id / "perception", [e for e in events if e.type == "calibration"]
    )
    checkpoint = ModelRegistry(models).path("bst_cg_ap_shuttleset", fetch=False)
    classifier = BSTClassifier(checkpoint, device="cpu")
    predictions, reasons = infer_strokes(session, events, frames, classifier)
    reports, evaluated = [], set()
    for rally in base["rallies"]:
        labels = rally["source_reference"]
        _source_binding(labels, session)
        truth = [{**shot, "player_id": shot.get("source_hitter")} for shot in labels["shots"]]
        rows_pred = []
        for old in rally["predictions"]:
            shadow = predictions[old["event_id"]]
            evaluated.add(old["event_id"])
            rows_pred.append(
                {
                    **old,
                    "family": shadow["family"],
                    "player_id": shadow["court_side"],
                    "court_side": shadow["court_side"],
                    "bst_status": shadow["status"],
                    "bst_skip_reason": shadow.get("reason"),
                }
            )
        result = evaluate({**labels, "shots": truth}, {**labels, "shots": rows_pred}, tolerance_s=base["tolerance_s"])
        reports.append(
            {
                "window_frames": labels["window_frames"],
                "predictions": rows_pred,
                "contact_detection": {
                    key: result[key]
                    for key in ("truth_count", "prediction_count", "matched", "false_positives", "false_negatives")
                },
                "shot_family": {
                    **{key: result[key] for key in ("per_class", "known_family", "confusion")},
                    "unknown_predictions": sum(p["family"] == "unknown" for p in rows_pred),
                },
                "court_side": _court_side(result, truth, rows_pred, base["tolerance_s"]),
                "joint_contact_family_court_side": result["end_to_end"]["joint_contact_family_hitter"],
                "timestamp_mae_s": result["timestamp_mae_s"],
            }
        )
    if catalogue != _catalogue(data, session_id) or rows != _event_rows(data, session_id):
        raise ValueError("source session changed during shadow evaluation")
    cache_dir = data / "sessions" / session_id / "perception"
    if any(digest(cache_dir / name) != value for name, value in cache_provenance["cache_sha256"].items()):
        raise ValueError("source cache changed during shadow evaluation")
    result = {
        "version": "bst-shadow-development-v1",
        "snapshot": str(snapshot.resolve()),
        "session_id": session_id,
        "policy": (
            "all nonprovisional detected strokes; argmax side-marginalized family; skipped contexts remain unknown"
        ),
        "context_policy": "official bounds using detected same-machine-rally neighbors; no reference anchors in inputs",
        "default_pipeline_changed": False,
        "device": "cpu",
        "torch_threads": torch.get_num_threads(),
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "checkpoint_size_bytes": checkpoint.stat().st_size,
        "base_benchmark_sha256": digest(snapshot / "benchmark.json"),
        "run_manifest_sha256": digest(snapshot / "run-manifest.json"),
        "event_log_sha256": event_hash,
        "cache_provenance": cache_provenance,
        "coverage_all_detected_strokes": dict(reasons),
        "coverage_evaluated_windows": dict(
            Counter(predictions[e].get("reason", predictions[e]["status"]) for e in evaluated)
        ),
        "default_rules_aggregate": base["aggregate"],
        "bst_aggregate": _aggregate(reports),
        "rallies": reports,
        "all_stroke_predictions": list(predictions.values()),
        "limitations": [
            "Published hit-anchor agreement, not independently verified physical-contact accuracy.",
            "No training-overlap guarantee; this is development recording0044 only.",
            "Sparse RTMPose observations differ from dense MMPose training data; missing frames are zeroed.",
            "Court side prediction is not named or durable player identity.",
            "Learned probabilities are not calibrated confidence and no threshold has been tuned.",
            "Detector timing errors and missed contacts remain in every confusion and score.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--models", type=Path, default=Path("models"))
    args = parser.parse_args()
    torch.set_num_threads(2)
    report = run(args.snapshot, args.output, args.models)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "coverage": report["coverage_evaluated_windows"],
                "rules": report["default_rules_aggregate"]["shot_family"]["known_family"]["macro_f1"],
                "bst": report["bst_aggregate"]["shot_family"]["known_family"]["macro_f1"],
            }
        )
    )


if __name__ == "__main__":
    main()
