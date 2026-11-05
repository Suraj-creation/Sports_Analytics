"""GT-free independent own-cache replay/fresh semantic comparison; no inference."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.production_contact_result_audit import completed_run, fold_events  # noqa: E402


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def event_address(event):
    return [event["type"], event["frame_start"], event["frame_end"], event["seq"]]


def identities(rows):
    """Resolve IDs by their recorded event/participant origin, never string shape."""
    result = {row["event_id"]: ["event", *event_address(row)] for row in rows}
    participants = {}
    for row in sorted(rows, key=lambda row: row["seq"]):
        if row["type"] != "participant_observation":
            continue
        person = row["payload"].get("participant_id")
        if person is not None:
            participants.setdefault(person, ["participant", *event_address(row), row["payload"].get("track_id")])
    result.update(participants)
    return result


def normalize(value, identity_map, field=None):
    if isinstance(value, dict):
        return {key: normalize(item, identity_map, key) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize(item, identity_map, field) for item in value]
    identity_field = isinstance(field, str) and (
        field.endswith(("_id", "_ids")) or field in {"attribution_target", "supersedes"}
    )
    if identity_field and isinstance(value, str) and value in identity_map:
        return identity_map[value]
    return value


def semantic_event(event, identity_map):
    result = normalize(event, identity_map)
    # Each replay is a new isolated session. Keep all other provenance fields.
    result["session_id"] = "<separate isolated session>"
    result["provenance"] = {key: item for key, item in result.get("provenance", {}).items() if key != "profile"}
    return result


def differences(left, right, path=""):
    if type(left) is not type(right):
        return [{"path": path, "fresh": left, "replay": right}]
    if isinstance(left, dict):
        result = []
        for key in sorted(left.keys() | right.keys()):
            if key not in left or key not in right:
                result.append({"path": path + "/" + key, "fresh": left.get(key), "replay": right.get(key)})
            else:
                result.extend(differences(left[key], right[key], path + "/" + key))
        return result
    if isinstance(left, list):
        if len(left) != len(right):
            return [{"path": path, "fresh": left, "replay": right}]
        return [
            d
            for index, (a, b) in enumerate(zip(left, right, strict=True))
            for d in differences(a, b, path + "/" + str(index))
        ]
    return [] if left == right else [{"path": path, "fresh": left, "replay": right}]


def compare_live(fresh_rows, replay_rows):
    _, fresh, _ = fold_events(fresh_rows)
    _, replay, _ = fold_events(replay_rows)
    maps = identities(fresh_rows), identities(replay_rows)
    grouped = []
    for rows in (fresh, replay):
        groups = defaultdict(list)
        for row in sorted(rows, key=lambda row: row["seq"]):
            groups[(row["type"], row["frame_start"], row["frame_end"])].append(row)
        grouped.append(groups)
    result, matched = [], defaultdict(list)
    for key in sorted(grouped[0].keys() | grouped[1].keys()):
        left, right = grouped[0].get(key, []), grouped[1].get(key, [])
        if len(left) != len(right):
            result.append(
                {
                    "event_address": key,
                    "cause": "live event multiplicity differs",
                    "fresh_ids": [e["event_id"] for e in left],
                    "replay_ids": [e["event_id"] for e in right],
                }
            )
            continue
        for a, b in zip(left, right, strict=True):
            diff = differences(semantic_event(a, maps[0]), semantic_event(b, maps[1]))
            matched[key[0]].append(
                {
                    "start": key[1],
                    "end": key[2],
                    "fresh_id": a["event_id"],
                    "replay_id": b["event_id"],
                    "exact_semantic_parity": not diff,
                    "fresh_status": a["status"],
                    "replay_status": b["status"],
                    "fresh_end_reason": a["payload"].get("end_reason"),
                    "replay_end_reason": b["payload"].get("end_reason"),
                }
            )
            if diff:
                detail = {"event_address": key, "differences": diff}
                if key[0] == "identity_ambiguity" and len(diff) == 1 and diff[0]["path"] == "/payload/tracker_instance":
                    expected = [
                        hashlib.sha256(f"{event['session_id']}:{event['frame_start']}".encode()).hexdigest()[:16]
                        for event in (a, b)
                    ]
                    if [diff[0]["fresh"], diff[0]["replay"]] == expected:
                        detail["verified_cause"] = "SHA256(isolated_session_id:reset_frame)[:16] tracker namespace"
                if key[0] == "format_decision" and diff == [
                    {
                        "path": "/provenance/model",
                        "fresh": "sustained_target_court_format_v1",
                        "replay": "diagnostic:recorded-format",
                    }
                ]:
                    detail["verified_cause"] = (
                        "replay explicitly supplies recorded format payload with diagnostic provider"
                    )
                result.append(detail)
    return {
        "fresh_live_counts": dict(Counter(e["type"] for e in fresh)),
        "replay_live_counts": dict(Counter(e["type"] for e in replay)),
        "differences": result,
        "matched": dict(matched),
        "ignored_runtime_identity_scope": [
            "session_id",
            "event IDs resolved by type/frame/sequence",
            "participant IDs resolved by recorded origin event/track",
            "provenance.profile only",
        ],
        "profile_labels": {
            "fresh": dict(Counter(e.get("provenance", {}).get("profile") for e in fresh)),
            "replay": dict(Counter(e.get("provenance", {}).get("profile") for e in replay)),
        },
    }


def audit(fresh, replay, output):
    metadata, inference = completed_run(fresh)
    replay_meta, candidate = read(replay / "replay_metadata.json"), read(replay / "candidate_manifest.json")
    if not replay_meta.get("source_unchanged") or replay_meta.get("git_commit") != metadata["git_commit_sha"]:
        raise ValueError("replay source guard/commit mismatch")
    if Path(candidate["source_run"]).resolve() != fresh.resolve():
        raise ValueError("replay bound to another run")
    if candidate["source_metadata_sha256"] != digest(fresh / "benchmark_metadata.json"):
        raise ValueError("replay source metadata bytes changed")
    if candidate["replay_metadata_sha256"] != digest(replay / "replay_metadata.json"):
        raise ValueError("replay metadata digest mismatch")
    if replay_meta["source_sha256"] != metadata["source_hashes"]:
        raise ValueError("replay/fresh executed source hashes differ")
    watches = {}
    for relative, expected in replay_meta["source_sha256"].items():
        path = replay / "executed_source" / relative
        if digest(path) != expected:
            raise ValueError("captured executed source mismatch")
        watches[str(path)] = expected
    traces = [json.loads(s) for s in (replay / "fsm_trace.jsonl").read_text().splitlines() if s]
    if digest(replay / "fsm_trace.jsonl") != replay_meta["trace_sha256"]:
        raise ValueError("replay trace digest mismatch")
    steps = [row["frame"] for row in traces if row["call"] == "step"]
    count = metadata["frame_count"]
    if steps != list(range(count)) or traces[-1]["call"] != "flush" or traces[-1]["frame"] != count - 1:
        raise ValueError("replay full-step/EOF frontier mismatch")
    cache_paths = sorted((fresh / "runtime/sessions").glob("*/perception/*.msgpack"))
    actual_caches = {path.name: digest(path) for path in cache_paths}
    if actual_caches != replay_meta["cache_sha256"]:
        raise ValueError("replay did not use exactly its fresh own caches")
    for path in cache_paths:
        watches[str(path)] = actual_caches[path.name]
    rows = []
    for run in (fresh, replay):
        path = run / "events.jsonl"
        rows.append([json.loads(line) for line in path.read_text().splitlines() if line])
    result = compare_live(*rows)
    result.update(
        schema="production-own-cache-parity:v1",
        fresh=str(fresh),
        replay=str(replay),
        canonical_frames=count,
        replay_step_count=len(steps),
        frontier=inference["frontier_frame"],
        flush_frame=traces[-1]["frame"],
        own_cache_count=len(actual_caches),
        source_commit=metadata["git_commit_sha"],
        no_GT_or_model_access=True,
        replay_is_fresh_inference=False,
    )
    for run in (fresh, replay):
        path = run / "predicted_rallies.csv"
        with path.open() as stream:
            intervals = [(int(row["Start_Frame"]), int(row["End_Frame"])) for row in csv.DictReader(stream)]
        result["fresh_intervals" if run == fresh else "replay_intervals"] = intervals
        for name in ("events.jsonl", "predicted_rallies.csv"):
            watches[str(run / name)] = digest(run / name)
    result["interval_sequence_equal"] = result["fresh_intervals"] == result["replay_intervals"]
    for path in [
        fresh / "benchmark_metadata.json",
        fresh / "inference.json",
        replay / "replay_metadata.json",
        replay / "candidate_manifest.json",
        replay / "fsm_trace.jsonl",
        replay / "executed_candidate.py",
        Path(__file__),
        ROOT / "research/production_contact_result_audit.py",
    ]:
        watches[str(path)] = digest(path)
    for path, expected in watches.items():
        if digest(path) != expected:
            raise ValueError("input changed during audit")
    if output.exists() or fresh.resolve() in output.resolve().parents or replay.resolve() in output.resolve().parents:
        raise ValueError("unique new output outside input runs required")
    output.mkdir(parents=True)
    (output / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    result["input_files_sha256"] = watches
    (output / "audit.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fresh", required=True, type=Path)
    parser.add_argument("--replay", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.fresh.resolve(strict=True), args.replay.resolve(strict=True), args.output.resolve())
    print(
        json.dumps(
            {
                "event_differences": len(result["differences"]),
                "interval_sequence_equal": result["interval_sequence_equal"],
                "counts": result["fresh_live_counts"],
                "output": str(args.output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
