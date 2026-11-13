"""Build the guarded Test1 V5 regression report, then seal all owned evidence."""
import json
import re
from hashlib import file_digest
from pathlib import Path

OUT = Path(__file__).resolve().parent
CFG = json.loads((OUT / "review_config.json").read_text())
ART = Path(CFG["artifact_root"])
VIS = OUT.parent / "visual_test01_v5_new_reset_review_v1"


def read(p):
    return json.loads(Path(p).read_text())


def sha(p):
    with Path(p).open("rb") as f:
        return file_digest(f, "sha256").hexdigest()


def fmt(v):
    return "N/A" if v is None else f"{v:.9f}"


def main():
    s = read(OUT / "summary.json")
    refs = read(OUT / "interval_reference_differences.json")
    secondary = read(OUT / "interval_secondary_2418_comparison.json")
    points = read(OUT / "point_population_decomposition.json")
    detail = read(OUT / "point_change_detail.json")
    raw = read(OUT / "full_raw_timeline_differences.json")
    events = read(OUT / "event_differences_previous_2418.json")
    protection = read(OUT / "protected_inputs_review.json")
    proof = read(OUT / "native_scene_epoch_full_proof.json")["proof"]
    previous_analysis = read(Path(CFG["previous_candidate_root"]) / "analysis/technical_analysis.json")
    assert s["all_182_coverage_audit"]["bbox_exact"] == 182
    assert not read(OUT / "all_current_gross_population_losses.json")["rows"]
    assert all(v["metrics_exactly_equal"] and v["comparison_rows_exactly_equal"] for v in secondary.values())
    assert protection["original_MAIN_Part2_files_verified"] == 62
    assert protection["candidate_Test1_annotation_copies_verified"] == 9
    assert proof["native_decoded_frames"] == 17268 and proof["weak_barrier_frames"] == [14114]
    assert not s["scene_differences"]["lost_vs_original"]
    assert s["scene_differences"]["new_vs_original"] == [14114]
    for p, digest in s["input_sha256"].items():
        assert sha(p) == digest, p
    for p, digest in protection["protected_paths_sha256"].items():
        assert sha(p) == digest, p
    visual = read(VIS / "verification_receipt.json")
    # Bind the separate source review without promoting its diagnostic judgments
    # to physical ground-truth labels or pretending to inspect its whole video.
    visual_bindings = {str(p): sha(p) for p in [VIS / "REPORT.md", VIS / "verification_receipt.json",
                                               VIS / "source_verification.json", VIS / "whole_native_structural_review.json"]}
    assets = []
    worker = read(ART / "run/inference.json")
    for name, row in worker["models"]["artifacts"].items():
        if row.get("status") == "verified_copy":
            p = Path(row["staged_path"])
            assert sha(p) == row["sha256"]
            assets.append({"name": name, "path": str(p), "sha256": row["sha256"]})
    graph = list((ART / "run/models/cache/rtmpose_m_body7").rglob("*.onnx"))
    assert len(graph) == 1 and sha(graph[0]) == "5c0a4bf67953e6d2ac43ce15e77dc9d5d354ae18430a47d2c5963a7bc5683e3c"
    assets.append({"name": "actual_staged_pose_graph", "path": str(graph[0]), "sha256": sha(graph[0])})
    (OUT / "actual_staged_model_asset_verification.json").write_text(json.dumps(assets, indent=2) + "\n")
    lines = ["# Independent Test 1 V5 full-run regression review", "",
             "**PASS for the stated Test 1 regression gates:** all six reference matrices and matched-row comparisons are exactly equal to the previous accepted 2418 run; all 182 historical image regions remain exact and no original participant-count loss occurs. All 13 original scene barriers remain, and the one new barrier14114 is supported by a real source edit. This is not physical component-accuracy certification or an all-video aggregate.", "",
             f"The actual completed producer is `{CFG['native_root']}`, commit `{CFG['expected_commit']}`. Its genuine fresh worker, parent, complete workflow and own-run semantic parity pass. Independent guards rehashed {s['completed_artifacts_verified']:,} output artifacts and {s['source_plan_files_verified']} worker-plan source files, with actual native imports and no ROOT reassignment. No inference, pipeline edits, model/profile changes, original annotation edits, or Test3 content analysis were performed by this reviewer.", "",
             "## Completion and protected evidence", "",
             "All 94 preflight-protected files are unchanged: **62 original files under MAIN/Part2**, nine candidate Test1 annotation copies, and 23 other protected baseline/control files. Candidate copies exactly match their originals. The initial review helper incorrectly counted both roots as 71 Part2 files and failed its expected62 assertion after already verifying every hash. Its failure log and executed source remain preserved; the corrected receipt scopes the original root exactly and verifies all94 hashes again. This was a review count-scope error, not a pipeline failure or a relaxed protection gate.", "",
             "Nine applicable Test1 annotation hashes, actual model identity and executed profile match the original full-neural baseline. Actual staged model assets, including the pose graph rather than only its ZIP, were additionally fingerprinted. The ten unsupported physical metric families remain null. Matching retains half-open intervals, maximum-cardinality/IoU assignment, minimumIoU0.5 and the unchanged boundary-error definitions.", "",
             "Evidence: [native guard](native_guard_receipt.json), [native full source/camera/format/foreground proof](native_scene_epoch_full_proof.json), [protected originals and copies](protected_inputs_review.json), [models/configuration/runtime](runtime_provenance_review.json), [actual staged model assets](actual_staged_model_asset_verification.json), [unchanged numerical helper bindings](method_bindings.json).", "",
             "## All six interval matrices", "",
             "The table is current performance against each distinct supplied reference. Every value and comparison row is exactly unchanged from accepted2418. Slight gains versus the earlier original full-neural baseline remain separately retained; one matched row changes per reference. Overlapping/generated timing references are not independent physical labels.", "",
             "| Reference | TP/FP/FN | Precision | Recall | F1 | MeanIoU original→current | Start MAE s | End MAE s | Duration MAE s |",
             "|---|---|---:|---:|---:|---|---:|---:|---:|"]
    for name, row in refs.items():
        m = row["fresh_metrics"]; d = m["detection"]; e = m["boundary_and_duration_errors"]
        counts = "/".join("N/A" if d[k] is None else str(d[k]) for k in ["true_positives", "false_positives", "false_negatives"])
        lines.append(f"| {name} | {counts} | {fmt(d['precision'])} | {fmt(d['recall'])} | {fmt(d['f1'])} | {fmt(row['before_metrics']['overlap']['mean_iou'])}→{fmt(m['overlap']['mean_iou'])} | {fmt(e['start_time_sec']['mae'])} | {fmt(e['end_time_sec']['mae'])} | {fmt(e['duration_sec']['mae'])} |")
    lines += ["", "Full2 is a partial reference: false positives, precision and F1 remain unavailable, while 19/20 reference intervals match. No missed rally or false detection is silently removed. All signed errors, medians, maxima, RMSE, tolerance populations, exact missed-reference rows, unmatched predictions and original/current comparison rows remain in [all reference details](interval_reference_differences.json); [2418 equality proof](interval_secondary_2418_comparison.json).", "",
              "## Scene/source and participant coverage", "",
              "Native auditing decodes all288codec24 packets and17,268 canonical frames, checks actual previous foreground across packet boundaries, and validates164 relative camera claims including three cross-packet pairs. All13 original barriers are retained. The sole new reset14114 is a **weak positive complete-court replacement**, not a raw strong hypothesis: raw remainsfalse under the unchanged intensity floor. It binds confirmed singles, current strict-court proposals and adjacent actual camera evidence. No overlap-dependent unknown reset occurs.", "",
              "The separately sealed [nine-frame source review](../visual_test01_v5_new_reset_review_v1/REPORT.md) inspected14110–14118. This reviewer also viewed original-source14113→14114: both athletes jump from the right courtside to central ready positions in one1/30s interval. The graphic disappearing is additional context; the athlete displacement supplies edit evidence. This supports that one reset without measuring full-video physical scene recall/precision.", "",
              "All182historical source-box regions across seven intervals are exactIoU1:72fresh detector matches and110carried/unmatched. There are zero lower-person-count frames versus either original or2418. Exact region restoration is not physical recall, named identity or AP. Current returned-player rows are33,956 versus33,716 original. Blue foreground remains image context only and grants no participant/contact/score authority. [All182 rows](all_182_coverage_review.json), [all gross losses](all_current_gross_population_losses.json), [scene records](scene_boundary_review_inputs.json).", "",
              "## Point agreement, cadence and raw shuttle tradeoffs", "",
              "Point tables are generated legacy references. Distances below measure agreement, not physical localization accuracy. All33,466original all-row pairs survive, plus240new pairs. Original13,966fresh-detector common pairs retain exactly identical errors. Versus2418, all33,706all-row pairs remain;36errors change,17increase and19decrease. Mean3.050997136→3.051355210px is a small worsening. Maximum increase18.342794588px occurs at2381: the old fresh box becomes a carried box and error1.202456402→19.545250990px. This predates14114, so changes cannot all be attributed to that later reset.", "",
              "Fresh-detector pair populations versus2418 swap12old-only for12new-only pairs;14,225common fresh errors remain exactly identical. Mean1.456150199→1.456216569px changes with population. Detector cadence adds six and loses six frames versus2418, with no gross person-count loss. Versus original it adds92detector frames and loses none. Source/model pixels being bound does not prove every carried estimate physically improves. Inherited fast-motion lag and overlap ambiguities remain.", "",
              "Raw shuttle values are **not identical**:109XY and107support differences versus both original and2418, limited to14219–14331. Of109XY differences,108are both-present (mean0.191492343px, max3.128491495px at14306);14242changes frommissing to[732.5,315]. Maximum absolute raw-support change is0.50830078125. Raw association payloads differ on3,161frames, including epoch/provenance. Raw camera, view and calibration values remain exactly identical. No physical shuttle label determines whether any changed estimate is better; no isolated causal neural/scheduling experiment was run.", "",
              "Every changed point row and every raw changed frame is retained: [point populations](point_population_decomposition.json), [point detail](point_change_detail.json), [full raw delta index](full_raw_timeline_differences.json), [original raw changes](all_raw_changed_rows_original.jsonl), [2418 raw changes](all_raw_changed_rows_previous_2418.jsonl), [shuttle locations and magnitudes](raw_shuttle_difference_magnitudes_previous_2418.json). Full original pose/racket/foreground arrays remain in the hash-bound immutable caches referenced by the native catalogue; the delta index does not duplicate those large arrays.", "",
              "## Events, classes, outcomes and uncertainty", "",
              "Original latest semantic control remains445contacts/strokes, distinct from the older446contact full-neural overlay baseline. Current has451, identical anchor count to2418. Versus2418 no contact/stroke anchor is added, removed or shifted; eight same-anchor payloads change. The only stroke class change is14639 unknown→estimatedlift with provisional anonymous attribution and altered body/proximity context. This is not a verified physical contact, hitter identity or correctlift label. Unknown strokes305→304 versus2418 (original semantic301).", "",
              "Participant-observation records117→113 and identity-ambiguity records50→51 versus2418; all other retained event-type counts remain visible in the complete event comparison. Named contact actors and known rally winners remain zero outputs, not measured0%accuracy. Observed broadcast-score473 and highlights4remain; neither establishes accepted score/winner/highlight quality. [Original semantic comparison](event_differences.json), [complete2418event/class payload differences](event_differences_previous_2418.json).", "",
              "## Runtime and resources", "",
              "| Recorded scope | Original fullNN | Previous2418 | Current5ae |", "|---|---:|---:|---:|"]
    for key, label in [("worker_elapsed_s", "Worker wall seconds"), ("worker_source_fps", "Worker source FPS"),
                       ("parent_completed_elapsed_s", "Parent wall seconds"), ("worker_final_cpu_s", "Worker CPU thread-seconds"),
                       ("worker_maxrss_bytes", "Worker maxRSS bytes"), ("sampled_worker_gpu_peak_mib", "Sampled worker GPU MiB")]:
        values = [s["resource_before"].get(key), previous_analysis["resources"].get(key), s["resource_fresh"].get(key)]
        lines.append(f"| {label} | " + " | ".join(fmt(v) for v in values) + " |")
    lines += ["", "Current uses physicalGPU1, exposed as logicalCUDA0, on the recorded GPU UUID. Worker wall time1912.072415543s is161.281413253s slower than original and128.065956667s slower than2418. Mixed pipeline/model initialization/cache work and shared host conditions remain included; neural-only FPS and isolated loading latency are unavailable. Stage/sample arrays remain in the runtimeJSON. This is an observed runtime tradeoff, not an isolated causal speed benchmark.", "",
              "## Scope and disposition", "",
              "The measured Test1 interval/population/source regression gates pass with the disclosed point, cadence, shuttle, class and runtime variations. Ten physical metric families remain null: player detection, tracking/identity, pose, shuttle, racket/contact, stroke classes, outcomes, score sequences, highlights and player analytics where independently reviewed labels are absent. Successful execution and generated-reference agreement do not fill those gaps. Root owns acceptance and the separately authorized Test2 generalisation run.", "",
              "All96curated source requests remain in [the source plan](source_frame_plan.json) and complete ≤128-frame partitions; this review does not claim all96have been newly visually inspected. Unchanged historical images were not redundantly rerendered. Newly changed point/class cases remain diagnostic evidence for later physical review. No source file, original run, GT record, model, or previous report was changed. The preliminary application gate and source/test handoff are separately preserved in [the final source/test gate](../final_validation_gate_v1/REPORT.md)."]
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")
    links = []
    for target in re.findall(r"\]\(([^)]+)\)", (OUT / "REPORT.md").read_text()):
        path = (OUT / target.split("#", 1)[0]).resolve()
        assert path.exists(), path
        links.append(str(path))
    inputs = dict(s["input_sha256"])
    inputs.update(protection["protected_paths_sha256"])
    inputs.update(visual_bindings)
    for p, h in inputs.items():
        assert sha(p) == h, p
    files = {str(p.relative_to(OUT)): sha(p) for p in sorted(OUT.rglob("*"))
             if p.is_file() and "__pycache__" not in p.parts and p.name != "verification_receipt.json"}
    receipt = {"status": "sealed_independent_Test1_v5_metric_source_review", "candidate_commit": CFG["expected_commit"],
               "native_root": CFG["native_root"], "completed_run_artifacts_verified": s["completed_artifacts_verified"],
               "worker_plan_source_files_verified": s["source_plan_files_verified"], "protected_total": 94,
               "protected_MAIN_Part2_originals": 62, "protected_candidate_Test1_copies": 9,
               "all_182_historical_regions_exact": True, "gross_count_losses": 0,
               "secondary_2418_all6_metrics_and_rows_exactly_equal": True,
               "raw_shuttle_xy_differences": 109, "raw_shuttle_support_differences": 107,
               "old_scene_barriers_preserved": 13, "new_source_supported_barrier": 14114,
               "full_native_crosspacket_source_proof_passed": True, "unsupported_metric_families_null": 10,
               "pipeline_root_acceptance_owned_by_orchestrator": True, "physical_accuracy_claimed": False,
               "new_neural_inference_by_reviewer": False, "input_sha256": inputs,
               "visual_review_bindings": visual_bindings, "local_links_verified": len(links), "artifact_sha256": files}
    with (OUT / "verification_receipt.json").open("x") as f:
        json.dump(receipt, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps({"status": receipt["status"], "artifacts": len(files), "links": len(links),
                      "report_sha256": sha(OUT / "REPORT.md"), "receipt_sha256": sha(OUT / "verification_receipt.json")}))


if __name__ == "__main__":
    main()
