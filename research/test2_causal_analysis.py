"""Offline recorded-gate summaries of completed fresh inference and exact replay.

These are diagnostic mechanisms, never adjudicated physical errors. Annotation
intervals group completed evidence only; no model or temporal parameter changes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def dump(path: Path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def intervals(frames: list[int]) -> list[list[int]]:
    """Compress sorted distinct frame IDs as half-open intervals."""
    if frames != sorted(set(frames)):
        raise ValueError("ordered unique frame IDs required")
    result = []
    for frame in frames:
        if result and frame == result[-1][1]:
            result[-1][1] += 1
        else:
            result.append([frame, frame + 1])
    return result


def finite_point(value) -> bool:
    return isinstance(value, (list, tuple)) and len(value) == 2 and all(
        type(v) in (int, float) and math.isfinite(v) for v in value
    )


def gate_status(raw: dict, step: dict) -> list[str]:
    """Describe stored gates, without treating any model coordinate as correct."""
    observation = step["observation"]
    association = raw.get("sa") or {}
    diagnostic = (raw.get("dg") or {}).get("shuttle") or {}
    flags = []
    if raw.get("r") or raw.get("v") != "main":
        flags.append("scene_excluded")
    if raw.get("l") or raw.get("cs") not in (None, "VALID"):
        flags.append("geometry_unavailable_or_reacquiring")
    if diagnostic.get("reason") == "mask_rejected":
        flags.append("recorded_heatmap_mask_rejection")
    if diagnostic.get("reason") == "below_threshold":
        flags.append("recorded_heatmap_below_threshold")
    if any(candidate.get("above_inference_threshold") and not candidate.get("mask_allows_peak")
           for candidate in association.get("candidates", [])):
        flags.append("above_threshold_heatmap_competitor_outside_mask")
    if not finite_point(raw.get("s")):
        flags.append("raw_provider_coordinate_absent")
    if association.get("status") in {"ambiguous", "invalid"}:
        flags.append("association_withheld")
    if observation.get("context_valid") is False:
        flags.append("temporal_context_invalid")
    if finite_point(association.get("selected_xy")) and observation["kind"] != "observed":
        flags.append("selected_coordinate_not_processed_as_observed")
    if observation["kind"] == "reconstructed":
        flags.append("processed_reconstruction")
    if observation["kind"] == "observed" and observation.get("speed") is None:
        flags.append("observed_adjacent_speed_unavailable")
    return flags


def recorded_window(lo: int, hi: int, steps: dict, raw: dict, start_speed: float = 3.0) -> dict:
    groups, kinds, reasons, participants = {}, Counter(), Counter(), Counter()
    firsts = {key: None for key in ["raw_provider_coordinate", "association_selected", "processed_observed",
                                  "measured_movement_above_start_gate", "aligned_player_motion"]}
    diagnostic_count = 0
    earliest = None
    for frame in range(lo, hi):
        item, step = raw[frame], steps[frame]
        observation = step["observation"]
        kinds[observation["kind"]] += 1
        association = item.get("sa") or {}
        people = item.get("p", [])
        participants.update({
            "frames_without_player_tracks": not people,
            "frames_detector_ran": bool(item.get("do")),
            "person_observations": len(people),
            "detector_matched_persons": sum(bool(person.get("dm")) for person in people),
            "current_pose_persons": sum(person.get("k") is not None and person.get("pf") == frame
                                        for person in people),
            "current_racket_persons": sum(person.get("rk") is not None and person.get("rf") == frame
                                          for person in people),
        })
        reasons.update(association.get("reasons", []))
        diagnostic_count += bool((item.get("dg") or {}).get("shuttle"))
        flags = gate_status(item, step)
        for flag in flags:
            groups.setdefault(flag, []).append(frame)
        if flags and earliest is None:
            earliest = {"frame": frame, "recorded_gate_patterns": flags,
                        "association_reasons": association.get("reasons", []),
                        "scope": "first machine limitation in reference-grouped window; physical relevance unreviewed"}
        facts = {
            "raw_provider_coordinate": finite_point(item.get("s")),
            "association_selected": finite_point(association.get("selected_xy")),
            "processed_observed": observation["kind"] == "observed",
            "measured_movement_above_start_gate": observation["kind"] == "observed"
            and observation.get("speed") is not None and observation["speed"] > start_speed,
            "aligned_player_motion": observation.get("player_motion") is True,
        }
        for key, supported in facts.items():
            if supported and firsts[key] is None:
                firsts[key] = frame
    runs = {key: intervals(values) for key, values in groups.items()}
    return {
        "window_half_open": [lo, hi], "firsts": firsts, "observation_kind_counts": dict(kinds),
        "association_reason_counts": dict(reasons), "detailed_heatmap_diagnostic_frames": diagnostic_count,
        "participant_evidence_coverage": dict(participants),
        "earliest_recorded_gate_limitation": earliest,
        "gate_patterns": {key: {"frames": len(groups[key]), "runs_half_open": ranges,
                                "longest_run_frames": max(end - start for start, end in ranges)}
                          for key, ranges in runs.items()},
        "interpretation": "Machine evidence coverage and gating only; absence does not prove an actual missed shuttle.",
    }


def transition_summary(rows: list[dict], minimum_frames: int) -> dict:
    starts, cancellations, proposals, finals, resumes, barriers = [], [], [], [], [], []
    for row in rows:
        frame, update = row["frame"], row["update"]
        before, after = row["before"], row["after"]
        identity = {"frame": frame, "call": row["call"], "available_through": row["available_through"]}
        if update.get("started") is not None:
            starts.append({**identity, "start": update["started"],
                           "admission": "accepted_contact_candidate" if row["call"] == "on_contact"
                           else "consecutive_observed_motion"})
        if update.get("cancelled_start") is not None:
            closed = before.get("closed") or after.get("closed")
            duration = closed["end"] - closed["start"] + 1 if closed else None
            mechanism = "discontinuity_before_mature_exchange" if row["call"] == "on_discontinuity" else "unresolved"
            if closed and closed["start"] == update["cancelled_start"] and duration < minimum_frames:
                mechanism = "candidate_below_minimum_duration"
            cancellations.append({**identity, "start": update["cancelled_start"], "closed_candidate": closed,
                                  "candidate_length_under_fsm_contract": duration, "minimum_frames": minimum_frames,
                                  "recorded_mechanism": mechanism})
        if after.get("tentative_end") is not None and after.get("tentative_end") != before.get("tentative_end"):
            proposals.append({**identity, "proposed_end": after["tentative_end"], "reason": after["end_reason"],
                              "invisible_run": after.get("invisible_run"), "observation": row.get("observation")})
        if update.get("finalized"):
            finals.append({**identity, **update["finalized"]})
        if before["state"] in {"ending", "closed"} and after["state"] == "in_play":
            resumes.append({**identity, "prior_state": before["state"], "start": after.get("start"),
                            "observation": row.get("observation")})
        if row["call"] == "on_discontinuity":
            barriers.append({**identity, "prior_state": before["state"], "prior_start": before.get("start")})
    def logical_updates(values, keys):
        # step_evidence can call the instrumented on_discontinuity internally.
        # Its returned update is visible in both wrappers, but is one FSM update.
        unique = {}
        for value in values:
            identity = tuple(value[key] for key in keys)
            if identity not in unique:
                unique[identity] = {**value, "recorded_wrapper_calls": [value["call"]]}
            else:
                unique[identity]["recorded_wrapper_calls"].append(value["call"])
        return list(unique.values())

    return {
        "starts": starts,
        "cancelled_candidates": logical_updates(cancellations, ["frame", "start"]),
        "terminal_proposals": proposals,
        "finalized_intervals": logical_updates(finals, ["frame", "start", "end", "reason"]),
        "reopened_candidates": resumes, "discontinuity_calls": barriers,
    }


def summarize_case(
    case: dict, steps: dict, raw: dict, traces: list[dict], events: list[dict], minimum_frames: int,
    start_speed: float = 3.0,
) -> dict:
    n = len(steps)
    if case.get("gt_start_frame") is not None:
        start, end = case["gt_start_frame"], case["gt_end_frame"]
    else:
        start, end = case["start_frame"], case["end_frame"]
    if not 0 <= start < end <= n:
        raise ValueError("case interval is outside complete canonical frame coverage")
    pred_start, pred_end = case.get("pred_start_frame"), case.get("pred_end_frame")
    lo, hi = max(0, min(start, pred_start if pred_start is not None else start) - 60), min(
        n, max(end, pred_end if pred_end is not None else end) + 60)
    subset = [row for row in traces if lo <= row["frame"] < hi]
    transitions = transition_summary(subset, minimum_frames)
    selected_events = [event for event in events if lo <= event["frame_start"] < hi]
    contacts = [{"frame": event["frame_start"], "event_id": event["event_id"],
                 "physical_event_status": event["payload"].get("physical_event_status", "unknown"),
                 "physical_evidence": event["payload"].get("physical_evidence"),
                 "attribution_reason": event["payload"].get("attribution_reason"),
                 "contact_status": event["payload"].get("contact_status")}
                for event in selected_events if event["type"] == "contact"]
    content = [{"frame": f, "content_epoch": raw[f].get("ce"), "content_evidence": raw[f].get("cc")}
               for f in range(lo, hi) if raw[f].get("cc")]
    reference = recorded_window(start, end, steps, raw, start_speed)
    onset_end = min(end, start + 120)
    onset = recorded_window(max(0, start - 60), onset_end, steps, raw, start_speed)
    terminal = None
    if pred_start is not None or case.get("matching_status") == "unmatched_prediction":
        ps, pe = (pred_start, pred_end) if pred_start is not None else (start, end)
        finalized = [row for row in transitions["finalized_intervals"] if row["start"] == ps and row["end"] == pe]
        if len(finalized) != 1:
            raise ValueError("prediction must bind exactly one finalized interval in its own semantic trace")
        terminal = {
            "prediction_interval_half_open_under_benchmark_contract": [ps, pe],
            "finalization": finalized[0],
            "surviving_start_calls": [row for row in transitions["starts"] if row["start"] == ps],
            "matching_terminal_proposals": [row for row in transitions["terminal_proposals"]
                                            if row["proposed_end"] == pe and row["frame"] <= finalized[0]["frame"]],
            "endpoint_evidence": recorded_window(max(0, pe - 15), min(n, pe + 31), steps, raw, start_speed),
        }
    mechanisms = []
    if transitions["cancelled_candidates"]:
        mechanisms.append("provisional_candidate_cancellation")
    for flag in ["scene_excluded", "geometry_unavailable_or_reacquiring", "recorded_heatmap_mask_rejection",
                 "recorded_heatmap_below_threshold", "association_withheld",
                 "selected_coordinate_not_processed_as_observed"]:
        if reference["gate_patterns"].get(flag):
            mechanisms.append(flag)
    for reason in sorted({item["reason"] for item in transitions["finalized_intervals"]}):
        mechanisms.append("recorded_termination_" + reason)
    return {
        "case_id": case["case_id"], "evaluation": case, "context_half_open": [lo, hi],
        "reference_interval_half_open": [start, end], "reference_interval_diagnostics": reference,
        "onset_context_diagnostics": onset, "temporal_transitions": transitions,
        "matched_or_unmatched_prediction_terminal": terminal,
        "contact_candidates": contacts,
        "contact_rejection_events": [{"frame": event["frame_start"], "type": event["type"],
                                      "event_id": event["event_id"], "payload": event["payload"]}
                                     for event in selected_events if event["type"] == "shuttle_turn"],
        "content_change_evidence": content,
        "machine_mechanism_tags": mechanisms,
        "physical_failure_classification": "unresolved_pending_source_and_independent_reference_review",
        "software_defect_established": False,
        "review_requirements": ["Verify actual serve/terminal frame and legacy annotation convention in source pixels",
                                "Check selected versus competing shuttle peaks against visible shuttle",
                                "Distinguish model limitation, reference ambiguity and software defect using controls"],
        "missing_evidence": [
            "Detailed heatmap/player diagnostics are limited to the prespecified 3600 frames",
            "Rejected same-actor alternation candidates lack individual emitted rejection events",
            "Rally labels do not adjudicate shuttle, contact, pose, racket or identity accuracy",
        ],
    }


def verify_comparison(comparisons: list[dict], supplemental: dict, prediction_path: Path, fps: float) -> None:
    """Independently bind CSV rows to unchanged evaluation on the original bytes."""
    from scripts.benchmarking.evaluate_rallies import evaluate, read_csv

    references = [Path(path) for path in supplemental["provenance"]
                  if Path(path).suffix == ".csv" and Path(path).resolve() != prediction_path.resolve()]
    if len(references) != 1:
        raise ValueError("one exact original ground-truth CSV in completed evaluation provenance required")
    metrics, expected = evaluate(read_csv(references[0], fps), read_csv(prediction_path, fps), fps)
    serialized = [{key: "" if value is None else str(value) for key, value in row.items()} for row in expected]
    if comparisons != serialized or supplemental["metrics"] != metrics:
        raise ValueError("per-rally comparison or metrics differ from unchanged evaluation of their bound inputs")


def analyse(run: Path, replay: Path, evaluation: Path, output: Path) -> dict:
    import msgpack

    from bai_badminton.events.rally_fsm import RallyParams
    from research.production_contact_result_audit import fold_events
    from research.production_external_semantic_replay import load_finished_input, verify_replay_output_artifacts
    from research.test2_failure_package import verify_replay

    session = read(run / "session.json")
    bound = load_finished_input(run, session["session_id"])
    trace_path, proof_path = replay / "bounded_fsm_trace.jsonl", replay / "replay_manifest.json"
    proof = read(proof_path)
    traces = [json.loads(line) for line in trace_path.open() if line.strip()]
    verify_replay(proof, bound, trace_path, traces, session["session_id"])
    verify_replay_output_artifacts(replay, proof)
    policy_path = ROOT / "sports/badminton/src/bai_badminton/events/rally_fsm.py"
    if sha(policy_path) != proof["executed_source_sha256"].get(str(policy_path.relative_to(ROOT))):
        raise ValueError("current rally policy differs from actual parity-verified replay")
    # Annotation-derived rows are read only after genuine completed-run guards.
    supplemental_path = evaluation / "supplemental_metrics.json"
    supplemental = read(supplemental_path)
    for path, expected in supplemental["provenance"].items():
        if sha(Path(path)) != expected:
            raise ValueError("completed evaluation input changed")
    for path in [run / "predicted_rallies.csv", bound.report_path]:
        if supplemental["provenance"].get(str(path.resolve())) != sha(path):
            raise ValueError("evaluation is not bound to the completed fresh run")
    raw, steps = {}, {row["frame"]: row for row in traces if row["call"] == "step"}
    for path in sorted(bound.cache_directory.glob("*.msgpack")):
        if sha(path) != bound.expected_caches[path.name]:
            raise ValueError("fresh source cache changed")
        for row in msgpack.unpackb(path.read_bytes(), raw=False)["frames"]:
            if row["f"] != len(raw):
                raise ValueError("cache frame population is not ordered complete coverage")
            raw[row["f"]] = row
    if list(raw) != list(range(bound.media["n_frames"])):
        raise ValueError("complete source cache frame population required")
    _, events, _ = fold_events([json.loads(line) for line in bound.events_path.open() if line.strip()])
    with (evaluation / "per_rally_comparison.csv").open(newline="") as stream:
        comparisons = list(csv.DictReader(stream))
    verify_comparison(comparisons, supplemental, run / "predicted_rallies.csv",
                      bound.media["fps_num"] / bound.media["fps_den"])
    cases = []
    significant = {case["case_id"] for case in supplemental["failure_cases"]}
    for row in comparisons:
        converted = dict(row)
        for name in ["gt_rally", "pred_rally", "gt_start_frame", "gt_end_frame", "pred_start_frame", "pred_end_frame"]:
            converted[name] = int(row[name]) if row[name] else None
        converted["case_id"] = f"gt_{converted['gt_rally']:03d}"
        cases.append(converted)
    cases.extend(case for case in supplemental["failure_cases"] if case["matching_status"] == "unmatched_prediction")
    parameters = dict(bound.profile["components"]["rally"].get("params", {}))
    for name in ["use_reconstruction", "motion_guard", "use_exit_recovery", "use_curve_exit"]:
        parameters.pop(name, None)
    policy = RallyParams(fps=bound.media["fps_num"] / bound.media["fps_den"], **parameters)
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases").mkdir()
    summaries = []
    for case in cases:
        summary = summarize_case(case, steps, raw, traces, events, policy.min_frames, policy.start_speed)
        summary["significant_failure_case"] = case["case_id"] in significant
        dump(output / "cases" / (case["case_id"] + ".json"), summary)
        summaries.append(summary)
    if {s["case_id"] for s in summaries if s["significant_failure_case"]} != significant:
        raise ValueError("causal summaries dropped significant cases")
    consumed = {str(path.resolve()): sha(path) for path in [Path(__file__), bound.report_path,
                run / "predicted_rallies.csv", bound.events_path, proof_path, trace_path,
                supplemental_path, evaluation / "per_rally_comparison.csv", policy_path,
                ROOT / "research/production_contact_result_audit.py",
                ROOT / "research/production_external_semantic_replay.py", ROOT / "research/test2_failure_package.py"]}
    consumed.update(supplemental["provenance"])
    result = {
        "schema": "completed-run-causal-summary:v1", "source_run": str(run.resolve()),
        "source_sha256": session["source"]["sha256"], "source_session": session["session_id"],
        "fresh_inference": False, "mode": "offline diagnostic grouping of previously completed fresh neural evidence",
        "frame_count": len(raw), "trace_exact_baseline_parity": True,
        "unchanged_evaluation_rows_and_metrics_recomputed_exact": True,
        "source_cache_catalogue": bound.cache_catalogue_receipt,
        "annotated_rows": len(comparisons), "unmatched_prediction_rows": len(cases) - len(comparisons),
        "significant_cases": len(significant), "all_significant_cases_preserved": True,
        "machine_mechanism_counts": dict(Counter(
            tag for summary in summaries for tag in summary["machine_mechanism_tags"])),
        "significant_machine_mechanism_counts": dict(Counter(
            tag for summary in summaries if summary["significant_failure_case"]
            for tag in summary["machine_mechanism_tags"])),
        "physical_failure_mechanisms_independently_validated": False,
        "cases": [{"case_id": s["case_id"], "matching_status": s["evaluation"]["matching_status"],
                   "significant": s["significant_failure_case"], "tags": s["machine_mechanism_tags"],
                   "case_json": "cases/" + s["case_id"] + ".json",
                   "firsts": s["reference_interval_diagnostics"]["firsts"],
                   "earliest_recorded_gate_limitation": s["reference_interval_diagnostics"][
                       "earliest_recorded_gate_limitation"]} for s in summaries],
        "input_sha256": consumed,
        "output_artifact_sha256": {str(path.relative_to(output)): sha(path)
                                   for path in sorted((output / "cases").glob("*.json"))},
    }
    dump(output / "causal_summary.json", result)
    for path, expected in consumed.items():
        if sha(Path(path)) != expected:
            raise ValueError("causal analysis input changed during execution")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["run", "replay", "evaluation", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    result = analyse(args.run.resolve(), args.replay.resolve(), args.evaluation.resolve(), args.output.resolve())
    keys = ["annotated_rows", "unmatched_prediction_rows", "significant_cases"]
    print(json.dumps({key: result[key] for key in keys}))


if __name__ == "__main__":
    main()
