"""Postprocessing-only native completed-run analysis with explicit tool provenance.

Run with the frozen producer on PYTHONPATH. No native globals or ROOT are patched.
All original numerical functions are called from that actual producer module.
"""

from __future__ import annotations

import argparse
import ast
import collections
import csv
import hashlib
import importlib
import importlib.util
import inspect
import json
import shutil
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import msgpack
import numpy as np

NUMERIC_HELPERS = (
    "event_summary",
    "ocr_summary",
    "track_summary",
    "resource_summary",
    "load_baseline",
    "prediction_changes",
    "compare_frame_fields",
    "canonical",
    "read_csv",
    "interval_iou",
    "match_rallies",
)


def snapshot_execution_sources(output, provenance):
    """Keep exact executable dependencies after temporary worktrees are retired."""
    manifests = {}
    roots = (("producer", Path(provenance["producer_root"])), ("tool", Path(provenance["tool_root"])))
    for name, digest in provenance["source_sha256"].items():
        source = Path(name).resolve(strict=True)
        for label, root in roots:
            if source.is_relative_to(root):
                relative = Path("executed_dependency_sources") / label / source.relative_to(root)
                break
        else:
            raise ValueError("Execution source lies outside declared producer/tool roots")
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("Executed source changed before archival: " + name)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(data)
        manifests[str(relative)] = {"original_path": name, "sha256": digest}
    with (output / "executed_dependency_sources_manifest.json").open("x") as stream:
        json.dump(manifests, stream, indent=2, allow_nan=False)
        stream.write("\n")


def load_native_interfaces(producer_root, tool_root):
    producer_root, tool_root = Path(producer_root).resolve(), Path(tool_root).resolve()
    if (
        Path(__file__).resolve()
        != tool_root / "evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py"
    ):
        raise ValueError("Explicit tool_root does not identify this executed adapter")
    original = importlib.import_module("research.pipeline_repair_run_analysis")
    plugin = importlib.import_module("bai_badminton.plugin")
    if (
        Path(original.__file__).resolve() != producer_root / "research/pipeline_repair_run_analysis.py"
        or original.ROOT.resolve() != producer_root
    ):
        raise ValueError("Actual recorded producer ROOT required; imported modules cannot be rebased")
    if Path(plugin.__file__).resolve() != producer_root / "sports/badminton/src/bai_badminton/plugin.py":
        raise ValueError("Actual recorded producer decoder required")
    auditor_path = tool_root / "research/scene_epoch_audit_v3.py"
    spec = importlib.util.spec_from_file_location("_explicit_scene_epoch_audit_v3", auditor_path)
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    sources = {
        str(p): original.sha(p)
        for p in (Path(__file__).resolve(), auditor_path, Path(original.__file__), Path(plugin.__file__))
    }
    functions = {}
    for name in NUMERIC_HELPERS:
        function = getattr(original, name)
        path = Path(inspect.getsourcefile(function)).resolve()
        if not path.is_relative_to(producer_root):
            raise ValueError("Numerical helper imported from outside recorded producer: " + name)
        text = inspect.getsource(function)
        functions[name] = {
            "path": str(path),
            "file_sha256": original.sha(path),
            "function_source_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "function_AST_sha256": hashlib.sha256(
                ast.dump(ast.parse(text), include_attributes=False).encode()
            ).hexdigest(),
        }
        sources[str(path)] = original.sha(path)

    def decoder(packet):
        receiver = SimpleNamespace(perception=SimpleNamespace(ref_id=packet["cr"]), _isolation_id=lambda: packet["ci"])
        return plugin.BadmintonSession.decode_perception(
            receiver, msgpack.packb(packet, use_bin_type=True), diagnostic=True
        )

    provenance = {
        "version": "explicit-native-postprocessing-adapter:v1",
        "producer_root": str(producer_root),
        "tool_root": str(tool_root),
        "native_ROOT_reassigned": False,
        "native_globals_patched": False,
        "original_analyse_function_AST_sha256": hashlib.sha256(
            ast.dump(ast.parse(inspect.getsource(original.analyse)), include_attributes=False).encode()
        ).hexdigest(),
        "source_sha256": sources,
        "native_function_bindings": functions,
        "metric_arithmetic_or_threshold_change": False,
        "structural_change": (
            "Native version-paired V4/V3 and V5/V4 scene proofs; exclusive feature origins bind actual prior "
            "foreground; overlap-dependent unknowns abstain; matching and arithmetic unchanged"
        ),
    }
    return original, auditor, decoder, provenance


def require_recorded_producer(bound, producer_root, original):
    # plan.root identifies the protocol artifact workspace, not the producer.
    # The original executor command and source-file population identify code.
    producer_root = Path(producer_root).resolve()
    plan = original.read(Path(bound["plan_path"]))
    executor = original.read(Path(bound["receipt_path"]).parent.with_suffix(".executor.json"))
    command = executor.get("command", [])
    expected_worker = producer_root / "research/production_external_stress.py"
    source_files = plan["source_files_sha256"]
    if (
        len(command) < 2
        or Path(command[1]).resolve() != expected_worker
        or str(expected_worker) not in source_files
        or not all(Path(path).resolve().is_relative_to(producer_root) for path in source_files)
    ):
        raise ValueError("Recorded inference producer differs from the actual native tool imports")
    for path, digest in source_files.items():
        if original.sha(Path(path)) != digest:
            raise ValueError("Recorded frozen producer source changed: " + path)


def analyse_native_completed_run(
    run: Path, output: Path, producer_root: Path, tool_root: Path, baseline_run: Path | None = None
) -> dict:
    original, auditor, decoder, provenance = load_native_interfaces(producer_root, tool_root)
    run, output = Path(run).resolve(strict=True), Path(output).resolve()
    if output.exists() or output == run or run in output.parents or output in run.parents:
        raise ValueError("Require new postprocessing output outside immutable original run")
    completion = None
    # Both gates validate actual original completion evidence. No inference.json
    # is fabricated and original failed executor receipts are never rewritten.
    bound = original.load_analysis_input(run, completion)
    require_recorded_producer(bound, producer_root, original)
    consumed = {str(path): original.sha(path) for path in bound["input_paths"]}
    consumed[str(Path(__file__).resolve())] = original.sha(Path(__file__).resolve())
    session_path, events_path = Path(bound["session_path"]), Path(bound["events_path"])
    session = original.read(session_path)
    media, sid = bound["media"], bound["session_id"]
    n = media["n_frames"]
    if (
        session["session_id"] != sid
        or session.get("status") != "analysed"
        or session.get("analysed_frames") != n
        or session.get("frontier_frame") != n - 1
    ):
        raise ValueError("actual session differs from strict recovered completion")
    chunks, frames = original.load_chunks(Path(bound["cache_dir"]), bound["cache_sha256"], consumed)
    frame_report, csv_rows, structural_proof = auditor.audit_frames(frames, n, packets=chunks, decode_packet=decoder)
    # Source/helper identities are distinct from the new structural tool.
    for path, digest in provenance["source_sha256"].items():
        consumed[path] = digest
    plan = original.read(Path(bound["plan_path"]))
    for path, digest in plan["source_files_sha256"].items():
        if original.sha(Path(path)) != digest:
            raise ValueError("Recorded frozen producer source changed: " + path)
        consumed[path] = digest
    events = [json.loads(line) for line in events_path.open()]
    event_report = original.event_summary(events, sid)
    current_predictions = original.read_csv(run / "predicted_rallies.csv", media["fps_num"] / media["fps_den"])
    if [(r.start_frame, r.end_frame) for r in current_predictions] != sorted(
        (r["start"], r["end"]) for r in event_report["details"].get("rallies", [])
    ):
        raise ValueError("actual prediction CSV differs from its live source rally ledger")
    ocr = original.ocr_summary(chunks)
    tracks = original.track_summary(run, sid, frames, consumed)
    stage_path = run / "stage_latency_samples.json"
    parent_path = run.with_suffix(".executor.json")
    samples_path = run.with_suffix(".gpu_process_samples.jsonl")
    predictions_path = run / "predicted_rallies.csv"
    for path in (session_path, events_path, stage_path, parent_path, samples_path, predictions_path):
        consumed[str(path)] = original.sha(path)
    parent = original.read(parent_path)
    if parent.get("status") != bound["original_parent_status"]:
        raise ValueError("original parent receipt changed after recovery")
    samples = [json.loads(line) for line in samples_path.open()]
    resources = original.resource_summary(parent, samples, original.read(stage_path), n, bound["worker_info"])
    model_sets, runtime_sets = {}, {}
    for chunk in chunks:
        for target, value in ((model_sets, chunk["models"]), (runtime_sets, chunk["ci"].get("runtimes", {}))):
            key = original.canonical(value)
            if key not in target:
                target[key] = {
                    "value": value,
                    "frames": 0,
                    "canonical_sha256": hashlib.sha256(key.encode()).hexdigest(),
                }
            target[key]["frames"] += len(chunk["frames"])
    models_verified = None
    if bound["completion_mode"] == "normal_completed_worker":
        from research.pipeline_repair_completion import verify_models

        declarations = {
            "loaded_models": {key: row["value"] for key, row in model_sets.items()},
            "runtimes": {key: row["value"] for key, row in runtime_sets.items()},
        }
        models_verified = verify_models(run, declarations, bound["profile"])
        for group in models_verified.values():
            for model in group.values():
                for name in ("source_path", "staged_path", "path"):
                    if name in model:
                        consumed[model[name]] = original.sha(Path(model[name]))
        for path in (run / "models").rglob("*"):
            if path.is_file():
                consumed[str(path)] = original.sha(path)
    baseline = None
    if baseline_run is not None:
        old_predictions, old_frames = original.load_baseline(baseline_run, bound["source_sha256"], media, consumed)
        baseline = {
            "run": str(baseline_run),
            "prediction_changes": original.prediction_changes(old_predictions, current_predictions),
            "perception_field_changes": original.compare_frame_fields(old_frames, frames),
        }
    disk = Counter()
    for path in run.rglob("*"):
        if path.is_file() and not path.is_symlink():
            stat = path.stat()
            disk["regular_files"] += 1
            disk["logical_bytes"] += stat.st_size
            disk["allocated_bytes"] += stat.st_blocks * 512
            if path.is_relative_to(Path(bound["cache_dir"])):
                disk["perception_cache_bytes"] += stat.st_size
            if path.is_relative_to(run / "models"):
                disk["staged_model_bytes"] += stat.st_size
    if any(original.sha(Path(path)) != digest for path, digest in consumed.items()):
        raise ValueError("source evidence changed while analysing completed run")
    result = {
        "schema": "pipeline-repair-posthoc-run-analysis:v2",
        "structural_compatibility": {**provenance, "scene_epoch_proof": structural_proof},
        "status": "technical_analysis_after_strict_posthoc_completion_proof"
        if bound["completion_mode"] == "independent_recovery"
        else "technical_analysis_after_verified_normal_completion",
        "completion_mode": bound["completion_mode"],
        "original_parent_status": parent["status"],
        "run": str(run),
        "session_id": sid,
        "completion_receipt": str(bound["receipt_path"]),
        "completion_receipt_sha256": original.sha(Path(bound["receipt_path"])),
        "frames": n,
        "frontier_frame": session["frontier_frame"],
        "media": media,
        "source_sha256": bound["source_sha256"],
        "proxy_sha256": bound["proxy_sha256"],
        "prediction_sha256": bound["prediction_sha256"],
        "profile_canonical_sha256": hashlib.sha256(original.canonical(bound["profile"]).encode()).hexdigest(),
        "selected_components": bound["profile"].get("components", {}),
        "model_sets_from_actual_caches": list(model_sets.values()),
        "runtime_declarations_from_actual_caches": list(runtime_sets.values()),
        "component_coverage": frame_report,
        "events": event_report,
        "ocr": ocr,
        "track_exports": tracks,
        "resources": resources,
        "disk": dict(disk),
        "session_players": session.get("players"),
        "session_roster": session.get("roster"),
        "session_degraded": bound.get(
            "degraded", bound.get("completion_receipt", {}).get("original_session_degraded", [])
        ),
        "models_verified_during_analysis": models_verified,
        "baseline_comparison": baseline,
        "consumed_files_sha256": consumed,
        "inputs_unchanged_after_analysis": True,
        "ground_truth_loaded": False,
        "accuracy_validated": False,
        "limits": [
            "This is posthoc analysis; no neural inference, replay or prediction edits are performed.",
            "Explicit recovery does not change an original failed receipt; "
            "normal runs require original worker/parent success.",
            "Only saved measurements are used; unavailable fields stay null and model-only timing is not invented.",
            "Prediction-to-prediction matching and exact cache changes are not sporting accuracy.",
            "Node placement, API/frontend behavior, highlight accuracy and summaries need separate validation.",
            "A prepared canonical clip source is the actual input; "
            "older long-match/VFR derivation mapping is not inferred.",
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    snapshot_execution_sources(output, provenance)
    shutil.copyfile(Path(__file__), output / "executed_analysis_source.py")
    with (output / "frame_component_coverage.csv").open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "frame",
                "view",
                "calibration",
                "player_count",
                "detector_executed",
                "current_pose_count",
                "current_racket_count",
                "raw_scene_hypothesis",
                "actual_content_barrier",
                "scene_decision",
                "content_epoch",
            ]
        )
        writer.writerows(csv_rows)
    original.dump(output / "technical_analysis.json", result)
    if baseline is not None:
        original.dump(output / "prediction_changes.json", baseline["prediction_changes"])
        original.dump(output / "perception_field_changes.json", baseline["perception_field_changes"])
    original.dump(
        output / "analysis_manifest.json",
        {
            "schema": "pipeline-repair-run-analysis-publication:v1",
            "run": str(run),
            "completion_receipt_sha256": result["completion_receipt_sha256"],
            "script_sha256": original.sha(Path(__file__)),
            "output_artifact_sha256": {
                path.name: original.sha(path) for path in sorted(output.iterdir()) if path.is_file()
            },
            "ground_truth_loaded": False,
            "original_artifacts_modified": False,
        },
    )
    original.dump(
        output / "structural_compatibility_receipt.json",
        {
            "schema": "native-completed-run-postprocessing-compatibility:v1",
            "status": "postprocessing_only_after_original_fresh_worker_completion",
            "producer_root": str(producer_root.resolve()),
            "tool_root": str(tool_root.resolve()),
            "original_worker_and_parent_modified": False,
            "original_outer_failure_modified": False,
            "new_neural_inference": False,
            "numeric_helper_binding": provenance["native_function_bindings"],
            "structural_proof": structural_proof,
            "artifacts_sha256": {path.name: original.sha(path) for path in sorted(output.iterdir()) if path.is_file()},
        },
    )
    return result


def evaluate_native_components(run, output, producer_root, tool_root, coordinate_binding=None):
    original, auditor, decoder, provenance = load_native_interfaces(producer_root, tool_root)
    components = importlib.import_module("evaluation.ground_truth_validation.orchestration.evaluate_test02_components")
    expected_path = (
        Path(producer_root).resolve() / "evaluation/ground_truth_validation/orchestration/evaluate_test02_components.py"
    )
    if (
        Path(components.__file__).resolve() != expected_path
        or components.ROOT.resolve() != Path(producer_root).resolve()
    ):
        raise ValueError("Actual native Test2 component evaluator required")
    completion_recovery = None
    provenance["native_component_function_AST_sha256"] = hashlib.sha256(
        ast.dump(ast.parse(inspect.getsource(components.evaluate_components)), include_attributes=False).encode()
    ).hexdigest()
    component_sources = [Path(components.__file__)]
    for name in ("reference_comparison", "pair_points", "distribution", "court_diagnostic", "binding_status"):
        function = getattr(components, name)
        component_sources.append(Path(inspect.getsourcefile(function)).resolve())
        if not component_sources[-1].is_relative_to(Path(producer_root).resolve()):
            raise ValueError("Component numerical helper imported from outside the recorded producer: " + name)
        provenance["native_function_bindings"][name] = {
            "path": str(component_sources[-1]),
            "file_sha256": original.sha(component_sources[-1]),
            "function_AST_sha256": hashlib.sha256(
                ast.dump(ast.parse(inspect.getsource(function)), include_attributes=False).encode()
            ).hexdigest(),
        }
    for path in component_sources:
        provenance["source_sha256"][str(path)] = original.sha(path)
    run, output = run.resolve(strict=True), output.resolve()
    if output.exists() or output == run or run in output.parents or output in run.parents:
        raise ValueError("Require new output outside immutable original run")
    session = components.read(run / "session.json")
    if session["source"].get("sha256") != components.TEST2_SHA:
        raise ValueError("Requires exact original Test2 source hash")
    # Completion/source/cache guards run before any annotation content is read.
    bound = components.load_analysis_input(run, completion_recovery)
    require_recorded_producer(bound, producer_root, original)
    media = bound["media"]
    if (
        bound["source_sha256"] != components.TEST2_SHA
        or tuple(media[k] for k in ("width", "height", "fps_num", "fps_den", "n_frames")) != components.MEDIA
    ):
        raise ValueError("Test2 canonical source/time contract differs; explicit mapping required")
    n, fps = media["n_frames"], media["fps_num"] / media["fps_den"]
    annotations = components.ROOT / "Part2/dataset/Test2_Full"
    paths = sorted(p for p in annotations.iterdir() if p.is_file())
    if {p.name for p in paths} != components.EXPECTED_FILES:
        raise ValueError("Test2 annotation inventory changed; explicit schema review required")
    hashes = {p.name: components.sha(p) for p in paths}
    consumed = {str(p): components.sha(p) for p in bound["input_paths"]}
    consumed.update({str(p): hashes[p.name] for p in paths})
    consumed[str(run / "predicted_rallies.csv")] = components.sha(run / "predicted_rallies.csv")
    helpers = [
        Path(components.__file__).resolve(),
        components.ROOT / "evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py",
        components.ROOT / "research/pipeline_repair_run_analysis.py",
        components.ROOT / "scripts/benchmarking/evaluate_rallies.py",
        components.ROOT / "research/test2_evaluation.py",
    ]
    consumed.update({str(p): components.sha(p) for p in helpers})
    if coordinate_binding is not None:
        consumed[str(coordinate_binding)] = components.sha(coordinate_binding)
    chunks, frames = components.load_chunks(bound["cache_dir"], bound["cache_sha256"], consumed)
    coverage, _, structural_proof = auditor.audit_frames(frames, n, packets=chunks, decode_packet=decoder)
    plan = original.read(Path(bound["plan_path"]))
    for path, digest in plan["source_files_sha256"].items():
        if original.sha(Path(path)) != digest:
            raise ValueError("Recorded frozen producer source changed: " + path)
        consumed[path] = digest
    consumed.update(provenance["source_sha256"])
    predictions = components.read_csv(run / "predicted_rallies.csv", fps)
    events_path = bound["events_path"]
    consumed[str(events_path)] = components.sha(events_path)
    events = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
    live = components.select_live_events(events, session["session_id"])
    ends = sorted((e["frame_start"], e["frame_end"]) for e in live if e["type"] == "rally_end")
    if ends != [(r.start_frame, r.end_frame) for r in predictions]:
        raise ValueError("Prediction CSV differs from original live rally ledger")
    references, applicability, raw_references = {}, [], {}
    for path in paths:
        item = {"file": path.name, "sha256": hashes[path.name]}
        if path.suffix == ".csv":
            fields, table = components.rows(path)
            if "Start_Frame" in fields or "start_time" in fields:
                reference = components.reference_comparison(path, predictions, fps)
                if any(r["gt_start_frame"] < 0 or r["gt_end_frame"] > n for r in reference["comparison"]):
                    raise ValueError("Interval annotation outside Test2 source extent")
                raw_references[path.name] = {
                    "raw_rows": reference.pop("raw_rows"),
                    "comparison": reference.pop("comparison"),
                }
                references[path.name] = reference
                item.update(
                    status="evaluated_with_reference_provenance",
                    role=reference["role"],
                    valid_positive_rows=len(raw_references[path.name]["comparison"]),
                    invalid_rows=reference["invalid_rows"],
                )
            elif fields[0] == "Frame":
                components.validate_dense_timeline(table, "Frame", n)
                item.update(
                    status="generated_trajectory_diagnostic",
                    role="filled model estimate, not independent localization ground truth",
                )
            elif "player_1_x" in fields:
                components.validate_dense_timeline(table, "frame_no", n)
                item.update(
                    status="generated_point_slot_diagnostic",
                    role="bottom-center points; neither boxes nor stable physical identities",
                )
            else:
                raise ValueError("Unreviewed Test2 schema: " + path.name)
        else:
            item.update(
                status="single_frame_manual_calibration_candidate",
                role="manual asserted frame300; source/corner interpretation requires review",
            )
        applicability.append(item)
    duplicate_equal = hashes["Test2_Full_ball_filled.csv"] == hashes["Test2_Full_Rev_ball_filled.csv"]
    if not duplicate_equal:
        raise ValueError("Previously duplicate shuttle tables differ; independent reference policy review required")
    contract = components.binding_status(
        components.read(coordinate_binding) if coordinate_binding else None, bound, hashes
    )
    for evidence in contract.get("certificate", {}).get("evidence", []):
        path = Path(evidence["path"])
        if not path.is_absolute():
            path = components.ROOT / path
        consumed[str(path)] = evidence["sha256"]
    bound_coords = contract["status"] == "diagnostic_coordinate_binding_declared"
    player_bound = bound_coords and contract["certificate"].get("legacy_player_point") == "bbox_bottom_center"
    shuttle_bound = bound_coords and contract["certificate"].get("legacy_shuttle_point") == "analysis_image_xy"
    _, shuttle = components.rows(annotations / "Test2_Full_ball_filled.csv")
    _, players = components.rows(annotations / "player_detections.csv")
    candidates, player_dist, fresh_dist, shuttle_dist, outliers = [], [], [], [], []
    presence, unmatched = collections.Counter(), collections.Counter()
    out_of_bounds = []
    for frame, s, p in zip(frames, shuttle, players, strict=True):
        fi = frame["f"]
        legacy = []
        for slot in (1, 2):
            x, y = components.finite(p[f"player_{slot}_x"]), components.finite(p[f"player_{slot}_y"])
            if x is not None and y is not None:
                legacy.append({"slot": slot, "xy": [x, y], "support": components.finite(p[f"player_{slot}_conf"])})
        current = [
            {
                "index": j,
                "xy": [(q["b"][0] + q["b"][2]) / 2, q["b"][3]],
                "bbox": q["b"],
                "track_id": q["t"],
                "detector_matched": q.get("dm"),
            }
            for j, q in enumerate(frame.get("p", []))
        ]
        ls = [float(s["X"]), float(s["Y"])] if s["Visibility"] == "1" else None
        cs = frame.get("s")
        presence[f"legacy_shuttle_visible={ls is not None},current_raw_present={cs is not None}"] += 1
        inside = ls is None or (0 <= ls[0] < media["width"] and 0 <= ls[1] < media["height"])
        if not inside:
            out_of_bounds.append(fi)
        row = {
            "frame": fi,
            "time_s": fi / fps,
            "reference_players": legacy,
            "current_players": current,
            "reference_shuttle": ls,
            "reference_visibility": s["Visibility"],
            "reference_confidence": components.finite(s.get("Confidence")),
            "reference_shuttle_in_image": inside if ls is not None else None,
            "current_raw_shuttle": cs,
            "current_association_status": (frame.get("sa") or {}).get("status"),
            "current_view": frame.get("v"),
            "current_calibration_state": frame.get("cs"),
            "coordinate_binding_status": contract["status"],
        }
        if player_bound:
            for label, selected, distances in (
                ("all_current_rows", current, player_dist),
                ("fresh_detector_rows", [q for q in current if q["detector_matched"] is True], fresh_dist),
            ):
                assignments = components.pair_points([q["xy"] for q in legacy], [q["xy"] for q in selected])
                for assignment in assignments:
                    assignment["reference_slot"] = legacy[assignment["reference_slot"] - 1]["slot"]
                    assignment["current_index"] = selected[assignment["current_index"]]["index"]
                row[label + "_assignments"] = assignments
                distances.extend(a["distance_px"] for a in assignments)
                unmatched[label + "_reference_points"] += len(legacy) - len(assignments)
                unmatched[label + "_current_points"] += len(selected) - len(assignments)
        if shuttle_bound and ls is not None and cs is not None:
            distance = float(np.linalg.norm(np.asarray(ls) - np.asarray(cs)))
            shuttle_dist.append(distance)
            row["shuttle_disagreement_px"] = distance
            outliers.append(
                {
                    "frame": fi,
                    "time_s": fi / fps,
                    "distance_px": distance,
                    "reference_xy": ls,
                    "current_raw_xy": cs,
                    "reference_in_image": inside,
                }
            )
        candidates.append(row)
    pointmetrics = {
        "classification": "legacy generated-output disagreement, NOT physical accuracy",
        "coordinate_binding": contract,
        "frame_population": n,
        "legacy_player_slots_present": sum(len(r["reference_players"]) for r in candidates),
        "current_player_rows": sum(len(r["current_players"]) for r in candidates),
        "shuttle_presence_cross_counts": dict(presence),
        "player_bottom_center_distance_px": components.compact(components.distribution(player_dist))
        if player_bound
        else None,
        "fresh_detector_bottom_center_distance_px": components.compact(components.distribution(fresh_dist))
        if player_bound
        else None,
        "shuttle_raw_distance_px_both_present": components.compact(components.distribution(shuttle_dist))
        if shuttle_bound
        else None,
        "unmatched_point_counts": dict(unmatched) if player_bound else None,
        "largest_shuttle_disagreements": sorted(outliers, key=lambda x: x["distance_px"], reverse=True)[:30],
        "reference_shuttle_out_of_image_count": len(out_of_bounds),
        "reference_shuttle_out_of_image_frames": out_of_bounds,
        "out_of_image_policy": (
            "Retained and flagged, no clipping/exclusion; distances diagnose generated disagreement only"
        ),
        "duplicate_shuttle_tables": {
            "byte_identical": duplicate_equal,
            "evaluated_once": True,
            "files": ["Test2_Full_ball_filled.csv", "Test2_Full_Rev_ball_filled.csv"],
        },
    }
    court = components.court_diagnostic(
        components.read(annotations / "Test2_Full_court.json"),
        frames,
        chunks,
        live,
        contract,
        hashes["Test2_Full_court.json"],
    )
    event_report = components.event_summary(events, session["session_id"])
    tracks = components.track_summary(run, session["session_id"], frames, consumed)
    ocr = components.ocr_summary(chunks)
    parent_path, sample_path, stage_path = (
        run.with_suffix(".executor.json"),
        run.with_suffix(".gpu_process_samples.jsonl"),
        run / "stage_latency_samples.json",
    )
    for path in (parent_path, sample_path, stage_path):
        consumed[str(path)] = components.sha(path)
    resources = components.resource_summary(
        components.read(parent_path),
        [json.loads(line) for line in sample_path.read_text().splitlines() if line.strip()],
        components.read(stage_path),
        n,
        bound["worker_info"],
    )
    outcome = {
        "predicted_rallies": len(predictions),
        "known_winner_outputs": sum(e["payload"].get("winner") is not None for e in live if e["type"] == "rally_end"),
        "unknown_winner_outputs": sum(e["payload"].get("winner") is None for e in live if e["type"] == "rally_end"),
        "stroke_label_counts": dict(
            collections.Counter(str(e["payload"].get("stroke", "unknown")) for e in live if e["type"] == "stroke")
        ),
        "winner_comparison_status": "unavailable_without_verified_identity_and_adjudicated_outcomes",
    }
    result = {
        "status": "completed_readonly_component_reference_diagnostics",
        "test": 2,
        "run": str(run),
        "session_id": session["session_id"],
        "completion_mode": bound["completion_mode"],
        "original_parent_status": bound["original_parent_status"],
        "source_sha256": bound["source_sha256"],
        "media": media,
        "all_annotation_files_accounted_for": len(applicability) == 7,
        "annotation_applicability": applicability,
        "interval_reference_comparisons": components.compact(references),
        "point_diagnostics": pointmetrics,
        "court_diagnostic": court,
        "unsupported_metrics": {
            k: {"value": None, "status": "unavailable", "prerequisite": v} for k, v in components.UNAVAILABLE.items()
        },
        "outcome_and_stroke_coverage": outcome,
        "event_coverage": components.compact(event_report),
        "actual_cache_component_coverage": components.compact(coverage),
        "track_coverage": components.compact(tracks),
        "ocr_coverage": components.compact(ocr),
        "runtime_resources": components.compact(resources),
        "executed_models": bound["worker_info"].get("loaded_models") if bound["worker_info"] else None,
        "degraded_components": bound.get("degraded", []),
        "input_sha256": consumed,
        "detail_files": [
            "reference_row_comparisons.json",
            "frame_point_candidates.jsonl",
            "component_raw_details.json",
        ],
        "new_inference_performed": False,
        "annotations_modified": False,
        "predictions_modified": False,
        "physical_accuracy_claimed": False,
        "helper_sha256": components.sha(Path(components.__file__)),
        "structural_compatibility": {**provenance, "scene_epoch_proof": structural_proof},
    }
    if any(components.sha(Path(p)) != digest for p, digest in consumed.items()):
        raise ValueError("Consumed input changed during evaluation")
    output.mkdir(parents=True)
    snapshot_execution_sources(output, provenance)
    (output / "component_reference_metrics.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (output / "reference_row_comparisons.json").write_text(json.dumps(raw_references, indent=2, allow_nan=False) + "\n")
    (output / "component_raw_details.json").write_text(
        json.dumps(
            {
                "scene_records": coverage["scene_records"],
                "event_details": event_report["details"],
                "ocr": ocr,
                "tracks": tracks,
                "resources": resources,
            },
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    with (output / "frame_point_candidates.jsonl").open("x") as stream:
        for row in candidates:
            stream.write(json.dumps(row, allow_nan=False) + "\n")
    report = [
        "# Test 2 component evaluation matrix",
        "",
        (
            "Strict completed-run, exact source, cache and timeline guards passed before reading "
            "annotations. Original data/run/Test1 records remain unchanged. Generated references "
            "measure agreement; they do not establish independent physical accuracy."
        ),
        "",
        "## All annotation files",
        "",
        "| File | Role | Status |",
        "|---|---|---|",
    ]
    report.extend(f"| {v['file']} | {v['role']} | {v['status']} |" for v in applicability)
    report += [
        "",
        "## Separate interval-reference agreement",
        "",
        (
            "Unchanged rally-boundaries-v1 matching: maximum cardinality then IoU, IoU ≥0.5, "
            "half-open timestamp spans. Coarse labels and generated references are separate "
            "populations; earlier benchmarks remain immutable."
        ),
        "",
        "| Reference | TP | FP | FN | Precision | Recall | F1 | Mean IoU | Start MAE s | End MAE s | Duration MAE s |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, reference in references.items():
        metrics = reference["metrics"]
        d, b = metrics["detection"], metrics["boundary_and_duration_errors"]
        row = (
            name,
            d["true_positives"],
            d["false_positives"],
            d["false_negatives"],
            d["precision"],
            d["recall"],
            d["f1"],
            metrics["overlap"]["mean_iou"],
            b["start_time_sec"]["mae"],
            b["end_time_sec"]["mae"],
            b["duration_sec"]["mae"],
        )
        report.append("| " + " | ".join(str(x) for x in row) + " |")
    report += [
        "",
        "## Component coverage and limitations",
        "",
        (
            f"Coordinate review: `{contract['status']}`. "
            "A source/hash-bound Test2 review certificate gates distances. "
            "They remain diagnostic disagreement with generated legacy outputs."
        ),
        "",
        (
            "The two supplied shuttle CSVs are byte-identical and are scored once. Out-of-image "
            "legacy coordinates are retained and flagged without clipping. Missing "
            "poses/identities/contact labels cannot support AP, IDF1/HOTA, PCK/OKS or contact F1."
        ),
        "",
        "| Coverage item | Value |",
        "|---|---|",
    ]
    for name, value in coverage["counts"].items():
        report.append(f"| {name} | {value} |")
    for name, value in event_report["live_counts"].items():
        report.append(f"| live {name} events | {value} |")
    report += ["", "## Runtime and resources", "", "| Item | Value |", "|---|---|"]
    for key in (
        "physical_gpu_index",
        "worker_elapsed_s",
        "worker_source_fps",
        "sampled_worker_gpu_peak_mib",
        "sampled_worker_tree_peak_rss_bytes",
        "worker_final_cpu_s",
    ):
        report.append(f"| {key} | {resources.get(key)} |")
    report += [
        "",
        (
            "Runtime counts establish execution and coverage, not sporting accuracy. GPU/RSS peaks "
            "are sampled; wall-time scopes include loading/media/postprocessing and are not pure "
            "neural throughput."
        ),
        "",
        "## Unavailable physical-accuracy metrics",
        "",
    ]
    report.extend(f"- **{key}**: unavailable. Requires {value}" for key, value in components.UNAVAILABLE.items())
    report += [
        "",
        (
            "Machine-readable aggregate metrics and input hashes: "
            "`component_reference_metrics.json`. Every reference row, exact matches, missed/extra "
            "IDs, malformed rows and raw annotations: `reference_row_comparisons.json`. Synchronized"
            " per-frame candidate values: `frame_point_candidates.jsonl`. Scene/event/OCR/resource "
            "evidence: `component_raw_details.json`."
        ),
        "",
    ]
    (output / "REPORT.md").write_text("\n".join(report))
    original.dump(
        output / "structural_compatibility_receipt.json",
        {
            "schema": "native-components-postprocessing-compatibility:v1",
            "status": "postprocessing_only_after_original_fresh_worker_completion",
            "producer_root": str(Path(producer_root).resolve()),
            "tool_root": str(Path(tool_root).resolve()),
            "original_worker_and_parent_modified": False,
            "original_outer_failure_modified": False,
            "new_neural_inference": False,
            "native_function_bindings": provenance["native_function_bindings"],
            "structural_proof": structural_proof,
            "artifacts_sha256": {p.name: original.sha(p) for p in sorted(output.iterdir()) if p.is_file()},
        },
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer-root", required=True, type=Path)
    parser.add_argument("--tool-root", required=True, type=Path)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--baseline-run", type=Path)
    parser.add_argument("--mode", choices=("analysis", "components-test2"), default="analysis")
    parser.add_argument("--coordinate-binding", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Postprocessing output must be a new exclusive directory")
    if args.mode == "analysis":
        if args.coordinate_binding is not None:
            raise ValueError("Coordinate binding applies only to component evaluation")
        result = analyse_native_completed_run(
            args.run, args.output, args.producer_root, args.tool_root, args.baseline_run
        )
    else:
        if args.baseline_run is not None:
            raise ValueError("Component reference policy does not consume a baseline-run argument")
        result = evaluate_native_components(
            args.run, args.output, args.producer_root, args.tool_root, args.coordinate_binding
        )
    print(
        json.dumps(
            {"status": result["status"], "mode": args.mode, "output": str(args.output), "new_neural_inference": False},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
