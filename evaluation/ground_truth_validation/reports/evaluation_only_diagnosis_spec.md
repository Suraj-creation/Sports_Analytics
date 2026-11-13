# Sequential evaluation-only diagnosis specification

Recorded 2026-11-12 against MAIN commit `88aa0ad47d6be8dc1f073d0297efdb430b6ceaa0`.

The current instruction is to evaluate **Test3 → Test4 → Test6 → Test7 → Test9 → Test10**, one large video at a time. Tests5 and8 are excluded. Test1/2 repair gates have been stopped by user instruction; preserve their existing records rather than rerunning them. The merged code is the fixed evaluation implementation for this sequence. No component fix, threshold change, model change, debugging patch or tuning is authorized during individual evaluations. Record new defects and proposed changes for later work.

## Evidence scope and outstanding Test1/2 limitations

The most recent completed Test2 comparison before this sequence is the preserved5ae fresh run, not a completed88aa Test2 run. Its primary coarse reference had TP68/FP5/FN7, precision0.931507, recall0.906667, F1=0.918919 and matched meanIoU0.847805. The two generated interval references had TP69/FP4/FN4, precision/recall/F1=0.945205 and meanIoU0.833925. These disagree because annotation definitions differ; neither replaces the other. Earlier dacc fresh results remain separate. This report does not claim that88aa reproduces those scores.

Preserved limitations requiring future investigation:

- Coarse row33,11700–11760, remains missed in completed5ae. The motion-started11716–11751 hypothesis was canceled by existing duration policy without independently qualified opposite-episode evidence. The callbacks11731/11740 belong to the same far episode. The first near physical impact is ambiguous. Do not manufacture11715 contact or bypass the short-exchange policy to restore a label.
- Source-visible floor-logo selection at23534/35/36/42 exposed an association error. The merged v3 association preserves raw NN coordinates/confidence and may select an observed alternative with explicit current-candidate support/provenance, or abstain. Bounded component controls supported the repair; full Test1/2 fresh acceptance was stopped. Test3 onward must measure actual resulting coverage and failure cases without assuming a four-frame physical-accuracy gain.
- Sparse player sampling at13552/53 and25680–25739 contributed to carried-box lag in the prior run. The merged acquisition controller has source-bound motion proofs and cadence provenance; future reports must measure actual requested/executed cadence and abstentions. Nominal configured stride is not evidence that detection ran on every frame.
- Real edits at2928/11082/22416/23279 were restored by the completed5ae source-origin scene contract;7703/23639 remained continuous controls. Source-scene hypotheses, participant admission, scene-only foreground and actual epoch barriers must remain distinct. Exclusive feature-origin masks do not prove distinct physical actors or statistically independent photometric pixels.
- Anonymous episode IDs are not named athletes. Named identity, winner mapping and many contact/stroke/score/pose/racket accuracy metrics remain unsupported by available independent labels. Existing raw shoe-adjacent shuttle errors, carried-box lag and racket/body false positives are not all resolved by the merged changes.
- The firstV6 fresh attempt failed before a cache was published because an actual NumPy-valued masked peak was rejected at the strict provider-to-wire boundary. The narrow normalization fix is included in88aa. That failed run and V6/V7 preparation remain historical records, not completed metrics.

Historical paths remain evidence references only. Deleted auxiliary checkout paths must never be recreated or substituted as native producer ROOTs. Use MAIN for every new command below. Do not revise historical metrics, receipts or annotation bytes.

## Native stage sequence for arbitrary videos

The following source-reviewed CLI sequence works without Test1/2-specific regression wrappers. It is a command specification, not a claim that Test3 has run. Use a new external artifact directory and the reviewed manifest produced by annotation inspection. `$EVAL_VIDEO`, `$EVAL_ART` and `$EVAL_MANIFEST` denote actual absolute paths chosen by the orchestrator; the source must be completely downloaded, hashed and paired before preparation.

```bash
cd /home/administrator/Desktop/sport-analytics/Sports_Analytics
source ../gpu-env.sh
export PYTHONPATH="$PWD/sports/badminton/src:$PWD/engine/src:$PWD/agents/src:$PWD/apps/api/src:$PWD"

.venv/bin/python research/production_external_stress.py prepare-upload \
  --case test3 --video "$EVAL_VIDEO" \
  --profile-source "$PWD/config/profiles/experimental-pipeline-repair-v1.yaml" \
  --output "$EVAL_ART/protocol"

.venv/bin/python research/production_external_stress.py run \
  --case test3 --plan "$EVAL_ART/protocol/plan.json" \
  --output "$EVAL_ART/run" --gpu-index 1

.venv/bin/python research/normal_timestamp_audit.py \
  --run "$EVAL_ART/run" --output "$EVAL_ART/timestamps"

.venv/bin/python evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py \
  --mode analysis --producer-root "$PWD" --tool-root "$PWD" \
  --run "$EVAL_ART/run" --output "$EVAL_ART/analysis"

.venv/bin/python evaluation/ground_truth_validation/orchestration/evaluate_manifest_components.py \
  --run "$EVAL_ART/run" --manifest "$EVAL_MANIFEST" \
  --output "$EVAL_ART/component_reference_diagnostics"

.venv/bin/python evaluation/ground_truth_validation/orchestration/export_completed_analytics.py \
  --run "$EVAL_ART/run" --output "$EVAL_ART/downstream_exports"
```

Repeat with a new matching `case` and session for each later video; `prepare-upload --case test3` produces session `UPLOADTEST3`. Derive the actual session ID from the preserved session JSON rather than borrowing Test1/2 IDs.

An optional exact own-run semantic replay uses the same completed observation caches and no neural inference. If requested for reproducibility, use the actual session ID and canonical frame count:

```bash
.venv/bin/python research/production_external_semantic_replay.py \
  --run "$EVAL_ART/run" --session UPLOADTEST3 \
  --output "$EVAL_ART/diagnostic_replay" --focus "" \
  --trace-ranges "[[0,$EVAL_FRAME_COUNT]]"
```

Do not set source-intervention, geometry-bracket or experimental contact flags during this evaluation. Preserve actual replay parity/failure; a replay is separate from new NN inference. The manifest evaluator already compares every declared interval reference, so a duplicate rally-only evaluator is unnecessary unless a separately requested original report requires it.

## Guards, caveats and reporting

1. Preserve the MAIN commit, all relevant source bytes, profile source and prepared passive-diagnostic profile, manifest/lock hashes, actual loaded model assets including packaged OCR, environment/backend/device declarations and executed commands. The existing prepare step records source snapshots. The full worker/parent/catalogue must complete before evaluating labels; no fake completion or cache-header changes are allowed.
2. `plan.root` is the external protocol staging directory. Actual source-file paths, executor command and imported native module paths bind MAIN. Do not equate protocol root to the source checkout, reassign imported ROOTs, patch module globals or import archived auxiliary sources.
3. `prepare-upload` requires verified CFR at unchanged proxy FPS and performs a frame count using the existing300-second timeout. Unsupported media, timeout or any guard failure is an evaluation failure: retain the complete log and partial artifacts. Do not silently change time basis, timeout, helper or pipeline.
4. The annotation manifest must inventory every immediate original supporting file and explicit reviewed role/schema/field eligibility. Dense frame coverage, exact source SHA/media and timestamps must agree. Filenames alone cannot establish roles. Byte-identical shuttle tables are deduplicated with aliases retained. Invalid/out-of-image coordinates remain flagged without clipping or filled ground truth.
5. Point/court disagreement requires a new source-bound coordinate certificate. Without binding, distances remain unavailable. Agent visual agreement and legacy generated coordinates are diagnostic references, not independent physical localization truth. Partial-positive interval files keep FP/precision/F1 null; unavailable never means zero.
6. Use `analyse_native_completed_run --mode analysis` for arbitrary videos. Its `components-test2` mode and both `export_test02_heatmaps.py` / `export_native_completed_heatmaps.py` are explicitly Test2-specific and reject arbitrary source SHA/media. Do not use or relabel these paths for Test3. Generic downstream export provides canonical analytics/individual estimates/highlight metadata; it does not render highlight clips or provide general grid export. Record standalone heatmap-grid export as unavailable with this helper limitation. Zero named grids is not a fabricated per-player heatmap.
7. The generic manifest evaluator compares **raw** shuttle NN coordinates against declared generated references. Associated selected-current-NN coordinates/support/provenance remain separately available in actual v3 caches. Report both roles distinctly in diagnosis; do not borrow raw confidence for an alternative or call model-generated agreement physical AP/recall.
8. Preserve interval precision/recall/F1, TP/FP/FN, all reference/miss/extra rows, IoU, every boundary/duration distribution and tolerance; event/stroke/outcome/scoring counts; coverage/abstentions; runtime/resources/model/backend provenance; annotation quality and field-specific limitations. Contact/racket/pose/tracking/stroke/winner/highlight physical accuracy stays null when the corresponding valid independent ground truth is absent.
9. At each observed failure, record source frame/time, annotation row/meaning, raw and admitted predictions, pose/detection freshness, source-shot/content epoch, camera/calibration, component configuration/version, rejection/unknown reason, downstream consequence and source-bound visual evidence. Rank a confirmed implementation defect separately from source annotation conflict, model ambiguity or unsupported metric.
10. No report is complete merely because inference succeeds. Verify retained artifact hashes, links and complete output population; publish a new immutable per-video report and cumulative index entry. Preserve original Test1/2 histories and distinguish current88aa results from historical aggregate scores.
11. Only after final evaluation/artifact verification may the orchestrator delete the owned downloaded large video and unnecessary temporary video-processing artifacts. Preserve original annotations, prediction/ledger/cache evidence, configuration, model identities, runtime logs and reports. All strict read-only guards require the original video at its recorded path; later re-evaluation after cleanup needs the same bytes restored and rehashed. A removed local copy must not be described as still guard-readable.

## Deferred improvement specification

For each new finding, propose the smallest reusable component change, evidence requirements, singles/doubles/unknown controls, failure/abstention semantics, cache identity/schema implications and before/after regression plan. Preserve observed coordinates versus tracker estimates and physical labels versus derived hypotheses. Proposed fixes are documentation only until the sequential evaluation and consolidated review are requested complete. No Test3-specific threshold/model adaptation or individual-video fixes should occur in this phase.

## Test3 annotation/source diagnosis before prediction review

Source-bound sparse inspection of ten canonical frames established a real broadcast edit between frames4204 and4207: a close-up with score17:15 changes to a wide view with score14:0. Opening-like reference points at4207 therefore do not by themselves establish a CSV time offset. The manual court polygon at4207 follows the outer singles floor rectangle. Dense player points are consistent with image-space box bottom centers; shuttle reference points include implausible racket/floor-logo cases and must remain generated diagnostic references. A source coordinate certificate permits agreement distances, not independent physical accuracy. No fix was made.

[Source overlays, certificate and exact evidence](../test_03/diagnostics/evaluation_only_v1/coordinate_review_v1/REPORT.md)

[New bound manifest](../test_03/annotations/evaluation_only_v1/evaluation_manifest_bound.json)

## Test10 completed retry — measured findings; no fixes implemented

The original frame-count timeout was retained. A new preparation-only deadline retry completed the same FFprobe command and was followed by fresh full native88aa0ad inference and all-six-file evaluation. No detector, temporal, matching or numeric configuration changes were made.

- Test10_Full.csv: TP=88, FP=10, FN=8, F1=0.9072164948453608. Missed reference IDs: [4, 22, 25, 29, 41, 57, 80, 88].
- Test10_Full_rally.csv: TP=85, FP=13, FN=8, F1=0.8900523560209425. Missed reference IDs: [9, 15, 30, 37, 40, 43, 55, 85].
- win_predictions.csv: TP=85, FP=13, FN=8, F1=0.8900523560209425. Missed reference IDs: [9, 15, 30, 37, 40, 43, 55, 85].

Review synchronized missed/extra boundary cases before proposing causal changes. Generated player/shuttle disagreement and manual-court comparison remain diagnostic; all unsupported physical accuracy prerequisites remain explicit.

[Complete report](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/reports/test_10_evaluation_only_v1.md) · [Visual evidence](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test10_retry1/visual_evidence)
