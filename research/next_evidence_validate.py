"""Recheck immutable evidence and every historical experiment without inference.

Only the required new output directory is written. No report is regenerated and
no historical artifact is modified. Run in the existing GPU-host environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.next_evidence_provenance import file_sha256  # noqa: E402
from scripts.benchmarking.evaluate_rallies import evaluate, read_csv, save_evaluation  # noqa: E402


def load(path):
    return json.loads(Path(path).read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    registry = load(ROOT / "research/evidence_registry.json")
    results = load(ROOT / "research/experiment_results.json")
    original_audit = load(ROOT / "research/benchmark_audit.json")
    checks = []

    def check(name, actual, expected):
        checks.append({"name": name, "actual": actual, "expected": expected, "match": actual == expected})

    for path, expected in registry["baseline_files_sha256"].items():
        check(path, file_sha256(ROOT / path), expected)
    for path, expected in registry["production_source_sha256"].items():
        content = subprocess.check_output(["git", "show", f"{registry['production_commit']}:{path}"], cwd=ROOT)
        check(f"historical_git_source:{path}", hashlib.sha256(content).hexdigest(), expected)
    for path, expected in [
        ("data/benchmarking/test1/Test1_Full_rev.mp4", registry["original_video_sha256"]),
        ("Part2/dataset/Test1_Full/Test1_Full_rally.csv", registry["ground_truth_sha256"]),
        *[(record["path"], record["sha256"]) for record in registry["models_verified"].values()],
    ]:
        check(path, file_sha256(ROOT / path), expected)

    truth = read_csv(ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv", 30)
    experiment_checks = []
    for experiment in results["experiments"]:
        directory = ROOT / experiment["path"]
        predictions = read_csv(directory / "predicted_rallies.csv", 30)
        metrics, rows = evaluate(truth, predictions, 30)
        for source, expected in [("register", experiment["metrics"]), ("run", load(directory / "metrics.json"))]:
            check(f"experiment:{experiment['id']}:{source}", metrics, expected)
        experiment_checks.append({"id": experiment["id"], "rows": len(rows), "detection": metrics["detection"]})

    fresh = ROOT / "artifacts/benchmarking/experiments/fresh_image_exit_v1"
    check("fresh_runtime", load(fresh / "inference.json"), results["fresh_runtime"])
    check("fresh_validation", load(fresh / "post_run_validation.json"), results["fresh_post_run_validation"])
    check(
        "summary_generator",
        file_sha256(ROOT / "research/finalize_pipeline_investigation.py"),
        results["summary_generator_sha256"],
    )
    for case in results["fresh_post_run_validation"]["failure_case_index"]["cases"]:
        case_dir = fresh / "failure_cases" / case["case_id"]
        check(f"case:{case['case_id']}:manifest", file_sha256(case_dir / "case.json"), case["manifest_sha256"])
        for name in [
            "observations.msgpack",
            "events.jsonl",
            "fsm_trace.jsonl",
            "execution.log",
            "boundary_overlay.jpg",
        ]:
            check(f"case:{case['case_id']}:{name}", (case_dir / name).is_file(), True)
    for name, expected in original_audit["evidence_hashes"].items():
        check(f"benchmark_audit:{name}", file_sha256(ROOT / "outputs/benchmarking/test1" / name), expected)

    predictions = read_csv(fresh / "predicted_rallies.csv", 30)
    save_evaluation(output / "v1_evaluation", truth, predictions, 30)
    check(
        "v1_comparison_bytes",
        file_sha256(output / "v1_evaluation/rally_comparison.csv"),
        file_sha256(fresh / "rally_comparison.csv"),
    )
    report = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "executor_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "harness_sha256": file_sha256(Path(__file__)),
        "mode": "read-only evidence verification and CSV reevaluation; no model inference",
        "experiment_checks": experiment_checks,
        "checks": checks,
        "all_passed": all(record["match"] for record in checks),
    }
    (output / "validation.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"checks": len(checks), "all_passed": report["all_passed"]}))
    if not report["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
