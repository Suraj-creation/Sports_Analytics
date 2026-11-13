"""New-arm focused diagnostics after standard completed/native gate only."""

import json
from pathlib import Path

from native_completion_gate import sha


def review_v6_cases(config, out, inputs, after, analysis, frames, consume):
    out = Path(out)
    art = Path(config["artifact_root"])

    def save(name, value):
        with (out / name).open("x") as f:
            json.dump(value, f, indent=2, allow_nan=False)
            f.write("\n")

    reasons = {}

    def focus(f, why):
        if 0 <= f < config["frame_count"]:
            reasons.setdefault(f, []).append(why)

    barriers = {r["frame"] for r in analysis["component_coverage"]["scene_records"] if r["actual_barrier"]}
    expected = {
        "four_source_confirmed_lost_cut_recoveries": {str(f): f in barriers for f in config["recovered_scene_anchors"]},
        "all_prior_source_reviewed_weak_reset_preservation": {
            str(f): f in barriers for f in config["known_weak_reset_anchors"]
        },
        "continuous_controls_without_reset": {str(f): f not in barriers for f in config["negative_reset_controls"]},
        "other_source_confirmed_scene_preservation": {
            str(f): f in barriers for f in config["other_source_confirmed_scene_anchors"]
        },
    }
    for group, cases in expected.items():
        for f, ok in cases.items():
            for k in [int(f) - 1, int(f), int(f) + 1]:
                focus(k, group + ": " + ("expected_behavior_present" if ok else "ACCEPTANCE_REVIEW_REQUIRED"))
    cadence = []
    for lo, hi in config["cadence_review_ranges_halfopen"] + [[13499, 13555]]:
        for f in range(lo, hi):
            row = frames[f]
            cadence.append(
                {
                    "frame": f,
                    "detector_observed": row["do"],
                    "participant_count": len(row["p"]),
                    "matched_participants": sum(p["dm"] is True for p in row["p"]),
                    "carried_participants": sum(p["dm"] is False for p in row["p"]),
                    "scene_only_foreground_count": len(row.get("fg", [])),
                    "content_epoch": row["ce"],
                    "raw_shuttle_present": row["s"] is not None,
                    "shuttle_status": row.get("sa", {}).get("status") if row.get("sa") else None,
                    "persons": row["p"],
                    "pose_stride": row.get("ps"),
                    "acquisition_request": row.get("aq"),
                }
            )
        for f in [lo - 1, lo, lo + 1, hi - 2, hi - 1, hi]:
            focus(f, "Exact requested detector-cadence window boundary; p versus fg distinct")
    save(
        "actual_cadence_and_AQ_source_windows.json",
        {
            "scope": "All actual requested source-window frames, no assumed nominal cadence or physical recall",
            "rows": cadence,
        },
    )
    currentrows = consume(art / "bound_reference_diagnostics/reference_row_comparisons.json")
    primaryrows = currentrows["Test2_Full.csv"]["comparison"]
    short = [r for r in primaryrows if r.get("reference_data_row") == 33]
    save(
        "short_coarse_row33_current.json",
        {
            "scope": "Existing coarse annotation row, original matching unchanged; no physical impact label",
            "rows": short,
        },
    )
    # Distinct completed5ae full-fresh arm; no failed-outer continuation.
    secondary = Path(config["secondary_completed_root"])
    completed = consume(secondary / "completion.json")
    if (
        completed["status"] != "completed_fresh_candidate_regression_root_visual_review_pending"
        or completed["candidate_commit"] != config["secondary_commit"]
        or completed["new_neural_inference"] is not True
        or completed["own_run_semantic_parity"] is not True
        or completed["frames"] != config["frame_count"]
    ):
        raise ValueError("Secondary completed fresh arm provenance differs")
    worker = consume(secondary / "run/inference.json")
    parent = consume(secondary / "run.executor.json")
    plan = consume(secondary / "protocol/plan.json")
    if (
        worker["status"] != "completed"
        or worker["cached_perception_used"] is not False
        or parent["worker_report_sha256"] != sha(secondary / "run/inference.json")
        or plan["code_commit"] != config["secondary_commit"]
    ):
        raise ValueError("Secondary genuine worker/parent/source plan differs")
    for path, digest in plan["source_files_sha256"].items():
        if not Path(path).is_relative_to(Path(config["secondary_native_root"])) or sha(path) != digest:
            raise ValueError("Secondary producer source differs: " + path)
        inputs[path] = digest
    second = consume(secondary / "bound_reference_diagnostics/component_reference_metrics.json")
    secondrows = consume(secondary / "bound_reference_diagnostics/reference_row_comparisons.json")
    if {x["file"]: x["sha256"] for x in second["annotation_applicability"]} != {
        x["file"]: x["sha256"] for x in after["annotation_applicability"]
    }:
        raise ValueError("Secondary annotation meanings/bytes changed")
    refs = {}
    for name, old in second["interval_reference_comparisons"].items():
        new = after["interval_reference_comparisons"][name]
        if old["metrics"]["matching_policy"] != new["metrics"]["matching_policy"]:
            raise ValueError("Secondary matching policy differs")
        refs[name] = {
            "secondary_5ae_metrics": old["metrics"],
            "fresh_candidate_metrics": new["metrics"],
            "secondary_row_count": len(secondrows[name]["comparison"]),
            "fresh_row_count": len(currentrows[name]["comparison"]),
        }
    save(
        "secondary_5ae_comparison.json",
        {
            "scope": (
                "Preserved5ae completed fresh NN versus " + config.get("review_label", "V6") + " fullfresh; "
                "not a baseline replacement or independent physical accuracy"
            ),
            "secondary_completed_fresh_root": str(secondary),
            "secondary_actual_producer_root": config["secondary_native_root"],
            "references": refs,
            "secondary_coarse_row33": [
                r for r in secondrows["Test2_Full.csv"]["comparison"] if r.get("reference_data_row") == 33
            ],
            "fresh_coarse_row33": short,
        },
    )
    result = {
        **expected,
        "all_expected_scene_controls_pass": all(v for cases in expected.values() for v in cases.values()),
        "cadence_window_frames": len(cadence),
        "actual_cadence_detector_frames": sum(r["detector_observed"] for r in cadence),
        "actual_cadence_fresh_participant_rows": sum(r["matched_participants"] for r in cadence),
        "coarse_row33_diagnostic_rows": len(short),
        "secondary_arm_is_baseline": False,
        "physical_accuracy_claimed": False,
    }
    save("repair_specific_summary.json", result)
    return {"summary": result, "frame_reasons": reasons}
