"""Separate raw NN, selected association and acquisition-only diagnostics.

No annotation metrics are recomputed here. The preserved evaluator still uses
its original raw prediction role and unchanged numerical matching.
"""

import json
from collections import Counter
from hashlib import file_digest
from pathlib import Path

import msgpack
import numpy as np

OUT = Path(__file__).resolve().parent


def sha(path):
    with Path(path).open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(name, value):
    with (OUT / name).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def distribution(values):
    return {
        "count": len(values),
        "mean": float(np.mean(values)) if values else None,
        "maximum": float(np.max(values)) if values else None,
        "median": float(np.median(values)) if values else None,
    }


def selected_view(frame):
    evidence = frame.get("sa")
    if evidence is None:
        return {"status": "unavailable", "xy": None, "support": None, "source": "unavailable"}
    observed = evidence["status"] == "observed"
    current = evidence["schema"] == "badminton-shuttle-association:v3"
    return {
        "status": evidence["status"],
        "association_status": evidence["association_status"],
        "xy": evidence["selected_xy"] if observed else None,
        "support": (evidence["selected_model_support"] if current else evidence["raw_model_support"])
        if observed
        else None,
        "source": evidence["selection_coordinate_source"]
        if current
        else "legacy_raw_coordinate"
        if observed
        else "unavailable",
        "schema": evidence["schema"],
    }


def timeline(root, expected_frames, inputs):
    catalogue = root / "run/perception_completion_catalog.json"
    inputs[str(catalogue)] = sha(catalogue)
    packets, frames = [], []
    for record in read(catalogue)["files"]:
        path = root / "run" / record["path"]
        if sha(path) != record["sha256"]:
            raise ValueError("Changed completed cache bytes")
        inputs[str(path)] = record["sha256"]
        packet = msgpack.unpackb(path.read_bytes(), raw=False)
        packets.append(packet)
        frames.extend(packet["frames"])
    if [f["f"] for f in frames] != list(range(expected_frames)):
        raise ValueError("Incomplete or duplicated source timeline")
    return packets, frames


def arm_summary(frames):
    selected = [selected_view(f) for f in frames]
    different = [
        f["f"]
        for f, s in zip(frames, selected, strict=True)
        if f.get("s") is not None and s["xy"] is not None and f["s"] != s["xy"]
    ]
    observed_pose_people = sum(p.get("k") is not None and p.get("pf") == f["f"] for f in frames for p in f["p"])
    return {
        "frames": len(frames),
        "raw_NN_present": sum(f.get("s") is not None for f in frames),
        "associated_selected_present": sum(s["xy"] is not None for s in selected),
        "association_status_counts": dict(Counter(s["status"] for s in selected)),
        "association_coordinate_source_counts": dict(Counter(s["source"] for s in selected)),
        "raw_vs_selected_different_frames": different,
        "raw_vs_selected_xy_distance_px": distribution(
            [float(np.linalg.norm(np.asarray(frames[f]["s"]) - selected[f]["xy"])) for f in different]
        ),
        "detector_observed_frames": sum(f.get("do") is True for f in frames),
        "pose_stride_frame_counts": dict(Counter(str(f.get("ps")) for f in frames)),
        "person_rows": sum(len(f["p"]) for f in frames),
        "pose_present_person_rows": sum(p.get("k") is not None for f in frames for p in f["p"]),
        "pose_measured_on_current_frame_person_rows": observed_pose_people,
    }


def main():
    cfg = read(OUT / "review_config.json")
    art = Path(cfg["artifact_root"])
    guard = read(OUT / "native_guard_receipt.json")
    if guard["orchestration_completion_sha256"] != sha(art / "completion.json"):
        raise ValueError("Supplement requires actual native completed run binding")
    if read(OUT / "summary.json")["candidate_commit"] != cfg["expected_commit"]:
        raise ValueError("Supplement requires independently completed primary review")
    inputs = {str(OUT / "review_config.json"): sha(OUT / "review_config.json"), str(Path(__file__)): sha(__file__)}
    arms = {}
    for label, root in [
        ("original", Path(cfg["baseline_root"])),
        ("previous_5ae", Path(cfg["previous_candidate_root"])),
        ("current", art),
    ]:
        arms[label] = timeline(root, cfg["frame_count"], inputs)
    summaries = {label: arm_summary(frames) for label, (_, frames) in arms.items()}
    packets, current = arms["current"]
    if any(not isinstance(f.get("sa"), dict) or f["sa"].get("schema") != cfg["expected_association"] for f in current):
        raise ValueError("Current stream lacks its explicit v3 association record")
    selections = []
    for frame in current:
        selected = selected_view(frame)
        if selected["source"] == "current_candidate_peak":
            selections.append(
                {
                    "frame": frame["f"],
                    "raw_xy": frame["s"],
                    "raw_support": frame["c"],
                    "selected": selected,
                    "evidence": frame["sa"],
                    "physical_ground_truth": None,
                }
            )
    save("all_current_candidate_peak_selections.json", selections)
    comparison = {}
    for label in ["original", "previous_5ae"]:
        rows, distances, support_deltas = [], [], []
        before = arms[label][1]
        for old, frame in zip(before, current, strict=True):
            a, b = selected_view(old), selected_view(frame)
            if a["xy"] is not None and b["xy"] is not None:
                distances.append(float(np.linalg.norm(np.asarray(a["xy"]) - b["xy"])))
                support_deltas.append(b["support"] - a["support"])
            if any(a.get(k) != b.get(k) for k in ["status", "association_status", "xy", "support"]):
                rows.append(
                    {
                        "frame": frame["f"],
                        "before": a,
                        "current": b,
                        "current_raw": {"xy": frame["s"], "support": frame["c"]},
                    }
                )
        save(f"all_associated_selected_changes_{label}.json", rows)
        comparison[label] = {
            "changed_frames": len(rows),
            "both_present_selected_distance_px": distribution(distances),
            "both_present_selected_support_delta": distribution(support_deltas),
        }
    leases = {}
    for packet in packets:
        for f in packet["frames"]:
            aq = f.get("aq")
            if aq is None:
                continue
            if aq["version"] != cfg["expected_acquisition"]:
                raise ValueError("Wrong acquisition schema")
            key = aq["decision_frame"]
            lease = leases.setdefault(
                key,
                {
                    "proof": aq,
                    "policy": packet["ci"]["motion_acquisition"],
                    "source_cache_chunk": [packet["start"], packet["end"]],
                    "applied_frames": [],
                    "pose_stride_counts": Counter(),
                    "detector_observed_frames": 0,
                    "current_pose_person_rows": 0,
                },
            )
            if lease["proof"] != aq:
                raise ValueError("Same acquisition decision has inconsistent proof")
            lease["applied_frames"].append(f["f"])
            lease["pose_stride_counts"][str(f["ps"])] += 1
            lease["detector_observed_frames"] += f.get("do") is True
            lease["current_pose_person_rows"] += sum(p.get("k") is not None and p.get("pf") == f["f"] for p in f["p"])
    save("all_acquisition_leases_and_actual_sampling.json", list(leases.values()))
    summary = {
        "scope": (
            "Raw model outputs remain the original evaluator inputs; selected coordinates and acquisition "
            "are separate diagnostics, not new physical metrics"
        ),
        "arms": summaries,
        "associated_comparison": comparison,
        "current_candidate_peak_selections": len(selections),
        "acquisition_lease_count": len(leases),
        "acquisition_applied_frames": sum(len(v["applied_frames"]) for v in leases.values()),
        "actual_profiles": {str(p["start"]): p["ci"].get("profile") for p in packets},
        "physical_ground_truth": None,
        "new_neural_inference_performed_by_reviewer": False,
        "input_sha256": inputs,
    }
    if any(sha(path) != digest for path, digest in inputs.items()):
        raise ValueError("Input changed during supplemental review")
    save("raw_associated_acquisition_summary.json", summary)
    print(json.dumps({"arms": summaries, "leases": len(leases), "candidate_selections": len(selections)}))


if __name__ == "__main__":
    main()
