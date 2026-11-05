"""Unchanged offline reference scoring AFTER a dynamic cached replay is durable."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_engine.schema.events import Event, current_view  # noqa: E402
from research.production_external_reference_report import (  # noqa: E402
    digest,
    extract_predictions,
    load_helper,
    project_d9,
    read,
    require,
    write_new,
)


def score(replay, reference, output):
    metadata = read(replay / "replay_manifest.json")
    require(
        metadata["schema"] in {"cached-external-semantic:v1", "cached-external-semantic:v2"},
        "durable declared replay required",
    )
    if metadata["schema"] == "cached-external-semantic:v2":
        hashes = metadata.get("harness_source_sha256")
        require(bool(hashes), "v2 replay must retain exact runner/helper identity")
        for name, expected in hashes.items():
            require(digest(replay / "executed_helpers" / name) == expected, "captured replay helper digest mismatch")
    require(metadata.get("no_GT_or_neural_model_input") is True, "label-free replay required")
    source_report = Path(
        metadata.get(
            "source_report_path", str(Path(metadata["source_run"]) / "results" / metadata["session_id"] / "report.json")
        )
    )
    require(digest(source_report) == metadata["source_report_sha256"], "fresh-source binding changed")
    labels = read(reference / "full_clip_reference.json")
    frozen = read(reference / "report.json")
    require(labels["session_id"] == metadata["session_id"] == frozen["session_id"], "reference session mismatch")
    require(frozen["inference_provenance"]["report"] == read(source_report), "reference from another fresh run")
    require(metadata["frames"] == labels["media_n_frames"], "partial replay cannot be scored")
    all_events = [Event.model_validate_json(s) for s in (replay / "events.jsonl").read_text().splitlines() if s]
    live = current_view(all_events)
    exported = [Event.model_validate_json(s) for s in (replay / "current-events.jsonl").read_text().splitlines() if s]
    require(
        [e.model_dump(mode="json") for e in live] == [e.model_dump(mode="json") for e in exported],
        "replay fold mismatch",
    )
    require(len({e.event_id for e in all_events}) == len(all_events), "duplicate event identities")
    helper = load_helper()
    machine = extract_predictions(live, {e.event_id: e for e in all_events}, labels, helper._root_event_id)
    results = {"native12": [helper.timing_metrics(labels, machine, tol) for tol in (3, 6)]}
    machines = {"native12": machine}
    if frozen["recording"] == "doubles":
        projected = project_d9(machine, frozen["taxonomy_protocol"])
        machines["D9"] = projected
        results["D9"] = [helper.timing_metrics(labels, projected, tol) for tol in (3, 6)]
    inventories = {}
    for name, metrics in results.items():
        inventories[name] = []
        for metric in metrics:
            truth_ids = {row["annotation_id"] for row in metric["matches"]}
            pred_ids = {row["contact_event_id"] for row in metric["matches"]}
            inventories[name].append(
                {
                    "tolerance_frames": metric["tolerance_frames"],
                    "matches": metric["matches"],
                    "missed_anchors": [row for row in labels["shots"] if row["annotation_id"] not in truth_ids],
                    "unmatched_live_contacts": [
                        row for row in machines[name]["shots"] if row["event_id"] not in pred_ids
                    ],
                }
            )
    files = [
        replay / "replay_manifest.json",
        replay / "events.jsonl",
        replay / "current-events.jsonl",
        replay / "emission_frontiers.json",
        reference / "report.json",
        reference / "full_clip_reference.json",
        Path(__file__),
        ROOT / "research/production_external_reference_report.py",
        ROOT / "research/shot_benchmark.py",
    ]
    hashes = {str(path): digest(path) for path in files}
    require(not output.exists(), "new output directory required")
    output.mkdir(parents=True)
    write_new(output / "predictions.json", machines)
    write_new(output / "matching_inventory.json", inventories)
    result = {
        "schema": "cached-external-reference-agreement:v1",
        "mode": "offline published-anchor agreement; NOT fresh inference",
        "accuracy_claim_eligible": False,
        "recording": frozen["recording"],
        "replay": metadata,
        "metrics": results,
        "fresh_metrics_native12": frozen["metrics_native12_strict"],
        "input_sha256": hashes,
    }
    write_new(output / "report.json", result)
    (output / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    for path, expected in hashes.items():
        require(digest(path) == expected, "input changed during offline evaluation")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--replay", required=True, type=Path)
    p.add_argument("--reference-package", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    result = score(a.replay.resolve(strict=True), a.reference_package.resolve(strict=True), a.output.resolve())
    print(
        json.dumps(
            {
                name: [
                    {
                        "tolerance": m["tolerance_frames"],
                        "contact": m["contact_detection"],
                        "class_correct": m["matched_known_class"]["correct"],
                        "class_support": m["matched_known_class"]["support"],
                        "unknown_fraction": m["classification"]["unknown_prediction_fraction"],
                    }
                    for m in metrics
                ]
                for name, metrics in result["metrics"].items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
