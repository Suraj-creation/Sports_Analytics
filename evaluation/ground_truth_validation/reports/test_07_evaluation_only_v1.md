# Test 7 — frozen-main component evaluation

Pipeline: `88aa0ad47d6be8dc1f073d0297efdb430b6ceaa0`. No pipeline changes, tuning or fixes were performed.

All supporting annotations are accounted for; generated references measure agreement. Unknown identity/outcome labels do not establish independently verified accuracy.

[Annotation inventory](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/test_07/annotations/evaluation_only_v1/README.md) · [Complete metrics JSON](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test07/components/component_reference_metrics.json) · [Raw comparisons](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test07/components/reference_raw_details.json) · [Visual evidence](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test07/visual_evidence) · [Diagnosis and proposed fixes](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/reports/evaluation_only_diagnosis_spec.md)

# Manifest-driven component evaluation

Native complete fresh worker and original cache guards passed. Generated references measure agreement, not physical accuracy. Original data and predictions are unchanged.

## Interval reference agreement

| Reference | Declared role | TP | FP | FN | Precision | Recall | F1 | Mean IoU |
|---|---|---|---|---|---|---|---|---|
| Test7_Full.csv | coarse_documented_human_origin_supplied_reference | 29 | 3 | 2 | 0.90625 | 0.9354838709677419 | 0.9206349206349206 | 0.7826301837363039 |
| Test7_Full_T4.csv | historical_generated_interval_reference_agreement | 28 | 4 | 5 | 0.875 | 0.8484848484848485 | 0.8615384615384616 | 0.836646921927409 |
| Test7_Full_rally.csv | historical_generated_interval_reference_agreement | 28 | 4 | 2 | 0.875 | 0.9333333333333333 | 0.9032258064516129 | 0.836646921927409 |
| win_predictions.csv | historical_generated_outcome_interval_reference_agreement | 28 | 4 | 2 | 0.875 | 0.9333333333333333 | 0.9032258064516129 | 0.836646921927409 |

## Test7_Full.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 33.241379310344826 | 23.0 | 54.65061440800473 | 241.0 | 59.99999999999999 | 31.448275862068964 | 23.0 |
| end_frame | 18.862068965517242 | 13.0 | 31.849321976218388 | 135.0 | 43.8 | 4.655172413793103 | 7.0 |
| start_time_sec | 1.1080459770114954 | 0.7666666666666657 | 1.8216871469334917 | 8.033333333333331 | 1.9999999999999998 | 1.0482758620689667 | 0.7666666666666657 |
| end_time_sec | 0.6287356321839067 | 0.4333333333333371 | 1.0616440658739452 | 4.5 | 1.4600000000000022 | 0.15517241379310356 | 0.23333333333332007 |
| duration_sec | 1.0908045977011491 | 0.6333333333333258 | 1.8319325892330887 | 7.599999999999994 | 2.16666666666664 | -0.8931034482758631 | -0.5666666666666629 |

## Test7_Full.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 0 | 0.0 | 0.0 |
| start | 3 | 0.1 | 4 | 0.13793103448275862 | 0.12903225806451613 |
| start | 5 | 0.16666666666666666 | 4 | 0.13793103448275862 | 0.12903225806451613 |
| start | 10 | 0.3333333333333333 | 5 | 0.1724137931034483 | 0.16129032258064516 |
| start | 15 | 0.5 | 8 | 0.27586206896551724 | 0.25806451612903225 |
| start | 30 | 1.0 | 22 | 0.7586206896551724 | 0.7096774193548387 |
| end | 1 | 0.03333333333333333 | 2 | 0.06896551724137931 | 0.06451612903225806 |
| end | 3 | 0.1 | 7 | 0.2413793103448276 | 0.22580645161290322 |
| end | 5 | 0.16666666666666666 | 8 | 0.27586206896551724 | 0.25806451612903225 |
| end | 10 | 0.3333333333333333 | 14 | 0.4827586206896552 | 0.45161290322580644 |
| end | 15 | 0.5 | 19 | 0.6551724137931034 | 0.6129032258064516 |
| end | 30 | 1.0 | 24 | 0.8275862068965517 | 0.7741935483870968 |

## Test7_Full.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.7826301837363039 |
| median_iou | 0.8 |
| minimum_iou | 0.5856443719412724 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 65.51724137931035 |
| percent IoU strictly above 0.9 | 13.793103448275861 |
| percent IoU strictly above 0.95 | 3.4482758620689653 |

Missed reference IDs: 22, 23.
## Test7_Full.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 4 | 1491 | 1615 | FP under complete reference |
| 22 | 6830 | 7018 | FP under complete reference |
| 24 | 7586 | 7695 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test7_Full_T4.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.214285714285715 | 8.0 | 50.616908524439026 | 226.0 | 47.60000000000002 | 20.642857142857142 | 6.5 |
| end_frame | 14.857142857142858 | 9.5 | 20.28018033168626 | 49.0 | 33.40000000000001 | -10.285714285714286 | -5.5 |
| start_time_sec | 0.7738095238095267 | 0.26666666666667416 | 1.6872302841479692 | 7.533333333333331 | 1.5866666666666795 | 0.6880952380952399 | 0.21666666666669698 |
| end_time_sec | 0.49523809523809337 | 0.3166666666666771 | 0.6760060110562062 | 1.6333333333333258 | 1.113333333333336 | -0.34285714285714153 | -0.18333333333334423 |
| duration_sec | 1.17380952380952 | 0.5666666666666629 | 2.0105870579162497 | 7.966666666666669 | 1.9633333333333443 | -1.0309523809523813 | -0.5000000000000142 |

## Test7_Full_T4.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.03571428571428571 | 0.030303030303030304 |
| start | 3 | 0.1 | 4 | 0.14285714285714285 | 0.12121212121212122 |
| start | 5 | 0.16666666666666666 | 9 | 0.32142857142857145 | 0.2727272727272727 |
| start | 10 | 0.3333333333333333 | 18 | 0.6428571428571429 | 0.5454545454545454 |
| start | 15 | 0.5 | 20 | 0.7142857142857143 | 0.6060606060606061 |
| start | 30 | 1.0 | 24 | 0.8571428571428571 | 0.7272727272727273 |
| end | 1 | 0.03333333333333333 | 2 | 0.07142857142857142 | 0.06060606060606061 |
| end | 3 | 0.1 | 7 | 0.25 | 0.21212121212121213 |
| end | 5 | 0.16666666666666666 | 10 | 0.35714285714285715 | 0.30303030303030304 |
| end | 10 | 0.3333333333333333 | 15 | 0.5357142857142857 | 0.45454545454545453 |
| end | 15 | 0.5 | 18 | 0.6428571428571429 | 0.5454545454545454 |
| end | 30 | 1.0 | 25 | 0.8928571428571429 | 0.7575757575757576 |

## Test7_Full_T4.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.836646921927409 |
| median_iou | 0.8569421892316824 |
| minimum_iou | 0.5411764705882328 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 82.14285714285714 |
| percent IoU strictly above 0.9 | 35.714285714285715 |
| percent IoU strictly above 0.95 | 10.714285714285714 |

Missed reference IDs: 3, 8, 23, 25, 29.
## Test7_Full_T4.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 3 | 1118 | 1455 | FP under complete reference |
| 4 | 1491 | 1615 | FP under complete reference |
| 5 | 1648 | 1943 | FP under complete reference |
| 22 | 6830 | 7018 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test7_Full_rally.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.214285714285715 | 8.0 | 50.616908524439026 | 226.0 | 47.60000000000002 | 20.642857142857142 | 6.5 |
| end_frame | 14.857142857142858 | 9.5 | 20.28018033168626 | 49.0 | 33.40000000000001 | -10.285714285714286 | -5.5 |
| start_time_sec | 0.7738095238095267 | 0.26666666666667416 | 1.6872302841479692 | 7.533333333333331 | 1.5866666666666795 | 0.6880952380952399 | 0.21666666666669698 |
| end_time_sec | 0.49523809523809337 | 0.3166666666666771 | 0.6760060110562062 | 1.6333333333333258 | 1.113333333333336 | -0.34285714285714153 | -0.18333333333334423 |
| duration_sec | 1.17380952380952 | 0.5666666666666629 | 2.0105870579162497 | 7.966666666666669 | 1.9633333333333443 | -1.0309523809523813 | -0.5000000000000142 |

## Test7_Full_rally.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.03571428571428571 | 0.03333333333333333 |
| start | 3 | 0.1 | 4 | 0.14285714285714285 | 0.13333333333333333 |
| start | 5 | 0.16666666666666666 | 9 | 0.32142857142857145 | 0.3 |
| start | 10 | 0.3333333333333333 | 18 | 0.6428571428571429 | 0.6 |
| start | 15 | 0.5 | 20 | 0.7142857142857143 | 0.6666666666666666 |
| start | 30 | 1.0 | 24 | 0.8571428571428571 | 0.8 |
| end | 1 | 0.03333333333333333 | 2 | 0.07142857142857142 | 0.06666666666666667 |
| end | 3 | 0.1 | 7 | 0.25 | 0.23333333333333334 |
| end | 5 | 0.16666666666666666 | 10 | 0.35714285714285715 | 0.3333333333333333 |
| end | 10 | 0.3333333333333333 | 15 | 0.5357142857142857 | 0.5 |
| end | 15 | 0.5 | 18 | 0.6428571428571429 | 0.6 |
| end | 30 | 1.0 | 25 | 0.8928571428571429 | 0.8333333333333334 |

## Test7_Full_rally.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.836646921927409 |
| median_iou | 0.8569421892316824 |
| minimum_iou | 0.5411764705882328 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 82.14285714285714 |
| percent IoU strictly above 0.9 | 35.714285714285715 |
| percent IoU strictly above 0.95 | 10.714285714285714 |

Missed reference IDs: 3, 22.
## Test7_Full_rally.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 3 | 1118 | 1455 | FP under complete reference |
| 4 | 1491 | 1615 | FP under complete reference |
| 5 | 1648 | 1943 | FP under complete reference |
| 22 | 6830 | 7018 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## win_predictions.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.214285714285715 | 8.0 | 50.616908524439026 | 226.0 | 47.60000000000002 | 20.642857142857142 | 6.5 |
| end_frame | 14.857142857142858 | 9.5 | 20.28018033168626 | 49.0 | 33.40000000000001 | -10.285714285714286 | -5.5 |
| start_time_sec | 0.7738095238095267 | 0.26666666666667416 | 1.6872302841479692 | 7.533333333333331 | 1.5866666666666795 | 0.6880952380952399 | 0.21666666666669698 |
| end_time_sec | 0.49523809523809337 | 0.3166666666666771 | 0.6760060110562062 | 1.6333333333333258 | 1.113333333333336 | -0.34285714285714153 | -0.18333333333334423 |
| duration_sec | 1.17380952380952 | 0.5666666666666629 | 2.0105870579162497 | 7.966666666666669 | 1.9633333333333443 | -1.0309523809523813 | -0.5000000000000142 |

## win_predictions.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.03571428571428571 | 0.03333333333333333 |
| start | 3 | 0.1 | 4 | 0.14285714285714285 | 0.13333333333333333 |
| start | 5 | 0.16666666666666666 | 9 | 0.32142857142857145 | 0.3 |
| start | 10 | 0.3333333333333333 | 18 | 0.6428571428571429 | 0.6 |
| start | 15 | 0.5 | 20 | 0.7142857142857143 | 0.6666666666666666 |
| start | 30 | 1.0 | 24 | 0.8571428571428571 | 0.8 |
| end | 1 | 0.03333333333333333 | 2 | 0.07142857142857142 | 0.06666666666666667 |
| end | 3 | 0.1 | 7 | 0.25 | 0.23333333333333334 |
| end | 5 | 0.16666666666666666 | 10 | 0.35714285714285715 | 0.3333333333333333 |
| end | 10 | 0.3333333333333333 | 15 | 0.5357142857142857 | 0.5 |
| end | 15 | 0.5 | 18 | 0.6428571428571429 | 0.6 |
| end | 30 | 1.0 | 25 | 0.8928571428571429 | 0.8333333333333334 |

## win_predictions.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.836646921927409 |
| median_iou | 0.8569421892316824 |
| minimum_iou | 0.5411764705882328 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 82.14285714285714 |
| percent IoU strictly above 0.9 | 35.714285714285715 |
| percent IoU strictly above 0.95 | 10.714285714285714 |

Missed reference IDs: 3, 22.
## win_predictions.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 3 | 1118 | 1455 | FP under complete reference |
| 4 | 1491 | 1615 | FP under complete reference |
| 5 | 1648 | 1943 | FP under complete reference |
| 22 | 6830 | 7018 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Annotation coverage

| File | Declared role | Purpose | Ambiguity |
|---|---|---|---|
| Test7_Full.csv | interval_reference | 31 supplied coarse clock/outcome/score records; all parseable nonblank timing retained | Documented legacy human-origin reference candidate; no certified physical A/B/team/official-score or exhaustive shot binding. Preserve blanks, raw taxonomy, score jumps and label conflicts. |
| Test7_Full_T4.csv | interval_reference | 33 original generated timing records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |
| Test7_Full_ball_filled.csv | dense_generated_shuttle | 10725 generated/filled shuttle coordinate and visibility rows; confidence column absent | No reviewed physical visibility/location GT or observed-versus-filled flag. Preserve out-of-image coordinates and invisible(0,0) sentinels. Missing confidence is unavailable, never synthesized; no coordinate certificate. |
| Test7_Full_court.json | supporting | One-frame court/net coordinate candidate at frame5362; explicit origin=unspecified | Physical line semantics/source-image alignment unverified. Source field absent: do not promote to manually labelled ground truth. No all-frame or airborne3D accuracy; never inject into automatic calibration. |
| Test7_Full_rally.csv | interval_reference | 30 original generated timing records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |
| player_detections.csv | dense_generated_players | 10725 anonymous two-slot generated bottom-center/confidence rows | Legacy first-two detection slots, not physical persistent identity. No reviewed boxes/pose/identity GT; missing cells stay missing; coordinate distances require certificate. |
| win_predictions.csv | interval_reference | 30 original generated timing/outcome/model-support/score records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |

## Generated point disagreement

| Reference | Population | Bound | Count | Mean px | Median px | Min px | Max px | P90 px | P95 px |
|---|---|---|---|---|---|---|---|---|---|
| Test7_Full_ball_filled.csv | all current | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| Test7_Full_ball_filled.csv | fresh detector | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | all current | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | fresh detector | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |

## Point coverage and data quality

| Reference | Count meaning | Count |
|---|---|---|
| Test7_Full_ball_filled.csv | reference_visible=False,current_raw_present=False | 2819 |
| Test7_Full_ball_filled.csv | visibility_unknown | 0 |
| Test7_Full_ball_filled.csv | visible_invalid_numeric | 0 |
| Test7_Full_ball_filled.csv | out_of_image_reference_points | 0 |
| Test7_Full_ball_filled.csv | reference_visible=True,current_raw_present=False | 1399 |
| Test7_Full_ball_filled.csv | reference_visible=True,current_raw_present=True | 6347 |
| Test7_Full_ball_filled.csv | reference_visible=False,current_raw_present=True | 160 |
| player_detections.csv | reference_points | 21019 |
| player_detections.csv | out_of_image_reference_points | 0 |
| player_detections.csv | current_points | 20460 |
| player_detections.csv | missing_or_invalid_slot_coordinates | 431 |

## Byte-identical dense-reference aliases

| Duplicate | Evaluated primary |
|---|---|

## Single-frame court candidates

| File | Frame | Bound | Mean corner px | Max corner px | Limit |
|---|---|---|---|---|---|

## Raw component coverage

| Quantity | Count |
|---|---|
| frames | 10725 |
| raw_shuttle_present | 6507 |
| detector_executed_frames | 4396 |
| person_rows | 20460 |
| scene_telemetry_present | 3669 |
| scene_raw_hypotheses | 13 |
| actual_content_epoch_increments | 15 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 8792 |
| person_propagated_or_unmatched | 11668 |
| pose_present_rows | 16554 |
| pose_current_source_rows | 16554 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 7810 |
| racket_present_rows | 7251 |
| racket_current_source_rows | 7251 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 95 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 95 |

## Track coverage

| Quantity | Count |
|---|---|
| camera_rows | 10725 |
| player_rows | 20388 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 19999 |
| projected_court_on_propagated_box | 11467 |
| racket_rows | 7208 |
| shuttle_rows | 10725 |

## Live event counts

| Quantity | Count |
|---|---|
| calibration | 1 |
| racket_observation_ambiguity | 1517 |
| activity_interval | 89 |
| scene | 14 |
| participant_observation | 91 |
| format_decision | 1 |
| rally_start | 32 |
| rally_end | 32 |
| stroke | 260 |
| contact | 260 |
| shuttle_turn | 17 |
| identity_ambiguity | 43 |
| broadcast_score | 261 |
| match_phase | 1 |

## Outcome and score coverage

| Quantity | Value |
|---|---|
| predicted_rallies | 32 |
| known_winner_outputs | 0 |
| unknown_winner_outputs | 32 |
| canonical_point_events | 0 |
| broadcast_score_observation_events | 261 |
| accuracy_status | unavailable_without_independent_identity_event_outcome_score_labels |

## Predicted stroke counts

| Predicted class | Count |
|---|---|
| unknown | 190 |
| push | 28 |
| lift | 10 |
| net_shot | 9 |
| drop | 16 |
| clear | 2 |
| drive | 3 |
| smash | 2 |

## Actual runtime and resources

| Quantity | Measured value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 766822 |
| parent_failure_inclusive_elapsed_s | unavailable |
| parent_failure_inclusive_source_fps | unavailable |
| neural_only_throughput_fps | unavailable |
| model_loading_time_s | unavailable |
| media_ready_time_s | 1.8445132891647518 |
| model_staging_time_s | 1.7215501703321934 |
| worker_final_cpu_s | 13071.579551 |
| worker_maxrss_bytes | 2869551104 |
| sampled_worker_tree_peak_rss_bytes | 2868633600 |
| sampled_worker_gpu_peak_mib | 2122 |
| sampled_cpu_seconds_max_observed | 13071.26 |
| sampled_cpu_seconds_last_observed | 13071.26 |
| sampled_system_available_ram_min_bytes | 101859426304 |
| sample_count | 561 |
| resource_rows | 561 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 1161.9515156056732 |
| parent_completed_source_fps | 9.230161375889715 |
| worker_elapsed_s | 1155.960730608087 |
| worker_source_fps | 9.27799683502931 |
| component_initialization_including_models_s | 9.178948466666043 |

## Stage invocation timing (scopes can overlap)

| Stage | Calls | Seconds | P50 ms | P95 ms |
|---|---|---|---|---|
| court | 179 | 69.22364204144105 | 305.0210867077112 | 918.2971847709268 |
| content_continuity_and_players | 179 | 542.6101774065755 | 3454.6205289661884 | 3707.9949508886784 |
| shuttle | 177 | 153.85618370072916 | 860.8089960180223 | 990.4655389487743 |
| players | 179 | 52.89488986087963 | 294.1608540713787 | 627.7711002156136 |
| ocr | 179 | 144.95961091900244 | 826.7811699770391 | 999.1248172242194 |

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
| Source SHA256 | 1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c |
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
