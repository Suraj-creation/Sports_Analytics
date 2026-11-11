# Test 2: prior findings, carried-forward fixes and diagnostic plan

Prepared 2026-11-11 from repository reports and source inspection. This document
is a planning review, not a new inference result or an independently adjudicated
ground-truth annotation. Existing Test 1 and historical Test 2 records remain
unchanged. Current fresh-run measurements belong in separate Test 2 run records.

## Test 1 readiness

The completed Test 1 reports establish three integrated correctness repairs:

| Repair | Production boundary | Regression evidence | Actual Test 1 result |
|---|---|---|---|
| Retain the last accepted recovery/resume frame before a cut | `sports/badminton/src/bai_badminton/events/rally_fsm.py` | 14 cases in `test_rally_recovery_cut_frontier.py`; six failures before repair | Edge condition did not occur; no measured rally gain |
| Count each independently corroborated source score transition once | `sports/badminton/src/bai_badminton/score_ocr.py` | Seven cases in `test_score_mapping_vote_provenance.py` | Anonymous identity correctly remains unknown; no winner-accuracy gain |
| Project the actual detector foot separately from the transformed bounding-box envelope | `sports/badminton/src/bai_badminton/engine.py` | Five cases in `test_stabilized_player_ground_point.py` | Camera transforms were identity; no measured position gain |

The fresh post-fix Test 1 run covered all 17,268 frames and retained byte-identical
rally predictions. Primary legacy-reference TP/FP/FN remained 36/0/0, mean IoU
0.871025665, start/end MAE 28.25/10.472222 frames, and duration MAE 1.111111 s.
The preserved reports record 2,490 application/engine/sport/API/benchmark and 686
research tests passing, with one optional browser control skipped. These are
existing validation receipts; this planning review did not rerun those tests.

No additional **confirmed, incompletely implemented Test 1 code repair** was
identified in the reviewed evidence. The user now explicitly authorizes proceeding
to Test 2. Earlier report text saying Test 2 had not started describes its original
completion state, not an ongoing prohibition after that authorization.

The following Test 1 limitations remain distinct from unresolved software defects:

- Legacy player slots change physical athlete; point slots are not stable IDs or
  bounding-box labels. AP/mAP/IoU and HOTA/IDF1 require different reviewed labels.
- `Full2` supplies only 20 numeric positive intervals plus an ellipsis record.
  Unknown coverage cannot establish false-positive or precision denominators.
- Coarse cumulative score conventions disagree with visible broadcast scores and
  with some alternative rows. Player A/B mappings are not source-bound.
- Unknown winners and public heatmap/highlight abstention follow missing identity
  and official-play evidence. Forcing IDs or official flags would fabricate data.
- A probable raw shuttle shoe distractor at Test 1 frame 13153 remains a diagnostic
  hypothesis needing a motion window and independently reviewed physical label.
- Earlier contact candidates canceled by maturity/witness gates are real machine
  mechanisms, but preparation/pickup versus short play needs continuous footage.
- The reviewed manual court rectangle follows singles lines, whereas the current
  automatic outer rectangle describes doubles lines. Comparing unlike corners
  creates a false calibration error.

## Historical Test 2 evidence to reuse

Historical root:
`artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/`.
Readable reports:
`research/test_video_benchmarks/reports/test_02/TEST2_EVALUATION_REPORT.md`,
`TEST2_FAILURE_ANALYSIS.md`, `TEST2_COMPONENT_VALIDATION.md` and
`TEST2_REPRODUCTION.md`.

The historical recording is `Test2_Full_Rev.mp4`, source SHA256
`4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`,
2,453,914,397 bytes, source 1920x1080 at exact zero-origin CFR 30, 29,296 decoded
frames. The historical 1280x720 proxy hash is
`2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd`.
These are pairing checks for a new download, not permission to bypass validating
the newly consumed bytes and complete execution.

The historical rally-only record already has 67 TP / 6 FP / 6 FN against 73
generated reference intervals, F1 0.917808 and mean IoU 0.849962. The separate
75-row coarse reference has F1 0.905405. Preserve those immutable results; they
are not a current post-Test-1-fix baseline. New inference is justified by the
requested latest-pipeline component evaluation and before/after repair evidence,
not by redoing the old interval-only benchmark as if it were missing.

Later shared repair reports additionally preserve an inherited-improvement fresh
Test 2 record: 75 predictions, 68 TP /7 FP /5 FN, F1 0.918919 and mean IoU
0.848135, with its original catalogue failure and separate strict recovery
disclosed. That implementation already included compatible-format confirmation,
typed short-exchange evidence, stationary recovery, detector-layout corroboration
and spatial OCR fixes. Its full external run directory was retired during
authorized cleanup; retained compact receipts/reports describe historical results.
Do not confuse this later record with the original 67/6/6 run or the new baseline.

The historical evidence includes 40 predeclared significant cases, exact frame
traces, all-frame cached observations and a package of 6,551 source JPEGs.
Reuse source panels and exact frame IDs where their hashes and provenance remain
valid. Source interpretation remains agent diagnostic review rather than human
adjudication. Historical paths into retired run directories must not be treated
as proof that those full directories still exist; use retained artifacts and
compact receipts actually accessible today.

## Prioritized discriminating investigations

| Priority | Historical evidence and exact frame scope | Question for the current run | Fix gate and negative controls |
|---|---|---|---|
| 1 | Missed same-camera edit at 11346 with player teleport/score jump; prior false barrier7703 already vetoed by inherited detector-layout repair | Does the new baseline still lack a raw hypothesis/probe when only one prior region exists? | Recorded51-case recomputation keeps49barriers/vetoes7703+23639;54tests pass. Use `scene_review/REPORT.md`, true cuts, continuous motion, camera changes, missing detections and doubles; no frame-ID exceptions |
| Resolved in inherited source; carry forward | OCR frame 22924: historical `SXFI21/LIVE12` branding reading despite athlete names in raw OCR text | Current `nearest-name-current-column-v2` already abstains on the existing exact-token/bounding-rectangle fixture | Deterministic history check reproduces the old bad reading and current abstention; 37 existing parser/provenance cases pass. See `ocr_pairing/REPORT.md`. No additional parser repair justified |
| 2 | G69 continuous overhead/high-clear play: gap terminal 27325, publication 27348, reacquisition 27349; reference spans 26616–27668 | Trace raw provider absence, association rejection, predicted/reconstructed support and terminal/publication policy separately | Distinguish perception dropout from software evidence loss. Require independent continuity witnesses; preserve true post-point gaps, edits and pickups. Do not globally extend timeout from one example |
| 2 | G31/G32/G56/G63 short activity versus G58 relaxed walking/handling around 21745–21795 | Inherited typed witness code already supports G31/G32; what remains missing for G56/G63? | Retain negative walking/handling control and distinguish preparation/retrieval from play. Never lower maturity merely to fit reference intervals |
| Carry-forward regression | Startup first reference frame53, first selected coordinate77, contact82, historical format reset95, inferred format96, readmission101 | Current compatible-format confirmation already preserves supported candidates; verify current run carries the fix | Do not repeat that repair; retain unknown→confirmed and singles/doubles transition controls without retrospectively certifying uncertain-format contact |
| 3 | G41/G71 post-point pickup continuation | Are inferred motion/contacts wrongly sufficient to reopen or extend official play? | Separate rally candidate from confirmed impact/official point; do not manufacture winner labels or terminate from an unverified shuttle estimate |

Historical G11/reference 3863–4215 spans an edit between play contexts; G5 starts
with service preparation, and FP45 around 15490–15565 appears to contain real net
play omitted by the chosen reference. Preserve their numerical FP/FN/error values,
but do not “fix” the pipeline to remove genuine activity or cross an edit solely
to improve agreement. These examples are annotation/context controls.

## Reusable tools and adaptation limits

| Tool | Useful purpose | Constraint before reuse |
|---|---|---|
| `research/production_external_stress.py` | Source/config/model bound fresh preparation and execution | New immutable output directory; actual latest source snapshots; video only, no annotation input |
| `research/normal_timestamp_audit.py` | Full source/proxy timestamp and decoded-frame audit | Use tracked retained helper, not deleted historical run paths |
| `research/test2_timestamp_validation.py` | Bind source PTS and completed proxy/inference identity | Reject offsets, VFR or incomplete coverage rather than guessing mapping |
| `research/test2_annotation_audit.py` | Exact schemas, coarse seconds conversion and interval data quality | Requires actual rational FPS and frame count; no filename-based human-GT claim |
| `scripts/benchmarking/evaluate_rallies.py`, `research/test2_evaluation.py` | Fixed interval matching, errors and source-review case selection | Keep current policy/half-open endpoint convention; unmatched errors unavailable |
| `research/test2_component_diagnostics.py` | All-frame stage/cache coverage and event observations | Successful completed-run binding required; counters are not component accuracy |
| `research/test2_causal_analysis.py` | Per-frame gate/transition summaries | Own-source exact replay and source-bound cache; no causal physical claims from absence alone |
| `research/test2_failure_package.py`, `research/test2_source_frame_cache.py` | Exact-PTS synchronized evidence and reusable source JPEGs | Strict replay/source/timebase proof; link existing images where source hashes match |
| `research/test2_resource_report.py` | Runtime and worker-attributed GPU memory/resource summary | Record actual worker PID/GPU UUID; keep shared-resource limitations explicit |
| `evaluation/ground_truth_validation/orchestration/export_completed_analytics.py` | Real completed-run analytics/highlights | Generic source binding; no forced identities, official flags or synthetic highlights |
| `evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py` | Useful comparison methodology and explicit unavailable metrics | **Not directly reusable for Test 2:** hard-coded Test 1 SHA, 17,268 frames, names/court frame and coordinate certificate. Create explicit Test 2/generalized contract; never bypass guards |

`distribution()` currently includes every raw value. Save raw distributions in
JSON or CSV, but summarize count/mean/median/P90/P95/min/max in Markdown to avoid
unreadable multi-megabyte report cells.

## New baseline and evaluation requirements

1. Inventory only Test 2's seven available files, hash originals, verify whether
   the two ball-filled exports are byte-identical, and explicitly record that no
   `Full2` exists if the current source inventory confirms this. Separate coarse
   outcomes, generated interval/winner outputs, point slots, filled trajectory,
   and the single declared court frame.
2. Download only the exact paired Test 2 original and preserve its Drive object
   reference, digest, source metadata and decoded PTS map. Source image coordinates
   must be mapped to the declared 1280x720 annotation space without fitted offsets.
3. Freeze current source/config/model identities and record actual enabled and
   unavailable stages. Do not silently describe an absent racket network or
   pose-derived racket heuristic as an independently validated detector.
4. Complete a fresh baseline before any new production fix. Preserve complete
   cache/frontier/event ledgers, model/provider evidence, logs, wall/CPU/GPU/RAM
   measurements and actual analytics/highlight exports. Read annotation labels
   only for offline comparisons; never feed their coordinates/ends into inference.
5. Independently review coordinate/timeline semantics before computing anonymous
   player-point/shuttle disagreement or court-corner distances. These are generated
   output comparisons, not physical precision/recall. Include missingness and
   current-versus-carried observation populations. Do not equate slots with IDs.
6. Report unsupported player-box, tracking-ID, pose-joint, contact, stroke-class,
   official outcome/score, heatmap and highlight accuracy as unavailable with an
   exact missing-label prerequisite. Rally-wide `ball_types` is not exhaustive
   per-contact stroke truth. Preserve coarse outcome inconsistencies by row.
7. Diagnose current high-impact failures with synchronized full windows and actual
   gate transitions, using the historical positive/negative controls above.
8. Implement only reproduced generic defects. Capture before-fix failure and
   after-fix success, then fresh-run Test 2 with a separate source/config manifest.
   Rerun Test 1 when affected stage changes could alter its outputs; a replay is
   supplemental and cannot be described as a fresh perception regression.
9. Hash and verify retained outputs and report links before deleting only the
   newly downloaded Test 2 source and provably disposable temporary video data.
   Preserve original annotation files, reusable proxies/evidence and all previous
   benchmark records. Do not move to Test 3 until these deliverables are verified.

## Focused regression families

Carry forward `test_rally_recovery_cut_frontier.py`,
`test_score_mapping_vote_provenance.py`, and
`test_stabilized_player_ground_point.py` unchanged.

For scene changes, inspect `test_scene_layout_decision.py`,
`test_scene_continuity.py`, `test_scene_continuity_v2.py`,
`test_scene_decision_cache.py`, `test_shuttle_scene_boundaries.py`,
`test_contact_scene_boundaries.py`, `test_camera_recovery_state.py` and
`test_scoreboard_scene_policy.py`. Include cache identity/replay provenance when
any scene decision algorithm changes.

For scoring/OCR changes, use `test_score_ocr.py`, `test_score_ocr_delay.py`, the
source-transition provenance cases and generic provider/parser tests discovered
with the actual extraction boundary. Row text is an observation; named-player
binding and accepted-point ownership remain separate contracts.

For gap/short-exchange changes, retain `test_rally_observed_continuity.py`,
`test_rally_short_exchange_evidence.py`, `test_rally_terminal_admission.py`,
`test_rally_evidence_segments.py` and relevant contact provenance controls.
Before broad testing, choose the narrow family matching the verified defect;
broaden after a meaningful code change or unresolved failure, not repeatedly
without new evidence.

## Scope of this review

The initial planning review wrote only this document. Subsequent explicitly
assigned independent reviews are preserved under `ocr_pairing/`, `scene_review/`
and `current_scene_and_ocr_review/`, including deterministic controls and bounded
standalone CPU OCR probes. The root orchestrator owns fresh full-video inference.
No production code, original data, historical report, model or pipeline setting
was modified by this reviewer, and no GPU inference was run by it. Experimental
RED contracts and isolated counterfactual classes remain diagnostic evidence,
with rejected alternatives explicitly identified.
