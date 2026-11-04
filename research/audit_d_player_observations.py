"""Read-only player/court/pose audit of frozen Test 1 cached observations."""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from itertools import pairwise
from pathlib import Path

import msgpack
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def summary(frames):
    people = [p for f in frames for p in f["p"]]
    valid_pose = [p for p in people if p["k"] is not None]
    keypoints = [np.asarray(p["k"], dtype=float) for p in valid_pose]
    fresh = [f for f in frames if f["do"]]
    geometry = [f for f in frames if f["v"] == "main" and not f["l"] and f["g"] is not None and f["cs"] == "VALID"]
    wrist_supported = sum(bool(np.any(k[[9, 10], 2] >= 0.3)) for k in keypoints)
    pose_bad_schedule = sum(f["ps"] <= 0 or f["f"] % f["ps"] != 0 for f in frames for p in f["p"] if p["k"] is not None)
    detector_mismatches = []
    for f in frames:
        if f["v"] != "main" or f["r"] or f["ps"] not in (1, 6):
            continue
        stride = 2 if f["ps"] == 1 else 6
        if f["do"] != (f["f"] % stride == 0):
            detector_mismatches.append(f["f"])
    return {
        "frames": len(frames),
        "view_counts": dict(collections.Counter(f["v"] for f in frames)),
        "calibration_counts": dict(collections.Counter(f["cs"] for f in frames)),
        "geometry_usable_frames": len(geometry),
        "camera_lost_frames": sum(f["l"] for f in frames),
        "replay_or_analysis_excluded_frames": sum(f["r"] for f in frames),
        "person_count_histogram": dict(collections.Counter(len(f["p"]) for f in frames)),
        "main_view_person_count_histogram": dict(collections.Counter(len(f["p"]) for f in frames if f["v"] == "main")),
        "detector_observed_frames": len(fresh),
        "fresh_person_count_histogram": dict(collections.Counter(len(f["p"]) for f in fresh)),
        "person_rows": len(people),
        "detector_matched_rows": sum(p["dm"] is True for p in people),
        "carried_or_tracker_only_rows": sum(p["dm"] is not True for p in people),
        "negative_or_unresolved_track_rows": sum(p["t"] < 0 for p in people),
        "unique_track_ids": sorted({p["t"] for p in people}),
        "identity_method_rows": dict(collections.Counter(p["im"] for p in people)),
        "pose_stride_frame_histogram": dict(collections.Counter(f["ps"] for f in frames)),
        "pose_rows": len(valid_pose),
        "pose_row_fraction": len(valid_pose) / len(people) if people else None,
        "pose_rows_with_confident_wrist": wrist_supported,
        "pose_confidence_quantiles": np.quantile(
            np.concatenate([k[:, 2] for k in keypoints]), [0, 0.1, 0.5, 0.9, 1]
        ).tolist()
        if keypoints
        else [],
        "pose_keypoint_scores_above_one": sum(int(np.sum(k[:, 2] > 1)) for k in keypoints),
        "person_confidence_quantiles": np.quantile([p["c"] for p in people], [0, 0.1, 0.5, 0.9, 1]).tolist()
        if people
        else [],
        "pose_off_schedule_rows": pose_bad_schedule,
        "detector_schedule_mismatches": detector_mismatches,
        "observed_racket_rows": sum(p["rk"] is not None for p in people),
        "no_people_despite_usable_geometry_frames": sum(not f["p"] for f in geometry),
        "single_person_despite_usable_geometry_frames": sum(len(f["p"]) == 1 for f in geometry),
        "court_quality_quantiles": np.quantile(
            [f["q"] for f in geometry if f["q"] is not None], [0, 0.1, 0.5, 0.9, 1]
        ).tolist()
        if geometry
        else [],
        "shot_id_count": len({f["sh"] for f in frames}),
        "shot_id_transitions": [b["f"] for a, b in pairwise(frames) if a["sh"] != b["sh"]],
    }


def main(output):
    baseline = ROOT / "outputs/benchmarking/test1"
    paths = sorted((baseline / "runtime/sessions/BenchmarkTest1/perception").glob("*.msgpack"))
    frames = [f for p in paths for f in msgpack.unpackb(p.read_bytes(), raw=False)["frames"]]
    assert [f["f"] for f in frames] == list(range(17268))
    all_events = [json.loads(line) for line in (baseline / "raw_events.jsonl").open()]
    superseded = {e["supersedes"] for e in all_events if e.get("supersedes")}
    events = [e for e in all_events if e["event_id"] not in superseded and e["status"] != "retracted"]
    contacts = [e for e in events if e["type"] == "contact"]
    activity = [e for e in events if e["type"] == "activity_interval"]
    with (ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv").open() as stream:
        labels = list(csv.DictReader(stream))
    rallies = []
    for i, row in enumerate(labels, 1):
        start, end = int(row["Start_Frame"]), int(row["End_Frame"])
        report = summary(frames[start : end + 1])
        report.update(
            gt_rally=i,
            start_frame=start,
            end_frame=end,
            contact_count=sum(start <= e["frame_start"] <= end for e in contacts),
            activity_frame_counts=dict(collections.Counter()),
        )
        count = collections.Counter()
        for e in activity:
            overlap = max(0, min(end, e["frame_end"]) - max(start, e["frame_start"]) + 1)
            count[e["payload"]["state"]] += overlap
        report["activity_frame_counts"] = dict(count)
        rallies.append(report)
    counts = collections.Counter()
    for e in activity:
        counts[e["payload"]["state"]] += e["frame_end"] - e["frame_start"] + 1
    label_mask = np.zeros(len(frames), dtype=bool)
    for row in labels:
        label_mask[int(row["Start_Frame"]) : int(row["End_Frame"]) + 1] = True
    activity_gt = collections.Counter()
    for event in activity:
        for frame in range(event["frame_start"], event["frame_end"] + 1):
            activity_gt[("inside_gt_" if label_mask[frame] else "outside_gt_") + event["payload"]["state"]] += 1
    contact_people = collections.Counter(len(frames[e["frame_start"]]["p"]) for e in contacts)
    result = {
        "baseline_commit": "b773e20c62d1c398cddc3d23510bd4adf823325b",
        "summary": summary(frames),
        "rallies": rallies,
        "activity_frame_counts": dict(counts),
        "activity_gt_overlap_frame_counts": dict(activity_gt),
        "identity_ambiguity_reason_counts": dict(
            collections.Counter(e["payload"].get("reason") for e in events if e["type"] == "identity_ambiguity")
        ),
        "participant_event_kind_counts": dict(
            collections.Counter(e["payload"].get("kind") for e in events if e["type"] == "participant_observation")
        ),
        "live_contacts": len(contacts),
        "contact_frames_person_counts": dict(contact_people),
        "contacts_with_named_actor": sum(e["actors"].get("player_id") is not None for e in contacts),
        "contacts_with_provisional_participant": sum(
            e["payload"].get("participant_hypothesis", {}).get("status") == "provisional" for e in contacts
        ),
        "contact_frames_with_two_poses": sum(
            sum(p["k"] is not None for p in frames[e["frame_start"]]["p"]) == 2 for e in contacts
        ),
        "format_decisions": [e["payload"] for e in events if e["type"] == "format_decision"],
        "cache_sha256": {p.name: sha(p) for p in paths},
        "scope": "cached prediction diagnostics, not player/pose/identity ground-truth accuracy or fresh inference",
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "observations.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in ("rallies", "cache_sha256", "format_decisions")}, indent=2
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    main(parser.parse_args().output.resolve())
