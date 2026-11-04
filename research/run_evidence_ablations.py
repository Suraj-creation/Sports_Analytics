"""Factorial fixed-input evidence ablations; labels are evaluation only."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.events.rally_evidence import EvidenceRallyFSM, ObservationKind, RallyObservation  # noqa: E402
from bai_badminton.events.rally_fsm import RallyParams  # noqa: E402
from research.compare_rally_experiments import compare_experiment  # noqa: E402
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
    assert metadata["source_unchanged"]
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
        provider = EvidenceRallyFSM(RallyParams(fps=30), **options)
        intervals, transitions = [], []
        for row in rows:
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
            else:
                update = provider.flush(frame)
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
            if call == "flush" and frame == 119:
                provider = EvidenceRallyFSM(RallyParams(fps=30), **options)
        intervals.sort()
        write_predictions(output / "predicted_rallies.csv", intervals, 30)
        if (name == "combined" and not args.include_exit) or (name == "exit_reconstruction" and args.include_exit):
            reference = read_csv(source / "predicted_rallies.csv", 30)
            assert intervals == [(r.start_frame, r.end_frame) for r in reference]
        dump(output / "state_transitions.json", transitions)
        dump(
            output / "benchmark_metadata.json",
            {
                **metadata,
                "mode": "fixed recorded evidence factorial ablation; NOT fresh inference",
                "intervention": name,
                "configuration": options,
                "parameters": asdict(RallyParams(fps=30)),
                "input_trace_sha256": digest(source / "fsm_trace.jsonl"),
                "source_video_sha256": metadata["video_sha256"],
                "exploratory": True,
                "prediction_sha256": digest(output / "predicted_rallies.csv"),
            },
        )
        labels = read_csv(ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv", 30)
        metrics = save_evaluation(output, labels, read_csv(output / "predicted_rallies.csv", 30), 30)
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
