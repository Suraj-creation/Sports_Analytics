"""Read-only final comparison of a completed fresh Test1 production run.

Labels enter only this offline report. Historical results and the selected run
are never modified. Cached semantic/component experiments are catalogued with
their recorded mode, and cannot be selected as fresh full-pipeline evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.compare_rally_experiments import _cross_run, _fp_changes, _run  # noqa: E402
from scripts.benchmarking.evaluate_rallies import error_stats, read_csv  # noqa: E402

EXPERIMENTS = ROOT / "artifacts/benchmarking/experiments"
REFERENCES = {
    "original": ROOT / "outputs/benchmarking/test1",
    "fresh_v1": EXPERIMENTS / "fresh_image_exit_v1",
}
LABELS = ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv"


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def file_ref(path: Path) -> dict:
    return {"path": str(path.resolve()), "sha256": digest(path), "bytes": path.stat().st_size}


def common_comparison(before: dict, after: dict, old_predictions, new_predictions) -> dict:
    old = {row["gt_rally"]: row for row in before["per_gt"] if row["matching_status"] == "matched"}
    new = {row["gt_rally"]: row for row in after["per_gt"] if row["matching_status"] == "matched"}
    shared = sorted(old.keys() & new.keys())
    result = {
        "common_matched_gt_ids": shared,
        "denominator": len(shared),
        "retained_matches": shared,
        "recovered_matches": sorted(new.keys() - old.keys()),
        "lost_matches": sorted(old.keys() - new.keys()),
        "errors": {},
        "false_positives": _fp_changes(before, after),
        "cross_prediction_topology": _cross_run(old_predictions, new_predictions),
    }
    for field, key in (("start", "start_frame_error"), ("end", "end_frame_error"), ("duration", "duration_error_sec")):
        values_before = [old[i][key] for i in shared]
        values_after = [new[i][key] for i in shared]
        # Integer frame errors are exact; duration arithmetic is compared with
        # a numerical roundoff tolerance, not a sporting tolerance.
        eps = 1e-9 if field == "duration" else 0
        item = {
            "units": "seconds" if field == "duration" else "frames",
            "before": error_stats(values_before),
            "after": error_stats(values_after),
            "improved_gt_ids": [i for i in shared if abs(new[i][key]) < abs(old[i][key]) - eps],
            "worsened_gt_ids": [i for i in shared if abs(new[i][key]) > abs(old[i][key]) + eps],
            "unchanged_absolute_error_gt_ids": [i for i in shared if abs(abs(new[i][key]) - abs(old[i][key])) <= eps],
            "per_gt_signed_and_absolute_error": [
                {
                    "gt": i,
                    "before": old[i][key],
                    "after": new[i][key],
                    "absolute_error_delta": abs(new[i][key]) - abs(old[i][key]),
                }
                for i in shared
            ],
        }
        if field != "duration":
            item["fixed_common_denominator_tolerances"] = [
                {
                    "frames": tolerance,
                    "before_count": sum(abs(v) <= tolerance for v in values_before),
                    "after_count": sum(abs(v) <= tolerance for v in values_after),
                    "denominator": len(shared),
                }
                for tolerance in (1, 3, 5, 10, 15, 30)
            ]
        result["errors"][field] = item
    return result


def runtime(directory: Path) -> dict:
    metadata_path, inference_path = directory / "benchmark_metadata.json", directory / "inference.json"
    metadata, inference = read(metadata_path), read(inference_path)
    keys = (
        "status",
        "mode",
        "elapsed_seconds",
        "frames_per_second",
        "media",
        "frontier_frame",
        "configured_chunk_frames",
        "effective_chunk_frames",
        "per_stage_seconds",
        "timing_note",
        "resources",
        "execution_backends",
        "degraded",
        "models",
        "event_counts",
        "proxy_sha256",
        "effective_profile",
        "pipeline",
    )
    return {
        "metadata": file_ref(metadata_path),
        "inference": file_ref(inference_path),
        "prediction": file_ref(directory / "predicted_rallies.csv"),
        "recorded_commit": metadata.get("git_commit_sha"),
        "recorded_branch": metadata.get("active_branch"),
        "recorded_runner_sha256": metadata.get("runner_sha256"),
        "recorded_source_hashes": metadata.get("source_hashes"),
        "source_video_sha256": metadata.get("source_video_sha256"),
        "ground_truth_sha256": metadata.get("ground_truth_sha256"),
        "runtime_versions": metadata.get("runtime_versions"),
        "configuration": metadata.get("configuration"),
        "recorded_inference_fields": {key: inference.get(key) for key in keys},
        "measurement_limits": [
            "Stage wall aggregates can overlap and must not be summed.",
            "ORT provider lists do not measure per-node placement or tensor precision.",
            "Sampled process GPU memory and Torch allocator maxima have different scopes.",
            "Unavailable measurements remain null; profile names are not hardware evidence.",
        ],
    }


def require_completed_fresh(directory: Path) -> dict:
    metadata = read(directory / "benchmark_metadata.json")
    inference = read(directory / "inference.json")
    if metadata.get("status") != "completed" or inference.get("status") != "analysed":
        raise ValueError(
            "selected run must be completed full-pipeline inference (metadata completed, inference analysed)"
        )
    if any(key in metadata for key in ("component_roles", "reference_rally_intervals_only")):
        raise ValueError("hybrid component caches cannot be selected as fresh full-pipeline evidence")
    if not metadata.get("source_hashes") or not metadata.get("git_commit_sha"):
        raise ValueError("completed run lacks source hash/commit binding")
    if (
        not metadata.get("prediction_sha256")
        or digest(directory / "predicted_rallies.csv") != metadata["prediction_sha256"]
    ):
        raise ValueError("completed prediction hash is missing or inconsistent")
    if inference.get("frontier_frame") != metadata["frame_count"] - 1:
        raise ValueError("selected run does not cover the declared source frontier")
    return metadata


def experiment_catalog() -> list[dict]:
    """Catalogue all dated outputs; do not infer acceptance from metric rank."""
    names = {
        "benchmark_metadata.json",
        "replay_metadata.json",
        "executor_metadata.json",
        "manifest.json",
        "metadata.json",
        "summary.json",
        "command.json",
        "config.json",
        "source_snapshot_manifest.json",
    }
    rows = []
    for directory in sorted(EXPERIMENTS.glob("next_20261105_*")):
        if not directory.is_dir():
            continue
        row = {
            "directory": str(directory.resolve()),
            "interpretation": "recorded experiment; acceptance is a separate review decision",
        }
        candidates = sorted(
            path
            for path in directory.rglob("*.json")
            if path.name in names or path.name.endswith(("_metadata.json", "_manifest.json"))
        )
        row["source_config_metadata"] = [file_ref(path) for path in candidates]
        row["recorded_modes_statuses"] = []
        for path in candidates:
            try:
                obj = read(path)
                if isinstance(obj, dict):
                    facts = {
                        key: obj[key]
                        for key in (
                            "status",
                            "mode",
                            "scope",
                            "implementation",
                            "source_unchanged",
                            "executor_sources_unchanged",
                            "configuration",
                            "parameters",
                            "overrides",
                        )
                        if key in obj
                    }
                    if facts:
                        row["recorded_modes_statuses"].append({"path": str(path.resolve()), **facts})
            except (ValueError, OSError) as exc:
                row.setdefault("metadata_read_errors", []).append({"path": str(path), "error": str(exc)})
        row["evaluations"] = []
        for metrics in sorted(directory.rglob("metrics.json")):
            obj = read(metrics)
            row["evaluations"].append(
                {
                    **file_ref(metrics),
                    "detection": obj.get("detection") if isinstance(obj, dict) else None,
                    "metrics_json_type": type(obj).__name__,
                }
            )
        row["source_snapshot_directories"] = [
            str(path.resolve())
            for path in directory.rglob("*")
            if path.is_dir() and path.name in {"source_snapshot", "executed_scripts"}
        ]
        rows.append(row)
    return rows


def test_logs() -> list[dict]:
    result = []
    for path in sorted(EXPERIMENTS.rglob("*.log")):
        if "next_20261105" not in str(path):
            continue
        with path.open("rb") as stream:
            stream.seek(max(0, path.stat().st_size - 16384))
            tail = stream.read().decode(errors="replace")
        summaries = [
            line for line in tail.splitlines() if re.search(r"\b\d+ (?:passed|failed|skipped|warnings?)\b", line)
        ]
        if not summaries and not any(
            word in path.name.lower() for word in ("test", "regression", "check", "validation")
        ):
            continue
        result.append(
            {
                **file_ref(path),
                "verbatim_summary_lines": summaries[-3:],
                "interpretation": "log references only; synthetic contracts do not establish sporting accuracy",
            }
        )
    return result


def report_markdown(data: dict) -> str:
    lines = [
        "# Completed fresh-run comparison",
        "",
        data["scope"],
        "",
        "| Run | TP/FP/FN | F1 | Mean IoU | Start MAE frames | End MAE frames | Duration MAE s |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, run in data["runs"].items():
        m = run["metrics"]
        d, e = m["detection"], m["boundary_and_duration_errors"]
        lines.append(
            f"| {name} | {d['true_positives']}/{d['false_positives']}/{d['false_negatives']} | {d['f1']:.6f} | "
            f"{m['overlap']['mean_iou']:.6f} | {e['start_frame']['mae']:.4f} | "
            f"{e['end_frame']['mae']:.4f} | {e['duration_sec']['mae']:.4f} |"
        )
    for reference, comparison in data["comparisons"].items():
        lines += [
            "",
            f"Fixed common matched denominator versus {reference}: {comparison['denominator']} rows. "
            f"Recovered {comparison['recovered_matches']}; lost {comparison['lost_matches']}.",
            "",
            "| Error | Before MAE | After MAE | Improved GT | Worsened GT |",
            "| --- | --- | --- | --- | --- |",
        ]
        for name, obj in comparison["errors"].items():
            lines.append(
                f"| {name} ({obj['units']}) | {obj['before']['mae']} | {obj['after']['mae']} | "
                f"{obj['improved_gt_ids']} | {obj['worsened_gt_ids']} |"
            )
    lines += [
        "",
        "All 36 rows follow. Each cell is signed start/end error in frames; unavailable matches remain null.",
        "",
        "| GT | Original | Fresh v1 | Selected fresh |",
        "| --- | --- | --- | --- |",
    ]
    for rows in zip(*(run["per_gt"] for run in data["runs"].values()), strict=True):
        cells = [f"{row['start_frame_error']}/{row['end_frame_error']}" for row in rows]
        lines.append(f"| {rows[0]['gt_rally']} | " + " | ".join(cells) + " |")
    for name, run in data["runs"].items():
        lines += [
            "",
            f"Unmatched predictions for {name}:",
            "",
            "```json",
            json.dumps(run["metrics"]["unmatched_predictions"], indent=2),
            "```",
        ]
    for name, run in data["runs"].items():
        lines += [
            "",
            f"Complete unchanged evaluator metrics for {name}:",
            "",
            "```json",
            json.dumps(run["metrics"], indent=2, allow_nan=False),
            "```",
        ]
    lines += [
        "",
        "Complete evaluator metrics (all requested tolerances and distributions), topology, row coordinates/durations, "
        "runtime/model/source hashes, test logs, and the experiment catalogue are preserved in results.json. "
        "Positive-overlap topology is geometric diagnosis, not semantic proof of a merge. Original and v1 remain "
        "immutable. Test1 is development footage; independent reviewed validation remains required.",
        "",
    ]
    return "\n".join(lines)


def build(run: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError(f"refusing existing output {output}")
    metadata = require_completed_fresh(run)
    fps = float(metadata["video_fps"])
    if metadata["ground_truth_sha256"] != digest(LABELS):
        raise ValueError("selected run annotation digest differs from offline evaluation labels")
    gt = read_csv(LABELS, fps)
    if len(gt) != 36:
        raise ValueError("this explicitly Test1 report expects the immutable 36-row annotation")
    runs, predictions = {}, {}
    for name, directory in {**REFERENCES, "selected_fresh": run}.items():
        source_metadata = read(directory / "benchmark_metadata.json")
        if (
            source_metadata.get("source_video_sha256") != metadata["source_video_sha256"]
            or source_metadata.get("ground_truth_sha256") != metadata["ground_truth_sha256"]
        ):
            raise ValueError(f"{name}: input identity mismatch")
        runs[name], predictions[name] = _run(directory, gt, fps)
        runs[name]["runtime_and_provenance"] = runtime(directory)
        runs[name]["prediction_overlaps_multiple_gt"] = [
            {"pred_rally": j + 1, "positive_overlap_gt_ids": ids}
            for j, interval in enumerate(predictions[name])
            if len(
                ids := [
                    i + 1
                    for i, target in enumerate(gt)
                    if min(interval.end, target.end) > max(interval.start, target.start)
                ]
            )
            > 1
        ]
    data = {
        "schema": "next-session-final-results:v1",
        "created_utc": datetime.now(UTC).isoformat(),
        "scope": (
            "Fresh completed full-pipeline production inference on Test1 development footage; offline evaluation only. "
            "No independent sporting-accuracy or live-causality claim."
        ),
        "reporter": file_ref(Path(__file__)),
        "reporter_validation_note": (
            "The earlier next_20261105_audit_reporter_control smoke is preliminary tool validation. "
            "Its earlier reporter bytes were not archived, so exact reproduction of that tool version is not claimed. "
            "This final report preserves its own executed reporter and numerical evaluation dependencies."
        ),
        "reporting_dependencies": [
            file_ref(ROOT / name)
            for name in ("research/compare_rally_experiments.py", "scripts/benchmarking/evaluate_rallies.py")
        ],
        "labels": file_ref(LABELS),
        "runs": runs,
        "comparisons": {
            name: common_comparison(
                runs[name], runs["selected_fresh"], predictions[name], predictions["selected_fresh"]
            )
            for name in REFERENCES
        },
        "test_logs": test_logs(),
        "experiment_catalog": experiment_catalog(),
    }
    output.mkdir(parents=True, exist_ok=False)
    for source in [data["reporter"], *data["reporting_dependencies"]]:
        original = Path(source["path"])
        snapshot = (
            output / "executed_reporter.py"
            if original == Path(__file__).resolve()
            else output / "reporting_source" / original.relative_to(ROOT)
        )
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        source_bytes = original.read_bytes()
        if hashlib.sha256(source_bytes).hexdigest() != source["sha256"]:
            raise RuntimeError("reporting source changed while building the offline report")
        with snapshot.open("xb") as stream:
            stream.write(source_bytes)
        source["snapshot"] = str(snapshot)
    (output / "results.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    (output / "results.md").write_text(report_markdown(data))
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = build(args.run.resolve(), args.output.resolve())
    print(
        json.dumps(
            {"output": str(args.output.resolve()), "detection": data["runs"]["selected_fresh"]["metrics"]["detection"]},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
