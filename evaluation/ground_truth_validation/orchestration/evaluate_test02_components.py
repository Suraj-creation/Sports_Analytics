"""Read-only, source-bound Test 2 diagnostics for a completed fresh pipeline run.

Historical generated CSVs are agreement references, never independent physical
ground truth. All original run, annotation and Test 1 files remain untouched.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from evaluation.ground_truth_validation.orchestration.evaluate_test01_components import (  # noqa: E402
    finite,
    pair_points,
    read,
    reference_comparison,
    rows,
    sha,
)
from research.pipeline_repair_run_analysis import (  # noqa: E402
    audit_frames,
    event_summary,
    load_analysis_input,
    load_chunks,
    ocr_summary,
    resource_summary,
    select_live_events,
    track_summary,
)
from research.test2_evaluation import distribution  # noqa: E402
from scripts.benchmarking.evaluate_rallies import read_csv  # noqa: E402

TEST2_SHA = "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"
MEDIA = (1280, 720, 30, 1, 29296)
EXPECTED_FILES = {
    "Test2_Full.csv",
    "Test2_Full_rally.csv",
    "win_predictions.csv",
    "Test2_Full_ball_filled.csv",
    "Test2_Full_Rev_ball_filled.csv",
    "player_detections.csv",
    "Test2_Full_court.json",
}
UNAVAILABLE = {
    "player_AP_mAP_IoU": (
        "Independently reviewed boxes and complete positive/negative coverage; supplied generated points are not boxes."
    ),
    "tracking_IDF1_HOTA_ID_switches_fragmentation": (
        "Reviewed persistent athlete identities, boxes and visibility; two generated detection slots"
        " are not persistent IDs."
    ),
    "pose_PCK_OKS": "Reviewed keypoints and joint visibility, skeleton convention and scale.",
    "shuttle_physical_localization_PR": (
        "Independent reviewed coordinates/visibility; filled model estimates do not identify interpolated frames."
    ),
    "racket_contact_PR_F1_temporal_error": (
        "Reviewed contact/racket times and negative windows, not rally-level labels."
    ),
    "stroke_per_class_PR_F1_confusion": (
        "Complete per-contact stroke taxonomy and labels; a single ball_types field per coarse rally is insufficient."
    ),
    "winner_outcome_accuracy_PR_F1_confusion": (
        "Verified symbolic Player A/B identity and source-bound adjudicated outcomes; win_predictions is generated."
    ),
    "score_sequence_accuracy": (
        "Reviewed broadcast identity, point alignment and score sequence, accounting for edited-video omissions."
    ),
    "highlight_quality": (
        "Reviewed highlight relevance/boundaries; rally overlap and execution are not relevance accuracy."
    ),
    "player_analytics_accuracy": "Reviewed participant identities and metric-specific physical movement/event labels.",
}


def compact(value):
    """Remove per-observation arrays from aggregate summaries, preserving counts."""
    if isinstance(value, dict):
        return {
            k: compact(v)
            for k, v in value.items()
            if k not in {"values", "scene_records", "readouts", "details", "resource_series", "raw_rows", "comparison"}
        }
    if isinstance(value, list):
        return [compact(v) for v in value]
    return value


def validate_dense_timeline(table, key, count):
    if [int(row[key]) for row in table] != list(range(count)):
        raise ValueError("Dense reference timeline differs from exact source frames; no filling/reindexing permitted")


def binding_status(binding, bound, hashes):
    if binding is None:
        return {
            "status": "unverified",
            "reason": (
                "No Test2 source/frame/coordinate review certificate supplied; candidates only, "
                "distance metrics unavailable"
            ),
        }
    expected = {
        "status": "source_and_coordinate_semantics_verified",
        "source_sha256": TEST2_SHA,
        "frame_size": [1280, 720],
        "fps_num": 30,
        "fps_den": 1,
    }
    for key, value in expected.items():
        if binding.get(key) != value or bound["source_sha256"] != TEST2_SHA:
            raise ValueError("Test2 coordinate certificate mismatch: " + key)
    reviewed = binding.get("reviewed_frames", [])
    if not reviewed or any(type(f) is not int or not 0 <= f < bound["media"]["n_frames"] for f in reviewed):
        raise ValueError("Coordinate review requires actual valid Test2 frame IDs")
    if not binding.get("reviewer_type") or not binding.get("evidence"):
        raise ValueError("Coordinate review requires reviewer and evidence")
    for evidence in binding["evidence"]:
        path = Path(evidence["path"])
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file() or sha(path) != evidence.get("sha256"):
            raise ValueError("Coordinate review evidence missing or hash changed")
    contracts = {
        "legacy_player_point": ("bbox_bottom_center", "player_detections.csv"),
        "legacy_shuttle_point": ("analysis_image_xy", "Test2_Full_ball_filled.csv"),
    }
    for key, (semantics, name) in contracts.items():
        if binding.get(key) is not None and (
            binding[key] != semantics or binding.get("reference_sha256", {}).get(name) != hashes[name]
        ):
            raise ValueError("Coordinate component/hash mismatch: " + key)
    corners = binding.get("court_corner_semantics")
    if corners is not None:
        if corners not in {"outer_singles_floor_corners", "outer_doubles_floor_corners"}:
            raise ValueError("Unknown court corner semantics")
        if binding.get("reference_sha256", {}).get("Test2_Full_court.json") != hashes["Test2_Full_court.json"]:
            raise ValueError("Court reference hash mismatch")
    return {
        "status": "diagnostic_coordinate_binding_declared",
        "certificate": binding,
        "independent_physical_accuracy": False,
        "limitation": "Source-bound agent diagnostic review does not create independently adjudicated labels",
    }


def court_diagnostic(court, frames, chunks, live, contract, reference_hash):
    target = court["frame_no"]
    if type(target) is not int or not 0 <= target < len(frames):
        raise ValueError("Court reference frame outside canonical source")
    if court["frame_size"] != {"width": 1280, "height": 720}:
        raise ValueError("Court reference coordinate dimensions differ")
    frame = frames[target]
    chunk = next(c for c in chunks if c["start"] <= target <= c["end"])
    court_id = chunk.get("cr")
    calibration = [
        e
        for e in live
        if e["type"] == "calibration" and e["frame_start"] <= target and e["payload"].get("cam_ref") == court_id
    ]
    result = {
        "reference_frame": target,
        "reference": court,
        "reference_sha256": reference_hash,
        "current_content_epoch": frame.get("ce"),
        "current_calibration_state": frame.get("cs"),
        "coordinate_binding_status": contract["status"],
        "metric": None,
        "prerequisite": "Source-bound explicit singles/doubles corner semantics and valid matching current calibration",
    }
    if not calibration or frame.get("g") is None or frame.get("cs") != "VALID" or frame.get("v") != "main":
        return result
    selected = max(calibration, key=lambda e: e.get("seq", 0))
    homography = np.asarray(frame["g"], float).reshape(3, 3) @ np.asarray(selected["payload"]["H"], float)
    world = np.array([[-3.05, 6.7, 1], [3.05, 6.7, 1], [3.05, -6.7, 1], [-3.05, -6.7, 1]], float)
    images = {}
    for name, factor in (("outer_doubles_floor_corners", 1), ("outer_singles_floor_corners", 5.18 / 6.1)):
        points = world.copy()
        points[:, 0] *= factor
        projected = (homography @ points.T).T
        if np.any(np.abs(projected[:, 2]) < 1e-12):
            return result
        image = projected[:, :2] / projected[:, 2:3]
        if not np.isfinite(image).all():
            return result
        images[name] = image
        result["current_candidate_" + name] = dict(zip(("TL", "TR", "BR", "BL"), image.tolist(), strict=True))
    result.update(
        calibration_event_id=selected["event_id"],
        calibration_source=selected["payload"].get("source"),
        calibration_method=selected["payload"].get("method"),
        cache_calibration_ref=court_id,
        current_effective_H=homography.tolist(),
    )
    semantics = contract.get("certificate", {}).get("court_corner_semantics")
    if contract["status"] == "diagnostic_coordinate_binding_declared" and semantics in images:
        distances = {
            name: float(np.linalg.norm(images[semantics][i] - np.asarray(court["corners"][name])))
            for i, name in enumerate(("TL", "TR", "BR", "BL"))
        }
        result["metric"] = {
            "classification": "single-frame manual-reference diagnostic disagreement, not all-frame physical accuracy",
            "declared_corner_semantics": semantics,
            "corner_error_px": distances,
            "mean_corner_error_px": float(np.mean(list(distances.values()))),
            "maximum_corner_error_px": max(distances.values()),
        }
    return result


def evaluate_components(run, output, completion_recovery=None, coordinate_binding=None):
    run, output = run.resolve(strict=True), output.resolve()
    if output.exists() or output == run or run in output.parents or output in run.parents:
        raise ValueError("Require new output outside immutable original run")
    session = read(run / "session.json")
    if session["source"].get("sha256") != TEST2_SHA:
        raise ValueError("Requires exact original Test2 source hash")
    # Completion/source/cache guards run before any annotation content is read.
    bound = load_analysis_input(run, completion_recovery)
    media = bound["media"]
    if (
        bound["source_sha256"] != TEST2_SHA
        or tuple(media[k] for k in ("width", "height", "fps_num", "fps_den", "n_frames")) != MEDIA
    ):
        raise ValueError("Test2 canonical source/time contract differs; explicit mapping required")
    n, fps = media["n_frames"], media["fps_num"] / media["fps_den"]
    annotations = ROOT / "Part2/dataset/Test2_Full"
    paths = sorted(p for p in annotations.iterdir() if p.is_file())
    if {p.name for p in paths} != EXPECTED_FILES:
        raise ValueError("Test2 annotation inventory changed; explicit schema review required")
    hashes = {p.name: sha(p) for p in paths}
    consumed = {str(p): sha(p) for p in bound["input_paths"]}
    consumed.update({str(p): hashes[p.name] for p in paths})
    consumed[str(run / "predicted_rallies.csv")] = sha(run / "predicted_rallies.csv")
    helpers = [
        Path(__file__).resolve(),
        ROOT / "evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py",
        ROOT / "research/pipeline_repair_run_analysis.py",
        ROOT / "scripts/benchmarking/evaluate_rallies.py",
        ROOT / "research/test2_evaluation.py",
    ]
    consumed.update({str(p): sha(p) for p in helpers})
    if coordinate_binding is not None:
        consumed[str(coordinate_binding)] = sha(coordinate_binding)
    chunks, frames = load_chunks(bound["cache_dir"], bound["cache_sha256"], consumed)
    coverage, _ = audit_frames(frames, n)
    predictions = read_csv(run / "predicted_rallies.csv", fps)
    events_path = bound["events_path"]
    consumed[str(events_path)] = sha(events_path)
    events = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
    live = select_live_events(events, session["session_id"])
    ends = sorted((e["frame_start"], e["frame_end"]) for e in live if e["type"] == "rally_end")
    if ends != [(r.start_frame, r.end_frame) for r in predictions]:
        raise ValueError("Prediction CSV differs from original live rally ledger")
    references, applicability, raw_references = {}, [], {}
    for path in paths:
        item = {"file": path.name, "sha256": hashes[path.name]}
        if path.suffix == ".csv":
            fields, table = rows(path)
            if "Start_Frame" in fields or "start_time" in fields:
                reference = reference_comparison(path, predictions, fps)
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
                validate_dense_timeline(table, "Frame", n)
                item.update(
                    status="generated_trajectory_diagnostic",
                    role="filled model estimate, not independent localization ground truth",
                )
            elif "player_1_x" in fields:
                validate_dense_timeline(table, "frame_no", n)
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
    contract = binding_status(read(coordinate_binding) if coordinate_binding else None, bound, hashes)
    for evidence in contract.get("certificate", {}).get("evidence", []):
        path = Path(evidence["path"])
        if not path.is_absolute():
            path = ROOT / path
        consumed[str(path)] = evidence["sha256"]
    bound_coords = contract["status"] == "diagnostic_coordinate_binding_declared"
    player_bound = bound_coords and contract["certificate"].get("legacy_player_point") == "bbox_bottom_center"
    shuttle_bound = bound_coords and contract["certificate"].get("legacy_shuttle_point") == "analysis_image_xy"
    _, shuttle = rows(annotations / "Test2_Full_ball_filled.csv")
    _, players = rows(annotations / "player_detections.csv")
    candidates, player_dist, fresh_dist, shuttle_dist, outliers = [], [], [], [], []
    presence, unmatched = collections.Counter(), collections.Counter()
    out_of_bounds = []
    for frame, s, p in zip(frames, shuttle, players, strict=True):
        fi = frame["f"]
        legacy = []
        for slot in (1, 2):
            x, y = finite(p[f"player_{slot}_x"]), finite(p[f"player_{slot}_y"])
            if x is not None and y is not None:
                legacy.append({"slot": slot, "xy": [x, y], "support": finite(p[f"player_{slot}_conf"])})
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
            "reference_confidence": finite(s.get("Confidence")),
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
                assignments = pair_points([q["xy"] for q in legacy], [q["xy"] for q in selected])
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
        "player_bottom_center_distance_px": compact(distribution(player_dist)) if player_bound else None,
        "fresh_detector_bottom_center_distance_px": compact(distribution(fresh_dist)) if player_bound else None,
        "shuttle_raw_distance_px_both_present": compact(distribution(shuttle_dist)) if shuttle_bound else None,
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
    court = court_diagnostic(
        read(annotations / "Test2_Full_court.json"), frames, chunks, live, contract, hashes["Test2_Full_court.json"]
    )
    event_report = event_summary(events, session["session_id"])
    tracks = track_summary(run, session["session_id"], frames, consumed)
    ocr = ocr_summary(chunks)
    parent_path, sample_path, stage_path = (
        run.with_suffix(".executor.json"),
        run.with_suffix(".gpu_process_samples.jsonl"),
        run / "stage_latency_samples.json",
    )
    for path in (parent_path, sample_path, stage_path):
        consumed[str(path)] = sha(path)
    resources = resource_summary(
        read(parent_path),
        [json.loads(line) for line in sample_path.read_text().splitlines() if line.strip()],
        read(stage_path),
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
        "interval_reference_comparisons": compact(references),
        "point_diagnostics": pointmetrics,
        "court_diagnostic": court,
        "unsupported_metrics": {
            k: {"value": None, "status": "unavailable", "prerequisite": v} for k, v in UNAVAILABLE.items()
        },
        "outcome_and_stroke_coverage": outcome,
        "event_coverage": compact(event_report),
        "actual_cache_component_coverage": compact(coverage),
        "track_coverage": compact(tracks),
        "ocr_coverage": compact(ocr),
        "runtime_resources": compact(resources),
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
        "helper_sha256": sha(Path(__file__)),
    }
    if any(sha(Path(p)) != digest for p, digest in consumed.items()):
        raise ValueError("Consumed input changed during evaluation")
    output.mkdir(parents=True)
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
    report.extend(f"- **{key}**: unavailable. Requires {value}" for key, value in UNAVAILABLE.items())
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
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--completion-recovery", type=Path)
    parser.add_argument("--coordinate-binding", type=Path)
    args = parser.parse_args()
    result = evaluate_components(args.run, args.output, args.completion_recovery, args.coordinate_binding)
    print(
        json.dumps(
            {
                "status": result["status"],
                "annotation_files": len(result["annotation_applicability"]),
                "coordinate_binding": result["point_diagnostics"]["coordinate_binding"]["status"],
            }
        )
    )


if __name__ == "__main__":
    main()
