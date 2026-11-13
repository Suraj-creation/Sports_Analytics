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
                and decision["version"] in {"detector-layout-scene-decision:v3", "detector-layout-scene-decision:v4"}
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
                and decision["version"] in {"detector-layout-scene-decision:v3", "detector-layout-scene-decision:v4"}
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


def contiguous(values):
    intervals = []
    for f in sorted(set(values)):
        if intervals and f == intervals[-1][1] + 1:
            intervals[-1][1] = f
        else:
            intervals.append([f, f])
    return intervals


def audit_acquisition_coverage(config, out, old_frames, new_frames):
    """Every count/region loss stays visible; old outputs are not physical GT."""
    out = Path(out)
    art = Path(config["artifact_root"])
    inputs = {str(Path(__file__)): sha(__file__)}

    def save(name, value):
        with (out / name).open("x") as f:
            json.dump(value, f, indent=2, allow_nan=False)
            f.write("\n")

    packets = []
    catalog_path = art / "run/perception_completion_catalog.json"
    inputs[str(catalog_path)] = sha(catalog_path)
    for entry in json.loads(catalog_path.read_text())["files"]:
        p = art / "run" / entry["path"]
        assert sha(p) == entry["sha256"]
        inputs[str(p)] = entry["sha256"]
        packets.append(msgpack.unpackb(p.read_bytes(), raw=False))
    camera = audit_camera_proofs(packets)
    assert camera["frames_seen"] == config["frame_count"]
    save("crosschunk_camera_format_audit.json", camera)
    gross = []
    dropped = []
    added = []
    extra_detector = []
    lost_detector = []
    for old, current in zip(old_frames, new_frames, strict=True):
        f = current["f"]
        assert old["f"] == f
        if current["do"] and not old["do"]:
            extra_detector.append(f)
        if old["do"] and not current["do"]:
            lost_detector.append(f)
        if len(current["p"]) < len(old["p"]):
            gross.append(
                {
                    "frame": f,
                    "old_count": len(old["p"]),
                    "fresh_count": len(current["p"]),
                    "historical_people": old["p"],
                    "fresh_people": current["p"],
                }
            )
        for person in old["p"]:
            nearest = max([(iou(person["b"], q["b"]), i) for i, q in enumerate(current["p"])], default=(0.0, None))
            if nearest[0] < 0.5:
                dropped.append(
                    {
                        "frame": f,
                        "historical_person": person,
                        "best_current_bbox_iou": nearest[0],
                        "best_current_index": nearest[1],
                        "fresh_people": current["p"],
                    }
                )
        for person in current["p"]:
            nearest = max([(iou(person["b"], q["b"]), i) for i, q in enumerate(old["p"])], default=(0.0, None))
            if nearest[0] < 0.5:
                added.append(
                    {
                        "frame": f,
                        "fresh_person": person,
                        "best_historical_bbox_iou": nearest[0],
                        "best_historical_index": nearest[1],
                        "historical_people": old["p"],
                    }
                )
    scope = (
        "Whole-video model-image population comparison only. No physical FN/FP/identity inference; "
        "source edits and original wrong-person outputs require diagnosis."
    )
    save("all_current_gross_population_losses.json", {"scope": scope, "rows": gross})
    save(
        "all_historical_regions_without_overlap.json",
        {"scope": scope, "diagnostic_overlap_threshold": 0.5, "rows": dropped},
    )
    save(
        "all_new_regions_without_historical_overlap.json",
        {"scope": scope, "diagnostic_overlap_threshold": 0.5, "rows": added},
    )
    save(
        "detector_freshness_changes.json",
        {
            "scope": "Recorded actual detector execution, not labelled accuracy",
            "extra_frames": extra_detector,
            "lost_frames": lost_detector,
        },
    )
    summary = {
        "original_person_rows": sum(len(r["p"]) for r in old_frames),
        "fresh_person_rows": sum(len(r["p"]) for r in new_frames),
        "gross_lower_count_frames": len(gross),
        "historical_unmatched_region_rows": len(dropped),
        "new_unmatched_region_rows": len(added),
        "extra_detector_frames": len(extra_detector),
        "lost_detector_frames": len(lost_detector),
        "raw_shuttle_xy_and_support_equal_all_frames": all(
            a["s"] == b["s"] and a["c"] == b["c"] for a, b in zip(old_frames, new_frames, strict=True)
        ),
        "physical_accuracy_claimed": False,
    }
    save("full_population_summary.json", summary)
    reasons = {}

    def focus(f, reason):
        if 0 <= f < config["frame_count"]:
            reasons.setdefault(f, []).append(reason)

    groups = {}
    for name, rows in [("lower_count", gross), ("historical_region_drop", dropped), ("new_region", added)]:
        intervals = contiguous([r["frame"] for r in rows])
        groups[name] = intervals
        for start, end in intervals:
            for f in (start - 1, start, end):
                focus(f, name + " interval before/start/end; source review required")
    save("population_change_intervals.json", groups)
    for f in camera["weak_barrier_frames"]:
        for neighbor in (f - 1, f, f + 1):
            focus(neighbor, "weak scene acquisition reset: source-adjacent review required")
    return {
        "input_sha256": inputs,
        "frame_reasons": reasons,
        "population_summary": summary,
        "camera_proofs": {
            k: v for k, v in camera.items() if k not in {"all_claims", "cross_chunk_claims", "format_context_per_chunk"}
        },
    }
