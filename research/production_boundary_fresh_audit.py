"""Independent completed-run/cache/trace boundary audit; no inference or media decoding."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/benchmarking/experiments"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def live_signatures(path, kind):
    events = [json.loads(line) for line in path.open()]
    superseded = {event["supersedes"] for event in events if event.get("supersedes")}
    return sorted(
        (event["frame_start"], event["frame_end"])
        for event in events
        if event["type"] == kind and event["event_id"] not in superseded and event["status"] != "retracted"
    )


def main():
    output = BASE / "prod_20261105_boundary_fresh_audit_v1"
    output.mkdir(exist_ok=False)
    old_rows = read_json(
        BASE / "next_20261105_fresh_air_tracklet_all36_model_firsts_v2/all36_model_temporal_firsts.json"
    )
    historical = {row["gt_rally"]: row["matched_interval"] for row in old_rows}
    cached = read_json(BASE / "prod_20261105_scene_final_validation/cached_effect_review.json")
    cached_scene = {**historical, **{row["gt_rally"]: row["new_interval"] for row in cached["scene"]["changed_rows"]}}
    result = {"mode": "independent read-only completed fresh-artifact and exact own-cache semantic audit", "runs": []}
    observed_frames = {}
    for suffix in ("association_v1", "association_scene_v1"):
        run, semantic = BASE / f"prod_20261105_fresh_{suffix}", BASE / f"prod_20261105_owncache_{suffix}"
        inference = read_json(run / "inference.json")
        metadata = read_json(run / "benchmark_metadata.json")
        replay = read_json(semantic / "replay_metadata.json")
        trace_path = semantic / "fsm_trace.jsonl"
        assert replay["source_unchanged"] and replay["baseline_interval_parity"]
        assert replay["video_sha256"] == metadata["source_video_sha256"]
        assert sha(trace_path) == replay["trace_sha256"]
        caches = sorted(run.glob("runtime/sessions/*/perception/*.msgpack"))
        cache_hashes = {path.name: sha(path) for path in caches}
        assert len(caches) == 288 and cache_hashes == replay["cache_sha256"]
        trace = [json.loads(line) for line in trace_path.open()]
        finalized = sorted(
            (
                row["update"]["finalized"]["start"],
                row["update"]["finalized"]["end"],
                row["update"]["finalized"]["reason"],
            )
            for row in trace
            if row["update"].get("finalized")
        )
        reference = sorted((row["start"], row["end"], row["end_reason"]) for row in inference["rally_events"])
        assert finalized == reference
        assert sha(run / "predicted_rallies.csv") == sha(semantic / "predicted_rallies.csv")
        timestamps = {}
        for kind in ("contact", "stroke", "rally_end"):
            actual = live_signatures(run / "events.jsonl", kind)
            assert actual == live_signatures(semantic / "events.jsonl", kind)
            timestamps[kind] = {"count": len(actual), "timestamps_and_multiplicity_exact": True}
        steps = {row["frame"]: row for row in trace if row["call"] == "step"}
        assert len(steps) == 17268
        assert all(row["evidence"]["frame"] == frame for frame, row in steps.items())
        rows = read_json(run / "comparison.json")["experiment"]["per_gt"]
        assert len(rows) == 36 and all(row["matching_status"] == "matched" for row in rows)
        per_gt = []
        for row in rows:
            number = row["gt_rally"]
            pair = [row["pred_start_frame"], row["pred_end_frame"]]
            gt_start, gt_end = row["gt_start_frame"], row["gt_end_frame"]
            candidates = [r for r in trace if gt_start <= r["frame"] < gt_end]
            observed = [r for r in candidates if r["call"] == "step" and r["evidence"]["kind"] == "observed"]
            starts = [r for r in trace if r["update"].get("started") == pair[0]]
            cancel = [r for r in candidates if r["update"].get("cancelled_start") is not None]
            final = next(
                r
                for r in trace
                if r["update"].get("finalized") is not None and r["update"]["finalized"]["start"] == pair[0]
            )
            end_proposals = [
                r
                for r in trace
                if pair[0] <= r["frame"] <= final["frame"]
                and r["after"].get("tentative_end") == pair[1]
                and r["before"].get("tentative_end") != pair[1]
            ]
            per_gt.append(
                {
                    "gt": number,
                    "ground_truth": [gt_start, gt_end],
                    "historical": historical[number],
                    "cached_scene_reference": cached_scene[number],
                    "fresh": pair,
                    "signed_error_start_end": [row["start_frame_error"], row["end_frame_error"]],
                    "first_processed_observed_in_gt": observed[0]["frame"] if observed else None,
                    "surviving_start_calls": [{"frame": r["frame"], "call": r["call"]} for r in starts],
                    "cancelled_candidates": [
                        {"frame": r["frame"], "start": r["update"]["cancelled_start"]} for r in cancel
                    ],
                    "terminal": {
                        "reason": final["update"]["finalized"]["reason"],
                        "publication": final["frame"],
                        "proposals": [{"frame": r["frame"], "evidence": r.get("evidence")} for r in end_proposals],
                    },
                    "changed_vs_historical": pair != historical[number],
                    "changed_vs_cached_scene": pair != cached_scene[number],
                }
            )
        # Only decode retained cache data; no provider/model construction or pixels.
        import msgpack

        frames = {}
        for path in caches:
            frames.update({row["f"]: row for row in msgpack.unpackb(path.read_bytes(), raw=False)["frames"]})
        observed_frames[suffix] = frames
        entry = {
            "fresh_run": str(run.relative_to(ROOT)),
            "semantic_run": str(semantic.relative_to(ROOT)),
            "source_commit": metadata["git_commit_sha"],
            "source_video_sha256": metadata["source_video_sha256"],
            "metadata_sha256": sha(run / "benchmark_metadata.json"),
            "inference_sha256": sha(run / "inference.json"),
            "trace_sha256": sha(trace_path),
            "prediction_sha256": sha(run / "predicted_rallies.csv"),
            "comparison_sha256": sha(run / "comparison.json"),
            "cache_count": len(caches),
            "cache_sha256_exact": True,
            "interval_end_reasons_and_multiplicity_exact": True,
            "prediction_csv_bytes_exact": True,
            "event_signatures": timestamps,
            "metrics": read_json(run / "metrics.json"),
            "per_gt": per_gt,
        }
        result["runs"].append(entry)
    first, second = observed_frames["association_v1"], observed_frames["association_scene_v1"]
    result["between_fresh_arms"] = {
        "raw_selected_xy_changed_frames": sum(row["s"] != second[frame]["s"] for frame, row in first.items()),
        "raw_selected_support_changed_frames": sum(row["c"] != second[frame]["c"] for frame, row in first.items()),
        "detector_ran_flag_changed_frames": sum(row["do"] != second[frame]["do"] for frame, row in first.items()),
        "scope": "Exact stored numerical comparison; coordinate differences are not automatically localization errors.",
    }
    ranges = [(7525, 7545), (8100, 8120), (10240, 10265), (10525, 10562), (10600, 10620), (10725, 10790)]
    for suffix, frames in observed_frames.items():
        selected = [
            {key: row.get(key) for key in ("f", "s", "c", "sh", "v", "cs", "do", "ps", "sa", "ce", "cc")}
            for frame, row in sorted(frames.items())
            if any(lo <= frame < hi for lo, hi in ranges)
        ]
        (output / f"{suffix}_boundary_observations.json").write_text(json.dumps(selected, indent=2) + "\n")
    result["script_sha256"] = sha(Path(__file__))
    (output / "fresh_boundary_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    (output / "executed_auditor.py").write_bytes(Path(__file__).read_bytes())
    print(
        json.dumps(
            {
                "output": str(output),
                "runs": [
                    {
                        "run": r["fresh_run"],
                        "cache_count": r["cache_count"],
                        "events": r["event_signatures"],
                        "changed_gt": [row["gt"] for row in r["per_gt"] if row["changed_vs_historical"]],
                    }
                    for r in result["runs"]
                ],
                "between_arms": result["between_fresh_arms"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
