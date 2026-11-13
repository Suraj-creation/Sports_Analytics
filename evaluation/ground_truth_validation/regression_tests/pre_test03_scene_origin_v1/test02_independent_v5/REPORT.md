# Independent Test2 V5 completed-run review

**Gate: HOLD.** Coarse-reference row33 remains missed and coarse recall/F1 decline slightly. Generated-reference agreement improves. The additional13452 reset and newly changed raw-shuttle observations require source adjudication. These mixed results do not establish all-component nonregression or physical accuracy. No merge/push/cleanup acceptance is issued here.

This independently reviews the actual fresh29,296-frame Test2 run from frozen native commit `5ae614826e6f909defb02445386962ac13b4641a`. The genuine worker, parent, catalogue, all workflow stages, own-run semantic replay,5,740 completed artifacts,289 recorded producer sources and all90 protected inputs passed. The90 protected inputs are62 original MAIN annotations,7 candidate Test2 annotation references and21 other protected inputs; these are separate path scopes, not a combined annotation count. The full native decoder/auditor validated codec24/rawV5/decisionV4 source foreground, court, camera, and format proofs without rebasing any ROOT.

## Reference metrics

Matching remains maximum-cardinality assignment followed by IoU, with eligibility IoU≥0.5 and the original canonical30FPS interval conventions. Start/end/duration errors are conditional on matched intervals; boundary tolerance coverage additionally reports all-reference denominators. Missing predictions are not assigned zero localization error. The two generated interval tables agree in timing; they are not two independent truth sets.

| Reference | Arm | TP | FP | FN | Precision | Recall | F1 | Mean IoU |
|---|---|---:|---:|---:|---:|---:|---:|---:|
|Test2_Full.csv|fresh dacc baseline|69|6|6|0.920000|0.920000|0.920000|0.830665|
|Test2_Full.csv|preserved2418 secondary|68|6|7|0.918919|0.906667|0.912752|0.838095|
|Test2_Full.csv|freshV5|68|5|7|0.931507|0.906667|0.918919|0.847805|
|Test2_Full_rally.csv|fresh dacc baseline|68|7|5|0.906667|0.931507|0.918919|0.849311|
|Test2_Full_rally.csv|preserved2418 secondary|68|6|5|0.918919|0.931507|0.925170|0.830790|
|Test2_Full_rally.csv|freshV5|69|4|4|0.945205|0.945205|0.945205|0.833925|
|win_predictions.csv|fresh dacc baseline|68|7|5|0.906667|0.931507|0.918919|0.849311|
|win_predictions.csv|preserved2418 secondary|68|6|5|0.918919|0.931507|0.925170|0.830790|
|win_predictions.csv|freshV5|69|4|4|0.945205|0.945205|0.945205|0.833925|

All raw missed-reference IDs, false-prediction IDs, matched pairs, per-row signed/absolute boundary errors and durations remain in the [native reference rows](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5/bound_reference_diagnostics/reference_row_comparisons.json) and [independent row differences](interval_reference_differences.json). No earlier matrix was re-evaluated or overwritten.

### Complete matched error summaries

Values are baseline→V5. Full_rally and win_predictions have identical timing metrics; win_predictions retains a separate matrix and its outcome columns remain unverified.

| Reference | Error | MAE | Median absolute | RMSE | Maximum absolute | P90 absolute | Mean signed | Median signed |
|---|---|---:|---:|---:|---:|---:|---:|---:|
|Test2_Full.csv|start_frame|24.608696→21.455882|17.000000→16.500000|38.425535→34.455214|197.000000→197.000000|42.800000→35.600000|6.550725→7.926471|12.000000→11.500000|
|Test2_Full.csv|end_frame|17.536232→17.588235|9.000000→9.000000|41.195539→41.439893|305.000000→305.000000|34.600000→35.400000|-4.318841→-3.852941|-1.000000→-0.500000|
|Test2_Full.csv|start_time_sec|0.820290→0.715196|0.566667→0.550000|1.280851→1.148507|6.566667→6.566667|1.426667→1.186667|0.218357→0.264216|0.400000→0.383333|
|Test2_Full.csv|end_time_sec|0.584541→0.586275|0.300000→0.300000|1.373185→1.381330|10.166667→10.166667|1.153333→1.180000|-0.143961→-0.128431|-0.033333→-0.016667|
|Test2_Full.csv|duration_sec|1.126570→1.061275|0.766667→0.733333|1.860246→1.813327|10.633333→10.633333|1.873333→1.763333|-0.362319→-0.392647|-0.466667→-0.483333|
|Test2_Full_rally.csv|start_frame|24.161765→27.231884|11.500000→15.000000|41.198051→43.918403|167.000000→167.000000|72.300000→75.000000|19.367647→22.768116|6.500000→10.000000|
|Test2_Full_rally.csv|end_frame|20.867647→20.913043|10.000000→10.000000|47.952642→47.664741|343.000000→343.000000|45.400000→44.600000|-9.602941→-8.913043|-2.000000→-2.000000|
|Test2_Full_rally.csv|start_time_sec|0.805392→0.907729|0.383333→0.500000|1.373268→1.463947|5.566667→5.566667|2.410000→2.500000|0.645588→0.758937|0.216667→0.333333|
|Test2_Full_rally.csv|end_time_sec|0.695588→0.697101|0.333333→0.333333|1.598421→1.588825|11.433333→11.433333|1.513333→1.486667|-0.320098→-0.297101|-0.066667→-0.066667|
|Test2_Full_rally.csv|duration_sec|1.300980→1.398068|0.633333→0.900000|2.278093→2.332194|12.700000→12.700000|3.010000→3.053333|-0.965686→-1.056039|-0.400000→-0.566667|

### IoU and tolerance coverage

| Reference | Median IoU | Minimum IoU | >0.5 | >0.75 | >0.9 | >0.95 |
|---|---:|---:|---:|---:|---:|---:|
|Test2_Full.csv|0.871009→0.876389|0.512915→0.569620|100.000000→100.000000|73.913043→76.470588|40.579710→45.588235|14.492754→17.647059|
|Test2_Full_rally.csv|0.881085→0.870504|0.504087→0.500000|100.000000→98.550725|80.882353→76.811594|45.588235→43.478261|27.941176→26.086957|

The percentages above use strict `>`; one eligible exact0.5 match therefore need not count as >0.5.

| Reference | Boundary | Tolerance(frames) | Within count | Matched fraction | All-reference fraction |
|---|---|---:|---:|---:|---:|
|Test2_Full.csv|start|1|4→5|0.057971→0.073529|0.053333→0.066667|
|Test2_Full.csv|start|3|6→9|0.086957→0.132353|0.080000→0.120000|
|Test2_Full.csv|start|5|9→12|0.130435→0.176471|0.120000→0.160000|
|Test2_Full.csv|start|10|22→26|0.318841→0.382353|0.293333→0.346667|
|Test2_Full.csv|start|15|28→32|0.405797→0.470588|0.373333→0.426667|
|Test2_Full.csv|start|30|58→58|0.840580→0.852941|0.773333→0.773333|
|Test2_Full.csv|end|1|11→11|0.159420→0.161765|0.146667→0.146667|
|Test2_Full.csv|end|3|17→17|0.246377→0.250000|0.226667→0.226667|
|Test2_Full.csv|end|5|21→21|0.304348→0.308824|0.280000→0.280000|
|Test2_Full.csv|end|10|37→35|0.536232→0.514706|0.493333→0.466667|
|Test2_Full.csv|end|15|49→48|0.710145→0.705882|0.653333→0.640000|
|Test2_Full.csv|end|30|61→60|0.884058→0.882353|0.813333→0.800000|
|Test2_Full_rally.csv|start|1|10→10|0.147059→0.144928|0.136986→0.136986|
|Test2_Full_rally.csv|start|3|18→14|0.264706→0.202899|0.246575→0.191781|
|Test2_Full_rally.csv|start|5|24→20|0.352941→0.289855|0.328767→0.273973|
|Test2_Full_rally.csv|start|10|33→29|0.485294→0.420290|0.452055→0.397260|
|Test2_Full_rally.csv|start|15|40→36|0.588235→0.521739|0.547945→0.493151|
|Test2_Full_rally.csv|start|30|52→51|0.764706→0.739130|0.712329→0.698630|
|Test2_Full_rally.csv|end|1|9→8|0.132353→0.115942|0.123288→0.109589|
|Test2_Full_rally.csv|end|3|16→15|0.235294→0.217391|0.219178→0.205479|
|Test2_Full_rally.csv|end|5|25→24|0.367647→0.347826|0.342466→0.328767|
|Test2_Full_rally.csv|end|10|35→35|0.514706→0.507246|0.479452→0.479452|
|Test2_Full_rally.csv|end|15|43→43|0.632353→0.623188|0.589041→0.589041|
|Test2_Full_rally.csv|end|30|56→57|0.823529→0.826087|0.767123→0.780822|

## Short-exchange and annotation disagreement

Coarse row33 is11700–11760; generated Full_rally/win row31 is11714–11830. All are currently missed, but the endpoint/coverage conventions differ. The dacc baseline matched the coarse row with11715–11751. Its lost early kinematic contact is not independent physical impact truth. The preserved2418 arm and currentV5 both miss this short exchange. Raw references remain immutable. The separately sealed [current short-case diagnosis](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/component_evaluations/pre_test03_test02_short_event_v5_review_v1/REPORT.md) verifies86 current raw frames identical to2418 except the content-epoch offset, pose stride1 here, and the same cancellation. See [short-row evidence](short_coarse_row33_current.json), [secondary comparison](secondary_2418_comparison.json), and the separate source-bound contact diagnosis.

The coarse table is75 rally-level rows; two trajectory CSVs are byte-identical generated filled estimates and are deduplicated. Player detections contain generated bottom-center slots, not labelled boxes or stable athlete identities. Court JSON is a source-bound manual single-frame candidate. Rally-level ball_types/player/win/score fields do not supply complete per-contact classes, physical identities or independently adjudicated score sequences. All7 files are accounted for by [native applicability records](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5/bound_reference_diagnostics/component_reference_metrics.json).

## Scene proofs and source controls

Every one of the36 dacc barriers remains. Four formerly lost real edits2928/11082/22416/23279 are restored. All9 source-reviewed weak resets and6151/6307/11346 remain;7703/23639 keep no-barrier decisions. There are49 actual content increments,41 raw hypotheses,274 relative layout/camera claims and4 cross-chunk camera claims. New weak13452 is additional to the nine earlier weak cases and requires its own source gate. Raw hypothesis and accepted epoch-increment counts deliberately differ.

The only source-format transition flag is chunk120: cache60–119 is encoded before ingest infers singles at96; next process120 correctly sees the now-confirmed format. This is the producer order, not proof forgery. Every weak decision uses its actual confirmed chunk-start context. See [source-order review](initial_format_transition_review.json), [full camera/format audit](crosschunk_camera_format_audit.json), and [native proof receipt](native_guard_receipt.json).

## Full populations and point agreement

Generated-reference distances are diagnostic agreement only. Current source-slot assignments preserve all57,305 dacc pairs and add404; mean3.461802→3.262098px, maximum429.411529→256.206844px. Common pairs improve in aggregate. Fresh-detector assignments grow24,129→24,530, with160 old-only and561 new-only pairs explicitly retained. Among23,969 common fresh assignments,23,964 are exact and5 improve; none worsen.

Against2418, all57,708 old assignments remain plus1 new. Common carried/all-row distances change on224 pairs:102 increase and122 decrease. Their mean3.277068→3.262147px;24,458 common fresh-detector assignments are exactly equal. Fresh-only population changes still matter:51 old-only versus72 new-only. The largest new common increase is21.351139px at13552 with a fresh→carried observation change, followed by13553;11111 has a17.817px increase. These require source context rather than a physical identity-error claim.

Raw admitted-person rows fall58,452→58,102 versus dacc. All754 lower-count frames occur in five intervals between5960 and6729, where known staff/athlete admission changes must be interpreted using source evidence. All832 unmatched historical regions,482 new unmatched regions and their time groups remain recorded. Against2418 raw person rows58,101→58,102 and there are **zero lower-count frames**. This is measured model-output population, not a physical recall/FN score.

The largest overall generated-point outliers14453 and13436 are inherited and unchanged; they are not newly introduced V5 errors. [Primary populations](point_population_decomposition.json), [all lower-count frames](all_current_gross_population_losses.json), [all unmatched historical regions](all_historical_regions_without_overlap.json), [secondary changes](secondary_point_populations_and_worsenings.json) and [all raw coverage](secondary_raw_coverage_and_shuttle_changes.json) preserve full populations.

### Shuttle and cadence questions

The dacc/current common both-present shuttle diagnostic mean is5.955751→5.955087px across19,942 frames. Aggregate similarity hides local changes. Against2418 there are191 presence changes,1,556 both-present XY changes,1,666 support changes and215 association-status changes. The largest XY delta is398.71px at23542: current prediction near572.53,439.64 versus old767.94,92.10. Current23535/36/42 appears nearly stationary in coordinates while old observations move near the top-right image; source inspection must establish whether either prediction is the physical projectile. Filled historical points agree with the old hypothesis but are not physical truth. This remains a HOLD source question.

Frames25680–25739 contain **12 actual detector executions and24 fresh person rows**; all60 records are retained, separating current detector matches, carried boxes and scene-only foreground. The known dacc→V5 generated-distance increase at25720 reflects altered observation cadence. It is not new against2418. See [exact cadence rows](actual_cadence_window_25680_25739.json) and [focused new source plan](additional_source_frame_plan.json).

## Component execution, uncertainty and downstream outputs

| Coverage | V5 count |
|---|---:|
|raw_shuttle_present|20024|
|detector_executed_frames|12435|
|person_rows|58102|
|person_current_detector_matches|24711|
|person_propagated_or_unmatched|33391|
|pose_current_source_rows|46457|
|pose_current_on_propagated_box|21856|
|racket_present_rows|20548|
|racket_current_source_rows|20548|

Raw racket observations20,548 remain preserved. Exactly4,299 unique frame/owner candidates have explicit semantic abstention events, leaving16,249 admitted candidate rows. This is semantic coverage, not improved racket precision. Pose source freshness on21,856 carried boxes is also distinct from correct joint localization. Court frame300 has mean1.550521px/max2.195053px disagreement against the reviewed single-frame singles-corner candidate, not all-frame physical court accuracy.

Live contacts/strokes816→818, unknown strokes586→585; rally ends75→73. Five same-anchor predicted class changes are recorded, with no independent stroke labels. Exact-anchor additions/removals are40/38; nearby shifted-event association is unavailable because rally populations changed, so no claim of zero true shifts is made. All anonymous source-region changes are retained; named contact actors and known winners stay0.

All73 rally winners are unknown; this is unavailable outcome accuracy, not zero accuracy. There are47 official and26 unofficial rally records,818 unattributed live strokes,5 highlight events and **zero canonical named-player heatmap grids**. Empty grids were not fabricated. Broadcast score observations are not accepted point decisions or a verified final score.

| Unavailable physical metric family | Required evidence |
|---|---|
|player_AP_mAP_IoU|Independently reviewed boxes and complete positive/negative coverage; supplied generated points are not boxes.|
|tracking_IDF1_HOTA_ID_switches_fragmentation|Reviewed persistent athlete identities, boxes and visibility; two generated detection slots are not persistent IDs.|
|pose_PCK_OKS|Reviewed keypoints and joint visibility, skeleton convention and scale.|
|shuttle_physical_localization_PR|Independent reviewed coordinates/visibility; filled model estimates do not identify interpolated frames.|
|racket_contact_PR_F1_temporal_error|Reviewed contact/racket times and negative windows, not rally-level labels.|
|stroke_per_class_PR_F1_confusion|Complete per-contact stroke taxonomy and labels; a single ball_types field per coarse rally is insufficient.|
|winner_outcome_accuracy_PR_F1_confusion|Verified symbolic Player A/B identity and source-bound adjudicated outcomes; win_predictions is generated.|
|score_sequence_accuracy|Reviewed broadcast identity, point alignment and score sequence, accounting for edited-video omissions.|
|highlight_quality|Reviewed highlight relevance/boundaries; rally overlap and execution are not relevance accuracy.|
|player_analytics_accuracy|Reviewed participant identities and metric-specific physical movement/event labels.|

All10 families remain null. No independently labelled box AP/IoU, tracking IDF1/HOTA/switches, pose PCK/OKS, physical shuttle PR, racket/contact PR/F1, stroke confusion, outcome accuracy, score accuracy, highlight quality or named-player analytics accuracy is manufactured.

## Runtime and reproducibility

| Measure | Fresh dacc baseline | FreshV5 |
|---|---:|---:|
|parent_completed_elapsed_s|3393.230043|3656.233981|
|worker_elapsed_s|3381.987166|3645.819068|
|worker_source_fps|8.662363|8.035506|
|sampled_worker_gpu_peak_mib|2122|2132|
|sampled_worker_tree_peak_rss_bytes|3162554368|2964209664|
|worker_maxrss_bytes|3194896384|2981371904|

These are wall-clock run scopes including initialization/media/postprocessing, not isolated neural throughput. Stage timings overlap and must not be summed. Sampling may miss short GPU peaks, shared-page RSS can double-count, and shared-host contention is not controlled.

Actual allocated physicalGPU1 is NVIDIA GTX1080Ti, UUID `GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab`. TrackNet uses Torch CUDA FP16; RFDETR and pose use ONNX CUDA with CPU fallback available but no reported backend fallback. OCR and racket/content geometry use CPU. Numerical profile, source/proxy pair and recorded model asset identities equal the baseline. The runtime model metadata records RFDETR1.4.2, RTMPose body7 archive1.0, TrackNet3.0 and RapidOCR3.10.0 with exact primary and OCR asset hashes. ReID/OSNet is unavailable in the production profile; an isolated research crop probe is not a loaded production model.

The component report’s `executed_models:null` is a reporting-field limitation. Actual evidence is [worker models/backends](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5/run/inference.json) and [analysis model verification](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5/analysis/technical_analysis.json), not a claim that inference failed. [Runtime/configuration/model/source review](runtime_provenance_review.json) and [protected input scopes](protected_input_scope_counts.json) preserve exact paths and hashes.

## Retained evidence and next gates

The complete520-frame review plan is preserved and split into5 batches of at most128 frames; the separate8-frame supplemental plan includes only meaningful new point/carry and raw-shuttle questions. Existing108-frame source verification and the new13452 review remain parent-owned source adjudication. They are diagnostic visual checks, not new independent physical labels.

- [Independent summary](summary.json), [reference deltas](interval_reference_differences.json), [point populations](point_population_decomposition.json), [events and anonymous actor regions](event_differences.json).
- [Raw observation differences](raw_shuttle_value_status_association_differences.json), [scene records](scene_boundary_review_inputs.json), [secondary raw changes](secondary_raw_coverage_and_shuttle_changes.json).
- [Original complete native matrices](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5/bound_reference_diagnostics/component_reference_metrics.json), [full row comparisons](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5/bound_reference_diagnostics/reference_row_comparisons.json), [source plan](source_frame_plan.json), [focused supplemental plan](additional_source_frame_plan.json).

HOLD remains appropriate until coarse row33 and the new source questions are resolved or explicitly adjudicated with a defensible acceptance decision. Pipeline source, frozen baselines, original annotations, model assets and all failed historical evidence remain untouched. No Test3 data, new neural execution, merge, push or cleanup was performed by this review.
