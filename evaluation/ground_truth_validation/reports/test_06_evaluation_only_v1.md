# Test 6 — frozen-main component evaluation

Pipeline: `88aa0ad47d6be8dc1f073d0297efdb430b6ceaa0`. No pipeline changes, tuning or fixes were performed.

All supporting annotations are accounted for; generated references measure agreement. Unknown identity/outcome labels do not establish independently verified accuracy.

[Annotation inventory](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/test_06/annotations/evaluation_only_v1/README.md) · [Complete metrics JSON](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test06/components/component_reference_metrics.json) · [Raw comparisons](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test06/components/reference_raw_details.json) · [Visual evidence](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test06/visual_evidence) · [Diagnosis and proposed fixes](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/reports/evaluation_only_diagnosis_spec.md)

# Manifest-driven component evaluation

Native complete fresh worker and original cache guards passed. Generated references measure agreement, not physical accuracy. Original data and predictions are unchanged.

## Interval reference agreement

| Reference | Declared role | TP | FP | FN | Precision | Recall | F1 | Mean IoU |
|---|---|---|---|---|---|---|---|---|
| Test6_Full.csv | coarse_documented_human_origin_supplied_reference | 40 | 8 | 2 | 0.8333333333333334 | 0.9523809523809523 | 0.8888888888888888 | 0.8405718442494946 |
| Test6_Full_T4.csv | historical_generated_interval_reference_agreement | 35 | 13 | 8 | 0.7291666666666666 | 0.813953488372093 | 0.7692307692307693 | 0.8793556433457254 |
| Test6_Full_rally.csv | historical_generated_interval_reference_agreement | 35 | 13 | 7 | 0.7291666666666666 | 0.8333333333333334 | 0.7777777777777778 | 0.8793556433457254 |
| win_predictions.csv | historical_generated_outcome_interval_reference_agreement | 35 | 13 | 7 | 0.7291666666666666 | 0.8333333333333334 | 0.7777777777777778 | 0.8793556433457254 |

## Test6_Full.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 21.275 | 14.5 | 39.68028477720391 | 213.0 | 39.300000000000004 | 15.475 | 11.0 |
| end_frame | 26.95 | 16.0 | 51.07347648241698 | 278.0 | 42.30000000000002 | 4.65 | 11.0 |
| start_time_sec | 0.7091666666666674 | 0.48333333333332007 | 1.3226761592401304 | 7.099999999999994 | 1.3099999999999985 | 0.5158333333333347 | 0.36666666666665293 |
| end_time_sec | 0.8983333333333323 | 0.5333333333333172 | 1.7024492160805647 | 9.266666666666652 | 1.4100000000000086 | 0.15500000000000283 | 0.3666666666666458 |
| duration_sec | 1.2191666666666687 | 0.6666666666666714 | 2.203753111802176 | 9.766666666666652 | 1.950000000000003 | -0.3608333333333319 | -0.08333333333335702 |

## Test6_Full.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 2 | 0.05 | 0.047619047619047616 |
| start | 3 | 0.1 | 7 | 0.175 | 0.16666666666666666 |
| start | 5 | 0.16666666666666666 | 10 | 0.25 | 0.23809523809523808 |
| start | 10 | 0.3333333333333333 | 16 | 0.4 | 0.38095238095238093 |
| start | 15 | 0.5 | 23 | 0.575 | 0.5476190476190477 |
| start | 30 | 1.0 | 32 | 0.8 | 0.7619047619047619 |
| end | 1 | 0.03333333333333333 | 1 | 0.025 | 0.023809523809523808 |
| end | 3 | 0.1 | 4 | 0.1 | 0.09523809523809523 |
| end | 5 | 0.16666666666666666 | 7 | 0.175 | 0.16666666666666666 |
| end | 10 | 0.3333333333333333 | 13 | 0.325 | 0.30952380952380953 |
| end | 15 | 0.5 | 19 | 0.475 | 0.4523809523809524 |
| end | 30 | 1.0 | 31 | 0.775 | 0.7380952380952381 |

## Test6_Full.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8405718442494946 |
| median_iou | 0.8725729927007275 |
| minimum_iou | 0.5116666666666674 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 82.5 |
| percent IoU strictly above 0.9 | 42.5 |
| percent IoU strictly above 0.95 | 20.0 |

Missed reference IDs: 27, 31.
## Test6_Full.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 2 | 666 | 725 | FP under complete reference |
| 12 | 3943 | 4140 | FP under complete reference |
| 15 | 5111 | 5191 | FP under complete reference |
| 25 | 7970 | 8232 | FP under complete reference |
| 31 | 10341 | 10439 | FP under complete reference |
| 32 | 10567 | 10767 | FP under complete reference |
| 36 | 12393 | 12503 | FP under complete reference |
| 48 | 17363 | 17878 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test6_Full_T4.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.314285714285713 | 10.0 | 43.112477477938036 | 201.0 | 51.6 | 21.82857142857143 | 6.0 |
| end_frame | 22.34285714285714 | 12.0 | 49.952548912514395 | 263.0 | 41.80000000000002 | -10.285714285714286 | -1.0 |
| start_time_sec | 0.777142857142855 | 0.33333333333337123 | 1.4370825825979325 | 6.699999999999989 | 1.7200000000000046 | 0.7276190476190483 | 0.1999999999999318 |
| end_time_sec | 0.7447619047619033 | 0.39999999999997726 | 1.6650849637504774 | 8.766666666666652 | 1.3933333333333286 | -0.3428571428571446 | -0.03333333333335986 |
| duration_sec | 1.3619047619047688 | 0.7333333333333201 | 2.4026440461912824 | 10.46666666666664 | 2.2666666666666604 | -1.070476190476193 | -0.566666666666606 |

## Test6_Full_T4.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 6 | 0.17142857142857143 | 0.13953488372093023 |
| start | 3 | 0.1 | 8 | 0.22857142857142856 | 0.18604651162790697 |
| start | 5 | 0.16666666666666666 | 15 | 0.42857142857142855 | 0.3488372093023256 |
| start | 10 | 0.3333333333333333 | 18 | 0.5142857142857142 | 0.4186046511627907 |
| start | 15 | 0.5 | 19 | 0.5428571428571428 | 0.4418604651162791 |
| start | 30 | 1.0 | 25 | 0.7142857142857143 | 0.5813953488372093 |
| end | 1 | 0.03333333333333333 | 5 | 0.14285714285714285 | 0.11627906976744186 |
| end | 3 | 0.1 | 11 | 0.3142857142857143 | 0.2558139534883721 |
| end | 5 | 0.16666666666666666 | 15 | 0.42857142857142855 | 0.3488372093023256 |
| end | 10 | 0.3333333333333333 | 17 | 0.4857142857142857 | 0.3953488372093023 |
| end | 15 | 0.5 | 23 | 0.6571428571428571 | 0.5348837209302325 |
| end | 30 | 1.0 | 28 | 0.8 | 0.6511627906976745 |

## Test6_Full_T4.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8793556433457254 |
| median_iou | 0.9040511727078858 |
| minimum_iou | 0.6111111111111105 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 88.57142857142857 |
| percent IoU strictly above 0.9 | 54.285714285714285 |
| percent IoU strictly above 0.95 | 31.428571428571427 |

Missed reference IDs: 9, 19, 22, 23, 27, 31, 41, 42.
## Test6_Full_T4.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 2 | 666 | 725 | FP under complete reference |
| 10 | 3592 | 3636 | FP under complete reference |
| 11 | 3796 | 3880 | FP under complete reference |
| 12 | 3943 | 4140 | FP under complete reference |
| 15 | 5111 | 5191 | FP under complete reference |
| 16 | 5221 | 5314 | FP under complete reference |
| 24 | 7635 | 7942 | FP under complete reference |
| 25 | 7970 | 8232 | FP under complete reference |
| 31 | 10341 | 10439 | FP under complete reference |
| 32 | 10567 | 10767 | FP under complete reference |
| 36 | 12393 | 12503 | FP under complete reference |
| 46 | 16877 | 17205 | FP under complete reference |
| 47 | 17225 | 17279 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test6_Full_rally.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.314285714285713 | 10.0 | 43.112477477938036 | 201.0 | 51.6 | 21.82857142857143 | 6.0 |
| end_frame | 22.34285714285714 | 12.0 | 49.952548912514395 | 263.0 | 41.80000000000002 | -10.285714285714286 | -1.0 |
| start_time_sec | 0.777142857142855 | 0.33333333333337123 | 1.4370825825979325 | 6.699999999999989 | 1.7200000000000046 | 0.7276190476190483 | 0.1999999999999318 |
| end_time_sec | 0.7447619047619033 | 0.39999999999997726 | 1.6650849637504774 | 8.766666666666652 | 1.3933333333333286 | -0.3428571428571446 | -0.03333333333335986 |
| duration_sec | 1.3619047619047688 | 0.7333333333333201 | 2.4026440461912824 | 10.46666666666664 | 2.2666666666666604 | -1.070476190476193 | -0.566666666666606 |

## Test6_Full_rally.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 6 | 0.17142857142857143 | 0.14285714285714285 |
| start | 3 | 0.1 | 8 | 0.22857142857142856 | 0.19047619047619047 |
| start | 5 | 0.16666666666666666 | 15 | 0.42857142857142855 | 0.35714285714285715 |
| start | 10 | 0.3333333333333333 | 18 | 0.5142857142857142 | 0.42857142857142855 |
| start | 15 | 0.5 | 19 | 0.5428571428571428 | 0.4523809523809524 |
| start | 30 | 1.0 | 25 | 0.7142857142857143 | 0.5952380952380952 |
| end | 1 | 0.03333333333333333 | 5 | 0.14285714285714285 | 0.11904761904761904 |
| end | 3 | 0.1 | 11 | 0.3142857142857143 | 0.2619047619047619 |
| end | 5 | 0.16666666666666666 | 15 | 0.42857142857142855 | 0.35714285714285715 |
| end | 10 | 0.3333333333333333 | 17 | 0.4857142857142857 | 0.40476190476190477 |
| end | 15 | 0.5 | 23 | 0.6571428571428571 | 0.5476190476190477 |
| end | 30 | 1.0 | 28 | 0.8 | 0.6666666666666666 |

## Test6_Full_rally.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8793556433457254 |
| median_iou | 0.9040511727078858 |
| minimum_iou | 0.6111111111111105 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 88.57142857142857 |
| percent IoU strictly above 0.9 | 54.285714285714285 |
| percent IoU strictly above 0.95 | 31.428571428571427 |

Missed reference IDs: 9, 19, 22, 26, 30, 40, 41.
## Test6_Full_rally.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 2 | 666 | 725 | FP under complete reference |
| 10 | 3592 | 3636 | FP under complete reference |
| 11 | 3796 | 3880 | FP under complete reference |
| 12 | 3943 | 4140 | FP under complete reference |
| 15 | 5111 | 5191 | FP under complete reference |
| 16 | 5221 | 5314 | FP under complete reference |
| 24 | 7635 | 7942 | FP under complete reference |
| 25 | 7970 | 8232 | FP under complete reference |
| 31 | 10341 | 10439 | FP under complete reference |
| 32 | 10567 | 10767 | FP under complete reference |
| 36 | 12393 | 12503 | FP under complete reference |
| 46 | 16877 | 17205 | FP under complete reference |
| 47 | 17225 | 17279 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## win_predictions.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.314285714285713 | 10.0 | 43.112477477938036 | 201.0 | 51.6 | 21.82857142857143 | 6.0 |
| end_frame | 22.34285714285714 | 12.0 | 49.952548912514395 | 263.0 | 41.80000000000002 | -10.285714285714286 | -1.0 |
| start_time_sec | 0.777142857142855 | 0.33333333333337123 | 1.4370825825979325 | 6.699999999999989 | 1.7200000000000046 | 0.7276190476190483 | 0.1999999999999318 |
| end_time_sec | 0.7447619047619033 | 0.39999999999997726 | 1.6650849637504774 | 8.766666666666652 | 1.3933333333333286 | -0.3428571428571446 | -0.03333333333335986 |
| duration_sec | 1.3619047619047688 | 0.7333333333333201 | 2.4026440461912824 | 10.46666666666664 | 2.2666666666666604 | -1.070476190476193 | -0.566666666666606 |

## win_predictions.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 6 | 0.17142857142857143 | 0.14285714285714285 |
| start | 3 | 0.1 | 8 | 0.22857142857142856 | 0.19047619047619047 |
| start | 5 | 0.16666666666666666 | 15 | 0.42857142857142855 | 0.35714285714285715 |
| start | 10 | 0.3333333333333333 | 18 | 0.5142857142857142 | 0.42857142857142855 |
| start | 15 | 0.5 | 19 | 0.5428571428571428 | 0.4523809523809524 |
| start | 30 | 1.0 | 25 | 0.7142857142857143 | 0.5952380952380952 |
| end | 1 | 0.03333333333333333 | 5 | 0.14285714285714285 | 0.11904761904761904 |
| end | 3 | 0.1 | 11 | 0.3142857142857143 | 0.2619047619047619 |
| end | 5 | 0.16666666666666666 | 15 | 0.42857142857142855 | 0.35714285714285715 |
| end | 10 | 0.3333333333333333 | 17 | 0.4857142857142857 | 0.40476190476190477 |
| end | 15 | 0.5 | 23 | 0.6571428571428571 | 0.5476190476190477 |
| end | 30 | 1.0 | 28 | 0.8 | 0.6666666666666666 |

## win_predictions.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8793556433457254 |
| median_iou | 0.9040511727078858 |
| minimum_iou | 0.6111111111111105 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 88.57142857142857 |
| percent IoU strictly above 0.9 | 54.285714285714285 |
| percent IoU strictly above 0.95 | 31.428571428571427 |

Missed reference IDs: 9, 19, 22, 26, 30, 40, 41.
## win_predictions.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 2 | 666 | 725 | FP under complete reference |
| 10 | 3592 | 3636 | FP under complete reference |
| 11 | 3796 | 3880 | FP under complete reference |
| 12 | 3943 | 4140 | FP under complete reference |
| 15 | 5111 | 5191 | FP under complete reference |
| 16 | 5221 | 5314 | FP under complete reference |
| 24 | 7635 | 7942 | FP under complete reference |
| 25 | 7970 | 8232 | FP under complete reference |
| 31 | 10341 | 10439 | FP under complete reference |
| 32 | 10567 | 10767 | FP under complete reference |
| 36 | 12393 | 12503 | FP under complete reference |
| 46 | 16877 | 17205 | FP under complete reference |
| 47 | 17225 | 17279 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Annotation coverage

| File | Declared role | Purpose | Ambiguity |
|---|---|---|---|
| Test6_Full.csv | interval_reference | 42 supplied coarse clock/outcome/score records; all parseable nonblank timing retained | Documented legacy human-origin reference candidate; no certified physical A/B/team/official-score or exhaustive shot binding. Preserve blanks, raw taxonomy, score jumps and label conflicts. |
| Test6_Full_T4.csv | interval_reference | 43 original generated timing records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |
| Test6_Full_ball_filled.csv | dense_generated_shuttle | 17915 generated/filled shuttle coordinate and visibility rows; confidence column absent | No reviewed physical visibility/location GT or observed-versus-filled flag. Preserve out-of-image coordinates and invisible(0,0) sentinels. Missing confidence is unavailable, never synthesized; no coordinate certificate. |
| Test6_Full_court.json | supporting | One-frame court/net coordinate candidate at frame8957; explicit origin=unspecified | Physical line semantics/source-image alignment unverified. Source field absent: do not promote to manually labelled ground truth. No all-frame or airborne3D accuracy; never inject into automatic calibration. |
| Test6_Full_rally.csv | interval_reference | 42 original generated timing records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |
| player_detections.csv | dense_generated_players | 17915 anonymous two-slot generated bottom-center/confidence rows | Legacy first-two detection slots, not physical persistent identity. No reviewed boxes/pose/identity GT; missing cells stay missing; coordinate distances require certificate. |
| win_predictions.csv | interval_reference | 42 original generated timing/outcome/model-support/score records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |

## Generated point disagreement

| Reference | Population | Bound | Count | Mean px | Median px | Min px | Max px | P90 px | P95 px |
|---|---|---|---|---|---|---|---|---|---|
| Test6_Full_ball_filled.csv | all current | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| Test6_Full_ball_filled.csv | fresh detector | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | all current | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | fresh detector | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |

## Point coverage and data quality

| Reference | Count meaning | Count |
|---|---|---|
| Test6_Full_ball_filled.csv | reference_visible=False,current_raw_present=False | 680 |
| Test6_Full_ball_filled.csv | visibility_unknown | 0 |
| Test6_Full_ball_filled.csv | visible_invalid_numeric | 0 |
| Test6_Full_ball_filled.csv | out_of_image_reference_points | 0 |
| Test6_Full_ball_filled.csv | reference_visible=True,current_raw_present=False | 2540 |
| Test6_Full_ball_filled.csv | reference_visible=True,current_raw_present=True | 14669 |
| Test6_Full_ball_filled.csv | reference_visible=False,current_raw_present=True | 26 |
| player_detections.csv | reference_points | 35395 |
| player_detections.csv | out_of_image_reference_points | 0 |
| player_detections.csv | current_points | 36002 |
| player_detections.csv | missing_or_invalid_slot_coordinates | 435 |

## Byte-identical dense-reference aliases

| Duplicate | Evaluated primary |
|---|---|

## Single-frame court candidates

| File | Frame | Bound | Mean corner px | Max corner px | Limit |
|---|---|---|---|---|---|

## Raw component coverage

| Quantity | Count |
|---|---|
| frames | 17915 |
| raw_shuttle_present | 14695 |
| detector_executed_frames | 8783 |
| person_rows | 36002 |
| scene_telemetry_present | 3704 |
| scene_raw_hypotheses | 39 |
| actual_content_epoch_increments | 42 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 17646 |
| person_propagated_or_unmatched | 18356 |
| pose_present_rows | 34781 |
| pose_current_source_rows | 34781 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 17153 |
| racket_present_rows | 14348 |
| racket_current_source_rows | 14348 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 130 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 130 |

## Track coverage

| Quantity | Count |
|---|---|
| camera_rows | 17915 |
| player_rows | 35994 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 35104 |
| projected_court_on_propagated_box | 17902 |
| racket_rows | 14343 |
| shuttle_rows | 17915 |

## Live event counts

| Quantity | Count |
|---|---|
| calibration | 1 |
| activity_interval | 65 |
| scene | 1 |
| participant_observation | 106 |
| racket_observation_ambiguity | 3959 |
| format_decision | 1 |
| rally_start | 48 |
| stroke | 600 |
| contact | 600 |
| rally_end | 48 |
| identity_ambiguity | 43 |
| broadcast_score | 477 |
| match_phase | 1 |
| highlight | 4 |
| shuttle_turn | 17 |

## Outcome and score coverage

| Quantity | Value |
|---|---|
| predicted_rallies | 48 |
| known_winner_outputs | 0 |
| unknown_winner_outputs | 48 |
| canonical_point_events | 0 |
| broadcast_score_observation_events | 477 |
| accuracy_status | unavailable_without_independent_identity_event_outcome_score_labels |

## Predicted stroke counts

| Predicted class | Count |
|---|---|
| unknown | 427 |
| push | 82 |
| net_shot | 19 |
| lift | 24 |
| clear | 8 |
| drive | 16 |
| drop | 21 |
| smash | 2 |
| rush | 1 |

## Actual runtime and resources

| Quantity | Measured value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 750520 |
| parent_failure_inclusive_elapsed_s | unavailable |
| parent_failure_inclusive_source_fps | unavailable |
| neural_only_throughput_fps | unavailable |
| model_loading_time_s | unavailable |
| media_ready_time_s | 1.8431949228979647 |
| model_staging_time_s | 1.6980746858753264 |
| worker_final_cpu_s | 23884.231433999998 |
| worker_maxrss_bytes | 2934673408 |
| sampled_worker_tree_peak_rss_bytes | 2887720960 |
| sampled_worker_gpu_peak_mib | 2124 |
| sampled_cpu_seconds_max_observed | 23884.49 |
| sampled_cpu_seconds_last_observed | 23884.49 |
| sampled_system_available_ram_min_bytes | 101752524800 |
| sample_count | 1054 |
| resource_rows | 1054 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 2183.220825475175 |
| parent_completed_source_fps | 8.205766357189647 |
| worker_elapsed_s | 2175.114664473105 |
| worker_source_fps | 8.236347394742836 |
| component_initialization_including_models_s | 9.38929946301505 |

## Stage invocation timing (scopes can overlap)

| Stage | Calls | Seconds | P50 ms | P95 ms |
|---|---|---|---|---|
| court | 299 | 93.71091108489782 | 305.40338484570384 | 403.87700963765377 |
| content_continuity_and_players | 299 | 1073.379328338895 | 3627.1210238337517 | 3824.6174663770944 |
| shuttle | 299 | 258.87711474485695 | 847.3265240900218 | 1009.591015335172 |
| players | 299 | 94.34176683798432 | 294.25829323008657 | 582.2308971546588 |
| ocr | 299 | 253.72802401334047 | 844.5187876932323 | 974.2029939312488 |

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
| Source SHA256 | 45f873540649ec9d2b20e2d14edbf35ba2b2e41b150bfe07f3c995a0310fdab8 |
| Native guard root | /home/administrator/Desktop/sport-analytics/Sports_Analytics |
| Recorded pipeline commit | 88aa0ad47d6be8dc1f073d0297efdb430b6ceaa0 |
| Coordinate review | unverified |

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
