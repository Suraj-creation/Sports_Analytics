"""Offline audit supplement for the mask component and cached semantic trials.

This never runs inference and never changes an inventory, prediction or historical
report. Issue recommendations are conditional on the evidence named below.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research.next_session_results import (
    EXPERIMENTS,
    LABELS,
    REFERENCES,
    ROOT,
    _run,
    common_comparison,
    digest,
    file_ref,
    read,
    read_csv,
)


def issue_recommendations() -> list[dict]:
    """Keep exact original IDs/titles; do not rewrite the structured inventory."""
    entries = [
        (
            "H01",
            "Conditionally recovered; scene/onset uncertainty remains",
            "Tracklet hybrid recovers GT23 at10769–11085 (+36,+7); conservative association can ignore one isolated "
            "10936 sample without erasing it. Same-camera edits and annotation preparation semantics "
            "remain unresolved.",
            [
                "next_20261105_temporal_audit/gt22_23_causal_trace.jsonl",
                "next_20261105_mask_tracklet_semantic/rally_comparison.csv",
                "next_20261105_contact_scene_foreground_v1/scene_foreground_metrics.json",
            ],
        ),
        (
            "H02",
            "Conditionally improved; terminal localization still unlabelled",
            "Fresh shuttle mask admits upper raw peaks and hybrid GT27 ends12954 (−12), replacing v1−218. "
            "The service-T peak still exists at12748; this does not prove all stationary observations are"
            " real landings.",
            [
                "next_20261105_mask_ceiling_component/hybrid_integrity_validation.json",
                "next_20261105_temporal_audit/gt27_causal_trace.jsonl",
                "next_20261105_mask_tracklet_semantic/rally_comparison.csv",
            ],
        ),
        (
            "H03",
            "Mask rejection cause reproduced; conditional improvement",
            "Strong raw14647/14684–94 peaks were rejected by the finite upward mask. New component admits them; "
            "hybrid starts14430 (+26) instead14701 (+297). Early close-up remains unobservable; no "
            "backdating justified.",
            [
                "next_20261105_shuttle_background_probe/comparisons.json",
                "next_20261105_contact_scene_perception_review/frame_evidence.json",
                "next_20261105_mask_tracklet_semantic/rally_comparison.csv",
            ],
        ),
        (
            "H04",
            "Measured original-reference regressions remain bounded",
            "GT4−71 andGT22−29 start errors persist. GT4 visible hold/launch precedes annotated return-like motion; "
            "GT22 evidence crosses a missed same-camera edit. Neither was silently corrected to labels.",
            [
                "next_20261105_temporal_audit/gt04_causal_trace.jsonl",
                "next_20261105_temporal_audit/gt22_23_causal_trace.jsonl",
                "next_20261105_mask_tracklet_semantic/comparison_original/comparison.json",
            ],
        ),
        (
            "H05",
            "All36 onsets classified; substantial residual late starts",
            "Source-bound audit distinguishes cancellation, missing processed motion, view exclusion and "
            "observability. "
            "Hybrid improves several cancelled starts; GT5+98,GT9+106,GT15+86 remain. No global offset fitted.",
            [
                "next_20261105_temporal_audit/all_onsets_ends.json",
                "next_20261105_mask_tracklet_semantic/rally_comparison.csv",
            ],
        ),
        (
            "H06",
            "End reasoning measured separately; residual terminal ambiguity",
            "Hybrid endMAE10.3333frames/max41; GT10−35/16+41/21−24 remain. No reviewed landing/contact labels "
            "establish a general endpoint refiner; original end regressions GT8/13/16 remain.",
            ["next_20261105_temporal_audit/all_onsets_ends.json", "next_20261105_mask_tracklet_semantic/metrics.json"],
        ),
        (
            "H07",
            "Boundary-quality limitation remains",
            "All36 matched does not imply precise onset: hybrid startMAE29.1389/max106, signedbias+22.75frames. "
            "Full tolerances, common denominators and worsened original rows remain explicit.",
            [
                "next_20261105_mask_tracklet_semantic/metrics.json",
                "next_20261105_mask_tracklet_semantic/comparison_original/comparison.json",
            ],
        ),
        (
            "H08",
            "Implemented bounded diagnostics; sporting calibration pending",
            "Opt-in candidate/mask/vote/background/rejection telemetry, explicit unsupported capabilities and cache18 "
            "binding checks added. Legacy17 decoding preserved. No full heatmap dump or calibrated probability claim.",
            [
                "next_20261105_shuttle_background_probe/manifest.json",
                "next_20261105_mask_ceiling_component/candidates.jsonl",
                "next_20261105_diagnostic_hardening_tests.log",
            ],
        ),
        (
            "H09",
            "Background and mask separated; remaining preprocessing effects open",
            "Rolling arm matches all1811 selected cached xy/support; fixed/zero backgrounds are separate controlled "
            "arms. Full component changes only flight mask. Resize/model localization accuracy remains unlabelled.",
            [
                "next_20261105_shuttle_background_probe/comparisons.json",
                "next_20261105_mask_ceiling_component/manifest.json",
                "next_20261105_mask_ceiling_component/hybrid_top_level_validation.json",
            ],
        ),
        (
            "H10",
            "Numerical defect reproduced; opt-in alternative not accepted for segmentation",
            "Reliability-aware absolute/residual motion provider and negative controls address ratio instability. "
            "Its conditional contact trial regresses GT27; legacy default retained and contact accuracy unmeasured.",
            [
                "next_20261105_contact_scene_sensitivity/contact_sensitivity.json",
                "next_20261105_contact_owner_validation/focused_tests.log",
                "next_20261105_contact_reliability_replay_v1/evaluation/metrics.json",
            ],
        ),
        (
            "H11",
            "Cadence/coverage remains an independent research gap",
            "Diagnostics expose fresh/carried and pose availability; event-triggered fresh pose/racket inference was "
            "not validated. Ledger counts are not reviewed physical impact accuracy.",
            [
                "next_20261105_contact_scene_perception_review/frame_evidence.json",
                "next_20261105_audit_repeat_control/comparison.json",
            ],
        ),
        (
            "H12",
            "Rejection provenance improved; association accuracy still unknown",
            "Bounded detector/ROI/NMS/capacity/carry diagnostics and four-player software controls retained. "
            "Reviewed identity/association episodes and four-player ground truth remain absent.",
            ["next_20261105_diagnostic_hardening_tests.log", "next_20261105_full_regression_after_mask.log"],
        ),
        (
            "H13",
            "Physical geometry accuracy still unvalidated",
            "Invalid-view/geometry gates preserved and mask geometry negative controls pass; no independent landmarks "
            "or airborne3D ground truth justify stronger accuracy claims.",
            [
                "next_20261105_mask_ceiling_component/geometry_controls.json",
                "next_20261105_mask_geometry_review/manifest.json",
            ],
        ),
        (
            "H14",
            "Known optional ReID degradation unchanged",
            "Actual run metadata retains unavailable ReID and unknown named identity. No weights installed, "
            "embeddings invented or restored-ReID boundary claim made.",
            ["next_20261105_fresh_control/inference.json"],
        ),
        (
            "H15",
            "Actual backend provenance measured; score calibration remains open",
            "Model/runtime bindings show TrackNet torchCUDA float16 and exact checkpoint; ORT CUDA provider lists "
            "are not per-node precision proof. Raw scores retain uncalibrated semantics.",
            ["next_20261105_mask_ceiling_component/manifest.json", "next_20261105_fresh_control/inference.json"],
        ),
        (
            "H16",
            "Temporal contracts preserved; hybrid cadence limitation explicit",
            "Frame-aligned evidence and bounded available future-anchor contracts remain. Hybrid caches preserve "
            "other perception, so changed segmentation feedback requires the separate fresh full-pipeline run.",
            [
                "next_20261105_mask_ceiling_component/hybrid_top_level_validation.json",
                "next_20261105_mask_tracklet_semantic/replay_metadata.json",
            ],
        ),
        (
            "H17",
            "Conservative recovery extended; real coverage limit remains",
            "Qualified singleton association recovers GT23 without idle starts/invented coordinates or wider top band. "
            "Curve support adds no interval gain with new mask and remains unnecessary for selected hybrid candidate.",
            [
                "next_20261105_mask_tracklet_semantic/replay_metadata.json",
                "next_20261105_mask_curve_semantic/replay_metadata.json",
            ],
        ),
        (
            "H18",
            "VOD/live validation limit remains",
            "No live-causal or zero-latency claim. Whole-chunk background and bounded semantic future windows are "
            "VOD mechanisms; streaming requires separate labelled timing and publication tests.",
            ["next_20261105_mask_ceiling_component/manifest.json", "next_20261105_fresh_control/inference.json"],
        ),
        (
            "H19",
            "Not triggered by Test1; generic mapping still unvalidated",
            "Verified source/proxy CFR30 frame alignment remains intact. High-FPS/VFR source-frame mapping needs "
            "independent temporal fixtures; software timestamp tests do not establish per-PTS ingestion correctness.",
            ["fresh_image_exit_v1/proxy_alignment.json", "next_20261105_audit_reproducible/validation.json"],
        ),
        (
            "H20",
            "Browser HLS seeking remains unexecuted",
            "No configured Chromium binary/verified browser transport available; Python tests cannot validate "
            "browser HLS seek/callback alignment. Runtime details recorded in initial audit.",
            ["research/next_evidence_tooling_review.md"],
        ),
        (
            "H21",
            "Runtime measured; isolation/checkpoint scaling still open",
            "Fresh-control stage/resources and component273.513s measured independently. Stage timers overlap; "
            "shared GPU/CPU environment and growing rollback history prevent an isolated speed comparison.",
            ["next_20261105_fresh_control/inference.json", "next_20261105_mask_ceiling_component/manifest.json"],
        ),
        (
            "H22",
            "Independent fresh v1 repeat now verified; candidate repeat pending",
            "New full v1 GPU repeat is byte/value exact for17268 frames,contact/stroke times,39intervals and metrics. "
            "Hybrid candidate remains conditional pending its own fresh pipeline; match-disjoint validation absent.",
            [
                "next_20261105_audit_repeat_control/comparison.json",
                "next_20261105_fresh_control/benchmark_metadata.json",
            ],
        ),
        (
            "H23",
            "Independent labels and generalization remain unavailable",
            "Only authorised Test1 development footage used. No reviewed match-disjoint singles/doubles, "
            "contact/localization/identity labels or alternative-model superiority claim.",
            [
                "next_20261105_fresh_control/benchmark_metadata.json",
                "next_20261105_mask_ceiling_component/manifest.json",
            ],
        ),
        (
            "H24",
            "Fixed and regression-tested without numerical changes",
            "Header-only comparison schema correction covers emptyGT/no-match cases. Original/v1/control full metrics "
            "and36row comparison CSVs remain byte-exact under the original recorded FPS representation.",
            ["next_20261105_audit_h24_bytes/parity.json", "next_20261105_audit_integrity/h24_h25_tests_green.log"],
        ),
        (
            "H25",
            "Executor and epoch provenance hardened for explicit Test1 harness",
            "Executed sources/harness,dirtydiff,config/trace/event hashes and recorded-format epoch resets pinned. "
            "All8 evidence/FSM factorial outputs reproduce exactly. Fixed Test1 experiment assumptions stay explicit.",
            [
                "next_20261105_audit_integrity/h25_event_epochs_comparison.json",
                "next_20261105_audit_provenance_event_epochs/executor_metadata.json",
            ],
        ),
        (
            "H26",
            "Historical evidence preserved; fixed finalizers not reused",
            "All1766 baselinehashes and28 experiment metrics reverified read-only; every new output gets a fresh path. "
            "Old fixed-output finalizers remain historical tools and were not invoked.",
            ["next_20261105_audit_post_tools/validation.json", "next_20261105_audit_reproducible/validation.json"],
        ),
        (
            "H27",
            "OCR warnings persist without measured rally causality",
            "Actual OCR models/fallback and unchanged hybrid OCR arrays recorded. Empty-result warnings are retained; "
            "no warning suppression presented as detection improvement.",
            [
                "next_20261105_fresh_control/execution.log",
                "next_20261105_mask_ceiling_component/hybrid_top_level_validation.json",
            ],
        ),
        (
            "H28",
            "Pre-existing warnings remain; unrelated edits avoided",
            "Required test/lint outcomes and deprecation warnings recorded. No dependency replacement or broad "
            "formatting cleanup claimed as a perception fix.",
            ["next_20261105_full_regression_after_mask.log", "next_20261105_precommit_checks.log"],
        ),
    ]
    inventory = read(ROOT / "research/next_session_failure_inventory.json")
    originals = {issue["id"]: issue for issue in inventory["issues"]}
    rows = []
    for issue_id, status, evidence, links in entries:
        refs = []
        for link in links:
            path = (ROOT if link.startswith("research/") else EXPERIMENTS) / link
            if not path.is_file():
                raise FileNotFoundError(path)
            refs.append(file_ref(path))
        rows.append(
            {
                "id": issue_id,
                "title": originals[issue_id]["title"],
                "original_status": originals[issue_id]["status"],
                "recommended_status": status,
                "rationale": evidence,
                "evidence": refs,
            }
        )
    assert set(originals) == {row["id"] for row in rows}
    return rows


def build(output: Path) -> dict:
    if output.exists():
        raise FileExistsError(output)
    gt = read_csv(LABELS, 30.0)
    directories = {**REFERENCES, "hybrid_tracklet": EXPERIMENTS / "next_20261105_mask_tracklet_semantic"}
    runs, predictions = {}, {}
    for name, directory in directories.items():
        runs[name], predictions[name] = _run(directory, gt, 30.0)
    curve = EXPERIMENTS / "next_20261105_mask_curve_semantic"
    tracklet = directories["hybrid_tracklet"]
    component = EXPERIMENTS / "next_20261105_mask_ceiling_component"
    metadata = read(component / "manifest.json")
    comparisons = {
        name: common_comparison(runs[name], runs["hybrid_tracklet"], predictions[name], predictions["hybrid_tracklet"])
        for name in REFERENCES
    }
    parity = {
        "prediction_csv_byte_equal": digest(tracklet / "predicted_rallies.csv")
        == digest(curve / "predicted_rallies.csv"),
        "full_metrics_value_equal": read(tracklet / "metrics.json") == read(curve / "metrics.json"),
    }
    assert all(parity.values())
    source_root = Path(metadata["recorded_run"])
    cache_roots = list((source_root / "runtime/sessions").glob("*/perception"))
    assert len(cache_roots) == 1
    source_ok = all(digest(cache_roots[0] / name) == value for name, value in metadata["source_cache_sha256"].items())
    output_roots = list((component / "runtime/sessions").glob("*/perception"))
    assert len(output_roots) == 1
    output_ok = all(digest(output_roots[0] / name) == value for name, value in metadata["output_cache_sha256"].items())
    events = [json.loads(line) for line in (component / "events.jsonl").read_text().splitlines()]
    assert {event["type"] for event in events} == {"calibration", "format_decision"} and len(events) == 2
    assert not (component / "predicted_rallies.csv").exists()
    data = {
        "schema": "next-session-hybrid-review:v1",
        "reporter": file_ref(Path(__file__)),
        "original_inventory": file_ref(ROOT / "research/next_session_failure_inventory.json"),
        "scope": (
            "OFFLINE CONDITIONAL HYBRID: fresh TrackNet-only full video + cached other perception + "
            "semantic replay; NOT fresh full-pipeline inference"
        ),
        "runs": runs,
        "comparisons": comparisons,
        "curve_extra_support_negative_control": parity,
        "component_provenance": {
            "manifest": file_ref(component / "manifest.json"),
            "source_cache_hashes_reverified": source_ok,
            "output_cache_hashes_reverified": output_ok,
            "source_cache_count": len(metadata["source_cache_sha256"]),
            "output_cache_count": len(metadata["output_cache_sha256"]),
            "reference_events_only": [event["type"] for event in events],
            "no_component_prediction_csv": True,
            "runtime": metadata["runtime"],
            "gpu": metadata["gpu"],
            "counters": metadata["counters"],
            "elapsed_seconds": metadata["elapsed_seconds"],
            "integrity_checks": file_ref(component / "hybrid_integrity_validation.json"),
            "non_shuttle_top_level_checks": file_ref(component / "hybrid_top_level_validation.json"),
        },
        "no_ground_truth_in_inference_review": {
            "component_harness": file_ref(ROOT / "research/next_shuttle_mask_experiment.py"),
            "semantic_harness": file_ref(ROOT / "research/replay_rally_evidence.py"),
            "imported_decoder": file_ref(ROOT / "research/audit_c_paired_inference.py"),
            "finding": (
                "Component and semantic harnesses copy GT digest only. No annotation file values are read. "
                "Component uses original images, recorded geometry/view, original background chronology and "
                "identical checkpoint. Only decode is imported from old paired probe; its case-selection main"
                " is not invoked. Original rally intervals are copied to hybrid output only after neural loop"
                " for reference parity, and never drive masks/shuttle observations. Semantic replay consumes "
                "own hybrid caches and only calibration/format reference events; contacts and rallies are "
                "recomputed. Evaluation labels enter this offline review only."
            ),
            "limits": (
                "Code/data-flow inspection plus input/output hash checks; this is not a general formal "
                "noninterference proof. Cached player cadence depends on original segmentation, so full "
                "production inference is still required."
            ),
        },
        "issue_recommendations": issue_recommendations(),
        "limitations": metadata["limitations"],
    }
    assert source_ok and output_ok
    output.mkdir(parents=True, exist_ok=False)
    (output / "hybrid_review.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    lines = [
        "# Conditional hybrid comparison and issue audit",
        "",
        data["scope"],
        "",
        "All 35 fresh-v1 matches remain; GT23 is newly matched. No start/end boundary worsens versus "
        "v1. Curve support adds no interval gain: prediction bytes and complete metrics are "
        "identical.",
        "",
    ]
    for reference, comparison in comparisons.items():
        lines += [
            f"Fixed common matched rows versus {reference}: {comparison['denominator']}.",
            "",
            "| Error | Before MAE | After MAE | Worsened GT |",
            "| --- | --- | --- | --- |",
        ]
        for name, obj in comparison["errors"].items():
            lines.append(f"| {name} | {obj['before']['mae']} | {obj['after']['mae']} | {obj['worsened_gt_ids']} |")
        lines += [""]
    lines += [
        "The component changes only shuttle values/support and expected cache provenance; all other "
        "cached frame/top-level fields remain unchanged. It processed all17268 frames with a48-frame "
        "EOF chunk. The inherited reference intervals are explicitly reference-only, and only two "
        "calibration/format events are reused. No GT values enter inference. All metrics, all36 rows,"
        " unmatched predictions, geometric topology, exact provenance and hash rechecks are in "
        "hybrid_review.json.",
        "",
        "Original-reference regressions remain GT4/22 starts and GT8/13/16 ends. GT5/9/15 remain "
        "markedly late. Contact reliability, scene editing, generalization, doubles accuracy, browser"
        " seek, live and VFR mapping remain separate limits.",
        "",
        "| Issue | Recommended status | Evidence limitation |",
        "| --- | --- | --- |",
    ]
    for row in data["issue_recommendations"]:
        lines.append(f"| {row['id']}: {row['title']} | {row['recommended_status']} | {row['rationale']} |")
    lines.append("")
    (output / "hybrid_review.md").write_text("\n".join(lines))
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    data = build(parser.parse_args().output.resolve())
    print(
        json.dumps(
            {
                "detection": data["runs"]["hybrid_tracklet"]["metrics"]["detection"],
                "comparisons": {
                    name: {
                        key: {
                            "before": item["before"]["mae"],
                            "after": item["after"]["mae"],
                            "worsened": item["worsened_gt_ids"],
                        }
                        for key, item in comp["errors"].items()
                    }
                    for name, comp in data["comparisons"].items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
