# Test 3 evaluation

Status: completed fresh end-to-end inference; unchanged pipeline and predictions. Comparison measures agreement with the supplied legacy rally CSV. Independent physical component accuracy is unavailable without reviewed component labels.

| Input / provenance | Value |
|---|---|
| Drive file | Test3_Full_Rev.mp4 (1BOqrabc6KqyvjsC0llTUm6g6BM7fD6fd) |
| Video SHA256 | `d587569affa3b4fcabab0ea6b97ecd278af15675ce5cba36c79298bb6d0db5fa` |
| Annotation | `/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test3_Full/Test3_Full_rally.csv` |
| Annotation SHA256 | `252e4f43e3f719a18b112ab85d087ce4b2d50aec976ee4863114a9c0bb3b98d8` |
| Reference rows | 19 |
| Canonical frames / FPS | 8414 / 30.0 |
| Frozen bindings | [Source, profile, manifest, model lock](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/frozen_pipeline.json) |

| Detection / overlap | Value |
|---|---|
| ground_truth_count | 19 |
| predicted_count | 24 |
| matched_count | 18 |
| true_positives | 18 |
| false_positives | 6 |
| false_negatives | 1 |
| precision | 0.750000 |
| recall | 0.947368 |
| f1 | 0.837209 |
| mean_iou | 0.895795 |
| median_iou | 0.951783 |
| minimum_iou | 0.505929 |
| percent_strictly_exceeding | {'0.5': 100.0, '0.75': 83.33333333333333, '0.9': 72.22222222222223, '0.95': 50.0} |

Boundary and duration statistics condition on matched intervals; all missed rallies and false detections remain in detection metrics. Signed errors are prediction minus reference. Matching: IoU ≥ 0.5, maximum cardinality then total IoU; zero-origin half-open frame intervals.

| Error | MAE | Median absolute | RMSE | P90 absolute | Maximum absolute | Signed bias |
|---|---|---|---|---|---|---|
| start_frame | 28.611111 | 5.000000 | 63.108813 | 88.000000 | 233.000000 | 28.500000 |
| end_frame | 8.500000 | 5.000000 | 10.596121 | 17.600000 | 20.000000 | 0.833333 |
| start_time_sec | 0.953704 | 0.166667 | 2.103627 | 2.933333 | 7.766667 | 0.950000 |
| end_time_sec | 0.283333 | 0.166667 | 0.353204 | 0.586667 | 0.666667 | 0.027778 |
| duration_sec | 0.992593 | 0.366667 | 2.003916 | 2.793333 | 7.200000 | -0.922222 |

| Boundary tolerance | Within / matched | Within / all reference |
|---|---|---|
| start ±1 frames | 3 / 18 (0.166667) | 3 / 19 (0.157895) |
| start ±3 frames | 9 / 18 (0.500000) | 9 / 19 (0.473684) |
| start ±5 frames | 9 / 18 (0.500000) | 9 / 19 (0.473684) |
| start ±10 frames | 12 / 18 (0.666667) | 12 / 19 (0.631579) |
| start ±15 frames | 13 / 18 (0.722222) | 13 / 19 (0.684211) |
| start ±30 frames | 14 / 18 (0.777778) | 14 / 19 (0.736842) |
| end ±1 frames | 2 / 18 (0.111111) | 2 / 19 (0.105263) |
| end ±3 frames | 3 / 18 (0.166667) | 3 / 19 (0.157895) |
| end ±5 frames | 11 / 18 (0.611111) | 11 / 19 (0.578947) |
| end ±10 frames | 11 / 18 (0.611111) | 11 / 19 (0.578947) |
| end ±15 frames | 14 / 18 (0.777778) | 14 / 19 (0.736842) |
| end ±30 frames | 18 / 18 (1.000000) | 18 / 19 (0.947368) |

Missed rally IDs: [7].

| False detection ID | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| 7 | 2485 | 2715 | 82.833333 | 90.500000 |
| 8 | 2717 | 2990 | 90.566667 | 99.666667 |
| 9 | 2993 | 3054 | 99.766667 | 101.800000 |
| 10 | 3130 | 3187 | 104.333333 | 106.233333 |
| 19 | 6692 | 6847 | 223.066667 | 228.233333 |
| 22 | 7337 | 7394 | 244.566667 | 246.466667 |

| Runtime / resources | Value |
|---|---|
| parent_completed_elapsed_s | 864.429404 |
| worker_elapsed_s | 858.445222 |
| worker_source_fps | 9.801441 |
| media_ready_time_s | 1.908980 |
| model_staging_time_s | 1.738413 |
| component_initialization_including_models_s | 9.256680 |
| worker_final_cpu_s | 10532.777135 |
| worker_maxrss_bytes | 2858205184 |
| sampled_worker_tree_peak_rss_bytes | 2827141120 |
| sampled_worker_gpu_peak_mib | 2130 |
| sampled_cpu_seconds_max_observed | 10532.310000 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| sample_count | 417 |
| sampling_error_count | 0 |

Stage timing scopes may overlap. GPU/RSS peaks are sampled; process-tree RSS can count shared pages more than once. Actual model and backend declarations are preserved; ORT provider declarations do not certify every node’s execution placement.

| Component | Observation / metric availability |
|---|---|
| Shuttle visibility/location, player tracking, pose, racket, scene/court | Per-frame coverage, detector cadence, epochs, model/runtime declarations and track diagnostics retained in technical_analysis.json and frame_component_coverage.csv. No reviewed per-frame labels; precision, recall, location error and ID accuracy unavailable. |
| Contact timing / hitter / shot class | Actual event counts, attribution/unknown coverage and evidence retained below. Rally CSV does not supply exhaustive per-contact reviewed labels; timing accuracy and per-class confusion unavailable. |
| Rally segmentation | Full detection, IoU, boundary, duration, miss/extra and overlap topology matrix retained in evaluation/. |
| Point decisions / score sequences | OCR observations and system decisions retained. No certified source-bound winner/score mapping; sporting accuracy unavailable. |

Component coverage and observed events:

```json
{
  "component_coverage": {
    "counts": {
      "frames": 8414,
      "raw_shuttle_present": 6225,
      "detector_executed_frames": 3557,
      "person_rows": 16542,
      "scene_telemetry_present": 3606,
      "scene_raw_hypotheses": 14,
      "actual_content_epoch_increments": 14,
      "content_epoch_decreases": 0,
      "detailed_diagnostic_frames": 3600,
      "person_current_detector_matches": 7056,
      "person_propagated_or_unmatched": 9486,
      "pose_present_rows": 13477,
      "pose_current_source_rows": 13477,
      "pose_present_without_current_source": 0,
      "pose_current_on_propagated_box": 6421,
      "racket_present_rows": 5443,
      "racket_current_source_rows": 5443,
      "racket_present_without_current_source": 0,
      "racket_current_on_propagated_box": 0,
      "scene_decision_records": 14,
      "scene_positive_correspondence_vetoes": 0,
      "scene_current_detector_probes": 14
    },
    "categories": {
      "view": {
        "main": 8334,
        "none": 80
      },
      "calibration_state": {
        "REACQUIRING": 16,
        "VALID": 8318,
        "LOST": 80
      },
      "player_population": {
        "0": 125,
        "2": 8253,
        "1": 36
      },
      "association_status": {
        "missing": 2109,
        "observed": 6225,
        "invalid": 80
      },
      "association_reason": {
        "no_accepted_raw_observation": 2109,
        "fresh_selection_retained": 6225,
        "image_view_invalid": 80
      },
      "scene_raw_status": {
        "unknown": 61,
        "measured": 3531,
        "hypothesis": 14
      },
      "person_detector_match": {
        "True": 7056,
        "False": 9486
      },
      "person_identity_method": {
        "bytetrack_v1": 16542
      },
      "scene_decision": {
        "barrier": 14
      },
      "scene_decision_reason": {
        "raw_change_and_current_layout_discontinuity": 14
      }
    },
    "scene_records": [
      {
        "frame": 1502,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 1,
        "raw": {
          "frame": 1502,
          "previous_frame": 1501,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 1501,
                "key": "track:0",
                "bbox": [
                  952.88818359375,
                  424.76904296875,
                  1039.9320068359375,
                  621.6967163085938
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 56,
              "consistent_fraction": 0.2857142857142857,
              "median_patch_error": 25.710247039794922,
              "median_forward_backward_error": 8.314393997192383,
              "discontinuity": 18.36446217128209,
              "previous_mean": 0.0,
              "adaptive_ratio": 18.36446217128209,
              "appearance_previous_mean": 4.84445858001709,
              "appearance_adaptive_ratio": 5.307145600510888
            },
            {
              "region": {
                "frame": 1501,
                "key": "track:2",
                "bbox": [
                  685.9805908203125,
                  206.24453735351562,
                  747.9671020507812,
                  340.6239013671875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 28,
              "consistent_fraction": 0.8214285714285714,
              "median_patch_error": 21.098674774169922,
              "median_forward_backward_error": 0.11805099248886108,
              "discontinuity": 3.7676204953874866,
              "previous_mean": 0.0,
              "adaptive_ratio": 3.7676204953874866,
              "appearance_previous_mean": 2.7820472717285156,
              "appearance_adaptive_ratio": 7.583866380912029
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 2.02862811088562,
          "discontinuity": 11.066041333334788,
          "photometric_gain": 0.9905660377358491,
          "photometric_offset": 1.6886792452830122,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 23.404460906982422
        },
        "decision": {
          "frame": 1502,
          "previous_frame": 1501,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 1502,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6fe46849ad06d22c8a9765452bcbd9937501bf77c1414d5d4e79638b529b5d4e",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              581.7513401806355,
              361.72235092520714,
              656.0461153686047,
              538.6104139387608
            ],
            [
              712.1304150894284,
              224.31354349851608,
              756.3358734771609,
              368.74414855241776
            ],
            [
              797.4941729977727,
              156.53226875513792,
              830.1308208033442,
              208.35118275135756
            ],
            [
              442.35264267772436,
              157.34205179661512,
              475.39444217830896,
              207.222654171288
            ]
          ],
          "detector_scores": [
            0.9366839286907307,
            0.912187865695892,
            0.44099099353489846,
            0.43074694164621546
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [
            [
              1,
              1
            ]
          ],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 1947,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 2,
        "raw": {
          "frame": 1947,
          "previous_frame": 1946,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 1946,
                "key": "track:0",
                "bbox": [
                  1003.6375732421875,
                  483.8443298339844,
                  1043.93359375,
                  671.9319458007812
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 26,
              "consistent_fraction": 0.34615384615384615,
              "median_patch_error": 29.718183517456055,
              "median_forward_backward_error": 3.2817392349243164,
              "discontinuity": 19.431119992182804,
              "previous_mean": 0.0,
              "adaptive_ratio": 19.431119992182804,
              "appearance_previous_mean": 5.028185419738293,
              "appearance_adaptive_ratio": 5.910319734987583
            },
            {
              "region": {
                "frame": 1946,
                "key": "track:1",
                "bbox": [
                  597.4224853515625,
                  213.3121795654297,
                  646.0927734375,
                  347.9960632324219
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 32,
              "consistent_fraction": 0.21875,
              "median_patch_error": 30.552366256713867,
              "median_forward_backward_error": 20.567447662353516,
              "discontinuity": 23.86903613805771,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.86903613805771,
              "appearance_previous_mean": 5.664222091436386,
              "appearance_adaptive_ratio": 5.393920959226744
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.5125,
          "background_patch_error": 2.4520621299743652,
          "discontinuity": 21.650078065120255,
          "photometric_gain": 1.019047619047619,
          "photometric_offset": -1.3904761904761926,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 30.13527488708496
        },
        "decision": {
          "frame": 1947,
          "previous_frame": 1946,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 1947,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "23abc2b1f0bf94d4392bb32601669bc00d0660f1ae0e41cb0681c8919b44c7bb",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              542.1592887639999,
              242.9438749551773,
              597.1255456209183,
              372.83151161670685
            ],
            [
              613.8583136200905,
              350.7876856327057,
              678.1475581526756,
              544.9222898483276
            ],
            [
              442.35433343052864,
              157.3259625658393,
              475.78935500979424,
              207.13581805676222
            ],
            [
              797.439463891089,
              156.57809396088123,
              829.8871667012572,
              208.6081926226616
            ]
          ],
          "detector_scores": [
            0.9321598658462683,
            0.9248466346780392,
            0.4526026729866761,
            0.4494104507266273
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 2380,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 3,
        "raw": {
          "frame": 2380,
          "previous_frame": 2379,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 2379,
                "key": "track:0",
                "bbox": [
                  353.9462585449219,
                  363.3739318847656,
                  417.5665588378906,
                  542.4498901367188
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 50,
              "consistent_fraction": 0.12,
              "median_patch_error": 33.19458770751953,
              "median_forward_backward_error": 6.628292083740234,
              "discontinuity": 29.211237182617186,
              "previous_mean": 0.0,
              "adaptive_ratio": 29.211237182617186,
              "appearance_previous_mean": 9.801994800567627,
              "appearance_adaptive_ratio": 3.386513498823449
            },
            {
              "region": {
                "frame": 2379,
                "key": "track:2",
                "bbox": [
                  570.4845581054688,
                  227.4518280029297,
                  611.9669799804688,
                  367.8414306640625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.4,
              "median_patch_error": 25.624752044677734,
              "median_forward_backward_error": 4.05821418762207,
              "discontinuity": 15.37485122680664,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.37485122680664,
              "appearance_previous_mean": 5.014101505279541,
              "appearance_adaptive_ratio": 5.110537155599352
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.017502784729004,
          "discontinuity": 22.29304420471191,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 29.409669876098633
        },
        "decision": {
          "frame": 2380,
          "previous_frame": 2379,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2380,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "c3cdce4a6f25bb56d1b66e8e2187a5d4263b99ef45d0fdf153dbeb153e24ec20",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              579.272441983223,
              355.33540856838226,
              653.5567342042923,
              536.3743268251419
            ],
            [
              703.2080280035734,
              225.8617182970047,
              749.8346174508333,
              369.91579377651215
            ],
            [
              796.8563114181161,
              156.3071047514677,
              831.5605477318168,
              206.07304121553898
            ],
            [
              442.1369900777936,
              156.9856794923544,
              475.4909124299884,
              206.9851467758417
            ]
          ],
          "detector_scores": [
            0.9434818507344912,
            0.9139652980537012,
            0.4201200959558064,
            0.38296134517978603
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 2716,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 4,
        "raw": {
          "frame": 2716,
          "previous_frame": 2715,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 2715,
                "key": "track:0",
                "bbox": [
                  572.4019165039062,
                  375.2024230957031,
                  633.706787109375,
                  574.567626953125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 44,
              "consistent_fraction": 0.022727272727272728,
              "median_patch_error": 33.96495819091797,
              "median_forward_backward_error": 86.69778442382812,
              "discontinuity": 33.19302732294256,
              "previous_mean": 0.0,
              "adaptive_ratio": 33.19302732294256,
              "appearance_previous_mean": 6.095911264419556,
              "appearance_adaptive_ratio": 5.571760597822951
            },
            {
              "region": {
                "frame": 2715,
                "key": "track:1",
                "bbox": [
                  564.7803955078125,
                  163.16790771484375,
                  639.5490112304688,
                  288.6636657714844
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 28,
              "consistent_fraction": 0.32142857142857145,
              "median_patch_error": 25.702911376953125,
              "median_forward_backward_error": 8.653036117553711,
              "discontinuity": 17.441261291503906,
              "previous_mean": 0.0,
              "adaptive_ratio": 17.441261291503906,
              "appearance_previous_mean": 3.153468608856201,
              "appearance_adaptive_ratio": 8.150679320152124
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.65,
          "background_patch_error": 4.805272102355957,
          "discontinuity": 25.317144307223234,
          "photometric_gain": 0.9716981132075472,
          "photometric_offset": 1.0943396226415132,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 29.833934783935547
        },
        "decision": {
          "frame": 2716,
          "previous_frame": 2715,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2716,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "3e0eabb1f0c078d7e40309a87b03c77201d5216d6359bc008d585b52b485d3d3",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              671.918318644166,
              375.0655283331871,
              748.4323259443045,
              556.6624394059181
            ],
            [
              609.5154660344124,
              232.10136312246323,
              681.5489274859428,
              374.8437879681587
            ],
            [
              441.8929870426655,
              157.21272057294846,
              475.2101201713085,
              207.23588933050632
            ],
            [
              796.1261742711067,
              156.3757770806551,
              832.0031520724297,
              204.6989336013794
            ]
          ],
          "detector_scores": [
            0.9339937131998103,
            0.9144241369668415,
            0.4664221507297781,
            0.44353110092990994
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 2991,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 5,
        "raw": {
          "frame": 2991,
          "previous_frame": 2990,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 2990,
                "key": "track:0",
                "bbox": [
                  697.2279663085938,
                  331.7203369140625,
                  744.9195556640625,
                  501.7314758300781
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 27,
              "consistent_fraction": 0.037037037037037035,
              "median_patch_error": 36.82915115356445,
              "median_forward_backward_error": 12.588787078857422,
              "discontinuity": 35.465108518247256,
              "previous_mean": 0.0,
              "adaptive_ratio": 35.465108518247256,
              "appearance_previous_mean": 5.490664146840572,
              "appearance_adaptive_ratio": 6.70759495911922
            },
            {
              "region": {
                "frame": 2990,
                "key": "track:1",
                "bbox": [
                  650.224365234375,
                  222.7398223876953,
                  725.5957641601562,
                  366.7630615234375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 32,
              "consistent_fraction": 0.3125,
              "median_patch_error": 22.389808654785156,
              "median_forward_backward_error": 5.161521911621094,
              "discontinuity": 15.392993450164795,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.392993450164795,
              "appearance_previous_mean": 3.014243170619011,
              "appearance_adaptive_ratio": 7.428003444787483
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.2221159934997559,
          "discontinuity": 25.429050984206025,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 29.609479904174805
        },
        "decision": {
          "frame": 2991,
          "previous_frame": 2990,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2991,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "e506f71f68d944ad9c31d908ac03e1aa9931c1c8992ef9a713e16268eb3bd372",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              603.0638857930899,
              351.8632860481739,
              678.955444470048,
              543.8907913863659
            ],
            [
              546.1381168216467,
              239.4268896728754,
              602.2027549892664,
              373.521448597312
            ],
            [
              442.7654574215412,
              157.35724925994873,
              476.02700087428093,
              207.03313592076302
            ],
            [
              798.9353637993336,
              156.37375033646822,
              831.340682476759,
              207.22445433586836
            ]
          ],
          "detector_scores": [
            0.9336955943063289,
            0.9182609387713927,
            0.3916871575099424,
            0.3684435864706749
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 3188,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 6,
        "raw": {
          "frame": 3188,
          "previous_frame": 3187,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 3187,
                "key": "track:0",
                "bbox": [
                  581.381591796875,
                  398.0055236816406,
                  675.3465576171875,
                  588.0488891601562
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 42,
              "consistent_fraction": 0.14285714285714285,
              "median_patch_error": 29.050594329833984,
              "median_forward_backward_error": 12.492015838623047,
              "discontinuity": 24.90050942557199,
              "previous_mean": 0.4180058751787463,
              "adaptive_ratio": 24.90050942557199,
              "appearance_previous_mean": 11.76048755645752,
              "appearance_adaptive_ratio": 2.4701862223290827
            },
            {
              "region": {
                "frame": 3187,
                "key": "track:1",
                "bbox": [
                  675.6790771484375,
                  222.57650756835938,
                  718.2888793945312,
                  354.5448303222656
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 24,
              "consistent_fraction": 0.5,
              "median_patch_error": 22.542020797729492,
              "median_forward_backward_error": 2.13962459564209,
              "discontinuity": 11.271010398864746,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.271010398864746,
              "appearance_previous_mean": 3.0808886289596558,
              "appearance_adaptive_ratio": 7.316726929315003
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.62368905544281,
          "discontinuity": 18.085759912218368,
          "photometric_gain": 1.0095238095238095,
          "photometric_offset": -0.7047619047619094,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 25.79630756378174
        },
        "decision": {
          "frame": 3188,
          "previous_frame": 3187,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3188,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "10d65e03b70a577fe20011d15fa1f7402e9ad1532861f55ade1d44d7e20cc50a",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              629.2005370259285,
              232.21423718333244,
              684.5495240092278,
              376.14084604382515
            ],
            [
              508.8588804602623,
              369.16308385133743,
              594.7707837224007,
              556.2830495238304
            ],
            [
              796.952714279294,
              156.28489163517952,
              832.3213760107756,
              207.0259851515293
            ],
            [
              442.2202413082123,
              157.42149601131678,
              475.5244474411011,
              207.10996719449759
            ]
          ],
          "detector_scores": [
            0.9324234497634344,
            0.9258120364702878,
            0.6750949542368748,
            0.6641992176026793
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 3472,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 7,
        "raw": {
          "frame": 3472,
          "previous_frame": 3471,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 3471,
                "key": "track:1",
                "bbox": [
                  791.4039306640625,
                  394.69244384765625,
                  876.5929565429688,
                  555.0498046875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 47,
              "consistent_fraction": 0.0425531914893617,
              "median_patch_error": 29.531320571899414,
              "median_forward_backward_error": 16.011266708374023,
              "discontinuity": 28.274668632669652,
              "previous_mean": 0.7630880858681421,
              "adaptive_ratio": 28.274668632669652,
              "appearance_previous_mean": 10.227023124694824,
              "appearance_adaptive_ratio": 2.887577373379669
            },
            {
              "region": {
                "frame": 3471,
                "key": "track:0",
                "bbox": [
                  557.2680053710938,
                  200.39291381835938,
                  598.00634765625,
                  330.5349426269531
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 20,
              "consistent_fraction": 0.8,
              "median_patch_error": 26.952062606811523,
              "median_forward_backward_error": 0.27415892481803894,
              "discontinuity": 5.390412521362303,
              "previous_mean": 0.0,
              "adaptive_ratio": 5.390412521362303,
              "appearance_previous_mean": 7.375212669372559,
              "appearance_adaptive_ratio": 3.6544115831041455
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 2.725127696990967,
          "discontinuity": 16.832540577015976,
          "photometric_gain": 1.019047619047619,
          "photometric_offset": -1.4095238095238045,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 28.24169158935547
        },
        "decision": {
          "frame": 3472,
          "previous_frame": 3471,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3472,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "0c094e52101ccf8a87743d02e289f62274c67881e7b370b5896445c251d336f8",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              583.2039768844843,
              407.01982989907265,
              648.101323351264,
              607.4345556199551
            ],
            [
              722.8885374069214,
              222.64831227064133,
              778.0513229370117,
              361.52850687503815
            ],
            [
              798.5090649649501,
              156.2425565868616,
              832.1688563302159,
              206.52791744470596
            ],
            [
              442.4294304102659,
              157.05171393603086,
              475.35354812443256,
              207.18780664354563
            ]
          ],
          "detector_scores": [
            0.9415442657832787,
            0.9219524117685213,
            0.40477394962258506,
            0.3839619089045431
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 5709,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 8,
        "raw": {
          "frame": 5709,
          "previous_frame": 5708,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 5708,
                "key": "track:0",
                "bbox": [
                  954.2154541015625,
                  426.2967224121094,
                  1043.23046875,
                  622.7098999023438
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 56,
              "consistent_fraction": 0.3392857142857143,
              "median_patch_error": 23.6395263671875,
              "median_forward_backward_error": 4.840510368347168,
              "discontinuity": 15.618972778320312,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.618972778320312,
              "appearance_previous_mean": 4.730070069432259,
              "appearance_adaptive_ratio": 4.997711666039845
            },
            {
              "region": {
                "frame": 5708,
                "key": "track:2",
                "bbox": [
                  684.4016723632812,
                  206.24459838867188,
                  747.8912353515625,
                  340.5924987792969
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 30,
              "consistent_fraction": 0.7666666666666667,
              "median_patch_error": 20.99907875061035,
              "median_forward_backward_error": 0.13459448516368866,
              "discontinuity": 4.899785041809081,
              "previous_mean": 0.0,
              "adaptive_ratio": 4.899785041809081,
              "appearance_previous_mean": 2.638959676027298,
              "appearance_adaptive_ratio": 7.957332179558901
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 2.188988208770752,
          "discontinuity": 10.259378910064697,
          "photometric_gain": 0.997624703087886,
          "photometric_offset": 1.1733966745843247,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 22.319302558898926
        },
        "decision": {
          "frame": 5709,
          "previous_frame": 5708,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 5709,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "a1d019f431ef46332e82950ae3a8882a616ae0d93650de673a6460c560c15075",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              581.8007628768682,
              361.7309318482876,
              656.1189420372248,
              538.6997486650944
            ],
            [
              712.0742443576455,
              224.34420865774155,
              756.2157865986228,
              368.8973745703697
            ],
            [
              797.3565660864115,
              156.53039583563805,
              830.010414943099,
              208.28520235419273
            ],
            [
              442.0733734443784,
              157.30639980733395,
              475.29642044752836,
              207.25032806396484
            ]
          ],
          "detector_scores": [
            0.9355216419863193,
            0.9122365905638957,
            0.4642151735035028,
            0.45378951892742525
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [
            [
              1,
              1
            ]
          ],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 6154,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 9,
        "raw": {
          "frame": 6154,
          "previous_frame": 6153,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 6153,
                "key": "track:0",
                "bbox": [
                  1003.6317749023438,
                  483.6980895996094,
                  1043.94287109375,
                  672.050537109375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 29,
              "consistent_fraction": 0.3448275862068966,
              "median_patch_error": 29.629676818847656,
              "median_forward_backward_error": 6.2109761238098145,
              "discontinuity": 19.412546881313983,
              "previous_mean": 0.0,
              "adaptive_ratio": 19.412546881313983,
              "appearance_previous_mean": 4.877922959625721,
              "appearance_adaptive_ratio": 6.074240422427893
            },
            {
              "region": {
                "frame": 6153,
                "key": "track:1",
                "bbox": [
                  597.2294921875,
                  213.4206085205078,
                  646.0929565429688,
                  348.0194091796875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.2903225806451613,
              "median_patch_error": 30.47966194152832,
              "median_forward_backward_error": 21.208940505981445,
              "discontinuity": 21.630727829471713,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.630727829471713,
              "appearance_previous_mean": 5.551941424608231,
              "appearance_adaptive_ratio": 5.489910575502712
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.5,
          "background_patch_error": 2.374645709991455,
          "discontinuity": 20.521637355392848,
          "photometric_gain": 1.019047619047619,
          "photometric_offset": -1.3904761904761926,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 30.05466938018799
        },
        "decision": {
          "frame": 6154,
          "previous_frame": 6153,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 6154,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "1ffa803af5f1699d9f4939273c30f34e32a577fab56160fea2092a7ca977c67d",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              542.2701536267996,
              243.2327868193388,
              597.177903547883,
              372.8403378278017
            ],
            [
              613.9429890364408,
              350.88183465600014,
              678.0294330865145,
              544.9803358018398
            ],
            [
              797.2431044429541,
              156.6100707873702,
              829.8768859058619,
              208.4488240107894
            ],
            [
              442.24578680098057,
              157.3086614459753,
              475.54342161118984,
              207.117161616683
            ]
          ],
          "detector_scores": [
            0.9309243356616166,
            0.9243545159047172,
            0.41816290912839077,
            0.41297501724616675
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 6587,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 10,
        "raw": {
          "frame": 6587,
          "previous_frame": 6586,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 6586,
                "key": "track:0",
                "bbox": [
                  355.9608459472656,
                  365.69439697265625,
                  416.254150390625,
                  544.9228515625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 51,
              "consistent_fraction": 0.1568627450980392,
              "median_patch_error": 33.504676818847656,
              "median_forward_backward_error": 7.361086845397949,
              "discontinuity": 28.249041239420574,
              "previous_mean": 0.0,
              "adaptive_ratio": 28.249041239420574,
              "appearance_previous_mean": 9.80130386352539,
              "appearance_adaptive_ratio": 3.4183897658282065
            },
            {
              "region": {
                "frame": 6586,
                "key": "track:1",
                "bbox": [
                  570.3094482421875,
                  227.37008666992188,
                  610.7427978515625,
                  367.8507385253906
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 30,
              "consistent_fraction": 0.3333333333333333,
              "median_patch_error": 26.567461013793945,
              "median_forward_backward_error": 5.736130714416504,
              "discontinuity": 17.711640675862633,
              "previous_mean": 0.0,
              "adaptive_ratio": 17.711640675862633,
              "appearance_previous_mean": 5.012701749801636,
              "appearance_adaptive_ratio": 5.30002827613777
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.0096018314361572,
          "discontinuity": 22.9803409576416,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 30.0360689163208
        },
        "decision": {
          "frame": 6587,
          "previous_frame": 6586,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 6587,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "e82c73cb41b8bb0109ce8c85c5ecfd6778c44dbff6cf8e2f235a5f495cf43c64",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              579.2469593882561,
              355.34426388144493,
              653.4230673909187,
              536.4760257303715
            ],
            [
              702.9785229116678,
              225.8654267191887,
              749.8352464288473,
              370.0735929608345
            ],
            [
              796.9295843616128,
              156.2888640537858,
              831.4781695827842,
              205.7800945714116
            ],
            [
              442.24749252945185,
              157.00210131704807,
              475.2285926565528,
              206.95219087600708
            ]
          ],
          "detector_scores": [
            0.9427574880893663,
            0.9124541408650046,
            0.4665841410926164,
            0.4191323035023969
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 6923,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 11,
        "raw": {
          "frame": 6923,
          "previous_frame": 6922,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 6922,
                "key": "track:2",
                "bbox": [
                  572.42138671875,
                  376.52960205078125,
                  632.6575317382812,
                  574.6840209960938
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 46,
              "consistent_fraction": 0.021739130434782608,
              "median_patch_error": 34.88003158569336,
              "median_forward_backward_error": 82.94587707519531,
              "discontinuity": 34.12177002948263,
              "previous_mean": 0.0,
              "adaptive_ratio": 34.12177002948263,
              "appearance_previous_mean": 6.158588409423828,
              "appearance_adaptive_ratio": 5.663640637572107
            },
            {
              "region": {
                "frame": 6922,
                "key": "track:1",
                "bbox": [
                  566.9953002929688,
                  162.4915771484375,
                  638.90966796875,
                  288.4998779296875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 30,
              "consistent_fraction": 0.36666666666666664,
              "median_patch_error": 24.569799423217773,
              "median_forward_backward_error": 8.197834968566895,
              "discontinuity": 15.560872968037922,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.560872968037922,
              "appearance_previous_mean": 3.127480149269104,
              "appearance_adaptive_ratio": 7.856100838548812
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.6625,
          "background_patch_error": 4.6892008781433105,
          "discontinuity": 24.841321498760276,
          "photometric_gain": 0.9716981132075472,
          "photometric_offset": 1.0943396226415132,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 29.724915504455566
        },
        "decision": {
          "frame": 6923,
          "previous_frame": 6922,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 6923,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "0aa41eb65819bdce6a895fdacd0593542917577bcaf917583f60eadb428c4f5e",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              671.9294725209475,
              374.9913266301155,
              748.3174685686827,
              556.5519184470177
            ],
            [
              609.500762924552,
              232.03072848916054,
              681.5425448566675,
              374.76122984290123
            ],
            [
              441.7529900148511,
              157.1416161507368,
              475.24775552004576,
              207.20008559525013
            ],
            [
              796.2319698706269,
              156.37630923092365,
              831.8249940499663,
              204.5881881415844
            ]
          ],
          "detector_scores": [
            0.9341278120047057,
            0.9154511268297842,
            0.45472918302527454,
            0.43238601042371216
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 7198,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 12,
        "raw": {
          "frame": 7198,
          "previous_frame": 7197,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 7197,
                "key": "track:0",
                "bbox": [
                  697.2523803710938,
                  331.6695861816406,
                  744.8364868164062,
                  501.8279724121094
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.038461538461538464,
              "median_patch_error": 36.739158630371094,
              "median_forward_backward_error": 11.58328914642334,
              "discontinuity": 35.32611406766451,
              "previous_mean": 0.0,
              "adaptive_ratio": 35.32611406766451,
              "appearance_previous_mean": 5.2553499937057495,
              "appearance_adaptive_ratio": 6.990811016273514
            },
            {
              "region": {
                "frame": 7197,
                "key": "track:1",
                "bbox": [
                  650.1460571289062,
                  222.9285888671875,
                  725.4144287109375,
                  366.6943664550781
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.3,
              "median_patch_error": 21.735225677490234,
              "median_forward_backward_error": 3.912010669708252,
              "discontinuity": 15.214657974243163,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.214657974243163,
              "appearance_previous_mean": 3.049514666199684,
              "appearance_adaptive_ratio": 7.127437660293908
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.2163052558898926,
          "discontinuity": 25.270386020953836,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 29.237192153930664
        },
        "decision": {
          "frame": 7198,
          "previous_frame": 7197,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7198,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "fc1456c3954e14a85a3dd51045f13d10b023df5d76861e087235a00880370742",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              603.1990711390972,
              351.7930588424206,
              678.9017267525196,
              543.855253726244
            ],
            [
              546.0587368011475,
              239.47800520062447,
              602.2353630065918,
              373.56741723418236
            ],
            [
              442.56501560658216,
              157.3452052026987,
              476.0703539326787,
              207.04297238588333
            ],
            [
              798.8357711210847,
              156.34783919155598,
              830.820833645761,
              207.13002052903175
            ]
          ],
          "detector_scores": [
            0.9327822078358003,
            0.9200878704750267,
            0.381027803497644,
            0.3558633145729993
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 7395,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 13,
        "raw": {
          "frame": 7395,
          "previous_frame": 7394,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 7394,
                "key": "track:0",
                "bbox": [
                  580.3209838867188,
                  396.3788757324219,
                  665.8064575195312,
                  586.0939331054688
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 43,
              "consistent_fraction": 0.23255813953488372,
              "median_patch_error": 26.574617385864258,
              "median_forward_backward_error": 10.291926383972168,
              "discontinuity": 20.39447380775629,
              "previous_mean": 0.4100644189786019,
              "adaptive_ratio": 20.39447380775629,
              "appearance_previous_mean": 11.638357639312744,
              "appearance_adaptive_ratio": 2.283364905035992
            },
            {
              "region": {
                "frame": 7394,
                "key": "track:1",
                "bbox": [
                  676.6870727539062,
                  222.93443298339844,
                  718.1192016601562,
                  355.3227233886719
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 23,
              "consistent_fraction": 0.4782608695652174,
              "median_patch_error": 22.623512268066406,
              "median_forward_backward_error": 3.9057698249816895,
              "discontinuity": 11.803571618121603,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.803571618121603,
              "appearance_previous_mean": 3.035997748374939,
              "appearance_adaptive_ratio": 7.451755285449722
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.6195082664489746,
          "discontinuity": 16.099022712938947,
          "photometric_gain": 1.0095238095238095,
          "photometric_offset": -0.7047619047619094,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 24.599064826965332
        },
        "decision": {
          "frame": 7395,
          "previous_frame": 7394,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7395,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b9fd91cfe44af382c94c44f243a95b2777cf65be01313d8d305ca45d55982837",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              629.1687646508217,
              232.1669506430626,
              684.5665363669395,
              376.1100062727928
            ],
            [
              508.8435244113207,
              369.1044392287731,
              594.888932749629,
              556.2963283360004
            ],
            [
              796.9877783060074,
              156.29120884090662,
              832.3485149145126,
              207.1862642392516
            ],
            [
              442.3338901475072,
              157.44062224030495,
              475.6379495188594,
              207.1288107186556
            ]
          ],
          "detector_scores": [
            0.9318314761971331,
            0.9233429328011745,
            0.6934108172274834,
            0.6384890906569014
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 7679,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 14,
        "raw": {
          "frame": 7679,
          "previous_frame": 7678,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 7678,
                "key": "track:1",
                "bbox": [
                  795.79345703125,
                  391.4881591796875,
                  880.7117309570312,
                  554.19970703125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 54,
              "consistent_fraction": 0.05555555555555555,
              "median_patch_error": 27.626346588134766,
              "median_forward_backward_error": 17.806360244750977,
              "discontinuity": 26.09154955546061,
              "previous_mean": 0.9762121899922688,
              "adaptive_ratio": 26.09154955546061,
              "appearance_previous_mean": 10.542587757110596,
              "appearance_adaptive_ratio": 2.6204521342022304
            },
            {
              "region": {
                "frame": 7678,
                "key": "track:0",
                "bbox": [
                  558.1321411132812,
                  201.43222045898438,
                  599.17822265625,
                  336.23236083984375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 23,
              "consistent_fraction": 0.782608695652174,
              "median_patch_error": 26.794429779052734,
              "median_forward_backward_error": 0.2909027636051178,
              "discontinuity": 5.824876038924507,
              "previous_mean": 0.0,
              "adaptive_ratio": 5.824876038924507,
              "appearance_previous_mean": 7.141900539398193,
              "appearance_adaptive_ratio": 3.751722616583869
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 2.7010698318481445,
          "discontinuity": 15.958212797192559,
          "photometric_gain": 1.019047619047619,
          "photometric_offset": -1.4095238095238045,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 27.21038818359375
        },
        "decision": {
          "frame": 7679,
          "previous_frame": 7678,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7679,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "8fc7765d5f7d5a9bf7e0885a4ec7b9edd47e5a9b0abcbbbc88e81e1652e94ca1",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              583.2123333066702,
              407.02775394916534,
              648.1467834860086,
              607.3981615304947
            ],
            [
              722.8259091675282,
              222.7067947536707,
              777.9867658317089,
              361.52021281421185
            ],
            [
              798.6065969914198,
              156.23165582120419,
              832.0330824404955,
              206.52268740534782
            ],
            [
              442.3741222769022,
              157.1019543260336,
              475.60912285745144,
              207.22863046824932
            ]
          ],
          "detector_scores": [
            0.9422409371048988,
            0.9219130132142633,
            0.41353092327206425,
            0.3876030602054695
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      }
    ],
    "limits": [
      "Counts are technical coverage, not reviewed component accuracy.",
      "Raw shuttle is pre-association decoder output that already passed court masking.",
      "Current pose execution and current box/person association are separate.",
      "Content epochs measure actual tracking action; raw hypotheses remain separate."
    ]
  },
  "events": {
    "append_only_counts": {
      "calibration": 1,
      "activity_interval": 69,
      "scene": 6,
      "participant_observation": 70,
      "rally_start": 52,
      "contact": 592,
      "stroke": 285,
      "format_decision": 1,
      "rally_end": 24,
      "shuttle_turn": 15,
      "broadcast_score": 207,
      "identity_ambiguity": 21,
      "match_phase": 1,
      "highlight": 1
    },
    "live_counts": {
      "calibration": 1,
      "activity_interval": 69,
      "scene": 6,
      "participant_observation": 70,
      "format_decision": 1,
      "rally_start": 24,
      "stroke": 273,
      "contact": 273,
      "rally_end": 24,
      "shuttle_turn": 15,
      "broadcast_score": 207,
      "identity_ambiguity": 21,
      "match_phase": 1,
      "highlight": 1
    },
    "categories": {
      "event_status": {
        "confirmed": 856,
        "provisional": 130
      },
      "stroke_actor": {
        "unknown": 273
      },
      "stroke_physical_event_status": {
        "insufficient": 142,
        "ambiguous": 88,
        "probable": 43
      },
      "stroke_contact_status": {
        "estimated": 273
      },
      "stroke_classification_status": {
        "unknown": 191,
        "estimated": 82
      },
      "stroke_stroke": {
        "unknown": 191,
        "push": 46,
        "lift": 8,
        "drive": 5,
        "net_shot": 13,
        "drop": 6,
        "clear": 4
      },
      "stroke_attribution_reason": {
        "nearest_proximity": 272,
        "ambiguous_proximity": 1
      },
      "stroke_classification_abstention_reason": {
        "missing_required_evidence": 189,
        "unresolved_initial_contact": 2
      },
      "contact_actor": {
        "unknown": 273
      },
      "contact_physical_event_status": {
        "insufficient": 142,
        "ambiguous": 88,
        "probable": 43
      },
      "contact_contact_status": {
        "estimated": 273
      },
      "contact_attribution_reason": {
        "nearest_proximity": 272,
        "ambiguous_proximity": 1
      },
      "contact_trajectory_reliability": {
        "insufficient": 69,
        "probable": 160,
        "ambiguous": 44
      },
      "contact_trajectory_reasons": {
        "coherent_motion_change_unavailable": 69,
        "supported_launch": 32,
        "association_unresolved": 44,
        "supported_turn": 128
      },
      "contact_impact_reliability": {
        "insufficient": 142,
        "ambiguous": 88,
        "probable": 43
      },
      "contact_impact_reasons": {
        "fresh_player_observation_unavailable": 142,
        "no_fresh_swing_or_racket_overlap": 20,
        "association_unresolved": 44,
        "coherent_motion_and_fresh_contact_cue": 43,
        "coherent_motion_change_unavailable": 24
      },
      "contact_attribution_reliability": {
        "insufficient": 173,
        "probable": 100
      },
      "contact_attribution_reasons": {
        "fresh_player_observation_unavailable": 173,
        "geometric_attribution_not_verified_identity": 100
      },
      "rally_end_reason": {
        "stationary": 9,
        "gap": 4,
        "cut": 11
      },
      "rally_phase": {
        "unknown": 2,
        "match_play": 22
      },
      "rally_official": {
        "False": 7,
        "True": 17
      },
      "rally_match_format_known": {
        "True": 24
      },
      "rally_match_format": {
        "singles": 24
      },
      "rally_winner": {
        "None": 24
      },
      "rally_score_transition_status": {
        "unavailable": 16,
        "candidate": 8
      },
      "rally_admission_reason": {
        "duration_policy": 22,
        "independent_contact_and_observed_motion_witnesses": 2
      }
    },
    "physical_accuracy_validated": false
  },
  "ocr": {
    "readout_count": 229,
    "label_counts": {
      "GEMKE": 229,
      "GINTING": 229
    },
    "context_counts": {
      "{\"acquisition_policy\":\"main_camera\",\"actual_replay_status\":\"unknown\",\"analysis_excluded\":false,\"view\":\"main\"}": 229
    },
    "previously_source_reviewed_branding_strings": {},
    "readouts": [
      {
        "f": 738,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.94252,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 768,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99978,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 798,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99679,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 828,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.9961,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 858,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99989,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 888,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99989,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 918,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 948,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.90016,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 978,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.98658,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1008,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.98358,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1038,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.86334,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1068,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99989,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1098,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.85472,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1128,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.83359,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1158,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1188,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1218,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99989,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1248,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1278,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.73939,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1308,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1338,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.78938,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1368,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.78865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1398,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1428,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.79288,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1458,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99502,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1488,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99851,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1518,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1548,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1578,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.78,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1608,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99972,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1638,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1668,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1698,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.9999,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1728,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99942,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1758,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1788,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1818,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.80553,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1848,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1878,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99996,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1908,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1938,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1968,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99994,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1998,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2028,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2058,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.76117,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2088,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2118,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99574,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2148,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.66562,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2178,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.64625,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2208,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.64676,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2238,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.68321,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2268,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99936,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2298,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.75339,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2328,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.74949,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2358,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2388,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99992,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2418,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2448,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2478,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99368,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2508,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2538,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2568,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2598,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2628,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2658,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2688,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2718,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2748,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2778,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2808,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2838,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2868,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2898,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2928,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2958,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2988,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3018,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99751,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3048,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3078,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.87282,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3108,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3138,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            9
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3168,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            9
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3198,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3228,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3258,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99993,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3288,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3318,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3348,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3378,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3408,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3438,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.98486,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3468,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99756,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3498,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3528,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3558,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3588,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3618,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3648,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3678,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3708,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3738,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3768,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3798,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3828,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3858,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3888,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3918,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3948,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3978,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99802,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4008,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.97148,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4038,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4068,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4098,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4128,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4158,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4188,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5035,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.92849,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5065,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5095,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5125,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.98351,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5155,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.91882,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5185,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99974,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5215,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5245,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99007,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5275,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99903,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5305,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.93491,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5335,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.9999,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5365,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99985,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5395,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5425,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.9999,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5455,
        "r": [
          [
            "GEMKE",
            2
          ],
          [
            "GINTING",
            1
          ]
        ],
        "c": 0.99991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5485,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5515,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.80859,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5545,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.78233,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5575,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5605,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5635,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.80584,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5665,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.78727,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5695,
        "r": [
          [
            "GEMKE",
            6
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.76513,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5725,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5755,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.79432,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5785,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5815,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.71806,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5845,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.74739,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5875,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5905,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5935,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.75403,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5965,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5995,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.74954,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6025,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.80604,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6055,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6085,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6115,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6145,
        "r": [
          [
            "GEMKE",
            7
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6175,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99994,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6205,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6235,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99992,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6265,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.75397,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6295,
        "r": [
          [
            "GEMKE",
            8
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6325,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.78072,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6355,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.7862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6385,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6415,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6445,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6475,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99623,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6505,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.6241,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6535,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.98386,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6565,
        "r": [
          [
            "GEMKE",
            13
          ],
          [
            "GINTING",
            6
          ]
        ],
        "c": 0.99926,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6595,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6625,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6655,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99994,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6685,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.96893,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6715,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.96854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6745,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99996,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6775,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6805,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6835,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99994,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6865,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99996,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6895,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            7
          ]
        ],
        "c": 0.99996,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6925,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6955,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6985,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7015,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7045,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7075,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7105,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7135,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7165,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7195,
        "r": [
          [
            "GEMKE",
            15
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7225,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99082,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7255,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99304,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7285,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7315,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            8
          ]
        ],
        "c": 0.99992,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7345,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            9
          ]
        ],
        "c": 0.94641,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7375,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            9
          ]
        ],
        "c": 0.90446,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7405,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7435,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7465,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7495,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7525,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7555,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7585,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7615,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7645,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7675,
        "r": [
          [
            "GEMKE",
            16
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7705,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99996,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7735,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99996,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7765,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7795,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7825,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7855,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7885,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7915,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7945,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7975,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8005,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8035,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8065,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8095,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8125,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8155,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8185,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8215,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8245,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8275,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8305,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8335,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8365,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8395,
        "r": [
          [
            "GEMKE",
            17
          ],
          [
            "GINTING",
            15
          ]
        ],
        "c": 0.99995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      }
    ],
    "accuracy_validated": false,
    "limit": "Observed labels are not verified athlete identities/scores. Known branding-string absence does not certify OCR accuracy."
  },
  "track_exports": {
    "counts": {
      "camera_rows": 8414,
      "player_rows": 16536,
      "nonfinite_projected_court_rows": 0,
      "player_projected_court_rows": 16346,
      "projected_court_on_propagated_box": 9392,
      "racket_rows": 5438,
      "shuttle_rows": 8414
    },
    "categories": {
      "player_id": {
        "None": 16536
      },
      "detector_matched": {
        "True": 7050,
        "False": 9486
      }
    },
    "invalid_geometry_frame_count": 96,
    "player_rows_on_invalid_geometry": [],
    "limit": "Anonymous projected positions and detector flags are evidence coverage, not physical identity or metric accuracy."
  },
  "session_degraded": [
    {
      "stage": "player_identity",
      "reason": "osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"
    },
    {
      "stage": "player_reid",
      "reason": "baseline player_reid provider is unavailable"
    }
  ]
}
```

Reproducibility artifacts: [predictions](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/run/predicted_rallies.csv), [worker receipt](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/run/inference.json), [parent receipt](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/run.executor.json), [complete evaluation](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/evaluation/supplemental_metrics.json), [per-rally comparison](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/evaluation/per_rally_comparison.csv), [failure case index](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/evaluation/failure_case_index.json), [technical analysis](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/analysis/technical_analysis.json), [source/proxy PTS and scene-pixel audit](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/timestamps/timestamp_audit.json), [frozen plan](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/protocol/plan.json). All command logs, stage samples, exact effective config, source snapshots, model manifest/lock and cache catalogue are preserved.

Failures and observations are recorded for the later consolidated analysis. No pipeline component, model, numerical threshold or matcher was changed during this video evaluation. No final aggregate or generalisation claim is made from this individual video.
