"""Compare two completed runs' own observations and folded semantic outputs.

This reads recorded artifacts. It never reruns perception or treats this
comparison as independent model inference. Ground-truth values are not read.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import zip_longest
from pathlib import Path

import msgpack

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.next_evidence_provenance import file_sha256  # noqa: E402


def frame_rows(run: Path):
    roots = list((run / "runtime/sessions").glob("*/perception"))
    if len(roots) != 1:
        raise ValueError("expected exactly one observation cache directory")
    expected = 0
    for path in sorted(roots[0].glob("*.msgpack")):
        record = msgpack.unpackb(path.read_bytes(), raw=False)
        frames = record["frames"]
        if not frames or frames[0]["f"] != record["start"] or frames[-1]["f"] != record["end"]:
            raise ValueError(f"cache range does not match frame identities: {path}")
        for frame in frames:
            if frame["f"] != expected:
                raise ValueError(f"cache duplicate/gap at frame {expected}: {path}")
            expected += 1
            yield frame


def folded_events(run: Path):
    path = run / "events.jsonl"
    if not path.is_file():
        path = run / "raw_events.jsonl"
    records = [json.loads(line) for line in path.open()]
    superseded = {record["supersedes"] for record in records if record.get("supersedes")}
    return [record for record in records if record["status"] != "retracted" and record["event_id"] not in superseded]


def compare(left: Path, right: Path) -> dict:
    changed_fields = Counter()
    examples = []
    counts = Counter(
        dict.fromkeys(
            [
                "paired_frames",
                "changed_frames",
                "frames_only_in_left",
                "frames_only_in_right",
                "left_raw_shuttle_observed",
                "right_raw_shuttle_observed",
                "shuttle_missingness_changed_frames",
            ],
            0,
        )
    )
    for a, b in zip_longest(frame_rows(left), frame_rows(right)):
        if a is None or b is None:
            counts["frames_only_in_left" if b is None else "frames_only_in_right"] += 1
            continue
        counts["paired_frames"] += 1
        changed = sorted(key for key in set(a) | set(b) if (key in a) != (key in b) or a.get(key) != b.get(key))
        if changed:
            counts["changed_frames"] += 1
            changed_fields.update(changed)
            if len(examples) < 20:
                examples.append({"frame": a["f"], "fields": changed})
        if a["s"] is not None:
            counts["left_raw_shuttle_observed"] += 1
        if b["s"] is not None:
            counts["right_raw_shuttle_observed"] += 1
        if (a["s"] is None) != (b["s"] is None):
            counts["shuttle_missingness_changed_frames"] += 1

    event_checks = {}
    left_events, right_events = folded_events(left), folded_events(right)
    for kind in ["contact", "stroke"]:
        a = sorted(record["frame_start"] for record in left_events if record["type"] == kind)
        b = sorted(record["frame_start"] for record in right_events if record["type"] == kind)
        event_checks[kind] = {
            "left_count": len(a),
            "right_count": len(b),
            "timestamps_equal": a == b,
            "only_left": list((Counter(a) - Counter(b)).elements()),
            "only_right": list((Counter(b) - Counter(a)).elements()),
        }
    left_inference = json.loads((left / "inference.json").read_text())
    right_inference = json.loads((right / "inference.json").read_text())
    left_metadata = json.loads((left / "benchmark_metadata.json").read_text())
    right_metadata = json.loads((right / "benchmark_metadata.json").read_text())
    for metadata, inference in [(left_metadata, left_inference), (right_metadata, right_inference)]:
        if metadata["status"] != "completed" or inference["status"] != "analysed":
            raise ValueError("run comparison requires completed inference artifacts")

    def identity(run, metadata, inference):
        cached_count = (
            counts["paired_frames"] + counts["frames_only_in_left" if run == left else "frames_only_in_right"]
        )
        if cached_count != inference["media"]["n_frames"]:
            raise ValueError("completed run's recorded cache does not cover its declared media frame count")
        return {
            "recorded_run_status": metadata["status"],
            "recorded_inference_status": inference["status"],
            "git_commit": metadata["git_commit_sha"],
            "source_hashes": metadata.get("source_hashes", metadata.get("production_source_hashes")),
            "runner_sha256": metadata.get("runner_sha256"),
            "metadata_sha256": file_sha256(run / "benchmark_metadata.json"),
            "inference_sha256": file_sha256(run / "inference.json"),
            "source_video_sha256": metadata["source_video_sha256"],
            "media": inference["media"],
            "cached_frame_count": cached_count,
            "cached_frame_count_matches_media": cached_count == inference["media"]["n_frames"],
            "frontier_matches_media_end": inference["frontier_frame"] == inference["media"]["n_frames"] - 1,
            "cache_files": len(list((run / "runtime/sessions").glob("*/perception/*.msgpack"))),
            "models": inference["models"],
            "actual_backends": inference["execution_backends"],
            "fallbacks": inference["degraded"],
        }

    def intervals(inference):
        return sorted((row["start"], row["end"], row["end_reason"]) for row in inference["rally_events"])

    return {
        "mode": "recorded-artifact comparison; not another model-inference execution",
        "left_directory": str(left),
        "right_directory": str(right),
        "left_run": identity(left, left_metadata, left_inference),
        "right_run": identity(right, right_metadata, right_inference),
        "harness_sha256": file_sha256(Path(__file__)),
        "counts": dict(counts),
        "changed_frame_fields": dict(changed_fields),
        "first_changed_frames": examples,
        "folded_events": event_checks,
        "rally_interval_and_reason_parity": intervals(left_inference) == intervals(right_inference),
        "left_intervals": intervals(left_inference),
        "right_intervals": intervals(right_inference),
        "prediction_bytes_equal": (left / "predicted_rallies.csv").read_bytes()
        == (right / "predicted_rallies.csv").read_bytes(),
        "actual_backend_records_equal": left_inference["execution_backends"] == right_inference["execution_backends"],
        "model_records_equal": left_inference["models"] == right_inference["models"],
        "proxy_sha256_equal": left_inference["proxy_sha256"] == right_inference["proxy_sha256"],
        "source_video_sha256_equal": left_metadata["source_video_sha256"] == right_metadata["source_video_sha256"],
        "fps_equal": left_metadata["video_fps"] == right_metadata["video_fps"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    result = compare(args.left.resolve(), args.right.resolve())
    (args.output / "comparison.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"counts": result["counts"], "prediction_bytes_equal": result["prediction_bytes_equal"]}))


if __name__ == "__main__":
    main()
