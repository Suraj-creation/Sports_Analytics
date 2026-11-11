"""Build an immutable compact Test2 matrix from completed, guarded evidence.

No inference, source edits, annotation edits, original database access or prior
report overwrites. Missing accuracy labels remain unavailable, not zero.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from evaluation.ground_truth_validation.orchestration.evaluate_test02_components import (  # noqa: E402
    MEDIA,
    TEST2_SHA,
    compact,
    read,
    sha,
)
from research.pipeline_repair_run_analysis import load_analysis_input  # noqa: E402

REFERENCES = {"Test2_Full.csv", "Test2_Full_rally.csv", "win_predictions.csv"}


def scalar_fields(value, prefix=""):
    """Flatten aggregate dictionaries/tolerance records; never print an array."""
    if isinstance(value, dict):
        for key, item in value.items():
            yield from scalar_fields(item, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from scalar_fields(item, f"{prefix}.{index}")
    else:
        yield prefix, value


def cell(value):
    if isinstance(value, (dict, list, tuple)):
        raise ValueError("Raw containers must never be rendered into Markdown cells")
    if value is None:
        return "unavailable"
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(lines, headers, records):
    lines += ["", "| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines.extend("| " + " | ".join(cell(v) for v in row) + " |" for row in records)
    lines.append("")


def link(path, label=None):
    path = Path(path)
    return f"[{label or path.name}]({path})"


def require_completed(artifact_root):
    """Reject absent/failed/mismatched completion before report publication."""
    root = artifact_root.resolve(strict=True)
    completions = [p for p in (root / "baseline_completion.json", root / "improved_completion.json") if p.is_file()]
    if len(completions) != 1:
        raise ValueError("One explicit completed Test2 baseline/improved receipt is required")
    completion = read(completions[0])
    if (
        completion.get("status")
        not in {
            "completed_fresh_Test2_baseline_and_diagnostics",
            "completed_fresh_Test2_improved_and_diagnostics",
        }
        or completion.get("frames") != MEDIA[-1]
        or completion.get("annotations_unchanged") is not True
    ):
        raise ValueError("Test2 artifact completion failed or is incomplete")
    run = root / "run"
    bound = load_analysis_input(run, None)
    if bound["completion_mode"] != "normal_completed_worker" or bound["source_sha256"] != TEST2_SHA:
        raise ValueError("Matrix requires completed fresh exact Test2 source")
    if tuple(bound["media"][key] for key in ("width", "height", "fps_num", "fps_den", "n_frames")) != MEDIA:
        raise ValueError("Matrix source timeline differs from Test2 contract")
    return root, completions[0], bound


def summarize_downstream(analytics, individual, estimated, highlights, outcomes, heatmaps=None):
    result = {
        "rallies_official": analytics.get("rallies"),
        "rallies_unofficial": analytics.get("unofficial_rallies"),
        "active_play_s": analytics.get("active_play_s"),
        "unofficial_play_s": analytics.get("unofficial_play_s"),
        "shot_accounting": analytics.get("shot_accounting"),
        "avg_rally_shots": analytics.get("avg_rally_shots"),
        "longest_rally_shots": analytics.get("longest_rally_shots"),
        "named_player_analytics_count": len(analytics.get("players", {})),
        "momentum_entries": len(analytics.get("momentum", [])),
        "score_timeline_entries": len(analytics.get("score_timeline", [])),
        "individual_available": individual.get("available"),
        "individual_match_format": individual.get("match_format"),
        "individual_participants": len(individual.get("participants", [])),
        "individual_teams": len(individual.get("teams", [])),
        "individual_accounting": individual.get("accounting"),
        "individual_unattributed_event_count": len(individual.get("unattributed_event_ids", [])),
        "estimated_individual_available": estimated.get("available"),
        "highlight_count": len(highlights.get("highlights", [])),
        "highlight_check_count": len(highlights.get("checks", [])),
        "highlight_clips_rendered": highlights.get("clip_rendering_performed"),
        "highlight_relevance_accuracy": None,
        "heatmap_accuracy": None,
        "heatmap_export_available": heatmaps is not None,
        "heatmap_grid_count": heatmaps.get("grid_count") if heatmaps is not None else None,
        "heatmap_limitation": (
            "No independently reviewed spatial-density labels; anonymous motion is not named-player ground truth"
        ),
    }
    records = outcomes.get("rallies", [])
    result["outcome_record_count"] = len(records)
    result["outcome_records_with_score_available"] = sum(r.get("score_available") is True for r in records)
    result["estimated_scopes"] = {}
    for scope in ("official", "all_linked"):
        data = estimated.get(scope, {})
        profile = estimated.get("episode_profiles", {}).get(scope, {})
        result["estimated_scopes"][scope] = {
            "accounting": data.get("accounting"),
            "participant_count": len(data.get("participants", [])),
            "unresolved_event_count": len(data.get("unresolved_event_ids", [])),
            "unresolved_reason_counts": dict(collections.Counter(data.get("unresolved_reasons", {}).values())),
            "anonymous_episode_count": len(profile.get("episodes", [])),
            "detector_run_counts": profile.get("detector_run_counts"),
        }
    if heatmaps is not None:
        result["heatmaps"] = compact_heatmaps(heatmaps)
    return result


def compact_heatmaps(value):
    """Keep exported heatmap metadata/counts but no grid or frame arrays."""
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key in {"values", "samples", "points", "frames", "input_sha256"}:
                result[key + "_count"] = len(item) if isinstance(item, (list, dict)) else None
            else:
                result[key] = compact_heatmaps(item)
        return result
    if isinstance(value, list):
        if all(isinstance(item, dict) for item in value):
            return [compact_heatmaps(item) for item in value]
        return {"entry_count": len(value)}
    return value


def runtime_stages(components, inference, downstream):
    counts = components["actual_cache_component_coverage"]["counts"]
    events = components["event_coverage"]["live_counts"]
    return [
        {
            "stage": "ingestion",
            "status": "completed full canonical source",
            "observed_count": inference["frames_processed"],
        },
        {
            "stage": "court calibration",
            "status": "calibration events; validity separately recorded",
            "observed_count": events.get("calibration", 0),
        },
        {
            "stage": "player detection",
            "status": "recorded detector execution frames",
            "observed_count": counts.get("detector_executed_frames", 0),
        },
        {
            "stage": "player tracking",
            "status": "stored person rows; physical identity accuracy unavailable",
            "observed_count": counts.get("person_rows", 0),
        },
        {
            "stage": "pose",
            "status": "pose rows with current-frame source stamps",
            "observed_count": counts.get("pose_current_source_rows", 0),
        },
        {
            "stage": "shuttle",
            "status": "raw decoded observations, before temporal association",
            "observed_count": counts.get("raw_shuttle_present", 0),
        },
        {
            "stage": "racket",
            "status": "racket rows with current-frame source stamps",
            "observed_count": counts.get("racket_current_source_rows", 0),
        },
        {
            "stage": "contact",
            "status": "emitted events; zero emissions do not prove stage did not execute",
            "observed_count": events.get("contact", 0),
        },
        {
            "stage": "stroke",
            "status": "emitted classifications; unknown/attribution counts separate",
            "observed_count": events.get("stroke", 0),
        },
        {"stage": "rally", "status": "live exported rally-end events", "observed_count": events.get("rally_end", 0)},
        {
            "stage": "outcome",
            "status": "known-winner rally outputs; unverified identities remain unknown",
            "observed_count": components["outcome_and_stroke_coverage"]["known_winner_outputs"],
        },
        {
            "stage": "scoring",
            "status": "canonical accepted point events, not raw OCR readings",
            "observed_count": events.get("point", 0),
        },
        {
            "stage": "broadcast OCR",
            "status": "observations, not accepted outcomes or labelled accuracy",
            "observed_count": events.get("broadcast_score", 0),
        },
        {
            "stage": "player analytics",
            "status": "named-player analytics exports",
            "observed_count": downstream["named_player_analytics_count"],
        },
        {
            "stage": "highlights",
            "status": "canonical heuristic selections, relevance unvalidated",
            "observed_count": downstream["highlight_count"],
        },
        {
            "stage": "heatmaps",
            "status": "export metadata available"
            if downstream["heatmap_export_available"]
            else "not present in canonical downstream export",
            "observed_count": downstream["heatmap_grid_count"],
        },
    ]


def build(artifact_root, output):
    output = output.resolve()
    if output.exists():
        raise ValueError("Report output must be new; previous matrices are immutable")
    root, completion_path, bound = require_completed(artifact_root)
    if output == root or (root / "run") in output.parents:
        raise ValueError("Report must not modify the immutable original run")
    components_dir = root / "bound_reference_diagnostics"
    if not (components_dir / "component_reference_metrics.json").is_file():
        components_dir = root / "all_reference_components"
    files = {
        "completion": completion_path,
        "components": components_dir / "component_reference_metrics.json",
        "reference_rows": components_dir / "reference_row_comparisons.json",
        "analysis": root / "analysis/technical_analysis.json",
        "inference": root / "run/inference.json",
        "plan": root / "protocol/plan.json",
        "environment": root / "environment.json",
        "timestamps": root / "timestamps/timestamp_audit.json",
        "export_receipt": root / "downstream_exports/export_receipt.json",
        "analytics": root / "downstream_exports/analytics.json",
        "individual": root / "downstream_exports/individual_analytics.json",
        "estimated": root / "downstream_exports/estimated_individual_analytics.json",
        "highlights": root / "downstream_exports/highlights.json",
        "outcomes": root / "downstream_exports/rally_outcome_records.json",
        "scoring": root / "downstream_exports/scoring_outcome_evidence.json",
        "failure_cases": root / "visual_failure_package/failure_case_index.json",
        "failure_manifest": root / "visual_failure_package/manifest.json",
        "replay": root / "diagnostic_replay/parity_vs_fresh.json",
    }
    data = {name: read(path) for name, path in files.items()}
    input_hashes = {str(path): sha(path) for path in files.values()}
    c, inference, analysis = data["components"], data["inference"], data["analysis"]
    if (
        c.get("status") != "completed_readonly_component_reference_diagnostics"
        or c.get("test") != 2
        or c.get("source_sha256") != TEST2_SHA
        or Path(c.get("run", "")).resolve() != (root / "run").resolve()
    ):
        raise ValueError("Component matrix is not completed Test2 evidence")
    if c.get("all_annotation_files_accounted_for") is not True or c.get("annotations_modified") is not False:
        raise ValueError("Annotation completeness/preservation gate failed")
    if set(c["interval_reference_comparisons"]) != REFERENCES:
        raise ValueError("All three separately interpreted Test2 interval references are required")
    if (
        analysis.get("source_sha256") != TEST2_SHA
        or analysis.get("inputs_unchanged_after_analysis") is not True
        or Path(analysis.get("run", "")).resolve() != (root / "run").resolve()
    ):
        raise ValueError("Technical analysis is not source-bound unchanged Test2 evidence")
    timestamps = data["timestamps"]
    if (
        timestamps.get("source_sha256") != TEST2_SHA
        or timestamps.get("frames_decoded") != MEDIA[-1]
        or timestamps.get("source_proxy_full_rational_pts_equal") is not True
    ):
        raise ValueError("Full Test2 source/proxy timestamp equality is not verified")
    receipt = data["export_receipt"]
    if (
        receipt.get("status") != "completed"
        or receipt.get("original_artifacts_unchanged") is not True
        or receipt.get("source_completion_sha256") != sha(files["inference"])
        or Path(receipt.get("source_run", "")).resolve() != (root / "run").resolve()
    ):
        raise ValueError("Downstream exports are not bound to completed unchanged inference")
    for name, digest in receipt.get("output_sha256", {}).items():
        if sha(root / "downstream_exports" / name) != digest:
            raise ValueError("Downstream export output hash changed: " + name)
    heatmap_path = root / "heatmap_exports/heatmaps.json"
    if not heatmap_path.is_file():
        heatmap_path = root / "downstream_exports/heatmaps.json"
    heatmaps = read(heatmap_path) if heatmap_path.is_file() else None
    if heatmaps is not None:
        files["heatmaps"] = heatmap_path
        input_hashes[str(heatmap_path)] = sha(heatmap_path)
        if heatmap_path.parent.name == "heatmap_exports":
            heatmap_receipt_path = heatmap_path.parent / "export_receipt.json"
            heatmap_receipt = read(heatmap_receipt_path)
            if (
                heatmap_receipt.get("status") != "completed"
                or heatmap_receipt.get("original_and_detached_artifacts_unchanged") is not True
                or heatmap_receipt.get("source_completion_sha256") != sha(files["inference"])
                or heatmap_receipt.get("heatmaps_sha256") != sha(heatmap_path)
                or Path(heatmap_receipt.get("source_run", "")).resolve() != (root / "run").resolve()
            ):
                raise ValueError("Heatmap export is not bound to unchanged exact Test2 run")
            files["heatmap_receipt"] = heatmap_receipt_path
            input_hashes[str(heatmap_receipt_path)] = sha(heatmap_receipt_path)
    downstream = summarize_downstream(
        data["analytics"], data["individual"], data["estimated"], data["highlights"], data["outcomes"], heatmaps
    )
    references = c["interval_reference_comparisons"]
    point = compact(c["point_diagnostics"])
    # Full per-frame/outlier lists are already preserved in component evidence.
    for key in ("largest_shuttle_disagreements", "reference_shuttle_out_of_image_frames"):
        point.pop(key, None)
    provenance = {
        "source_sha256": TEST2_SHA,
        "proxy_sha256": inference.get("proxy_sha256"),
        "pipeline_commit": data["plan"].get("code_commit"),
        "git_status_at_freeze": data["plan"].get("git_status"),
        "profile_source": data["plan"].get("profile_source"),
        "profile_source_sha256": data["plan"].get("profile_source_sha256"),
        "profile_canonical_sha256": analysis.get("profile_canonical_sha256"),
        "source_file_count": len(data["plan"].get("source_files_sha256", {})),
        "media": bound["media"],
        "execution_backends": inference.get("execution_backends"),
        "models_verified": analysis.get("models_verified_during_analysis"),
        "selected_components": analysis.get("selected_components"),
        "configuration": inference.get("profile"),
        "environment": data["environment"],
    }
    stages = runtime_stages(c, inference, downstream)
    case_rows = [
        {
            k: case.get(k)
            for k in (
                "case_id",
                "gt_rally",
                "pred_rally",
                "matching_status",
                "gt_start_frame",
                "pred_start_frame",
                "gt_end_frame",
                "pred_end_frame",
                "causal_classification",
                "case_json",
            )
        }
        for case in data["failure_cases"]
    ]
    result = {
        "schema": "test2-completed-evaluation-matrix:v1",
        "status": "completed_evidence_matrix",
        "test": 2,
        "artifact_root": str(root),
        "component_evidence": str(components_dir),
        "interpretation": (
            "Reference agreement and diagnostic coverage; independent physical accuracy remains "
            "unavailable where labels are insufficient"
        ),
        "provenance": provenance,
        "interval_references": references,
        "point_diagnostics": point,
        "court_diagnostic": c["court_diagnostic"],
        "component_coverage": c["actual_cache_component_coverage"],
        "event_coverage": c["event_coverage"],
        "track_coverage": c["track_coverage"],
        "outcome_and_stroke_coverage": c["outcome_and_stroke_coverage"],
        "ocr_coverage": c["ocr_coverage"],
        "runtime_resources": c["runtime_resources"],
        "stage_status": stages,
        "downstream": downstream,
        "unavailable_metrics": c["unsupported_metrics"],
        "degraded_components": c["degraded_components"],
        "failure_cases": case_rows,
        "evidence_paths": {k: str(v) for k, v in files.items()},
        "input_sha256": input_hashes,
        "builder_sha256": sha(Path(__file__)),
        "inference_performed": False,
        "pipeline_changes_made_by_builder": False,
        "prior_reports_overwritten": False,
    }
    lines = [
        "# Test Video 2 — Complete Evaluation Matrix",
        "",
        (
            "This report records a completed fresh run of the current pipeline carrying Test1 fixes."
            " Earlier rally benchmarks and original Part2 data remain immutable. Each annotation "
            "family is evaluated separately. Generated references are agreement diagnostics, not "
            "independently adjudicated physical ground truth."
        ),
        "",
        (
            "A numeric zero describes an observed count or evaluated score. **Unavailable** means "
            "the necessary labels, identity, completeness or measurement contract is missing. "
            "Execution and unit-test success do not establish sporting accuracy."
        ),
        "",
        "## Reproducibility and implementation",
    ]
    table(
        lines,
        ["Item", "Value"],
        scalar_fields(
            {
                k: provenance[k]
                for k in (
                    "source_sha256",
                    "proxy_sha256",
                    "pipeline_commit",
                    "profile_source",
                    "profile_source_sha256",
                    "profile_canonical_sha256",
                    "source_file_count",
                    "media",
                )
            }
        ),
    )
    lines += [
        "The complete thresholds/profile are preserved in "
        + link(root / "protocol/profiles/experiment.yaml")
        + "; exact source snapshots, per-file hashes and dirty-source status are in "
        + link(files["plan"])
        + ". Runtime packages and devices are in "
        + link(files["environment"])
        + ".",
        "",
        "## Annotation coverage",
    ]
    table(
        lines,
        ["File", "Role", "Evaluation status"],
        ((r["file"], r["role"], r["status"]) for r in c["annotation_applicability"]),
    )
    lines += [
        "## Separate rally-reference agreement",
        "",
        (
            "Matching uses the preserved rally-boundaries-v1 policy: IoU eligibility ≥0.5; "
            "maximum-cardinality assignment, then total IoU and boundary-distance tie breaking; "
            "timestamp spans are half open. Boundary/duration/IoU scores condition on matched pairs;"
            " missed and extra proposals remain in detection metrics."
        ),
    ]
    table(
        lines,
        ["Reference", "TP", "FP", "FN", "Precision", "Recall", "F1", "Mean IoU"],
        (
            (
                name,
                *[
                    r["metrics"]["detection"][k]
                    for k in ("true_positives", "false_positives", "false_negatives", "precision", "recall", "f1")
                ],
                r["metrics"]["overlap"]["mean_iou"],
            )
            for name, r in references.items()
        ),
    )
    for name, reference in references.items():
        metrics = reference["metrics"]
        lines += [
            "### " + name,
            "",
            "Reference role: "
            + reference["role"]
            + ". Every original row and prediction match is preserved in "
            + link(files["reference_rows"])
            + ".",
        ]
        aggregates = {
            k: metrics[k] for k in ("detection", "overlap", "boundary_and_duration_errors", "boundary_tolerances")
        }
        table(lines, ["Aggregate metric", "Value"], scalar_fields(aggregates))
        table(lines, ["Missed reference ID"], ((identifier,) for identifier in metrics["missed_gt_rallies"]))
        table(
            lines,
            ["False-detection prediction ID", "Start frame", "End frame", "Start seconds", "End seconds"],
            (
                (row["pred_rally"], row["start_frame"], row["end_frame"], row["start"], row["end"])
                for row in metrics["unmatched_predictions"]
            ),
        )
        if reference.get("invalid_rows"):
            table(
                lines,
                ["Invalid source row", "Reason"],
                ((r["source_data_row"], r["reason"]) for r in reference["invalid_rows"]),
            )
    lines += [
        "## Source-bound generated-point and court diagnostics",
        "",
        (
            "Anonymous point assignment compares geometry without inventing athlete identity or "
            "bounding-box IoU. A source/frame/coordinate review certificate gates distance metrics. "
            "These distances remain disagreement with legacy generated outputs. The identical "
            "shuttle exports are counted once; out-of-image values remain flagged and are not "
            "clipped."
        ),
    ]
    point_summary = {k: v for k, v in point.items() if k not in {"coordinate_binding", "duplicate_shuttle_tables"}}
    table(lines, ["Diagnostic", "Value"], scalar_fields(point_summary))
    lines += ["Coordinate binding status: " + cell(point["coordinate_binding"]["status"]) + "."]
    table(
        lines,
        ["Court diagnostic", "Value"],
        scalar_fields(
            {
                k: v
                for k, v in c["court_diagnostic"].items()
                if k
                in {"reference_frame", "current_calibration_state", "current_content_epoch", "metric", "prerequisite"}
            }
        ),
    )
    lines += ["## Actual component execution and output coverage"]
    table(
        lines,
        ["Stage", "Evidence meaning", "Observed count"],
        ((r["stage"], r["status"], r["observed_count"]) for r in stages),
    )
    table(lines, ["Cache coverage metric", "Value"], scalar_fields(c["actual_cache_component_coverage"]))
    lines += ["## Contact, stroke, identity, outcome and scoring"]
    table(
        lines,
        ["Metric", "Value"],
        scalar_fields(
            {
                "event_coverage": c["event_coverage"],
                "outcome_and_stroke_coverage": c["outcome_and_stroke_coverage"],
                "track_coverage": c["track_coverage"],
            }
        ),
    )
    lines += [
        (
            "Named identities, anonymous tracks, raw broadcast OCR observations and canonical "
            "accepted points are distinct. Unknown outcomes are not assigned winners; an empty "
            "accepted score sequence is not verified 0–0."
        ),
        "",
        "## Downstream analytics, heatmaps and highlights",
    ]
    table(lines, ["Output", "Value"], scalar_fields(downstream))
    lines += [
        (
            "Canonical exports are linked below. Anonymous episode profiles and heuristic highlights"
            " remain diagnostic estimates. A missing heatmap export or identity-supported player "
            "output is recorded explicitly rather than counted as accurate."
        ),
        "",
        "## Runtime, resources, models and configuration",
    ]
    table(lines, ["Resource/stage metric", "Value"], scalar_fields(c["runtime_resources"]))
    table(
        lines,
        ["Model/backend/configuration", "Value"],
        scalar_fields({k: provenance[k] for k in ("execution_backends", "models_verified", "selected_components")}),
    )
    table(lines, ["Degraded component evidence", "Value"], scalar_fields(c["degraded_components"]))
    lines += [
        (
            "GPU peaks are sampled for the allocated worker/PID; CPU/RSS scopes and stage scopes may"
            " overlap. Worker throughput includes preparation, loading and postprocessing. Pure "
            "neural-only throughput remains unavailable."
        ),
        "",
        "## Unavailable accuracy metrics",
    ]
    table(
        lines,
        ["Metric", "Status", "Missing prerequisite"],
        ((k, v["status"], v["prerequisite"]) for k, v in c["unsupported_metrics"].items()),
    )
    lines += [
        "## Source-synchronized failure evidence",
        "",
        (
            "Cases originate from reference disagreement and diagnostic thresholds. Their presence "
            "does not itself establish a pipeline defect. Causal classifications require "
            "synchronized source review; annotations and generated references can also be wrong."
        ),
    ]
    table(
        lines,
        [
            "Case",
            "Reference ID",
            "Prediction ID",
            "Status",
            "Reference start",
            "Prediction start",
            "Reference end",
            "Prediction end",
            "Diagnosis",
        ],
        (
            (
                r["case_id"],
                r["gt_rally"],
                r["pred_rally"],
                r["matching_status"],
                r["gt_start_frame"],
                r["pred_start_frame"],
                r["gt_end_frame"],
                r["pred_end_frame"],
                r["causal_classification"],
            )
            for r in case_rows
        ),
    )
    lines += [
        "Interactive synchronized evidence: "
        + link(root / "visual_failure_package/index.html")
        + ". Full raw FSM/contact traces and replay-versus-fresh parity remain in "
        + link(root / "diagnostic_replay")
        + ".",
        "",
        "## Complete evidence references",
    ]
    lines.extend("- " + name + ": " + link(path) for name, path in files.items())
    lines += [
        "- per-frame point candidates: " + link(components_dir / "frame_point_candidates.jsonl"),
        "- full component details: " + link(components_dir / "component_raw_details.json"),
        "- immutable original predictions: " + link(root / "run/predicted_rallies.csv"),
        "",
        (
            "Test2 evaluation evidence is complete enough to build this matrix. The orchestrator "
            "must separately review diagnosis, validate justified fixes and regression results, and "
            "verify retained artifacts before cleanup or advancement to Test3."
        ),
        "",
    ]
    if any(sha(Path(path)) != digest for path, digest in input_hashes.items()):
        raise ValueError("Report input changed during generation")
    output.mkdir(parents=True)
    (output / "matrix.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (output / "matrix.md").write_text("\n".join(lines))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.artifact_root, args.output)
    print(json.dumps({"status": result["status"], "test": 2, "output": str(args.output)}))


if __name__ == "__main__":
    main()
