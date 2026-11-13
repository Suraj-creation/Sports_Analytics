"""Manifest-declared, read-only component diagnostics for a native finished run.

No filename role inference, inference, replay, GT ingestion by workers, or edits
of original data. Generated references only establish diagnostic agreement.
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
    seconds,
    sha,
)
from evaluation.ground_truth_validation.orchestration.evaluate_test02_components import UNAVAILABLE  # noqa: E402
from research import pipeline_repair_run_analysis as analysis  # noqa: E402
from research import production_external_semantic_replay as replay  # noqa: E402
from research.pipeline_repair_completion import verify_models  # noqa: E402
from research.test2_evaluation import distribution  # noqa: E402
from scripts.benchmarking.evaluate_rallies import read_csv  # noqa: E402

ROLES = {"interval_reference", "dense_generated_players", "dense_generated_shuttle", "manual_court", "supporting"}
FORMATS = {
    "frames_seconds": {"Start_Frame", "End_Frame", "Start_Time_sec", "End_Time_sec", "Duration_sec"},
    "frames": {"start_frame", "end_frame"},
    "clock": {"start_time", "end_time"},
}


def require_new_output(output, protected):
    original = Path(output)
    if original.exists() or original.is_symlink():
        raise ValueError("Require NEW output; existing results and failed attempts are immutable")
    output = original.resolve()
    for path in protected:
        path = Path(path).resolve()
        if output == path or path in output.parents or output in path.parents:
            raise ValueError("Output overlaps an original input/run")
    return output


def validate_manifest(manifest):
    if manifest.get("schema") != "component-evaluation-manifest:v1":
        raise ValueError("Explicit supported manifest schema required")
    source = manifest["source"]
    digest = source["sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("Exact source SHA256 required")
    media = source["media"]
    if set(media) != {"width", "height", "fps_num", "fps_den", "n_frames"} or any(
        type(v) is not int or v <= 0 for v in media.values()
    ):
        raise ValueError("Positive exact canonical media integers required")
    if manifest.get("time_basis") != {
        "timeline": "canonical_cfr",
        "frame_origin": 0,
        "offset_seconds": 0,
        "interval_end": "exclusive",
    }:
        raise ValueError("Explicit zero-origin canonical time basis without offset required")
    if not Path(manifest["annotations"]["directory"]).is_absolute():
        raise ValueError("Original annotation directory must be explicit and absolute")
    files = manifest["annotations"]["files"]
    names = [entry["name"] for entry in files]
    if not files or len(set(names)) != len(names):
        raise ValueError("Every annotation must have one unique declaration")
    for entry in files:
        if Path(entry["name"]).name != entry["name"] or entry["name"] in {".", ".."}:
            raise ValueError("Annotation names must be immediate original files")
        if entry.get("role") not in ROLES or not entry.get("purpose") or not entry.get("ambiguity"):
            raise ValueError("Explicit reviewed role, purpose and ambiguity required; no filename inference")
        if len(entry.get("sha256", "")) != 64:
            raise ValueError("Annotation hash required")
        schema = entry["schema"]
        if schema.get("format") not in {"csv", "json"}:
            raise ValueError("Only explicitly reviewed CSV/JSON schemas supported")
        if schema["format"] == "csv":
            columns = schema["columns"]
            if len(set(columns)) != len(columns) or set(entry["field_eligibility"]) != set(columns):
                raise ValueError("Every CSV column needs explicit field eligibility")
            for field in entry["field_eligibility"].values():
                if (
                    not field.get("status")
                    or not field.get("reason")
                    or field.get("kind")
                    not in {"timing", "coordinate", "outcome", "stroke", "score", "identity", "other"}
                ):
                    raise ValueError("Column eligibility requires kind, status and ambiguity reason")
        elif not schema.get("top_level_keys") or set(entry.get("field_eligibility", {})) != set(
            schema["top_level_keys"]
        ):
            raise ValueError("Explicit JSON key schema and field eligibility required")
        if entry["role"] == "interval_reference" and (
            schema["format"] != "csv"
            or schema.get("interval_format") not in FORMATS
            or type(entry.get("partial_positive_only")) is not bool
            or not entry.get("reference_role")
        ):
            raise ValueError("Interval format, declared reference role and completeness policy required")
        if entry["role"] == "manual_court" and schema["format"] != "json":
            raise ValueError("Manual court requires a reviewed JSON schema")
        if entry["role"] in {"dense_generated_players", "dense_generated_shuttle"}:
            if schema["format"] != "csv" or schema.get("frame_column") not in schema["columns"]:
                raise ValueError("Dense generated reference requires declared frame column")
            if entry["role"] == "dense_generated_players":
                slots = schema.get("slots", [])
                if (
                    not slots
                    or len({s["id"] for s in slots}) != len(slots)
                    or any(s[k] not in schema["columns"] for s in slots for k in ("x", "y"))
                ):
                    raise ValueError("Distinct explicit anonymous point slots required")
            elif (
                any(schema.get(k) not in schema["columns"] for k in ("x", "y", "visibility"))
                or not schema.get("visible_values")
                or not schema.get("invisible_values")
                or set(schema["visible_values"]) & set(schema["invisible_values"])
            ):
                raise ValueError("Explicit shuttle coordinates/visibility convention required")
    return manifest


def native_completion(run):
    """Reject foreign-root guard imports before consuming any annotation labels."""
    run = Path(run).resolve(strict=True)
    if Path(analysis.ROOT).resolve() != ROOT or Path(replay.ROOT).resolve() != ROOT:
        raise ValueError("Guard helper imports differ from evaluator native root")
    parent = read(run.with_suffix(".executor.json"))
    command = parent.get("command", [])
    if command.count("--plan") != 1:
        raise ValueError("Actual original source-guarded worker plan required")
    plan_path = Path(command[command.index("--plan") + 1])
    plan = read(plan_path)
    sources = plan.get("source_files_sha256", {})
    if str(ROOT / "sports/badminton/src/bai_badminton/engine.py") not in sources or any(
        not Path(p).is_relative_to(ROOT) for p in sources
    ):
        raise ValueError("Recorded source root differs: execute this helper natively in that exact checkout")
    return analysis.load_analysis_input(run, None), plan_path, plan


def require_pairing(bound, source):
    """Canonical pairing is exact; descriptive worker metadata is preserved too."""
    if bound["source_sha256"] != source["sha256"] or any(
        bound["media"].get(key) != value for key, value in source["media"].items()
    ):
        raise ValueError("Manifest video/media pairing differs from completed run")


def inventory(manifest, consumed):
    folder = Path(manifest["annotations"]["directory"]).resolve(strict=True)
    declared = {entry["name"] for entry in manifest["annotations"]["files"]}
    actual = {p.name for p in folder.iterdir() if p.is_file()}
    if actual != declared or any(p.is_dir() for p in folder.iterdir()):
        raise ValueError("Annotation inventory differs; every original supporting file must be declared")
    for entry in manifest["annotations"]["files"]:
        path = folder / entry["name"]
        if sha(path) != entry["sha256"]:
            raise ValueError("Original annotation hash changed: " + entry["name"])
        consumed[str(path)] = entry["sha256"]
    return folder


def load_annotation(path, entry, media):
    schema = entry["schema"]
    if schema["format"] == "json":
        value = read(path)
        if not isinstance(value, dict) or set(value) != set(schema["top_level_keys"]):
            raise ValueError("JSON schema differs from declared original keys")
        return value
    columns, table = rows(path)
    if columns != schema["columns"] or any(None in row for row in table):
        raise ValueError("CSV columns differ from reviewed exact schema")
    if entry["role"].startswith("dense_generated_"):
        key, n = schema["frame_column"], media["n_frames"]
        if [int(row[key]) for row in table] != list(range(n)):
            raise ValueError("Dense timeline differs; no reindex/filling/time shift permitted")
        if schema.get("timestamp_column"):
            if schema["timestamp_column"] not in columns or schema.get("timestamp_format") not in {"seconds", "clock"}:
                raise ValueError("Dense timestamps require an explicit seconds/clock column convention")
            parser = seconds if schema["timestamp_format"] == "clock" else float
            fps = media["fps_num"] / media["fps_den"]
            if any(
                finite(parser(row[schema["timestamp_column"]])) is None
                or abs(parser(row[schema["timestamp_column"]]) - i / fps) > 1e-6
                for i, row in enumerate(table)
            ):
                raise ValueError("Dense timestamps differ from canonical frames")
    return table


def compare_intervals(path, entry, predictions, media):
    columns = set(entry["schema"]["columns"])
    actual = "frames_seconds" if "Start_Frame" in columns else "frames" if "start_frame" in columns else "clock"
    if actual != entry["schema"]["interval_format"] or not FORMATS[actual] <= columns:
        raise ValueError("Declared interval convention conflicts with original comparator schema")
    result = reference_comparison(
        path, predictions, media["fps_num"] / media["fps_den"], partial=entry["partial_positive_only"]
    )
    # The legacy helper uses names for role metadata only. Override that metadata
    # explicitly; completeness and numerical matching are independent arguments.
    result["role"] = entry["reference_role"]
    if any(r["gt_start_frame"] < 0 or r["gt_end_frame"] > media["n_frames"] for r in result["comparison"]):
        raise ValueError("Reference interval outside exact source extent")
    return result


def coordinate_contract(path, manifest, consumed):
    if path is None:
        return {"status": "unverified", "independent_physical_accuracy": False}
    path = Path(path).resolve(strict=True)
    certificate = read(path)
    source, media = manifest["source"], manifest["source"]["media"]
    expected = {
        "status": "source_and_coordinate_semantics_verified",
        "source_sha256": source["sha256"],
        "frame_size": [media["width"], media["height"]],
        "fps_num": media["fps_num"],
        "fps_den": media["fps_den"],
    }
    if (
        any(certificate.get(k) != v for k, v in expected.items())
        or not certificate.get("reviewer_type")
        or not certificate.get("evidence")
    ):
        raise ValueError("Coordinate certificate source/frame/schema mismatch")
    reviewed = certificate.get("reviewed_frames", [])
    if not reviewed or any(type(f) is not int or not 0 <= f < media["n_frames"] for f in reviewed):
        raise ValueError("Coordinate certificate reviewed frame population invalid")
    consumed[str(path)] = sha(path)
    for evidence in certificate["evidence"]:
        p = Path(evidence["path"])
        p = p if p.is_absolute() else ROOT / p
        if sha(p) != evidence["sha256"]:
            raise ValueError("Coordinate evidence hash changed")
        consumed[str(p)] = evidence["sha256"]
    return {
        "status": "diagnostic_coordinate_binding_declared",
        "certificate": certificate,
        "independent_physical_accuracy": False,
    }


def component_bound(entry, contract):
    cert = contract.get("certificate", {})
    key = {
        "dense_generated_players": ("legacy_player_point", "bbox_bottom_center"),
        "dense_generated_shuttle": ("legacy_shuttle_point", "analysis_image_xy"),
        "manual_court": ("court_corner_semantics", entry["schema"].get("corner_semantics")),
    }[entry["role"]]
    declared = cert.get(key[0])
    if declared is None:
        return False
    if declared != key[1] or cert.get("reference_sha256", {}).get(entry["name"]) != entry["sha256"]:
        raise ValueError("Coordinate reference semantics/hash mismatch")
    return True


def point_rows(entry, table, frames, media, bound):
    schema, distances, fresh, counts = entry["schema"], [], [], collections.Counter()
    output = []
    for frame, row in zip(frames, table, strict=True):
        index = frame["f"]
        item = {
            "frame": index,
            "raw_reference": row,
            "coordinate_status": "bound_generated_diagnostic" if bound else "unverified",
        }
        if entry["role"] == "dense_generated_players":
            reference = []
            for slot in schema["slots"]:
                x, y = finite(row[slot["x"]]), finite(row[slot["y"]])
                if x is None or y is None:
                    counts["missing_or_invalid_slot_coordinates"] += 1
                    continue
                inside = 0 <= x < media["width"] and 0 <= y < media["height"]
                counts["reference_points"] += 1
                counts["out_of_image_reference_points"] += not inside
                reference.append({"slot": slot["id"], "xy": [x, y], "in_image": inside})
            current = [
                {
                    "index": i,
                    "xy": [(p["b"][0] + p["b"][2]) / 2, p["b"][3]],
                    "detector_matched": p.get("dm"),
                    "track_id": p["t"],
                }
                for i, p in enumerate(frame["p"])
            ]
            counts["current_points"] += len(current)
            item.update(reference=reference, current=current)
            if bound:
                for label, selected, values in [
                    ("all_current", current, distances),
                    ("fresh_detector", [p for p in current if p["detector_matched"] is True], fresh),
                ]:
                    pairs = pair_points([p["xy"] for p in reference], [p["xy"] for p in selected])
                    for pair in pairs:
                        pair["reference_slot_name"] = reference[pair["reference_slot"] - 1]["slot"]
                        pair["current_index"] = selected[pair["current_index"]]["index"]
                    values.extend(p["distance_px"] for p in pairs)
                    counts[label + "_unmatched_reference"] += len(reference) - len(pairs)
                    counts[label + "_unmatched_current"] += len(selected) - len(pairs)
                    item[label + "_assignments"] = pairs
        else:
            marker = row[schema["visibility"]]
            visible = (
                True
                if marker in schema["visible_values"]
                else (False if marker in schema.get("invisible_values", []) else None)
            )
            x, y = finite(row[schema["x"]]), finite(row[schema["y"]])
            valid = visible is True and x is not None and y is not None
            reference = [x, y] if valid else None
            current = frame.get("s")
            counts[f"reference_visible={visible},current_raw_present={current is not None}"] += 1
            counts["visibility_unknown"] += visible is None
            counts["visible_invalid_numeric"] += visible is True and not valid
            inside = valid and 0 <= x < media["width"] and 0 <= y < media["height"]
            counts["out_of_image_reference_points"] += valid and not inside
            item.update(
                reference_xy=reference,
                reference_visible=visible,
                reference_in_image=inside if valid else None,
                current_raw_xy=current,
                invalid_numeric=visible is True and not valid,
            )
            if bound and reference is not None and current is not None:
                distance = float(np.linalg.norm(np.asarray(reference) - np.asarray(current)))
                distances.append(distance)
                item["distance_px"] = distance
        output.append(item)
    return {
        "classification": "generated-reference disagreement, NOT physical accuracy",
        "counts": dict(counts),
        "distance_px": aggregate(distribution(distances)) if bound else None,
        "fresh_detector_distance_px": aggregate(distribution(fresh))
        if bound and entry["role"] == "dense_generated_players"
        else None,
        "coordinate_bound": bound,
        "out_of_image_policy": "retained, flagged and never clipped/excluded",
    }, output


def deduplicate(entry, seen):
    """Byte-identical generated point tables are one population, preserving aliases."""
    key = (entry["role"], entry["sha256"])
    if key in seen:
        previous = seen[key]
        if previous["schema"] != entry["schema"]:
            raise ValueError("Byte-identical generated references have conflicting declared semantics")
        return previous["name"]
    seen[key] = entry
    return None


def aggregate(value):
    if isinstance(value, dict):
        return {
            k: aggregate(v)
            for k, v in value.items()
            if k not in {"values", "scene_records", "details", "readouts", "resource_series", "comparison", "raw_rows"}
        }
    if isinstance(value, list):
        return [aggregate(v) for v in value]
    return value


def court_result(entry, court, frames, chunks, live, media, bound):
    target = court["frame_no"]
    if (
        type(target) is not int
        or not 0 <= target < len(frames)
        or court["frame_size"] != {"width": media["width"], "height": media["height"]}
    ):
        raise ValueError("Manual court candidate frame/size mismatch")
    result = {
        "reference_frame": target,
        "coordinate_bound": bound,
        "metric": None,
        "classification": "single-frame manual candidate; not all-frame accuracy",
    }
    if not bound:
        return result
    semantics = entry["schema"]["corner_semantics"]
    if semantics not in {"outer_singles_floor_corners", "outer_doubles_floor_corners"}:
        raise ValueError("Explicit reviewed court corner semantics required")
    frame = frames[target]
    chunk = next(c for c in chunks if c["start"] <= target <= c["end"])
    candidates = [
        e
        for e in live
        if e["type"] == "calibration" and e["frame_start"] <= target and e["payload"].get("cam_ref") == chunk.get("cr")
    ]
    if not candidates or frame.get("g") is None or frame.get("cs") != "VALID" or frame.get("v") != "main":
        result["reason"] = "No compatible VALID current calibration"
        return result
    selected = max(candidates, key=lambda e: e.get("seq", 0))
    h = np.asarray(frame["g"]).reshape(3, 3) @ np.asarray(selected["payload"]["H"])
    half = 2.59 if semantics == "outer_singles_floor_corners" else 3.05
    world = np.array([[-half, 6.7, 1], [half, 6.7, 1], [half, -6.7, 1], [-half, -6.7, 1]])
    projected = (h @ world.T).T
    if np.any(np.abs(projected[:, 2]) < 1e-12):
        result["reason"] = "Singular projection"
        return result
    points = projected[:, :2] / projected[:, 2:3]
    reference = np.asarray([court["corners"][k] for k in ("TL", "TR", "BR", "BL")], float)
    if reference.shape != (4, 2) or not np.isfinite(reference).all() or not np.isfinite(points).all():
        raise ValueError("Invalid manual/current court coordinates")
    error = np.linalg.norm(points - reference, axis=1)
    result["metric"] = {
        "corner_error_px": dict(zip(("TL", "TR", "BR", "BL"), error.tolist(), strict=True)),
        "mean_corner_error_px": float(error.mean()),
        "maximum_corner_error_px": float(error.max()),
    }
    return result


def render_report(result):
    """Scalar aggregate tables only; observation arrays remain in linked evidence."""

    def cell(value):
        if value is None:
            return "unavailable"
        if isinstance(value, (list, dict, tuple)):
            raise ValueError("Raw arrays belong in evidence, not Markdown cells")
        return str(value).replace("|", "/").replace("\n", " ")

    lines = [
        "# Manifest-driven component evaluation",
        "",
        "Native complete fresh worker and original cache guards passed. Generated references measure agreement, "
        "not physical accuracy. Original data and predictions are unchanged.",
        "",
    ]

    def table(title, headers, records):
        lines.extend(["## " + title, "", "| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)])
        lines.extend("| " + " | ".join(cell(v) for v in record) + " |" for record in records)
        lines.append("")

    references = result["interval_reference_comparisons"]
    records = []
    for name, ref in references.items():
        m, d = ref["metrics"], ref["metrics"]["detection"]
        records.append(
            (
                name,
                ref["role"],
                d["true_positives"],
                d["false_positives"],
                d["false_negatives"],
                d["precision"],
                d["recall"],
                d["f1"],
                m["overlap"]["mean_iou"],
            )
        )
    table(
        "Interval reference agreement",
        ["Reference", "Declared role", "TP", "FP", "FN", "Precision", "Recall", "F1", "Mean IoU"],
        records,
    )
    for name, ref in references.items():
        metrics = ref["metrics"]
        table(
            name + " boundary and duration errors",
            ["Quantity", "MAE", "Median abs", "RMSE", "Max abs", "P90 abs", "Mean signed", "Median signed"],
            [
                (
                    key,
                    *[
                        value.get(k)
                        for k in [
                            "mae",
                            "median_absolute_error",
                            "rmse",
                            "max_absolute_error",
                            "p90_absolute_error",
                            "mean_signed_error",
                            "median_signed_error",
                        ]
                    ],
                )
                for key, value in metrics["boundary_and_duration_errors"].items()
            ],
        )
        table(
            name + " boundary tolerances",
            ["Boundary", "Frames", "Seconds", "Within", "Matched fraction", "All-GT fraction"],
            [
                (
                    side,
                    item["frames"],
                    item["seconds"],
                    item["within_count"],
                    item["matched_accuracy"],
                    item["all_gt_accuracy"],
                )
                for side, entries in metrics["boundary_tolerances"].items()
                for item in entries
            ],
        )
        overlap = metrics["overlap"]
        table(
            name + " overlap",
            ["Measure", "Value"],
            [(k, v) for k, v in overlap.items() if not isinstance(v, dict)]
            + [
                ("percent IoU strictly above " + key, value)
                for key, value in overlap.get("percent_strictly_exceeding", {}).items()
            ],
        )
        missed = metrics["missed_gt_rallies"]
        lines.append("Missed reference IDs: " + (", ".join(map(str, missed)) if missed else "none") + ".")
        table(
            name + " extra or unscored predictions",
            ["Prediction ID", "Start frame", "End frame", "Interpretation"],
            [
                (item["pred_rally"], item["start_frame"], item["end_frame"], label)
                for values, label in [
                    (metrics["unmatched_predictions"], "FP under complete reference"),
                    (ref.get("unscored_current_predictions", []), "Unscored partial-reference proposal; not FP"),
                ]
                for item in values
            ],
        )
        lines.append(metrics.get("conditional_metrics_note", "") + "\n")
    table(
        "Annotation coverage",
        ["File", "Declared role", "Purpose", "Ambiguity"],
        [(v["name"], v["role"], v["purpose"], v["ambiguity"]) for v in result["annotation_applicability"]],
    )
    table(
        "Generated point disagreement",
        ["Reference", "Population", "Bound", "Count", "Mean px", "Median px", "Min px", "Max px", "P90 px", "P95 px"],
        [
            (
                name,
                label,
                value["coordinate_bound"],
                *[(stat or {}).get(k) for k in ["count", "mean", "median", "minimum", "maximum", "p90", "p95"]],
            )
            for name, value in result["point_diagnostics"].items()
            for label, stat in [
                ("all current", value["distance_px"]),
                ("fresh detector", value["fresh_detector_distance_px"]),
            ]
        ],
    )
    table(
        "Point coverage and data quality",
        ["Reference", "Count meaning", "Count"],
        [
            (name, key, count)
            for name, value in result["point_diagnostics"].items()
            for key, count in value["counts"].items()
        ],
    )
    table(
        "Byte-identical dense-reference aliases",
        ["Duplicate", "Evaluated primary"],
        list(result["duplicate_generated_references"].items()),
    )
    table(
        "Single-frame court candidates",
        ["File", "Frame", "Bound", "Mean corner px", "Max corner px", "Limit"],
        [
            (
                name,
                value["reference_frame"],
                value["coordinate_bound"],
                (value["metric"] or {}).get("mean_corner_error_px"),
                (value["metric"] or {}).get("maximum_corner_error_px"),
                value.get("reason", value["classification"]),
            )
            for name, value in result["court_diagnostics"].items()
        ],
    )
    for title, counts in [
        ("Raw component coverage", result["actual_cache_component_coverage"]["counts"]),
        ("Track coverage", result["track_coverage"].get("counts", {})),
        ("Live event counts", result["event_coverage"]["live_counts"]),
    ]:
        table(title, ["Quantity", "Count"], list(counts.items()))
    outcomes = result["outcome_and_stroke_coverage"]
    table(
        "Outcome and score coverage",
        ["Quantity", "Value"],
        [(k, v) for k, v in outcomes.items() if not isinstance(v, dict)],
    )
    table("Predicted stroke counts", ["Predicted class", "Count"], list(outcomes["stroke_label_counts"].items()))
    resources = result["runtime_resources"]
    table(
        "Actual runtime and resources",
        ["Quantity", "Measured value"],
        [(k, v) for k, v in resources.items() if not isinstance(v, (dict, list))],
    )
    table(
        "Stage invocation timing (scopes can overlap)",
        ["Stage", "Calls", "Seconds", "P50 ms", "P95 ms"],
        [
            (name, *[value.get(k) for k in ["calls", "seconds", "p50_ms", "p95_ms"]])
            for name, value in resources.get("stage_latency", {}).items()
        ],
    )
    provenance = result["provenance"]
    table(
        "Verified actual model artifacts",
        ["Group", "Model", "SHA256", "Status"],
        [
            (group, name, value.get("sha256"), value.get("status", "verified"))
            for group, models in provenance["actual_verified_models"].items()
            for name, value in models.items()
        ],
    )
    table(
        "Actual worker backend declarations",
        ["Stage", "Requested", "Actual", "Device", "Dtype", "Fallback"],
        [
            (
                stage,
                value.get("requested_backend"),
                value.get("actual_backend", value.get("backend")),
                value.get("device"),
                value.get("dtype"),
                value.get("backend_fallback"),
            )
            for stage, value in provenance["actual_worker"].get("execution_backends", {}).items()
        ],
    )
    table(
        "Source and coordinate provenance",
        ["Quantity", "Value"],
        [
            ("Source SHA256", result["source_sha256"]),
            ("Native guard root", provenance["native_guard_root"]),
            ("Recorded pipeline commit", provenance["recorded_pipeline_commit"]),
            ("Coordinate review", result["coordinate_binding"]["status"]),
        ],
    )
    table(
        "Unavailable physical accuracy",
        ["Metric family", "Value", "Prerequisite"],
        [(key, value["value"], value["prerequisite"]) for key, value in result["unsupported_metrics"].items()],
    )
    lines += [
        "Full per-reference rows, original fields/eligibility and semantic field counts: "
        "[reference_raw_details.json](reference_raw_details.json). All scalar metrics and complete actual "
        "Worker/profile/backend/source provenance: "
        "[component_reference_metrics.json](component_reference_metrics.json). "
        "Detailed OCR/scene/events/tracks/resources: [component_raw_details.json](component_raw_details.json). "
        "Synchronized points are separate point_reference_XX.jsonl files.",
        "",
        "Execution, coverage and generated-reference agreement do not validate physical accuracy. "
        "Unavailable values remain null, not zero. Raw arrays are preserved outside this summary.",
        "",
    ]
    return "\n".join(lines)


def evaluate(run, manifest_path, output, certificate=None):
    manifest_path = Path(manifest_path).resolve(strict=True)
    manifest = validate_manifest(read(manifest_path))
    run = Path(run).resolve(strict=True)
    output = require_new_output(output, [run, manifest_path, manifest["annotations"]["directory"]])
    bound, plan_path, plan = native_completion(run)
    require_pairing(bound, manifest["source"])
    consumed = {str(p): sha(p) for p in bound["input_paths"]}
    consumed.update({str(manifest_path): sha(manifest_path), str(plan_path): sha(plan_path)})
    for module in [
        sys.modules[__name__],
        analysis,
        replay,
        sys.modules[reference_comparison.__module__],
        sys.modules[pair_points.__module__],
        sys.modules[distribution.__module__],
        sys.modules[verify_models.__module__],
        sys.modules[read_csv.__module__],
    ]:
        p = Path(module.__file__).resolve()
        consumed[str(p)] = sha(p)
    unsupported_helper = Path(__file__).with_name("evaluate_test02_components.py")
    consumed[str(unsupported_helper)] = sha(unsupported_helper)
    folder = inventory(manifest, consumed)
    chunks, frames = analysis.load_chunks(bound["cache_dir"], bound["cache_sha256"], consumed)
    coverage, _ = analysis.audit_frames(frames, bound["media"]["n_frames"])
    events_path = Path(bound["events_path"])
    consumed[str(events_path)] = sha(events_path)
    events = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
    live = analysis.select_live_events(events, bound["session_id"])
    predictions_path = run / "predicted_rallies.csv"
    consumed[str(predictions_path)] = sha(predictions_path)
    predictions = read_csv(predictions_path, bound["media"]["fps_num"] / bound["media"]["fps_den"])
    if sorted((e["frame_start"], e["frame_end"]) for e in live if e["type"] == "rally_end") != [
        (p.start_frame, p.end_frame) for p in predictions
    ]:
        raise ValueError("Prediction CSV differs from live original rally ledger")
    declared_binding = manifest.get("coordinate_binding")
    if certificate is not None and declared_binding is None:
        raise ValueError("Declare coordinate certificate path and hash in the manifest")
    if declared_binding is not None:
        declared_path = Path(declared_binding["path"]).resolve(strict=True)
        if certificate is not None and Path(certificate).resolve() != declared_path:
            raise ValueError("CLI coordinate certificate differs from manifest")
        if sha(declared_path) != declared_binding["sha256"]:
            raise ValueError("Coordinate certificate hash changed")
        certificate = declared_path
    contract = coordinate_contract(certificate, manifest, consumed)
    references, points, courts, raw, point_details, duplicates, seen = {}, {}, {}, {}, {}, {}, {}
    for entry in manifest["annotations"]["files"]:
        name, role = entry["name"], entry["role"]
        table = load_annotation(folder / name, entry, bound["media"])
        raw[name] = {
            "role": role,
            "purpose": entry["purpose"],
            "ambiguity": entry["ambiguity"],
            "field_eligibility": entry["field_eligibility"],
            "original_rows": table,
        }
        if entry["schema"]["format"] == "csv":
            raw[name]["semantic_field_counts"] = {
                field: dict(collections.Counter(row[field] for row in table))
                for field, declaration in entry["field_eligibility"].items()
                if declaration["kind"] in {"outcome", "stroke", "score", "identity"}
            }
        if role == "interval_reference":
            reference = compare_intervals(folder / name, entry, predictions, bound["media"])
            raw[name].update(comparison=reference.pop("comparison"), parsed_raw_rows=reference.pop("raw_rows"))
            references[name] = reference
        elif role.startswith("dense_generated_"):
            previous = deduplicate(entry, seen)
            if previous is not None:
                duplicates[name] = previous
                continue
            metric, detail = point_rows(entry, table, frames, bound["media"], component_bound(entry, contract))
            points[name], point_details[name] = metric, detail
        elif role == "manual_court":
            courts[name] = court_result(
                entry, table, frames, chunks, live, bound["media"], component_bound(entry, contract)
            )
    event_report = analysis.event_summary(events, bound["session_id"])
    parent_path, samples_path, latency_path = (
        run.with_suffix(".executor.json"),
        run.with_suffix(".gpu_process_samples.jsonl"),
        run / "stage_latency_samples.json",
    )
    for p in (parent_path, samples_path, latency_path):
        consumed[str(p)] = sha(p)
    resources = analysis.resource_summary(
        read(parent_path),
        [json.loads(line) for line in samples_path.read_text().splitlines() if line.strip()],
        read(latency_path),
        len(frames),
        bound["worker_info"],
    )
    declarations = {"loaded_models": {}, "runtimes": {}}
    for chunk in chunks:
        for label, value in [("loaded_models", chunk["models"]), ("runtimes", chunk["ci"].get("runtimes", {}))]:
            declarations[label][analysis.canonical(value)] = value
    models = verify_models(run, declarations, bound["profile"])
    for group in models.values():
        for model in group.values():
            for key in ("source_path", "staged_path", "path"):
                if key in model:
                    consumed[model[key]] = sha(model[key])
    tracks = analysis.track_summary(run, bound["session_id"], frames, consumed)
    result = {
        "status": "completed_manifest_component_diagnostics",
        "source_sha256": bound["source_sha256"],
        "media": bound["media"],
        "manifest_sha256": sha(manifest_path),
        "all_annotation_files_accounted_for": True,
        "interval_reference_comparisons": references,
        "point_diagnostics": points,
        "court_diagnostics": courts,
        "duplicate_generated_references": duplicates,
        "annotation_applicability": [
            {k: e[k] for k in ("name", "role", "purpose", "ambiguity", "field_eligibility")}
            for e in manifest["annotations"]["files"]
        ],
        "coordinate_binding": contract,
        "unsupported_metrics": {
            k: {"value": None, "status": "unavailable", "prerequisite": v} for k, v in UNAVAILABLE.items()
        },
        "actual_cache_component_coverage": aggregate(coverage),
        "event_coverage": aggregate(event_report),
        "outcome_and_stroke_coverage": {
            "predicted_rallies": len(predictions),
            "known_winner_outputs": sum(
                e["payload"].get("winner") is not None for e in live if e["type"] == "rally_end"
            ),
            "unknown_winner_outputs": sum(e["payload"].get("winner") is None for e in live if e["type"] == "rally_end"),
            "stroke_label_counts": dict(
                collections.Counter(str(e["payload"].get("stroke", "unknown")) for e in live if e["type"] == "stroke")
            ),
            "canonical_point_events": sum(e["type"] == "point" for e in live),
            "broadcast_score_observation_events": sum(e["type"] == "broadcast_score" for e in live),
            "accuracy_status": "unavailable_without_independent_identity_event_outcome_score_labels",
        },
        "runtime_resources": aggregate(resources),
        "track_coverage": aggregate(tracks),
        "provenance": {
            "native_guard_root": str(ROOT),
            "recorded_plan": str(plan_path),
            "recorded_pipeline_commit": plan["code_commit"],
            "recorded_source_files_sha256": plan["source_files_sha256"],
            "actual_worker": bound["worker_info"],
            "actual_verified_models": models,
            "profile": bound["profile"],
            "degraded_components": bound.get("degraded", []),
        },
        "new_inference_performed": False,
        "physical_accuracy_claimed": False,
        "annotations_modified": False,
        "predictions_modified": False,
        "input_sha256": consumed,
    }
    if any(sha(p) != digest for p, digest in consumed.items()):
        raise ValueError("Original inputs changed during read-only evaluation")
    output.mkdir(parents=True, exist_ok=False)
    (output / "evaluation_manifest.json").write_bytes(manifest_path.read_bytes())
    (output / "recorded_plan.json").write_bytes(plan_path.read_bytes())
    if certificate is not None:
        (output / "coordinate_binding.json").write_bytes(Path(certificate).read_bytes())
    for original in consumed:
        path = Path(original)
        if path.suffix == ".py" and path.is_relative_to(ROOT):
            snapshot = output / "executed_helpers" / path.relative_to(ROOT)
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(path.read_bytes())
    for name, value in [
        ("component_reference_metrics.json", result),
        ("reference_raw_details.json", raw),
        (
            "component_raw_details.json",
            {
                "events": event_report,
                "coverage": coverage,
                "resources": resources,
                "ocr": analysis.ocr_summary(chunks),
                "tracks": tracks,
            },
        ),
    ]:
        (output / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    for index, (name, detail) in enumerate(point_details.items(), 1):
        with (output / f"point_reference_{index:02d}.jsonl").open("x") as stream:
            for row in detail:
                stream.write(json.dumps({"annotation": name, **row}, allow_nan=False) + "\n")
    (output / "REPORT.md").write_text(render_report(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--coordinate-binding", type=Path)
    arguments = parser.parse_args()
    evaluate(arguments.run, arguments.manifest, arguments.output, arguments.coordinate_binding)
