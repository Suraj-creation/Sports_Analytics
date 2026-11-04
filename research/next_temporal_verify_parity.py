"""Bind own-cache replay to fresh intervals, end reasons and live event times."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.next_temporal_diagnose import sha, verify_trace_cache_identity  # noqa: E402


def live_times(events, kind):
    superseded = {event["supersedes"] for event in events if event.get("supersedes")}
    return sorted(
        (event["frame_start"], event["frame_end"])
        for event in events
        if event["type"] == kind and event["event_id"] not in superseded and event["status"] != "retracted"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--semantic", type=Path, required=True)
    args = parser.parse_args()
    run, semantic = args.run.resolve(), args.semantic.resolve()
    metadata = json.loads((run / "benchmark_metadata.json").read_text())
    replay = json.loads((semantic / "replay_metadata.json").read_text())
    traces = [json.loads(line) for line in (semantic / "fsm_trace.jsonl").open()]
    caches = sorted(run.glob("runtime/sessions/*/perception/*.msgpack"))
    hashes = verify_trace_cache_identity(metadata, semantic / "fsm_trace.jsonl", caches)
    reference = json.loads((run / "inference.json").read_text())["rally_events"]
    triples = sorted((event["start"], event["end"], event["end_reason"]) for event in reference)
    final = sorted(
        (row["update"]["finalized"]["start"], row["update"]["finalized"]["end"], row["update"]["finalized"]["reason"])
        for row in traces
        if row["update"]["finalized"]
    )
    assert final == triples, "every interval/end reason/multiplicity must match the fresh inference"
    assert replay["baseline_interval_parity"] is True
    assert sha(run / "predicted_rallies.csv") == sha(semantic / "predicted_rallies.csv")
    original_events = [json.loads(line) for line in (run / "events.jsonl").open()]
    semantic_events = [json.loads(line) for line in (semantic / "events.jsonl").open()]
    event_times = {}
    for kind in ("contact", "stroke", "rally_end"):
        original, current = live_times(original_events, kind), live_times(semantic_events, kind)
        assert original == current, f"live folded {kind} timestamps differ"
        event_times[kind] = {"count": len(original), "exact_timestamps_and_multiplicity": True}
    result = {
        "mode": "exact own-cache semantic parity audit; not a second perception inference",
        "fresh_run": str(run),
        "semantic_run": str(semantic),
        "fresh_source_commit": metadata["git_commit_sha"],
        "fresh_video_sha256": metadata["source_video_sha256"],
        "fresh_label_provenance_sha256": metadata["ground_truth_sha256"],
        "labels_read": False,
        "cache_count": len(hashes),
        "cache_sha256_exact": True,
        "trace_sha256_exact": True,
        "source_unchanged_during_replay": replay["source_unchanged"],
        "finalized_interval_triples_exact": True,
        "interval_count": len(final),
        "prediction_csv_bytes_exact": True,
        "event_timestamps": event_times,
        "script_sha256": sha(Path(__file__)),
        "trace_sha256": sha(semantic / "fsm_trace.jsonl"),
        "prediction_sha256": sha(run / "predicted_rallies.csv"),
    }
    target = semantic / "control_verification.json"
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(result, indent=2) + "\n")
    (semantic / "executed_parity_verifier.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
