"""Read-only ledger and unique-contact counterfactual audit; no physical labels.

The inputs are immutable recorded runs. This tool verifies a previously executed
intervention; it performs no perception, semantic replay, matching or inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def live(rows):
    superseded = {row["supersedes"] for row in rows if row.get("supersedes")}
    return [row for row in rows if row["event_id"] not in superseded and row["status"] != "retracted"]


def contact_signature(event):
    return {
        "confidence": event["confidence"],
        "xy": event["payload"].get("shuttle_xy"),
        "components": [row.get("scores") for row in event["evidence"] if row["kind"] == "component_scores"],
        "model": event["provenance"].get("model"),
        "racket_contact_observed": event["payload"].get("racket_contact_observed"),
        "attribution_reason": event["payload"].get("attribution_reason"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fresh", type=Path, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--negative", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    paths = [p.resolve() for p in (args.fresh, args.control, args.negative)]
    fresh, control, negative = paths
    event_rows = [read_rows(p / "events.jsonl") for p in paths]
    current = [live(rows) for rows in event_rows]
    control_trace, negative_trace = (read_rows(p / "fsm_trace.jsonl") for p in (control, negative))
    step_keys = ("frame", "visible", "speed", "replay", "x", "y", "interpolated", "evidence", "exit_proof")
    steps = [
        {r["frame"]: {k: r[k] for k in step_keys} for r in rows if r["call"] == "step"}
        for rows in (control_trace, negative_trace)
    ]
    step_differences = sorted(f for f in set(steps[0]) | set(steps[1]) if steps[0].get(f) != steps[1].get(f))
    contacts = [{r["frame_start"]: contact_signature(r) for r in rows if r["type"] == "contact"} for rows in current]
    removed = sorted(set(contacts[1]) - set(contacts[2]))
    added = sorted(set(contacts[2]) - set(contacts[1]))
    contact_differences = sorted(f for f in set(contacts[1]) & set(contacts[2]) if contacts[1][f] != contacts[2][f])
    calls = [[r["frame"] for r in rows if r["call"] == "contact"] for rows in (control_trace, negative_trace)]
    comparison = json.loads((negative / "comparison.json").read_text())
    old_rows, new_rows = comparison["baseline"]["per_gt"], comparison["experiment"]["per_gt"]
    changed_gt = [
        a["gt_rally"]
        for a, b in zip(old_rows, new_rows, strict=True)
        if (a["pred_start_frame"], a["pred_end_frame"], a["matching_status"])
        != (b["pred_start_frame"], b["pred_end_frame"], b["matching_status"])
    ]
    suppressed_meta = json.loads((negative / "suppression_metadata.json").read_text())
    replay_meta = json.loads((negative / "replay_metadata.json").read_text())
    parity = {
        "control_fresh_csv_exact": (fresh / "predicted_rallies.csv").read_bytes()
        == (control / "predicted_rallies.csv").read_bytes(),
        "control_fresh_live_contact_signatures_exact": contacts[0] == contacts[1],
        "control_selected_calls": len(calls[0]),
        "negative_selected_calls": len(calls[1]),
        "selected_call_removed": sorted(set(calls[0]) - set(calls[1])),
        "selected_call_added": sorted(set(calls[1]) - set(calls[0])),
        "all_remaining_selected_call_order_exact": [f for f in calls[0] if f != 12766] == calls[1],
        "live_contact_removed": removed,
        "live_contact_added": added,
        "common_live_contact_signature_differences": contact_differences,
        "processed_shuttle_steps": len(steps[0]),
        "processed_shuttle_step_differences": step_differences,
        "changed_gt_boundary_rows": changed_gt,
        "counterfactual_source_commit": replay_meta["git_commit"],
        "counterfactual_source_unchanged": replay_meta["source_unchanged"],
        "counterfactual_contact_source_sha256": replay_meta["source_sha256"][
            "sports/badminton/src/bai_badminton/events/contact.py"
        ],
    }
    assert parity["control_fresh_csv_exact"] and parity["control_fresh_live_contact_signatures_exact"]
    assert len(calls[0]) == len(calls[1]) + 1 and parity["all_remaining_selected_call_order_exact"]
    assert removed == [12766] and not added and not contact_differences and not step_differences
    assert len(steps[0]) == 17268 and changed_gt == [27] and replay_meta["source_unchanged"]
    ledger = {"raw_rows": len(event_rows[0]), "live_rows": len(current[0]), "types": {}}
    for kind in ("contact", "stroke", "shuttle_turn"):
        selected = [r for r in current[0] if r["type"] == kind]
        ledger["types"][kind] = {
            "live": len(selected),
            "lifecycle_statuses": dict(Counter(r["status"] for r in selected)),
            "confidence_bands": dict(Counter(r["band"] for r in selected)),
            "named_actor_count": sum(r["actors"]["player_id"] is not None for r in selected),
            "contact_statuses": dict(Counter(r["payload"].get("contact_status") for r in selected)),
        }
        if kind == "contact":
            ledger["types"][kind].update(
                {
                    "physical_racket_impact_observed": sum(
                        r["payload"].get("racket_contact_observed") is True for r in selected
                    ),
                    "geometric_racket_overlap": sum(
                        r["payload"].get("racket_overlap_observed") is True for r in selected
                    ),
                }
            )
        if kind == "stroke":
            ledger["types"][kind].update(
                {
                    "labels": dict(Counter(r["payload"].get("stroke") for r in selected)),
                    "classification_statuses": dict(
                        Counter(r["payload"].get("classification_status") for r in selected)
                    ),
                    "abstention_reasons": dict(
                        Counter(r["payload"].get("classification_abstention_reason") or "none" for r in selected)
                    ),
                }
            )
    result = {
        "schema": "badminton-contact-ledger-audit:v1",
        "mode": "read-only recorded-output audit; no inference, labels or automatic physical accuracy claim",
        "paths": {"fresh": str(fresh), "control": str(control), "negative": str(negative)},
        "parity": parity,
        "ledger": ledger,
        "gt27": {
            "old": old_rows[26],
            "negative": new_rows[26],
            "removed_candidate": suppressed_meta["removed_candidates"][0],
        },
        "detection": comparison["experiment"]["metrics"]["detection"],
        "limits": [
            "Manual removal is a causal negative control, never a production rule",
            "No independently reviewed contact, hitter or shot labels",
            "Lifecycle confirmed does not mean physically confirmed",
        ],
    }
    (args.output / "audit.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    inputs = [p / name for p in paths for name in ("events.jsonl", "predicted_rallies.csv")]
    inputs += [
        control / "fsm_trace.jsonl",
        negative / "fsm_trace.jsonl",
        negative / "replay_metadata.json",
        negative / "suppression_metadata.json",
        negative / "comparison.json",
    ]
    manifest = {
        "executor_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "script_sha256": digest(Path(__file__)),
        "input_sha256": {str(p): digest(p) for p in inputs},
        "result_sha256": digest(args.output / "audit.json"),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(parity, indent=2), flush=True)


if __name__ == "__main__":
    main()
