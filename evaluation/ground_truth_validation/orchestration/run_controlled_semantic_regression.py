"""Guarded Test1/Test2 full-timeline engine regression on unchanged perceptions.

This invokes cached semantic replay only, NEVER fresh neural inference. Original
completed runs, strict parity proofs, references and reports remain immutable.
Run only after the orchestrator explicitly applies the reviewed two-file fix.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from evaluation.ground_truth_validation.orchestration.evaluate_test01_components import (  # noqa: E402
    reference_comparison,
)
from research.pipeline_repair_run_analysis import (  # noqa: E402
    audit_frames,
    event_summary,
    load_analysis_input,
    load_chunks,
    select_live_events,
)
from research.production_external_semantic_replay import (  # noqa: E402
    REPLAY_SCHEMA,
    load_finished_input,
    read,
    require_source_intervention,
    sha,
    source_hashes,
    verify_replay_output_artifacts,
)
from scripts.benchmarking.evaluate_rallies import Rally  # noqa: E402

WORKSPACE = ROOT / "evaluation/ground_truth_validation"
EXTERNAL = ROOT.parent / "ground-truth-validation-artifacts-20261110"
ENGINE = "sports/badminton/src/bai_badminton/engine.py"
ADMISSION = "sports/badminton/src/bai_badminton/racket_admission.py"
ALLOWED_CHANGES = {ENGINE, ADMISSION}
CONTRACTS = {
    1: {
        "source": "877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6",
        "frames": 17268,
        "baseline": EXTERNAL / "test_01/improved_v1",
        "refs": {
            "Test1_Full.csv",
            "Test1_Full2.csv",
            "Test1_Full_rally.csv",
            "Test1_Full_rev_T.csv",
            "Test1_Full_rev_T4.csv",
            "win_predictions.csv",
        },
    },
    2: {
        "source": "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a",
        "frames": 29296,
        "baseline": EXTERNAL / "test_02/baseline_v1",
        "refs": {"Test2_Full.csv", "Test2_Full_rally.csv", "win_predictions.csv"},
    },
}


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def validate_applied_fix(receipt, current, recorded, *, root=ROOT):
    """Accept only the declared engine edit and newly added admission helper."""
    if receipt.get("schema") != "test2-applied-correctness-fix:v1":
        raise ValueError("Applied production fix receipt schema required")
    if receipt.get("fix") != "racket_anatomical_alias_abstention_v1":
        raise ValueError("Only the reviewed racket admission fix is authorized")
    for key in ("regressions_passed", "baseline_protected", "perception_models_profile_unchanged"):
        if receipt.get(key) is not True:
            raise ValueError("Applied fix requires true " + key)
    declared = {}
    for name, value in receipt.get("production_files", {}).items():
        path = Path(name)
        path = path if path.is_absolute() else root / path
        relative = str(path.resolve().relative_to(root.resolve()))
        if relative in declared:
            raise ValueError("Duplicate production receipt path")
        declared[relative] = value
    baseline = {name: digest for name, digest in recorded.items() if name.startswith(("engine/src/", "sports/"))}
    delta = {
        name: {"recorded": baseline.get(name), "current": current.get(name)}
        for name in sorted(baseline.keys() | current.keys())
        if baseline.get(name) != current.get(name)
    }
    if set(delta) != ALLOWED_CHANGES or set(declared) != ALLOWED_CHANGES:
        raise ValueError("Require exact engine.py plus new racket_admission.py delta; no other core changes")
    if baseline.get(ADMISSION) is not None or current.get(ADMISSION) is None:
        raise ValueError("Admission helper must be a new file relative to this completed baseline")
    for name, change in delta.items():
        value = declared[name]
        if (
            value.get("before_sha256") != change["recorded"]
            or value.get("after_sha256") != change["current"]
            or change["current"] is None
        ):
            raise ValueError("Applied fix source hashes differ from completed baseline/current source")
    return delta


def require_proof_contract(proof, *, test, report_sha, caches, run):
    n = CONTRACTS[test]["frames"]
    if (
        proof.get("schema") != REPLAY_SCHEMA
        or proof.get("baseline_parity") is not True
        or proof.get("geometry_bracket") is not False
        or proof.get("contact_motion_reliability") is not False
        or proof.get("source_intervention") is not None
        or proof.get("source_report_sha256") != report_sha
        or proof.get("cache_sha256") != caches
        or proof.get("session_id") != f"UPLOADTEST{test}"
        or Path(proof.get("source_run", "/missing")).resolve() != run.resolve()
        or proof.get("frames") != n
        or proof.get("trace_step_count") != n
        or proof.get("trace_ranges_telemetry_only") != [[0, n]]
        or not proof.get("harness_source_sha256")
    ):
        raise ValueError("Require original strict full-timeline parity proof bound to this exact source/cache/run")


def events(path, sid):
    values = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    return values, select_live_events(values, sid)


def live_rallies(live, *, n):
    values = sorted((e["frame_start"], e["frame_end"]) for e in live if e["type"] == "rally_end")
    if any(type(s) is not int or type(e) is not int or not 0 <= s < e <= n for s, e in values):
        raise ValueError("Replay rally intervals must be positive canonical source-frame intervals")
    return [Rally(s, e, s / 30, e / 30) for s, e in values]


def event_counts(all_events, live, sid):
    summary = event_summary(all_events, sid)

    def valid(value):
        return value is not None and value not in ("", "unknown", "unavailable")

    summary["semantic_counts"] = {
        "known_rally_winners": sum(
            e["type"] == "rally_end" and valid(e.get("payload", {}).get("winner")) for e in live
        ),
        "official_rallies": sum(
            e["type"] == "rally_end" and e.get("payload", {}).get("official") is True for e in live
        ),
        "contacts": sum(e["type"] == "contact" for e in live),
        "contacts_with_named_actor": sum(
            e["type"] == "contact" and bool(e.get("actors", {}).get("player_id")) for e in live
        ),
        "identity_ambiguity_events": sum(e["type"] == "identity_ambiguity" for e in live),
        "live_type_counts": dict(collections.Counter(e["type"] for e in live)),
    }
    return summary


def frozen_files(mapping):
    for name, expected in mapping.items():
        path = Path(name)
        if not path.is_file() or sha(path) != expected:
            raise ValueError("Protected original input changed: " + name)


def fix_test_logs(receipt):
    declared = receipt.get("test_logs")
    if not isinstance(declared, list) or not declared:
        raise ValueError("Applied fix receipt requires retained regression test logs")
    paths = {}
    for item in declared:
        name = item if isinstance(item, str) else item.get("path") if isinstance(item, dict) else None
        if not isinstance(name, str):
            raise ValueError("Regression test log requires an explicit file path")
        path = Path(name)
        path = (path if path.is_absolute() else ROOT / path).resolve(strict=True)
        if not path.is_file():
            raise ValueError("Regression test log must be a retained regular file")
        digest = sha(path)
        if isinstance(item, dict) and item.get("sha256", digest) != digest:
            raise ValueError("Regression test log hash changed")
        paths[str(path)] = digest
    return paths


def verify_trace(path, n):
    count = 0
    with path.open() as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("call") != "step":
                continue
            frame, frontier = row.get("frame"), row.get("available_through")
            if type(frame) is not int or frame != count or type(frontier) is not int or not frame <= frontier < n:
                raise ValueError("Full ordered FSM trace requires every source frame and a valid emission frontier")
            count += 1
    if count != n:
        raise ValueError("Incomplete full-timeline FSM trace")
    return count


def trace_schedule_states(path, chunk_frontiers, n):
    """Read every traced call in order; contacts after step may change cadence.

    The terminal chunk frontier is excluded from next-chunk feedback: engine
    flush advances delayed tail steps at that same frontier, and no subsequent
    neural chunk exists. Its observations remain separately disclosed.
    """
    frontiers = sorted(set(chunk_frontiers))
    if not frontiers or frontiers[-1] != n - 1 or frontiers != list(chunk_frontiers):
        raise ValueError("Exact increasing completed-cache chunk frontiers required")
    valid_states = {"idle", "in_play", "ending", "closed"}
    last, steps, flushes = {}, {}, []
    with path.open() as stream:
        for sequence, line in enumerate(stream):
            row = json.loads(line)
            call, frontier = row.get("call"), row.get("available_through")
            before, after = row.get("before", {}).get("state"), row.get("after", {}).get("state")
            if before not in valid_states or after not in valid_states:
                raise ValueError("Schedule comparison requires explicit valid before/after FSM states")
            item = {
                "sequence": sequence,
                "call": call,
                "frame": row.get("frame"),
                "available_through": frontier,
                "state_before": before,
                "state_after": after,
                "in_play_after": after != "idle",
            }
            if call == "step":
                if row["frame"] in steps:
                    raise ValueError("Schedule comparison refuses duplicate FSM step frames")
                steps[row["frame"]] = item
            if call == "flush":
                flushes.append(item)
            if frontier in frontiers:
                # Include all traced operations, including nonterminal format
                # flushes, on_contact/evidence and on_discontinuity after a step.
                last[frontier] = item
    if sorted(steps) != list(range(n)):
        raise ValueError("Missing full source steps in schedule trace")
    return {
        "frontiers": {f: last.get(f) for f in frontiers[:-1]},
        "unobserved_frontiers": [f for f in frontiers[:-1] if f not in last],
        "steps": steps,
        "excluded_terminal_frontier": last.get(frontiers[-1]),
        "flush_calls": flushes,
    }


def compare_schedule_feedback(before_path, after_path, chunk_frontiers, n):
    before = trace_schedule_states(before_path, chunk_frontiers, n)
    after = trace_schedule_states(after_path, chunk_frontiers, n)
    rows = []
    for frontier in chunk_frontiers[:-1]:
        left, right = before["frontiers"][frontier], after["frontiers"][frontier]
        observed = left is not None and right is not None
        rows.append(
            {
                "frontier": frontier,
                "baseline_last_operation": left,
                "candidate_last_operation": right,
                "comparison_status": "observed" if observed else "unobserved_frontier",
                "fsm_state_equal": left["state_after"] == right["state_after"] if observed else None,
                "nonidle_schedule_driver_equal": left["in_play_after"] == right["in_play_after"] if observed else None,
            }
        )
    differing = [r["frontier"] for r in rows if r["nonidle_schedule_driver_equal"] is False]
    state_differences = [r["frontier"] for r in rows if r["fsm_state_equal"] is False]
    unknown = [r["frontier"] for r in rows if r["comparison_status"] == "unobserved_frontier"]
    step_differences = [
        f
        for f in range(n)
        if any(before["steps"][f][key] != after["steps"][f][key] for key in ("state_before", "state_after"))
    ]
    return {
        "driver": "BadmintonSession.in_play == engine.fsm.state is not RallyState.IDLE",
        "method": "Final traced operation in original call order at each actual nonterminal cache chunk frontier",
        "frontier_count_requested": len(rows),
        "frontier_count_compared": len(rows) - len(unknown),
        "frontier_count_unknown": len(unknown),
        "unknown_driver_frontiers": unknown,
        "baseline_unobserved_frontiers": before["unobserved_frontiers"],
        "candidate_unobserved_frontiers": after["unobserved_frontiers"],
        "frontier_comparisons": rows,
        "identical_driver_frontiers": [r["frontier"] for r in rows if r["nonidle_schedule_driver_equal"]],
        "differing_driver_frontiers": differing,
        "fsm_state_differing_frontiers": state_differences,
        "known_schedule_drivers_equal": not differing,
        "schedule_driver_equal": False if differing else None if unknown else True,
        "final_fsm_states_equal": False if state_differences else None if unknown else True,
        "all_step_before_after_states_equal": not step_differences,
        "step_state_differing_frames": step_differences,
        "terminal_frontier_excluded_from_next_chunk_feedback": n - 1,
        "baseline_terminal_record": before["excluded_terminal_frontier"],
        "candidate_terminal_record": after["excluded_terminal_frontier"],
        "baseline_flush_calls": before["flush_calls"],
        "candidate_flush_calls": after["flush_calls"],
        "fresh_inference_required_due_to_feedback_change": bool(differing),
        "fresh_inference_required_due_to_feedback_uncertainty": bool(unknown),
        "fresh_inference_required": bool(differing or unknown),
        "unknown_frontier_policy": "No carried/interpolated FSM state is inferred for unobserved chunk frontiers. "
        "Complete ordered steps permit interval evaluation, but uncertain cadence requires fresh inference.",
        "scope": "Driver equality with unchanged perception/profile/model inputs establishes equal recorded "
        "chunk-cadence input. It is not a new neural execution or independent physical accuracy test.",
    }


def verify_report_resume_preflight(output, expected, *, root=ROOT):
    """Verify existing evidence against its archived helper, not edited source.

    This refuses completed/partially written reports. Only an already completed
    replay whose report helper failed before writing outputs may be recovered.
    """
    for name in (
        "semantic_regression_metrics.json",
        "perception_schedule_feedback.json",
        "REPORT.md",
        "completion.json",
        "report_recovery_v1",
    ):
        if (output / name).exists() or (output / name).is_symlink():
            raise ValueError("Report-only resume refuses existing report/recovery outputs: " + name)
    previous = read(output / "preflight.json")
    for key, value in expected.items():
        if previous.get(key) != value:
            raise ValueError("Resume preflight binding differs: " + key)
    protected = previous.get("protected_inputs_sha256")
    if not protected:
        raise ValueError("Resume requires original protected input hash map")
    frozen_files(protected)
    helpers = previous.get("helper_sha256")
    if not helpers:
        raise ValueError("Resume requires original archived helper hashes")
    verified = {}
    this_helper = Path(__file__).resolve()
    if str(this_helper) not in helpers:
        raise ValueError("Resume requires the original report helper source hash")
    for name, digest in helpers.items():
        relative = Path(name).resolve().relative_to(root.resolve())
        archived = output / "executed_helpers" / relative
        if archived.is_symlink() or not archived.is_file() or sha(archived) != digest:
            raise ValueError("Resume original archived helper hash differs")
        # This report helper is the declared correction. Other evaluation
        # dependencies must remain the same as the original executed helpers.
        if Path(name).resolve() != this_helper and sha(Path(name)) != digest:
            raise ValueError("Resume refuses an undeclared evaluation dependency change")
        verified[str(archived)] = digest
    if sha(output / "applied_fix_receipt.json") != previous["applied_fix_receipt_sha256"]:
        raise ValueError("Resume original applied fix receipt changed")
    return previous, verified


def verify_completed_candidate(output, *, intervention, current, proof, n, caches, report_sha, run, sid):
    replay_dir = output / "replay"
    replay = read(replay_dir / "replay_manifest.json")
    verify_replay_output_artifacts(replay_dir, replay)
    verify_trace(replay_dir / "bounded_fsm_trace.jsonl", n)
    if (
        replay.get("source_intervention") != intervention
        or replay.get("frames") != n
        or replay.get("trace_step_count") != n
        or replay.get("trace_ranges_telemetry_only") != [[0, n]]
        or replay.get("cache_sha256") != caches
        or replay.get("source_report_sha256") != report_sha
        or replay.get("executed_source_sha256") != current
        or replay.get("core_source_snapshot", {}).get("sha256") != current
        or replay.get("actual_profile") != proof.get("actual_profile")
        or replay.get("baseline_proof_sha256") != intervention["baseline_proof_sha256"]
        or replay.get("session_id") != sid
        or Path(replay.get("source_run", "/missing")).resolve() != run.resolve()
    ):
        raise ValueError("Replay completed manifest has foreign cache/source/profile/intervention or incomplete trace")
    helpers = replay.get("harness_source_sha256")
    if not helpers:
        raise ValueError("Completed replay requires archived harness source hashes")
    for name, digest in helpers.items():
        if sha(replay_dir / "executed_helpers" / name) != digest:
            raise ValueError("Completed replay archived harness changed")
    return replay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", type=int, choices=(1, 2), required=True)
    parser.add_argument("--fix-receipt", type=Path, default=WORKSPACE / "test_02/fixes/applied_fix_receipt.json")
    parser.add_argument("--baseline-root", type=Path)
    parser.add_argument("--baseline-proof", type=Path)
    parser.add_argument("--baseline-metrics", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--resume-report-only",
        action="store_true",
        help="Verify an existing completed replay and recover absent reports; never rerun replay",
    )
    parser.add_argument(
        "--original-failure-log",
        type=Path,
        help="Original report-helper launch traceback log, required for report-only recovery",
    )
    args = parser.parse_args()
    contract = CONTRACTS[args.test]
    baseline = (args.baseline_root or contract["baseline"]).resolve(strict=True)
    run = baseline / "run"
    proof_dir = (args.baseline_proof or baseline / "diagnostic_replay").resolve(strict=True)
    metrics = args.baseline_metrics
    if metrics is None:
        candidate = baseline / "bound_reference_diagnostics/component_reference_metrics.json"
        metrics = (
            candidate if candidate.is_file() else baseline / "all_reference_components/component_reference_metrics.json"
        )
    metrics = metrics.resolve(strict=True)
    output = (args.output or EXTERNAL / f"test_02/test{args.test}_semantic_regression_v1").resolve()
    link = WORKSPACE / f"test_02/regression/test{args.test}_semantic_regression_v1"
    if output in (ROOT, baseline, run) or ROOT in output.parents or run in output.parents:
        raise ValueError("Require external output outside immutable original run")
    if args.resume_report_only:
        if (
            not output.is_dir()
            or not link.is_symlink()
            or link.resolve() != output
            or args.original_failure_log is None
            or not args.original_failure_log.is_file()
        ):
            raise ValueError("Report-only resume requires existing output/link and original failure log")
    elif output.exists() or link.exists() or link.is_symlink():
        raise ValueError("Require new external output and an unused Test2 regression link")
    sid, n = f"UPLOADTEST{args.test}", contract["frames"]
    session = read(run / "session.json")
    if session.get("session_id") != sid or session.get("source", {}).get("sha256") != contract["source"]:
        raise ValueError("Wrong video/session rejected before completion or annotation access")
    bound = load_analysis_input(run, None)
    media = bound["media"]
    if bound["source_sha256"] != contract["source"] or tuple(
        media[k] for k in ("width", "height", "fps_num", "fps_den", "n_frames")
    ) != (1280, 720, 30, 1, n):
        raise ValueError("Exact Test-specific canonical media contract required")
    finished = load_finished_input(run, sid)
    consumed = {str(p): sha(p) for p in bound["input_paths"]}
    consumed.update(
        {
            str(run / "predicted_rallies.csv"): sha(run / "predicted_rallies.csv"),
            str(metrics): sha(metrics),
            str(args.fix_receipt.resolve(strict=True)): sha(args.fix_receipt),
        }
    )
    proof = read(proof_dir / "replay_manifest.json")
    report_sha = sha(finished.report_path)
    require_proof_contract(proof, test=args.test, report_sha=report_sha, caches=finished.expected_caches, run=run)
    verify_replay_output_artifacts(proof_dir, proof)
    verify_trace(proof_dir / "bounded_fsm_trace.jsonl", n)
    for name, digest in proof["harness_source_sha256"].items():
        p = proof_dir / "executed_helpers" / name
        if sha(p) != digest:
            raise ValueError("Original baseline proof helper source bytes changed")
    consumed[str(proof_dir / "replay_manifest.json")] = sha(proof_dir / "replay_manifest.json")
    current = source_hashes()
    fix = read(args.fix_receipt)
    delta = validate_applied_fix(fix, current, finished.code_files)
    tests = fix_test_logs(fix)
    consumed.update(tests)
    plan = read(finished.manifest_path)
    # Includes frozen source video, prepared profile/session, actual source
    # profile, model manifest and model lock: no changed profile/model selection.
    frozen_files(plan["input_files_sha256"])
    consumed.update(plan["input_files_sha256"])
    chunks, frames = load_chunks(finished.cache_directory, finished.expected_caches, consumed)
    coverage, _ = audit_frames(frames, n)
    chunk_frontiers = [chunk["end"] for chunk in chunks]
    del chunks, frames
    old_metrics = read(metrics)
    if (
        old_metrics.get("source_sha256") != contract["source"]
        or Path(old_metrics.get("run", "/missing")).resolve() != run.resolve()
        or set(old_metrics.get("interval_reference_comparisons", {})) != contract["refs"]
    ):
        raise ValueError("Completed baseline metrics must bind exact source/run and full reference population")
    annotations = ROOT / f"Part2/dataset/Test{args.test}_Full"
    originals = old_metrics["input_sha256"]
    for path in sorted(annotations.iterdir()):
        if path.is_file():
            if originals.get(str(path)) != sha(path):
                raise ValueError("Original annotation differs from completed baseline matrix")
            consumed[str(path)] = sha(path)
    intervention = {
        "schema": "controlled-semantic-source-intervention:v1",
        "source_report_sha256": report_sha,
        "baseline_proof_sha256": sha(proof_dir / "replay_manifest.json"),
        "executed_source_sha256": current,
        "changes": delta,
        "hypothesis": "Reject source-demonstrated anatomical ellipse aliases at the engine evidence boundary; "
        "preserve all recorded perception, profile and model bytes and test full timeline semantics.",
    }
    require_source_intervention(
        intervention,
        proof,
        report_sha=report_sha,
        proof_sha=intervention["baseline_proof_sha256"],
        current_sources=current,
        recorded_sources=finished.code_files,
    )
    snapshot_paths = [
        Path(__file__),
        ROOT / "evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py",
        ROOT / "research/pipeline_repair_run_analysis.py",
        ROOT / "research/test2_evaluation.py",
        ROOT / "scripts/benchmarking/evaluate_rallies.py",
    ]
    preflight = {
        "test": args.test,
        "source_sha256": contract["source"],
        "frames": n,
        "baseline": str(baseline),
        "baseline_metrics": str(metrics),
        "baseline_proof": str(proof_dir),
        "core_delta": delta,
        "protected_inputs_sha256": consumed,
        "original_cache_coverage": coverage,
        "new_neural_inference": False,
        "applied_fix_receipt_sha256": sha(args.fix_receipt),
    }
    recovery_receipt = None
    start = time.monotonic()
    if args.resume_report_only:
        previous, archived = verify_report_resume_preflight(output, preflight)
        if read(output / "source_intervention.json") != intervention:
            raise ValueError("Resume original source-intervention manifest differs")
        verify_completed_candidate(
            output,
            intervention=intervention,
            current=current,
            proof=proof,
            n=n,
            caches=finished.expected_caches,
            report_sha=report_sha,
            run=run,
            sid=sid,
        )
        recovery_dir = output / "report_recovery_v1"
        recovery_dir.mkdir()
        snapshot_base = recovery_dir
        failure_log = args.original_failure_log.resolve(strict=True)
        consumed[str(failure_log)] = sha(failure_log)
        shutil.copyfile(failure_log, recovery_dir / "original_report_helper_failure.log")
        recovery_receipt = {
            "schema": "controlled-semantic-report-only-recovery:v1",
            "test": args.test,
            "scope": "Existing child replay is complete; recover failed evaluation/report helper only",
            "new_neural_inference": False,
            "semantic_replay_rerun": False,
            "original_preflight_sha256": sha(output / "preflight.json"),
            "original_intervention_sha256": sha(output / "source_intervention.json"),
            "completed_replay_manifest_sha256": sha(output / "replay/replay_manifest.json"),
            "original_archived_helpers_sha256": archived,
            "original_failure_log": str(failure_log),
            "original_failure_log_sha256": sha(failure_log),
            "original_replay_log_sha256": sha(output / "replay.log"),
            "original_replay_command_sha256": sha(output / "replay.command.json"),
            "original_helper_sha256": previous["helper_sha256"][str(Path(__file__).resolve())],
            "corrected_report_helper_sha256": sha(Path(__file__)),
            "reason": "Complete ordered source steps do not guarantee a traced operation at every chunk frontier; "
            "retain unknown frontier state and require fresh inference rather than blocking interval evaluation.",
        }
        dump(
            recovery_dir / "resume.command.json",
            {"argv": [sys.executable, *sys.argv], "cwd": str(ROOT), "scope": recovery_receipt["scope"]},
        )
    else:
        output.mkdir(parents=True)
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(output, target_is_directory=True)
        dump(output / "source_intervention.json", intervention)
        shutil.copyfile(args.fix_receipt, output / "applied_fix_receipt.json")
        for index, name in enumerate(tests):
            target = output / "executed_fix_tests" / f"{index:02d}_{Path(name).name}"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(name, target)
        snapshot_base = output
    helper_hashes = {}
    for path in snapshot_paths:
        destination = snapshot_base / "executed_helpers" / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        helper_hashes[str(path)] = sha(path)
    if args.resume_report_only:
        recovery_receipt["corrected_helper_sha256"] = helper_hashes
        dump(snapshot_base / "resume_receipt.json", recovery_receipt)
    else:
        dump(output / "preflight.json", {**preflight, "helper_sha256": helper_hashes})
    command = [
        str(ROOT / ".venv/bin/python"),
        str(ROOT / "research/production_external_semantic_replay.py"),
        "--run",
        str(run),
        "--session",
        sid,
        "--output",
        str(output / "replay"),
        "--baseline-proof",
        str(proof_dir),
        "--source-intervention",
        str(output / "source_intervention.json"),
        "--trace-ranges",
        json.dumps([[0, n]]),
        "--focus",
        "",
    ]
    if not args.resume_report_only:
        dump(
            output / "replay.command.json",
            {"argv": command, "cwd": str(ROOT), "scope": "cached semantic replay only; NOT fresh neural inference"},
        )
        with (output / "replay.log").open("x") as stream:
            result = subprocess.run(  # noqa: S603 - fixed local helper and source-bound paths passed as argv
                command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=False
            )
        if result.returncode:
            dump(
                output / "failure.json",
                {"stage": "semantic_replay", "returncode": result.returncode, "new_neural_inference": False},
            )
            raise RuntimeError("Controlled semantic replay failed; logs preserved")
    verify_completed_candidate(
        output,
        intervention=intervention,
        current=current,
        proof=proof,
        n=n,
        caches=finished.expected_caches,
        report_sha=report_sha,
        run=run,
        sid=sid,
    )
    frozen_files(consumed)
    verify_replay_output_artifacts(proof_dir, proof)
    frozen_files(helper_hashes)
    if source_hashes() != current:
        raise ValueError("Production source changed during controlled regression")
    new_all, new_live = events(output / "replay/events.jsonl", sid)
    old_all, old_live = events(finished.events_path, sid)
    feedback = compare_schedule_feedback(
        proof_dir / "bounded_fsm_trace.jsonl", output / "replay/bounded_fsm_trace.jsonl", chunk_frontiers, n
    )
    dump(output / "perception_schedule_feedback.json", feedback)
    predictions = live_rallies(new_live, n=n)
    comparisons = {}
    for name in sorted(contract["refs"]):
        compared = reference_comparison(annotations / name, predictions, 30, partial="Full2" in name)
        original = old_metrics["interval_reference_comparisons"][name]
        if (
            compared["role"] != original["role"]
            or compared["reference_source_rows"] != original["reference_source_rows"]
        ):
            raise ValueError("Reference interpretation or population changed")
        comparisons[name] = {
            "baseline_metrics": original["metrics"],
            "semantic_replay_metrics": compared["metrics"],
            "metrics_equal": original["metrics"] == compared["metrics"],
            "reference_role": compared["role"],
            "full_replay_comparison": compared,
        }
    summary = {
        "status": "completed_controlled_semantic_regression",
        "test": args.test,
        "scope": "Full-timeline semantic regression over immutable recorded perception; NOT fresh neural inference",
        "source_sha256": contract["source"],
        "frames": n,
        "baseline_run": str(run),
        "baseline_metrics_sha256": sha(metrics),
        "source_intervention": intervention,
        "all_reference_comparisons": comparisons,
        "all_interval_metrics_equal": all(value["metrics_equal"] for value in comparisons.values()),
        "baseline_event_summary": event_counts(old_all, old_live, sid),
        "semantic_replay_event_summary": event_counts(new_all, new_live, sid),
        "parity_vs_original": read(output / "replay/parity_vs_fresh.json"),
        "new_neural_inference": False,
        "independent_physical_accuracy": False,
        "original_inputs_annotations_cache_unchanged": True,
        "perception_schedule_feedback": feedback,
        "full_pipeline_preservation_scope": "CONDITIONAL: scheduling feedback changed or was unobserved; "
        f"fresh Test{args.test} "
        "inference is required "
        "before claiming full-pipeline preservation."
        if feedback["fresh_inference_required"]
        else "All compared nonterminal chunk-cadence drivers match with unchanged perception/profile/models. "
        "This remains a fixed-perception semantic regression, not fresh neural inference.",
        "report_only_recovery": args.resume_report_only,
        "report_recovery_receipt": recovery_receipt,
        "runtime_seconds_replay_and_comparison": None if args.resume_report_only else time.monotonic() - start,
        "runtime_seconds_report_recovery": time.monotonic() - start if args.resume_report_only else None,
        "limitations": [
            "No new AP/HOTA/contact/racket physical accuracy labels or fresh model evaluation.",
            "Generated reference agreement and partial Full2 limits remain unchanged.",
            "Semantic parity may change by design; unchanged or improved interval metrics do not certify contacts.",
            "A candidate is not automatically accepted by this orchestration helper.",
        ],
    }
    frozen_files(consumed)
    dump(output / "semantic_regression_metrics.json", summary)
    write_report(output, summary)
    artifacts = {
        str(p.relative_to(output)): sha(p)
        for p in output.rglob("*")
        if p.is_file() and p.suffix not in {".sqlite", ".sqlite-wal", ".sqlite-shm"}
    }
    dump(
        output / "completion.json",
        {"status": summary["status"], "test": args.test, "new_neural_inference": False, "artifact_sha256": artifacts},
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "test": args.test,
                "frames": n,
                "all_interval_metrics_equal": summary["all_interval_metrics_equal"],
                "scope": summary["scope"],
            }
        )
    )


def write_report(output, summary):
    lines = [
        f"# Test {summary['test']} controlled semantic regression",
        "",
        summary["scope"],
        "",
        f"All {summary['frames']} canonical frames replayed. Original annotations, raw/proxy media and perception "
        "cache hashes verified unchanged. No new neural execution or independently labelled accuracy claim.",
        "",
        "| Reference | Arm | TP/FP/FN | Precision | Recall | F1 | Mean IoU | Start/end MAE frames | Duration MAE s |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name, comparison in summary["all_reference_comparisons"].items():
        for arm, key in (("completed baseline", "baseline_metrics"), ("semantic candidate", "semantic_replay_metrics")):
            m = comparison[key]
            d, b = m["detection"], m["boundary_and_duration_errors"]
            lines.append(
                f"| {name} | {arm} | {d['true_positives']}/{d['false_positives']}/{d['false_negatives']} "
                f"| {d['precision']} | {d['recall']} | {d['f1']} | {m['overlap']['mean_iou']} "
                f"| {b['start_frame']['mae']}/{b['end_frame']['mae']} | {b['duration_sec']['mae']} |"
            )
    lines.extend(
        [
            "",
            "`None` means unavailable, including precision/F1/FP for partial Full2. Each supplied reference "
            "retains its original provenance and separate denominator.",
            "",
            "## Semantic output counts",
            "",
            "```json",
            json.dumps(
                {
                    "baseline": summary["baseline_event_summary"]["semantic_counts"],
                    "candidate": summary["semantic_replay_event_summary"]["semantic_counts"],
                },
                indent=2,
            ),
            "```",
            "",
            "Complete metric distributions, unmatched intervals, event categories and parity differences "
            "are retained in `semantic_regression_metrics.json` and the hashed replay artifacts. "
            "This comparison does not itself accept a pipeline change.",
            "",
            "## Perception scheduling feedback",
            "",
            summary["full_pipeline_preservation_scope"],
            "",
            f"Nonterminal chunk frontiers compared: "
            f"{summary['perception_schedule_feedback']['frontier_count_compared']}. "
            f"Unobserved frontiers: {summary['perception_schedule_feedback']['unknown_driver_frontiers']}. "
            f"Differing non-IDLE drivers: "
            f"{summary['perception_schedule_feedback']['differing_driver_frontiers']}. "
            f"Differing final FSM states: "
            f"{summary['perception_schedule_feedback']['fsm_state_differing_frontiers']}.",
            "",
            "All traced operations are considered in their original order, including contacts and discontinuities "
            "after a step. Terminal chunk/flush is separately retained and excluded from next-chunk neural feedback. "
            "Full driver comparisons and full step-state difference frame IDs are in "
            "`perception_schedule_feedback.json`.",
            "",
        ]
    )
    with (output / "REPORT.md").open("x") as stream:
        stream.write("\n".join(lines))


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
