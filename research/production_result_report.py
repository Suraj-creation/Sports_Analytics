"""Compare completed runs using their unchanged evaluator outputs, with every GT row.

No inference or matching occurs here. Missing rows remain misses, and shared-row
comparisons cannot hide regressions behind newly matched rows. Quantiles are
supplemental descriptive metrics; the original evaluator is unchanged.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_run(path, *, fresh=False):
    metadata = json.loads((path / "benchmark_metadata.json").read_text())
    metrics = json.loads((path / "metrics.json").read_text())
    rows = list(csv.DictReader((path / "rally_comparison.csv").open()))
    inference = json.loads((path / "inference.json").read_text()) if (path / "inference.json").exists() else {}
    if fresh:
        if metadata.get("status") != "completed" or inference.get("status") != "analysed":
            raise ValueError("unfinished/failed inference cannot be compared as a completed fresh run")
        if inference["frontier_frame"] != metadata["frame_count"] - 1:
            raise ValueError("fresh run did not cover the complete source")
        if sha(path / "predicted_rallies.csv") != metadata["prediction_sha256"]:
            raise ValueError("fresh predictions differ from the executor's durable output")
    if len(rows) != metrics["detection"]["ground_truth_count"]:
        raise ValueError("comparison must preserve every ground-truth row")
    predictions = list(csv.DictReader((path / "predicted_rallies.csv").open()))
    topology = interval_topology(
        [(int(r["gt_rally"]), int(r["gt_start_frame"]), int(r["gt_end_frame"])) for r in rows],
        [(i + 1, int(r["Start_Frame"]), int(r["End_Frame"])) for i, r in enumerate(predictions)],
    )
    return {
        "path": path,
        "metadata": metadata,
        "metrics": metrics,
        "rows": rows,
        "inference": inference,
        "topology": topology,
    }


def interval_topology(ground_truth, predictions):
    """Report every positive half-open overlap, including tiny boundary tails.

    This diagnostic never changes assignment. Multiple overlaps alone do not
    establish a semantic split/merge: the complete edge sizes remain visible.
    Coverage is the union of predictions clipped to each annotation.
    """
    edges, coverage = [], {}
    gt_adjacency, pred_adjacency = {}, {}
    for identity, start, end in ground_truth:
        if end <= start:
            raise ValueError("invalid ground-truth interval")
        fragments = []
        for pred_id, pstart, pend in predictions:
            if pend <= pstart:
                raise ValueError("invalid predicted interval")
            a, b = max(start, pstart), min(end, pend)
            if a >= b:
                continue
            edges.append(
                {
                    "gt": identity,
                    "prediction": pred_id,
                    "overlap_frames": b - a,
                    "gt_fraction": (b - a) / (end - start),
                    "prediction_fraction": (b - a) / (pend - pstart),
                }
            )
            gt_adjacency.setdefault(identity, []).append(pred_id)
            pred_adjacency.setdefault(pred_id, []).append(identity)
            fragments.append((a, b))
        union, frontier = 0, start
        for a, b in sorted(fragments):
            union += max(0, b - max(frontier, a))
            frontier = max(frontier, b)
        coverage[str(identity)] = {"covered_frames": union, "fraction": union / (end - start)}
    return {
        "definition": "all positive frame overlaps; [start,end); diagnostic only; matching unchanged",
        "interpretation_limit": (
            "Tiny adjacent boundary tails are retained; multiplicity alone is not a physical split or merge."
        ),
        "edges": edges,
        "gt_overlapped_by_multiple_predictions": {str(k): v for k, v in gt_adjacency.items() if len(v) > 1},
        "predictions_overlapping_multiple_gt": {str(k): v for k, v in pred_adjacency.items() if len(v) > 1},
        "gt_union_coverage": coverage,
    }


def matched(rows):
    return {int(row["gt_rally"]): row for row in rows if row["matching_status"] == "matched"}


def mean_error(rows, field):
    return float(np.mean([abs(float(row[field])) for row in rows])) if rows else None


def compare(reference, candidate):
    old, new = matched(reference["rows"]), matched(candidate["rows"])
    common = sorted(old.keys() & new.keys())
    differences = {}
    for key in common:
        before, after = old[key], new[key]
        changes = {}
        for boundary in ("start", "end"):
            a, b = abs(int(before[f"{boundary}_frame_error"])), abs(int(after[f"{boundary}_frame_error"]))
            changes[boundary] = "improved" if b < a else "worsened" if b > a else "unchanged"
        changes["interval_unchanged"] = all(
            before[f"pred_{b}_frame"] == after[f"pred_{b}_frame"] for b in ("start", "end")
        )
        differences[str(key)] = changes
    paired = {
        field: {
            "reference": mean_error([old[i] for i in common], field),
            "candidate": mean_error([new[i] for i in common], field),
        }
        for field in ("start_frame_error", "end_frame_error", "duration_error_sec")
    }
    quantiles = {}
    for field in ("start_frame_error", "end_frame_error", "duration_error_sec"):
        values = np.asarray([abs(float(row[field])) for row in new.values()])
        quantiles[field] = {f"p{p}": float(np.percentile(values, p)) if len(values) else None for p in (50, 90, 95)}
    return {
        "shared_matched_count": len(common),
        "previously_matched_lost": sorted(old.keys() - new.keys()),
        "newly_matched": sorted(new.keys() - old.keys()),
        "paired_mae": paired,
        "per_gt_changes": differences,
        "supplemental_absolute_quantiles": quantiles,
        "quantile_method": "numpy linear percentile; matched-only",
        "retained_historical_recoveries": {str(i): i in new for i in (2, 19, 20, 23, 31)},
        "unchanged_evaluator_metrics": candidate["metrics"],
        "overlap_topology": candidate.get("topology"),
    }


def cell(row, key):
    value = row.get(key, "")
    return value if value else "—"


def fmt(value, digits=4):
    return "unavailable" if value is None else f"{value:.{digits}f}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selected", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--fresh-v1", type=Path, required=True)
    parser.add_argument("--run", action="append", required=True, help="name=completed-run-directory")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    references = {
        "original": read_run(args.original),
        "fresh_v1": read_run(args.fresh_v1),
        "selected": read_run(args.selected),
    }
    runs = {name: read_run(Path(path), fresh=True) for name, path in (spec.split("=", 1) for spec in args.run)}
    selected = references["selected"]
    args.output.mkdir(parents=True, exist_ok=False)
    results, source_hashes = {}, {}
    lines = [
        "# Complete production-candidate comparison",
        "",
        "Test1 is exposed development footage. No production or generalization acceptance follows from these metrics.",
        "The evaluator, annotations, matching and half-open intervals are unchanged.",
        "",
        "| Run | TP / FP / FN | F1 | Mean / median / min IoU | Start MAE | End MAE | Duration MAE s |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, run in {**references, **runs}.items():
        metrics, detection = run["metrics"], run["metrics"]["detection"]
        error, overlap = metrics["boundary_and_duration_errors"], metrics["overlap"]
        lines.append(
            f"| {name} | {detection['true_positives']} / {detection['false_positives']} / "
            f"{detection['false_negatives']} | {fmt(detection['f1'], 6)} | "
            f"{fmt(overlap['mean_iou'], 6)} / {fmt(overlap['median_iou'], 6)} / "
            f"{fmt(overlap['minimum_iou'], 6)} | {fmt(error['start_frame']['mae'])} | "
            f"{fmt(error['end_frame']['mae'])} | {fmt(error['duration_sec']['mae'])} |"
        )
        for filename in ("benchmark_metadata.json", "metrics.json", "rally_comparison.csv", "predicted_rallies.csv"):
            source_hashes[str((run["path"] / filename).resolve())] = sha(run["path"] / filename)
    reference_rows = {int(row["gt_rally"]): row for row in selected["rows"]}
    for name, run in runs.items():
        result = compare(selected, run)
        result["other_reference_comparisons"] = {key: compare(references[key], run) for key in ("original", "fresh_v1")}
        results[name] = result
        lines += [
            "",
            f"## {name}",
            "",
            "Boundary errors are prediction minus annotation in frames. "
            "Every GT row is retained; misses are not zero error.",
            "",
            f"Lost previous matches: {result['previously_matched_lost']}; newly matched: {result['newly_matched']}.",
            "",
            "| GT | GT [start,end) | Selected [start,end) | Candidate [start,end) | "
            "Start error | End error | Duration error s | IoU | Start / end change |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for row in run["rows"]:
            key = int(row["gt_rally"])
            old = reference_rows[key]
            change = result["per_gt_changes"].get(str(key), {})
            lines.append(
                f"| {key} | {row['gt_start_frame']},{row['gt_end_frame']} | "
                f"{cell(old, 'pred_start_frame')},{cell(old, 'pred_end_frame')} | "
                f"{cell(row, 'pred_start_frame')},{cell(row, 'pred_end_frame')} | "
                f"{cell(row, 'start_frame_error')} | {cell(row, 'end_frame_error')} | "
                f"{cell(row, 'duration_error_sec')} | {cell(row, 'interval_iou')} | "
                f"{change.get('start', row['matching_status'])} / {change.get('end', row['matching_status'])} |"
            )
        lines += [
            "",
            "All unmatched predictions:",
            "",
            "```json",
            json.dumps(run["metrics"]["unmatched_predictions"], indent=2),
            "```",
            "",
            "Complete metrics, tolerance denominators, IoU distribution, paired errors and supplemental P95:",
            "",
            "```json",
            json.dumps(result, indent=2),
            "```",
            "",
            "Actual runtime/backend/resource evidence (stage walltime aggregates overlap):",
            "",
            "```json",
            json.dumps(
                {
                    key: run["inference"].get(key)
                    for key in (
                        "elapsed_seconds",
                        "frames_per_second",
                        "per_stage_seconds",
                        "resources",
                        "execution_device",
                        "execution_backends",
                        "degraded",
                    )
                },
                indent=2,
            ),
            "```",
        ]
    manifest = {
        "mode": "completed-output comparison only; no inference/matching",
        "input_sha256": source_hashes,
        "script_sha256": sha(Path(__file__)),
        "results": results,
        "reference_topologies": {key: value["topology"] for key, value in references.items()},
        "runtime_comparison_limit": "two fresh workers ran concurrently on separate GPUs; CPU/IO were shared",
    }
    (args.output / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (args.output / "comparison.md").write_text("\n".join(lines) + "\n")
    (args.output / "executed_report.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps({name: result["paired_mae"] for name, result in results.items()}, indent=2))


if __name__ == "__main__":
    main()
