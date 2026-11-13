# Test 3 — frozen-main component evaluation

Pipeline: `88aa0ad47d6be8dc1f073d0297efdb430b6ceaa0`. No pipeline changes, tuning or fixes were performed.

All supporting annotations are accounted for; generated references measure agreement. Unknown identity/outcome labels do not establish independently verified accuracy.

[Annotation inventory](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/test_03/annotations/evaluation_only_v1/README.md) · [Complete metrics JSON](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test03/components/component_reference_metrics.json) · [Raw comparisons](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test03/components/reference_raw_details.json) · [Visual evidence](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test03/visual_evidence) · [Diagnosis and proposed fixes](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/reports/evaluation_only_diagnosis_spec.md)

# Manifest-driven component evaluation

Native complete fresh worker and original cache guards passed. Generated references measure agreement, not physical accuracy. Original data and predictions are unchanged.

## Interval reference agreement

| Reference | Declared role | TP | FP | FN | Precision | Recall | F1 | Mean IoU |
|---|---|---|---|---|---|---|---|---|
| Test3_Full.csv | coarse_documented_human_origin_supplied_reference | 22 | 2 | 0 | 0.9166666666666666 | 1.0 | 0.9565217391304348 | 0.8719202531071143 |
| Test3_Full_Rev_T4.csv | historical_generated_interval_reference_agreement | 18 | 6 | 1 | 0.75 | 0.9473684210526315 | 0.8372093023255814 | 0.8953833204633642 |
| Test3_Full_rally.csv | historical_generated_interval_reference_agreement | 18 | 6 | 1 | 0.75 | 0.9473684210526315 | 0.8372093023255814 | 0.8953833204633642 |
| win_predictions.csv | historical_generated_outcome_interval_reference_agreement | 18 | 6 | 1 | 0.75 | 0.9473684210526315 | 0.8372093023255814 | 0.8953833204633642 |

## Test3_Full.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 14.909090909090908 | 15.0 | 17.753360757383888 | 34.0 | 25.0 | 13.0 | 14.0 |
| end_frame | 15.818181818181818 | 13.0 | 19.537842069360494 | 53.0 | 27.0 | 5.090909090909091 | 9.0 |
| start_time_sec | 0.4969696969696962 | 0.5 | 0.5917786919127956 | 1.1333333333333258 | 0.8333333333333318 | 0.4333333333333326 | 0.46666666666666856 |
| end_time_sec | 0.5272727272727296 | 0.4333333333333371 | 0.651261402312019 | 1.76666666666668 | 0.9000000000000057 | 0.169696969696969 | 0.30000000000000426 |
| duration_sec | 0.560606060606064 | 0.4000000000000057 | 0.7156264473321368 | 1.8333333333333428 | 1.1166666666666605 | -0.2636363636363635 | -0.2666666666666657 |

## Test3_Full.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 0 | 0.0 | 0.0 |
| start | 3 | 0.1 | 4 | 0.18181818181818182 | 0.18181818181818182 |
| start | 5 | 0.16666666666666666 | 6 | 0.2727272727272727 | 0.2727272727272727 |
| start | 10 | 0.3333333333333333 | 9 | 0.4090909090909091 | 0.4090909090909091 |
| start | 15 | 0.5 | 12 | 0.5454545454545454 | 0.5454545454545454 |
| start | 30 | 1.0 | 21 | 0.9545454545454546 | 0.9545454545454546 |
| end | 1 | 0.03333333333333333 | 0 | 0.0 | 0.0 |
| end | 3 | 0.1 | 2 | 0.09090909090909091 | 0.09090909090909091 |
| end | 5 | 0.16666666666666666 | 3 | 0.13636363636363635 | 0.13636363636363635 |
| end | 10 | 0.3333333333333333 | 10 | 0.45454545454545453 | 0.45454545454545453 |
| end | 15 | 0.5 | 14 | 0.6363636363636364 | 0.6363636363636364 |
| end | 30 | 1.0 | 21 | 0.9545454545454546 | 0.9545454545454546 |

## Test3_Full.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8719202531071143 |
| median_iou | 0.8808333333333314 |
| minimum_iou | 0.6777777777777771 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 90.9090909090909 |
| percent IoU strictly above 0.9 | 31.818181818181817 |
| percent IoU strictly above 0.95 | 13.636363636363637 |

Missed reference IDs: none.
## Test3_Full.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 10 | 3130 | 3187 | FP under complete reference |
| 22 | 7337 | 7394 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test3_Full_Rev_T4.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 28.666666666666668 | 5.0 | 63.109252711292484 | 233.0 | 88.0 | 28.444444444444443 | 5.0 |
| end_frame | 8.5 | 5.0 | 10.596120883501555 | 20.0 | 17.6 | 0.8333333333333334 | -1.0 |
| start_time_sec | 0.9555555555555545 | 0.16666666666666963 | 2.1036417570430848 | 7.76666666666668 | 2.9333333333333274 | 0.9481481481481475 | 0.16666666666666963 |
| end_time_sec | 0.28333333333333655 | 0.1666666666666714 | 0.35320402945005475 | 0.6666666666666856 | 0.5866666666666639 | 0.027777777777776593 | -0.03333333333333144 |
| duration_sec | 0.9907407407407413 | 0.3666666666666707 | 2.003900517478507 | 7.200000000000017 | 2.79333333333333 | -0.920370370370371 | -0.23333333333333073 |

## Test3_Full_Rev_T4.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 3 | 0.16666666666666666 | 0.15789473684210525 |
| start | 3 | 0.1 | 9 | 0.5 | 0.47368421052631576 |
| start | 5 | 0.16666666666666666 | 9 | 0.5 | 0.47368421052631576 |
| start | 10 | 0.3333333333333333 | 12 | 0.6666666666666666 | 0.631578947368421 |
| start | 15 | 0.5 | 13 | 0.7222222222222222 | 0.6842105263157895 |
| start | 30 | 1.0 | 14 | 0.7777777777777778 | 0.7368421052631579 |
| end | 1 | 0.03333333333333333 | 2 | 0.1111111111111111 | 0.10526315789473684 |
| end | 3 | 0.1 | 3 | 0.16666666666666666 | 0.15789473684210525 |
| end | 5 | 0.16666666666666666 | 11 | 0.6111111111111112 | 0.5789473684210527 |
| end | 10 | 0.3333333333333333 | 11 | 0.6111111111111112 | 0.5789473684210527 |
| end | 15 | 0.5 | 14 | 0.7777777777777778 | 0.7368421052631579 |
| end | 30 | 1.0 | 18 | 1.0 | 0.9473684210526315 |

## Test3_Full_Rev_T4.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8953833204633642 |
| median_iou | 0.9517829109665841 |
| minimum_iou | 0.5059288537549403 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 83.33333333333333 |
| percent IoU strictly above 0.9 | 72.22222222222223 |
| percent IoU strictly above 0.95 | 50.0 |

Missed reference IDs: 7.
## Test3_Full_Rev_T4.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 7 | 2485 | 2715 | FP under complete reference |
| 8 | 2717 | 2990 | FP under complete reference |
| 9 | 2993 | 3054 | FP under complete reference |
| 10 | 3130 | 3187 | FP under complete reference |
| 19 | 6692 | 6847 | FP under complete reference |
| 22 | 7337 | 7394 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test3_Full_rally.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 28.666666666666668 | 5.0 | 63.109252711292484 | 233.0 | 88.0 | 28.444444444444443 | 5.0 |
| end_frame | 8.5 | 5.0 | 10.596120883501555 | 20.0 | 17.6 | 0.8333333333333334 | -1.0 |
| start_time_sec | 0.9555555555555545 | 0.16666666666666963 | 2.1036417570430848 | 7.76666666666668 | 2.9333333333333274 | 0.9481481481481475 | 0.16666666666666963 |
| end_time_sec | 0.28333333333333655 | 0.1666666666666714 | 0.35320402945005475 | 0.6666666666666856 | 0.5866666666666639 | 0.027777777777776593 | -0.03333333333333144 |
| duration_sec | 0.9907407407407413 | 0.3666666666666707 | 2.003900517478507 | 7.200000000000017 | 2.79333333333333 | -0.920370370370371 | -0.23333333333333073 |

## Test3_Full_rally.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 3 | 0.16666666666666666 | 0.15789473684210525 |
| start | 3 | 0.1 | 9 | 0.5 | 0.47368421052631576 |
| start | 5 | 0.16666666666666666 | 9 | 0.5 | 0.47368421052631576 |
| start | 10 | 0.3333333333333333 | 12 | 0.6666666666666666 | 0.631578947368421 |
| start | 15 | 0.5 | 13 | 0.7222222222222222 | 0.6842105263157895 |
| start | 30 | 1.0 | 14 | 0.7777777777777778 | 0.7368421052631579 |
| end | 1 | 0.03333333333333333 | 2 | 0.1111111111111111 | 0.10526315789473684 |
| end | 3 | 0.1 | 3 | 0.16666666666666666 | 0.15789473684210525 |
| end | 5 | 0.16666666666666666 | 11 | 0.6111111111111112 | 0.5789473684210527 |
| end | 10 | 0.3333333333333333 | 11 | 0.6111111111111112 | 0.5789473684210527 |
| end | 15 | 0.5 | 14 | 0.7777777777777778 | 0.7368421052631579 |
| end | 30 | 1.0 | 18 | 1.0 | 0.9473684210526315 |

## Test3_Full_rally.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8953833204633642 |
| median_iou | 0.9517829109665841 |
| minimum_iou | 0.5059288537549403 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 83.33333333333333 |
| percent IoU strictly above 0.9 | 72.22222222222223 |
| percent IoU strictly above 0.95 | 50.0 |

Missed reference IDs: 7.
## Test3_Full_rally.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 7 | 2485 | 2715 | FP under complete reference |
| 8 | 2717 | 2990 | FP under complete reference |
| 9 | 2993 | 3054 | FP under complete reference |
| 10 | 3130 | 3187 | FP under complete reference |
| 19 | 6692 | 6847 | FP under complete reference |
| 22 | 7337 | 7394 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## win_predictions.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 28.666666666666668 | 5.0 | 63.109252711292484 | 233.0 | 88.0 | 28.444444444444443 | 5.0 |
| end_frame | 8.5 | 5.0 | 10.596120883501555 | 20.0 | 17.6 | 0.8333333333333334 | -1.0 |
| start_time_sec | 0.9555555555555545 | 0.16666666666666963 | 2.1036417570430848 | 7.76666666666668 | 2.9333333333333274 | 0.9481481481481475 | 0.16666666666666963 |
| end_time_sec | 0.28333333333333655 | 0.1666666666666714 | 0.35320402945005475 | 0.6666666666666856 | 0.5866666666666639 | 0.027777777777776593 | -0.03333333333333144 |
| duration_sec | 0.9907407407407413 | 0.3666666666666707 | 2.003900517478507 | 7.200000000000017 | 2.79333333333333 | -0.920370370370371 | -0.23333333333333073 |

## win_predictions.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 3 | 0.16666666666666666 | 0.15789473684210525 |
| start | 3 | 0.1 | 9 | 0.5 | 0.47368421052631576 |
| start | 5 | 0.16666666666666666 | 9 | 0.5 | 0.47368421052631576 |
| start | 10 | 0.3333333333333333 | 12 | 0.6666666666666666 | 0.631578947368421 |
| start | 15 | 0.5 | 13 | 0.7222222222222222 | 0.6842105263157895 |
| start | 30 | 1.0 | 14 | 0.7777777777777778 | 0.7368421052631579 |
| end | 1 | 0.03333333333333333 | 2 | 0.1111111111111111 | 0.10526315789473684 |
| end | 3 | 0.1 | 3 | 0.16666666666666666 | 0.15789473684210525 |
| end | 5 | 0.16666666666666666 | 11 | 0.6111111111111112 | 0.5789473684210527 |
| end | 10 | 0.3333333333333333 | 11 | 0.6111111111111112 | 0.5789473684210527 |
| end | 15 | 0.5 | 14 | 0.7777777777777778 | 0.7368421052631579 |
| end | 30 | 1.0 | 18 | 1.0 | 0.9473684210526315 |

## win_predictions.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8953833204633642 |
| median_iou | 0.9517829109665841 |
| minimum_iou | 0.5059288537549403 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 83.33333333333333 |
| percent IoU strictly above 0.9 | 72.22222222222223 |
| percent IoU strictly above 0.95 | 50.0 |

Missed reference IDs: 7.
## win_predictions.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 7 | 2485 | 2715 | FP under complete reference |
| 8 | 2717 | 2990 | FP under complete reference |
| 9 | 2993 | 3054 | FP under complete reference |
| 10 | 3130 | 3187 | FP under complete reference |
| 19 | 6692 | 6847 | FP under complete reference |
| 22 | 7337 | 7394 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Annotation coverage

| File | Declared role | Purpose | Ambiguity |
|---|---|---|---|
| Test3_Full.csv | interval_reference | 22 coarse whole-second rally spans plus symbolic winner/reason/final-ball-type/running-score candidates | Row6 has7 of8 fields: retain valid timing; semantic fields ball_types/lose_reason/scores are misaligned or missing. Row9 winner has leading whitespace. No certified A/B identity or official scoreboard binding. One ball_types value is not per-contact shot GT. |
| Test3_Full_Rev_T4.csv | interval_reference | 19 generated frame/time intervals; preserve both supplied files as separate references | Exact byte duplicates, not independent GT. Different count/boundaries from22 coarse spans. Human frame-exact timing completeness not certified; printed clock fields are lossy displays. |
| Test3_Full_ball_filled.csv | dense_generated_shuttle | 8414-frame generated/interpolated shuttle image-coordinate/visibility/support reference | Visibility is exporter state, not reviewed physical visibility. No observed-versus-filled indicator; confidence is uncalibrated model output. Invisible(0,0) sentinel is not a position. No coordinate certificate yet. |
| Test3_Full_court.json | manual_court | Manual-origin assertion for one frame4207 with1280x720 corners and net coordinates | No supplied physical singles/doubles line semantics, named reviewer or source-image certificate. Do not inject into automatic calibration or infer all-frame/airborne3D accuracy. |
| Test3_Full_rally.csv | interval_reference | 19 generated frame/time intervals; preserve both supplied files as separate references | Exact byte duplicates, not independent GT. Different count/boundaries from22 coarse spans. Human frame-exact timing completeness not certified; printed clock fields are lossy displays. |
| player_detections.csv | dense_generated_players | 8414-frame two-slot generated bottom-center and confidence reference | Legacy producer enumerates first two filtered YOLO detections per frame, without persistent physical identity. Not boxes, pose joints or reviewed detection/tracking GT. Missing cells remain missing; no coordinate certificate yet. |
| win_predictions.csv | interval_reference | 19 generated outcome/reason/score rows with exact frame boundaries; compare timing while preserving semantic counts | ML/rule provenance and CNN supports are earlier predictions, not winner/reason/score truth. Frames exactly equal generated rally table. Legacy Player A=far/Player B=near is producer convention, not reviewed physical identity for this video. |

## Generated point disagreement

| Reference | Population | Bound | Count | Mean px | Median px | Min px | Max px | P90 px | P95 px |
|---|---|---|---|---|---|---|---|---|---|
| Test3_Full_ball_filled.csv | all current | True | 6169 | 1.890797978284961 | 1.4448386615202167 | 0.030690131405469914 | 414.0485292391738 | 2.527405426513281 | 2.9287753833518018 |
| Test3_Full_ball_filled.csv | fresh detector | True | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | all current | True | 16652 | 2.7288475207847283 | 1.4858176029233854 | 0.012800878161801829 | 37.45864739131699 | 6.829752826907652 | 9.243946636783358 |
| player_detections.csv | fresh detector | True | 7698 | 1.5974033552760176 | 1.107146090753275 | 0.026372502815529577 | 26.108384728383513 | 2.785037772202364 | 4.463769937448575 |

## Point coverage and data quality

| Reference | Count meaning | Count |
|---|---|---|
| Test3_Full_ball_filled.csv | reference_visible=False,current_raw_present=False | 1297 |
| Test3_Full_ball_filled.csv | visibility_unknown | 0 |
| Test3_Full_ball_filled.csv | visible_invalid_numeric | 0 |
| Test3_Full_ball_filled.csv | out_of_image_reference_points | 0 |
| Test3_Full_ball_filled.csv | reference_visible=True,current_raw_present=False | 892 |
| Test3_Full_ball_filled.csv | reference_visible=True,current_raw_present=True | 6169 |
| Test3_Full_ball_filled.csv | reference_visible=False,current_raw_present=True | 56 |
| player_detections.csv | reference_points | 16709 |
| player_detections.csv | out_of_image_reference_points | 0 |
| player_detections.csv | current_points | 16656 |
| player_detections.csv | all_current_unmatched_reference | 57 |
| player_detections.csv | all_current_unmatched_current | 4 |
| player_detections.csv | fresh_detector_unmatched_reference | 9011 |
| player_detections.csv | fresh_detector_unmatched_current | 1 |
| player_detections.csv | missing_or_invalid_slot_coordinates | 119 |

## Byte-identical dense-reference aliases

| Duplicate | Evaluated primary |
|---|---|

## Single-frame court candidates

| File | Frame | Bound | Mean corner px | Max corner px | Limit |
|---|---|---|---|---|---|
| Test3_Full_court.json | 4207 | True | unavailable | unavailable | No compatible VALID current calibration |

## Raw component coverage

| Quantity | Count |
|---|---|
| frames | 8414 |
| raw_shuttle_present | 6225 |
| detector_executed_frames | 3852 |
| person_rows | 16656 |
| scene_telemetry_present | 3640 |
| scene_raw_hypotheses | 14 |
| actual_content_epoch_increments | 14 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 7699 |
| person_propagated_or_unmatched | 8957 |
| pose_present_rows | 14856 |
| pose_current_source_rows | 14856 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 7181 |
| racket_present_rows | 5885 |
| racket_current_source_rows | 5885 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 69 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 69 |

## Track coverage

| Quantity | Count |
|---|---|
| camera_rows | 8414 |
| player_rows | 16629 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 16444 |
| projected_court_on_propagated_box | 8870 |
| racket_rows | 5868 |
| shuttle_rows | 8414 |

## Live event counts

| Quantity | Count |
|---|---|
| calibration | 1 |
| racket_observation_ambiguity | 1744 |
| activity_interval | 43 |
| scene | 6 |
| participant_observation | 52 |
| format_decision | 1 |
| rally_start | 24 |
| stroke | 274 |
| contact | 274 |
| rally_end | 24 |
| shuttle_turn | 16 |
| broadcast_score | 207 |
| identity_ambiguity | 21 |
| match_phase | 1 |
| highlight | 1 |

## Outcome and score coverage

| Quantity | Value |
|---|---|
| predicted_rallies | 24 |
| known_winner_outputs | 0 |
| unknown_winner_outputs | 24 |
| canonical_point_events | 0 |
| broadcast_score_observation_events | 207 |
| accuracy_status | unavailable_without_independent_identity_event_outcome_score_labels |

## Predicted stroke counts

| Predicted class | Count |
|---|---|
| unknown | 186 |
| push | 49 |
| lift | 11 |
| net_shot | 11 |
| drop | 9 |
| clear | 5 |
| drive | 3 |

## Actual runtime and resources

| Quantity | Measured value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 722646 |
| parent_failure_inclusive_elapsed_s | unavailable |
| parent_failure_inclusive_source_fps | unavailable |
| neural_only_throughput_fps | unavailable |
| model_loading_time_s | unavailable |
| media_ready_time_s | 1.8702243859879673 |
| model_staging_time_s | 1.7700658198446035 |
| worker_final_cpu_s | 10972.639943000002 |
| worker_maxrss_bytes | 2807406592 |
| sampled_worker_tree_peak_rss_bytes | 2791931904 |
| sampled_worker_gpu_peak_mib | 2122 |
| sampled_cpu_seconds_max_observed | 10972.07 |
| sampled_cpu_seconds_last_observed | 10972.07 |
| sampled_system_available_ram_min_bytes | 101537132544 |
| sample_count | 470 |
| resource_rows | 470 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 973.3628617497161 |
| parent_completed_source_fps | 8.644258303501536 |
| worker_elapsed_s | 967.4764997912571 |
| worker_source_fps | 8.696852070117885 |
| component_initialization_including_models_s | 8.715979506727308 |

## Stage invocation timing (scopes can overlap)

| Stage | Calls | Seconds | P50 ms | P95 ms |
|---|---|---|---|---|
| court | 141 | 45.58305310131982 | 305.2658988162875 | 402.38335309550166 |
| content_continuity_and_players | 141 | 466.023289448116 | 3500.7057660259306 | 3760.1641919463873 |
| shuttle | 141 | 125.84295260393992 | 875.8662142790854 | 1061.8530930951238 |
| players | 141 | 40.03598018595949 | 271.79616782814264 | 598.8833289593458 |
| ocr | 141 | 126.4783441615291 | 887.8341508097947 | 1041.3114186376333 |

## Verified actual model artifacts

| Group | Model | SHA256 | Status |
|---|---|---|---|
| registry_artifacts | osnet_ain_x0_25 | unavailable | unavailable_not_claimed_loaded |
| registry_artifacts | racketvision_balltrack | unavailable | unavailable_not_claimed_loaded |
| registry_artifacts | rfdetr_small | fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e | verified |
| registry_artifacts | rtmpose_m_body7 | f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741 | verified |
| registry_artifacts | tracknetv3 | df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a | verified |
| package_ocr_artifacts | det | 090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f | verified |
| package_ocr_artifacts | cls | e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c | verified |
| package_ocr_artifacts | rec | 6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884 | verified |

## Actual worker backend declarations

| Stage | Requested | Actual | Device | Dtype | Fallback |
|---|---|---|---|---|---|
| shuttle | torch-cuda | torch-cuda | cuda:0 | torch.float16 | False |
| shuttle_association | unavailable | numpy-cpu | unavailable | unavailable | unavailable |
| content_continuity | unavailable | opencv-cpu | unavailable | unavailable | unavailable |
| player_detector | onnx-cuda | onnx-cuda | unavailable | unavailable | False |
| pose | onnx-cuda | onnx-cuda | unavailable | unavailable | False |
| ocr | onnx-cpu | unavailable | unavailable | unavailable | False |
| racket | opencv-cpu | opencv-cpu | unavailable | unavailable | False |

## Source and coordinate provenance

| Quantity | Value |
|---|---|
| Source SHA256 | d587569affa3b4fcabab0ea6b97ecd278af15675ce5cba36c79298bb6d0db5fa |
| Native guard root | /home/administrator/Desktop/sport-analytics/Sports_Analytics |
| Recorded pipeline commit | 88aa0ad47d6be8dc1f073d0297efdb430b6ceaa0 |
| Coordinate review | diagnostic_coordinate_binding_declared |

## Unavailable physical accuracy

| Metric family | Value | Prerequisite |
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

Full per-reference rows, original fields/eligibility and semantic field counts: [reference_raw_details.json](reference_raw_details.json). All scalar metrics and complete actual Worker/profile/backend/source provenance: [component_reference_metrics.json](component_reference_metrics.json). Detailed OCR/scene/events/tracks/resources: [component_raw_details.json](component_raw_details.json). Synchronized points are separate point_reference_XX.jsonl files.

Execution, coverage and generated-reference agreement do not validate physical accuracy. Unavailable values remain null, not zero. Raw arrays are preserved outside this summary.
