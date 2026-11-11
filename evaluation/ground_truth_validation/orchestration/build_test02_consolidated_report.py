"""Publish a NEW self-contained Test2 before/after report after genuine completion.

Read-only reporting only: no inference, annotation conversion, old-run
re-evaluation, source modification, media cleanup or automatic Test3 advance.
Heavy full-run verification belongs to the existing fresh-run orchestration.
This builder independently checks its compact completion/hash/model bindings.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "evaluation/ground_truth_validation"
SOURCE_SHA = "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"
REFS = {"Test2_Full.csv", "Test2_Full_rally.csv", "win_predictions.csv"}
N = 29296
OPAQUE = {"values", "samples", "points", "frames", "scene_records", "readouts", "input_sha256",
          "frontier_comparisons", "source_intervention", "reference_source_rows", "raw_rows", "comparison",
          "unattributed_event_ids", "unresolved_event_ids", "largest_shuttle_disagreements",
          "reference_shuttle_out_of_image_frames", "evidence", "certificate", "perception_caches"}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def fmt(value):
    if value is None:
        return "Unavailable"
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("Nonfinite metric cannot be published")
        return format(value, ".10g")
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def cell(value):
    return fmt(value).replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def link(path, title=None):
    path = Path(path).resolve()
    target = "<" + str(path) + ">" if " " in str(path) else str(path)
    return "[" + (title or path.name) + "](" + target + ")"


def table(lines, headers, rows):
    lines += ["", "| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(cell(value) for value in row) + " |" for row in rows]
    lines.append("")


def flatten(value, prefix="", *, record_lists=False):
    """Preserve scalar metrics/tolerances without copying sample/frame arrays."""
    result = {}
    if isinstance(value, dict):
        for key, item in value.items():
            path = prefix + "." + str(key) if prefix else str(key)
            if key in OPAQUE and isinstance(item, (list, dict)):
                result[path + ".retained_entries"] = len(item)
                continue
            result.update(flatten(item, path, record_lists=record_lists or key == "boundary_tolerances"))
    elif isinstance(value, list):
        if record_lists and all(isinstance(item, dict) for item in value):
            for index, item in enumerate(value):
                result.update(flatten(item, prefix + f"[{index}]", record_lists=True))
        elif len(value) <= 32 and all(not isinstance(item, (dict, list)) for item in value):
            for index, item in enumerate(value):
                result.update(flatten(item, prefix + f"[{index}]"))
        else:
            result[prefix + ".retained_entries"] = len(value)
    else:
        result[prefix] = value
    return result


def compact(value):
    if isinstance(value, dict):
        return {key: (dict(retained_entries=len(item)) if key in OPAQUE and isinstance(item, (dict, list))
                      else compact(item)) for key, item in value.items() if key not in {"source_intervention"}}
    if isinstance(value, list):
        if len(value) <= 32 and all(isinstance(v, dict) for v in value):
            return [compact(item) for item in value]
        return {"retained_entries": len(value)}
    return value


def comparisons(before, after):
    a, b = flatten(before), flatten(after)
    return [(key, a.get(key), b.get(key), b[key] - a[key] if number(a.get(key)) and number(b.get(key)) else None)
            for key in sorted(set(a) | set(b))]


def absolute_markdown(text, source):
    """Make embedded report links usable from any output location."""
    base = Path(source).resolve().parent
    def replace(match):
        label, raw = match.group(1), match.group(2).strip()
        target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
        if re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|/|#)", target):
            return match.group(0)
        path, marker, anchor = target.partition("#")
        resolved = str((base / path).resolve()) + (marker + anchor if marker else "")
        if " " in resolved:
            resolved = "<" + resolved + ">"
        return "[" + label + "](" + resolved + ")"
    # Includes images because the leading exclamation mark is outside the match.
    converted = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace, text)
    return re.sub(r"^(#{1,5}) ", lambda m: "#" + m.group(1) + " ", converted, flags=re.MULTILINE)


def paired_rows(before, after):
    """Join by original reference row, never by mutable prediction ordinal."""
    if before["raw_rows"] != after["raw_rows"]:
        raise ValueError("Original annotation row content changed")
    def indexed(reference):
        result, predictions = {}, set()
        for row in reference["comparison"]:
            key = row.get("reference_data_row", row.get("gt_rally"))
            if type(key) is not int or not 1 <= key <= len(reference["raw_rows"]):
                raise ValueError("Original reference-row index outside source population")
            if key in result:
                raise ValueError("Duplicate original reference-row identity")
            result[key] = row
            if row["matching_status"] == "matched":
                if row["pred_rally"] in predictions:
                    raise ValueError("One prediction matched multiple reference rows")
                predictions.add(row["pred_rally"])
        return result
    a, b = indexed(before), indexed(after)
    if set(a) != set(b) or set(a) != set(range(1, len(before["raw_rows"])+1)):
        raise ValueError("Reference-row population differs between runs")
    rows = []
    for key in sorted(a):
        old, new = a[key], b[key]
        if any(old[k] != new[k] for k in ("gt_rally", "gt_start_frame", "gt_end_frame")):
            raise ValueError("Reference interval changed across before/after")
        rows.append({"reference_data_row": key, "source_annotation": before["raw_rows"][key-1],
                     "baseline": old, "fresh_postfix": new})
    return rows


def require_finished_documents(info, executor, *, expected_sha=SOURCE_SHA, expected_frames=N):
    """Pure completion admission, also exercised by small guard fixtures."""
    if (info.get("status") != "completed" or info.get("cached_perception_used") is not False
        or info.get("frames_processed") != expected_frames or info.get("frontier_frame") != expected_frames-1
        or info.get("source_sha256") != expected_sha or executor.get("status") != "completed"
        or executor.get("worker_exit_code") != 0 or executor.get("frozen_source_inputs_unchanged") is not True):
        raise ValueError("Genuine completed fresh full inference and parent receipt required")
    if executor.get("output_proxy_sha256") != info.get("proxy_sha256"):
        raise ValueError("Parent/worker proxy identities differ")
    catalogue = executor.get("perception_cache_catalog_verification", {})
    receipt = info.get("perception_cache_catalog", {})
    if (catalogue.get("status") != "verified" or catalogue.get("frames") != expected_frames
        or catalogue.get("catalog_sha256") != receipt.get("sha256")
        or catalogue.get("files") != receipt.get("file_count")):
        raise ValueError("Parent-verified full cache completion catalogue required")


def require_final_receipts(completion, diagnostics, verification, comparison):
    if (completion.get("status") != "completed_fresh_Test2_improved_and_diagnostics"
        or completion.get("frames") != N or completion.get("fresh_neural_inference_performed") is not True
        or any(completion.get(key) is not True for key in ("annotations_unchanged", "baseline_unchanged",
              "models_unchanged", "profile_unchanged", "own_run_semantic_parity"))
        or diagnostics.get("status") != "full_Test2_improved_component_metrics_and_source_diagnostics_complete"
        or diagnostics.get("original_annotations_unchanged") is not True or diagnostics.get("baseline_unchanged") is not True
        or verification.get("status") != "completed" or verification.get("baseline_unchanged") is not True
        or verification.get("original_annotations_unchanged") is not True
        or comparison.get("model_checkpoint_identity_equal") is not True or comparison.get("profile_equal") is not True):
        raise ValueError("All post-fix comparisons, matrices and final preservation receipts must finish before publication")


def model_identity(analysis):
    return {group: {name: {k: row[k] for k in ("sha256", "status") if k in row}
                    for name, row in records.items()}
            for group, records in analysis["models_verified_during_analysis"].items()}


def require_independent_review(review, receipt):
    if (review.get("status") != "completed_independent_fresh_component_review"
        or review.get("source_sha256") != SOURCE_SHA or review.get("fresh_cached_perception_used") is not False
        or review.get("inputs_unchanged") is not True
        or receipt.get("status") != "completed_independent_fresh_component_review"
        or receipt.get("all_unsupported_values_null") is not True
        or receipt.get("all_local_links_exist") is not True
        or receipt.get("parent_outer_orchestration_completion_claimed") is not False):
        raise ValueError("Completed source-bound independent fresh component review required")


def load_independent_review(after, inputs):
    directory = WORK/"test_02/fixes/fresh_component_review_v1"
    review = inputs.read(directory/"review.json")
    receipt = inputs.read(directory/"verification_receipt.json")
    require_independent_review(review, receipt)
    for name in ("REVIEW.md", "review.json", "executed_review.py"):
        path = (directory/name).resolve()
        digest = sha(path)
        if receipt["artifact_sha256"].get(name) != digest:
            raise ValueError("Independent component review artifact changed: " + name)
        inputs.hashes[str(path)] = digest
    for relative in ("protocol/plan.json", "run/inference.json", "run.executor.json", "run/perception_completion_catalog.json",
                     "bound_reference_diagnostics/component_reference_metrics.json", "analysis/technical_analysis.json"):
        path = after["root"]/relative
        if review["input_sha256"].get(str(path)) != inputs.hashes[str(path)]:
            raise ValueError("Independent component review is not bound to final fresh inputs: " + relative)
    return review, directory/"REVIEW.md"


class Inputs:
    def __init__(self):
        self.hashes = {}
    def read(self, path):
        path = Path(path).resolve()
        value = json.loads(path.read_text())
        self.hashes[str(path)] = sha(path)
        return value
    def prose(self, path):
        path = Path(path).resolve()
        value = path.read_text()
        self.hashes[str(path)] = sha(path)
        return absolute_markdown(value, path)
    def unchanged(self):
        if any(sha(path) != digest for path, digest in self.hashes.items()):
            raise ValueError("A consumed report/evidence input changed during consolidation")


def load_arm(root, inputs):
    root = Path(root).resolve(strict=True)
    info = inputs.read(root/"run/inference.json")
    executor = inputs.read(root/"run.executor.json")
    require_finished_documents(info, executor)
    if executor["worker_report_sha256"] != inputs.hashes[str(root/"run/inference.json")]:
        raise ValueError("Worker completion report no longer matches genuine parent binding")
    plan_path = root/"protocol/plan.json"
    plan = inputs.read(plan_path)
    if executor["plan_sha256"] != inputs.hashes[str(plan_path)]:
        raise ValueError("Executed plan changed")
    receipt = info["perception_cache_catalog"]
    catalogue_path = root/"run"/receipt["path"]
    catalogue = inputs.read(catalogue_path)
    if (inputs.hashes[str(catalogue_path)] != receipt["sha256"] or catalogue.get("frame_count") != N
        or catalogue.get("source_sha256") != SOURCE_SHA or catalogue.get("proxy_sha256") != info["proxy_sha256"]):
        raise ValueError("Source/proxy-bound completion catalogue changed")
    diagnostic = inputs.read(root/"all_reference_diagnostics_completion.json")
    matrix_path = Path(diagnostic["report"]).with_suffix(".json").resolve()
    matrix = inputs.read(matrix_path)
    components = inputs.read(root/"bound_reference_diagnostics/component_reference_metrics.json")
    rows = inputs.read(root/"bound_reference_diagnostics/reference_row_comparisons.json")
    analysis = inputs.read(root/"analysis/technical_analysis.json")
    if (matrix.get("status") != "completed_evidence_matrix" or matrix.get("test") != 2
        or Path(matrix["artifact_root"]).resolve() != root or matrix["provenance"]["source_sha256"] != SOURCE_SHA
        or components.get("all_annotation_files_accounted_for") is not True or components.get("annotations_modified") is not False
        or set(components["interval_reference_comparisons"]) != REFS or set(rows) != REFS
        or analysis.get("inputs_unchanged_after_analysis") is not True or analysis.get("source_sha256") != SOURCE_SHA):
        raise ValueError("Completed source-bound Test2 all-annotation matrix required")
    for path, digest in matrix["input_sha256"].items():
        # Recheck compact consumed evidence; do not replay models or rehash full
        # raw caches/media already verified by their genuine parent catalogue.
        p = Path(path)
        if p.suffix in {".json", ".md", ".yaml", ".yml", ".csv"} and p.stat().st_size <= 16_000_000:
            if sha(p) != digest:
                raise ValueError("Matrix input changed: " + str(p))
    return {"root": root, "info": info, "executor": executor, "plan": plan,
            "diagnostics": diagnostic, "matrix": matrix, "matrix_path": matrix_path,
            "components": components, "rows": rows, "analysis": analysis}


def load_bundle(artifact_root, inputs):
    root = Path(artifact_root).resolve(strict=True)
    # Final receipts are checked FIRST. No report directory is created while a
    # worker is running or only improved_completion (pre-matrix) exists.
    final = inputs.read(root/"improved_v1/improved_completion.json")
    diagnostics = inputs.read(root/"improved_v1/all_reference_diagnostics_completion.json")
    verification = inputs.read(root/"improved_v1/artifact_verification.json")
    comparison = inputs.read(root/"improved_v1/before_after_comparison.json")
    require_final_receipts(final, diagnostics, verification, comparison)
    before, after = load_arm(root/"baseline_v1", inputs), load_arm(root/"improved_v1", inputs)
    if (Path(comparison["baseline_source"]).resolve() != before["root"]
        or Path(comparison["fresh_postfix_source"]).resolve() != after["root"]
        or model_identity(before["analysis"]) != model_identity(after["analysis"])
        or before["plan"]["profile_source_sha256"] != after["plan"]["profile_source_sha256"]):
        raise ValueError("Before/after source/model/profile identities differ from comparison receipts")
    full_comparison = inputs.read(after["root"]/"before_after_component_matrix_comparison.json")
    if (full_comparison["baseline_matrix_sha256"] != sha(before["matrix_path"])
        or full_comparison["fresh_postfix_matrix_sha256"] != sha(after["matrix_path"])):
        raise ValueError("Complete component-matrix comparison receipt changed")
    for section, arms in full_comparison["sections"].items():
        if arms["baseline"] != before["matrix"][section] or arms["fresh_postfix"] != after["matrix"][section]:
            raise ValueError("Compared component section disagrees with preserved matrix: " + section)
    for name in REFS:
        record = comparison["interval_references"][name]
        if (record["baseline"] != before["matrix"]["interval_references"][name]["metrics"]
            or record["fresh_postfix"] != after["matrix"]["interval_references"][name]["metrics"]):
            raise ValueError("Reference metric comparison is not bound to saved matrix")
    fix = inputs.read(after["root"]/"applied_fix_receipt.json")
    for raw, values in fix["production_files"].items():
        path = Path(raw).resolve()
        if sha(path) != values["after_sha256"] or after["plan"]["source_files_sha256"].get(str(path)) != values["after_sha256"]:
            raise ValueError("Current/executed repair source no longer matches applied receipt")
        inputs.hashes[str(path)] = values["after_sha256"]
    for item in [{"path": fix["test_file"], "sha256": fix["test_sha256"]}, *fix["test_logs"]]:
        path = Path(item["path"]).resolve()
        if sha(path) != item["sha256"]:
            raise ValueError("Applied-fix regression source/log changed: " + str(path))
        inputs.hashes[str(path)] = item["sha256"]
    semantic_root = root/"test1_semantic_regression_v1"
    semantic_completion = inputs.read(semantic_root/"completion.json")
    semantic = inputs.read(semantic_root/"semantic_regression_metrics.json")
    if (semantic_completion.get("status") != "completed_controlled_semantic_regression"
        or semantic_completion.get("new_neural_inference") is not False or semantic.get("new_neural_inference") is not False
        or semantic.get("frames") != 17268 or semantic.get("original_inputs_annotations_cache_unchanged") is not True
        or semantic_completion["artifact_sha256"]["semantic_regression_metrics.json"] != sha(semantic_root/"semantic_regression_metrics.json")):
        raise ValueError("Completed preserved Test1 fixed-perception semantic regression required")
    for path, digest in inputs.hashes.items():
        p = Path(path)
        if after["root"] in p.parents:
            relative = str(p.relative_to(after["root"]))
            expected = verification.get("artifacts_sha256", {}).get(relative)
            if expected is not None and expected != digest:
                raise ValueError("Post-fix final artifact catalogue disagrees: " + relative)
    if verification["report_sha256"].get("matrix.json") != sha(after["matrix_path"]):
        raise ValueError("Final published improved matrix catalogue mismatch")
    return {"root": root, "before": before, "after": after, "comparison": comparison,
            "fix": fix, "test1": semantic, "test1_root": semantic_root, "final": final}


def racket_semantics(path):
    counts = Counter({"withheld_unique_owner_frames": 0, "raw_candidate_preserved": 0,
                      "cross_owner_face_witness": 0, "duplicate_owner_frame_records": 0})
    policies, reasons, keys = Counter(), Counter(), set()
    with Path(path).open() as stream:
        for line in stream:
            event = json.loads(line)
            if event["type"] != "racket_observation_ambiguity" or event.get("status") == "retracted":
                continue
            p = event["payload"]
            key = (p.get("frame_idx"), p.get("owner_track_id"), p.get("racket_source_frame"))
            if key in keys:
                counts["duplicate_owner_frame_records"] += 1
                continue
            keys.add(key)
            counts["withheld_unique_owner_frames"] += 1
            counts["raw_candidate_preserved"] += p.get("raw_candidate_preserved") is True
            counts["cross_owner_face_witness"] += any(w.get("track_id") != p.get("owner_track_id") for w in p.get("face_witnesses", []))
            policies[str(p.get("policy"))] += 1
            reasons[str(p.get("reason"))] += 1
    return {"counts": dict(counts), "policy_counts": dict(policies), "reason_counts": dict(reasons),
            "scope": "Unique nonretracted append-only owner/frame ambiguity records; not all raw geometry rows",
            "interpretation": "Semantic equipment abstention, not physical negative racket/contact labels; no raw-count subtraction used"}


def interval_text(row, prefix):
    a, b = row.get(prefix+"_start_frame"), row.get(prefix+"_end_frame")
    if a is None or b is None:
        return "Unavailable"
    return f"[{a},{b})f /{a/30:.6f}–{b/30:.6f}s"


def row_error(row, stem):
    return "/".join(fmt(row.get(key)) for key in (stem+"_frame_error", stem+"_frame_absolute_error", stem+"_time_error_sec", stem+"_time_absolute_error_sec"))


def reference_sections(lines, bundle):
    results, per_rows = {}, {}
    for name in sorted(REFS):
        old = bundle["before"]["matrix"]["interval_references"][name]
        new = bundle["after"]["matrix"]["interval_references"][name]
        if old["role"] != new["role"] or old["metrics"]["matching_policy"] != new["metrics"]["matching_policy"]:
            raise ValueError("Reference role or matching policy changed")
        lines += ["### " + name, "", "Role: " + old["role"] + ". Scores describe this reference population only."]
        fields = {k: old["metrics"][k] for k in ("detection", "overlap", "boundary_and_duration_errors", "boundary_tolerances")}
        post = {k: new["metrics"][k] for k in fields}
        scores = comparisons(fields, post)
        table(lines, ["Every saved aggregate/tolerance metric", "Baseline", "Fresh post-fix", "After−before"], scores)
        rows = paired_rows(bundle["before"]["rows"][name], bundle["after"]["rows"][name])
        per_rows[name] = rows
        lines += ["Original-row alignment below uses reference_data_row, not prediction ordinal. Frames/timestamps are half open. "
                  "Error cells are signed frames /absolute frames /signed seconds /absolute seconds. Missing matches remain unavailable."]
        table(lines, ["Original row", "Reference interval", "Baseline pred ID /interval", "Post-fix pred ID /interval", "Status before→after", "IoU before→after", "Start error before→after", "End error before→after", "Duration GT /before /after s", "Duration error before→after s"],
            ((r["reference_data_row"], interval_text(r["baseline"], "gt"),
              str(r["baseline"].get("pred_rally"))+" /"+interval_text(r["baseline"], "pred"),
              str(r["fresh_postfix"].get("pred_rally"))+" /"+interval_text(r["fresh_postfix"], "pred"),
              r["baseline"]["matching_status"]+"→"+r["fresh_postfix"]["matching_status"],
              fmt(r["baseline"].get("interval_iou"))+"→"+fmt(r["fresh_postfix"].get("interval_iou")),
              row_error(r["baseline"], "start")+"→"+row_error(r["fresh_postfix"], "start"),
              row_error(r["baseline"], "end")+"→"+row_error(r["fresh_postfix"], "end"),
              "/".join(fmt(v) for v in (r["baseline"].get("gt_duration_sec"),r["baseline"].get("pred_duration_sec"),r["fresh_postfix"].get("pred_duration_sec"))),
              fmt(r["baseline"].get("duration_error_sec"))+" /abs "+fmt(r["baseline"].get("duration_absolute_error_sec"))+"→"+
              fmt(r["fresh_postfix"].get("duration_error_sec"))+" /abs "+fmt(r["fresh_postfix"].get("duration_absolute_error_sec"))) for r in rows))
        if name in {"Test2_Full.csv", "win_predictions.csv"}:
            label_fields = ("win_point_player", "win_reason", "ball_types", "lose_reason", "roundscore_A", "roundscore_B") if name == "Test2_Full.csv" else (
                "winner", "loser", "win_reason", "reason_src", "fault_side", "fault_src", "cnn_class", "cnn_conf", "cnn_oob", "cnn_hn", "cnn_wbl", "score_Player A", "score_Player B")
            lines += ["All supplied non-timing labels are preserved below. They are reference annotations, not verified current athlete identities or current winner predictions. "
                      "Row-level outcome/class accuracy remains unavailable: current outputs lack the verified identity and compatible reviewed outcome/stroke-label contract."]
            table(lines, ["Original row", *label_fields],
                  ((r["reference_data_row"], *(r["source_annotation"].get(k) for k in label_fields)) for r in rows))
        table(lines, ["Arm", "Missed original reference IDs"], ((label, ", ".join(map(str, ref["metrics"]["missed_gt_rallies"])) or "None") for label, ref in (("Baseline",old),("Fresh post-fix",new))))
        table(lines, ["Arm", "Extra prediction ID", "Start/end frames", "Start/end seconds"],
              ((label,p["pred_rally"],f"[{p['start_frame']},{p['end_frame']})",f"{p['start']:.6f}–{p['end']:.6f}")
               for label,ref in (("Baseline",old),("Fresh post-fix",new)) for p in ref["metrics"]["unmatched_predictions"]))
        results[name] = {"role": old["role"], "baseline": compact(old["metrics"]),
                         "fresh_postfix": compact(new["metrics"]), "all_saved_metric_comparisons": scores}
    return results, per_rows


def build(artifact_root, output):
    output = Path(output).resolve()
    json_path = output.with_suffix(".json")
    if output.suffix != ".md" or output.exists() or json_path.exists():
        raise ValueError("Require NEW .md and sibling .json paths; previous records are immutable")
    root = Path(artifact_root).resolve()
    if any((root/arm) in output.parents for arm in ("baseline_v1", "improved_v1", "test1_semantic_regression_v1", "test2_semantic_regression_v1")):
        raise ValueError("Report cannot modify immutable inference/regression artifact directories")
    inputs = Inputs()
    data = load_bundle(root, inputs)
    independent_review, independent_review_path = load_independent_review(data["after"], inputs)
    before, after = data["before"]["matrix"], data["after"]["matrix"]
    lines = ["# Test Video 2 — consolidated ground-truth-driven evaluation and improvement", "",
      "Both Test2 arms are genuine complete fresh pipeline runs. Test1's new regression reuses immutable perception and is **not fresh neural inference**. "
      "Original Part2 files and historical benchmarks remain separate and unchanged; this is a per-video result, not a ten-video aggregate.", "",
      "Supplied human-origin coarse labels, generated support predictions and source-reviewed diagnostic evidence are distinguished below. "
      "Unavailable accuracy is never converted to zero. Counts, execution success and regression tests do not establish physical sporting correctness. "
      "Displayed numbers use up to10 significant digits; sibling JSON and linked original metrics preserve full numeric precision.", "",
      "## Outcome and evidence scope"]
    summary = []
    for arm,m in (("Baseline",before),("Fresh post-fix",after)):
        r=m["interval_references"]["Test2_Full_rally.csv"]["metrics"]
        summary.append((arm,r["detection"]["true_positives"],r["detection"]["false_positives"],r["detection"]["false_negatives"],
                        r["detection"]["precision"],r["detection"]["recall"],r["detection"]["f1"],r["overlap"]["mean_iou"]))
    table(lines,["Fresh Test2 arm","TP","FP","FN","Precision","Recall","F1","Mean IoU"],summary)
    lines += ["The implemented change is **racket_anatomical_alias_abstention_v1**: retain raw equipment geometry, but withhold its semantic racket cue when it aliases fresh facial landmarks. "
              "It does not retrain models, establish racket/contact ground truth, resolve torso/background aliases or manufacture identities, points or winners.", "",
              "## Complete three-reference before/after matrix and every original row", "",
              "Matching is unchanged: IoU≥0.5 maximum cardinality, then total IoU with the existing boundary-distance tie term. "
              "IoU/boundary/duration statistics condition on matched pairs; TP/FP/FN retain every missed and extra interval."]
    reference_metrics, row_comparisons = reference_sections(lines, data)
    lines += ["## Component, point, court, outcome and product comparisons", "",
              "Point and trajectory distances are disagreement with legacy generated outputs after source/coordinate binding, not physical localization accuracy. "
              "Anonymous slot assignment is not stable athlete identity; no bounding-box IoU is invented. The court diagnostic concerns the declared source frame and corner semantics only."]
    section_results = {}
    for section,title in (("point_diagnostics","Generated player/shuttle point diagnostics"),("court_diagnostic","Single-frame court reference"),
            ("component_coverage","Actual per-stage cache coverage"),("event_coverage","Contact/stroke, class and abstention coverage"),
            ("track_coverage","Position/tracking export coverage"),("outcome_and_stroke_coverage","Winner and stroke output coverage"),
            ("ocr_coverage","Broadcast observations"),("downstream","Actual analytics, heatmaps and highlights")):
        a,b=before[section],after[section]
        if section=="court_diagnostic":
            wanted={"reference_frame","reference_sha256","current_content_epoch","current_calibration_state","coordinate_binding_status","metric","prerequisite"}
            a,b=({k:v for k,v in x.items()if k in wanted}for x in(a,b))
        rows=comparisons(a,b);section_results[section]=rows
        lines += ["### "+title]
        table(lines,["Metric /observed meaning","Baseline","Fresh post-fix","After−before"],rows)
    stage_maps = [{r["stage"]: r for r in matrix["stage_status"]} for matrix in (before, after)]
    table(lines, ["Actual stage", "Baseline status /count", "Fresh post-fix status /count"],
          ((name, str(stage_maps[0].get(name, {}).get("status"))+" /"+fmt(stage_maps[0].get(name, {}).get("observed_count")),
            str(stage_maps[1].get(name, {}).get("status"))+" /"+fmt(stage_maps[1].get(name, {}).get("observed_count")))
           for name in sorted(set(stage_maps[0]) | set(stage_maps[1]))))
    def abstention_rates(matrix):
        counts = matrix["outcome_and_stroke_coverage"]["stroke_label_counts"]
        total = sum(counts.values())
        rallies = matrix["outcome_and_stroke_coverage"]["predicted_rallies"]
        return {"stroke_total": total, "unknown_stroke_rate": counts.get("unknown",0)/total if total else None,
                "unknown_winner_rate": matrix["outcome_and_stroke_coverage"]["unknown_winner_outputs"]/rallies if rallies else None}
    table(lines, ["Explicit abstention denominator/rate", "Baseline", "Fresh post-fix", "After−before"],
          comparisons(abstention_rates(before), abstention_rates(after)))
    table(lines,["Unavailable metric family","Baseline status","Post-fix status","Missing independent labels /contract"],
          ((name,before["unavailable_metrics"][name]["status"],after["unavailable_metrics"][name]["status"],after["unavailable_metrics"][name]["prerequisite"])
           for name in sorted(set(before["unavailable_metrics"])|set(after["unavailable_metrics"]))))
    lines += ["Unknown winner/score identity is preserved. An empty accepted score sequence is not a verified0–0. "
              "Anonymous raw floor positions are not named-player heatmap accuracy. Highlight counts are heuristic selections; relevance remains unvalidated, and rendered clips are reported separately.",
              "## Raw racket observations versus semantic admission"]
    semantic_racket={}
    for label,arm in(("baseline",data["before"]),("fresh_postfix",data["after"])):
        path=arm["root"]/"run/events.jsonl";semantic_racket[label]=racket_semantics(path);inputs.hashes[str(path)]=sha(path)
    table(lines,["Semantic-equipment diagnostic","Baseline","Fresh post-fix","After−before"],comparisons(semantic_racket["baseline"],semantic_racket["fresh_postfix"]))
    lines += ["Raw current-source racket rows are reported above independently from semantic abstention records. "
              "Withheld owner/frame counters alone do not justify subtraction from all raw geometry. The independent fresh review below verifies the exact owner/frame mapping before reporting remaining semantic candidates. "
              "A real racket overlapping a face can lose this equipment cue; absent/stale/low-confidence face evidence does not create an anatomical alias.",
              "## Fix, tests and risks"]
    table(lines,["Applied repair receipt field","Value"],flatten({k:v for k,v in data["fix"].items()if k not in {"production_files","test_logs"}}).items())
    table(lines,["Production file","Baseline SHA256","Executed/current post-fix SHA256"],
          ((name,v.get("before_sha256"),v["after_sha256"])for name,v in data["fix"]["production_files"].items()))
    table(lines,["Regression log","SHA256"],((link(v["path"]),v["sha256"])for v in data["fix"]["test_logs"]))
    lines += ["The initial applied receipt predates fresh evaluation; its pending flags describe integration time. "
              "Final completion/comparison receipts verified by this builder supersede those pending flags. "
              "Contact scores, provisional hitters, class labels, local-max suppression and highlights can change even when rally intervals do not. "
              "Neither fewer equipment cues nor lower unknown rate is automatically higher accuracy.", "",
              "## Test1 preservation: controlled fixed-perception semantic regression"]
    test1=data["test1"]
    lines += ["All17268 Test1 frames were replayed on unchanged recorded perception. This preserves the original model/cache population; "
              "it is not a fresh Test1 neural run. Actual chunk-cadence feedback and interval comparisons are reported separately."]
    table(lines,["Test1 scope/gate","Value"],flatten({k:test1.get(k)for k in("status","scope","frames","new_neural_inference","all_interval_metrics_equal","original_inputs_annotations_cache_unchanged","full_pipeline_preservation_scope")}).items())
    feedback={k:v for k,v in test1["perception_schedule_feedback"].items()if k not in("frontier_comparisons","baseline_terminal_record","candidate_terminal_record","baseline_flush_calls","candidate_flush_calls","step_state_differing_frames")}
    table(lines,["Test1 next-chunk feedback diagnostic","Value"],flatten(feedback).items())
    for name,ref in test1["all_reference_comparisons"].items():
        lines += ["### Test1 reference: "+name]
        fields=("detection","overlap","boundary_and_duration_errors","boundary_tolerances")
        table(lines,["Saved metric","Before fix","Fixed-perception semantic replay","Delta"],
              comparisons({k:ref["baseline_metrics"][k]for k in fields},{k:ref["semantic_replay_metrics"][k]for k in fields}))
    table(lines,["Test1 semantic output","Before","After semantic replay","Delta"],comparisons(test1["baseline_event_summary"],test1["semantic_replay_event_summary"]))
    effect_path=WORK/"test_02/fixes/semantic_effect_review.md"
    if effect_path.exists():
        lines += ["## Source-bound semantic side effects and contact-NMS risk", "",
                  "The following independent event review concerns controlled semantic replays; any Test2 cached-replay reporting failure remains separate from the completed fresh Test2 arm above.",
                  inputs.prose(effect_path)]
    lines += ["## Implementation, model/checkpoint identity, configuration and resources"]
    table(lines,["Reproducibility field","Baseline","Fresh post-fix","Delta"],comparisons(
        {k:v for k,v in before["provenance"].items()if k not in{"configuration","environment","git_status_at_freeze","models_verified"}},
        {k:v for k,v in after["provenance"].items()if k not in{"configuration","environment","git_status_at_freeze","models_verified"}}))
    models=model_identity(data["after"]["analysis"])
    table(lines,["Verified actual model artifact","SHA256 /status"],flatten(models).items())
    table(lines,["Explicit executed configuration","Baseline","Fresh post-fix","Delta"],comparisons(before["provenance"]["configuration"],after["provenance"]["configuration"]))
    table(lines,["Runtime packages/device declarations","Baseline","Fresh post-fix","Delta"],comparisons(before["provenance"]["environment"],after["provenance"]["environment"]))
    table(lines,["Measured resource /stage latency scope","Baseline","Fresh post-fix","Delta"],comparisons(before["runtime_resources"],after["runtime_resources"]))
    table(lines,["Direct completed worker measurement","Baseline","Fresh post-fix","Delta"],comparisons(
        {"worker_elapsed_s":data["before"]["info"].get("elapsed_s"),"parent_elapsed_s":data["before"]["executor"].get("elapsed_s"),"worker_runtime_scope":data["before"]["info"].get("runtime_scope"),
         "physical_gpu_index":data["before"]["executor"].get("physical_gpu_index"),"allocated_gpu_uuid":data["before"]["executor"].get("allocated_gpu_uuid")},
        {"worker_elapsed_s":data["after"]["info"].get("elapsed_s"),"parent_elapsed_s":data["after"]["executor"].get("elapsed_s"),"worker_runtime_scope":data["after"]["info"].get("runtime_scope"),
         "physical_gpu_index":data["after"]["executor"].get("physical_gpu_index"),"allocated_gpu_uuid":data["after"]["executor"].get("allocated_gpu_uuid")}))
    lines += ["The same physical GPU assignment does not isolate CPU, RAM, I/O or background training. "
              "Standalone CPU diagnostic probes shared the host during baseline execution. Stage timers may overlap; sums are not exclusive end-to-end time. "
              "Model loading/pure-neural throughput remain unavailable where not instrumented. Raw runtime changes are not a controlled speedup claim.",
              "## Annotation schemas, complete coverage and quality"]
    inventory=inputs.read(WORK/"test_02/annotations/annotation_inventory.json")
    if len(inventory["files"])!=7:
        raise ValueError("All seven original Test2 annotation files required")
    table(lines,["Original annotation","Bytes","Data rows","SHA256"],
          ((Path(f["path"]).name,f["bytes"],f.get("data_rows"),f["sha256"])for f in inventory["files"]))
    lines += ["## Ranked diagnosis and remaining improvement priorities", "",
              "1. **Confirmed correctness repair, evaluated above:** anatomical ellipse aliases previously entered semantic racket evidence. "
              "The narrow admission repair withholds facial aliases while preserving raw geometry. Neither cache execution nor the generated filled-ball files establish its physical precision/recall.",
              "2. **Confirmed baseline perception/continuity limitations:** background-official admission at6492 and propagated-box failures at355/25521 survive favorable aggregate player-point agreement. "
              "Their first incorrect detector/tracker/admission update remains unresolved; no fitted distance cutoff was introduced. The baseline also missed actual source/player-layout edit11346; its G69 split follows a22-frame raw-decoder gap, end publication and reacquisition beyond the existing merge window. "
              "These mechanisms are source/cache/trace-bound; neither a blanket scene reset nor a merge-threshold change has demonstrated safe improvement. Inspect the negative walking/retrieval controls before changing temporal policy.",
              "3. **Confirmed product coverage limits:** verified athlete identity, contact attribution, winners and accepted scoring remain dependent on missing roster/identity/outcome evidence. "
              "Unknowns and empty named-player analytics/heatmaps must remain visible. Torso/background racket aliases and ambiguous shuttle branches remain outside the narrow facial policy.",
              "4. **Annotation ambiguity rather than established code defects:** anonymous player slots are not permanent athletes; historical scoreboard columns differ from current-game scores; coarse boundaries can include preparation/retrieval. "
              "Generated winners and filled shuttle positions are diagnostic agreement targets. Duplicate ball files and out-of-canvas positions must not increase the independent sample population.",
              "5. **Rejected alternatives:** forcing full-corner OCR did not resolve the actual readout gap and removed a correct9/12 countercontrol. "
              "Lowering short-rally duration/evidence gates would admit a walking control. No Test2-fitted threshold, brand blacklist, synthesized track or guessed winner was adopted.", "",
              "Priorities above describe observed failure mechanisms and missing evidence; proposed future changes require independent labels, source review, preserved before/after metrics and Test1 regression checks. "
              "Detailed baseline cases and the separate fresh post-fix measurements follow."]
    embedded=[]
    docs=[("Annotation meaning and data-quality assessment","test_02/annotations/annotation_mapping.md"),
          ("Baseline component failure evidence","test_02/diagnostics/racket_false_positive_review/DIAGNOSIS.md"),
          ("Source-bound player population and propagation outliers","test_02/diagnostics/player_outlier_review/REPORT.md"),
          ("Preserved baseline temporal root causes and priorities","test_02/diagnostics/temporal_root_cause/REPORT.md"),
          ("Every baseline significant case and reference comparison","test_02/diagnostics/temporal_root_cause/case_register.md"),
          ("Completed baseline scene, OCR and synchronized evidence","test_02/diagnostics/current_scene_and_ocr_review/REVIEW.md"),
          ("Rejected ROI alternative and numerical-recognition limits","test_02/diagnostics/current_scene_and_ocr_review/ROI_ACQUISITION_REVIEW.md"),
          ("Identity availability and abstention","test_02/diagnostics/identity_availability.md"),
          ("Alternative model investigation and adoption limits","test_02/diagnostics/racket_false_positive_review/alternative_models.md")]
    for title,relative in docs:
        path=WORK/relative
        if not path.is_file():
            raise ValueError("Required diagnosis report missing: "+str(path))
        lines += ["## "+title,"", "Preserved diagnosis scope: baseline/source investigation; proposal/pending language within this embedded record is historical. "
                  "Executed post-fix outcomes are the fresh comparison above. Original record: "+link(path)+".","",inputs.prose(path)]
        embedded.append(str(path.resolve()))
    lines += ["## Independent fresh component review", "",
              "The following review inspects the actual completed fresh post-fix Test2 worker, full raw observation population and saved component diagnostics. "
              "Its component-review completion originally preceded the enclosing orchestration's final report receipt; this consolidated report independently requires both that final receipt and the review's own artifact/unsupported-metric/link verification. "
              "Fresh Test2 neural inference is distinct from the Test1 fixed-perception semantic regression. Baseline visual outlier/scene diagnoses remain scoped to their source-bound evidence; exact fresh/baseline cache agreement, where independently established here, supports transferring those observations without inventing new ground truth. "
              "Original review: "+link(independent_review_path)+".", "", inputs.prose(independent_review_path)]
    embedded.append(str(independent_review_path.resolve()))
    lines += ["## Fresh post-fix significant cases and baseline association", "",
              "These are the new run's actual significant cases, not inherited physical labels. Match IDs are reference-local; extra prediction ordinals can change after contact/segmentation changes."]
    table(lines,["Post-fix case","Status","Reference interval","Actual predicted interval","Exact new synchronized case evidence"],
          ((r["case_id"],r["matching_status"],str((r.get("gt_start_frame"),r.get("gt_end_frame"))),
            str((r.get("pred_start_frame"),r.get("pred_end_frame"))),link(data["after"]["root"]/"visual_failure_package"/r["case_json"]))for r in after["failure_cases"]))
    lines += ["Baseline39-case diagnosis remains preserved above; every post-fix case and all unmatched intervals are also retained. "
              "A changed metric does not by itself adjudicate a reference omission, preparation boundary, physical contact or winner.",
              "## Evidence index, preservation and reproducibility"]
    for label,arm in(("Baseline",data["before"]),("Fresh post-fix",data["after"])):
        table(lines,[label+" retained evidence","Location"],((key,link(path))for key,path in arm["matrix"]["evidence_paths"].items()))
    table(lines,["Comparison /regression receipt","Location"],[("Fresh before/after",link(data["after"]["root"]/"before_after_comparison.json")),
          ("Complete matrix comparison",link(data["after"]["root"]/"before_after_component_matrix_comparison.json")),
          ("Fresh final artifact verification",link(data["after"]["root"]/"artifact_verification.json")),
          ("Test1 semantic regression",link(data["test1_root"]/"semantic_regression_metrics.json")),
          ("Original source pairing",link(data["before"]["root"]/"input_pairing.json"))])
    lines += ["No raw video, proxy, annotation, model, baseline or previous report is deleted or modified by this builder. "
              "Test3 is not started. Video cleanup requires the root's separate final artifact verification and retention decision.", ""]
    payload={"schema":"test2-consolidated-before-after:v1","status":"completed_consolidated_report","test":2,
       "source_sha256":SOURCE_SHA,"test2_scope":"Two full fresh neural pipeline arms; same models/profile, documented source repair", 
       "test1_scope":"Controlled full-timeline semantic regression on fixed perception; NOT fresh neural inference",
       "interval_references":reference_metrics,"all_original_reference_row_comparisons":row_comparisons,
       "component_scalar_comparisons":section_results,"semantic_racket_admission":semantic_racket,
       "independent_fresh_component_review":compact(independent_review),
       "test1_semantic_summary":compact({k:v for k,v in test1.items()if k not in{"all_reference_comparisons","source_intervention","parity_vs_original"}}),
       "fix":compact(data["fix"]),"fresh_completion":data["final"],"embedded_reports":embedded,
       "input_sha256":inputs.hashes,"builder_sha256":sha(Path(__file__)),"new_inference_performed":False,
       "pipeline_modified":False,"prior_records_overwritten":False,"physical_accuracy_gain_claimed":False}
    rendered="\n".join(lines)
    if max(map(len,rendered.splitlines()),default=0)>12000:
        raise ValueError("Oversized report cell/line; raw arrays must be linked rather than embedded")
    inputs.unchanged()
    output.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation preserves immutable report versions and prevents races.
    with json_path.open("x")as stream:
        json.dump(payload,stream,indent=2,allow_nan=False);stream.write("\n")
    with output.open("x")as stream:
        stream.write(rendered)
    return {"markdown":str(output),"json":str(json_path),"reference_families":len(reference_metrics),
            "original_rows":sum(map(len,row_comparisons.values())),"bytes":len(rendered.encode())}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root",type=Path,default=ROOT.parent/"ground-truth-validation-artifacts-20261110/test_02",
                        help="Parent containing baseline_v1, improved_v1 and test1_semantic_regression_v1")
    parser.add_argument("--output",type=Path,default=WORK/"reports/test_02_consolidated_v1.md")
    args=parser.parse_args()
    print(json.dumps(build(args.artifact_root,args.output),indent=2))


if __name__=="__main__":
    main()
