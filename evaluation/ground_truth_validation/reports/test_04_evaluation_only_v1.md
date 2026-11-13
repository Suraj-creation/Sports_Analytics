# Test 4 — frozen-main component evaluation

Pipeline: `88aa0ad47d6be8dc1f073d0297efdb430b6ceaa0`. No pipeline changes, tuning or fixes were performed.

All supporting annotations are accounted for; generated references measure agreement. Unknown identity/outcome labels do not establish independently verified accuracy.

[Annotation inventory](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/test_04/annotations/evaluation_only_v1/README.md) · [Complete metrics JSON](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test04/components/component_reference_metrics.json) · [Raw comparisons](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test04/components/reference_raw_details.json) · [Visual evidence](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test04/visual_evidence) · [Diagnosis and proposed fixes](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/reports/evaluation_only_diagnosis_spec.md)

# Manifest-driven component evaluation

Native complete fresh worker and original cache guards passed. Generated references measure agreement, not physical accuracy. Original data and predictions are unchanged.

## Interval reference agreement

| Reference | Declared role | TP | FP | FN | Precision | Recall | F1 | Mean IoU |
|---|---|---|---|---|---|---|---|---|
| Test4_Full.csv | coarse_documented_human_origin_supplied_reference | 43 | 4 | 2 | 0.9148936170212766 | 0.9555555555555556 | 0.9347826086956522 | 0.8170575025616877 |
| Test4_Full_rally.csv | historical_generated_interval_reference_agreement | 38 | 9 | 3 | 0.8085106382978723 | 0.926829268292683 | 0.8636363636363636 | 0.8208291969663278 |
| win_predictions.csv | historical_generated_outcome_interval_reference_agreement | 38 | 9 | 3 | 0.8085106382978723 | 0.926829268292683 | 0.8636363636363636 | 0.8208291969663278 |

## Test4_Full.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 19.093023255813954 | 15.0 | 24.853524386263704 | 77.0 | 36.800000000000004 | 18.348837209302324 | 15.0 |
| end_frame | 27.930232558139537 | 15.0 | 50.26557377546529 | 213.0 | 66.80000000000004 | 0.7209302325581395 | 5.0 |
| start_time_sec | 0.6364341085271342 | 0.5 | 0.8284508128754605 | 2.5666666666667197 | 1.2266666666666795 | 0.6116279069767454 | 0.5 |
| end_time_sec | 0.9310077519379831 | 0.5 | 1.6755191258488469 | 7.100000000000023 | 2.226666666666678 | 0.0240310077519386 | 0.1666666666666572 |
| duration_sec | 1.2434108527131793 | 0.7999999999999972 | 1.9141523785125845 | 7.633333333333326 | 2.4133333333333353 | -0.5875968992248068 | -0.2666666666666657 |

## Test4_Full.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 5 | 0.11627906976744186 | 0.1111111111111111 |
| start | 3 | 0.1 | 6 | 0.13953488372093023 | 0.13333333333333333 |
| start | 5 | 0.16666666666666666 | 8 | 0.18604651162790697 | 0.17777777777777778 |
| start | 10 | 0.3333333333333333 | 15 | 0.3488372093023256 | 0.3333333333333333 |
| start | 15 | 0.5 | 22 | 0.5116279069767442 | 0.4888888888888889 |
| start | 30 | 1.0 | 33 | 0.7674418604651163 | 0.7333333333333333 |
| end | 1 | 0.03333333333333333 | 2 | 0.046511627906976744 | 0.044444444444444446 |
| end | 3 | 0.1 | 3 | 0.06976744186046512 | 0.06666666666666667 |
| end | 5 | 0.16666666666666666 | 8 | 0.18604651162790697 | 0.17777777777777778 |
| end | 10 | 0.3333333333333333 | 16 | 0.37209302325581395 | 0.35555555555555557 |
| end | 15 | 0.5 | 22 | 0.5116279069767442 | 0.4888888888888889 |
| end | 30 | 1.0 | 37 | 0.8604651162790697 | 0.8222222222222222 |

## Test4_Full.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8170575025616877 |
| median_iou | 0.833333333333328 |
| minimum_iou | 0.5503875968992323 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 72.09302325581395 |
| percent IoU strictly above 0.9 | 34.883720930232556 |
| percent IoU strictly above 0.95 | 13.953488372093023 |

Missed reference IDs: 28, 31.
## Test4_Full.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 5 | 2380 | 2449 | FP under complete reference |
| 29 | 12988 | 13085 | FP under complete reference |
| 32 | 13959 | 14072 | FP under complete reference |
| 44 | 19030 | 19178 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test4_Full_rally.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 31.57894736842105 | 19.0 | 43.382023926967726 | 104.0 | 78.70000000000005 | 24.157894736842106 | 14.0 |
| end_frame | 26.973684210526315 | 11.0 | 54.03580684187691 | 248.0 | 59.20000000000002 | -13.868421052631579 | -2.0 |
| start_time_sec | 1.0526315789473635 | 0.6333333333333542 | 1.4460674642322515 | 3.4666666666666686 | 2.6233333333333473 | 0.8052631578947335 | 0.46666666666666856 |
| end_time_sec | 0.8991228070175437 | 0.36666666666667425 | 1.801193561395896 | 8.266666666666666 | 1.9733333333333354 | -0.46228070175438885 | -0.06666666666664867 |
| duration_sec | 1.5780701754386024 | 0.7500000000000071 | 2.4567189168192023 | 9.633333333333326 | 3.3666666666666436 | -1.2675438596491224 | -0.63333333333334 |

## Test4_Full_rally.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 0 | 0.0 | 0.0 |
| start | 3 | 0.1 | 1 | 0.02631578947368421 | 0.024390243902439025 |
| start | 5 | 0.16666666666666666 | 5 | 0.13157894736842105 | 0.12195121951219512 |
| start | 10 | 0.3333333333333333 | 14 | 0.3684210526315789 | 0.34146341463414637 |
| start | 15 | 0.5 | 17 | 0.4473684210526316 | 0.4146341463414634 |
| start | 30 | 1.0 | 24 | 0.631578947368421 | 0.5853658536585366 |
| end | 1 | 0.03333333333333333 | 4 | 0.10526315789473684 | 0.0975609756097561 |
| end | 3 | 0.1 | 7 | 0.18421052631578946 | 0.17073170731707318 |
| end | 5 | 0.16666666666666666 | 8 | 0.21052631578947367 | 0.1951219512195122 |
| end | 10 | 0.3333333333333333 | 19 | 0.5 | 0.4634146341463415 |
| end | 15 | 0.5 | 22 | 0.5789473684210527 | 0.5365853658536586 |
| end | 30 | 1.0 | 31 | 0.8157894736842105 | 0.7560975609756098 |

## Test4_Full_rally.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8208291969663278 |
| median_iou | 0.8617522958550514 |
| minimum_iou | 0.5194029850746246 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 76.3157894736842 |
| percent IoU strictly above 0.9 | 39.473684210526315 |
| percent IoU strictly above 0.95 | 15.789473684210526 |

Missed reference IDs: 1, 14, 25.
## Test4_Full_rally.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 1 | 363 | 435 | FP under complete reference |
| 5 | 2380 | 2449 | FP under complete reference |
| 7 | 2971 | 3143 | FP under complete reference |
| 10 | 4271 | 4336 | FP under complete reference |
| 17 | 6787 | 6978 | FP under complete reference |
| 28 | 12827 | 12879 | FP under complete reference |
| 29 | 12988 | 13085 | FP under complete reference |
| 32 | 13959 | 14072 | FP under complete reference |
| 46 | 19575 | 19702 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## win_predictions.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 31.57894736842105 | 19.0 | 43.382023926967726 | 104.0 | 78.70000000000005 | 24.157894736842106 | 14.0 |
| end_frame | 26.973684210526315 | 11.0 | 54.03580684187691 | 248.0 | 59.20000000000002 | -13.868421052631579 | -2.0 |
| start_time_sec | 1.0526315789473635 | 0.6333333333333542 | 1.4460674642322515 | 3.4666666666666686 | 2.6233333333333473 | 0.8052631578947335 | 0.46666666666666856 |
| end_time_sec | 0.8991228070175437 | 0.36666666666667425 | 1.801193561395896 | 8.266666666666666 | 1.9733333333333354 | -0.46228070175438885 | -0.06666666666664867 |
| duration_sec | 1.5780701754386024 | 0.7500000000000071 | 2.4567189168192023 | 9.633333333333326 | 3.3666666666666436 | -1.2675438596491224 | -0.63333333333334 |

## win_predictions.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 0 | 0.0 | 0.0 |
| start | 3 | 0.1 | 1 | 0.02631578947368421 | 0.024390243902439025 |
| start | 5 | 0.16666666666666666 | 5 | 0.13157894736842105 | 0.12195121951219512 |
| start | 10 | 0.3333333333333333 | 14 | 0.3684210526315789 | 0.34146341463414637 |
| start | 15 | 0.5 | 17 | 0.4473684210526316 | 0.4146341463414634 |
| start | 30 | 1.0 | 24 | 0.631578947368421 | 0.5853658536585366 |
| end | 1 | 0.03333333333333333 | 4 | 0.10526315789473684 | 0.0975609756097561 |
| end | 3 | 0.1 | 7 | 0.18421052631578946 | 0.17073170731707318 |
| end | 5 | 0.16666666666666666 | 8 | 0.21052631578947367 | 0.1951219512195122 |
| end | 10 | 0.3333333333333333 | 19 | 0.5 | 0.4634146341463415 |
| end | 15 | 0.5 | 22 | 0.5789473684210527 | 0.5365853658536586 |
| end | 30 | 1.0 | 31 | 0.8157894736842105 | 0.7560975609756098 |

## win_predictions.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8208291969663278 |
| median_iou | 0.8617522958550514 |
| minimum_iou | 0.5194029850746246 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 76.3157894736842 |
| percent IoU strictly above 0.9 | 39.473684210526315 |
| percent IoU strictly above 0.95 | 15.789473684210526 |

Missed reference IDs: 1, 14, 25.
## win_predictions.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 1 | 363 | 435 | FP under complete reference |
| 5 | 2380 | 2449 | FP under complete reference |
| 7 | 2971 | 3143 | FP under complete reference |
| 10 | 4271 | 4336 | FP under complete reference |
| 17 | 6787 | 6978 | FP under complete reference |
| 28 | 12827 | 12879 | FP under complete reference |
| 29 | 12988 | 13085 | FP under complete reference |
| 32 | 13959 | 14072 | FP under complete reference |
| 46 | 19575 | 19702 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Annotation coverage

| File | Declared role | Purpose | Ambiguity |
|---|---|---|---|
| Test4_Full.csv | interval_reference | 45 supplied coarse time/outcome/score rows; evaluate all nonblank parseable timing spans independently | Legacy documentation describes coarse tables as human-labelled; no per-row review ledger or certified physical A/B/team/official-score binding. Preserve all blanks, raw strings, reason taxonomy and score discontinuities. One ball_types value is not per-contact stroke GT. |
| Test4_Full_ball_filled.csv | dense_generated_shuttle | 20034 generated/filled shuttle image-coordinate, visibility and raw-support rows | Exporter visibility and model support are not reviewed physical visibility/probability. No per-row observed-versus-interpolated flag. Invisible(0,0) stays sentinel. Out-of-image values retained without clipping; no coordinate certificate. |
| Test4_Full_Rev_ball_filled.csv | dense_generated_shuttle | 20034 generated/filled shuttle image-coordinate, visibility and raw-support rows | Exporter visibility and model support are not reviewed physical visibility/probability. No per-row observed-versus-interpolated flag. Invisible(0,0) stays sentinel. Out-of-image values retained without clipping; no coordinate certificate. |
| Test4_Full_court.json | manual_court | One-frame supplied court/net geometry at frame300; source assertion=manual | No source-bound source-image/physical corner-semantics certificate or all-frame geometry GT. Do not inject this reference into automatic inference. Original explicitly says manual, but names no reviewer. |
| Test4_Full_rally.csv | interval_reference | 41 original generated frame/time interval rows; distinct supplied timing family | Historical generated timing output, not independent frame-exact physical rally truth. Compare each supplied timing variant separately; preserve differences from coarse references and aliases. |
| player_detections.csv | dense_generated_players | 20034 canonical-frame anonymous two-slot bottom-center/confidence generated rows | First-two filtered detection slots are not persistent/named physical identities. Missing cells remain missing; no box AP/pose/track-identity GT or coordinate certificate. |
| win_predictions.csv | interval_reference | 41 generated winner/reason/CNN/score rows with frame intervals; preserve semantic counts and compare interval agreement | Earlier ML/rule predictions, not independent winner/reason/score GT. PlayerA=far/PlayerB=near is the producer naming default, not verified physical identity or team membership. |

## Generated point disagreement

| Reference | Population | Bound | Count | Mean px | Median px | Min px | Max px | P90 px | P95 px |
|---|---|---|---|---|---|---|---|---|---|
| Test4_Full_ball_filled.csv | all current | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| Test4_Full_ball_filled.csv | fresh detector | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | all current | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | fresh detector | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |

## Point coverage and data quality

| Reference | Count meaning | Count |
|---|---|---|
| Test4_Full_ball_filled.csv | reference_visible=False,current_raw_present=False | 4138 |
| Test4_Full_ball_filled.csv | visibility_unknown | 0 |
| Test4_Full_ball_filled.csv | visible_invalid_numeric | 0 |
| Test4_Full_ball_filled.csv | out_of_image_reference_points | 34 |
| Test4_Full_ball_filled.csv | reference_visible=True,current_raw_present=False | 2992 |
| Test4_Full_ball_filled.csv | reference_visible=True,current_raw_present=True | 12357 |
| Test4_Full_ball_filled.csv | reference_visible=False,current_raw_present=True | 547 |
| player_detections.csv | reference_points | 37755 |
| player_detections.csv | out_of_image_reference_points | 0 |
| player_detections.csv | current_points | 37191 |
| player_detections.csv | missing_or_invalid_slot_coordinates | 2313 |

## Byte-identical dense-reference aliases

| Duplicate | Evaluated primary |
|---|---|
| Test4_Full_Rev_ball_filled.csv | Test4_Full_ball_filled.csv |

## Single-frame court candidates

| File | Frame | Bound | Mean corner px | Max corner px | Limit |
|---|---|---|---|---|---|
| Test4_Full_court.json | 300 | False | unavailable | unavailable | single-frame manual candidate; not all-frame accuracy |

## Raw component coverage

| Quantity | Count |
|---|---|
| frames | 20034 |
| raw_shuttle_present | 12904 |
| detector_executed_frames | 8107 |
| person_rows | 37191 |
| scene_telemetry_present | 3687 |
| scene_raw_hypotheses | 3 |
| actual_content_epoch_increments | 3 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 16188 |
| person_propagated_or_unmatched | 21003 |
| pose_present_rows | 30707 |
| pose_current_source_rows | 30707 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 14595 |
| racket_present_rows | 13230 |
| racket_current_source_rows | 13230 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 108 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 108 |

## Track coverage

| Quantity | Count |
|---|---|
| camera_rows | 20034 |
| player_rows | 37019 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 36645 |
| projected_court_on_propagated_box | 20771 |
| racket_rows | 13134 |
| shuttle_rows | 20034 |

## Live event counts

| Quantity | Count |
|---|---|
| calibration | 1 |
| racket_observation_ambiguity | 2296 |
| activity_interval | 142 |
| scene | 62 |
| participant_observation | 120 |
| format_decision | 1 |
| rally_start | 47 |
| stroke | 537 |
| contact | 537 |
| rally_end | 47 |
| identity_ambiguity | 78 |
| shuttle_turn | 28 |
| broadcast_score | 504 |
| match_phase | 1 |
| highlight | 1 |

## Outcome and score coverage

| Quantity | Value |
|---|---|
| predicted_rallies | 47 |
| known_winner_outputs | 0 |
| unknown_winner_outputs | 47 |
| canonical_point_events | 0 |
| broadcast_score_observation_events | 504 |
| accuracy_status | unavailable_without_independent_identity_event_outcome_score_labels |

## Predicted stroke counts

| Predicted class | Count |
|---|---|
| unknown | 367 |
| push | 82 |
| lift | 24 |
| net_shot | 24 |
| drive | 7 |
| drop | 24 |
| clear | 7 |
| smash | 2 |

## Actual runtime and resources

| Quantity | Measured value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 733780 |
| parent_failure_inclusive_elapsed_s | unavailable |
| parent_failure_inclusive_source_fps | unavailable |
| neural_only_throughput_fps | unavailable |
| model_loading_time_s | unavailable |
| media_ready_time_s | 2.1521872570738196 |
| model_staging_time_s | 1.717642413917929 |
| worker_final_cpu_s | 24030.193884 |
| worker_maxrss_bytes | 2846334976 |
| sampled_worker_tree_peak_rss_bytes | 2776064000 |
| sampled_worker_gpu_peak_mib | 2124 |
| sampled_cpu_seconds_max_observed | 24030.58 |
| sampled_cpu_seconds_last_observed | 24030.58 |
| sampled_system_available_ram_min_bytes | 101824700416 |
| sample_count | 1078 |
| resource_rows | 1078 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 2233.926953815855 |
| parent_completed_source_fps | 8.968064047832526 |
| worker_elapsed_s | 2225.778536465019 |
| worker_source_fps | 9.00089549422019 |
| component_initialization_including_models_s | 9.3768909573555 |

## Stage invocation timing (scopes can overlap)

| Stage | Calls | Seconds | P50 ms | P95 ms |
|---|---|---|---|---|
| court | 334 | 97.7614757665433 | 227.79153031297028 | 589.3188660731536 |
| content_continuity_and_players | 334 | 1011.9042906849645 | 3481.620617210865 | 3741.3544880691916 |
| shuttle | 332 | 293.9372360520065 | 872.8186003863811 | 1018.3725423878059 |
| players | 334 | 111.73298476682976 | 334.9065980874002 | 684.2707905219867 |
| ocr | 334 | 266.976416092366 | 812.0725438930094 | 950.2290744567288 |

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
| Source SHA256 | adff61dad4741ea6e8220c5d3292ddb0578b3c91b9e724f49b6f6608203558ed |
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
