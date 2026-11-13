"""Independent completed Test2 candidate review; no inference or original edits.

An actual candidate-native completion guard receipt is mandatory before this
script opens new metrics, events or labels. All output files are exclusive NEW.
"""

import importlib.util
import json
from collections import Counter
from hashlib import file_digest
from pathlib import Path

import msgpack
import numpy as np

OUT = Path(__file__).resolve().parent
CONFIG = json.loads((OUT / "review_config.json").read_text())
ROOT = Path(CONFIG["workspace_root"])
MAIN = Path(CONFIG["main_root"])
ART = Path(CONFIG["artifact_root"])
NEURAL = Path(CONFIG["neural_artifact_root"])
RUN = Path(CONFIG["original_run"])
BEFORE = Path(CONFIG["baseline_root"])
CANDIDATE = Path(CONFIG["native_root"])
SOURCE_SHA = CONFIG["source_sha256"]
EXPECTED_COMMIT = CONFIG["expected_commit"]
FRAME_COUNT = CONFIG["frame_count"]


def sha(path):
    with Path(path).open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(name, value):
    with (OUT / name).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def dist(values):
    array = np.asarray(values, float)
    return {
        "count": len(array),
        "mean": float(array.mean()) if len(array) else None,
        "median": float(np.median(array)) if len(array) else None,
        "maximum": float(array.max()) if len(array) else None,
        "p95": float(np.percentile(array, 95)) if len(array) else None,
    }


def iou(a, b):
    a, b = np.asarray(a), np.asarray(b)
    intersection = np.maximum(0, np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2])).prod()
    union = (a[2:] - a[:2]).prod() + (b[2:] - b[:2]).prod() - intersection
    return float(intersection / union) if union > 0 else 0.0


def main():
    # Completion existence and independently executed native guards precede all
    # new reference/prediction consumption. Never import MAIN as native candidate.
    completion_path = ART / "completion.json"
    native_path = OUT / "native_guard_receipt.json"
    if not completion_path.is_file():
        raise ValueError("Orchestration is not complete; predictions/metrics must not be consumed")
    if not native_path.is_file():
        from native_completion_gate import verify_native_completion

        verify_native_completion(CONFIG, OUT)
    assert native_path.is_file()
    completion, native = read(completion_path), read(native_path)
    assert completion["status"] == CONFIG["postprocessing_completion_status"]
    assert completion["new_neural_inference"] is False
    assert completion["original_neural_inference_was_fresh"] is True
    assert Path(completion["original_NN_root"]).resolve() == NEURAL.resolve()
    assert completion["candidate_commit"] == EXPECTED_COMMIT
    assert completion["source_sha256"] == native["source_sha256"] == SOURCE_SHA
    assert native["status"] == "passed_actual_candidate_native_strict_completion_guard" and native[
        "native_root"
    ] == str(CANDIDATE)
    assert completion["own_run_semantic_parity"] is True
    assert native["orchestration_completion_sha256"] == sha(completion_path)
    inputs = {
        str(path): sha(path) for path in [completion_path, native_path, Path(__file__), OUT / "review_config.json"]
    }

    def consume(path):
        inputs[str(path)] = sha(path)
        return read(path)

    verified = 0
    for name, digest in completion["artifact_sha256"].items():
        assert sha(ART / name) == digest
        verified += 1
    for path, digest in native["input_paths_sha256"].items():
        assert sha(path) == digest
    plan = consume(NEURAL / "protocol/plan.json")
    assert all(sha(path) == digest for path, digest in plan["source_files_sha256"].items())
    assert sha(NEURAL / "before_components.json") == sha(
        BEFORE / "bound_reference_diagnostics/component_reference_metrics.json"
    )
    before = consume(NEURAL / "before_components.json")
    after = consume(ART / "bound_reference_diagnostics/component_reference_metrics.json")
    old_analysis = consume(NEURAL / "before_analysis.json")
    analysis = consume(ART / "analysis/technical_analysis.json")
    worker = consume(RUN / "inference.json")
    old_worker = consume(NEURAL / "before_worker.json")
    original_parent = consume(NEURAL / "before_parent.json")
    assert old_worker["status"] == "completed" and old_worker["cached_perception_used"] is False
    assert old_worker["frames_processed"] == FRAME_COUNT and old_worker["source_sha256"] == SOURCE_SHA
    assert original_parent["status"] == "completed" and original_parent["worker_exit_code"] == 0
    assert sha(NEURAL / "before_worker.json") == sha(BEFORE / "run/inference.json")
    control_path = BEFORE / "run/events.jsonl"
    inputs[str(control_path)] = sha(control_path)
    assert worker["profile"] == old_worker["profile"]

    def model_identity(item):
        return {
            group: {
                name: {key: value for key, value in entry.items() if key in {"sha256", "status"}}
                for name, entry in models.items()
            }
            for group, models in item["models_verified_during_analysis"].items()
        }

    assert model_identity(old_analysis) == model_identity(analysis)
    assert {row["file"]: row["sha256"] for row in before["annotation_applicability"]} == {
        row["file"]: row["sha256"] for row in after["annotation_applicability"]
    }
    assert (
        len(after["annotation_applicability"]) == CONFIG["annotation_count"] and len(after["unsupported_metrics"]) == 10
    )
    assert all(item["value"] is None for item in after["unsupported_metrics"].values())
    assert all(sha(path) == digest for path, digest in after["input_sha256"].items())
    method_receipt = consume(Path(CONFIG["method_receipt"]))
    for method in method_receipt["unchanged_evaluator_byte_and_AST_bindings"]:
        assert sha(MAIN / method["file"]) == sha(CANDIDATE / method["file"]) == method["sha256"]["main"]
    helper_path = MAIN / "evaluation/ground_truth_validation/test_02/fixes/review_semantic_effects.py"
    spec = importlib.util.spec_from_file_location("preserved_pure_event_review", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    inputs[str(helper_path)] = sha(helper_path)
    assert (
        len(before["interval_reference_comparisons"])
        == len(after["interval_reference_comparisons"])
        == CONFIG["interval_reference_count"]
    )
    curated = {}

    def focus(frame, reason):
        if 0 <= frame < FRAME_COUNT:
            curated.setdefault(frame, set()).add(reason)

    def points(path):
        inputs[str(path)] = sha(path)
        result = {row["frame"]: row for row in (json.loads(line) for line in path.open())}
        assert sorted(result) == list(range(FRAME_COUNT))
        return result

    point_rows = {
        name: points(base / "bound_reference_diagnostics/frame_point_candidates.jsonl")
        for name, base in [("original", BEFORE), ("fresh", ART)]
    }
    subsets = {}
    for arm in ["original"]:
        comparisons = {}
        for kind in ["all_current_rows_assignments", "fresh_detector_rows_assignments"]:

            def mapping(rows, assignment_kind=kind):
                return {
                    (frame, pair["reference_slot"]): {
                        "distance": pair["distance_px"],
                        "current": row["current_players"][pair["current_index"]],
                        "reference": row["reference_players"],
                    }
                    for frame, row in rows.items()
                    for pair in row.get(assignment_kind, [])
                }

            a, b = mapping(point_rows[arm]), mapping(point_rows["fresh"])
            common, added, removed = a.keys() & b.keys(), b.keys() - a.keys(), a.keys() - b.keys()
            top = [
                {
                    "frame": key[0],
                    "reference_slot": key[1],
                    "before_distance": a[key]["distance"] if key in a else None,
                    "fresh_distance": b[key]["distance"],
                    "current": b[key]["current"],
                    "reference": b[key]["reference"],
                }
                for key in sorted(b, key=lambda item: b[item]["distance"], reverse=True)[:20]
            ]
            comparisons[kind] = {
                "population": "same source-frame and legacy reference-slot assignment; not physical athlete identity",
                "before_all": dist([row["distance"] for row in a.values()]),
                "fresh_all": dist([row["distance"] for row in b.values()]),
                "common_before": dist([a[key]["distance"] for key in common]),
                "common_fresh": dist([b[key]["distance"] for key in common]),
                "common_error_delta": dist([b[key]["distance"] - a[key]["distance"] for key in common]),
                "new_only": dist([b[key]["distance"] for key in added]),
                "old_only": dist([a[key]["distance"] for key in removed]),
                "new_only_keys": sorted(added),
                "old_only_keys": sorted(removed),
                "top_fresh_disagreements": top,
            }
            for row in top[:3]:
                focus(row["frame"], kind + " top generated-reference disagreement")
            for key in sorted(added, key=lambda item: b[item]["distance"], reverse=True)[:3]:
                focus(key[0], kind + " newly scored extreme")
            for key in sorted(common, key=lambda item: b[item]["distance"] - a[item]["distance"], reverse=True)[:3]:
                focus(key[0], kind + " maximum common-pair increase versus " + arm)
        common = [
            frame
            for frame in point_rows[arm]
            if "shuttle_disagreement_px" in point_rows[arm][frame]
            and "shuttle_disagreement_px" in point_rows["fresh"][frame]
        ]
        comparisons["shuttle_common_both_present"] = {
            "before": dist([point_rows[arm][frame]["shuttle_disagreement_px"] for frame in common]),
            "fresh": dist([point_rows["fresh"][frame]["shuttle_disagreement_px"] for frame in common]),
        }
        subsets[arm + "_versus_fresh"] = comparisons
    for frame, _row in sorted(
        point_rows["fresh"].items(), key=lambda item: item[1].get("shuttle_disagreement_px", -1), reverse=True
    )[:3]:
        focus(frame, "largest raw-shuttle versus generated-filled disagreement")
    write("point_population_decomposition.json", subsets)
    before_reference_rows = consume(BEFORE / "bound_reference_diagnostics/reference_row_comparisons.json")
    after_reference_rows = consume(ART / "bound_reference_diagnostics/reference_row_comparisons.json")
    references = {}
    for name, a in before["interval_reference_comparisons"].items():
        b = after["interval_reference_comparisons"][name]
        assert a["metrics"]["matching_policy"] == b["metrics"]["matching_policy"]
        if b["role"] == "partial_mixed_label_candidate":
            assert all(b["metrics"]["detection"][key] is None for key in ["false_positives", "precision", "f1"])
        rows = []

        def comparison_key(row):
            return (
                ("reference", row["reference_data_row"])
                if "reference_data_row" in row
                else ("unmatched_prediction", row.get("pred_rally"))
            )

        old = {comparison_key(row): row for row in before_reference_rows[name]["comparison"]}
        current = {comparison_key(row): row for row in after_reference_rows[name]["comparison"]}
        for source_row in old.keys() | current.keys():
            if old.get(source_row) != current.get(source_row):
                rows.append(
                    {
                        "comparison_key": source_row,
                        "reference_data_row": source_row[1] if source_row[0] == "reference" else None,
                        "before": old.get(source_row),
                        "fresh": current.get(source_row),
                    }
                )
        references[name] = {
            "role": b["role"],
            "matching_policy_unchanged": True,
            "before_metrics": a["metrics"],
            "fresh_metrics": b["metrics"],
            "changed_reference_comparison_rows": rows,
        }
    write("interval_reference_differences.json", references)

    def cache_frames(run, catalogue):
        records = []
        for entry in catalogue["files"]:
            path = run / entry["path"]
            assert sha(path) == entry["sha256"]
            inputs[str(path)] = entry["sha256"]
            records.extend(msgpack.unpackb(path.read_bytes(), raw=False)["frames"])
        assert [row["f"] for row in records] == list(range(FRAME_COUNT))
        return records

    old_frames = cache_frames(BEFORE / "run", consume(NEURAL / "before_catalogue.json"))
    new_frames = cache_frames(RUN, consume(RUN / "perception_completion_catalog.json"))
    write(
        "raw_shuttle_value_status_association_differences.json",
        {
            "scope": (
                "Exact source-frame model observation differences; no attribution to scene alone or physical accuracy"
            ),
            "rows": [
                {
                    "frame": old["f"],
                    "before": {key: old.get(key) for key in ("s", "c", "sa")},
                    "fresh": {key: fresh.get(key) for key in ("s", "c", "sa")},
                }
                for old, fresh in zip(old_frames, new_frames, strict=True)
                if any(old.get(key) != fresh.get(key) for key in ("s", "c", "sa"))
            ],
        },
    )
    old_live = helper.live(control_path)
    new_event_path = RUN / "events.jsonl"
    new_live = helper.live(new_event_path)
    inputs[str(control_path)], inputs[str(new_event_path)] = sha(control_path), sha(new_event_path)
    events = {
        "scope": (
            "Original completed fresh full-neural Test2 dacc05e baseline versus preserved fresh candidate NN; "
            "separate new postprocessing, "
            "not physical event/identity truth"
        ),
        "baseline_full_NN_contact_count": old_analysis["events"]["live_counts"].get("contact"),
        "baseline_full_fresh_contact_count": sum(row["type"] == "contact" for row in old_live),
        "before_counts": dict(Counter(row["type"] for row in old_live)),
        "fresh_counts": dict(Counter(row["type"] for row in new_live)),
        "before_stroke_labels": dict(
            Counter(row["payload"].get("stroke", "unknown") for row in old_live if row["type"] == "stroke")
        ),
        "fresh_stroke_labels": dict(
            Counter(row["payload"].get("stroke", "unknown") for row in new_live if row["type"] == "stroke")
        ),
    }
    for kind in ["contact", "stroke"]:
        try:
            events[kind] = helper.compare_kind(old_live, new_live, kind)
        except ValueError as error:
            before_events = {row["frame_start"]: helper.compact_event(row) for row in old_live if row["type"] == kind}
            fresh_events = {row["frame_start"]: helper.compact_event(row) for row in new_live if row["type"] == kind}
            changes = []
            for frame in sorted(before_events.keys() & fresh_events.keys()):
                a, b = before_events[frame], fresh_events[frame]
                delta = {key: {"before": a[key], "after": b[key]} for key in a if a[key] != b[key]}
                if delta:
                    changes.append({"frame": frame, "before": a, "after": b, "changes": delta})
            events[kind] = {
                "nearby_anchor_association_status": "unavailable_rally_context_changed",
                "reason": str(error),
                "scope": "Exact-anchor set differences only; no shifted-event identity inference",
                "before_count": len(before_events),
                "after_count": len(fresh_events),
                "candidate_temporal_shifts": [],
                "unpaired_removed": [
                    before_events[frame] for frame in sorted(before_events.keys() - fresh_events.keys())
                ],
                "unpaired_added": [fresh_events[frame] for frame in sorted(fresh_events.keys() - before_events.keys())],
                "same_anchor_changes": changes,
            }
    assert events["baseline_full_fresh_contact_count"] == CONFIG["baseline_expected_contacts"]
    assert events["before_stroke_labels"]["unknown"] == CONFIG["baseline_expected_unknown_strokes"]
    assert events["before_counts"]["rally_end"] == CONFIG["baseline_expected_rallies"]
    actor_changes = []
    for row in events["contact"].get("same_anchor_changes", []):
        a, b = row["before"], row["after"]
        if a["hypothesis_track_id"] == b["hypothesis_track_id"] and a["hypothesis_status"] == b["hypothesis_status"]:
            continue
        frame = row["frame"]
        old_person = [person for person in old_frames[frame]["p"] if person["t"] == a["hypothesis_track_id"]]
        new_person = [person for person in new_frames[frame]["p"] if person["t"] == b["hypothesis_track_id"]]
        overlap = iou(old_person[0]["b"], new_person[0]["b"]) if len(old_person) == len(new_person) == 1 else None
        actor_changes.append(
            {
                "frame": frame,
                "before_episode": a["hypothesis_track_id"],
                "fresh_episode": b["hypothesis_track_id"],
                "before_status": a["hypothesis_status"],
                "fresh_status": b["hypothesis_status"],
                "current_box_iou": overlap,
                "category": "same source image region despite episode-record change"
                if overlap is not None and overlap >= 0.5
                else "different selected source image regions"
                if overlap is not None
                else "unresolved or selected current raw person unavailable",
            }
        )
    events["anonymous_actor_region_changes"] = actor_changes
    for row in actor_changes:
        focus(row["frame"], "anonymous attribution episode/selected source region changed; no physical identity claim")
    for kind in ["contact", "stroke"]:
        for row in events[kind].get("unpaired_removed", []) + events[kind].get("unpaired_added", []):
            focus(row["frame"], "unpaired " + kind + " anchor")
        for row in events[kind].get("candidate_temporal_shifts", []):
            focus(row["before_frame"], "candidate shifted " + kind + " before")
            focus(row["after_frame"], "candidate shifted " + kind + " fresh")
    for row in events["stroke"].get("same_anchor_changes", []):
        if "stroke" in row["changes"]:
            focus(row["frame"], "same-anchor predicted stroke-class change")
    write("event_differences.json", events)
    barrier_sets = {
        name: {row["frame"] for row in item["component_coverage"]["scene_records"] if row["actual_barrier"]}
        for name, item in [("original", old_analysis), ("fresh", analysis)]
    }
    scene = {
        "barrier_frames": {key: sorted(value) for key, value in barrier_sets.items()},
        "new_vs_original": sorted(barrier_sets["fresh"] - barrier_sets["original"]),
        "lost_vs_original": sorted(barrier_sets["original"] - barrier_sets["fresh"]),
        "scope": "Every recorded scene/content barrier; source review required for every new/lost reset",
    }
    for frame in barrier_sets["original"]:
        focus(frame - 1, "all original content barrier previous frame")
        focus(frame, "all original content barriers must be preserved or explained")
    for frame in set(scene["new_vs_original"] + scene["lost_vs_original"]):
        for nearby in [frame - 1, frame, frame + 1]:
            focus(nearby, "NEW or LOST content barrier; source review mandatory")
    known = set(CONFIG["known_source_case_anchors"])
    scene["fresh_changed_boundary_records"] = [
        row
        for row in analysis["component_coverage"]["scene_records"]
        if row["frame"] in set(scene["new_vs_original"] + scene["lost_vs_original"]) | known
    ]
    scene["source_case_cache_evidence"] = [
        {key: frame.get(key) for key in ["f", "p", "fg", "do", "ce", "cc", "cd"]}
        for frame in new_frames
        if frame["f"] in {f for anchor in known for f in (anchor - 1, anchor, anchor + 1)}
    ]
    write("scene_boundary_review_inputs.json", scene)
    for anchor in sorted(set(CONFIG["known_source_case_anchors"]) | set(CONFIG["known_weak_reset_anchors"])):
        for f in (anchor - 1, anchor, anchor + 1):
            focus(f, "Test2 source-confirmed edit, athlete/official handover or negative reset control")
    for start, stop in CONFIG["mandatory_source_review_ranges_halfopen"]:
        for frame in range(start, stop):
            focus(frame, CONFIG["mandatory_source_review_reason"])
    from audit_acquisition_coverage import audit_acquisition_coverage

    extra = audit_acquisition_coverage(CONFIG, OUT, old_frames, new_frames)
    inputs.update(extra["input_sha256"])
    for frame, reasons in extra["frame_reasons"].items():
        for reason in reasons:
            focus(int(frame), reason)
    write(
        "source_frame_plan.json",
        {
            "source_sha256": SOURCE_SHA,
            "proxy_sha256": worker["proxy_sha256"],
            "frames": [{"frame": frame, "reasons": sorted(reasons)} for frame, reasons in sorted(curated.items())],
            "scope": (
                "Every new/lost content barrier, predicted class change, changed contact anchors and point extremes; "
                "no physical annotation labels"
            ),
        },
    )
    plans = OUT / "source_frame_plans"
    plans.mkdir(exist_ok=False)
    full_frames = [{"frame": frame, "reasons": sorted(reasons)} for frame, reasons in sorted(curated.items())]
    for offset in range(0, len(full_frames), 128):
        with (plans / f"batch_{offset // 128 + 1:02d}.json").open("x") as handle:
            json.dump(
                {
                    "source_sha256": SOURCE_SHA,
                    "proxy_sha256": worker["proxy_sha256"],
                    "frames": full_frames[offset : offset + 128],
                    "scope": "Exact partition of complete independent review plan; no cases silently removed",
                },
                handle,
                indent=2,
            )
            handle.write("\n")
    write(
        "runtime_provenance_review.json",
        {
            "candidate_commit": completion["candidate_commit"],
            "original_NN_root": str(NEURAL),
            "new_postprocessing_root": str(ART),
            "new_neural_inference_performed_here": False,
            "native_root": str(CANDIDATE),
            "source_sha256": SOURCE_SHA,
            "proxy_sha256": worker["proxy_sha256"],
            "configuration_exactly_equal_to_full_NN_baseline": worker["profile"] == old_worker["profile"],
            "executed_profile": worker["profile"],
            "actual_models_verified": analysis["models_verified_during_analysis"],
            "runtime_resources": analysis["resources"],
            "selected_components": analysis.get("selected_components"),
            "execution_environment": consume(NEURAL / "environment.json"),
            "postprocessing_continuation": consume(ART / "continuation_manifest.json"),
            "all_annotation_file_sha256": {row["file"]: row["sha256"] for row in after["annotation_applicability"]},
            "helper_file_sha256": {
                row["file"]: row["sha256"]["main"]
                for row in method_receipt["unchanged_evaluator_byte_and_AST_bindings"]
            },
            "source_plan_file_sha256": plan["source_files_sha256"],
            "baseline_event_scope": (
                "Preserved completed fresh Test2 full-neural baseline:816 contacts,586 unknown strokes,75 rallies; "
                "no cached semantic substitute"
            ),
            "physical_accuracy_validated": False,
        },
    )
    summary = {
        "status": "completed_independent_Test2_postprocessing_review_pending_source_classification",
        "candidate_commit": completion["candidate_commit"],
        "original_NN_root": str(NEURAL),
        "new_postprocessing_root": str(ART),
        "new_neural_inference_performed_here": False,
        "source_sha256": SOURCE_SHA,
        "completed_artifacts_verified": verified,
        "source_plan_files_verified": len(plan["source_files_sha256"]),
        "profile_exactly_unchanged": True,
        "actual_model_identity_equal": True,
        "seven_annotation_hashes_equal": True,
        "crosschunk_scene_proof_audit": extra["camera_proofs"],
        "full_population_audit": extra["population_summary"],
        "unsupported_physical_metric_families_null": 10,
        "references": {
            name: {
                "before_detection": row["before_metrics"]["detection"],
                "fresh_detection": row["fresh_metrics"]["detection"],
                "before_mean_iou": row["before_metrics"]["overlap"]["mean_iou"],
                "fresh_mean_iou": row["fresh_metrics"]["overlap"]["mean_iou"],
                "changed_rows": len(row["changed_reference_comparison_rows"]),
            }
            for name, row in references.items()
        },
        "scene_differences": {
            key: value
            for key, value in scene.items()
            if key not in ["fresh_changed_boundary_records", "source_case_cache_evidence"]
        },
        "event_counts": {
            "before": events["before_counts"],
            "fresh": events["fresh_counts"],
            "before_labels": events["before_stroke_labels"],
            "fresh_labels": events["fresh_stroke_labels"],
        },
        "named_contact_actors_before_fresh": [
            sum(row.get("actors", {}).get("player_id") is not None for row in data if row["type"] == "contact")
            for data in [old_live, new_live]
        ],
        "known_rally_winners_before_fresh": [
            sum(row["payload"].get("winner") is not None for row in data if row["type"] == "rally_end")
            for data in [old_live, new_live]
        ],
        "resource_before": old_analysis["resources"],
        "resource_fresh": analysis["resources"],
        "all_current_raw_coverage_before": old_analysis["component_coverage"]["counts"],
        "all_current_raw_coverage_fresh": analysis["component_coverage"]["counts"],
        "physical_accuracy_gain_claimed": False,
        "no_original_files_modified": True,
        "no_new_inference": True,
        "input_sha256": inputs,
    }
    assert all(sha(path) == digest for path, digest in inputs.items())
    write("summary.json", summary)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "references": summary["references"],
                "scenes": summary["scene_differences"],
                "event_counts": summary["event_counts"],
                "plan_frames": len(curated),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
