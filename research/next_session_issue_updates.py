"""Attach a source-specific issue review without replacing handoff measurements.

Run only after the completed fresh-run results helper. The original inventory
bytes and all old status strings are preserved in a new revision directory.
No inference, annotation editing or historical result regeneration occurs here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# State, measured conclusion, remaining limitation, next discriminating action.
DISPOSITIONS = {
    "H01": (
        "partially_resolved_scene_authority_open",
        "Qualified singleton association recovers the later GT23 split while retaining GT22 as a separate interval.",
        (
            "Both same-camera edits remain unflagged; the annotated GT23 onset precedes the visible edit "
            "and its convention is unknown."
        ),
        (
            "Review independent same-camera cuts and fast-play/occlusion controls before adopting a "
            "foreground continuity detector."
        ),
    ),
    "H02": (
        "interval_improved_terminal_and_contact_validity_open",
        (
            "New upper-flight admission restores source-visible re-entry. The conditional GT27 end "
            "improves from 12748 to 12954."
        ),
        (
            "The T attractor and stationary-end proposal persist. Recovery still uses suspect legacy "
            "contact 12766; interval accuracy does not validate this contact or landing."
        ),
        (
            "Completed suppression and reliable-contact controls prove the dependency. Test richer "
            "association with reviewed floor/landing and close-rally controls; the fixed-radius "
            "cluster counterfactual failed and must not be widened to fit this case."
        ),
    ),
    "H03": (
        "partially_resolved_demonstrated_mask_loss",
        (
            "Identical-context fresh inference exposes 16 strong GT31 peaks rejected by the old mask; "
            "admission restores ordinary top-exit continuity without curve support."
        ),
        (
            "Frames 14651–14682 remain subthreshold/physically unverified. The pickup close-up cannot "
            "justify backdating the start into unobservable footage."
        ),
        (
            "Review launch/contact onset semantics and the remaining visibility gap independently; retain "
            "missing observations rather than inventing coordinates."
        ),
    ),
    "H04": (
        "open_reproduced_and_bounded",
        (
            "GT4/22 early starts remain unchanged by the selected mask/association changes. GT22 contact "
            "context crosses an unflagged 10603→10604 edit."
        ),
        (
            "GT4's earlier high-flight/feed sequence has ambiguous sporting onset; detecting the GT22 "
            "edit alone does not prove its first weak contact will disappear."
        ),
        (
            "Obtain reviewed onset/contact/cut labels, then test independent provisional-start validation "
            "while retaining GT2/19/20."
        ),
    ),
    "H05": (
        "partially_resolved_causal_classes_recorded",
        (
            "All 36 rows have source-bound first-provider/processed/motion/contact/start/cancellation/end "
            "records; upstream admission rescues several cancelled early events."
        ),
        (
            "Late starts persist through weak motion, view exclusion, ambiguous preparation and "
            "cancellations. First provider output is not a verified sporting onset."
        ),
        (
            "Review remaining large delays by causal group, using current-frame pose/racket acquisition "
            "only where it can distinguish competing explanations."
        ),
    ),
    "H06": (
        "improved_residual_terminal_evidence_open",
        (
            "End errors are evaluated independently; the major GT27 truncation improves and every "
            "remaining end proposal stays traceable."
        ),
        (
            "Neither static coordinates nor slow players establish landing. GT10/16 and other residual "
            "end errors remain; physical terminal labels are absent."
        ),
        (
            "Review terminal contact/landing/disappearance separately and test reversible terminal "
            "validation without increasing merge gaps."
        ),
    ),
    "H07": (
        "improved_fine_localization_open",
        (
            "Full metrics retain start/end MAE, RMSE, median, bias, P90, max and all requested "
            "tolerances with both denominators."
        ),
        (
            "High detection recall does not establish frame-level boundaries; multi-second onset outliers "
            "and early GT4/22 remain."
        ),
        "Resolve annotation conventions and evaluate starts and ends independently on reviewed unseen matches.",
    ),
    "H08": (
        "fixed_bounded_opt_in_observability",
        (
            "Codec 18 diagnostics retain ranked components, raw/masked peaks, selection/rejection "
            "reasons, entropy, model votes and background digest with exact frame/provider identity."
        ),
        (
            "Top-k connected components above a diagnostic floor are not every local peak or a calibrated "
            "posterior. Unrecorded historical heatmaps remain unavailable."
        ),
        (
            "Use bounded evidence for association experiments; extend the versioned schema only when a "
            "concrete missing field is required."
        ),
    ),
    "H09": (
        "partially_resolved_factors_isolated",
        (
            "Three background arms hold checkpoints/resize/masks/chunks fixed; rolling reproduces all "
            "1811 observations/supports exactly. Fixed-startup removes 24/24 T outputs but does not "
            "recover the true track."
        ),
        (
            "Zero concat input is not a separately trained background-free model. Resize-only and broader "
            "background generalization remain unmeasured."
        ),
        (
            "Evaluate context/association first; use controlled interpolation/background ablations with "
            "independently reviewed localization controls."
        ),
    ),
    "H10": (
        "open_numerical_defect_reproduced_alternative_not_promoted",
        (
            "The optional reliable-motion provider removes unstable relative gain, exposes slope "
            "sensitivity and passes weak-launch/zero-incoming controls."
        ),
        (
            "Its old-perception semantic trial newly misses GT27. The selected candidate retains legacy "
            "scoring, and suspect 12766 still has saturated ratio cues."
        ),
        (
            "Both completed controls confirm the coupling. Validate static-to-track association and "
            "reviewed contact precision/recall before replacing the provider; the new-mask reliable "
            "trial also fragments GT27."
        ),
    ),
    "H11": (
        "open_sampling_and_label_limit",
        (
            "Fresh/carried boxes, actual pose stride, keypoint availability and racket evidence are "
            "visible in the new bounded replay."
        ),
        (
            "No event-triggered pose/racket policy was accepted, and sparse evidence has no independently "
            "measured contact-error attribution."
        ),
        (
            "Test current-frame event-triggered acquisition on reviewed uncertain contacts with "
            "compute-cost and frontier controls."
        ),
    ),
    "H12": (
        "partially_fixed_telemetry_labels_missing",
        (
            "Player diagnostics expose raw-query counters/top-k boxes, rejection/ROI reasons, carried "
            "state and tracker admission/capacity without changing decisions."
        ),
        (
            "Historical rejected boxes cannot be recreated from caches, and no reviewed "
            "detection/association/identity labels were added."
        ),
        (
            "Review ROI, carried detections and identity episodes on independent singles/four-player "
            "sequences before changing admission or association."
        ),
    ),
    "H13": (
        "open_physical_validation_limit",
        (
            "Invalid/offscreen geometry and adjacent columns retain regression controls; floor and player "
            "admission rules remain unchanged."
        ),
        "Full-height court columns are an image prior, not 3D airborne ownership, line-call or landing accuracy.",
        "Review projected court geometry and airborne multi-court overlap on authorized independent footage.",
    ),
    "H14": (
        "known_optional_provider_unavailable",
        (
            "Actual runtime records preserve unavailable OSNet/ReID degradation and unknown named "
            "identity; no embeddings or names were fabricated."
        ),
        (
            "Tracking episodes, people, teams and scoring slots remain distinct. ReID accuracy and its "
            "boundary effect remain unknown."
        ),
        (
            "Only a separate authorized weight/license/hash/runtime/identity-labelled experiment can "
            "justify enabling ReID."
        ),
    ),
    "H15": (
        "partially_resolved_explicit_semantics_and_runtime",
        (
            "Telemetry labels raw model support, heuristic fusion and fit sensitivity explicitly. Actual "
            "runtime providers/dtypes/fallbacks/model hashes are retained."
        ),
        (
            "No score calibration was fitted. ORT provider registration alone does not establish every "
            "operator's GPU placement or precision."
        ),
        (
            "Calibrate only against independent labels; use provider profiling if node-level execution "
            "attribution is required."
        ),
    ),
    "H16": (
        "protected_alignment_and_fresh_feedback_checked",
        (
            "The selected profile receives a full production run after conditional replay; frame-aligned "
            "participant and semantic-frontier contracts remain tested."
        ),
        (
            "Cached replay is not fresh perception and cannot reproduce changed cadence. VOD context may "
            "contain declared bounded lookahead."
        ),
        (
            "Compare fresh own-cache replay and publication boundaries; never substitute accumulated "
            "future activity for current-frame evidence."
        ),
    ),
    "H17": (
        "partially_resolved_association_and_admission",
        (
            "Qualified-event singleton association handles GT23's competing observation. Corrected "
            "admission makes ordinary upper-exit proof sufficient for GT31; curve support adds no "
            "selected-run benefit."
        ),
        (
            "The conservative cue still requires coherent observed brackets and bounded same-context "
            "loss; it is not general occlusion recovery."
        ),
        (
            "Evaluate multi-hypothesis continuity with explicit ambiguity/static/floor controls; keep "
            "curve support disabled without incremental evidence."
        ),
    ),
    "H18": (
        "open_vod_live_mode_limit",
        (
            "Only available episode-window observations are consumed; tests preserve frontier/context "
            "barriers and no reconstructed coordinate becomes fresh evidence."
        ),
        (
            "This is buffered VOD execution, not validated causal-live contact/rally inference. Declared "
            "lookahead must not be hidden."
        ),
        "Build a streaming availability/latency evaluation with frontier timestamps before making live-mode claims.",
    ),
    "H19": (
        "open_generic_source_mapping_risk",
        (
            "Actual Test1 source/proxy alignment is verified CFR30 with zero-origin half-open export and "
            "actual recorded FPS conversion."
        ),
        "No end-to-end generic VFR/unsupported/high-FPS mapping fix or new validation was established.",
        (
            "Use explicit decoded-source/proxy timestamp maps and reviewed variable-rate fixtures in a "
            "separate ingestion change."
        ),
    ),
    "H20": (
        "open_browser_hls_validation_gap",
        "The offline renderer records exact original PTS and passed a static Firefox smoke review.",
        (
            "Static HTML playback does not validate application HLS/MSE seeking or browser callback "
            "alignment; no compatible Playwright browser was installed."
        ),
        (
            "Run the existing seek harness in an available supported browser without altering deployment "
            "or extrapolating offline errors to UI timing."
        ),
    ),
    "H21": (
        "partially_measured_rollback_profiling_open",
        (
            "Full runs retain stage wall aggregates, worker CPU/RSS, sampled GPU memory and backend "
            "records; overlaps and scope are stated."
        ),
        (
            "Short diagnostic CPU work overlapped each control/final run startup. Stage aggregates "
            "overlap and rollback-history growth was not isolated."
        ),
        (
            "Profile rollback memory/latency separately and use repeated isolated runs before attributing "
            "cost to a particular algorithm."
        ),
    ),
    "H22": (
        "v1_repeat_verified_selected_repeat_pending",
        (
            "An independent unchanged full-video control exactly reproduces 17268 frame records, 447 "
            "contact/stroke timestamps,39 interval/reason triples and CSV bytes from v1."
        ),
        (
            "The new selected profile has one full inference validation; semantic or component replays "
            "are not additional complete repeats."
        ),
        "Repeat the selected profile and run independently reviewed validation before default or production promotion.",
    ),
    "H23": (
        "open_independent_labels_and_generalization",
        (
            "A match-disjoint validation matrix and primary-source alternative-method screening are "
            "recorded; no new model or unrelated footage was accessed."
        ),
        (
            "Test1 is development footage. No reviewed doubles/contact/shot/identity/localization "
            "validation set is available in scope."
        ),
        (
            "Obtain authorized independent match footage and reviewed component/onset/end labels, then "
            "freeze the profile before evaluation."
        ),
    ),
    "H24": (
        "fixed_export_contract",
        (
            "Empty-GT comparison exports now retain the existing 20-column header. Red/green tests and "
            "original/v1/control byte parity pass."
        ),
        "This changes no primary seven-column prediction schema, interval, matching rule or Test1 metric.",
        "Retain empty-input and nonempty-byte regression controls.",
    ),
    "H25": (
        "fixed_executor_provenance_and_epoch_assumptions",
        (
            "Ablations separate executor snapshots from trace-generator provenance, derive recorded "
            "format resets and refuse existing outputs; eight historical variant CSV/metric results "
            "remain exact."
        ),
        "The research tools still explicitly target Test1 and are not generic independent-dataset executors.",
        "Preserve separate generator/executor identity and explicit dataset scope in future experiments.",
    ),
    "H26": (
        "mitigated_and_integrity_verified",
        (
            "New outputs refuse reuse; safe audits verify1766 frozen files, 86 historical source blobs, "
            "models/inputs and all 28 historical metric objects."
        ),
        (
            "Ignored local evidence still requires preservation; historical hardcoded finalizers remain "
            "historical and were not rerun."
        ),
        (
            "Use explicit new output directories and the safe verifier; archive source-bound evidence "
            "without Git media/cache additions."
        ),
    ),
    "H27": (
        "unchanged_noncausal_warning",
        (
            "RapidOCR empty-result warnings remain visible in preserved logs; valid installed models and "
            "actual backends are recorded."
        ),
        "No direct rally-boundary causality is established; suppressing a warning would not validate OCR or scoring.",
        "Investigate separately with reviewed scoreboard evidence if OCR accuracy or warning handling is required.",
    ),
    "H28": (
        "unchanged_noncausal_maintenance",
        (
            "The application/engine/sport suite (1966) and benchmark suite (77) pass, totaling 2043 "
            "tests with 19 pre-existing deprecation warnings; changed Python lint passes."
        ),
        (
            "An unrelated existing plugin string-format preference and framework deprecations remain; no "
            "boundary mechanism is attributed to them."
        ),
        "Handle framework/format maintenance separately without broadening the research diff.",
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--revision-output", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    metadata = json.loads((run / "benchmark_metadata.json").read_text())
    if metadata.get("status") != "completed":
        raise ValueError("a completed fresh full-pipeline run is required")
    metrics = json.loads((run / "metrics.json").read_text())
    with (run / "rally_comparison.csv").open() as stream:
        rows = {int(row["gt_rally"]): row for row in csv.DictReader(stream)}
    # These are report-review preconditions, never inputs to inference. A fresh
    # cadence regression must trigger an explicit review rather than inheriting
    # the earlier conditional conclusions below.
    if set(rows) != set(range(1, 37)) or metrics["detection"]["false_negatives"] != 0:
        raise ValueError("fresh result differs from the reviewed complete match set; review dispositions first")
    expected = {4: (1803, 2167), 22: (10578, 10737), 23: (10769, 11085), 27: (12455, 12954), 31: (14430, 15171)}
    for gt_id, interval in expected.items():
        row = rows[gt_id]
        if (int(row["pred_start_frame"]), int(row["pred_end_frame"])) != interval:
            raise ValueError(f"GT{gt_id} differs from the reviewed interval; review dispositions first")
    supplement = ROOT / "artifacts/benchmarking/experiments/next_20261105_audit_hybrid_comparison/hybrid_review.json"
    recommendations = {item["id"]: item for item in json.loads(supplement.read_text())["issue_recommendations"]}
    comparison = json.loads((run / "comparison.json").read_text())["experiment"]
    inventory_path = ROOT / "research/next_session_failure_inventory.json"
    original_bytes = inventory_path.read_bytes()
    inventory = json.loads(original_bytes)
    if "next_session_review" in inventory:
        raise ValueError("inventory already revised; review it explicitly instead of replacing the review")
    if {issue["id"] for issue in inventory["issues"]} != set(DISPOSITIONS):
        raise ValueError("the complete H01–H28 register is required")
    args.revision_output.mkdir(parents=True, exist_ok=False)
    (args.revision_output / "handoff_inventory.json").write_bytes(original_bytes)
    script_bytes = Path(__file__).read_bytes()
    (args.revision_output / "executor.py").write_bytes(script_bytes)
    common_evidence = [
        "research/next_session_root_cause_report.md",
        "research/next_session_final_report.md",
        "research/next_session_validation_matrix.md",
        "research/next_session_experiment_results.json",
        "artifacts/benchmarking/experiments/next_20261105_fresh_air_tracklet_all36_model_firsts/"
        "all36_model_temporal_firsts.json",
    ]
    for issue in inventory["issues"]:
        state, conclusion, limitation, action = DISPOSITIONS[issue["id"]]
        issue["handoff_status"] = issue["status"]
        issue["status"] = state
        issue["next_session_review"] = {
            "source_commit": metadata["git_commit_sha"],
            "conclusion": conclusion,
            "limitation": limitation,
            "next_action": action,
            "evidence": common_evidence,
            "component_and_control_evidence": recommendations[issue["id"]]["evidence"],
            "fresh_run_evidence": str(run.relative_to(ROOT)),
        }
        if issue["id"] == "H20":
            issue["next_session_review"]["browser_runtime_evidence"] = "research/next_evidence_tooling_review.md"
    inventory["next_session_review"] = {
        "schema": "badminton-next-session-review:v1",
        "date": "2026-11-05",
        "source_commit": metadata["git_commit_sha"],
        "handoff_inventory_sha256": hashlib.sha256(original_bytes).hexdigest(),
        "executor_sha256": hashlib.sha256(script_bytes).hexdigest(),
        "fresh_run": str(run.relative_to(ROOT)),
        "metrics": metrics,
        "per_gt_selected": comparison["per_gt"],
        "selected_fragmentation": comparison["fragmentation"],
        "selected_unmatched_predictions": metrics["unmatched_predictions"],
        "promotion": "experimental opt-in only; no default promotion",
        "historical_fields": "All handoff metrics, rows, hashes, evidence, controls and old statuses remain preserved.",
    }
    updated = (json.dumps(inventory, indent=2, allow_nan=False) + "\n").encode()
    (args.revision_output / "revised_inventory.json").write_bytes(updated)
    inventory_path.write_bytes(updated)
    print(json.dumps({"issues_reviewed": len(DISPOSITIONS), "fresh_run": str(run)}))


if __name__ == "__main__":
    main()
