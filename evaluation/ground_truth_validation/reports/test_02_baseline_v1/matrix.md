# Test Video 2 — Complete Evaluation Matrix

This report records a completed fresh run of the current pipeline carrying Test1 fixes. Earlier rally benchmarks and original Part2 data remain immutable. Each annotation family is evaluated separately. Generated references are agreement diagnostics, not independently adjudicated physical ground truth.

A numeric zero describes an observed count or evaluated score. **Unavailable** means the necessary labels, identity, completeness or measurement contract is missing. Execution and unit-test success do not establish sporting accuracy.

## Reproducibility and implementation

| Item | Value |
|---|---|
| source_sha256 | 4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a |
| proxy_sha256 | 2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd |
| pipeline_commit | a53f95ffef26a23bac92531e87b74a17a3b09c26 |
| profile_source | /home/administrator/Desktop/sport-analytics/Sports_Analytics/config/profiles/experimental-pipeline-repair-v1.yaml |
| profile_source_sha256 | 280cbf717568fa2a7a1c3b476921bac1b48e9958bf65be0469fae7b5b2dae756 |
| profile_canonical_sha256 | 504816be296e38c30cea52dff6a2e52d72147f8d497044dad05bb36cb9a9a3e2 |
| source_file_count | 286 |
| media.fps_num | 30 |
| media.fps_den | 1 |
| media.n_frames | 29296 |
| media.width | 1280 |
| media.height | 720 |
| media.duration_us | 976533333 |
| media.codec | h264 |
| media.has_audio | True |
| media.source_width | 1920 |
| media.source_height | 1080 |
| media.source_codec | h264 |
| media.source_fps | 30 |
| media.variable_frame_rate | False |

The complete thresholds/profile are preserved in [experiment.yaml](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/protocol/profiles/experiment.yaml); exact source snapshots, per-file hashes and dirty-source status are in [plan.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/protocol/plan.json). Runtime packages and devices are in [environment.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/environment.json).

## Annotation coverage

| File | Role | Evaluation status |
|---|---|---|
| Test2_Full.csv | coarse_legacy_label_agreement | evaluated_with_reference_provenance |
| Test2_Full_Rev_ball_filled.csv | filled model estimate, not independent localization ground truth | generated_trajectory_diagnostic |
| Test2_Full_ball_filled.csv | filled model estimate, not independent localization ground truth | generated_trajectory_diagnostic |
| Test2_Full_court.json | manual asserted frame300; source/corner interpretation requires review | single_frame_manual_calibration_candidate |
| Test2_Full_rally.csv | legacy_generated_reference_agreement | evaluated_with_reference_provenance |
| player_detections.csv | bottom-center points; neither boxes nor stable physical identities | generated_point_slot_diagnostic |
| win_predictions.csv | legacy_generated_reference_agreement | evaluated_with_reference_provenance |

## Separate rally-reference agreement

Matching uses the preserved rally-boundaries-v1 policy: IoU eligibility ≥0.5; maximum-cardinality assignment, then total IoU and boundary-distance tie breaking; timestamp spans are half open. Boundary/duration/IoU scores condition on matched pairs; missed and extra proposals remain in detection metrics.

| Reference | TP | FP | FN | Precision | Recall | F1 | Mean IoU |
|---|---|---|---|---|---|---|---|
| Test2_Full.csv | 69 | 6 | 6 | 0.92 | 0.92 | 0.92 | 0.8332145284202773 |
| Test2_Full_rally.csv | 68 | 7 | 5 | 0.9066666666666666 | 0.9315068493150684 | 0.918918918918919 | 0.848134653705245 |
| win_predictions.csv | 68 | 7 | 5 | 0.9066666666666666 | 0.9315068493150684 | 0.918918918918919 | 0.848134653705245 |

### Test2_Full.csv

Reference role: coarse_legacy_label_agreement. Every original row and prediction match is preserved in [reference_row_comparisons.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/bound_reference_diagnostics/reference_row_comparisons.json).

| Aggregate metric | Value |
|---|---|
| detection.ground_truth_count | 75 |
| detection.predicted_count | 75 |
| detection.matched_count | 69 |
| detection.true_positives | 69 |
| detection.false_positives | 6 |
| detection.false_negatives | 6 |
| detection.precision | 0.92 |
| detection.recall | 0.92 |
| detection.f1 | 0.92 |
| overlap.mean_iou | 0.8332145284202773 |
| overlap.median_iou | 0.871008939974457 |
| overlap.minimum_iou | 0.5129151291512913 |
| overlap.percent_strictly_exceeding.0.5 | 100.0 |
| overlap.percent_strictly_exceeding.0.75 | 75.3623188405797 |
| overlap.percent_strictly_exceeding.0.9 | 40.57971014492754 |
| overlap.percent_strictly_exceeding.0.95 | 15.942028985507246 |
| boundary_and_duration_errors.start_frame.mae | 24.304347826086957 |
| boundary_and_duration_errors.start_frame.median_absolute_error | 17.0 |
| boundary_and_duration_errors.start_frame.rmse | 38.274939771249194 |
| boundary_and_duration_errors.start_frame.max_absolute_error | 197.0 |
| boundary_and_duration_errors.start_frame.p90_absolute_error | 42.80000000000001 |
| boundary_and_duration_errors.start_frame.mean_signed_error | 6.27536231884058 |
| boundary_and_duration_errors.start_frame.median_signed_error | 11.0 |
| boundary_and_duration_errors.end_frame.mae | 17.246376811594203 |
| boundary_and_duration_errors.end_frame.median_absolute_error | 9.0 |
| boundary_and_duration_errors.end_frame.rmse | 41.06410682780301 |
| boundary_and_duration_errors.end_frame.max_absolute_error | 305.0 |
| boundary_and_duration_errors.end_frame.p90_absolute_error | 34.60000000000002 |
| boundary_and_duration_errors.end_frame.mean_signed_error | -3.8550724637681157 |
| boundary_and_duration_errors.end_frame.median_signed_error | -1.0 |
| boundary_and_duration_errors.start_time_sec.mae | 0.8101449275362308 |
| boundary_and_duration_errors.start_time_sec.median_absolute_error | 0.5666666666666629 |
| boundary_and_duration_errors.start_time_sec.rmse | 1.275831325708305 |
| boundary_and_duration_errors.start_time_sec.max_absolute_error | 6.566666666666663 |
| boundary_and_duration_errors.start_time_sec.p90_absolute_error | 1.4266666666666485 |
| boundary_and_duration_errors.start_time_sec.mean_signed_error | 0.2091787439613519 |
| boundary_and_duration_errors.start_time_sec.median_signed_error | 0.36666666666667425 |
| boundary_and_duration_errors.end_time_sec.mae | 0.5748792270531389 |
| boundary_and_duration_errors.end_time_sec.median_absolute_error | 0.29999999999999716 |
| boundary_and_duration_errors.end_time_sec.rmse | 1.368803560926762 |
| boundary_and_duration_errors.end_time_sec.max_absolute_error | 10.166666666666629 |
| boundary_and_duration_errors.end_time_sec.p90_absolute_error | 1.1533333333333524 |
| boundary_and_duration_errors.end_time_sec.mean_signed_error | -0.1285024154589321 |
| boundary_and_duration_errors.end_time_sec.median_signed_error | -0.03333333333330302 |
| boundary_and_duration_errors.duration_sec.mae | 1.0961352657004755 |
| boundary_and_duration_errors.duration_sec.median_absolute_error | 0.7333333333333485 |
| boundary_and_duration_errors.duration_sec.rmse | 1.8451791214779507 |
| boundary_and_duration_errors.duration_sec.max_absolute_error | 10.633333333333326 |
| boundary_and_duration_errors.duration_sec.p90_absolute_error | 1.8733333333332671 |
| boundary_and_duration_errors.duration_sec.mean_signed_error | -0.3376811594202839 |
| boundary_and_duration_errors.duration_sec.median_signed_error | -0.4666666666665833 |
| boundary_tolerances.start.0.frames | 1 |
| boundary_tolerances.start.0.seconds | 0.03333333333333333 |
| boundary_tolerances.start.0.within_count | 4 |
| boundary_tolerances.start.0.matched_accuracy | 0.057971014492753624 |
| boundary_tolerances.start.0.all_gt_accuracy | 0.05333333333333334 |
| boundary_tolerances.start.1.frames | 3 |
| boundary_tolerances.start.1.seconds | 0.1 |
| boundary_tolerances.start.1.within_count | 6 |
| boundary_tolerances.start.1.matched_accuracy | 0.08695652173913043 |
| boundary_tolerances.start.1.all_gt_accuracy | 0.08 |
| boundary_tolerances.start.2.frames | 5 |
| boundary_tolerances.start.2.seconds | 0.16666666666666666 |
| boundary_tolerances.start.2.within_count | 10 |
| boundary_tolerances.start.2.matched_accuracy | 0.14492753623188406 |
| boundary_tolerances.start.2.all_gt_accuracy | 0.13333333333333333 |
| boundary_tolerances.start.3.frames | 10 |
| boundary_tolerances.start.3.seconds | 0.3333333333333333 |
| boundary_tolerances.start.3.within_count | 23 |
| boundary_tolerances.start.3.matched_accuracy | 0.3333333333333333 |
| boundary_tolerances.start.3.all_gt_accuracy | 0.30666666666666664 |
| boundary_tolerances.start.4.frames | 15 |
| boundary_tolerances.start.4.seconds | 0.5 |
| boundary_tolerances.start.4.within_count | 29 |
| boundary_tolerances.start.4.matched_accuracy | 0.42028985507246375 |
| boundary_tolerances.start.4.all_gt_accuracy | 0.38666666666666666 |
| boundary_tolerances.start.5.frames | 30 |
| boundary_tolerances.start.5.seconds | 1.0 |
| boundary_tolerances.start.5.within_count | 58 |
| boundary_tolerances.start.5.matched_accuracy | 0.8405797101449275 |
| boundary_tolerances.start.5.all_gt_accuracy | 0.7733333333333333 |
| boundary_tolerances.end.0.frames | 1 |
| boundary_tolerances.end.0.seconds | 0.03333333333333333 |
| boundary_tolerances.end.0.within_count | 11 |
| boundary_tolerances.end.0.matched_accuracy | 0.15942028985507245 |
| boundary_tolerances.end.0.all_gt_accuracy | 0.14666666666666667 |
| boundary_tolerances.end.1.frames | 3 |
| boundary_tolerances.end.1.seconds | 0.1 |
| boundary_tolerances.end.1.within_count | 16 |
| boundary_tolerances.end.1.matched_accuracy | 0.2318840579710145 |
| boundary_tolerances.end.1.all_gt_accuracy | 0.21333333333333335 |
| boundary_tolerances.end.2.frames | 5 |
| boundary_tolerances.end.2.seconds | 0.16666666666666666 |
| boundary_tolerances.end.2.within_count | 21 |
| boundary_tolerances.end.2.matched_accuracy | 0.30434782608695654 |
| boundary_tolerances.end.2.all_gt_accuracy | 0.28 |
| boundary_tolerances.end.3.frames | 10 |
| boundary_tolerances.end.3.seconds | 0.3333333333333333 |
| boundary_tolerances.end.3.within_count | 38 |
| boundary_tolerances.end.3.matched_accuracy | 0.5507246376811594 |
| boundary_tolerances.end.3.all_gt_accuracy | 0.5066666666666667 |
| boundary_tolerances.end.4.frames | 15 |
| boundary_tolerances.end.4.seconds | 0.5 |
| boundary_tolerances.end.4.within_count | 50 |
| boundary_tolerances.end.4.matched_accuracy | 0.7246376811594203 |
| boundary_tolerances.end.4.all_gt_accuracy | 0.6666666666666666 |
| boundary_tolerances.end.5.frames | 30 |
| boundary_tolerances.end.5.seconds | 1.0 |
| boundary_tolerances.end.5.within_count | 61 |
| boundary_tolerances.end.5.matched_accuracy | 0.8840579710144928 |
| boundary_tolerances.end.5.all_gt_accuracy | 0.8133333333333334 |


| Missed reference ID |
|---|
| 28 |
| 36 |
| 43 |
| 48 |
| 59 |
| 65 |


| False-detection prediction ID | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| 35 | 12174 | 12268 | 405.8 | 408.93333333333334 |
| 40 | 13462 | 13533 | 448.73333333333335 | 451.1 |
| 43 | 14131 | 14293 | 471.03333333333336 | 476.43333333333334 |
| 48 | 15681 | 16059 | 522.7 | 535.3 |
| 58 | 20114 | 20175 | 670.4666666666667 | 672.5 |
| 71 | 27349 | 27649 | 911.6333333333333 | 921.6333333333333 |

### Test2_Full_rally.csv

Reference role: legacy_generated_reference_agreement. Every original row and prediction match is preserved in [reference_row_comparisons.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/bound_reference_diagnostics/reference_row_comparisons.json).

| Aggregate metric | Value |
|---|---|
| detection.ground_truth_count | 73 |
| detection.predicted_count | 75 |
| detection.matched_count | 68 |
| detection.true_positives | 68 |
| detection.false_positives | 7 |
| detection.false_negatives | 5 |
| detection.precision | 0.9066666666666666 |
| detection.recall | 0.9315068493150684 |
| detection.f1 | 0.918918918918919 |
| overlap.mean_iou | 0.848134653705245 |
| overlap.median_iou | 0.8810851655700043 |
| overlap.minimum_iou | 0.5040871934604902 |
| overlap.percent_strictly_exceeding.0.5 | 100.0 |
| overlap.percent_strictly_exceeding.0.75 | 79.41176470588235 |
| overlap.percent_strictly_exceeding.0.9 | 45.588235294117645 |
| overlap.percent_strictly_exceeding.0.95 | 27.941176470588236 |
| boundary_and_duration_errors.start_frame.mae | 23.88235294117647 |
| boundary_and_duration_errors.start_frame.median_absolute_error | 11.5 |
| boundary_and_duration_errors.start_frame.rmse | 40.33098356467541 |
| boundary_and_duration_errors.start_frame.max_absolute_error | 167.0 |
| boundary_and_duration_errors.start_frame.p90_absolute_error | 73.0 |
| boundary_and_duration_errors.start_frame.mean_signed_error | 19.08823529411765 |
| boundary_and_duration_errors.start_frame.median_signed_error | 6.5 |
| boundary_and_duration_errors.end_frame.mae | 21.16176470588235 |
| boundary_and_duration_errors.end_frame.median_absolute_error | 10.5 |
| boundary_and_duration_errors.end_frame.rmse | 48.021900641024935 |
| boundary_and_duration_errors.end_frame.max_absolute_error | 343.0 |
| boundary_and_duration_errors.end_frame.p90_absolute_error | 45.400000000000034 |
| boundary_and_duration_errors.end_frame.mean_signed_error | -9.132352941176471 |
| boundary_and_duration_errors.end_frame.median_signed_error | -2.0 |
| boundary_and_duration_errors.start_time_sec.mae | 0.7960784313725436 |
| boundary_and_duration_errors.start_time_sec.median_absolute_error | 0.38333333333333997 |
| boundary_and_duration_errors.start_time_sec.rmse | 1.3443661188225053 |
| boundary_and_duration_errors.start_time_sec.max_absolute_error | 5.566666666666663 |
| boundary_and_duration_errors.start_time_sec.p90_absolute_error | 2.4333333333333145 |
| boundary_and_duration_errors.start_time_sec.mean_signed_error | 0.6362745098039249 |
| boundary_and_duration_errors.start_time_sec.median_signed_error | 0.21666666666668277 |
| boundary_and_duration_errors.end_time_sec.mae | 0.7053921568627398 |
| boundary_and_duration_errors.end_time_sec.median_absolute_error | 0.35000000000002274 |
| boundary_and_duration_errors.end_time_sec.rmse | 1.6007300213674873 |
| boundary_and_duration_errors.end_time_sec.max_absolute_error | 11.43333333333328 |
| boundary_and_duration_errors.end_time_sec.p90_absolute_error | 1.5133333333333565 |
| boundary_and_duration_errors.end_time_sec.mean_signed_error | -0.30441176470587833 |
| boundary_and_duration_errors.end_time_sec.median_signed_error | -0.06666666666660603 |
| boundary_and_duration_errors.duration_sec.mae | 1.3024509803921493 |
| boundary_and_duration_errors.duration_sec.median_absolute_error | 0.6333333333333471 |
| boundary_and_duration_errors.duration_sec.rmse | 2.259934494972931 |
| boundary_and_duration_errors.duration_sec.max_absolute_error | 12.699999999999932 |
| boundary_and_duration_errors.duration_sec.p90_absolute_error | 3.0099999999999554 |
| boundary_and_duration_errors.duration_sec.mean_signed_error | -0.9406862745098032 |
| boundary_and_duration_errors.duration_sec.median_signed_error | -0.33333333333337123 |
| boundary_tolerances.start.0.frames | 1 |
| boundary_tolerances.start.0.seconds | 0.03333333333333333 |
| boundary_tolerances.start.0.within_count | 10 |
| boundary_tolerances.start.0.matched_accuracy | 0.14705882352941177 |
| boundary_tolerances.start.0.all_gt_accuracy | 0.136986301369863 |
| boundary_tolerances.start.1.frames | 3 |
| boundary_tolerances.start.1.seconds | 0.1 |
| boundary_tolerances.start.1.within_count | 18 |
| boundary_tolerances.start.1.matched_accuracy | 0.2647058823529412 |
| boundary_tolerances.start.1.all_gt_accuracy | 0.2465753424657534 |
| boundary_tolerances.start.2.frames | 5 |
| boundary_tolerances.start.2.seconds | 0.16666666666666666 |
| boundary_tolerances.start.2.within_count | 24 |
| boundary_tolerances.start.2.matched_accuracy | 0.35294117647058826 |
| boundary_tolerances.start.2.all_gt_accuracy | 0.3287671232876712 |
| boundary_tolerances.start.3.frames | 10 |
| boundary_tolerances.start.3.seconds | 0.3333333333333333 |
| boundary_tolerances.start.3.within_count | 33 |
| boundary_tolerances.start.3.matched_accuracy | 0.4852941176470588 |
| boundary_tolerances.start.3.all_gt_accuracy | 0.4520547945205479 |
| boundary_tolerances.start.4.frames | 15 |
| boundary_tolerances.start.4.seconds | 0.5 |
| boundary_tolerances.start.4.within_count | 40 |
| boundary_tolerances.start.4.matched_accuracy | 0.5882352941176471 |
| boundary_tolerances.start.4.all_gt_accuracy | 0.547945205479452 |
| boundary_tolerances.start.5.frames | 30 |
| boundary_tolerances.start.5.seconds | 1.0 |
| boundary_tolerances.start.5.within_count | 52 |
| boundary_tolerances.start.5.matched_accuracy | 0.7647058823529411 |
| boundary_tolerances.start.5.all_gt_accuracy | 0.7123287671232876 |
| boundary_tolerances.end.0.frames | 1 |
| boundary_tolerances.end.0.seconds | 0.03333333333333333 |
| boundary_tolerances.end.0.within_count | 9 |
| boundary_tolerances.end.0.matched_accuracy | 0.1323529411764706 |
| boundary_tolerances.end.0.all_gt_accuracy | 0.1232876712328767 |
| boundary_tolerances.end.1.frames | 3 |
| boundary_tolerances.end.1.seconds | 0.1 |
| boundary_tolerances.end.1.within_count | 15 |
| boundary_tolerances.end.1.matched_accuracy | 0.22058823529411764 |
| boundary_tolerances.end.1.all_gt_accuracy | 0.2054794520547945 |
| boundary_tolerances.end.2.frames | 5 |
| boundary_tolerances.end.2.seconds | 0.16666666666666666 |
| boundary_tolerances.end.2.within_count | 24 |
| boundary_tolerances.end.2.matched_accuracy | 0.35294117647058826 |
| boundary_tolerances.end.2.all_gt_accuracy | 0.3287671232876712 |
| boundary_tolerances.end.3.frames | 10 |
| boundary_tolerances.end.3.seconds | 0.3333333333333333 |
| boundary_tolerances.end.3.within_count | 34 |
| boundary_tolerances.end.3.matched_accuracy | 0.5 |
| boundary_tolerances.end.3.all_gt_accuracy | 0.4657534246575342 |
| boundary_tolerances.end.4.frames | 15 |
| boundary_tolerances.end.4.seconds | 0.5 |
| boundary_tolerances.end.4.within_count | 42 |
| boundary_tolerances.end.4.matched_accuracy | 0.6176470588235294 |
| boundary_tolerances.end.4.all_gt_accuracy | 0.5753424657534246 |
| boundary_tolerances.end.5.frames | 30 |
| boundary_tolerances.end.5.seconds | 1.0 |
| boundary_tolerances.end.5.within_count | 56 |
| boundary_tolerances.end.5.matched_accuracy | 0.8235294117647058 |
| boundary_tolerances.end.5.all_gt_accuracy | 0.7671232876712328 |


| Missed reference ID |
|---|
| 31 |
| 39 |
| 56 |
| 58 |
| 63 |


| False-detection prediction ID | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| 11 | 3877 | 3936 | 129.23333333333332 | 131.2 |
| 32 | 11715 | 11751 | 390.5 | 391.7 |
| 40 | 13462 | 13533 | 448.73333333333335 | 451.1 |
| 41 | 13579 | 13718 | 452.6333333333333 | 457.26666666666665 |
| 47 | 15451 | 15609 | 515.0333333333333 | 520.3 |
| 58 | 20114 | 20175 | 670.4666666666667 | 672.5 |
| 71 | 27349 | 27649 | 911.6333333333333 | 921.6333333333333 |

### win_predictions.csv

Reference role: legacy_generated_reference_agreement. Every original row and prediction match is preserved in [reference_row_comparisons.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/bound_reference_diagnostics/reference_row_comparisons.json).

| Aggregate metric | Value |
|---|---|
| detection.ground_truth_count | 73 |
| detection.predicted_count | 75 |
| detection.matched_count | 68 |
| detection.true_positives | 68 |
| detection.false_positives | 7 |
| detection.false_negatives | 5 |
| detection.precision | 0.9066666666666666 |
| detection.recall | 0.9315068493150684 |
| detection.f1 | 0.918918918918919 |
| overlap.mean_iou | 0.848134653705245 |
| overlap.median_iou | 0.8810851655700043 |
| overlap.minimum_iou | 0.5040871934604902 |
| overlap.percent_strictly_exceeding.0.5 | 100.0 |
| overlap.percent_strictly_exceeding.0.75 | 79.41176470588235 |
| overlap.percent_strictly_exceeding.0.9 | 45.588235294117645 |
| overlap.percent_strictly_exceeding.0.95 | 27.941176470588236 |
| boundary_and_duration_errors.start_frame.mae | 23.88235294117647 |
| boundary_and_duration_errors.start_frame.median_absolute_error | 11.5 |
| boundary_and_duration_errors.start_frame.rmse | 40.33098356467541 |
| boundary_and_duration_errors.start_frame.max_absolute_error | 167.0 |
| boundary_and_duration_errors.start_frame.p90_absolute_error | 73.0 |
| boundary_and_duration_errors.start_frame.mean_signed_error | 19.08823529411765 |
| boundary_and_duration_errors.start_frame.median_signed_error | 6.5 |
| boundary_and_duration_errors.end_frame.mae | 21.16176470588235 |
| boundary_and_duration_errors.end_frame.median_absolute_error | 10.5 |
| boundary_and_duration_errors.end_frame.rmse | 48.021900641024935 |
| boundary_and_duration_errors.end_frame.max_absolute_error | 343.0 |
| boundary_and_duration_errors.end_frame.p90_absolute_error | 45.400000000000034 |
| boundary_and_duration_errors.end_frame.mean_signed_error | -9.132352941176471 |
| boundary_and_duration_errors.end_frame.median_signed_error | -2.0 |
| boundary_and_duration_errors.start_time_sec.mae | 0.7960784313725436 |
| boundary_and_duration_errors.start_time_sec.median_absolute_error | 0.38333333333333997 |
| boundary_and_duration_errors.start_time_sec.rmse | 1.3443661188225053 |
| boundary_and_duration_errors.start_time_sec.max_absolute_error | 5.566666666666663 |
| boundary_and_duration_errors.start_time_sec.p90_absolute_error | 2.4333333333333145 |
| boundary_and_duration_errors.start_time_sec.mean_signed_error | 0.6362745098039249 |
| boundary_and_duration_errors.start_time_sec.median_signed_error | 0.21666666666668277 |
| boundary_and_duration_errors.end_time_sec.mae | 0.7053921568627398 |
| boundary_and_duration_errors.end_time_sec.median_absolute_error | 0.35000000000002274 |
| boundary_and_duration_errors.end_time_sec.rmse | 1.6007300213674873 |
| boundary_and_duration_errors.end_time_sec.max_absolute_error | 11.43333333333328 |
| boundary_and_duration_errors.end_time_sec.p90_absolute_error | 1.5133333333333565 |
| boundary_and_duration_errors.end_time_sec.mean_signed_error | -0.30441176470587833 |
| boundary_and_duration_errors.end_time_sec.median_signed_error | -0.06666666666660603 |
| boundary_and_duration_errors.duration_sec.mae | 1.3024509803921493 |
| boundary_and_duration_errors.duration_sec.median_absolute_error | 0.6333333333333471 |
| boundary_and_duration_errors.duration_sec.rmse | 2.259934494972931 |
| boundary_and_duration_errors.duration_sec.max_absolute_error | 12.699999999999932 |
| boundary_and_duration_errors.duration_sec.p90_absolute_error | 3.0099999999999554 |
| boundary_and_duration_errors.duration_sec.mean_signed_error | -0.9406862745098032 |
| boundary_and_duration_errors.duration_sec.median_signed_error | -0.33333333333337123 |
| boundary_tolerances.start.0.frames | 1 |
| boundary_tolerances.start.0.seconds | 0.03333333333333333 |
| boundary_tolerances.start.0.within_count | 10 |
| boundary_tolerances.start.0.matched_accuracy | 0.14705882352941177 |
| boundary_tolerances.start.0.all_gt_accuracy | 0.136986301369863 |
| boundary_tolerances.start.1.frames | 3 |
| boundary_tolerances.start.1.seconds | 0.1 |
| boundary_tolerances.start.1.within_count | 18 |
| boundary_tolerances.start.1.matched_accuracy | 0.2647058823529412 |
| boundary_tolerances.start.1.all_gt_accuracy | 0.2465753424657534 |
| boundary_tolerances.start.2.frames | 5 |
| boundary_tolerances.start.2.seconds | 0.16666666666666666 |
| boundary_tolerances.start.2.within_count | 24 |
| boundary_tolerances.start.2.matched_accuracy | 0.35294117647058826 |
| boundary_tolerances.start.2.all_gt_accuracy | 0.3287671232876712 |
| boundary_tolerances.start.3.frames | 10 |
| boundary_tolerances.start.3.seconds | 0.3333333333333333 |
| boundary_tolerances.start.3.within_count | 33 |
| boundary_tolerances.start.3.matched_accuracy | 0.4852941176470588 |
| boundary_tolerances.start.3.all_gt_accuracy | 0.4520547945205479 |
| boundary_tolerances.start.4.frames | 15 |
| boundary_tolerances.start.4.seconds | 0.5 |
| boundary_tolerances.start.4.within_count | 40 |
| boundary_tolerances.start.4.matched_accuracy | 0.5882352941176471 |
| boundary_tolerances.start.4.all_gt_accuracy | 0.547945205479452 |
| boundary_tolerances.start.5.frames | 30 |
| boundary_tolerances.start.5.seconds | 1.0 |
| boundary_tolerances.start.5.within_count | 52 |
| boundary_tolerances.start.5.matched_accuracy | 0.7647058823529411 |
| boundary_tolerances.start.5.all_gt_accuracy | 0.7123287671232876 |
| boundary_tolerances.end.0.frames | 1 |
| boundary_tolerances.end.0.seconds | 0.03333333333333333 |
| boundary_tolerances.end.0.within_count | 9 |
| boundary_tolerances.end.0.matched_accuracy | 0.1323529411764706 |
| boundary_tolerances.end.0.all_gt_accuracy | 0.1232876712328767 |
| boundary_tolerances.end.1.frames | 3 |
| boundary_tolerances.end.1.seconds | 0.1 |
| boundary_tolerances.end.1.within_count | 15 |
| boundary_tolerances.end.1.matched_accuracy | 0.22058823529411764 |
| boundary_tolerances.end.1.all_gt_accuracy | 0.2054794520547945 |
| boundary_tolerances.end.2.frames | 5 |
| boundary_tolerances.end.2.seconds | 0.16666666666666666 |
| boundary_tolerances.end.2.within_count | 24 |
| boundary_tolerances.end.2.matched_accuracy | 0.35294117647058826 |
| boundary_tolerances.end.2.all_gt_accuracy | 0.3287671232876712 |
| boundary_tolerances.end.3.frames | 10 |
| boundary_tolerances.end.3.seconds | 0.3333333333333333 |
| boundary_tolerances.end.3.within_count | 34 |
| boundary_tolerances.end.3.matched_accuracy | 0.5 |
| boundary_tolerances.end.3.all_gt_accuracy | 0.4657534246575342 |
| boundary_tolerances.end.4.frames | 15 |
| boundary_tolerances.end.4.seconds | 0.5 |
| boundary_tolerances.end.4.within_count | 42 |
| boundary_tolerances.end.4.matched_accuracy | 0.6176470588235294 |
| boundary_tolerances.end.4.all_gt_accuracy | 0.5753424657534246 |
| boundary_tolerances.end.5.frames | 30 |
| boundary_tolerances.end.5.seconds | 1.0 |
| boundary_tolerances.end.5.within_count | 56 |
| boundary_tolerances.end.5.matched_accuracy | 0.8235294117647058 |
| boundary_tolerances.end.5.all_gt_accuracy | 0.7671232876712328 |


| Missed reference ID |
|---|
| 31 |
| 39 |
| 56 |
| 58 |
| 63 |


| False-detection prediction ID | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| 11 | 3877 | 3936 | 129.23333333333332 | 131.2 |
| 32 | 11715 | 11751 | 390.5 | 391.7 |
| 40 | 13462 | 13533 | 448.73333333333335 | 451.1 |
| 41 | 13579 | 13718 | 452.6333333333333 | 457.26666666666665 |
| 47 | 15451 | 15609 | 515.0333333333333 | 520.3 |
| 58 | 20114 | 20175 | 670.4666666666667 | 672.5 |
| 71 | 27349 | 27649 | 911.6333333333333 | 921.6333333333333 |

## Source-bound generated-point and court diagnostics

Anonymous point assignment compares geometry without inventing athlete identity or bounding-box IoU. A source/frame/coordinate review certificate gates distance metrics. These distances remain disagreement with legacy generated outputs. The identical shuttle exports are counted once; out-of-image values remain flagged and are not clipped.

| Diagnostic | Value |
|---|---|
| classification | legacy generated-output disagreement, NOT physical accuracy |
| frame_population | 29296 |
| legacy_player_slots_present | 57839 |
| current_player_rows | 58452 |
| shuttle_presence_cross_counts.legacy_shuttle_visible=False,current_raw_present=False | 4688 |
| shuttle_presence_cross_counts.legacy_shuttle_visible=True,current_raw_present=False | 4352 |
| shuttle_presence_cross_counts.legacy_shuttle_visible=True,current_raw_present=True | 20199 |
| shuttle_presence_cross_counts.legacy_shuttle_visible=False,current_raw_present=True | 57 |
| player_bottom_center_distance_px.count | 57305 |
| player_bottom_center_distance_px.mean | 3.4618022688218693 |
| player_bottom_center_distance_px.median | 1.5726106656020609 |
| player_bottom_center_distance_px.minimum | 0.001696952975397686 |
| player_bottom_center_distance_px.maximum | 429.41152875061556 |
| player_bottom_center_distance_px.p90 | 8.09668918606945 |
| player_bottom_center_distance_px.p95 | 11.764084543087986 |
| fresh_detector_bottom_center_distance_px.count | 24129 |
| fresh_detector_bottom_center_distance_px.mean | 1.6786299705400263 |
| fresh_detector_bottom_center_distance_px.median | 1.1176447249497874 |
| fresh_detector_bottom_center_distance_px.minimum | 0.019301976135856557 |
| fresh_detector_bottom_center_distance_px.maximum | 429.41152875061556 |
| fresh_detector_bottom_center_distance_px.p90 | 2.7309403253548084 |
| fresh_detector_bottom_center_distance_px.p95 | 4.366445007542395 |
| shuttle_raw_distance_px_both_present.count | 20199 |
| shuttle_raw_distance_px_both_present.mean | 5.991199644034486 |
| shuttle_raw_distance_px_both_present.median | 1.488654464489006 |
| shuttle_raw_distance_px_both_present.minimum | 0.015728282144981686 |
| shuttle_raw_distance_px_both_present.maximum | 729.122194879401 |
| shuttle_raw_distance_px_both_present.p90 | 2.7281737026457256 |
| shuttle_raw_distance_px_both_present.p95 | 3.5214482127785187 |
| unmatched_point_counts.all_current_rows_reference_points | 534 |
| unmatched_point_counts.all_current_rows_current_points | 1147 |
| unmatched_point_counts.fresh_detector_rows_reference_points | 33710 |
| unmatched_point_counts.fresh_detector_rows_current_points | 462 |
| reference_shuttle_out_of_image_count | 50 |
| out_of_image_policy | Retained and flagged, no clipping/exclusion; distances diagnose generated disagreement only |

Coordinate binding status: diagnostic_coordinate_binding_declared.

| Court diagnostic | Value |
|---|---|
| reference_frame | 300 |
| current_content_epoch | 0 |
| current_calibration_state | VALID |
| metric.classification | single-frame manual-reference diagnostic disagreement, not all-frame physical accuracy |
| metric.declared_corner_semantics | outer_singles_floor_corners |
| metric.corner_error_px.TL | 2.0934745563846318 |
| metric.corner_error_px.TR | 1.4017213579497438 |
| metric.corner_error_px.BR | 2.1950527161059017 |
| metric.corner_error_px.BL | 0.5118340439309265 |
| metric.mean_corner_error_px | 1.550520668592801 |
| metric.maximum_corner_error_px | 2.1950527161059017 |
| prerequisite | Source-bound explicit singles/doubles corner semantics and valid matching current calibration |

## Actual component execution and output coverage

| Stage | Evidence meaning | Observed count |
|---|---|---|
| ingestion | completed full canonical source | 29296 |
| court calibration | calibration events; validity separately recorded | 1 |
| player detection | recorded detector execution frames | 12315 |
| player tracking | stored person rows; physical identity accuracy unavailable | 58452 |
| pose | pose rows with current-frame source stamps | 46816 |
| shuttle | raw decoded observations, before temporal association | 20256 |
| racket | racket rows with current-frame source stamps | 20568 |
| contact | emitted events; zero emissions do not prove stage did not execute | 819 |
| stroke | emitted classifications; unknown/attribution counts separate | 819 |
| rally | live exported rally-end events | 75 |
| outcome | known-winner rally outputs; unverified identities remain unknown | 0 |
| scoring | canonical accepted point events, not raw OCR readings | 0 |
| broadcast OCR | observations, not accepted outcomes or labelled accuracy | 708 |
| player analytics | named-player analytics exports | 0 |
| highlights | canonical heuristic selections, relevance unvalidated | 12 |
| heatmaps | export metadata available | 0 |


| Cache coverage metric | Value |
|---|---|
| counts.frames | 29296 |
| counts.raw_shuttle_present | 20256 |
| counts.detector_executed_frames | 12315 |
| counts.person_rows | 58452 |
| counts.scene_telemetry_present | 3633 |
| counts.scene_raw_hypotheses | 38 |
| counts.actual_content_epoch_increments | 36 |
| counts.content_epoch_decreases | 0 |
| counts.detailed_diagnostic_frames | 3600 |
| counts.person_current_detector_matches | 24591 |
| counts.person_propagated_or_unmatched | 33861 |
| counts.pose_present_rows | 46816 |
| counts.pose_current_source_rows | 46816 |
| counts.pose_present_without_current_source | 0 |
| counts.pose_current_on_propagated_box | 22227 |
| counts.racket_present_rows | 20568 |
| counts.racket_current_source_rows | 20568 |
| counts.racket_present_without_current_source | 0 |
| counts.racket_current_on_propagated_box | 0 |
| counts.scene_decision_records | 38 |
| counts.scene_positive_correspondence_vetoes | 2 |
| counts.scene_current_detector_probes | 38 |
| categories.view.main | 29227 |
| categories.view.none | 69 |
| categories.calibration_state.REACQUIRING | 22 |
| categories.calibration_state.VALID | 29205 |
| categories.calibration_state.LOST | 69 |
| categories.player_population.0 | 194 |
| categories.player_population.2 | 27842 |
| categories.player_population.1 | 506 |
| categories.player_population.3 | 754 |
| categories.association_status.missing | 8971 |
| categories.association_status.observed | 20227 |
| categories.association_status.invalid | 69 |
| categories.association_status.ambiguous | 29 |
| categories.association_reason.no_accepted_raw_observation | 8971 |
| categories.association_reason.fresh_selection_retained | 20227 |
| categories.association_reason.image_view_invalid | 69 |
| categories.association_reason.coobserved_competing_static_hypothesis | 29 |
| categories.scene_raw_status.unknown | 162 |
| categories.scene_raw_status.measured | 3433 |
| categories.scene_raw_status.hypothesis | 38 |
| categories.person_detector_match.True | 24591 |
| categories.person_detector_match.False | 33861 |
| categories.person_identity_method.bytetrack_v1 | 58452 |
| categories.scene_decision.barrier | 36 |
| categories.scene_decision.no_barrier | 2 |
| categories.scene_decision_reason.raw_change_and_current_layout_discontinuity | 36 |
| categories.scene_decision_reason.complete_current_layout_correspondence | 2 |
| limits.0 | Counts are technical coverage, not reviewed component accuracy. |
| limits.1 | Raw shuttle is pre-association decoder output that already passed court masking. |
| limits.2 | Current pose execution and current box/person association are separate. |
| limits.3 | Content epochs measure actual tracking action; raw hypotheses remain separate. |

## Contact, stroke, identity, outcome and scoring

| Metric | Value |
|---|---|
| event_coverage.append_only_counts.calibration | 1 |
| event_coverage.append_only_counts.activity_interval | 167 |
| event_coverage.append_only_counts.scene | 3 |
| event_coverage.append_only_counts.participant_observation | 298 |
| event_coverage.append_only_counts.rally_start | 149 |
| event_coverage.append_only_counts.contact | 1746 |
| event_coverage.append_only_counts.stroke | 847 |
| event_coverage.append_only_counts.rally_end | 75 |
| event_coverage.append_only_counts.format_decision | 1 |
| event_coverage.append_only_counts.shuttle_turn | 58 |
| event_coverage.append_only_counts.broadcast_score | 708 |
| event_coverage.append_only_counts.match_phase | 1 |
| event_coverage.append_only_counts.highlight | 6 |
| event_coverage.append_only_counts.identity_ambiguity | 48 |
| event_coverage.live_counts.calibration | 1 |
| event_coverage.live_counts.activity_interval | 167 |
| event_coverage.live_counts.scene | 3 |
| event_coverage.live_counts.participant_observation | 298 |
| event_coverage.live_counts.rally_start | 75 |
| event_coverage.live_counts.stroke | 819 |
| event_coverage.live_counts.contact | 819 |
| event_coverage.live_counts.rally_end | 75 |
| event_coverage.live_counts.format_decision | 1 |
| event_coverage.live_counts.shuttle_turn | 58 |
| event_coverage.live_counts.broadcast_score | 708 |
| event_coverage.live_counts.match_phase | 1 |
| event_coverage.live_counts.highlight | 6 |
| event_coverage.live_counts.identity_ambiguity | 48 |
| event_coverage.categories.event_status.confirmed | 2600 |
| event_coverage.categories.event_status.provisional | 479 |
| event_coverage.categories.stroke_actor.unknown | 819 |
| event_coverage.categories.stroke_physical_event_status.insufficient | 427 |
| event_coverage.categories.stroke_physical_event_status.probable | 109 |
| event_coverage.categories.stroke_physical_event_status.ambiguous | 283 |
| event_coverage.categories.stroke_contact_status.estimated | 819 |
| event_coverage.categories.stroke_classification_status.unknown | 587 |
| event_coverage.categories.stroke_classification_status.estimated | 232 |
| event_coverage.categories.stroke_stroke.unknown | 587 |
| event_coverage.categories.stroke_stroke.push | 105 |
| event_coverage.categories.stroke_stroke.clear | 16 |
| event_coverage.categories.stroke_stroke.drop | 51 |
| event_coverage.categories.stroke_stroke.lift | 22 |
| event_coverage.categories.stroke_stroke.net_shot | 26 |
| event_coverage.categories.stroke_stroke.smash | 1 |
| event_coverage.categories.stroke_stroke.drive | 11 |
| event_coverage.categories.stroke_attribution_reason.nearest_proximity | 815 |
| event_coverage.categories.stroke_attribution_reason.ambiguous_proximity | 4 |
| event_coverage.categories.stroke_classification_abstention_reason.missing_required_evidence | 579 |
| event_coverage.categories.stroke_classification_abstention_reason.unresolved_initial_contact | 8 |
| event_coverage.categories.contact_actor.unknown | 819 |
| event_coverage.categories.contact_physical_event_status.insufficient | 427 |
| event_coverage.categories.contact_physical_event_status.probable | 109 |
| event_coverage.categories.contact_physical_event_status.ambiguous | 283 |
| event_coverage.categories.contact_contact_status.estimated | 819 |
| event_coverage.categories.contact_attribution_reason.nearest_proximity | 815 |
| event_coverage.categories.contact_attribution_reason.ambiguous_proximity | 4 |
| event_coverage.categories.contact_trajectory_reliability.probable | 435 |
| event_coverage.categories.contact_trajectory_reliability.insufficient | 222 |
| event_coverage.categories.contact_trajectory_reliability.ambiguous | 162 |
| event_coverage.categories.contact_trajectory_reasons.supported_turn | 330 |
| event_coverage.categories.contact_trajectory_reasons.coherent_motion_change_unavailable | 222 |
| event_coverage.categories.contact_trajectory_reasons.supported_launch | 105 |
| event_coverage.categories.contact_trajectory_reasons.association_unresolved | 162 |
| event_coverage.categories.contact_impact_reliability.insufficient | 427 |
| event_coverage.categories.contact_impact_reliability.probable | 109 |
| event_coverage.categories.contact_impact_reliability.ambiguous | 283 |
| event_coverage.categories.contact_impact_reasons.fresh_player_observation_unavailable | 427 |
| event_coverage.categories.contact_impact_reasons.coherent_motion_and_fresh_contact_cue | 109 |
| event_coverage.categories.contact_impact_reasons.association_unresolved | 162 |
| event_coverage.categories.contact_impact_reasons.coherent_motion_change_unavailable | 76 |
| event_coverage.categories.contact_impact_reasons.no_fresh_swing_or_racket_overlap | 45 |
| event_coverage.categories.contact_attribution_reliability.insufficient | 528 |
| event_coverage.categories.contact_attribution_reliability.probable | 291 |
| event_coverage.categories.contact_attribution_reasons.fresh_player_observation_unavailable | 528 |
| event_coverage.categories.contact_attribution_reasons.geometric_attribution_not_verified_identity | 291 |
| event_coverage.categories.rally_end_reason.stationary | 40 |
| event_coverage.categories.rally_end_reason.gap | 30 |
| event_coverage.categories.rally_end_reason.cut | 5 |
| event_coverage.categories.rally_phase.unknown | 2 |
| event_coverage.categories.rally_phase.match_play | 73 |
| event_coverage.categories.rally_official.False | 28 |
| event_coverage.categories.rally_official.True | 47 |
| event_coverage.categories.rally_match_format_known.False | 1 |
| event_coverage.categories.rally_match_format_known.True | 74 |
| event_coverage.categories.rally_match_format.unknown | 1 |
| event_coverage.categories.rally_match_format.singles | 74 |
| event_coverage.categories.rally_winner.None | 75 |
| event_coverage.categories.rally_score_transition_status.match_format_unknown | 1 |
| event_coverage.categories.rally_score_transition_status.unavailable | 47 |
| event_coverage.categories.rally_score_transition_status.candidate | 27 |
| event_coverage.categories.rally_admission_reason.duration_policy | 73 |
| event_coverage.categories.rally_admission_reason.independent_contact_and_observed_motion_witnesses | 2 |
| event_coverage.physical_accuracy_validated | False |
| outcome_and_stroke_coverage.predicted_rallies | 75 |
| outcome_and_stroke_coverage.known_winner_outputs | 0 |
| outcome_and_stroke_coverage.unknown_winner_outputs | 75 |
| outcome_and_stroke_coverage.stroke_label_counts.unknown | 587 |
| outcome_and_stroke_coverage.stroke_label_counts.push | 105 |
| outcome_and_stroke_coverage.stroke_label_counts.clear | 16 |
| outcome_and_stroke_coverage.stroke_label_counts.drop | 51 |
| outcome_and_stroke_coverage.stroke_label_counts.lift | 22 |
| outcome_and_stroke_coverage.stroke_label_counts.net_shot | 26 |
| outcome_and_stroke_coverage.stroke_label_counts.smash | 1 |
| outcome_and_stroke_coverage.stroke_label_counts.drive | 11 |
| outcome_and_stroke_coverage.winner_comparison_status | unavailable_without_verified_identity_and_adjudicated_outcomes |
| track_coverage.counts.camera_rows | 29296 |
| track_coverage.counts.player_rows | 58440 |
| track_coverage.counts.nonfinite_projected_court_rows | 0 |
| track_coverage.counts.player_projected_court_rows | 56597 |
| track_coverage.counts.projected_court_on_propagated_box | 32805 |
| track_coverage.counts.racket_rows | 20559 |
| track_coverage.counts.shuttle_rows | 29296 |
| track_coverage.categories.player_id.None | 58440 |
| track_coverage.categories.detector_matched.True | 24579 |
| track_coverage.categories.detector_matched.False | 33861 |
| track_coverage.invalid_geometry_frame_count | 91 |
| track_coverage.limit | Anonymous projected positions and detector flags are evidence coverage, not physical identity or metric accuracy. |

Named identities, anonymous tracks, raw broadcast OCR observations and canonical accepted points are distinct. Unknown outcomes are not assigned winners; an empty accepted score sequence is not verified 0–0.

## Downstream analytics, heatmaps and highlights

| Output | Value |
|---|---|
| rallies_official | 47 |
| rallies_unofficial | 28 |
| active_play_s | 459.1 |
| unofficial_play_s | 206.7 |
| shot_accounting.total | 553 |
| shot_accounting.attributed | 0 |
| shot_accounting.unattributed | 553 |
| avg_rally_shots | 11.77 |
| longest_rally_shots | 35 |
| named_player_analytics_count | 0 |
| momentum_entries | 0 |
| score_timeline_entries | 0 |
| individual_available | False |
| individual_match_format | unavailable |
| individual_participants | 0 |
| individual_teams | 0 |
| individual_accounting.total_shots | 553 |
| individual_accounting.attributed_shots | 0 |
| individual_accounting.unattributed_shots | 553 |
| individual_unattributed_event_count | 553 |
| estimated_individual_available | False |
| highlight_count | 12 |
| highlight_check_count | 12 |
| highlight_clips_rendered | False |
| highlight_relevance_accuracy | unavailable |
| heatmap_accuracy | unavailable |
| heatmap_export_available | True |
| heatmap_grid_count | 0 |
| heatmap_limitation | No independently reviewed spatial-density labels; anonymous motion is not named-player ground truth |
| outcome_record_count | 75 |
| outcome_records_with_score_available | 0 |
| estimated_scopes.official.accounting.total_linked_shots | 553 |
| estimated_scopes.official.accounting.estimated_shots | 0 |
| estimated_scopes.official.accounting.unresolved_shots | 553 |
| estimated_scopes.official.accounting.verified_shots | 0 |
| estimated_scopes.official.participant_count | 0 |
| estimated_scopes.official.unresolved_event_count | 553 |
| estimated_scopes.official.unresolved_reason_counts.no_unique_provisional_track_hypothesis | 357 |
| estimated_scopes.official.unresolved_reason_counts.no_prior_reviewed_seed | 196 |
| estimated_scopes.official.anonymous_episode_count | 70 |
| estimated_scopes.official.detector_run_counts.ran | 196 |
| estimated_scopes.official.detector_run_counts.not_run | 0 |
| estimated_scopes.official.detector_run_counts.unknown | 0 |
| estimated_scopes.all_linked.accounting.total_linked_shots | 819 |
| estimated_scopes.all_linked.accounting.estimated_shots | 0 |
| estimated_scopes.all_linked.accounting.unresolved_shots | 819 |
| estimated_scopes.all_linked.participant_count | 0 |
| estimated_scopes.all_linked.unresolved_event_count | 819 |
| estimated_scopes.all_linked.unresolved_reason_counts.no_unique_provisional_track_hypothesis | 528 |
| estimated_scopes.all_linked.unresolved_reason_counts.no_prior_reviewed_seed | 291 |
| estimated_scopes.all_linked.anonymous_episode_count | 108 |
| estimated_scopes.all_linked.detector_run_counts.ran | 291 |
| estimated_scopes.all_linked.detector_run_counts.not_run | 0 |
| estimated_scopes.all_linked.detector_run_counts.unknown | 0 |
| heatmaps.schema | canonical-test2-heatmap-export:v1 |
| heatmaps.status | completed |
| heatmaps.test | 2 |
| heatmaps.session_id | UPLOADTEST2 |
| heatmaps.source_sha256 | 4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a |
| heatmaps.grid_count | 0 |
| heatmaps.available | False |
| heatmaps.canonical_named_player_count | 0 |
| heatmaps.official_rally_count | 47 |
| heatmaps.unofficial_rally_count | 28 |
| heatmaps.live_stroke_events | 819 |
| heatmaps.unattributed_live_stroke_events | 819 |
| heatmaps.stroke_actor_counts.unknown | 819 |
| heatmaps.no_grid_reasons.entry_count | 1 |
| heatmaps.policy.phase | Production build admits stroke statistics and presence paths only from official rallies |
| heatmaps.policy.identity | Named canonical actors/player_id required; anonymous detection slots are not renamed players |
| heatmaps.policy.geometry | Production camera validity, court-quality, visibility, confidence, continuity and finite-coordinate gates unchanged |
| heatmaps.policy.kinds | presence, movement, origin, targeting and supported trajectory/human landing; only actually present grids exported |
| heatmaps.policy.normalization | Exact production HeatmapSet.to_public default normalization; total retains raw grid mass |
| heatmaps.policy.missing | No default zero grids manufactured for missing players or kinds |
| heatmaps.physical_accuracy | unavailable |
| heatmaps.independent_spatial_ground_truth_available | False |
| heatmaps.inference_performed | False |
| heatmaps.pipeline_changes | False |

Canonical exports are linked below. Anonymous episode profiles and heuristic highlights remain diagnostic estimates. A missing heatmap export or identity-supported player output is recorded explicitly rather than counted as accurate.

## Runtime, resources, models and configuration

| Resource/stage metric | Value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 3983955 |
| parent_failure_inclusive_elapsed_s | unavailable |
| parent_failure_inclusive_source_fps | unavailable |
| neural_only_throughput_fps | unavailable |
| model_loading_time_s | unavailable |
| media_ready_time_s | 2.3215769147500396 |
| model_staging_time_s | 1.7377009382471442 |
| worker_final_cpu_s | 38419.118835999994 |
| worker_maxrss_bytes | 3133997056 |
| sampled_worker_tree_peak_rss_bytes | 3097358336 |
| sampled_worker_gpu_peak_mib | 2124 |
| sampled_cpu_seconds_max_observed | 38418.56 |
| sampled_cpu_seconds_last_observed | 38418.56 |
| sampled_system_available_ram_min_bytes | 95199424512 |
| sample_count | 1673 |
| resource_rows | 1673 |
| sampling_error_count | 0 |
| stage_latency.court.calls | 489 |
| stage_latency.court.seconds | 156.59145409194753 |
| stage_latency.court.p50_ms | 311.4873911254108 |
| stage_latency.court.p95_ms | 385.3482705540955 |
| stage_latency.court.min_ms | 89.18674429878592 |
| stage_latency.court.max_ms | 822.5697227753699 |
| stage_latency.court.scope | existing pipeline stage invocation; scopes may overlap |
| stage_latency.court.frame_population_sum | 29296 |
| stage_latency.content_continuity_and_players.calls | 489 |
| stage_latency.content_continuity_and_players.seconds | 1447.5912264287472 |
| stage_latency.content_continuity_and_players.p50_ms | 3327.7024468407035 |
| stage_latency.content_continuity_and_players.p95_ms | 3665.617719199508 |
| stage_latency.content_continuity_and_players.min_ms | 848.695449065417 |
| stage_latency.content_continuity_and_players.max_ms | 4365.661193151027 |
| stage_latency.content_continuity_and_players.scope | existing pipeline stage invocation; scopes may overlap |
| stage_latency.content_continuity_and_players.frame_population_sum | 29296 |
| stage_latency.shuttle.calls | 489 |
| stage_latency.shuttle.seconds | 438.30177550949156 |
| stage_latency.shuttle.p50_ms | 868.4488451108336 |
| stage_latency.shuttle.p95_ms | 1108.2750102505088 |
| stage_latency.shuttle.min_ms | 230.605143122375 |
| stage_latency.shuttle.max_ms | 1580.3097351454198 |
| stage_latency.shuttle.scope | existing pipeline stage invocation; scopes may overlap |
| stage_latency.shuttle.frame_population_sum | 29296 |
| stage_latency.players.calls | 489 |
| stage_latency.players.seconds | 127.57976488769054 |
| stage_latency.players.p50_ms | 243.71276888996363 |
| stage_latency.players.p95_ms | 525.0467304140329 |
| stage_latency.players.min_ms | 4.764311946928501 |
| stage_latency.players.max_ms | 922.2834818065166 |
| stage_latency.players.scope | existing pipeline stage invocation; scopes may overlap |
| stage_latency.players.frame_population_sum | 29296 |
| stage_latency.ocr.calls | 489 |
| stage_latency.ocr.seconds | 509.88396056368947 |
| stage_latency.ocr.p50_ms | 991.3333249278367 |
| stage_latency.ocr.p95_ms | 1600.0267465598881 |
| stage_latency.ocr.min_ms | 527.5942832231522 |
| stage_latency.ocr.max_ms | 1969.2478757351637 |
| stage_latency.ocr.scope | existing pipeline stage invocation; scopes may overlap |
| stage_latency.ocr.frame_population_sum | 29296 |
| limits.0 | Normal completed worker/parent timing scopes remain separate; they include initialization/media/postprocessing. |
| limits.1 | Component initialization includes model construction and is not isolated model-loading latency. |
| limits.2 | Pure neural-only throughput remains unavailable; saved stage wall scopes can overlap. |
| limits.3 | GPU peaks use the allocated GPU UUID and worker PID only; sampling can miss short peaks. |
| limits.4 | Tree RSS may double-count shared pages; CPU snapshots omit exited children and are not final worker CPU usage. |
| limits.5 | Other workers may share host CPU/RAM/storage; establish actual overlap from parent start/end times and PID receipts before comparing performance. |
| parent_completed_elapsed_s | 3463.2286817640997 |
| parent_completed_source_fps | 8.459158401598014 |
| worker_elapsed_s | 3453.0654241819866 |
| worker_source_fps | 8.484055875350254 |
| component_initialization_including_models_s | 8.59035194804892 |
| visible_torch_devices.0.logical_index | 0 |
| visible_torch_devices.0.name | NVIDIA GeForce GTX 1080 Ti |
| visible_torch_devices.0.uuid | a618f090-66bf-ad80-b0a5-0c91bee61fab |
| runner_stage_seconds.component_initialization_including_models_s | 8.59035194804892 |
| runner_stage_seconds.decode_perception_cache_s | 2872.4381433576345 |


| Model/backend/configuration | Value |
|---|---|
| execution_backends.shuttle.requested_backend | torch-cuda |
| execution_backends.shuttle.actual_backend | torch-cuda |
| execution_backends.shuttle.device | cuda:0 |
| execution_backends.shuttle.dtype | torch.float16 |
| execution_backends.shuttle.backend_fallback | False |
| execution_backends.shuttle.requested_precision | fp16 |
| execution_backends.shuttle.checkpoint_sha256 | df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a |
| execution_backends.shuttle_association.backend | numpy-cpu |
| execution_backends.shuttle_association.weights | unavailable |
| execution_backends.content_continuity.backend | opencv-cpu |
| execution_backends.content_continuity.weights | unavailable |
| execution_backends.content_continuity.input_dtype | uint8 |
| execution_backends.content_continuity.mode | barrier_detector_layout_v2 |
| execution_backends.content_continuity.barrier_enabled | True |
| execution_backends.content_continuity.evidence_schema | foreground-scene-hypothesis:v2 |
| execution_backends.content_continuity.score_semantics | uncalibrated_pixel_and_ratio_evidence |
| execution_backends.player_detector.requested_backend | onnx-cuda |
| execution_backends.player_detector.providers.0 | CUDAExecutionProvider |
| execution_backends.player_detector.providers.1 | CPUExecutionProvider |
| execution_backends.player_detector.actual_backend | onnx-cuda |
| execution_backends.player_detector.backend_fallback | False |
| execution_backends.pose.requested_backend | onnx-cuda |
| execution_backends.pose.providers.0 | CUDAExecutionProvider |
| execution_backends.pose.providers.1 | CPUExecutionProvider |
| execution_backends.pose.actual_backend | onnx-cuda |
| execution_backends.pose.backend_fallback | False |
| execution_backends.ocr.package_version | 3.10.0 |
| execution_backends.ocr.requested_backend | onnx-cpu |
| execution_backends.ocr.parser_policy | nearest-name-current-column-v2 |
| execution_backends.ocr.requested_num_threads | unavailable |
| execution_backends.ocr.stages.det.model_file | PP-OCRv6_det_small.onnx |
| execution_backends.ocr.stages.det.sha256 | 090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f |
| execution_backends.ocr.stages.det.configured_ocr_version | PP-OCRv6 |
| execution_backends.ocr.stages.det.providers.0 | CPUExecutionProvider |
| execution_backends.ocr.stages.det.session_options.intra_op_num_threads | 0 |
| execution_backends.ocr.stages.det.session_options.inter_op_num_threads | 0 |
| execution_backends.ocr.stages.cls.model_file | ch_ppocr_mobile_v2.0_cls_mobile.onnx |
| execution_backends.ocr.stages.cls.sha256 | e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c |
| execution_backends.ocr.stages.cls.configured_ocr_version | PP-OCRv4 |
| execution_backends.ocr.stages.cls.providers.0 | CPUExecutionProvider |
| execution_backends.ocr.stages.cls.session_options.intra_op_num_threads | 0 |
| execution_backends.ocr.stages.cls.session_options.inter_op_num_threads | 0 |
| execution_backends.ocr.stages.rec.model_file | PP-OCRv6_rec_small.onnx |
| execution_backends.ocr.stages.rec.sha256 | 6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884 |
| execution_backends.ocr.stages.rec.configured_ocr_version | PP-OCRv6 |
| execution_backends.ocr.stages.rec.providers.0 | CPUExecutionProvider |
| execution_backends.ocr.stages.rec.session_options.intra_op_num_threads | 0 |
| execution_backends.ocr.stages.rec.session_options.inter_op_num_threads | 0 |
| execution_backends.ocr.backend_fallback | False |
| execution_backends.racket.requested_backend | opencv-cpu |
| execution_backends.racket.actual_backend | opencv-cpu |
| execution_backends.racket.backend_fallback | False |
| execution_backends.racket.method | opencv_ellipse_shaft_v1 |
| models_verified.registry_artifacts.osnet_ain_x0_25.status | unavailable_not_claimed_loaded |
| models_verified.registry_artifacts.racketvision_balltrack.status | unavailable_not_claimed_loaded |
| models_verified.registry_artifacts.rfdetr_small.sha256 | fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e |
| models_verified.registry_artifacts.rfdetr_small.source_path | /home/administrator/Desktop/sport-analytics/Sports_Analytics/models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx |
| models_verified.registry_artifacts.rfdetr_small.staged_path | /home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run/models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx |
| models_verified.registry_artifacts.rtmpose_m_body7.sha256 | f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741 |
| models_verified.registry_artifacts.rtmpose_m_body7.source_path | /home/administrator/Desktop/sport-analytics/Sports_Analytics/models/cache/rtmpose_m_body7/rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504.zip |
| models_verified.registry_artifacts.rtmpose_m_body7.staged_path | /home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run/models/cache/rtmpose_m_body7/rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504.zip |
| models_verified.registry_artifacts.tracknetv3.sha256 | df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a |
| models_verified.registry_artifacts.tracknetv3.source_path | /home/administrator/Desktop/sport-analytics/Sports_Analytics/models/cache/tracknetv3/TrackNet_best.pt |
| models_verified.registry_artifacts.tracknetv3.staged_path | /home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run/models/cache/tracknetv3/TrackNet_best.pt |
| models_verified.package_ocr_artifacts.det.path | /home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/lib/python3.12/site-packages/rapidocr/models/PP-OCRv6_det_small.onnx |
| models_verified.package_ocr_artifacts.det.sha256 | 090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f |
| models_verified.package_ocr_artifacts.cls.path | /home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/lib/python3.12/site-packages/rapidocr/models/ch_ppocr_mobile_v2.0_cls_mobile.onnx |
| models_verified.package_ocr_artifacts.cls.sha256 | e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c |
| models_verified.package_ocr_artifacts.rec.path | /home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/lib/python3.12/site-packages/rapidocr/models/PP-OCRv6_rec_small.onnx |
| models_verified.package_ocr_artifacts.rec.sha256 | 6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884 |
| selected_components.stroke.model | none |
| selected_components.stroke.implementation | stroke-rules-v0 |
| selected_components.stroke.backend | none |
| selected_components.stroke.precision | fp32 |
| selected_components.stroke.batch | 1 |
| selected_components.stroke.input_size | unavailable |
| selected_components.rally.model | none |
| selected_components.rally.implementation | rally-evidence-tracklets-v1 |
| selected_components.rally.backend | none |
| selected_components.rally.precision | fp32 |
| selected_components.rally.batch | 1 |
| selected_components.rally.input_size | unavailable |
| selected_components.rally.params.use_reconstruction | False |
| selected_components.rally.params.motion_guard | False |
| selected_components.rally.params.use_exit_recovery | True |
| selected_components.rally.params.use_curve_exit | False |
| selected_components.rally.params.use_short_exchange_evidence | True |
| selected_components.rally.params.use_terminal_contact_evidence | False |
| selected_components.shuttle_association.model | none |
| selected_components.shuttle_association.implementation | coobserved-static-hypotheses-v1 |
| selected_components.shuttle_association.backend | none |
| selected_components.shuttle_association.precision | fp32 |
| selected_components.shuttle_association.batch | 1 |
| selected_components.shuttle_association.input_size | unavailable |
| selected_components.contact.model | none |
| selected_components.contact.implementation | contact-evidence-v1 |
| selected_components.contact.backend | none |
| selected_components.contact.precision | fp32 |
| selected_components.contact.batch | 1 |
| selected_components.contact.input_size | unavailable |
| selected_components.contact.params.spatial_sigma_px | 0.7216878364870323 |
| selected_components.content_continuity.model | none |
| selected_components.content_continuity.implementation | foreground-content-continuity-v2 |
| selected_components.content_continuity.backend | none |
| selected_components.content_continuity.precision | fp32 |
| selected_components.content_continuity.batch | 1 |
| selected_components.content_continuity.input_size | unavailable |
| selected_components.content_continuity.params.mode | barrier_detector_layout_v2 |


| Degraded component evidence | Value |
|---|---|
| .0.stage | player_identity |
| .0.reason | osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25` |
| .1.stage | player_reid |
| .1.reason | baseline player_reid provider is unavailable |

GPU peaks are sampled for the allocated worker/PID; CPU/RSS scopes and stage scopes may overlap. Worker throughput includes preparation, loading and postprocessing. Pure neural-only throughput remains unavailable.

## Unavailable accuracy metrics

| Metric | Status | Missing prerequisite |
|---|---|---|
| player_AP_mAP_IoU | unavailable | Independently reviewed boxes and complete positive/negative coverage; supplied generated points are not boxes. |
| tracking_IDF1_HOTA_ID_switches_fragmentation | unavailable | Reviewed persistent athlete identities, boxes and visibility; two generated detection slots are not persistent IDs. |
| pose_PCK_OKS | unavailable | Reviewed keypoints and joint visibility, skeleton convention and scale. |
| shuttle_physical_localization_PR | unavailable | Independent reviewed coordinates/visibility; filled model estimates do not identify interpolated frames. |
| racket_contact_PR_F1_temporal_error | unavailable | Reviewed contact/racket times and negative windows, not rally-level labels. |
| stroke_per_class_PR_F1_confusion | unavailable | Complete per-contact stroke taxonomy and labels; a single ball_types field per coarse rally is insufficient. |
| winner_outcome_accuracy_PR_F1_confusion | unavailable | Verified symbolic Player A/B identity and source-bound adjudicated outcomes; win_predictions is generated. |
| score_sequence_accuracy | unavailable | Reviewed broadcast identity, point alignment and score sequence, accounting for edited-video omissions. |
| highlight_quality | unavailable | Reviewed highlight relevance/boundaries; rally overlap and execution are not relevance accuracy. |
| player_analytics_accuracy | unavailable | Reviewed participant identities and metric-specific physical movement/event labels. |

## Source-synchronized failure evidence

Cases originate from reference disagreement and diagnostic thresholds. Their presence does not itself establish a pipeline defect. Causal classifications require synchronized source review; annotations and generated references can also be wrong.

| Case | Reference ID | Prediction ID | Status | Reference start | Prediction start | Reference end | Prediction end | Diagnosis |
|---|---|---|---|---|---|---|---|---|
| gt_005 | 5 | 5 | matched | 1955 | 2040 | 2410 | 2404 | unreviewed |
| gt_006 | 6 | 6 | matched | 2477 | 2492 | 2621 | 2655 | unreviewed |
| gt_007 | 7 | 7 | matched | 2811 | 2790 | 2870 | 2866 | unreviewed |
| gt_008 | 8 | 8 | matched | 2927 | 2946 | 3157 | 3099 | unreviewed |
| gt_011 | 11 | 12 | matched | 3863 | 4030 | 4215 | 4230 | unreviewed |
| gt_014 | 14 | 15 | matched | 4854 | 4882 | 5185 | 5131 | unreviewed |
| gt_024 | 24 | 25 | matched | 8593 | 8627 | 8748 | 8734 | unreviewed |
| gt_030 | 30 | 31 | matched | 11394 | 11353 | 11661 | 11657 | unreviewed |
| gt_031 | 31 | unavailable | missed | 11714 | unavailable | 11830 | unavailable | unreviewed |
| gt_032 | 32 | 33 | matched | 11860 | 11873 | 11942 | 11926 | unreviewed |
| gt_034 | 34 | 35 | matched | 12173 | 12174 | 12230 | 12268 | unreviewed |
| gt_035 | 35 | 36 | matched | 12268 | 12310 | 12559 | 12555 | unreviewed |
| gt_037 | 37 | 38 | matched | 12813 | 12859 | 13037 | 13051 | unreviewed |
| gt_039 | 39 | unavailable | missed | 13427 | unavailable | 13707 | unavailable | unreviewed |
| gt_041 | 41 | 43 | matched | 14125 | 14131 | 14251 | 14293 | unreviewed |
| gt_042 | 42 | 44 | matched | 14280 | 14320 | 14467 | 14442 | unreviewed |
| gt_044 | 44 | 46 | matched | 14885 | 14966 | 15386 | 15377 | unreviewed |
| gt_046 | 46 | 49 | matched | 16170 | 16186 | 16616 | 16532 | unreviewed |
| gt_048 | 48 | 51 | matched | 17293 | 17299 | 17435 | 17373 | unreviewed |
| gt_052 | 52 | 55 | matched | 18522 | 18595 | 18969 | 18947 | unreviewed |
| gt_053 | 53 | 56 | matched | 19021 | 19050 | 19472 | 19531 | unreviewed |
| gt_054 | 54 | 57 | matched | 19606 | 19567 | 20020 | 20055 | unreviewed |
| gt_055 | 55 | 59 | matched | 20061 | 20198 | 20884 | 20883 | unreviewed |
| gt_056 | 56 | unavailable | missed | 20947 | unavailable | 21045 | unavailable | unreviewed |
| gt_058 | 58 | unavailable | missed | 21736 | unavailable | 21809 | unavailable | unreviewed |
| gt_059 | 59 | 61 | matched | 22098 | 22111 | 22418 | 22367 | unreviewed |
| gt_061 | 61 | 63 | matched | 23025 | 23098 | 23222 | 23219 | unreviewed |
| gt_063 | 63 | unavailable | missed | 23879 | unavailable | 24012 | unavailable | unreviewed |
| gt_067 | 67 | 68 | matched | 25520 | 25629 | 26061 | 26018 | unreviewed |
| gt_069 | 69 | 70 | matched | 26616 | 26654 | 27668 | 27325 | unreviewed |
| gt_071 | 71 | 73 | matched | 27927 | 28002 | 28667 | 28671 | unreviewed |
| gt_072 | 72 | 74 | matched | 28694 | 28734 | 28937 | 28958 | unreviewed |
| pred_011 | unavailable | 11 | unmatched_prediction | unavailable | unavailable | unavailable | unavailable | unreviewed |
| pred_032 | unavailable | 32 | unmatched_prediction | unavailable | unavailable | unavailable | unavailable | unreviewed |
| pred_040 | unavailable | 40 | unmatched_prediction | unavailable | unavailable | unavailable | unavailable | unreviewed |
| pred_041 | unavailable | 41 | unmatched_prediction | unavailable | unavailable | unavailable | unavailable | unreviewed |
| pred_047 | unavailable | 47 | unmatched_prediction | unavailable | unavailable | unavailable | unavailable | unreviewed |
| pred_058 | unavailable | 58 | unmatched_prediction | unavailable | unavailable | unavailable | unavailable | unreviewed |
| pred_071 | unavailable | 71 | unmatched_prediction | unavailable | unavailable | unavailable | unavailable | unreviewed |

Interactive synchronized evidence: [index.html](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/visual_failure_package/index.html). Full raw FSM/contact traces and replay-versus-fresh parity remain in [diagnostic_replay](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/diagnostic_replay).

## Complete evidence references
- completion: [baseline_completion.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/baseline_completion.json)
- components: [component_reference_metrics.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/bound_reference_diagnostics/component_reference_metrics.json)
- reference_rows: [reference_row_comparisons.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/bound_reference_diagnostics/reference_row_comparisons.json)
- analysis: [technical_analysis.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/analysis/technical_analysis.json)
- inference: [inference.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run/inference.json)
- plan: [plan.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/protocol/plan.json)
- environment: [environment.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/environment.json)
- timestamps: [timestamp_audit.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/timestamps/timestamp_audit.json)
- export_receipt: [export_receipt.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/downstream_exports/export_receipt.json)
- analytics: [analytics.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/downstream_exports/analytics.json)
- individual: [individual_analytics.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/downstream_exports/individual_analytics.json)
- estimated: [estimated_individual_analytics.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/downstream_exports/estimated_individual_analytics.json)
- highlights: [highlights.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/downstream_exports/highlights.json)
- outcomes: [rally_outcome_records.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/downstream_exports/rally_outcome_records.json)
- scoring: [scoring_outcome_evidence.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/downstream_exports/scoring_outcome_evidence.json)
- failure_cases: [failure_case_index.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/visual_failure_package/failure_case_index.json)
- failure_manifest: [manifest.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/visual_failure_package/manifest.json)
- replay: [parity_vs_fresh.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/diagnostic_replay/parity_vs_fresh.json)
- heatmaps: [heatmaps.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/heatmap_exports/heatmaps.json)
- heatmap_receipt: [export_receipt.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/heatmap_exports/export_receipt.json)
- per-frame point candidates: [frame_point_candidates.jsonl](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/bound_reference_diagnostics/frame_point_candidates.jsonl)
- full component details: [component_raw_details.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/bound_reference_diagnostics/component_raw_details.json)
- immutable original predictions: [predicted_rallies.csv](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run/predicted_rallies.csv)

Test2 evaluation evidence is complete enough to build this matrix. The orchestrator must separately review diagnosis, validate justified fixes and regression results, and verify retained artifacts before cleanup or advancement to Test3.
