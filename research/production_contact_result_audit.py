"""Read-only completed-run contact/association audit; never reads GT or runs models.

Counts describe current machine hypotheses. They do not measure physical hit,
hitter, shot-family, calibration or generalization accuracy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELIABILITIES = {"confirmed", "probable", "ambiguous", "rejected", "insufficient"}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fold_events(rows):
    """Fold by identity/lineage, independent of export's frame versus seq ordering."""
    by_id = {}
    successors = defaultdict(list)
    for row in rows:
        identity = row["event_id"]
        if identity in by_id:
            raise ValueError(f"duplicate event identity: {identity}")
        by_id[identity] = row
        if row.get("supersedes"):
            successors[row["supersedes"]].append(identity)
    completed = set()
    for identity in by_id:
        seen, current = set(), identity
        while current is not None and current not in completed:
            if current in seen:
                raise ValueError("cyclic event supersession")
            if current not in by_id:
                raise ValueError(f"superseded event missing from complete export: {current}")
            seen.add(current)
            current = by_id[current].get("supersedes")
        completed.update(seen)
    current = [row for identity, row in by_id.items() if identity not in successors and row["status"] != "retracted"]
    return by_id, current, dict(successors)


def resolve_current(identity, by_id, successors):
    while identity in successors:
        following = successors[identity]
        if len(following) != 1:
            return None  # A branching lineage is not a unique current parent.
        identity = following[0]
    row = by_id.get(identity)
    return row if row is not None and row["status"] != "retracted" else None


def completed_run(run):
    metadata = json.loads((run / "benchmark_metadata.json").read_text())
    if metadata.get("status") != "completed":
        raise ValueError("refusing unfinished or failed run; benchmark status must be completed")
    inference = json.loads((run / "inference.json").read_text())
    count = metadata.get("frame_count")
    if (
        type(count) is not int
        or count <= 0
        or inference.get("status") != "analysed"
        or inference.get("frontier_frame") != count - 1
        or inference.get("media", {}).get("n_frames") != count
    ):
        raise ValueError("completed run lacks its complete analysed canonical frontier")
    if metadata.get("inference") != inference:
        raise ValueError("completed benchmark and inference records disagree")
    if sha(run / "predicted_rallies.csv") != metadata.get("prediction_sha256"):
        raise ValueError("completed prediction bytes do not match their recorded digest")
    for name, field in (
        ("executed_runner.py", "runner_sha256"),
        ("executed_resource_guard.py", "resource_guard_sha256"),
    ):
        if field in metadata and sha(run / name) != metadata[field]:
            raise ValueError(f"executed harness digest mismatch: {name}")
    return metadata, inference


class Issues:
    def __init__(self):
        self.counts = Counter()
        self.examples = []

    def add(self, kind, **details):
        self.counts[kind] += 1
        if len(self.examples) < 200:
            self.examples.append({"kind": kind, **details})


def _valid_wrists(keypoints):
    if not isinstance(keypoints, list) or len(keypoints) != 17:
        return False
    return any(
        isinstance(keypoints[index], list)
        and len(keypoints[index]) == 3
        and all(type(value) in (int, float) and math.isfinite(value) for value in keypoints[index])
        and keypoints[index][2] >= 0.3
        for index in (9, 10)
    )


def cache_frames(run, session_id, frontier, issues):
    import msgpack

    paths = sorted((run / "runtime/sessions" / session_id / "perception").glob("*.msgpack"))
    if not paths:
        raise ValueError("completed run has no own perception caches; PF/RF cannot be audited")
    frames, hashes, counts = {}, {}, Counter()
    for path in paths:
        data = path.read_bytes()
        hashes[str(path.relative_to(run))] = hashlib.sha256(data).hexdigest()
        payload = msgpack.unpackb(data, raw=False)
        version = payload.get("v", 1)
        counts[f"cache_segments_v{version}"] += 1
        for row in payload["frames"]:
            frame = row["f"]
            if type(frame) is not int or not 0 <= frame <= frontier or frame in frames:
                raise ValueError("cache frame indices must be unique and inside completed media")
            people = {}
            for person in row["p"]:
                counts["person_rows"] += 1
                pf, rf = (person.get("pf"), person.get("rf")) if version >= 20 else (None, None)
                for source, name in ((pf, "pose"), (rf, "racket")):
                    if source is not None and (type(source) is not int or source < 0 or source > frame):
                        issues.add(f"{name}_source_frame_violation", frame=frame, source=source, track_id=person["t"])
                    counts[
                        f"{name}_source_unknown"
                        if source is None
                        else f"{name}_source_current"
                        if source == frame
                        else f"{name}_source_stale"
                    ] += 1
                counts["keypoints_without_known_pose_source"] += int(person.get("k") is not None and pf is None)
                counts["racket_geometry_without_known_source"] += int(person.get("rk") is not None and rf is None)
                if person["t"] in people:
                    issues.add("duplicate_person_track_in_frame", frame=frame, track_id=person["t"])
                people[person["t"]] = {
                    "pf": pf,
                    "rf": rf,
                    "dm": person.get("dm"),
                    "valid_wrists": _valid_wrists(person.get("k")),
                    "racket": person.get("rk") is not None,
                }
            observation = row.get("sa") if version >= 19 else None
            if observation is not None:
                counts["association_" + observation["status"]] += 1
                counts["association_state_" + observation["association_status"]] += 1
                if (
                    observation["frame_idx"] != frame
                    or observation["raw_xy"] != row["s"]
                    or observation["raw_model_support"] != row["c"]
                ):
                    issues.add("association_raw_identity_mismatch", frame=frame)
                if observation["epoch"] != (row["sh"] << 32) | row.get("ce", 0):
                    issues.add("association_epoch_mismatch", frame=frame)
                if observation["status"] == "observed" and observation["selected_xy"] != row["s"]:
                    issues.add("association_invented_selected_coordinate", frame=frame)
                if observation["status"] != "observed" and observation["selected_xy"] is not None:
                    issues.add("unobserved_association_emits_coordinate", frame=frame)
                if any(
                    type(f) is not int or f < 0 or f >= frame for f in observation.get("competing_motion_frames", [])
                ):
                    issues.add("association_future_witness", frame=frame)
            else:
                counts["association_unavailable"] += 1
            frames[frame] = {
                "frame": frame,
                "version": version,
                "pose_stride": row.get("ps"),
                "detector_observed": row.get("do"),
                "people": people,
                "association": observation,
                "raw_xy": row["s"],
                "raw_support": row["c"],
            }
    if set(frames) != set(range(frontier + 1)):
        raise ValueError("own perception caches do not cover the completed canonical timeline exactly")
    return frames, hashes, dict(counts)


def evidence_issues(event, evidence, frontier, frames, track_id, issues, counters, source_sha256=None):
    inputs = evidence["inputs"]
    frame = event["frame_start"]
    start, stop, available = inputs["context_start"], inputs["context_stop"], inputs["available_through"]
    identity = event["event_id"]
    if inputs["frame"] != frame:
        issues.add("contact_evidence_frame_mismatch", event_id=identity, frame=frame, evidence_frame=inputs["frame"])
    if not 0 <= start <= frame < stop or not frame <= available <= frontier or stop > frontier + 1:
        issues.add("contact_context_outside_media", event_id=identity, frame=frame)
    motion = inputs.get("motion") or {}
    for kind in ("before", "after"):
        for sample in motion.get(kind + "_frames", []):
            if (
                type(sample) is not int
                or not start <= sample < stop
                or sample > available
                or (kind == "before" and sample > frame)
                or (kind == "after" and sample < frame)
            ):
                issues.add("motion_sample_frontier_violation", event_id=identity, frame=frame, sample=sample, side=kind)
    for kind in ("player", "pose", "racket"):
        for sample in inputs.get(kind + "_observation_frames", []):
            if type(sample) is not int or not start <= sample < stop or sample > available:
                issues.add("cue_sample_frontier_violation", event_id=identity, frame=frame, sample=sample, cue=kind)
                continue
            source = frames.get(sample)
            person = source["people"].get(track_id) if source is not None and track_id is not None else None
            if person is None:
                counters[kind + "_cue_identity_unverifiable"] += 1
                continue
            counters[kind + "_cue_identity_checked"] += 1
            if kind == "player" and (source["detector_observed"] is not True or person["dm"] is not True):
                issues.add("player_cue_without_detector_match", event_id=identity, frame=frame, sample=sample)
            if kind == "pose":
                cadence = source["pose_stride"]
                if (
                    person["pf"] != sample
                    or not person["valid_wrists"]
                    or type(cadence) is not int
                    or cadence <= 0
                    or sample % cadence
                ):
                    issues.add("pose_cue_without_exact_fresh_source", event_id=identity, frame=frame, sample=sample)
            if kind == "racket" and (person["rf"] != sample or not person["racket"] or person["dm"] is not True):
                issues.add("racket_cue_without_exact_fresh_source", event_id=identity, frame=frame, sample=sample)
    status = evidence["impact"]["reliability"]
    if status == "confirmed":
        review = inputs.get("review")
        if (
            review is None
            or review.get("frame") != frame
            or review.get("physical_impact") is not True
            or (source_sha256 is not None and review.get("source_sha256") != source_sha256)
        ):
            issues.add("physical_confirmation_without_matching_external_review", event_id=identity, frame=frame)


def audit_run(run, output, focus_frames=(), expected_source=None):
    run, output = run.resolve(), output.resolve()
    metadata, inference = completed_run(run)  # Must precede any event/cache reads or output creation.
    if expected_source is not None and metadata["git_commit_sha"] != expected_source:
        raise ValueError("completed run is from another measured source commit")
    if output == run or output.is_relative_to(run):
        raise ValueError("audit output must be outside the immutable input run")
    output.mkdir(parents=True, exist_ok=False)
    events_path = run / "events.jsonl"
    rows = [json.loads(line) for line in events_path.read_text().splitlines()]
    by_id, current, successors = fold_events(rows)
    sessions = {row["session_id"] for row in rows}
    if len(sessions) != 1:
        raise ValueError("audit requires one explicit session in the complete event export")
    issues, cue_counts = Issues(), Counter()
    frontier = inference["frontier_frame"]
    frames, cache_hashes, cache_counts = cache_frames(run, next(iter(sessions)), frontier, issues)
    episode_tracks = defaultdict(set)
    for row in current:
        payload = row["payload"]
        if (
            row["type"] == "participant_observation"
            and payload.get("participant_id") is not None
            and type(payload.get("track_id")) is int
        ):
            episode_tracks[payload["participant_id"]].add(payload["track_id"])
    for identity, following in successors.items():
        if len(following) != 1:
            issues.add("branching_supersession", event_id=identity, successors=following)
    summaries, contacts = {}, []
    for kind in ("contact", "stroke", "shuttle_turn"):
        selected = [row for row in current if row["type"] == kind]
        summary = {
            "live_count": len(selected),
            "lifecycle_statuses": dict(Counter(r["status"] for r in selected)),
            "physical_statuses": dict(
                Counter(r["payload"].get("physical_event_status", "legacy_unknown") for r in selected)
            ),
            "named_actor_ids": dict(
                Counter(r["actors"]["player_id"] for r in selected if r["actors"]["player_id"] is not None)
            ),
            "unattributed_actor_count": sum(r["actors"]["player_id"] is None for r in selected),
        }
        if kind == "stroke":
            summary["labels"] = dict(Counter(r["payload"].get("stroke", "unknown") for r in selected))
            summary["classification_statuses"] = dict(
                Counter(r["payload"].get("classification_status", "legacy_unknown") for r in selected)
            )
            summary["abstention_reasons"] = dict(
                Counter(r["payload"].get("classification_abstention_reason") or "none" for r in selected)
            )
        if kind == "contact":
            summary["trajectory_reliability"] = dict(
                Counter(
                    (r["payload"].get("physical_evidence") or {})
                    .get("trajectory", {})
                    .get("reliability", "legacy_unknown")
                    for r in selected
                )
            )
            summary["assessment_policies"] = dict(
                Counter((r["payload"].get("physical_evidence") or {}).get("policy", "legacy_unknown") for r in selected)
            )
            summary["physical_reasons"] = dict(
                Counter(
                    reason
                    for r in selected
                    for reason in (r["payload"].get("physical_evidence") or {}).get("impact", {}).get("reasons", [])
                )
            )
        summaries[kind] = summary
        for event in selected:
            frame, payload = event["frame_start"], event["payload"]
            if not 0 <= frame <= event["frame_end"] <= frontier:
                issues.add("event_frame_outside_completed_media", event_id=event["event_id"], frame=frame)
            if kind == "stroke":
                parent = resolve_current(
                    payload.get("physical_evidence_event_id", payload.get("contact_event_id")), by_id, successors
                )
                if parent is None or parent["type"] != "contact":
                    issues.add("stroke_without_live_contact_parent", event_id=event["event_id"], frame=frame)
                elif payload.get("physical_event_status", "legacy_unknown") != parent["payload"].get(
                    "physical_event_status", "legacy_unknown"
                ):
                    issues.add("stroke_parent_physical_status_mismatch", event_id=event["event_id"], frame=frame)
            if kind != "contact":
                continue
            evidence = payload.get("physical_evidence")
            if evidence is not None:
                if payload.get("physical_event_status") != evidence["impact"]["reliability"]:
                    issues.add("contact_physical_status_mismatch", event_id=event["event_id"], frame=frame)
                target = evidence["inputs"].get("attribution_target")
                tracks = episode_tracks.get(target, set())
                track_id = next(iter(tracks)) if len(tracks) == 1 else event["actors"].get("track_id")
                hypothesis = payload.get("participant_hypothesis") or {}
                if track_id is None and hypothesis.get("participant_id") == target:
                    track_id = hypothesis.get("track_id")
                evidence_issues(
                    event, evidence, frontier, frames, track_id, issues, cue_counts, metadata["source_video_sha256"]
                )
            contacts.append(
                {
                    "frame": frame,
                    "event_id": event["event_id"],
                    "actor_id": event["actors"]["player_id"],
                    "support": event["confidence"],
                    "model": event["provenance"].get("model"),
                    "physical_status": payload.get("physical_event_status", "legacy_unknown"),
                    "physical_evidence": evidence,
                }
            )
    report = {
        "schema": "production-contact-result-audit:v1",
        "mode": "GT-free read-only completed-run audit; no model or semantic inference",
        "run": str(run),
        "raw_event_rows": len(rows),
        "current_event_rows": len(current),
        "frontier_frame": frontier,
        "events": summaries,
        "cache_counts": cache_counts,
        "cue_identity_checks": dict(cue_counts),
        "violation_counts": dict(issues.counts),
        "violation_examples": issues.examples,
        "violation_examples_limit": 200,
        "focus_windows": {
            str(f): [frames[j] for j in range(max(0, f - 3), min(frontier, f + 3) + 1)] for f in focus_frames
        },
        "measured_source": {
            key: metadata.get(key)
            for key in (
                "git_commit_sha",
                "active_branch",
                "source_hashes",
                "runner_sha256",
                "resource_guard_sha256",
                "source_video_sha256",
                "allocated_gpu_uuid",
                "configuration",
                "dataset_role",
                "exploratory",
            )
        },
        "configuration_sha256": hashlib.sha256(
            json.dumps(metadata["configuration"], sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "limits": [
            "Counts and reliability states are machine-policy coverage, not physical-contact/shot/hitter accuracy",
            "No reviewed labels and no inference/GT file access",
            "No named/team identity inferred from arbitrary actor or track IDs",
            (
                "Post-contact context is allowed through its declared available frontier; "
                "this does not reconstruct decision emission latency"
            ),
            "Cue identity checks remain explicitly unverifiable if no unique recorded target track exists",
        ],
    }
    (output / "audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (output / "contacts.jsonl").write_text("".join(json.dumps(row, allow_nan=False) + "\n" for row in contacts))
    paths = [
        run / name
        for name in (
            "benchmark_metadata.json",
            "inference.json",
            "events.jsonl",
            "predicted_rallies.csv",
            "executed_runner.py",
            "executed_resource_guard.py",
        )
        if (run / name).is_file()
    ]
    manifest = {
        "executor_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "auditor_sha256": sha(Path(__file__)),
        "input_sha256": {str(p): sha(p) for p in paths},
        "own_cache_sha256": cache_hashes,
        "output_sha256": {name: sha(output / name) for name in ("audit.json", "contacts.jsonl")},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--focus-frame", type=int, action="append", default=[])
    parser.add_argument("--expected-source-commit")
    args = parser.parse_args()
    result = audit_run(args.run, args.output, args.focus_frame, args.expected_source_commit)
    print(json.dumps({"events": result["events"], "violation_counts": result["violation_counts"]}, indent=2))


if __name__ == "__main__":
    main()
