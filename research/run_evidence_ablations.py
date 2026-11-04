"""Factorial fixed-input evidence ablations; labels are evaluation only."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.events.rally_evidence import EvidenceRallyFSM, ObservationKind, RallyObservation  # noqa: E402
from bai_badminton.events.rally_fsm import RallyParams  # noqa: E402
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
    parser.add_argument(
        "--source", type=Path, default=ROOT / "artifacts/benchmarking/experiments/evidence_feature_replay_v1"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/benchmarking/experiments/evidence_ablations")
    parser.add_argument("--include-exit", action="store_true")
    args = parser.parse_args()
    source = args.source.resolve()
    baseline = ROOT / "outputs/benchmarking/test1"
    parent = args.output.resolve()
    parent.mkdir(parents=True, exist_ok=False)
    rows = [json.loads(line) for line in (source / "fsm_trace.jsonl").open()]
    metadata = json.loads((source / "replay_metadata.json").read_text())
    if not metadata["source_unchanged"]:
        raise ValueError("input trace was generated while its source changed")
    if digest(source / "fsm_trace.jsonl") != metadata["trace_sha256"]:
        raise ValueError("input trace does not match its generator metadata")
    source_events = [json.loads(line) for line in (source / "events.jsonl").open()]
    resets = trace_epoch_reset_indices(rows, format_events=source_events)
    fps = float(metadata["parameters"]["fps"])
    executor = snapshot_executor(
        ROOT,
        parent,
        [
            Path(__file__),
            ROOT / "research/next_evidence_provenance.py",
            ROOT / "research/compare_rally_experiments.py",
            ROOT / "scripts/benchmarking/production_inference.py",
            ROOT / "scripts/benchmarking/evaluate_rallies.py",
            ROOT / "sports/badminton/src/bai_badminton/events/rally_fsm.py",
            ROOT / "sports/badminton/src/bai_badminton/events/rally_evidence.py",
        ],
        Path(__file__),
    )
    dump(parent / "executor_metadata.json", executor)
    summary = []
    matrix = [
        ("disabled", False, False, False),
        ("reconstruction_only", True, False, False),
        ("motion_only", False, True, False),
        ("combined", True, True, False),
    ]
    if args.include_exit:
        matrix += [
            ("exit_only", False, False, True),
            ("exit_reconstruction", True, False, True),
            ("exit_motion", False, True, True),
            ("all_signals", True, True, True),
        ]
    for name, reconstruction, motion, exit_recovery in matrix:
        output = parent / name
        output.mkdir()
        options = {"use_reconstruction": reconstruction, "motion_guard": motion, "use_exit_recovery": exit_recovery}
        provider = EvidenceRallyFSM(RallyParams(fps=fps), **options)
        intervals, transitions = [], []
        started = time.perf_counter()
        for row_index, row in enumerate(rows):
            frame, call = row["frame"], row["call"]
            before = provider.state.value
            if call == "step":
                evidence = dict(row["evidence"])
                evidence["kind"] = ObservationKind(evidence["kind"])
                update = provider.step_evidence(RallyObservation(**evidence))
            elif call == "contact":
                update = provider.on_contact(frame)
            elif call == "discontinuity":
                update = provider.on_discontinuity(frame)
            elif call == "flush":
                update = provider.flush(frame)
            else:
                raise ValueError(f"unsupported recorded call: {call}")
            if update.finalized:
                intervals.append((update.finalized.start, update.finalized.end))
            if before != provider.state.value or update.finalized or update.started is not None:
                transitions.append(
                    {
                        "frame": frame,
                        "call": call,
                        "before": before,
                        "after": provider.state.value,
                        "update": asdict(update),
                    }
                )
            if row_index in resets:
                provider = EvidenceRallyFSM(RallyParams(fps=fps), **options)
        intervals.sort()
        elapsed = time.perf_counter() - started
        if not executor_sources_unchanged(ROOT, executor):
            raise RuntimeError("executor source changed during fixed-input experiment")
        write_predictions(output / "predicted_rallies.csv", intervals, fps)
        if (name == "combined" and not args.include_exit) or (name == "exit_reconstruction" and args.include_exit):
            reference = read_csv(source / "predicted_rallies.csv", fps)
            assert intervals == [(r.start_frame, r.end_frame) for r in reference]
        dump(output / "state_transitions.json", transitions)
        dump(
            output / "benchmark_metadata.json",
            {
                "mode": "fixed recorded evidence factorial ablation; NOT fresh inference",
                "executor": executor,
                "executor_source_unchanged": True,
                "git_commit": executor["git_commit"],
                "source_sha256": executor["source_sha256"],
                "source_unchanged": True,
                "trace_generator": metadata,
                "trace_generator_metadata_sha256": digest(source / "replay_metadata.json"),
                "trace_epoch_reset_frames": [rows[index]["frame"] for index in sorted(resets)],
                "trace_epoch_reset_basis": "recorded format_decision events aligned to nonterminal trace flushes",
                "input_events_sha256": digest(source / "events.jsonl"),
                "intervention": name,
                "configuration": options,
                "overrides": options,
                "source_replay_overrides": metadata["overrides"],
                "source_replay_elapsed_seconds": metadata["elapsed_seconds"],
                "elapsed_seconds": elapsed,
                "timing_scope": "FSM transition loop only, shared decoded input trace loading and evaluation excluded",
                "parameters": asdict(RallyParams(fps=fps)),
                "input_trace_sha256": digest(source / "fsm_trace.jsonl"),
                "source_video_sha256": metadata["video_sha256"],
                "ground_truth_sha256": metadata["ground_truth_sha256"],
                "ground_truth_usage": "evaluation only; no labels provided to the FSM",
                "exploratory": True,
                "prediction_sha256": digest(output / "predicted_rallies.csv"),
            },
        )
        (output / "execution.log").write_text(
            f"Fixed-input FSM ablation {name}\nConfiguration: {json.dumps(options)}\n"
            f"Input trace: {source / 'fsm_trace.jsonl'}\nFSM loop elapsed_seconds: {elapsed}\n"
            "No fresh video/model inference. Annotation values are read only after prediction CSV export.\n"
        )
        labels = read_csv(ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv", fps)
        metrics = save_evaluation(output, labels, read_csv(output / "predicted_rallies.csv", fps), fps)
        compare_experiment(output, baseline)
        entry = {
            "experiment": name,
            **metrics["detection"],
            "start_mae": metrics["boundary_and_duration_errors"]["start_frame"]["mae"],
            "end_mae": metrics["boundary_and_duration_errors"]["end_frame"]["mae"],
            "start_max": metrics["boundary_and_duration_errors"]["start_frame"]["max_absolute_error"],
            "end_max": metrics["boundary_and_duration_errors"]["end_frame"]["max_absolute_error"],
            "mean_iou": metrics["overlap"]["mean_iou"],
        }
        summary.append(entry)
        print(json.dumps(entry), flush=True)
    dump(parent / "summary.json", summary)


if __name__ == "__main__":
    main()
