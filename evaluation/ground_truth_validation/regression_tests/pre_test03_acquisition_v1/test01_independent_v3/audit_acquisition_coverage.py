"""Cross-chunk source camera proofs and every historical coverage-loss row."""

import json
from hashlib import file_digest
from pathlib import Path

import msgpack
import numpy as np


def sha(path):
    with Path(path).open("rb") as f:
        return file_digest(f, "sha256").hexdigest()


def iou(a, b):
    a, b = np.asarray(a), np.asarray(b)
    intersection = np.maximum(0, np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2])).prod()
    union = (a[2:] - a[:2]).prod() + (b[2:] - b[:2]).prod() - intersection
    return float(intersection / union) if union > 0 else 0.0


def audit_camera_proofs(packets):
    frames = {}
    weak = []
    cross = []
    format_steps = []
    previous_policy = None
    all_claims = []
    for packet in packets:
        policy = packet["ci"]
        context = policy.get("layout_format_context")
        relation = None
        if previous_policy is not None:
            relation = context == {
                "match_format": previous_policy.get("match_format"),
                "confirmed": previous_policy.get("layout_format_confirmed"),
            }
        format_steps.append(
            {
                "start": packet["start"],
                "end": packet["end"],
                "codec": packet["v"],
                "before_chunk_context": context,
                "post_chunk_format": policy.get("match_format"),
                "post_chunk_confirmed": policy.get("layout_format_confirmed"),
                "matches_previous_post_chunk_state": relation,
            }
        )
        for frame in packet["frames"]:
            f = frame["f"]
            if f in frames:
                raise ValueError("Duplicate source frame in camera proof audit")
            decision = frame.get("cd")
            is_weak = bool(
                decision
                and decision["version"] == "detector-layout-scene-decision:v3"
                and not decision["raw_hypothesis"]
                and decision["decision"] == "barrier"
            )
            if is_weak:
                if (
                    not isinstance(context, dict)
                    or context.get("confirmed") is not True
                    or decision["expected_participants"]
                    != {"singles": 2, "doubles": 4}.get(context.get("match_format"))
                ):
                    raise ValueError("Weak reset contradicts the source chunk-start format context")
                weak.append(f)
            if (
                decision
                and decision["version"] == "detector-layout-scene-decision:v3"
                and decision.get("previous_to_current") is not None
            ):
                previous = frames.get(decision["previous_frame"])
                if previous is None or decision["previous_frame"] != f - 1:
                    raise ValueError("No actual adjacent source camera for a relative layout proof")
                for source in (previous, frame):
                    if (
                        source.get("g") is None
                        or source.get("cs") != "VALID"
                        or source.get("v") != "main"
                        or source.get("r")
                    ):
                        raise ValueError("Relative camera proof lacks valid adjacent calibrated source views")
                a = np.asarray(previous["g"], float).reshape(3, 3)
                b = np.asarray(frame["g"], float).reshape(3, 3)
                claimed = np.asarray(decision["previous_camera"], float).reshape(3, 3)
                relative = np.asarray(decision["previous_to_current"], float).reshape(3, 3)
                if not np.array_equal(a, claimed):
                    raise ValueError("Serialized previous camera differs across the actual completed cache timeline")
                if not np.allclose(relative, b @ np.linalg.inv(a), rtol=0, atol=1e-9):
                    raise ValueError("Relative source camera pair arithmetic mismatch")
                cross_chunk = decision["previous_frame"] < packet["start"]
                record = {
                    "frame": f,
                    "previous_frame": f - 1,
                    "chunk_start": packet["start"],
                    "cross_chunk": cross_chunk,
                    "weak": is_weak,
                    "actual_previous_camera_equal": True,
                    "relative_pair_arithmetic_equal": True,
                }
                all_claims.append(record)
                if cross_chunk:
                    cross.append(record)
            frames[f] = frame
        previous_policy = policy
    mismatches = [row for row in format_steps if row["matches_previous_post_chunk_state"] is False]
    return {
        "scope": (
            "Actual adjacent recorded source cameras across full completed catalogue; "
            "not independent physical camera estimation accuracy"
        ),
        "frames_seen": len(frames),
        "relative_claim_count": len(all_claims),
        "cross_chunk_claim_count": len(cross),
        "weak_barrier_frames": weak,
        "all_claims": all_claims,
        "cross_chunk_claims": cross,
        "format_context_per_chunk": format_steps,
        "format_context_transition_mismatches_requiring_runtime_order_review": mismatches,
    }


def audit_acquisition_coverage(config, out, old_frames, new_frames):
    out = Path(out)
    art = Path(config["artifact_root"])
    historical = Path(config["historical_coverage_rows"])
    ledger = json.loads(historical.read_text())
    inputs = {str(historical): sha(historical), str(Path(__file__)): sha(__file__)}

    def write(name, value):
        with (out / name).open("x") as f:
            json.dump(value, f, indent=2, allow_nan=False)
            f.write("\n")

    packets = []
    catalog_path = art / "run/perception_completion_catalog.json"
    inputs[str(catalog_path)] = sha(catalog_path)
    for entry in json.loads(catalog_path.read_text())["files"]:
        path = art / "run" / entry["path"]
        assert sha(path) == entry["sha256"]
        inputs[str(path)] = entry["sha256"]
        packets.append(msgpack.unpackb(path.read_bytes(), raw=False))
    camera = audit_camera_proofs(packets)
    write("crosschunk_camera_format_audit.json", camera)
    if camera["frames_seen"] != config["frame_count"]:
        raise ValueError("Incomplete completed timeline")
    historical_rows = []
    frame_reasons = {}

    def focus(f, reason):
        frame_reasons.setdefault(f, []).append(reason)

    for row in ledger["all_rows"]:
        f = row["frame"]
        box = row["old_withheld_region"]["b"]
        current = new_frames[f]
        matches = sorted([(iou(box, p["b"]), p) for p in current["p"]], key=lambda item: item[0], reverse=True)
        overlap, person = matches[0] if matches else (0.0, None)
        historical_rows.append(
            {
                "frame": f,
                "historical_region": box,
                "historical_detector_matched": row["old_withheld_region"]["dm"],
                "fresh_best_iou": overlap,
                "exact_historical_bbox_equal": person is not None and person["b"] == box,
                "fresh_selected_person": person,
                "fresh_detector_observed": current.get("do"),
                "restoration_scope": "Historical source image region agreement, not physical identity/AP/recall",
            }
        )
        if overlap < 0.5:
            focus(f, "historical182 coverage region not recovered; source review mandatory")
    assert len(historical_rows) == ledger["total_withheld_person_rows"] == 182
    grouped = []
    for group in ledger["groups"]:
        start, end = group["frames"]
        rows = [r for r in historical_rows if start <= r["frame"] <= end]
        grouped.append(
            {
                "frames": [start, end],
                "total": len(rows),
                "bbox_exact": sum(r["exact_historical_bbox_equal"] for r in rows),
                "iou_at_least_half": sum(r["fresh_best_iou"] >= 0.5 for r in rows),
                "minimum_iou": min(r["fresh_best_iou"] for r in rows),
                "fresh_matched": sum((r["fresh_selected_person"] or {}).get("dm") is True for r in rows),
                "fresh_carried_or_unmatched": sum(
                    (r["fresh_selected_person"] or {}).get("dm") is not True for r in rows
                ),
            }
        )
        for f in [start - 1, start, end]:
            focus(f, "all historical182 coverage-loss intervals: before/start/end")
    summary = {
        "total": 182,
        "groups": grouped,
        "bbox_exact": sum(r["exact_historical_bbox_equal"] for r in historical_rows),
        "iou_at_least_half": sum(r["fresh_best_iou"] >= 0.5 for r in historical_rows),
        "minimum_iou": min(r["fresh_best_iou"] for r in historical_rows),
        "physical_recall_claimed": False,
    }
    write("all_182_coverage_review.json", {"summary": summary, "rows": historical_rows, "input_sha256": inputs})
    # Every current gross population loss is retained, including rows not paired
    # with generated point annotations. IDs are never treated as physical truth.
    gross = []
    for old, current in zip(old_frames, new_frames, strict=True):
        if len(current["p"]) < len(old["p"]):
            rows = [
                {
                    "historical_person": p,
                    "best_current_iou": max([iou(p["b"], q["b"]) for q in current["p"]], default=0.0),
                }
                for p in old["p"]
            ]
            gross.append(
                {
                    "frame": current["f"],
                    "old_count": len(old["p"]),
                    "fresh_count": len(current["p"]),
                    "historical_regions": rows,
                }
            )
    write(
        "all_current_gross_population_losses.json",
        {
            "scope": "Every fresh-vs-original lower participant count; source diagnosis required, not labelled FN",
            "rows": gross,
        },
    )
    loss_intervals = []
    for row in gross:
        f = row["frame"]
        if loss_intervals and f == loss_intervals[-1][1] + 1:
            loss_intervals[-1][1] = f
        else:
            loss_intervals.append([f, f])
    for start, end in loss_intervals:
        for f in [start - 1, start, end]:
            focus(f, "every new gross participant-count loss interval: before/start/end")
    for f in camera["weak_barrier_frames"]:
        for neighbor in [f - 1, f, f + 1]:
            focus(neighbor, "new weak scene barrier: mandatory source-adjacent review")
    for record in camera["cross_chunk_claims"]:
        if record["weak"]:
            focus(record["frame"], "weak reset source-camera proof crosses cache chunk")
    return {
        "input_sha256": inputs,
        "frame_reasons": frame_reasons,
        "camera_proofs": {
            k: v for k, v in camera.items() if k not in {"all_claims", "cross_chunk_claims", "format_context_per_chunk"}
        },
        "historical_coverage_summary": summary,
    }
