"""Offline boundary review of completed source-bound evidence, never inference input."""

# Long literal sentences are report content rather than executable expressions.
# ruff: noqa: E501

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/benchmarking/experiments"
FIRSTS = BASE / "next_20261105_fresh_air_tracklet_all36_model_firsts_v2"
AUDIT = BASE / "next_20261105_fresh_air_tracklet_temporal_audit"
SEMANTIC = BASE / "next_20261105_fresh_air_tracklet_semantic"
PIXELS = BASE / "next_20261105_temporal_source_onset_review/review.json"
SCENE = BASE / "prod_20261105_scene_final_validation/cached_effect_review.json"

ONSET = {
    1: "Weak initial model support; admitted 248, movement 261, contact starts 264. Earlier physical onset unreviewed.",
    2: "Short motion-confirmation delay; recovered match retained. Physical onset convention unreviewed.",
    3: "Short motion-confirmation delay. Physical onset convention unreviewed.",
    4: "Pre-label contact 1803 and high serve/feed retained through upper flight. First-return versus serve convention unresolved.",
    5: "Candidate 2210 closes at 2254 after loss and cancels 2277; next start 2308. Severe provisional-event continuity loss.",
    6: "Raw 2560 is excluded close-up. Wide view 2574, valid context 2576, contact 2578; no close-up backdate justified.",
    7: "Near-exact confirmation. Separate 2895 preparation/2917 launch is a retained maturity-gate negative control.",
    8: "Annotation begins in reviewed preparation close-up. Accepted 3465 precedes sustained movement 3519; mixed visibility and sparse motion.",
    9: "Raw 3753 is excluded close-up. Candidate 3771 cancels 3827 after loss ending 3804; surviving start 3857. Mixed causes.",
    10: "Provider begins 4260, movement 4268, contact start 4272. Earlier physical onset unreviewed.",
    11: "Provider 4876 precedes movement 4898/contact 4901. Sparse/weak-motion onset; physical onset unreviewed.",
    12: "Earlier preparation candidate 5379 cancels 5434; current accepted 5448, motion start 5455. Earlier physical onset unreviewed.",
    13: "Raw 5958 is excluded close-up; main view 5960, valid 5962, first accepted 5976, contact 5979.",
    14: "Raw 6382 is excluded close-up; accepted 6396/motion 6397 lacks sustained confirmation until start 6450.",
    15: "Candidate 6732 closes at 6750 and cancels 6773; start 6802. Severe loss before event maturity; no global duration reduction.",
    16: "Raw 6976 is excluded close-up; wide 6991/valid 6993 precede accepted 7005 and start 7006.",
    17: "Contact-confirmed 7535 shortly after provider 7532. Physical onset unreviewed.",
    18: "Provider 7952, contact start 7953, motion 7954. Physical onset unreviewed.",
    19: "First provider 8106 and motion 8107 yield start 8110. Previously recovered case retained.",
    20: "Main view 8697/valid 8699, accepted 8708, movement 8709, start 8715. Previously recovered long rally retained.",
    21: "Short provider/motion-confirmation delay, 10247/10248 to start 10250. Physical onset unreviewed.",
    22: "Weak pre-edit contact starts 10578 across content edit 10604. Explicit scene counterfactual changes start to 10605; annotation 10607.",
    23: "Preparation before real edit 10770; old contact start 10769 crosses edit. Later singleton continuity is separate; scene start 10777 regresses 8 frames.",
    24: "Contact-confirmed start 11274 after provider 11273. Physical onset unreviewed.",
    25: "Candidate 11570 closes 11587 and cancels 11610; new contact starts 11613. Provisional continuity loss.",
    26: "Short motion confirmation: provider 11980/motion 11982, start 11982. Physical onset unreviewed.",
    27: "Near-exact onset. Later recovered continuity depends on suspect T contact 12766 in historical selected run; boundary alone is insufficient.",
    28: "Source-visible wide-view upper streak at 13054 is rejected by geometry reacquisition; no accepted return until 13112. Image validity and projection differ.",
    29: "Provider 13683/motion 13684 to start 13686. Previously recovered match retained; physical onset unreviewed.",
    30: "Short motion confirmation from first provider 14219 to start 14222. Physical onset unreviewed.",
    31: "Raw 14405 is excluded close-up; main 14425/valid 14427, start 14430. Upper-mask repair preserves later flight without close-up backdate.",
    32: "Short motion confirmation from provider 15353/motion 15354 to start 15354. Physical onset unreviewed.",
    33: "Start 15602 closes 15615 and cancels 15638 after loss; surviving start 15664. Provisional continuity loss.",
    34: "Pre-label contact 15983 precedes content edit 15985; scene counterfactual starts 16000. Earlier physical onset remains unadjudicated.",
    35: "Provider 16517/motion 16518 yield start 16521. Physical onset unreviewed.",
    36: "Weak raw support before provider 17072/motion start 17074. Physical onset unreviewed; endpoint is not EOF finalization.",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.report = args.report.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    if args.report.exists():
        raise FileExistsError(args.report)
    rows = json.loads((FIRSTS / "all36_model_temporal_firsts.json").read_text())
    first_manifest = json.loads((FIRSTS / "manifest.json").read_text())
    temporal_manifest = json.loads((AUDIT / "manifest.json").read_text())
    replay = json.loads((SEMANTIC / "replay_metadata.json").read_text())
    assert len(rows) == 36 and [row["gt_rally"] for row in rows] == list(range(1, 37))
    assert sha(FIRSTS / "all36_model_temporal_firsts.json") == first_manifest["output_sha256"]
    assert sha(SEMANTIC / "fsm_trace.jsonl") == first_manifest["own_semantic_trace_sha256"]
    assert temporal_manifest["trace_cache_bytes_and_source_identity_exact"] is True
    hashes = {Path(key).name: value for key, value in temporal_manifest["cache_sha256"].items()}
    assert hashes == replay["cache_sha256"]
    for path, expected in temporal_manifest["cache_sha256"].items():
        assert sha(ROOT / path) == expected
    assert sha(SEMANTIC / "predicted_rallies.csv") == temporal_manifest["prediction_sha256"]
    physical = {row["gt_rally"]: row for row in json.loads(PIXELS.read_text())["notes"]}
    scene = json.loads(SCENE.read_text())
    changed = {row["gt_rally"]: row for row in scene["scene"]["changed_rows"]}
    compact = []
    for row in rows:
        number = row["gt_rally"]
        model = row["first_recorded_raw_model_peak_above_inference_threshold"]
        end = row["matched_terminal_chain"]
        record = {
            "gt": number,
            "ground_truth_interval": row["interval"],
            "historical_selected": row["matched_interval"],
            "signed_error_start_end": [row["signed_start_error_frames"], row["signed_end_error_frames"]],
            "model_provider_processed_motion_player_contact_firsts": [
                model["frame"] if model else None,
                row["first_accepted_provider_output_in_onset_review"],
                row["first_processed_observation"],
                row["first_adjacent_movement_over_start_speed"],
                row["first_aligned_participant_motion"],
                row["first_accepted_contact"],
            ],
            "scope": "Model/provider firsts cover onset_review_half_open; processed/motion/player/contact firsts cover GT interval.",
            "onset_review_half_open": row["onset_review_half_open"],
            "onset_status": ONSET[number],
            "surviving_proposal": row["surviving_start_proposal"],
            "candidate_cancellations": row["candidate_cancellations"],
            "onset_diagnostic_coverage": row["onset_model_diagnostic_coverage"],
            "terminal": {k: v for k, v in end.items() if k != "frames_around_endpoint"},
            "physical_earlier_onset": physical.get(
                number, {"note": "Unknown: no reviewed source evidence establishes first physical onset."}
            ),
            "scene_counterfactual": changed.get(number),
        }
        compact.append(record)
    result = {
        "mode": "offline synthesis of historical fresh own-cache diagnostics and separately labelled cached counterfactuals",
        "new_fresh_results": "pending; not read by this baseline report",
        "rows": compact,
        "cache_files_validated": len(hashes),
        "labels_used_only_for_completed_offline_grouping": True,
    }
    (args.output / "all36_boundary_status.json").write_text(json.dumps(result, indent=2) + "\n")
    sources = [
        Path(__file__),
        FIRSTS / "all36_model_temporal_firsts.json",
        FIRSTS / "manifest.json",
        AUDIT / "manifest.json",
        SEMANTIC / "replay_metadata.json",
        SEMANTIC / "fsm_trace.jsonl",
        PIXELS,
        SCENE,
    ]
    provenance = {str(path.relative_to(ROOT)): sha(path) for path in sources}
    (args.output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    (args.output / "executed_boundary_review.py").write_bytes(Path(__file__).read_bytes())
    lines = [
        "# Production boundary review",
        "",
        "## Scope and source identity",
        "",
        "This is an offline review of the completed historical selected fresh inference at source `33d3a5b`, not a result from the production-continuation GPU pair. Its exact own-cache semantic trace is bound to all 288 cache-file hashes and the prediction CSV. These hashes were checked again while building this report. The original frames, labels, historical metrics and experimental evidence are unchanged.",
        "",
        "The canonical video has 17,268 frames at 30 FPS. All intervals are zero-origin and half-open. Signed error is prediction minus annotation. An accepted coordinate or contact is a model/heuristic hypothesis, not physical ground truth. The onset probes have exact coordinate/support parity with the historical caches in their declared paired scopes; 5,081 diagnostic frames cover all 36 onset-review windows. They are component inference evidence, not additional full-pipeline inference.",
        "",
        "The firsts column lists **model / provider / processed / movement / player motion / accepted contact**. Model/provider firsts cover the declared review window between annotation and surviving onset; the remaining firsts cover the annotated span. In early-start rows these different scopes must not be interpreted as a single chronological chain. The machine-readable artifact retains both windows and complete candidate cancellations.",
        "",
        "## All 36 onset classifications",
        "",
        "| GT | Historical prediction | Signed start/end | Firsts | Onset and observability status |",
        "|---|---|---|---|---|",
    ]
    for record in compact:
        start, end = record["historical_selected"]
        errors = "/".join(f"{error:+d}" for error in record["signed_error_start_end"])
        firsts = "/".join(
            str(value) if value is not None else "unknown"
            for value in record["model_provider_processed_motion_player_contact_firsts"]
        )
        lines.append(f"| {record['gt']} | [{start}, {end}) | {errors} | {firsts} | {record['onset_status']} |")
    lines += [
        "",
        "## All 36 terminal classifications",
        "",
        "`gap` is an evidence-timeout decision; `stationary` is an engine reason, not a verified landing. The evidence kind at the proposal is listed separately because a retained stationary hypothesis can be acted on when the current observation is missing. Player motion cannot establish a terminal contact. No row has independently reviewed landing/contact-time labels, so the physical terminal mechanism remains unknown even where the numerical boundary is close.",
        "",
        "| GT | Signed end | Final reason | Proposal → close → publication | Evidence at proposal | Terminal status |",
        "|---|---|---|---|---|---|",
    ]
    for record in compact:
        terminal = record["terminal"]
        evidence = terminal["evidence_at_proposal"]
        end_error = record["signed_error_start_end"][1]
        status = "Physical endpoint unverified; " + (
            "early" if end_error < 0 else "late" if end_error > 0 else "annotation-aligned"
        )
        if record["gt"] == 16:
            status += "; scene counterfactual worsens +41 to +44"
        if record["gt"] == 27:
            status += "; intermediate closure at 12748 depends on suspect contact reopening"
        if record["gt"] == 31:
            status += "; stationary reason has no current speed at proposal"
        speed = evidence["speed"]
        evidence_text = evidence["kind"] + (f", speed {speed:.4f}" if speed is not None else ", speed unknown")
        chain = " → ".join(str(terminal[key]) for key in ("end_proposal_frame", "closed_frame", "finalization_frame"))
        lines.append(
            f"| {record['gt']} | {end_error:+d} | {terminal['reason']} | {chain} | {evidence_text} | {status} |"
        )
    lines += [
        "",
        "## Discriminating mechanisms and bounds",
        "",
        "Cancelled in-span provisional candidates remain material at GT5, GT9, GT15, GT25 and GT33. Waiting through an unsupported gap cannot confer event maturity. The existing qualified association deliberately does not extend these events merely because that improves an annotation score. Sparse early points without sustained motion are a separate mechanism at GT8 and GT14. GT12's earlier candidate predates the supplied onset and must not be conflated with those in-span cancellations.",
        "",
        "Original-frame review shows excluded close-ups at GT6 frame2560, GT9 frame3753, GT13 frame5958, GT14 frame6382, GT16 frame6976 and GT31 frame14405. Those strong rejected model peaks do not justify earlier rally inference. GT8 frame3451 shows a shuttle held in preparation; preparation visibility does not establish a rally onset. These are assistant-reviewed examples, not independently adjudicated first-visible-frame labels. For other rows, the exact first physically observable sporting onset remains unknown unless explicitly described above.",
        "",
        "GT28 frame13054 differs: a wide view and visible upper streak support the accepted provider point while projection is REACQUIRING. Geometry rejects two useful image-plane observations, but the following frame moves only 0.708 pixels before the long admission/visibility gap to13112. Separating image validity from floor calibration repairs evidence semantics; it alone does not prove an earlier start.",
        "",
        "GT4 begins at weak accepted contact1803; pixels show a held shuttle near1803, launch around1828 and overhead preparation at1874. A serve-versus-first-return annotation convention remains unresolved. GT7's comparable preparation/launch is a negative regression control, not a pretext to fit one rally. Do not offset or edit either boundary.",
        "",
        "GT23's later loss has a competing singleton10936 retained in raw observations; coherent top-flight brackets10906–10910 and10947–10951 support qualified continuity. This is separate from the physical content edit10769→10770. Historical GT31 continuity instead uses ordinary observed top-exit/return brackets14646–14650 and14683–14687 after upstream mask repair; no curve or invented point is needed.",
        "",
        "GT27's historical result conceals an unreliable causal dependency: stationary evidence proposes12748, closes12763, and suspect T contact12766 reopens it. Removing only that contact fragments the rally while every processed shuttle step and the other35matched rows remain unchanged. The new association/contact consumer experiments must be evaluated jointly and must retain actual-floor, low-speed serve, fast flight and separate-rally controls. Historical perfect detection is not proof that this dependency is sound.",
        "",
        "## Cached scene effects awaiting fresh validation",
        "",
        "The separately executed cached association counterfactual retains all36historical intervals exactly and changes live contacts457→453. Association plus 13causal scene hypotheses retains36TP/0FP/0FN and changes only four rows. Start MAE29.1389→28.25 and mean IoU0.867622→0.871347 improve; end MAE10.3333→10.4167 worsens. Changed neural context windows and detector resets are not represented as fresh perception by this experiment.",
        "",
        "| GT | Historical interval | Cached scene interval | Measured effect |",
        "|---|---|---|---|",
    ]
    effects = {
        16: "End +41→+44: worsens3frames",
        22: "Start −29→−2: improves27frames",
        23: "Start +36→+44: worsens8frames",
        34: "Start −15→+2: improves13absolute frames",
    }
    for number, row in changed.items():
        lines.append(f"| {number} | {row['old_interval']} | {row['new_interval']} | {effects[number]} |")
    lines += [
        "",
        "All other32rows remain endpoint-identical. GT22 and GT23 remain distinct. The 13automatically proposed edits have assistant original-frame review, not an independently labelled cut-recall denominator. The explicit experimental barrier does not recalibrate a valid same-camera court.",
        "",
        "## New full-pipeline pair",
        "",
        "Pending completion and own-cache trace validation. No new inference score, runtime, causal effect or promotion claim is made in this baseline review. The orchestrator's two fresh runs must be compared against both immutable references, with every unmatched prediction and changed boundary retained. This section will be extended only after the completed artifacts are independently checked.",
        "",
        f"Machine-readable rows, input hashes and the exact executed script are in `{args.output.relative_to(ROOT)}/`.",
        "",
    ]
    args.report.write_text("\n".join(lines))
    print(
        json.dumps({"report": str(args.report), "rows": len(compact), "validated_cache_files": len(hashes)}, indent=2)
    )


if __name__ == "__main__":
    main()
