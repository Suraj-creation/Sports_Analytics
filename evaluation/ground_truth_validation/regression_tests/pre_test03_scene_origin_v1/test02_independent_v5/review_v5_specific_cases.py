"""New-arm focused diagnostics after standard completed/native gate only."""

import json
from pathlib import Path

from native_completion_gate import sha


def review_v5_cases(config, out, inputs, after, analysis, frames, consume):
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
        "nine_source_confirmed_weak_reset_preservation": {
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
    for lo, hi in config["cadence_review_ranges_halfopen"]:
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
                }
            )
        for f in [lo - 1, lo, lo + 1, hi - 2, hi - 1, hi]:
            focus(f, "Exact requested detector-cadence window boundary; p versus fg distinct")
    save(
        "actual_cadence_window_25680_25739.json",
        {"scope": "All actual60 source frames, no assumed nominal cadence or physical recall", "rows": cadence},
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
    # Distinct historical secondary arm: no fresh inference claim or native ROOT rebasing.
    secondary = Path(config["secondary_completed_postprocessing_root"])
    original = Path(config["secondary_original_neural_root"])
    completed = consume(secondary / "completion.json")
    if (
        completed["status"] != "completed_postprocessing_of_original_fresh_run_root_review_pending"
        or completed["candidate_commit"] != "2418ab8cbe4cca74dd16b722b9727ffdc950294a"
        or completed["new_neural_inference"] is not False
        or completed["original_neural_inference_was_fresh"] is not True
        or Path(completed["original_NN_root"]) != original
    ):
        raise ValueError("Secondary arm provenance differs")
    if (original / "completion.json").exists() or not (original / "failure.json").is_file():
        raise ValueError("Historical outer failure must remain preserved")
    continuation = consume(secondary / "continuation_manifest.json")
    for path, h in continuation["original_artifact_sha256"].items():
        if sha(path) != h:
            raise ValueError("Historical secondary original evidence changed: " + path)
        inputs[path] = h
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
            "secondary_2418_metrics": old["metrics"],
            "fresh_v5_metrics": new["metrics"],
            "secondary_row_count": len(secondrows[name]["comparison"]),
            "fresh_row_count": len(currentrows[name]["comparison"]),
        }
    save(
        "secondary_2418_comparison.json",
        {
            "scope": (
                "Preserved2418 completed fresh NN + separate completed postprocessing versus newV5 fullfresh; "
                "not baseline replacement or independent physical accuracy"
            ),
            "secondary_original_NN_root": str(original),
            "secondary_postprocessing_root": str(secondary),
            "original_outer_failure_preserved": True,
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
    save("v5_specific_summary.json", result)
    return {"summary": result, "frame_reasons": reasons}
