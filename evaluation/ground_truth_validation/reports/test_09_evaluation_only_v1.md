# Test 9 — frozen-main component evaluation

Pipeline: `88aa0ad47d6be8dc1f073d0297efdb430b6ceaa0`. No pipeline changes, tuning or fixes were performed.

All supporting annotations are accounted for; generated references measure agreement. Unknown identity/outcome labels do not establish independently verified accuracy.

[Annotation inventory](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/test_09/annotations/evaluation_only_v1/README.md) · [Complete metrics JSON](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test09/components/component_reference_metrics.json) · [Raw comparisons](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test09/components/reference_raw_details.json) · [Visual evidence](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test09/visual_evidence) · [Diagnosis and proposed fixes](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/reports/evaluation_only_diagnosis_spec.md)

# Manifest-driven component evaluation

Native complete fresh worker and original cache guards passed. Generated references measure agreement, not physical accuracy. Original data and predictions are unchanged.

## Interval reference agreement

| Reference | Declared role | TP | FP | FN | Precision | Recall | F1 | Mean IoU |
|---|---|---|---|---|---|---|---|---|
| Test9_Full.csv | coarse_documented_human_origin_supplied_reference | 71 | 13 | 7 | 0.8452380952380952 | 0.9102564102564102 | 0.8765432098765432 | 0.8163960879316249 |
| Test9_Full_rally.csv | historical_generated_interval_reference_agreement | 69 | 15 | 13 | 0.8214285714285714 | 0.8414634146341463 | 0.8313253012048193 | 0.8631654499972389 |
| win_predictions.csv | historical_generated_outcome_interval_reference_agreement | 69 | 15 | 13 | 0.8214285714285714 | 0.8414634146341463 | 0.8313253012048193 | 0.8631654499972389 |

## Test9_Full.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 26.929577464788732 | 15.0 | 47.75878357381713 | 210.0 | 41.0 | 24.197183098591548 | 15.0 |
| end_frame | 24.450704225352112 | 16.0 | 42.94083712455716 | 189.0 | 42.0 | 3.464788732394366 | 7.0 |
| start_time_sec | 0.8976525821596251 | 0.5 | 1.59195945246057 | 7.0 | 1.3666666666666742 | 0.8065727699530517 | 0.5 |
| end_time_sec | 0.8150234741784018 | 0.5333333333333314 | 1.43136123748524 | 6.2999999999999545 | 1.3999999999999773 | 0.11549295774647914 | 0.23333333333333428 |
| duration_sec | 1.2600938967136122 | 0.6999999999999318 | 2.0722021883091344 | 6.86666666666666 | 4.133333333333439 | -0.6910798122065727 | -0.33333333333337123 |

## Test9_Full.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.014084507042253521 | 0.01282051282051282 |
| start | 3 | 0.1 | 5 | 0.07042253521126761 | 0.0641025641025641 |
| start | 5 | 0.16666666666666666 | 6 | 0.08450704225352113 | 0.07692307692307693 |
| start | 10 | 0.3333333333333333 | 21 | 0.29577464788732394 | 0.2692307692307692 |
| start | 15 | 0.5 | 36 | 0.5070422535211268 | 0.46153846153846156 |
| start | 30 | 1.0 | 58 | 0.8169014084507042 | 0.7435897435897436 |
| end | 1 | 0.03333333333333333 | 8 | 0.11267605633802817 | 0.10256410256410256 |
| end | 3 | 0.1 | 11 | 0.15492957746478872 | 0.14102564102564102 |
| end | 5 | 0.16666666666666666 | 18 | 0.2535211267605634 | 0.23076923076923078 |
| end | 10 | 0.3333333333333333 | 27 | 0.38028169014084506 | 0.34615384615384615 |
| end | 15 | 0.5 | 34 | 0.4788732394366197 | 0.4358974358974359 |
| end | 30 | 1.0 | 57 | 0.8028169014084507 | 0.7307692307692307 |

## Test9_Full.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8163960879316249 |
| median_iou | 0.8613138686131402 |
| minimum_iou | 0.5000000000000194 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 76.05633802816901 |
| percent IoU strictly above 0.9 | 28.169014084507044 |
| percent IoU strictly above 0.95 | 9.859154929577464 |

Missed reference IDs: 10, 24, 32, 33, 40, 41, 68.
## Test9_Full.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 9 | 3004 | 3161 | FP under complete reference |
| 11 | 3585 | 3664 | FP under complete reference |
| 14 | 4495 | 4618 | FP under complete reference |
| 33 | 13026 | 13225 | FP under complete reference |
| 34 | 13259 | 13468 | FP under complete reference |
| 35 | 13715 | 13770 | FP under complete reference |
| 36 | 13820 | 13910 | FP under complete reference |
| 41 | 15827 | 15959 | FP under complete reference |
| 44 | 16587 | 16719 | FP under complete reference |
| 45 | 17819 | 18045 | FP under complete reference |
| 62 | 24508 | 24587 | FP under complete reference |
| 73 | 28542 | 28609 | FP under complete reference |
| 83 | 32913 | 33023 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test9_Full_rally.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 22.942028985507246 | 6.0 | 55.7537286723459 | 286.0 | 35.40000000000002 | 3.1449275362318843 | 5.0 |
| end_frame | 19.043478260869566 | 9.0 | 40.188324788119274 | 184.0 | 30.80000000000001 | -6.115942028985507 | -3.0 |
| start_time_sec | 0.7647342995169129 | 0.20000000000004547 | 1.8584576224115277 | 9.533333333333303 | 1.1799999999999962 | 0.1048309178744045 | 0.16666666666674246 |
| end_time_sec | 0.6347826086956545 | 0.29999999999999716 | 1.3396108262706508 | 6.133333333333326 | 1.0266666666666655 | -0.20386473429951407 | -0.10000000000002274 |
| duration_sec | 1.2613526570048412 | 0.6333333333333258 | 2.2214116879314916 | 9.033333333333303 | 4.1800000000000885 | -0.3086956521739186 | -0.39999999999997726 |

## Test9_Full_rally.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 9 | 0.13043478260869565 | 0.10975609756097561 |
| start | 3 | 0.1 | 15 | 0.21739130434782608 | 0.18292682926829268 |
| start | 5 | 0.16666666666666666 | 31 | 0.4492753623188406 | 0.3780487804878049 |
| start | 10 | 0.3333333333333333 | 50 | 0.7246376811594203 | 0.6097560975609756 |
| start | 15 | 0.5 | 54 | 0.782608695652174 | 0.6585365853658537 |
| start | 30 | 1.0 | 59 | 0.855072463768116 | 0.7195121951219512 |
| end | 1 | 0.03333333333333333 | 11 | 0.15942028985507245 | 0.13414634146341464 |
| end | 3 | 0.1 | 17 | 0.2463768115942029 | 0.2073170731707317 |
| end | 5 | 0.16666666666666666 | 27 | 0.391304347826087 | 0.32926829268292684 |
| end | 10 | 0.3333333333333333 | 38 | 0.5507246376811594 | 0.4634146341463415 |
| end | 15 | 0.5 | 47 | 0.6811594202898551 | 0.573170731707317 |
| end | 30 | 1.0 | 62 | 0.8985507246376812 | 0.7560975609756098 |

## Test9_Full_rally.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8631654499972389 |
| median_iou | 0.9166666666666674 |
| minimum_iou | 0.5222222222222237 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 81.15942028985508 |
| percent IoU strictly above 0.9 | 57.971014492753625 |
| percent IoU strictly above 0.95 | 26.08695652173913 |

Missed reference IDs: 5, 7, 16, 24, 32, 33, 41, 42, 46, 50, 52, 55, 71.
## Test9_Full_rally.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 5 | 1694 | 1923 | FP under complete reference |
| 6 | 1962 | 2279 | FP under complete reference |
| 8 | 2733 | 2887 | FP under complete reference |
| 9 | 3004 | 3161 | FP under complete reference |
| 14 | 4495 | 4618 | FP under complete reference |
| 33 | 13026 | 13225 | FP under complete reference |
| 34 | 13259 | 13468 | FP under complete reference |
| 35 | 13715 | 13770 | FP under complete reference |
| 36 | 13820 | 13910 | FP under complete reference |
| 41 | 15827 | 15959 | FP under complete reference |
| 48 | 18807 | 19094 | FP under complete reference |
| 49 | 19155 | 19487 | FP under complete reference |
| 54 | 20896 | 20968 | FP under complete reference |
| 62 | 24508 | 24587 | FP under complete reference |
| 83 | 32913 | 33023 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## win_predictions.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 22.942028985507246 | 6.0 | 55.7537286723459 | 286.0 | 35.40000000000002 | 3.1449275362318843 | 5.0 |
| end_frame | 19.043478260869566 | 9.0 | 40.188324788119274 | 184.0 | 30.80000000000001 | -6.115942028985507 | -3.0 |
| start_time_sec | 0.7647342995169129 | 0.20000000000004547 | 1.8584576224115277 | 9.533333333333303 | 1.1799999999999962 | 0.1048309178744045 | 0.16666666666674246 |
| end_time_sec | 0.6347826086956545 | 0.29999999999999716 | 1.3396108262706508 | 6.133333333333326 | 1.0266666666666655 | -0.20386473429951407 | -0.10000000000002274 |
| duration_sec | 1.2613526570048412 | 0.6333333333333258 | 2.2214116879314916 | 9.033333333333303 | 4.1800000000000885 | -0.3086956521739186 | -0.39999999999997726 |

## win_predictions.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 9 | 0.13043478260869565 | 0.10975609756097561 |
| start | 3 | 0.1 | 15 | 0.21739130434782608 | 0.18292682926829268 |
| start | 5 | 0.16666666666666666 | 31 | 0.4492753623188406 | 0.3780487804878049 |
| start | 10 | 0.3333333333333333 | 50 | 0.7246376811594203 | 0.6097560975609756 |
| start | 15 | 0.5 | 54 | 0.782608695652174 | 0.6585365853658537 |
| start | 30 | 1.0 | 59 | 0.855072463768116 | 0.7195121951219512 |
| end | 1 | 0.03333333333333333 | 11 | 0.15942028985507245 | 0.13414634146341464 |
| end | 3 | 0.1 | 17 | 0.2463768115942029 | 0.2073170731707317 |
| end | 5 | 0.16666666666666666 | 27 | 0.391304347826087 | 0.32926829268292684 |
| end | 10 | 0.3333333333333333 | 38 | 0.5507246376811594 | 0.4634146341463415 |
| end | 15 | 0.5 | 47 | 0.6811594202898551 | 0.573170731707317 |
| end | 30 | 1.0 | 62 | 0.8985507246376812 | 0.7560975609756098 |

## win_predictions.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8631654499972389 |
| median_iou | 0.9166666666666674 |
| minimum_iou | 0.5222222222222237 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 81.15942028985508 |
| percent IoU strictly above 0.9 | 57.971014492753625 |
| percent IoU strictly above 0.95 | 26.08695652173913 |

Missed reference IDs: 5, 7, 16, 24, 32, 33, 41, 42, 46, 50, 52, 55, 71.
## win_predictions.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 5 | 1694 | 1923 | FP under complete reference |
| 6 | 1962 | 2279 | FP under complete reference |
| 8 | 2733 | 2887 | FP under complete reference |
| 9 | 3004 | 3161 | FP under complete reference |
| 14 | 4495 | 4618 | FP under complete reference |
| 33 | 13026 | 13225 | FP under complete reference |
| 34 | 13259 | 13468 | FP under complete reference |
| 35 | 13715 | 13770 | FP under complete reference |
| 36 | 13820 | 13910 | FP under complete reference |
| 41 | 15827 | 15959 | FP under complete reference |
| 48 | 18807 | 19094 | FP under complete reference |
| 49 | 19155 | 19487 | FP under complete reference |
| 54 | 20896 | 20968 | FP under complete reference |
| 62 | 24508 | 24587 | FP under complete reference |
| 83 | 32913 | 33023 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Annotation coverage

| File | Declared role | Purpose | Ambiguity |
|---|---|---|---|
| Test9_Full.csv | interval_reference | 88 supplied coarse clock/outcome/score records; all parseable nonblank timing retained | Documented legacy human-origin reference candidate; no certified physical A/B/team/official-score or exhaustive shot binding. Preserve blanks, raw taxonomy, score jumps and label conflicts. |
| Test9_Full_ball_filled.csv | dense_generated_shuttle | 33157 generated/filled shuttle coordinate and visibility rows; raw model-support column retained | No reviewed physical visibility/location GT or observed-versus-filled flag. Preserve out-of-image coordinates and invisible(0,0) sentinels. Missing confidence is unavailable, never synthesized; no coordinate certificate. |
| Test9_Full_court.json | manual_court | One-frame court/net coordinate candidate at frame300; explicit origin=manual | Physical line semantics/source-image alignment unverified. Original explicitly says manual but no named reviewer. No all-frame or airborne3D accuracy; never inject into automatic calibration. |
| Test9_Full_rally.csv | interval_reference | 82 original generated timing records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |
| player_detections.csv | dense_generated_players | 33157 anonymous two-slot generated bottom-center/confidence rows | Legacy first-two detection slots, not physical persistent identity. No reviewed boxes/pose/identity GT; missing cells stay missing; coordinate distances require certificate. |
| win_predictions.csv | interval_reference | 82 original generated timing/outcome/model-support/score records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |

## Generated point disagreement

| Reference | Population | Bound | Count | Mean px | Median px | Min px | Max px | P90 px | P95 px |
|---|---|---|---|---|---|---|---|---|---|
| Test9_Full_ball_filled.csv | all current | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| Test9_Full_ball_filled.csv | fresh detector | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | all current | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | fresh detector | False | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |

## Point coverage and data quality

| Reference | Count meaning | Count |
|---|---|---|
| Test9_Full_ball_filled.csv | reference_visible=False,current_raw_present=False | 7466 |
| Test9_Full_ball_filled.csv | visibility_unknown | 0 |
| Test9_Full_ball_filled.csv | visible_invalid_numeric | 0 |
| Test9_Full_ball_filled.csv | out_of_image_reference_points | 0 |
| Test9_Full_ball_filled.csv | reference_visible=True,current_raw_present=False | 4674 |
| Test9_Full_ball_filled.csv | reference_visible=True,current_raw_present=True | 20761 |
| Test9_Full_ball_filled.csv | reference_visible=False,current_raw_present=True | 256 |
| player_detections.csv | reference_points | 63606 |
| player_detections.csv | out_of_image_reference_points | 0 |
| player_detections.csv | current_points | 64400 |
| player_detections.csv | missing_or_invalid_slot_coordinates | 2708 |

## Byte-identical dense-reference aliases

| Duplicate | Evaluated primary |
|---|---|

## Single-frame court candidates

| File | Frame | Bound | Mean corner px | Max corner px | Limit |
|---|---|---|---|---|---|
| Test9_Full_court.json | 300 | False | unavailable | unavailable | single-frame manual candidate; not all-frame accuracy |

## Raw component coverage

| Quantity | Count |
|---|---|
| frames | 33157 |
| raw_shuttle_present | 21017 |
| detector_executed_frames | 14135 |
| person_rows | 64400 |
| scene_telemetry_present | 3816 |
| scene_raw_hypotheses | 47 |
| actual_content_epoch_increments | 53 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 28267 |
| person_propagated_or_unmatched | 36133 |
| pose_present_rows | 53857 |
| pose_current_source_rows | 53857 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 25672 |
| racket_present_rows | 25444 |
| racket_current_source_rows | 25444 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 247 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 247 |

## Track coverage

| Quantity | Count |
|---|---|
| camera_rows | 33157 |
| player_rows | 64354 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 63687 |
| projected_court_on_propagated_box | 35803 |
| racket_rows | 25417 |
| shuttle_rows | 33157 |

## Live event counts

| Quantity | Count |
|---|---|
| calibration | 1 |
| racket_observation_ambiguity | 3854 |
| activity_interval | 178 |
| scene | 5 |
| participant_observation | 240 |
| format_decision | 1 |
| rally_start | 84 |
| rally_end | 84 |
| stroke | 909 |
| contact | 909 |
| identity_ambiguity | 69 |
| broadcast_score | 956 |
| match_phase | 1 |
| shuttle_turn | 31 |
| highlight | 4 |

## Outcome and score coverage

| Quantity | Value |
|---|---|
| predicted_rallies | 84 |
| known_winner_outputs | 0 |
| unknown_winner_outputs | 84 |
| canonical_point_events | 0 |
| broadcast_score_observation_events | 956 |
| accuracy_status | unavailable_without_independent_identity_event_outcome_score_labels |

## Predicted stroke counts

| Predicted class | Count |
|---|---|
| unknown | 669 |
| push | 110 |
| net_shot | 29 |
| drop | 26 |
| lift | 49 |
| smash | 5 |
| clear | 9 |
| drive | 12 |

## Actual runtime and resources

| Quantity | Measured value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 778482 |
| parent_failure_inclusive_elapsed_s | unavailable |
| parent_failure_inclusive_source_fps | unavailable |
| neural_only_throughput_fps | unavailable |
| model_loading_time_s | unavailable |
| media_ready_time_s | 2.5281944987364113 |
| model_staging_time_s | 1.68307946017012 |
| worker_final_cpu_s | 40822.286298 |
| worker_maxrss_bytes | 2868314112 |
| sampled_worker_tree_peak_rss_bytes | 3017064448 |
| sampled_worker_gpu_peak_mib | 2124 |
| sampled_cpu_seconds_max_observed | 40821.66 |
| sampled_cpu_seconds_last_observed | 40821.66 |
| sampled_system_available_ram_min_bytes | 98765844480 |
| sample_count | 1967 |
| resource_rows | 1967 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 4074.8849226552993 |
| parent_completed_source_fps | 8.13691690178923 |
| worker_elapsed_s | 4064.123054103926 |
| worker_source_fps | 8.158463599304227 |
| component_initialization_including_models_s | 9.148773774039 |

## Stage invocation timing (scopes can overlap)

| Stage | Calls | Seconds | P50 ms | P95 ms |
|---|---|---|---|---|
| court | 553 | 201.69770676409826 | 307.1437948383391 | 408.96198032423825 |
| content_continuity_and_players | 553 | 1833.482719358988 | 3658.9401769451797 | 4062.214687280357 |
| shuttle | 540 | 469.4486003536731 | 853.4226580522954 | 1034.0435494435944 |
| players | 553 | 106.46273038024083 | 199.70127567648888 | 394.5364694111047 |
| ocr | 553 | 417.09136674785987 | 748.4102929010987 | 1012.4802804552015 |

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
| Source SHA256 | f2aabeb9610c437b38b840ae45885b4b71854702a6b30dd4aee4c54d1417dd4a |
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
