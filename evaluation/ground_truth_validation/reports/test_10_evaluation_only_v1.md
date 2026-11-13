# Test10 — complete six-annotation evaluation

Fresh full inference on88aa0ad; only the prior frame-count deadline was extended in the separate preparation process. Original failure is retained. Generated references measure diagnostic agreement; unsupported accuracy remains unavailable.

# Manifest-driven component evaluation

Native complete fresh worker and original cache guards passed. Generated references measure agreement, not physical accuracy. Original data and predictions are unchanged.

## Interval reference agreement

| Reference | Declared role | TP | FP | FN | Precision | Recall | F1 | Mean IoU |
|---|---|---|---|---|---|---|---|---|
| Test10_Full.csv | coarse_documented_human_origin_supplied_reference | 88 | 10 | 8 | 0.8979591836734694 | 0.9166666666666666 | 0.9072164948453608 | 0.8269216234816164 |
| Test10_Full_rally.csv | historical_generated_interval_reference_agreement | 85 | 13 | 8 | 0.8673469387755102 | 0.9139784946236559 | 0.8900523560209425 | 0.8452629496877632 |
| win_predictions.csv | historical_generated_outcome_interval_reference_agreement | 85 | 13 | 8 | 0.8673469387755102 | 0.9139784946236559 | 0.8900523560209425 | 0.8452629496877632 |

## Test10_Full.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 20.454545454545453 | 15.0 | 35.89694846488917 | 216.0 | 30.299999999999997 | 17.727272727272727 | 14.5 |
| end_frame | 20.795454545454547 | 15.0 | 29.8895694789397 | 163.0 | 43.0 | 5.954545454545454 | 11.0 |
| start_time_sec | 0.6818181818181739 | 0.5 | 1.1965649488296382 | 7.2000000000000455 | 1.0100000000000078 | 0.5909090909090892 | 0.4833333333333485 |
| end_time_sec | 0.6931818181818128 | 0.5 | 0.9963189826313187 | 5.43333333333328 | 1.4333333333333371 | 0.19848484848484632 | 0.36666666666661385 |
| duration_sec | 0.8416666666666663 | 0.5333333333333243 | 1.3927844358867882 | 6.7000000000000455 | 1.7099999999999842 | -0.3924242424242428 | -0.1500000000000341 |

## Test10_Full.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 6 | 0.06818181818181818 | 0.0625 |
| start | 3 | 0.1 | 11 | 0.125 | 0.11458333333333333 |
| start | 5 | 0.16666666666666666 | 16 | 0.18181818181818182 | 0.16666666666666666 |
| start | 10 | 0.3333333333333333 | 29 | 0.32954545454545453 | 0.3020833333333333 |
| start | 15 | 0.5 | 45 | 0.5113636363636364 | 0.46875 |
| start | 30 | 1.0 | 79 | 0.8977272727272727 | 0.8229166666666666 |
| end | 1 | 0.03333333333333333 | 7 | 0.07954545454545454 | 0.07291666666666667 |
| end | 3 | 0.1 | 11 | 0.125 | 0.11458333333333333 |
| end | 5 | 0.16666666666666666 | 12 | 0.13636363636363635 | 0.125 |
| end | 10 | 0.3333333333333333 | 25 | 0.2840909090909091 | 0.2604166666666667 |
| end | 15 | 0.5 | 45 | 0.5113636363636364 | 0.46875 |
| end | 30 | 1.0 | 71 | 0.8068181818181818 | 0.7395833333333334 |

## Test10_Full.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8269216234816164 |
| median_iou | 0.8593929391504012 |
| minimum_iou | 0.5064935064935068 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 76.13636363636364 |
| percent IoU strictly above 0.9 | 30.681818181818183 |
| percent IoU strictly above 0.95 | 12.5 |

Missed reference IDs: 4, 22, 25, 29, 41, 57, 80, 88.
## Test10_Full.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 4 | 1091 | 1199 | FP under complete reference |
| 24 | 8741 | 9287 | FP under complete reference |
| 28 | 11073 | 11131 | FP under complete reference |
| 40 | 15556 | 15662 | FP under complete reference |
| 44 | 17174 | 17340 | FP under complete reference |
| 61 | 24185 | 24347 | FP under complete reference |
| 68 | 26206 | 26355 | FP under complete reference |
| 81 | 31584 | 31725 | FP under complete reference |
| 89 | 34122 | 34223 | FP under complete reference |
| 90 | 34246 | 34335 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test10_Full_rally.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 24.32941176470588 | 7.0 | 50.396545166369116 | 206.0 | 52.800000000000026 | 16.0 | 6.0 |
| end_frame | 17.8 | 7.0 | 30.57392199051919 | 136.0 | 45.60000000000001 | -10.364705882352942 | -2.0 |
| start_time_sec | 0.8109803921568599 | 0.2333333333333485 | 1.6798848388789718 | 6.866666666666788 | 1.7599999999999918 | 0.533333333333332 | 0.20000000000004547 |
| end_time_sec | 0.5933333333333356 | 0.2333333333333485 | 1.0191307330173058 | 4.533333333333303 | 1.519999999999982 | -0.3454901960784374 | -0.06666666666671972 |
| duration_sec | 1.2403921568627414 | 0.6666666666666572 | 2.0576431723786843 | 7.43333333333328 | 3.1800000000000224 | -0.8788235294117692 | -0.5666666666666629 |

## Test10_Full_rally.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 7 | 0.08235294117647059 | 0.07526881720430108 |
| start | 3 | 0.1 | 14 | 0.16470588235294117 | 0.15053763440860216 |
| start | 5 | 0.16666666666666666 | 30 | 0.35294117647058826 | 0.3225806451612903 |
| start | 10 | 0.3333333333333333 | 53 | 0.6235294117647059 | 0.5698924731182796 |
| start | 15 | 0.5 | 61 | 0.7176470588235294 | 0.6559139784946236 |
| start | 30 | 1.0 | 69 | 0.8117647058823529 | 0.7419354838709677 |
| end | 1 | 0.03333333333333333 | 11 | 0.12941176470588237 | 0.11827956989247312 |
| end | 3 | 0.1 | 19 | 0.2235294117647059 | 0.20430107526881722 |
| end | 5 | 0.16666666666666666 | 34 | 0.4 | 0.3655913978494624 |
| end | 10 | 0.3333333333333333 | 48 | 0.5647058823529412 | 0.5161290322580645 |
| end | 15 | 0.5 | 57 | 0.6705882352941176 | 0.6129032258064516 |
| end | 30 | 1.0 | 70 | 0.8235294117647058 | 0.7526881720430108 |

## Test10_Full_rally.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8452629496877632 |
| median_iou | 0.8984771573603954 |
| minimum_iou | 0.5100671140939599 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 77.6470588235294 |
| percent IoU strictly above 0.9 | 49.411764705882355 |
| percent IoU strictly above 0.95 | 23.529411764705884 |

Missed reference IDs: 9, 15, 30, 37, 40, 43, 55, 85.
## Test10_Full_rally.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 28 | 11073 | 11131 | FP under complete reference |
| 32 | 12209 | 12280 | FP under complete reference |
| 33 | 12313 | 12471 | FP under complete reference |
| 37 | 14065 | 14227 | FP under complete reference |
| 40 | 15556 | 15662 | FP under complete reference |
| 43 | 16643 | 17055 | FP under complete reference |
| 44 | 17174 | 17340 | FP under complete reference |
| 45 | 17376 | 17655 | FP under complete reference |
| 61 | 24185 | 24347 | FP under complete reference |
| 68 | 26206 | 26355 | FP under complete reference |
| 85 | 32693 | 32831 | FP under complete reference |
| 89 | 34122 | 34223 | FP under complete reference |
| 90 | 34246 | 34335 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## win_predictions.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 24.32941176470588 | 7.0 | 50.396545166369116 | 206.0 | 52.800000000000026 | 16.0 | 6.0 |
| end_frame | 17.8 | 7.0 | 30.57392199051919 | 136.0 | 45.60000000000001 | -10.364705882352942 | -2.0 |
| start_time_sec | 0.8109803921568599 | 0.2333333333333485 | 1.6798848388789718 | 6.866666666666788 | 1.7599999999999918 | 0.533333333333332 | 0.20000000000004547 |
| end_time_sec | 0.5933333333333356 | 0.2333333333333485 | 1.0191307330173058 | 4.533333333333303 | 1.519999999999982 | -0.3454901960784374 | -0.06666666666671972 |
| duration_sec | 1.2403921568627414 | 0.6666666666666572 | 2.0576431723786843 | 7.43333333333328 | 3.1800000000000224 | -0.8788235294117692 | -0.5666666666666629 |

## win_predictions.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 7 | 0.08235294117647059 | 0.07526881720430108 |
| start | 3 | 0.1 | 14 | 0.16470588235294117 | 0.15053763440860216 |
| start | 5 | 0.16666666666666666 | 30 | 0.35294117647058826 | 0.3225806451612903 |
| start | 10 | 0.3333333333333333 | 53 | 0.6235294117647059 | 0.5698924731182796 |
| start | 15 | 0.5 | 61 | 0.7176470588235294 | 0.6559139784946236 |
| start | 30 | 1.0 | 69 | 0.8117647058823529 | 0.7419354838709677 |
| end | 1 | 0.03333333333333333 | 11 | 0.12941176470588237 | 0.11827956989247312 |
| end | 3 | 0.1 | 19 | 0.2235294117647059 | 0.20430107526881722 |
| end | 5 | 0.16666666666666666 | 34 | 0.4 | 0.3655913978494624 |
| end | 10 | 0.3333333333333333 | 48 | 0.5647058823529412 | 0.5161290322580645 |
| end | 15 | 0.5 | 57 | 0.6705882352941176 | 0.6129032258064516 |
| end | 30 | 1.0 | 70 | 0.8235294117647058 | 0.7526881720430108 |

## win_predictions.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8452629496877632 |
| median_iou | 0.8984771573603954 |
| minimum_iou | 0.5100671140939599 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 77.6470588235294 |
| percent IoU strictly above 0.9 | 49.411764705882355 |
| percent IoU strictly above 0.95 | 23.529411764705884 |

Missed reference IDs: 9, 15, 30, 37, 40, 43, 55, 85.
## win_predictions.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 28 | 11073 | 11131 | FP under complete reference |
| 32 | 12209 | 12280 | FP under complete reference |
| 33 | 12313 | 12471 | FP under complete reference |
| 37 | 14065 | 14227 | FP under complete reference |
| 40 | 15556 | 15662 | FP under complete reference |
| 43 | 16643 | 17055 | FP under complete reference |
| 44 | 17174 | 17340 | FP under complete reference |
| 45 | 17376 | 17655 | FP under complete reference |
| 61 | 24185 | 24347 | FP under complete reference |
| 68 | 26206 | 26355 | FP under complete reference |
| 85 | 32693 | 32831 | FP under complete reference |
| 89 | 34122 | 34223 | FP under complete reference |
| 90 | 34246 | 34335 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Annotation coverage

| File | Declared role | Purpose | Ambiguity |
|---|---|---|---|
| Test10_Full.csv | interval_reference | 101 supplied coarse clock/outcome/score records; preserve blanks and all valid timing spans | Documented legacy human-origin reference candidate; no certified physical A/B/team/official-score or exhaustive shot binding. Preserve blanks, raw taxonomy, score jumps and label conflicts. |
| Test10_Full_ball_filled.csv | dense_generated_shuttle | 37133 generated/filled shuttle coordinate,visibility,uncalibrated-support rows | No reviewed physical visibility/location GT or observed-versus-filled flag. Preserve out-of-image coordinates and invisible(0,0) sentinels. Missing confidence is unavailable, never synthesized; no coordinate certificate. |
| Test10_Full_court.json | manual_court | One-frame supplied court/net coordinate candidate at frame300; explicit origin=manual | Physical line semantics/source-image alignment unverified. Original explicitly says manual but no named reviewer. No all-frame or airborne3D accuracy; never inject into automatic calibration. |
| Test10_Full_rally.csv | interval_reference | 93 original generated timing records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |
| player_detections.csv | dense_generated_players | 37133 anonymous two-slot generated bottom-center/confidence rows | Legacy first-two detection slots, not physical persistent identity. No reviewed boxes/pose/identity GT; missing cells stay missing; coordinate distances require certificate. |
| win_predictions.csv | interval_reference | 93 original generated timing/outcome/model-support/score records | Generated legacy predictions, not independent physical timing/outcome GT. Keep all variant boundaries and model fields distinct; no forced winner, identity or score mapping. |

## Generated point disagreement

| Reference | Population | Bound | Count | Mean px | Median px | Min px | Max px | P90 px | P95 px |
|---|---|---|---|---|---|---|---|---|---|
| Test10_Full_ball_filled.csv | all current | True | 24406 | 4.286132561265727 | 1.485230030325421 | 0.011112929011417286 | 564.9779874074968 | 2.747172608501635 | 3.465958572006019 |
| Test10_Full_ball_filled.csv | fresh detector | True | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | all current | True | 71946 | 2.7896052695520415 | 1.5544062291361098 | 0.001362397112155134 | 86.41022242701837 | 6.604708074028768 | 9.545306606853698 |
| player_detections.csv | fresh detector | True | 32540 | 1.6046668852074644 | 1.200508815654838 | 0.001362397112155134 | 86.41022242701837 | 2.7564869370379266 | 3.9477127843940694 |

## Point coverage and data quality

| Reference | Count meaning | Count |
|---|---|---|
| Test10_Full_ball_filled.csv | reference_visible=False,current_raw_present=False | 6982 |
| Test10_Full_ball_filled.csv | visibility_unknown | 0 |
| Test10_Full_ball_filled.csv | visible_invalid_numeric | 0 |
| Test10_Full_ball_filled.csv | out_of_image_reference_points | 0 |
| Test10_Full_ball_filled.csv | reference_visible=True,current_raw_present=False | 5088 |
| Test10_Full_ball_filled.csv | reference_visible=True,current_raw_present=True | 24406 |
| Test10_Full_ball_filled.csv | reference_visible=False,current_raw_present=True | 657 |
| player_detections.csv | reference_points | 72241 |
| player_detections.csv | out_of_image_reference_points | 0 |
| player_detections.csv | current_points | 73521 |
| player_detections.csv | all_current_unmatched_reference | 295 |
| player_detections.csv | all_current_unmatched_current | 1575 |
| player_detections.csv | fresh_detector_unmatched_reference | 39701 |
| player_detections.csv | fresh_detector_unmatched_current | 789 |
| player_detections.csv | missing_or_invalid_slot_coordinates | 2025 |

## Byte-identical dense-reference aliases

| Duplicate | Evaluated primary |
|---|---|

## Single-frame court candidates

| File | Frame | Bound | Mean corner px | Max corner px | Limit |
|---|---|---|---|---|---|
| Test10_Full_court.json | 300 | True | 1.0156020550123726 | 1.57524553391127 | single-frame manual candidate; not all-frame accuracy |

## Raw component coverage

| Quantity | Count |
|---|---|
| frames | 37133 |
| raw_shuttle_present | 25063 |
| detector_executed_frames | 16679 |
| person_rows | 73521 |
| scene_telemetry_present | 3891 |
| scene_raw_hypotheses | 54 |
| actual_content_epoch_increments | 58 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 33329 |
| person_propagated_or_unmatched | 40192 |
| pose_present_rows | 63983 |
| pose_current_source_rows | 63983 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 30760 |
| racket_present_rows | 29201 |
| racket_current_source_rows | 29201 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 323 |
| scene_positive_correspondence_vetoes | 1 |
| scene_current_detector_probes | 323 |

## Track coverage

| Quantity | Count |
|---|---|
| camera_rows | 37133 |
| player_rows | 73425 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 72574 |
| projected_court_on_propagated_box | 39796 |
| racket_rows | 29142 |
| shuttle_rows | 37133 |

## Live event counts

| Quantity | Count |
|---|---|
| calibration | 1 |
| activity_interval | 224 |
| scene | 7 |
| participant_observation | 252 |
| racket_observation_ambiguity | 2856 |
| format_decision | 1 |
| rally_start | 98 |
| stroke | 1096 |
| contact | 1096 |
| rally_end | 98 |
| identity_ambiguity | 89 |
| broadcast_score | 1117 |
| match_phase | 1 |
| highlight | 4 |
| shuttle_turn | 28 |

## Outcome and score coverage

| Quantity | Value |
|---|---|
| predicted_rallies | 98 |
| known_winner_outputs | 0 |
| unknown_winner_outputs | 98 |
| canonical_point_events | 0 |
| broadcast_score_observation_events | 1117 |
| accuracy_status | unavailable_without_independent_identity_event_outcome_score_labels |

## Predicted stroke counts

| Predicted class | Count |
|---|---|
| unknown | 794 |
| lift | 58 |
| push | 141 |
| net_shot | 45 |
| drop | 39 |
| drive | 8 |
| clear | 10 |
| rush | 1 |

## Actual runtime and resources

| Quantity | Measured value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 909853 |
| parent_failure_inclusive_elapsed_s | unavailable |
| parent_failure_inclusive_source_fps | unavailable |
| neural_only_throughput_fps | unavailable |
| model_loading_time_s | unavailable |
| media_ready_time_s | 2.8711438355967402 |
| model_staging_time_s | 1.7659707893617451 |
| worker_final_cpu_s | 46608.570429 |
| worker_maxrss_bytes | 3193643008 |
| sampled_worker_tree_peak_rss_bytes | 3228663808 |
| sampled_worker_gpu_peak_mib | 2126 |
| sampled_cpu_seconds_max_observed | 46607.72 |
| sampled_cpu_seconds_last_observed | 46607.72 |
| sampled_system_available_ram_min_bytes | 103349182464 |
| sample_count | 2307 |
| resource_rows | 2307 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 4780.385202378966 |
| parent_completed_source_fps | 7.767784065083439 |
| worker_elapsed_s | 4768.768428303301 |
| worker_source_fps | 7.7867064753261035 |
| component_initialization_including_models_s | 8.422863772138953 |

## Stage invocation timing (scopes can overlap)

| Stage | Calls | Seconds | P50 ms | P95 ms |
|---|---|---|---|---|
| court | 619 | 207.6882518925704 | 310.8146353624761 | 412.85506705753505 |
| content_continuity_and_players | 619 | 2172.2083677323535 | 3715.57974582538 | 4115.081892721356 |
| shuttle | 616 | 513.3088330891915 | 815.421886742115 | 993.7653845408931 |
| players | 619 | 119.53235392319039 | 214.4707036204636 | 364.37227129936224 |
| ocr | 619 | 471.5896119363606 | 717.4836862832308 | 950.5378023721278 |

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
| Source SHA256 | cf71d8e02086df5e192e3cf834804407ca5d9e0f2f6bdf26512b39b6b264214f |
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


[Complete artifacts](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test10_retry1)

[Visual evidence](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/test10_retry1/visual_evidence)
