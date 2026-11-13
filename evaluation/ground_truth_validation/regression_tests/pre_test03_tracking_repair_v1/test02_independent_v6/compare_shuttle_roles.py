"""Separate raw NN and associated-current-NN roles after completed native gates."""

import json
from collections import Counter
from pathlib import Path

import numpy as np


def role_observation(frame):
    observation = frame.get("sa")
    if not isinstance(observation, dict):
        raise ValueError("Explicit association availability is required for role export")
    if observation.get("raw_xy") != frame.get("s") or observation.get("raw_model_support") != frame.get("c"):
        raise ValueError("Raw NN provenance changed")
    selected = observation.get("selected_xy")
    support = observation.get("selected_model_support")
    if observation.get("schema") == "badminton-shuttle-association:v2":
        if selected is not None and selected != frame.get("s"):
            raise ValueError("Legacy association cannot promote a different raw coordinate")
        support = frame["c"] if selected is not None else None
    elif selected is not None and support is None:
        raise ValueError("Never borrow raw support for an associated alternative")
    if observation.get("status") != "observed" and selected is not None:
        raise ValueError("Unavailable association cannot export an observed point")
    return {
        "raw_nn": {"xy": frame.get("s"), "support": frame.get("c")},
        "associated_selected_nn": {"xy": selected, "support": support},
        "association_status": observation.get("association_status"),
        "observation_status": observation.get("status"),
        "selection_coordinate_source": observation.get("selection_coordinate_source", "legacy_selected_equals_raw"),
        "selection_candidate_rank": observation.get("selected_candidate_rank"),
        "raw_masked_peak_xy": observation.get("raw_masked_peak_xy"),
        "selection_witness_frames": observation.get("selection_witness_frames", []),
    }


def compare_shuttle_roles(config, out, inputs, current_frames, current_points, consume):
    # Imports are delayed until the caller has run genuine native completion gates.
    import msgpack
    from native_completion_gate import sha

    from evaluation.ground_truth_validation.orchestration.evaluate_test02_components import compact
    from research.test2_evaluation import distribution

    out = Path(out)
    artifact = Path(config["artifact_root"])
    secondary = Path(config["secondary_completed_root"])
    metrics = consume(artifact / "bound_reference_diagnostics/component_reference_metrics.json")
    certificate = metrics["point_diagnostics"]["coordinate_binding"]
    bound = (
        certificate["status"] == "diagnostic_coordinate_binding_declared"
        and certificate["certificate"].get("legacy_shuttle_point") == "analysis_image_xy"
    )
    counts = Counter()
    raw_distances, selected_distances, alternative_frames, ambiguity_frames, aq_frames = [], [], [], [], []
    rows_path = out / "raw_and_associated_selected_frame_rows.jsonl"
    with rows_path.open("x") as stream:
        for f in current_frames:
            row = role_observation(f)
            fi = f["f"]
            ref = current_points[fi]["reference_shuttle"]
            raw, selected = row["raw_nn"]["xy"], row["associated_selected_nn"]["xy"]
            counts["raw_nn_present"] += raw is not None
            counts["associated_selected_present"] += selected is not None
            counts["raw_present_selected_unavailable"] += raw is not None and selected is None
            counts["reference_outside_image"] += current_points[fi].get("reference_shuttle_in_image") is False
            is_alternative = row["selection_coordinate_source"] == "current_candidate_peak"
            if is_alternative:
                alternative_frames.append(fi)
            if row["observation_status"] == "ambiguous":
                ambiguity_frames.append(fi)
            if f.get("aq") is not None:
                aq_frames.append(fi)
            details = {
                "frame": fi,
                "shot": f["sh"],
                "content_epoch": f["ce"],
                **row,
                "reference_generated_xy": ref,
                "reference_in_image": current_points[fi].get("reference_shuttle_in_image"),
                "AQ": f.get("aq"),
            }
            if bound and ref is not None and raw is not None:
                value = float(np.linalg.norm(np.asarray(ref) - np.asarray(raw)))
                raw_distances.append(value)
                details["raw_generated_disagreement_px"] = value
            if bound and ref is not None and selected is not None:
                value = float(np.linalg.norm(np.asarray(ref) - np.asarray(selected)))
                selected_distances.append(value)
                details["associated_generated_disagreement_px"] = value
            stream.write(json.dumps(details, allow_nan=False) + "\n")
    raw_summary = compact(distribution(raw_distances)) if bound else None
    if raw_summary != metrics["point_diagnostics"]["shuttle_raw_distance_px_both_present"]:
        raise ValueError("Raw role export changed the original canonical disagreement formula/population")
    source_cases = {
        f: "Source visual review of changed associated observation/abstention, not physical GT"
        for f in alternative_frames
    }
    for f in config["floor_alias_source_case_frames"]:
        source_cases[f] = "Known floor-region source case: inspect raw NN and separately associated observation"
    summaries = {
        "classification": (
            "Generated-reference diagnostic agreement; raw and associated-selected are different roles, "
            "not physical accuracy"
        ),
        "coverage": dict(counts),
        "raw_nn_generated_disagreement_px": raw_summary,
        "associated_selected_nn_generated_disagreement_px": compact(distribution(selected_distances))
        if bound
        else None,
        "alternative_selection_count": len(alternative_frames),
        "association_ambiguous_count": len(ambiguity_frames),
        "AQ_requested_frame_count": len(aq_frames),
        "separate_model_roles": True,
        "physical_accuracy_claimed": False,
    }
    with (out / "raw_and_associated_selected_summary.json").open("x") as f:
        json.dump(summaries, f, indent=2, allow_nan=False)
        f.write("\n")
    with (out / "associated_selection_case_frames.json").open("x") as f:
        json.dump(
            {"alternative_frames": alternative_frames, "ambiguous_frames": ambiguity_frames, "AQ_frames": aq_frames},
            f,
            indent=2,
        )
        f.write("\n")
    # Original assignment machinery and aggregate function are reused unchanged.
    old_path = secondary / "bound_reference_diagnostics/frame_point_candidates.jsonl"
    inputs[str(old_path)] = sha(old_path)
    old_points = {r["frame"]: r for r in map(json.loads, old_path.open())}
    comparisons = {}
    for kind in ["all_current_rows_assignments", "fresh_detector_rows_assignments"]:

        def mapping(points, assignment_kind=kind):
            return {
                (fi, pair["reference_slot"]): (pair["distance_px"], row["current_players"][pair["current_index"]])
                for fi, row in points.items()
                for pair in row[assignment_kind]
            }

        old, new = mapping(old_points), mapping(current_points)
        common, added, dropped = old.keys() & new.keys(), new.keys() - old.keys(), old.keys() - new.keys()
        increases = sorted(
            (key for key in common if new[key][0] > old[key][0]),
            key=lambda key: new[key][0] - old[key][0],
            reverse=True,
        )
        comparisons[kind] = {
            "scope": "Same source-frame/generated-reference-slot assignment, no physical identity assertion",
            "common_before": compact(distribution([old[key][0] for key in common])),
            "common_current": compact(distribution([new[key][0] for key in common])),
            "added": compact(distribution([new[key][0] for key in added])),
            "dropped": compact(distribution([old[key][0] for key in dropped])),
            "added_keys": sorted(added),
            "dropped_keys": sorted(dropped),
            "all_common_changed_rows": [
                {
                    "frame": key[0],
                    "reference_slot": key[1],
                    "before_distance": old[key][0],
                    "current_distance": new[key][0],
                    "before_person": old[key][1],
                    "current_person": new[key][1],
                }
                for key in sorted(common)
                if old[key] != new[key]
            ],
        }
        for key in increases[:3]:
            source_cases[key[0]] = (
                "Largest NEW common generated-point disagreement increase versus completed5ae; "
                "inspect observation/carry/source region"
            )
    with (out / "secondary_5ae_point_population_comparison.json").open("x") as f:
        json.dump(comparisons, f, indent=2, allow_nan=False)
        f.write("\n")
    # Do not reinterpret raw NN changes as associated-model changes.
    cat = consume(secondary / "run/perception_completion_catalog.json")
    old_frames = []
    for entry in cat["files"]:
        path = secondary / "run" / entry["path"]
        assert sha(path) == entry["sha256"]
        inputs[str(path)] = entry["sha256"]
        old_frames.extend(msgpack.unpackb(path.read_bytes(), raw=False)["frames"])
    if [r["f"] for r in old_frames] != list(range(config["frame_count"])):
        raise ValueError("Secondary source timeline differs")
    deltas = []
    for old, current in zip(old_frames, current_frames, strict=True):
        old_role, new_role = role_observation(old), role_observation(current)
        if old_role != new_role:
            deltas.append({"frame": old["f"], "before_5ae": old_role, "current": new_role})
    with (out / "secondary_5ae_raw_and_selected_role_changes.json").open("x") as f:
        json.dump(
            {
                "scope": "Separate raw/associated roles from complete recorded NN runs, no physical labels",
                "rows": deltas,
            },
            f,
            indent=2,
            allow_nan=False,
        )
        f.write("\n")
    return {"summary": summaries, "source_cases": source_cases}
