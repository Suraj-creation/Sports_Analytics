"""Publish review of preserved Test1/2 evidence into this task's owned paths."""
from __future__ import annotations

import json
from pathlib import Path

import build_failure_database as db

OUT, WORK, ROOT = db.OUT, db.WORK, db.ROOT
REPORT = WORK / "reports/test_01_02_annotation_and_failure_review.md"


def link(path, label=None):
    path = Path(path).resolve()
    return f"[{label or path.name}]({path})"


def run():
    evidence = {
        "test1_fixes": WORK / "reports/test_01_fixes_and_regression.md",
        "test1_matrix": WORK / "reports/test_01_evaluation_matrix.md",
        "test1_annotation_visual": WORK / "test_01/diagnostics/annotation_visual_review/annotation_visual_review.md",
        "test2_annotations": WORK / "test_02/annotations/annotation_mapping.md",
        "test2_annotation_visual": WORK / "test_02/diagnostics/annotation_visual_review/annotation_visual_review.md",
        "test2_identity": WORK / "test_02/diagnostics/identity_availability.md",
        "test2_player_outliers": WORK / "test_02/diagnostics/player_outlier_review/REPORT.md",
        "test2_semantic_effects": WORK / "test_02/fixes/semantic_effect_review.md",
        "test2_full_consolidated": WORK / "reports/test_02_consolidated_v1.md",
        "test2_fix_receipt": WORK / "test_02/fixes/applied_fix_receipt.json",
        "test1_semantic_receipt": WORK / "test_02/regression/test1_semantic_regression_v1/completion.json",
        "test2_fresh_receipt": WORK / "test_02/improved_v1/improved_completion.json",
        "test2_temporal": WORK / "test_02/diagnostics/temporal_root_cause/REPORT.md",
        "test2_scene_ocr": WORK / "test_02/diagnostics/current_scene_and_ocr_review/REVIEW.md",
        "test2_ocr_acquisition": WORK / "test_02/diagnostics/current_scene_and_ocr_review/ROI_ACQUISITION_REVIEW.md",
        "test2_gap": WORK / "test_02/diagnostics/current_scene_and_ocr_review/g69_gap_extended/REVIEW.md",
        "tracking_birth_probe": WORK / "component_evaluations/pre_test03_perception_v1/tracking_prefix_probe_v1/summary.json",
    }
    for path in evidence.values():
        db.bind(path)
    modules = ["engine.py", "events/rally_fsm.py", "racket_admission.py", "score_ocr.py",
               "perception/players.py", "perception/pipeline.py", "perception/racket.py",
               "perception/player_association.py", "perception/association.py"]
    code_evidence = {name: db.bind(ROOT / "sports/badminton/src/bai_badminton" / name) for name in modules}
    snapshot_dir = OUT / "source_snapshots"
    snapshot_dir.mkdir(exist_ok=True)
    for name, item in code_evidence.items():
        snapshot = snapshot_dir / (name.replace("/", "__") + ".source")
        original_bytes = Path(item["path"]).read_bytes()
        if snapshot.exists():
            assert snapshot.read_bytes() == original_bytes, "Existing inspection source changed; create new review version"
        else:
            snapshot.write_bytes(original_bytes)
        item["preserved_snapshot"] = db.bind(snapshot)
    # Current inspection hashes locate code under investigation; executed run hashes remain in original receipts.
    db.save("current_code_inspection.json", {"scope": "current main source inspection only; not a new inference receipt", "files": code_evidence})
    findings = [
        {"id": "PERCEPTION-01", "priority": "P0", "component": "target-player admission", "test": 2,
         "frames": [6492, 6493, 6494], "status": "confirmed agent visual failure; precise first causal stage unresolved",
         "observed": "Current fresh track0 at frame6492 encloses a seated background official; near red athlete is absent. Far athlete agrees within0.215px. Same wrong population carries through6493/6494.",
         "root_cause": "Wrong target-person population, not a global coordinate scale/time shift. Original cache alone lacks exhaustive proposals. New source-bound chronological birth-only probes separate the mechanism: both athletes are detected, but backend birth suppression omits the near athlete. Candidate restores near+far while official remains. Independently traced court-anchor self-renewal is separate: uniquely overlapping out-of-court fresh detections can reuse continuity, then refresh the same anchor without strict court membership. Isolated combined correction and full-fresh validation are pending; no fully solved pipeline claim.",
         "modules": ["perception/players.py", "perception/pipeline.py", "perception/isolation.py"],
         "source": evidence["test2_player_outliers"], "secondary_source": evidence["tracking_birth_probe"], "image": WORK / "test_02/diagnostics/player_outlier_review/frame_06492/proxy_overlay.png",
         "court_admission_source_snapshot": code_evidence["perception/players.py"]["preserved_snapshot"],
         "validation": "Trace all proposals, crop/ROI and admission before/after; independently review target boxes/negatives; require ordinary/singles/doubles/occlusion/adjacent-court controls and fresh Test1/2 perception."},
        {"id": "PERCEPTION-02", "priority": "P0", "component": "propagated player boxes", "test": 2,
         "frames": [354, 355, 25520, 25521], "status": "confirmed post-edit misalignment; chronological diagnosis supersedes generic drift hypothesis",
         "observed": "Both frames use propagated boxes. At355 near pair disagreement403.540px; at25521 current boxes occupy empty left background while visible athletes are elsewhere (364.874/308.521px).",
         "root_cause": "Initial selected-frame review only established bad alignment. Exact source transitions354→355 and25520→25521 show same-camera edited jumps/score changes; boxes were correct before each jump. This supersedes generic within-shot propagation drift. Original-backend prefix reproduces saved boxes. Birth-only candidate recovers new athletes earlier but emits no content barrier; edit acquisition remains separate and unresolved. Final combined/fresh validation belongs in a later receipt.",
         "modules": ["perception/players.py", "perception/pipeline.py"], "source": evidence["test2_player_outliers"],
         "image": WORK / "test_02/diagnostics/player_outlier_review/frame_00355/proxy_overlay.png",
         "secondary_source": evidence["tracking_birth_probe"],
         "chronological_evidence": [WORK / "component_evaluations/pre_test03_perception_v1/prefix_baseline_alignment.json",
                                    WORK / "component_evaluations/pre_test03_perception_v1/tracking_prefix_probe_v1/test2_00300_00365.json",
                                    WORK / "component_evaluations/pre_test03_perception_v1/tracking_prefix_probe_v1/test2_25206_25540.json",
                                    WORK / "component_evaluations/pre_test03_perception_v1/tracking_prefix_probe_v1/test2_00300_00365_frame_00354.png",
                                    WORK / "component_evaluations/pre_test03_perception_v1/tracking_prefix_probe_v1/test2_00300_00365_frame_00355.png",
                                    WORK / "component_evaluations/pre_test03_perception_v1/tracking_prefix_probe_v1/test2_25206_25540_frame_25520.png",
                                    WORK / "component_evaluations/pre_test03_perception_v1/tracking_prefix_probe_v1/test2_25206_25540_frame_25521.png"],
         "validation": "Inspect preceding fresh and carried observations, cuts and recovery. Fix the earliest verified state/admission error, preserve freshness provenance, then fresh inference; no distance cutoff fitted to legacy points."},
        {"id": "EQUIPMENT-01", "priority": "P1", "component": "racket evidence and contact cascade", "test": [1, 2],
         "frames": [300, 1594, 3754, 5446, 14066, 14078, 19494, 28828],
         "status": "narrow correctness safeguard implemented; remaining raw geometry limitation",
         "observed": "Classical ellipse candidates coincide with heads, torso or background. Existing anatomical-alias policy withholds selected fresh candidates supported by reliable facial overlap, preserving raw output; it does not find the real racket.",
         "root_cause": "Geometric shape/wrist evidence is not equipment semantics. Removing one cue changes contact scores and NMS competitors, classes and some rally boundaries. Genuine overhead equipment may overlap anatomy, so withholding is ambiguity rather than a negative label.",
         "modules": ["perception/racket.py", "racket_admission.py", "engine.py", "events/contact.py"],
         "source": evidence["test2_semantic_effects"],
         "image": WORK / "test_02/fixes/semantic_effect_evidence/test_02_v2/frame_19494_raw_vs_semantic.png",
         "validation": "Review impacts and negative racket windows independently; preserve before/after source caches and one-variable regressions; evaluate replacement models with code/weight/data licences and singles/doubles limits, not arbitrary model upgrades."},
        {"id": "ANNOTATION-01", "priority": "P0_evaluation", "component": "reference semantics", "test": 1,
         "frames": [3451, 3751, 6382, 6976, 8683], "status": "confirmed source thumbnails contradict assumption that every generated start is a visible serve",
         "observed": "gt_008/009/014/016/020 generated start frames show closeups; their later predicted start frames show full-court action. All retain matched status despite timing deltas.",
         "root_cause": "Legacy generated interval starts can include edit/closeup lead-in. Boundary disagreement is not sufficient evidence of a serve detection bug.",
         "modules": ["reference adapter/evaluation policy", "events/rally_fsm.py"],
         "source": OUT / "visual_review/contact_sheet_manifest.json",
         "validation": "Create separate source-bound reviewed physical start/end labels with explicit serve/action/edit conventions; preserve original timing families and do not shift predictions to fit them."},
        {"id": "SEGMENTATION-01", "priority": "P1_review", "component": "temporal segmentation", "test": 2,
         "frames": [11714, 11715, 11751, 11830, 13427, 13462, 13533, 13579, 13707, 13718, 26616, 27325, 27349, 27668],
         "status": "confirmed interval splitting/disagreement; physical correctness not independently adjudicated",
         "observed": "Reference31 overlaps prediction32 atIoU36/116=.310345. Reference39 overlaps predictions40/41 at71/280=.253571 and128/291=.439863. Reference69 matches prediction70 but also overlaps unmatched prediction71, with matched end343frames early.",
         "root_cause": "Under IoU0.5 one-to-one policy short fragments generate both FN and FP; those counts do not mean the component never ran or the extra is physically false. Trace missing/slow shuttle, contact and finalize/reopen gates across each full window.",
         "modules": ["events/rally_fsm.py", "engine.py", "perception/association.py"],
         "source": OUT / "failure_database.jsonl",
         "validation": "Independently determine whether each source interval is one physical exchange or edited activity; replay exact state transitions and both initial/recovery gates; only then change a verified contract and rerun both tests."},
        {"id": "SEGMENTATION-02", "priority": "P1_review", "component": "short exchange coverage", "test": 2,
         "frames": [20947, 21045, 21736, 21809, 23879, 24012], "status": "no positive-overlap predicted intervals in generated reference spans",
         "observed": "Missed references56/58/63 last98/73/133frames. Source boundary thumbnails show athletes/court, but do not certify serve/contact/end times. Full trace/perception coverage exists for all windows.",
         "root_cause": "Baseline original-contact audit establishes canceled candidates: G56 lacks the required probable trajectory/impact cue; G58 contacts target the same episode and source shows walking/handling; G63 opposite episode pair changes1/2→1/3, so stable typed proof fails. These are distinct gates, not an execution failure or a justified universal duration reduction. Improved-arm raw/state counts and original baseline gate evidence remain separately attributed.",
         "modules": ["events/rally_fsm.py", "engine.py", "perception/tracknet.py", "perception/association.py"],
         "source": OUT / "failure_database.jsonl",
         "validation": "Inspect every observed/missing/estimated step and contact gate, preserve raw proposals; review short serves, faults and idle controls. Do not simply lower a minimum duration or confidence threshold."},
        {"id": "ANNOTATION-02", "priority": "P0_evaluation", "component": "outcome, identity and scores", "test": [1, 2],
         "frames": [8634, 3863, 4030], "status": "unresolved source/annotation conventions; not all annotation rows erroneous",
         "observed": "Test1 Full2 row19 disagrees with coarse winner/reason/class/score, row21 is literal ellipsis; source8634 displays20:20 rather than supplied10:9/9:10. Test2 has26 nonunit adjacent coarse score transitions (including resets); source3863 and4030 visibly show7:7 and9:8 within one generated span.",
         "root_cause": "Partial/conflicting annotations, edited-video omissions, resets and unbound A/B semantics. Legacy far/near convention does not imply persistent athletes through side changes.",
         "modules": ["score_ocr.py", "identity/roster review", "reference alignment"],
         "source": evidence["test2_annotations"], "secondary_source": evidence["test1_annotation_visual"],
         "validation": "Review exact source scoreboard transitions and athlete/team/row mappings per game; store adjudications separately, keep score observations distinct from accepted points. No invented missing points or automatic corruption repair."},
        {"id": "ANNOTATION-03", "priority": "P0_evaluation", "component": "generated player/shuttle reference validity", "test": 2,
         "frames": [4, 6, 1594, 1614, 16246], "status": "confirmed generated-data limitations",
         "observed": "Player slots exchange order; no boxes/IDs. Two filled shuttle files are byte-identical;50 visible filled points lie outside1280x720, including1614=(551,929). No interpolation flag distinguishes actual observations from filled points.",
         "root_cause": "Model output schema lacks required physical GT provenance. Repeated files and slot flips cannot supply independent detection or identity labels.",
         "modules": ["evaluation reference schema", "legacy generated datasets"],
         "source": evidence["test2_annotations"], "secondary_source": evidence["test2_annotation_visual"],
         "validation": "Retain invalid/outside-canvas rows and duplicates with categories, use anonymous point disagreement only, independently label boxes/identities/shuttle visibility/coordinates before AP/HOTA/localization accuracy."},
        {"id": "IDENTITY-01", "priority": "P1", "component": "optional appearance identity and named attribution", "test": [1, 2],
         "frames": [], "status": "known missing optional model and unresolved independent identity prerequisites",
         "observed": "Configured OSNet artifact is absent; factory degrades to unavailable provider. ByteTrack still runs. Baseline public format explanation is narrower than the actual adapter contract. Test2 has75 unknown winners; unknown is not0% measured accuracy.",
         "root_cause": "Missing checkpoint explains unloaded neural appearance stage, not all unknown roster/score/contact identities. Model installation cannot establish A/B, persistent names or team score rows.",
         "modules": ["perception/pipeline.py", "perception/offline_reid.py", "plugin.py", "identity review"],
         "source": evidence["test2_identity"],
         "validation": "Separate model acquisition/real crop-runtime test with pinned licence/hash and fresh cache; review persistent identities/roster/team/score rows independently; singles and four-person doubles controls."},
        {"id": "METRICS-01", "priority": "P0_reporting", "component": "multi-reference comparison", "test": 2,
         "frames": [5224, 5432, 5446, 8626, 8627, 8734, 8751, 13856, 14045, 14079, 18594, 18595, 24711, 25155, 25156, 25629, 25650, 26018],
         "status": "exact mathematical explanation verified",
         "observed": "Same matching assignment and TP/FP/FN after six interval movements; coarse meanIoU decreases while generated meanIoU increases because reference spans differ.",
         "root_cause": "Detection membership atIoU>=.5 and matched overlap quality are different statistics. Distinct references reward different boundary placement; win_predictions timing duplicates rally reference.",
         "modules": ["reference_comparison evaluator", "reporting"], "source": OUT / "mixed_iou_exact.json",
         "validation": "Report every family, per-row rational deltas, matched denominators, misses/extras and start/end/duration metrics. No single aggregate across duplicate/partial annotation versions."},
        {"id": "FIXED-CONTRACTS-01", "priority": "preserve", "component": "recovery, score-vote independence and camera projection", "test": 1,
         "frames": [], "status": "three implemented Test1 code correctness fixes with focused regressions and preserved fresh-video metrics",
         "observed": "Reopened-rally cut frontier, repeated score-transition vote inflation, and detector-foot coordinate transform were reproduced/fixed. Test1 prediction CSV and all6 reference metrics remain unchanged after its fresh run.",
         "root_cause": "Verified state/provenance/coordinate edge contracts; these source examples did not trigger metric changes.",
         "modules": ["events/rally_fsm.py", "score_ocr.py", "engine.py"], "source": evidence["test1_fixes"],
         "validation": "Keep original regressions and fresh baselines. Subsequent racket policy has full Test1 fixed-perception semantic regression with287/287 matching cadence drivers, not a new full Test1 neural run."},
        {"id": "COVERAGE-01", "priority": "P0_evaluation", "component": "pose, contact, stroke, scoring, analytics, highlights", "test": [1, 2],
         "frames": [], "status": "insufficient independent GT; execution and coverage are measurable",
         "observed": "No reviewed per-impact/negative racket/contact set, exhaustive stroke sequence, keypoints, persistent identity or highlight relevance labels. Test2 unknown stroke rate587/819→586/816 (71.67%→71.81%); lower unknown count does not mean better classification.",
         "root_cause": "Rally-level ball_types cannot label every contact; generated predictions cannot validate themselves. No accepted scoring output is a coverage limitation with dependencies, not independently measured accuracy0.",
         "modules": ["component evaluation contracts", "events", "analytics", "highlights"],
         "source": evidence["test2_full_consolidated"],
         "validation": "Create a distinct source-bound reviewed event/identity/keypoint/relevance set with explicit class/tolerance/exhaustiveness conventions, ordinary negatives and held-out videos; retain unavailable metrics as null."},
        {"id": "SCENE-01", "priority": "P1", "component": "same-camera edit acquisition", "test": 2,
         "frames": [11345, 11346, 11347, 11348, 11353], "status": "source-supported missed edit; tracked output and observer dependencies separated",
         "observed": "At11345→11346 athletes relocate abruptly and displayed current score changes4:0→5:1. Only one prior player region exists; no raw hypothesis/layout decision is published; epoch13 is unchanged. Detector runs11346 but returns no final tracks until11348.",
         "root_cause": "Selected raw observer requires two-to-four prior regions, so detector corroboration is not acquired. New birth-only chronological probe returns both fresh athletes at11346 but still emits no scene barrier, proving birth repair alone does not solve acquisition. Engine is IDLE at the cut; later11353 legacy contact opens a candidate, so fixing the edit does not automatically repair41early boundary frames.",
         "modules": ["perception/content.py", "perception/scene_change.py", "perception/players.py", "engine.py"],
         "source": evidence["test2_scene_ocr"], "secondary_source": evidence["test2_temporal"],
         "validation": "Preserve exact proposal/track lifecycle and prior-region evidence; require continuous lunge7703/walking23639, real edit22946, occlusion and doubles controls. No lower-region-count/frame-ID exception; test early contact admission separately."},
        {"id": "SHUTTLE-01", "priority": "P1", "component": "raw shuttle dropout and temporal continuity", "test": 2,
         "frames": [27325, 27326, 27335, 27340, 27347, 27348, 27349, 27351, 27354],
         "status": "exact raw-to-FSM sequence established; physical shuttle trajectory remains unreviewed",
         "observed": "No accepted raw coordinate27326–27347 (22frames);15 retained candidate peaks are mask-allowed but below0.5,10gap frames have no candidate. First observed reacquisition27348 has no adjacent speed. Lower branch then competes with upper/lower selection27354.",
         "root_cause": "Association lacks accepted input rather than vetoing a strong raw coordinate. FSM proposes end27325 at27335, closes27340; separation27325→27348 is23frames beyond round(.75*30)=22, so old interval publishes27348 and new starts27349. No proven ordering bug or justification for invented flight/forced upper candidate/global timeout expansion.",
         "modules": ["perception/tracknet.py", "perception/association.py", "engine.py", "events/rally_fsm.py"],
         "source": evidence["test2_gap"], "secondary_source": evidence["test2_temporal"],
         "validation": "Review shuttle visibility/coordinates and equipment negatives across continuous gap; retain G39/G55/post-point controls. Ordinary missing-composition candidate is distinct because benchmark disables reconstruction; do not claim it solvesG69."},
        {"id": "OCR-01", "priority": "preserve_positive_control", "component": "score crop/branding ownership", "test": 2,
         "frames": [22924, 22945, 22946, 22954], "status": "previous branding error already resolved in actual fresh baseline",
         "observed": "Actual reader22924 returns AXELSEN9/ANTONSEN12, confidence.96547, matching visible text. Source22946 visibly edits9:12→9:14 with epoch26→27; later9:14 is source-supported rather than an OCR error.",
         "root_cause": "Historical branding21:12 failure is not current. Standalone full-corner reader misses upper current digit and abstains, so replacing actual crop would lose a sampled positive. Score jump across edited footage supplies no invented winners.",
         "modules": ["perception/scoreboard.py", "score_ocr.py", "perception/content.py"],
         "source": evidence["test2_scene_ocr"], "secondary_source": evidence["test2_ocr_acquisition"],
         "validation": "Keep branding and known9:12 positive controls, visible edit and legal unknown handling; do not re-fix solved parser behavior or convert+2edit into observed accepted points."},
        {"id": "OCR-02", "priority": "P2_research", "component": "score acquisition and fused numeric tokens", "test": 2,
         "frames": [9484, 9604, 11346, 12604, 12634], "status": "bounded gap cause rejected; separate generic ROI growth defect and token-fusion limitation retained",
         "observed": "Scheduled105-call actual-pixel replay reproduces only12604/12634readings in both current/full-corner arms; current unlocks9604. Complete11346pixels still yield fused165/211tokens, so parser abstains. Generic ROI-expansion contract has1RED/2controls; candidate3controls pass but no gap coverage gain.",
         "root_cause": "Persistent narrow ROI does not explain actual missing readings after9484through12604. A synthetic stale-successful-crop hazard exists separately. One fused-token frame cannot explain entire gap or justify silently splitting numbers.",
         "modules": ["perception/scoreboard.py"], "source": evidence["test2_ocr_acquisition"],
         "validation": "Reject current full-corner-only promotion; research source-bound column layout/acquisition with9:12positive and ambiguity controls, runtime/resource comparisons, no fabricated sporting scores."},
        {"id": "COMPOSITION-01", "priority": "P1", "component": "modern shuttle evidence versus reconstructed geometry", "test": [1, 2],
         "frames": [], "status": "source contract identified by parent; isolated semantic fix requires full regressions",
         "observed": "Current engine._window runs postprocessing, then evidence.status!=observed clears both track.vis and track.interp. This treats ordinary modern missing input like competing/ambiguous evidence; equivalent legacy absent evidence can retain explicitly reconstructed geometry.",
         "root_cause": "Observation-composition/provenance integration rather than proof of a neural detector error. Reconstruction eligibility must distinguish ordinary missing from ambiguity/rejection/invalid context. Benchmark profile disables reconstruction, so this contract is not automaticallyG69's cause.",
         "modules": ["engine.py", "perception/shuttle_post.py"],
         "source": snapshot_dir / "engine.py.source",
         "validation": "Parent candidate must preserve interpolation provenance, hard barriers and observed-only contact use; verify singles/doubles, invalid/ambiguous/missing controls, full Test1/2 regressions. This review did not execute candidate tests or change source."},
    ]
    for finding in findings:
        if "chronological_evidence" in finding:
            finding["chronological_evidence"] = [db.bind(p) for p in finding["chronological_evidence"]]
        for key in ("source", "secondary_source", "image"):
            if key in finding:
                path = Path(finding[key])
                finding[key] = db.bind(path)
        finding["evidence_status"] = "agent diagnostic review, not independent human physical ground truth"
        finding["production_change_performed_by_this_review"] = False
    db.save("component_findings.json", findings)
    db.save("component_cases.json", {"schema": "test01-test02-nonrally-component-cases:v1",
                                    "packaged_rally_case_count_unchanged": 53,
                                    "case_count": len(findings), "cases": findings,
                                    "physical_gt_labels_created": False})
    sheets = json.loads((OUT / "visual_review/contact_sheet_manifest.json").read_text())
    review = {"schema": "test01-test02-source-thumbnail-review:v1", "reviewer_kind": "agent",
              "physical_gt_certification": False, "all_53_case_thumbnail_pairs_reviewed": True,
              "full_video_frame_by_frame_review": False,
              "scope": "Exact preserved source frame thumbnails at reference/predicted starts; missed and extra cases use interval endpoints. Full raw overlay/trace files retained; this task does not newly view every frame in those windows.",
              "test1_closeup_reference_start_cases": ["gt_008", "gt_009", "gt_014", "gt_016", "gt_020"],
              "test2_source_review": "All selected thumbnails show court/player context. Several generated intervals cross visible score changes/edited context (gt_011,gt_044,gt_067,gt_071,gt_072). Static endpoints cannot establish exact physical impact or cut timing.",
              "do_not_infer": ["all timing disagreement is a code defect", "unmatched prediction is a physical false rally", "racket abstention means no real contact", "model slots are named athlete GT"],
              "sheets": [{"path": x["path"], "sha256": x["sha256"], "cases": x["cases"]} for x in sheets]}
    db.save("visual_review/review_notes.json", review)
    refs = json.loads((OUT / "reference_metrics.json").read_text())
    anns = json.loads((OUT / "annotation_inventory.json").read_text())
    mixed = json.loads((OUT / "mixed_iou_exact.json").read_text())
    cases = [json.loads(x) for x in (OUT / "failure_database.jsonl").read_text().splitlines()]
    lines = ["# Test1–2 annotation and failure review before Test3", "",
             "This is a new, read-only diagnostic consolidation of preserved completed Test1/2 runs. It covers **16 original annotation files, all six Test1 interval-reference families, all seven Test2 annotations, 422 valid reference rows and 53 unique packaged cases** (14 Test1 +39 Test2). Each case retains both baseline and improved observations:106 observations are not106 independent failures. No production code, original annotation, baseline, model or configuration was changed; no inference or Test3 data access was performed.", "",
             "Agent source checks remain diagnostic. The original legacy human-origin coarse tables have documented provenance but no per-row adjudication ledger; generated rally/player/shuttle/outcome files are not independent physical truth. The new database preserves these distinctions and does not invent AP, HOTA, PCK, contact F1, class confusion, winner accuracy or accepted points.", "",
             "## Reproducible evidence", "",
             f"{link(OUT/'failure_database.jsonl', '53-case structured database')} · {link(OUT/'failure_index.csv', 'flat failure index')} · {link(OUT/'reference_rows.jsonl', 'all422 raw/reference comparison rows')} · {link(OUT/'reference_metrics.json', 'complete per-reference metrics')} · {link(OUT/'mixed_iou_exact.json', 'exact rational IoU changes')} · {link(OUT/'component_cases.json', 'separate component case database')} · {link(OUT/'component_findings.json', 'ranked component findings')} · {link(OUT/'annotation_inventory.json', 'original-file hashes and schemas')} · {link(OUT/'input_provenance.json', 'input SHA256 manifest')}.", "",
             "The builder asserts stable source hashes, row assignments/statuses, exact original annotation checksums,14/39 case counts,53 unique cases,422 valid rows, and exact IoU delta reconstruction. Every consumed immutable input is rehashed after construction. Selected source JPEGs match the original source/PTS-bound failure manifests. Original cache/proxy/source bindings remain in those manifests; large raw arrays are linked and hashed rather than copied into a misleading summary.", "",
             "Historical runs are pinned by their original receipts, source/model/configuration snapshots and logs. Current module inspection hashes only locate the present implementation; they are explicitly not a new execution receipt. Test1’s three fixes have a fresh17,268-frame before/after baseline. The later racket policy has a complete Test1 cached-semantic regression with287/287 matching scheduling drivers; it is **not a fresh Test1 neural run**. Test2 baseline/post-fix are separate genuine29,296-frame fresh inference runs with unchanged models/profile/original annotations.", "",
             f"Receipts: {link(evidence['test1_fixes'])}, {link(evidence['test1_semantic_receipt'])}, {link(evidence['test2_fresh_receipt'])}, {link(evidence['test2_fix_receipt'])}. Full existing detailed metrics/runtime/resources: {link(evidence['test1_matrix'])}, {link(evidence['test2_full_consolidated'])}.", "",
             "## Annotation inventory and limits", "",
             "| Test | File | Data rows | Role |", "|---|---|---:|---|"]
    for a in anns:
        lines.append(f"| {a['test']} | {link(a['original']['path'],a['file'])} | {a.get('raw_data_row_count','single JSON frame')} | {a['role']} |")
    lines += ["", "Test1 Full2 contributes20 valid positives and a retained malformed ellipsis row21; false positives, precision and F1 are unavailable for its partial population. Full2 row19 differs from the coarse table in winner/reason/stroke/score; row20 score also differs. Source scoreboard8634 shows20:20, so copying either supplied10:9 or9:10 into the OCR result would falsify source evidence. Match by interval rather than row ordinal.", "",
              "Test2 has no Full2 original. Its two shuttle files are byte-identical29,296-row aliases, not two independent references. Filled visibility has no observed/interpolated marker;50 visible rows lie outside1280×720. Player points are bbox bottom-centers in detector order, with2,407 adjacent relative-Y flips; they provide no box extents or persistent IDs. Court frame300 visually follows inner singles sidelines; one manual candidate is not whole-video calibration GT or a doubles boundary definition.", "",
              "Test2 coarse labels contain75 spans versus73 generated rally spans. All73 win_predictions spans exactly duplicate rally timing. Symbolic A/B may reflect legacy far/near slots, not persistent athletes across end changes; scores have26 nonunit adjacent changes including reset candidates. These are unresolved edit/game/convention issues, not26 proved annotation errors. Preserve original files, visible scoreboard observations, identity hypotheses and accepted scoring decisions separately.", "",
              f"Full schema/source interpretations and exact issue rows: {link(evidence['test2_annotations'])}; source-frame review: {link(evidence['test1_annotation_visual'])}, {link(evidence['test2_annotation_visual'])}.", "",
              "## Complete interval-reference summary", "",
              "All rows use half-open intervals and maximum-cardinality one-to-one matching atIoU≥0.5, then total IoU/boundary tie-break. Boundary/duration/IoU summaries condition on matched pairs; misses and extras remain in detection counts. Do not average the six/three overlapping reference versions as independent tests.", "",
              "| Test / reference | TP/FP/FN before→after | P / R / F1 after | Mean IoU before→after | Start / end / duration MAE seconds after |", "|---|---|---|---|---|"]
    def fmt(x):
        return "unavailable" if x is None else f"{x:.6f}"
    for ref in refs:
        b, a = ref["before"], ref["after"]
        bd, ad = b["detection"], a["detection"]
        counts = lambda d: "/".join("null" if d[k] is None else str(d[k]) for k in ("true_positives", "false_positives", "false_negatives"))
        errors = a["boundary_and_duration_errors"]
        maes = " / ".join(fmt(errors[k]["mae"]) for k in ("start_time_sec", "end_time_sec", "duration_sec"))
        lines.append(f"| {ref['test']} / {ref['reference']} | {counts(bd)}→{counts(ad)} | {' / '.join(fmt(ad[k]) for k in ('precision','recall','f1'))} | {fmt(b['overlap']['mean_iou'])}→{fmt(a['overlap']['mean_iou'])} | {maes} |")
    lines += ["", "The JSON matrices retain every original precision/recall/F1 count, error median/RMSE/max/p90/signed distribution, tolerance denominator, overlap summary, missed row and extra prediction. The422-row JSONL retains original CSV values, data-row and physical CSV-line indices, hashes and before/after start/end/duration errors for every valid reference row; malformed Full2 row21 remains explicit in the inventory/matrix.", "",
              "## Why unchanged TP/FP/FN accompanies mixed IoU", "",
              "Exactly six Test2 predicted intervals move; the other69 do not. Each moved interval remains matched to the same reference row above0.5 in all three families. Consequently TP/FP/FN and precision/recall/F1 remain identical. IoU measures the overlap geometry inside that unchanged membership and can still improve or worsen. Coarse and generated reference spans have different endpoints, so the same movement has different rewards.", "",
              "| Prediction ordinal | Baseline→improved frames | Coarse reference row and span | Coarse IoU before→after | Generated row and span | Generated IoU before→after |", "|---:|---|---|---|---|---|"]
    coarse, generated = mixed[:2]
    generated_by_pred = {r['after']['pred_rally']:r for r in generated['changed_matched_rows']}
    for r in coarse['changed_matched_rows']:
        b,a=r['before'],r['after']; g=generated_by_pred[a['pred_rally']];ga=g['after']
        lines.append(f"| {a['pred_rally']} | [{b['pred_start_frame']},{b['pred_end_frame']})→[{a['pred_start_frame']},{a['pred_end_frame']}) | {r['source_data_row']}: [{a['gt_start_frame']},{a['gt_end_frame']}) | {r['exact_iou_before']['value']:.9f}→{r['exact_iou_after']['value']:.9f} | {g['source_data_row']}: [{ga['gt_start_frame']},{ga['gt_end_frame']}) | {g['exact_iou_before']['value']:.9f}→{g['exact_iou_after']['value']:.9f} |")
    lines += ["", "For prediction25, moving8627–8734→8626–8751 extends the predicted end17frames. Generated row24 ends8748: overlap grows107/155→122/158 (.690323→.772152). Coarse row25 ends8730: overshoot increases and IoU falls103/124→104/141 (.830645→.737589). Neither reference is silently selected as the physical truth.", ""]
    for m in mixed:
        lines.append(f"- `{m['reference']}`: sum of its six exact matched-IoU deltas ÷{m['matched_denominator']} = **{m['exact_mean_delta']['value']:+.12f}**, exactly reconstructing {m['mean_iou_before']:.12f}→{m['mean_iou_after']:.12f} within1e-12.")
    lines += ["", "Generated-reference start MAE worsens even while mean IoU improves; coarse start/end/duration MAE all worsen. Winner-file timing duplicates generated rally timing and supplies no second independent improvement. This evidence supports a narrow evidence-contract correction with preserved detection F1, not uniform rally accuracy gain.", "",
              "## Source review and ranked findings", "",
              f"All14 newly generated contact sheets were inspected, covering boundary thumbnail pairs for all53 unique cases. {link(OUT/'visual_review/review_notes.json','review scope and limits')} and {link(OUT/'visual_review/contact_sheet_manifest.json','exact image hashes/case membership')} preserve that review. This was not continuous manual adjudication of every frame in all53 windows.", "",
              "Five Test1 generated starts are visibly closeups:3451,3751,6382,6976,8683. Later predicted starts show wide-court action. Treating these deltas as missed serve time would confuse reference lead-in with physical action. Test2 case11’s reference/prediction start thumbnails visibly read7:7/9:8, illustrating edited or merged temporal context; static samples cannot determine all hidden boundaries.", "",
              "| Priority / ID | Finding and present status | Required validation |", "|---|---|---|"]
    for f in findings:
        lines.append(f"| {f['priority']} / {f['id']} | {f['observed']} **{f['status']}**. {link(f['source']['path'],'evidence')} | {f['validation']} |")
    lines += ["", "The429.411529px player-point maximum is a population error: an official paired against the omitted near athlete after the far athlete matched correctly. It does not mean one known athlete’s foot is429px off. Frames6492–6494 are one contiguous incident. Original cache alone lacked exhaustive proposals; subsequent source-bound chronological probes establish backend birth suppression despite both athletes being raw-detected. Birth-only repair restores both athletes but retains the official; court-anchor continuity admission is independently under repair. Exact source transitions354→355 and25520→25521 show same-camera edited jumps/score changes: preceding boxes were correct. This supersedes a generic within-shot drift explanation. Original-backend prefix reproduces saved boxes; birth-only prefix emits no scene barrier, so edit acquisition remains unresolved. These bounded candidate probes are not completed full-pipeline accuracy claims; later combined/fresh results require separate receipts.", "",
              "For generated reference31, short prediction32 gives36/116 IoU; reference39 splits across predictions40/41 (71/280 and128/291), all below0.5. These produce misses and extras despite actual output. References56/58/63 have no positively overlapping prediction. Reference69 matches prediction70 ending343frames early and also overlaps prediction71. Root causes remain conditional until full source/trace review confirms the physical exchange conventions.", "",
              "The racket safeguard changes contact competition, provisional hitter/class context and highlights. It does not replace the classical racket detector or certify rejected contacts as false. Test1’s known NMS cascade is demonstrated in preserved probes; other events cannot inherit that exact cause without their own probe. OSNet missing weights explain unavailable appearance embeddings, but installing it would not bind roster names, annotation A/B, teams or scoreboard rows.", "",
              "## Every packaged case", "",
              "The following table is the exact improved-arm disagreement against each generated rally reference. Signed errors are prediction minus reference. `missed`/`unmatched_prediction` are evaluator statuses, not adjudicated physical labels. Each linked JSON contains original raw predictions and complete trace; database records also retain baseline-arm case/file hashes, source/proxy/cache bindings, replay windows, within-reference signal/state counts and all positively overlapping predicted intervals. The prior baseline gate audit is independently linked/hashed for every case; all39 Test2 source narratives, cancellation/finalization and terminal reasons are preserved as prior baseline diagnostics rather than silently attributed to the changed arm.", "",
              "| Case | Status | Reference frames | Predicted frames | Start / end error frames | IoU |", "|---|---|---|---|---|---|"]
    for c in cases:
        o=c['observations']['improved_v1'];r=o['case_record']
        span=lambda s,e: "unavailable" if s is None else f"[{s},{e})"
        lines.append(f"| {link(o['raw_case_evidence']['path'],c['id'])} | {r['matching_status']} | {span(r.get('gt_start_frame'),r.get('gt_end_frame'))} | {span(r.get('pred_start_frame',r.get('start_frame')),r.get('pred_end_frame',r.get('end_frame')))} | {r.get('start_frame_error')} / {r.get('end_frame_error')} | {fmt(r.get('interval_iou'))} |")
    lines += ["", "## Validation order before accepting further changes", "",
              "1. Preserve the existing Test1/2 raw baselines, run receipts and all annotation families. Review new hypotheses in separate source-bound artifacts; never correct originals to fit predictions.",
              "2. Resolve the target-person and propagated-box failure mechanisms using original detector/crop/admission/tracker evidence and ordinary/doubles controls. A changed perception path requires new inference, cache identity and Test1/2 comparison.",
              "3. Diagnose each segmentation split/miss with exact signal/state/contact admission traces and reviewed physical conventions. Fix one verified contract, retain negatives and rerun both reference families; do not optimize a single generated IoU.",
              "4. Review identity, game resets, symbolic A/B and scoreboard rows separately from appearance-model availability. Preserve unknowns while measuring output coverage; record accepted points only when independently supported.",
              "5. Add reviewed per-impact/equipment/keypoint/identity/class/negative labels and held-out controls before claims of contact, classification, tracking or pose accuracy. Test1/2 are already examined development cases and cannot establish unseen-match generalisation.", "",
              "This review adds structured evidence and validation priorities only. It neither implements further pipeline fixes nor marks all issues resolved. Parent orchestration owns code experiments and decides when both-test regressions permit moving to Test3."]
    REPORT.write_text("\n".join(lines) + "\n")
    provenance = json.loads((OUT/'input_provenance.json').read_text())
    provenance['files'].update(db.INPUTS)
    provenance['review_writer_sha256'] = db.sha(__file__)
    for p, info in provenance['files'].items():
        assert db.sha(p) == info['sha256'], p
    db.save('input_provenance.json',provenance)
    db.save('review_completion.json', {'schema':'test01-test02-annotation-failure-review:v1',
                                      'annotation_files':16,'interval_reference_families':9,'valid_reference_rows':422,
                                      'unique_packaged_cases':53,'arm_observations':106,'component_findings':len(findings),
                                      'source_contact_sheets_agent_reviewed':14,'physical_gt_claim':False,
                                      'production_edits':False,'inference_performed':False,'test3_inputs_accessed':False,
                                      'all_consumed_input_hashes_reverified':True,'report':str(REPORT),'report_sha256':db.sha(REPORT)})
    print(REPORT)


if __name__ == '__main__':
    run()
