"""Controlled real-input production-FSM ablations; not fresh perception inference."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallyState  # noqa: E402
from research.compare_rally_experiments import compare_experiment  # noqa: E402
from research.next_evidence_provenance import (  # noqa: E402
    executor_sources_unchanged,
    snapshot_executor,
    trace_epoch_reset_indices,
)
from scripts.benchmarking.evaluate_rallies import read_csv, save_evaluation, write_predictions  # noqa: E402
from scripts.benchmarking.production_inference import digest, dump  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/benchmarking/experiments/fsm_correctness")
    args = parser.parse_args()
    baseline = ROOT / "outputs/benchmarking/test1"
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=False)
    frozen_source = subprocess.check_output(
        [
            "git",
            "show",
            "301baf08be5e989dd0ed93cb885733c3cf6f356a:sports/badminton/src/bai_badminton/events/rally_fsm.py",
        ],
        cwd=ROOT,
    )
    path = root / "frozen_fsm.py"
    path.write_bytes(frozen_source)
    spec = importlib.util.spec_from_file_location("frozen_fsm_ablation", path)
    frozen = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = frozen
    spec.loader.exec_module(frozen)
    # Only unify Enum identity for methods borrowed from the pinned baseline.
    # Default parameters/algorithm stay byte-pinned and the control must reproduce.
    frozen.RallyState = RallyState
    original_step, original_contact = frozen.RallyFSM.step, frozen.RallyFSM.on_contact
    rows = [
        json.loads(line)
        for line in (ROOT / "artifacts/benchmarking/investigation/baseline_semantic_replay/fsm_trace.jsonl").open()
    ]
    trace_metadata_path = ROOT / "artifacts/benchmarking/investigation/baseline_semantic_replay/replay_metadata.json"
    trace_metadata = json.loads(trace_metadata_path.read_text())
    input_trace = ROOT / "artifacts/benchmarking/investigation/baseline_semantic_replay/fsm_trace.jsonl"
    if digest(input_trace) != trace_metadata["trace_sha256"]:
        raise ValueError("input trace does not match its generator metadata")
    source_metadata = json.loads((baseline / "benchmark_metadata.json").read_text())
    input_events = input_trace.parent / "events.jsonl"
    resets = trace_epoch_reset_indices(rows, format_events=[json.loads(line) for line in input_events.open()])
    fps = float(source_metadata["video_fps"])
    executor = snapshot_executor(
        ROOT,
        root,
        [
            Path(__file__),
            ROOT / "research/next_evidence_provenance.py",
            ROOT / "research/compare_rally_experiments.py",
            ROOT / "scripts/benchmarking/production_inference.py",
            ROOT / "scripts/benchmarking/evaluate_rallies.py",
            ROOT / "sports/badminton/src/bai_badminton/events/rally_fsm.py",
        ],
        Path(__file__),
    )
    dump(root / "executor_metadata.json", executor)
    truth = None  # Label values are loaded only after each prediction is written.
    matrix = [
        ("control", original_step, original_contact),
        ("contact_history_only", original_step, RallyFSM.on_contact),
        ("motion_onset_clock_only", RallyFSM.step, original_contact),
        ("combined", RallyFSM.step, RallyFSM.on_contact),
    ]
    results = []
    reference = sorted(
        (r["start"], r["end"]) for r in json.loads((baseline / "inference.json").read_text())["rally_events"]
    )
    for name, step, contact in matrix:
        output = root / name
        output.mkdir()
        provider = type(f"Ablation_{name}", (RallyFSM,), {"step": step, "on_contact": contact})
        fsm = provider(RallyParams(fps=fps))
        intervals = []
        transitions = []
        before_time = time.perf_counter()
        for row_index, row in enumerate(rows):
            frame = row["frame"]
            method = row["call"]
            before = fsm.state.value
            if method == "step":
                result = fsm.step(
                    frame, row["visible"], row["speed"] if row["speed"] is not None else math.nan, row["replay"]
                )
            elif method == "contact":
                result = fsm.on_contact(frame)
            elif method == "discontinuity":
                result = fsm.on_discontinuity(frame)
            elif method == "flush":
                result = fsm.flush(frame)
            else:
                raise ValueError(f"unsupported recorded call: {method}")
            if result.finalized:
                intervals.append((result.finalized.start, result.finalized.end))
            if before != fsm.state.value or result.finalized or result.started is not None:
                transitions.append(
                    {
                        "frame": frame,
                        "call": method,
                        "before": before,
                        "after": fsm.state.value,
                        "update": asdict(result),
                    }
                )
            if row_index in resets:
                fsm = provider(RallyParams(fps=fps))
        elapsed = time.perf_counter() - before_time
        intervals.sort()
        if name == "control" and intervals != reference:
            raise RuntimeError("frozen fixed-input control does not reproduce all49intervals")
        if not executor_sources_unchanged(ROOT, executor):
            raise RuntimeError("executor source changed during fixed-input experiment")
        write_predictions(output / "predicted_rallies.csv", intervals, fps)
        dump(output / "state_transitions.json", transitions)
        dump(
            output / "benchmark_metadata.json",
            {
                "mode": "fixed recorded production FSM input ablation; NOT fresh model inference",
                "intervention": name,
                "parameters": asdict(RallyParams(fps=fps)),
                "git_commit_sha": executor["git_commit"],
                "executor": executor,
                "executor_source_unchanged": True,
                "trace_generator": trace_metadata,
                "trace_generator_metadata_sha256": digest(trace_metadata_path),
                "trace_epoch_reset_frames": [rows[index]["frame"] for index in sorted(resets)],
                "trace_epoch_reset_basis": "recorded format_decision events aligned to nonterminal trace flushes",
                "input_events_sha256": digest(input_events),
                "video_sha256": source_metadata["source_video_sha256"],
                "source_video_sha256": source_metadata["source_video_sha256"],
                "ground_truth_sha256": source_metadata["ground_truth_sha256"],
                "ground_truth_usage": "evaluation only; no labels provided to the FSM",
                "baseline_source_sha256": digest(path),
                "current_source_sha256": digest(ROOT / "sports/badminton/src/bai_badminton/events/rally_fsm.py"),
                "input_trace_sha256": digest(
                    ROOT / "artifacts/benchmarking/investigation/baseline_semantic_replay/fsm_trace.jsonl"
                ),
                "checkpoints": source_metadata["models"],
                "runtime_versions": source_metadata["runtime_dependencies"],
                "device": "CPU semantic replay of recorded CUDA FP16 perception",
                "exploratory": True,
                "elapsed_seconds": elapsed,
                "timing_scope": "FSM transition loop only, shared decoded input trace loading and evaluation excluded",
            },
        )
        if truth is None:
            truth = read_csv(ROOT / source_metadata["ground_truth_path"], fps)
        pred = read_csv(output / "predicted_rallies.csv", fps)
        metrics = save_evaluation(output, truth, pred, fps)
        compare_experiment(output, baseline)
        result = {
            "experiment": name,
            **metrics["detection"],
            "start_mae": metrics["boundary_and_duration_errors"]["start_frame"]["mae"],
            "end_mae": metrics["boundary_and_duration_errors"]["end_frame"]["mae"],
            "mean_iou": metrics["overlap"]["mean_iou"],
        }
        results.append(result)
        print(json.dumps(result), flush=True)
    dump(root / "summary.json", results)


if __name__ == "__main__":
    main()
