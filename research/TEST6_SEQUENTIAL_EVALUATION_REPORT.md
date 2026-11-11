# Test 6 evaluation

Status: completed fresh end-to-end inference; unchanged pipeline and predictions. Comparison measures agreement with the supplied legacy rally CSV. Independent physical component accuracy is unavailable without reviewed component labels.

| Input / provenance | Value |
|---|---|
| Drive file | Test6_Full.mp4 (1LxlJnH5bJo_tLVfgDH73UQ35XCtRg1tC) |
| Video SHA256 | `45f873540649ec9d2b20e2d14edbf35ba2b2e41b150bfe07f3c995a0310fdab8` |
| Annotation | `/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test6_Full/Test6_Full_rally.csv` |
| Annotation SHA256 | `237e7710a7f534bd2c7143c0010cca8872e46581f336c18c5be639f4349c4236` |
| Reference rows | 42 |
| Canonical frames / FPS | 17915 / 30.0 |
| Frozen bindings | [Source, profile, manifest, model lock](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/frozen_pipeline.json) |

| Detection / overlap | Value |
|---|---|
| ground_truth_count | 42 |
| predicted_count | 47 |
| matched_count | 35 |
| true_positives | 35 |
| false_positives | 12 |
| false_negatives | 7 |
| precision | 0.744681 |
| recall | 0.833333 |
| f1 | 0.786517 |
| mean_iou | 0.884584 |
| median_iou | 0.911392 |
| minimum_iou | 0.601533 |
| percent_strictly_exceeding | {'0.5': 100.0, '0.75': 88.57142857142857, '0.9': 60.0, '0.95': 34.285714285714285} |

Boundary and duration statistics condition on matched intervals; all missed rallies and false detections remain in detection metrics. Signed errors are prediction minus reference. Matching: IoU ≥ 0.5, maximum cardinality then total IoU; zero-origin half-open frame intervals.

| Error | MAE | Median absolute | RMSE | P90 absolute | Maximum absolute | Signed bias |
|---|---|---|---|---|---|---|
| start_frame | 23.485714 | 10.000000 | 43.798239 | 51.600000 | 206.000000 | 21.828571 |
| end_frame | 20.571429 | 10.000000 | 49.055654 | 33.600000 | 263.000000 | -12.114286 |
| start_time_sec | 0.782857 | 0.333333 | 1.459941 | 1.720000 | 6.866667 | 0.727619 |
| end_time_sec | 0.685714 | 0.333333 | 1.635188 | 1.120000 | 8.766667 | -0.403810 |
| duration_sec | 1.350476 | 0.733333 | 2.408965 | 2.266667 | 10.466667 | -1.131429 |

| Boundary tolerance | Within / matched | Within / all reference |
|---|---|---|
| start ±1 frames | 6 / 35 (0.171429) | 6 / 42 (0.142857) |
| start ±3 frames | 9 / 35 (0.257143) | 9 / 42 (0.214286) |
| start ±5 frames | 15 / 35 (0.428571) | 15 / 42 (0.357143) |
| start ±10 frames | 18 / 35 (0.514286) | 18 / 42 (0.428571) |
| start ±15 frames | 19 / 35 (0.542857) | 19 / 42 (0.452381) |
| start ±30 frames | 25 / 35 (0.714286) | 25 / 42 (0.595238) |
| end ±1 frames | 5 / 35 (0.142857) | 5 / 42 (0.119048) |
| end ±3 frames | 11 / 35 (0.314286) | 11 / 42 (0.261905) |
| end ±5 frames | 16 / 35 (0.457143) | 16 / 42 (0.380952) |
| end ±10 frames | 18 / 35 (0.514286) | 18 / 42 (0.428571) |
| end ±15 frames | 25 / 35 (0.714286) | 25 / 42 (0.595238) |
| end ±30 frames | 30 / 35 (0.857143) | 30 / 42 (0.714286) |

Missed rally IDs: [9, 19, 22, 26, 30, 40, 41].

| False detection ID | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| 2 | 666 | 725 | 22.200000 | 24.166667 |
| 10 | 3592 | 3636 | 119.733333 | 121.200000 |
| 11 | 3796 | 3880 | 126.533333 | 129.333333 |
| 12 | 3943 | 4140 | 131.433333 | 138.000000 |
| 15 | 5111 | 5191 | 170.366667 | 173.033333 |
| 16 | 5221 | 5314 | 174.033333 | 177.133333 |
| 24 | 7635 | 7942 | 254.500000 | 264.733333 |
| 25 | 7970 | 8232 | 265.666667 | 274.400000 |
| 31 | 10341 | 10439 | 344.700000 | 347.966667 |
| 32 | 10567 | 10754 | 352.233333 | 358.466667 |
| 36 | 12393 | 12475 | 413.100000 | 415.833333 |
| 46 | 16877 | 17205 | 562.566667 | 573.500000 |

| Runtime / resources | Value |
|---|---|
| parent_completed_elapsed_s | 1992.107158 |
| worker_elapsed_s | 1984.001834 |
| worker_source_fps | 9.029730 |
| media_ready_time_s | 1.798781 |
| model_staging_time_s | 1.690110 |
| component_initialization_including_models_s | 9.016501 |
| worker_final_cpu_s | 23014.755924 |
| worker_maxrss_bytes | 2968973312 |
| sampled_worker_tree_peak_rss_bytes | 2848849920 |
| sampled_worker_gpu_peak_mib | 2128 |
| sampled_cpu_seconds_max_observed | 23015.030000 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| sample_count | 962 |
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
      "frames": 17915,
      "raw_shuttle_present": 14711,
      "detector_executed_frames": 8357,
      "person_rows": 35556,
      "scene_telemetry_present": 3629,
      "scene_raw_hypotheses": 37,
      "actual_content_epoch_increments": 37,
      "content_epoch_decreases": 0,
      "detailed_diagnostic_frames": 3600,
      "person_current_detector_matches": 16637,
      "person_propagated_or_unmatched": 18919,
      "pose_present_rows": 32651,
      "pose_current_source_rows": 32651,
      "pose_present_without_current_source": 0,
      "pose_current_on_propagated_box": 16014,
      "racket_present_rows": 13506,
      "racket_current_source_rows": 13506,
      "racket_present_without_current_source": 0,
      "racket_current_on_propagated_box": 0,
      "scene_decision_records": 37,
      "scene_positive_correspondence_vetoes": 0,
      "scene_current_detector_probes": 37
    },
    "categories": {
      "view": {
        "main": 17913,
        "none": 2
      },
      "calibration_state": {
        "REACQUIRING": 4,
        "VALID": 17909,
        "LOST": 2
      },
      "player_population": {
        "0": 124,
        "2": 17429,
        "1": 194,
        "3": 168
      },
      "association_status": {
        "missing": 3202,
        "observed": 14634,
        "ambiguous": 77,
        "invalid": 2
      },
      "association_reason": {
        "no_accepted_raw_observation": 3202,
        "fresh_selection_retained": 14634,
        "coobserved_competing_static_hypothesis": 77,
        "image_view_invalid": 2
      },
      "scene_raw_status": {
        "unknown": 94,
        "measured": 3498,
        "hypothesis": 37
      },
      "person_detector_match": {
        "True": 16637,
        "False": 18919
      },
      "person_identity_method": {
        "bytetrack_v1": 35556
      },
      "scene_decision": {
        "barrier": 36,
        "unknown": 1
      },
      "scene_decision_reason": {
        "raw_change_and_current_layout_discontinuity": 36,
        "participant_count_unresolved_raw_barrier_fallback": 1
      }
    },
    "scene_records": [
      {
        "frame": 726,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 1,
        "raw": {
          "frame": 726,
          "previous_frame": 725,
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
                "frame": 725,
                "key": "track:0",
                "bbox": [
                  539.3365478515625,
                  365.6629638671875,
                  598.0953369140625,
                  548.23779296875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 38,
              "consistent_fraction": 0.0,
              "median_patch_error": 38.759071350097656,
              "median_forward_backward_error": 31.292236328125,
              "discontinuity": 38.759071350097656,
              "previous_mean": 0.0,
              "adaptive_ratio": 38.759071350097656,
              "appearance_previous_mean": 5.519805669784546,
              "appearance_adaptive_ratio": 7.021818098101728
            },
            {
              "region": {
                "frame": 725,
                "key": "track:1",
                "bbox": [
                  534.2552490234375,
                  177.7900848388672,
                  585.3802490234375,
                  325.04425048828125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.0967741935483871,
              "median_patch_error": 52.905826568603516,
              "median_forward_backward_error": 5.542935371398926,
              "discontinuity": 47.785907868416075,
              "previous_mean": 0.14584447315761026,
              "adaptive_ratio": 47.785907868416075,
              "appearance_previous_mean": 10.644416332244873,
              "appearance_adaptive_ratio": 4.970289109073756
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.8375,
          "background_patch_error": 1.3084254264831543,
          "discontinuity": 43.272489609256866,
          "photometric_gain": 0.9894736842105263,
          "photometric_offset": 0.8842105263157976,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 45.832448959350586
        },
        "decision": {
          "frame": 726,
          "previous_frame": 725,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 726,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "ff9462adc7318ddc378fd0af2529774ccc34e4c8197c7e1902781738ccf52ba9",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              577.8100072294474,
              412.25324934720993,
              682.3525783866644,
              571.3355607390404
            ],
            [
              606.6565797924995,
              224.2129643857479,
              710.8321885466576,
              366.7278247177601
            ],
            [
              445.2543411850929,
              151.1284384354949,
              485.3991566300392,
              202.5533846244216
            ],
            [
              792.5774769000709,
              151.26749974116683,
              830.9917555637658,
              203.567924503237
            ],
            [
              622.6721567735076,
              151.60803355649114,
              655.6108374968171,
              204.56559028849006
            ]
          ],
          "detector_scores": [
            0.9390496868460805,
            0.9262114591948309,
            0.6780377406845391,
            0.6694135830187425,
            0.6544274016895881
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
        "frame": 1028,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 2,
        "raw": {
          "frame": 1028,
          "previous_frame": 1027,
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
                "frame": 1027,
                "key": "track:0",
                "bbox": [
                  531.2657470703125,
                  328.96673583984375,
                  582.77392578125,
                  507.5224609375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.1,
              "median_patch_error": 39.72764205932617,
              "median_forward_backward_error": 7.845193862915039,
              "discontinuity": 35.75487785339356,
              "previous_mean": 0.0,
              "adaptive_ratio": 35.75487785339356,
              "appearance_previous_mean": 9.135841846466064,
              "appearance_adaptive_ratio": 4.348547482210811
            },
            {
              "region": {
                "frame": 1027,
                "key": "track:1",
                "bbox": [
                  347.5791320800781,
                  244.98728942871094,
                  417.925048828125,
                  404.0617980957031
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 43,
              "consistent_fraction": 0.20930232558139536,
              "median_patch_error": 41.10558319091797,
              "median_forward_backward_error": 16.291412353515625,
              "discontinuity": 32.50208903467932,
              "previous_mean": 0.40474418971849496,
              "adaptive_ratio": 32.50208903467932,
              "appearance_previous_mean": 12.278539657592773,
              "appearance_adaptive_ratio": 3.3477583114290956
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 1.058708906173706,
          "discontinuity": 34.12848344403644,
          "photometric_gain": 0.989247311827957,
          "photometric_offset": 0.9139784946236489,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 40.41661262512207
        },
        "decision": {
          "frame": 1028,
          "previous_frame": 1027,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 1028,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6ff77c5012d3374511664acc629f48ec723a74d33e37f6137e9ae749bc621937",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              480.12031380832195,
              378.9307347536087,
              561.3166989833117,
              561.5552965402603
            ],
            [
              621.2788933590055,
              213.0642253011465,
              682.7690788432956,
              368.92029924690723
            ],
            [
              792.7409959286451,
              151.236338339746,
              830.7247247248888,
              203.7017743512988
            ],
            [
              445.5541735962033,
              151.13881294056773,
              485.51762007921934,
              202.16815561428666
            ],
            [
              622.4161231592298,
              151.6793143413961,
              655.2821066305041,
              205.46588853374124
            ],
            [
              620.8461573235691,
              151.5767921730876,
              655.4954111464322,
              236.99067125469446
            ]
          ],
          "detector_scores": [
            0.9157250924511497,
            0.902774670181778,
            0.7087158435269405,
            0.6796619555585462,
            0.5318403332091292,
            0.350999687446809
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
        "frame": 1667,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 3,
        "raw": {
          "frame": 1667,
          "previous_frame": 1666,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 1666,
                "key": "track:0",
                "bbox": [
                  613.3372802734375,
                  357.3479919433594,
                  657.471435546875,
                  537.0772705078125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 27,
              "consistent_fraction": 0.1111111111111111,
              "median_patch_error": 33.50113296508789,
              "median_forward_backward_error": 9.804609298706055,
              "discontinuity": 29.7787848578559,
              "previous_mean": 0.0,
              "adaptive_ratio": 29.7787848578559,
              "appearance_previous_mean": 11.419801712036133,
              "appearance_adaptive_ratio": 2.933600233161552
            },
            {
              "region": {
                "frame": 1666,
                "key": "track:2",
                "bbox": [
                  540.236572265625,
                  151.580078125,
                  602.9197998046875,
                  262.976318359375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 28,
              "consistent_fraction": 0.35714285714285715,
              "median_patch_error": 33.342262268066406,
              "median_forward_backward_error": 2.1054749488830566,
              "discontinuity": 21.43431145804269,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.43431145804269,
              "appearance_previous_mean": 11.43891716003418,
              "appearance_adaptive_ratio": 2.914809312944336
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9,
          "background_patch_error": 1.812074899673462,
          "discontinuity": 25.606548157949295,
          "photometric_gain": 0.978494623655914,
          "photometric_offset": 1.827956989247312,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 33.42169761657715
        },
        "decision": {
          "frame": 1667,
          "previous_frame": 1666,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 1667,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "be4460c37b6ecdd1a732c9ac84f0fd109041dca9ac9d1ee0d13075b86ec3b2d7",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              669.8752380982041,
              377.2522581219673,
              753.6151278838515,
              560.1218510270119
            ],
            [
              593.054206378758,
              216.22112257778645,
              656.0087653324008,
              369.76647494733334
            ],
            [
              792.5393781326711,
              151.2337747067213,
              830.266647849232,
              204.42021461576223
            ],
            [
              445.2382670417428,
              151.07542932406068,
              486.3619003519416,
              201.93683509156108
            ],
            [
              622.8778179995716,
              151.9826691634953,
              655.734733927995,
              205.85424315556884
            ]
          ],
          "detector_scores": [
            0.9281074145718824,
            0.9128065207973934,
            0.7608839295681536,
            0.7236374399062533,
            0.6589662626242715
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
        "frame": 1967,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 4,
        "raw": {
          "frame": 1967,
          "previous_frame": 1966,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 1966,
                "key": "track:0",
                "bbox": [
                  790.1195068359375,
                  319.45721435546875,
                  841.2181396484375,
                  495.3250427246094
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 34,
              "consistent_fraction": 0.029411764705882353,
              "median_patch_error": 22.798114776611328,
              "median_forward_backward_error": 23.293560028076172,
              "discontinuity": 22.127581989063938,
              "previous_mean": 0.0,
              "adaptive_ratio": 22.127581989063938,
              "appearance_previous_mean": 11.058514595031738,
              "appearance_adaptive_ratio": 2.0615892469729924
            },
            {
              "region": {
                "frame": 1966,
                "key": "track:1",
                "bbox": [
                  541.7399291992188,
                  203.50424194335938,
                  599.0576171875,
                  360.487548828125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 35,
              "consistent_fraction": 0.11428571428571428,
              "median_patch_error": 35.796627044677734,
              "median_forward_backward_error": 5.0268378257751465,
              "discontinuity": 31.70558395385742,
              "previous_mean": 0.0,
              "adaptive_ratio": 31.70558395385742,
              "appearance_previous_mean": 11.48405647277832,
              "appearance_adaptive_ratio": 3.117071666229582
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9375,
          "background_patch_error": 1.451247215270996,
          "discontinuity": 26.916582971460677,
          "photometric_gain": 0.989247311827957,
          "photometric_offset": -0.08602150537635112,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 29.29737091064453
        },
        "decision": {
          "frame": 1967,
          "previous_frame": 1966,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 1967,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "654fa867228cdc882bc9b1216263d61d6f5f3800217a353cc904fc8f83c19527",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              599.7788017690182,
              225.8682925477624,
              672.8944703638554,
              363.78039183467627
            ],
            [
              467.4365745186806,
              364.3889663219452,
              561.8020252585411,
              529.7007123231888
            ],
            [
              445.1087354570627,
              151.06970850750804,
              486.3851199001074,
              201.67406060174108
            ],
            [
              793.8050124868751,
              151.2901472710073,
              829.5161585584283,
              204.303262013942
            ],
            [
              623.0012090019882,
              151.93180483207107,
              655.31229807809,
              204.40728910639882
            ]
          ],
          "detector_scores": [
            0.9132717086209979,
            0.9077525846468844,
            0.6644825894485084,
            0.6314044453798674,
            0.581278022056722
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
        "frame": 2548,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 5,
        "raw": {
          "frame": 2548,
          "previous_frame": 2547,
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
                "frame": 2547,
                "key": "track:3",
                "bbox": [
                  761.4857788085938,
                  384.9604187011719,
                  853.8301391601562,
                  576.6820068359375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 40,
              "consistent_fraction": 0.0,
              "median_patch_error": 34.466339111328125,
              "median_forward_backward_error": 27.121047973632812,
              "discontinuity": 34.466339111328125,
              "previous_mean": 0.0,
              "adaptive_ratio": 34.466339111328125,
              "appearance_previous_mean": 6.675807952880859,
              "appearance_adaptive_ratio": 5.162871573687888
            },
            {
              "region": {
                "frame": 2547,
                "key": "track:2",
                "bbox": [
                  862.603515625,
                  151.04885864257812,
                  904.687744140625,
                  290.4243469238281
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.06451612903225806,
              "median_patch_error": 46.76658248901367,
              "median_forward_backward_error": 11.42039680480957,
              "discontinuity": 43.74938361875473,
              "previous_mean": 0.0,
              "adaptive_ratio": 43.74938361875473,
              "appearance_previous_mean": 10.216694831848145,
              "appearance_adaptive_ratio": 4.57746690673679
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.9188988208770752,
          "discontinuity": 39.10786136504143,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 40.6164608001709
        },
        "decision": {
          "frame": 2548,
          "previous_frame": 2547,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2548,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "a87b25976dae2c11f60174b9704e0deb099a56ee4530d88f1d6e03c465b8d4f6",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              679.1550610288978,
              380.6461798995733,
              739.3106369748712,
              568.4432186037302
            ],
            [
              757.6822814419866,
              183.41661339998245,
              811.3627808615565,
              329.39750558137894
            ],
            [
              622.5276463925838,
              151.52249493077397,
              655.7060059607029,
              204.59539410099387
            ],
            [
              444.7299626171589,
              151.1722938194871,
              486.0339510142803,
              202.9804547354579
            ],
            [
              791.2046509124339,
              151.03111930564046,
              831.2204477451742,
              202.47293327376246
            ]
          ],
          "detector_scores": [
            0.9224807068037365,
            0.9047539293614641,
            0.7911696535914442,
            0.7771719761981851,
            0.7182593896518985
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
        "frame": 2767,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 6,
        "raw": {
          "frame": 2767,
          "previous_frame": 2766,
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
                "frame": 2766,
                "key": "track:0",
                "bbox": [
                  464.9252014160156,
                  384.4781799316406,
                  560.6199340820312,
                  576.1396484375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 40,
              "consistent_fraction": 0.725,
              "median_patch_error": 26.794288635253906,
              "median_forward_backward_error": 0.3839978575706482,
              "discontinuity": 7.368429374694824,
              "previous_mean": 0.0,
              "adaptive_ratio": 7.368429374694824,
              "appearance_previous_mean": 7.593431234359741,
              "appearance_adaptive_ratio": 3.528614115054027
            },
            {
              "region": {
                "frame": 2766,
                "key": "track:2",
                "bbox": [
                  674.3124389648438,
                  192.3771514892578,
                  735.8605346679688,
                  346.74957275390625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 41,
              "consistent_fraction": 0.3170731707317073,
              "median_patch_error": 37.982357025146484,
              "median_forward_backward_error": 1.9898124933242798,
              "discontinuity": 25.939170651319547,
              "previous_mean": 0.0,
              "adaptive_ratio": 25.939170651319547,
              "appearance_previous_mean": 9.043243408203125,
              "appearance_adaptive_ratio": 4.200081244157676
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.0149872303009033,
          "discontinuity": 16.653800013007185,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 32.388322830200195
        },
        "decision": {
          "frame": 2767,
          "previous_frame": 2766,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2767,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b386312f13c2b307c809a7a50e38e4fc18dbf5f9b1ed68852ef36612604527e6",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              481.19478595256805,
              379.5957470536232,
              563.5577429533005,
              560.5283278822899
            ],
            [
              609.2515657171607,
              212.70460104942322,
              684.6855621114373,
              370.0951167047024
            ],
            [
              791.2225747741759,
              151.23864097893238,
              831.3533498607576,
              203.15276539325714
            ],
            [
              445.11980510130525,
              151.1094237715006,
              486.30220996961,
              202.32564645260572
            ],
            [
              621.7466593794525,
              151.4772314429283,
              655.39191140607,
              234.11521373689175
            ]
          ],
          "detector_scores": [
            0.9206829093852186,
            0.9200481033854003,
            0.7524838435289368,
            0.7485694579469809,
            0.6686524208323257
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [
            [
              0,
              0
            ]
          ],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 3195,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 7,
        "raw": {
          "frame": 3195,
          "previous_frame": 3194,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 3194,
                "key": "track:0",
                "bbox": [
                  591.96142578125,
                  346.16064453125,
                  637.43896484375,
                  531.5220336914062
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 38,
              "consistent_fraction": 0.13157894736842105,
              "median_patch_error": 36.97945022583008,
              "median_forward_backward_error": 4.785984039306641,
              "discontinuity": 32.113733090852435,
              "previous_mean": 0.0,
              "adaptive_ratio": 32.113733090852435,
              "appearance_previous_mean": 6.63134241104126,
              "appearance_adaptive_ratio": 5.576465206239219
            },
            {
              "region": {
                "frame": 3194,
                "key": "track:1",
                "bbox": [
                  481.7373962402344,
                  151.3708038330078,
                  543.5877685546875,
                  269.4099426269531
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.6363636363636364,
              "median_patch_error": 24.558460235595703,
              "median_forward_backward_error": 0.597750186920166,
              "discontinuity": 8.930349176580256,
              "previous_mean": 0.0,
              "adaptive_ratio": 8.930349176580256,
              "appearance_previous_mean": 8.445383548736572,
              "appearance_adaptive_ratio": 2.907915323664565
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.925,
          "background_patch_error": 1.61582350730896,
          "discontinuity": 20.522041133716346,
          "photometric_gain": 0.9891304347826086,
          "photometric_offset": -0.0760869565217348,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 30.76895523071289
        },
        "decision": {
          "frame": 3195,
          "previous_frame": 3194,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3195,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "7a087dcee8e161fa7ec710549a91fab8582fe1076c845cba52254e98c388647a",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              539.7051113173366,
              243.27137431502342,
              611.6610577777028,
              368.6518039405346
            ],
            [
              605.2731775194407,
              369.08352142572403,
              676.7492774575949,
              555.7948762774467
            ],
            [
              444.9269440472126,
              151.15209836885333,
              486.4236169755459,
              201.94886606559157
            ],
            [
              792.0986080430448,
              151.18821654841304,
              831.2243010737002,
              203.1691974811256
            ],
            [
              622.2837822958827,
              151.49012327566743,
              655.8431717827916,
              204.47569895908237
            ]
          ],
          "detector_scores": [
            0.9327674967819177,
            0.9221884212044357,
            0.6295494424180169,
            0.6242990138438045,
            0.6086070096512874
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [
            [
              0,
              1
            ]
          ],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 3371,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 8,
        "raw": {
          "frame": 3371,
          "previous_frame": 3370,
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
                "frame": 3370,
                "key": "track:2",
                "bbox": [
                  775.4005126953125,
                  329.8886413574219,
                  871.3438110351562,
                  499.8162841796875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 49,
              "consistent_fraction": 0.02040816326530612,
              "median_patch_error": 24.4010066986084,
              "median_forward_backward_error": 17.520626068115234,
              "discontinuity": 23.90302697006537,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.90302697006537,
              "appearance_previous_mean": 3.6982708871364594,
              "appearance_adaptive_ratio": 6.597950080801652
            },
            {
              "region": {
                "frame": 3370,
                "key": "track:0",
                "bbox": [
                  677.7051391601562,
                  243.06690979003906,
                  725.9183349609375,
                  404.92474365234375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.0,
              "median_patch_error": 30.651927947998047,
              "median_forward_backward_error": 12.692426681518555,
              "discontinuity": 30.651927947998047,
              "previous_mean": 0.0,
              "adaptive_ratio": 30.651927947998047,
              "appearance_previous_mean": 4.837195202708244,
              "appearance_adaptive_ratio": 6.336715113509721
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9125,
          "background_patch_error": 1.74868905544281,
          "discontinuity": 27.277477459031708,
          "photometric_gain": 0.9891304347826086,
          "photometric_offset": 0.9130434782608745,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 27.526467323303223
        },
        "decision": {
          "frame": 3371,
          "previous_frame": 3370,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3371,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "356dda8b0ad53306b10a4658ccd307481c4910363619a9537b46ef7a25a0213c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              457.3689707070589,
              357.4627791941166,
              583.7301803082228,
              534.9198313653469
            ],
            [
              611.444915316999,
              215.43247497081757,
              685.5968909040093,
              362.95126071572304
            ],
            [
              793.7185358889401,
              151.21397495642304,
              829.0254988782108,
              203.99323501065373
            ],
            [
              444.82296754419804,
              151.0869214721024,
              486.0335949510336,
              202.8267904035747
            ],
            [
              622.918463524431,
              151.8412946946919,
              655.285158816725,
              204.55907386168838
            ]
          ],
          "detector_scores": [
            0.9434489903420037,
            0.8928771247933928,
            0.6838428341884197,
            0.6590832710934159,
            0.5111338565723016
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
        "frame": 3587,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 9,
        "raw": {
          "frame": 3587,
          "previous_frame": 3586,
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
                "frame": 3586,
                "key": "track:0",
                "bbox": [
                  607.74951171875,
                  381.3083801269531,
                  688.343505859375,
                  564.15087890625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 41,
              "consistent_fraction": 0.24390243902439024,
              "median_patch_error": 35.039894104003906,
              "median_forward_backward_error": 4.961320400238037,
              "discontinuity": 26.493578468881,
              "previous_mean": 0.0,
              "adaptive_ratio": 26.493578468881,
              "appearance_previous_mean": 10.110384941101074,
              "appearance_adaptive_ratio": 3.465732937779506
            },
            {
              "region": {
                "frame": 3586,
                "key": "track:1",
                "bbox": [
                  513.7266845703125,
                  207.8861846923828,
                  593.7724609375,
                  364.7188720703125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 42,
              "consistent_fraction": 0.47619047619047616,
              "median_patch_error": 33.31147003173828,
              "median_forward_backward_error": 1.4761167764663696,
              "discontinuity": 17.448865254720054,
              "previous_mean": 0.0,
              "adaptive_ratio": 17.448865254720054,
              "appearance_previous_mean": 9.501381874084473,
              "appearance_adaptive_ratio": 3.505960551127526
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 1.7662982940673828,
          "discontinuity": 21.97122186180053,
          "photometric_gain": 0.9891304347826086,
          "photometric_offset": -0.0760869565217348,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 34.175682067871094
        },
        "decision": {
          "frame": 3587,
          "previous_frame": 3586,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3587,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "1fdbde24415286077b47fa1544a2dfcf3ab8f947947a3c1a0c26ed74bc09ee5f",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              595.2497527077794,
              221.2479312568903,
              666.8685495182872,
              369.1678729504347
            ],
            [
              615.2027615606785,
              355.9188406765461,
              725.8363920152187,
              533.3206631839275
            ],
            [
              444.9192600212991,
              151.11744301766157,
              486.5727607049048,
              203.0289659127593
            ],
            [
              793.2360128574073,
              151.16035756096244,
              829.4476722069085,
              203.96336805447936
            ],
            [
              623.3120688125491,
              152.26204412430525,
              655.8241254165769,
              205.5147217437625
            ]
          ],
          "detector_scores": [
            0.9251443098684264,
            0.9239675096832602,
            0.6910146729908119,
            0.68964833325465,
            0.5982992449495818
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [
            [
              0,
              1
            ]
          ],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 3719,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 10,
        "raw": {
          "frame": 3719,
          "previous_frame": 3718,
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
                "frame": 3718,
                "key": "track:1",
                "bbox": [
                  657.0791625976562,
                  360.4172668457031,
                  744.1630249023438,
                  541.8636474609375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 43,
              "consistent_fraction": 0.5813953488372093,
              "median_patch_error": 25.932682037353516,
              "median_forward_backward_error": 0.6925874948501587,
              "discontinuity": 10.855541317961936,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.855541317961936,
              "appearance_previous_mean": 6.066999673843384,
              "appearance_adaptive_ratio": 4.274383291819994
            },
            {
              "region": {
                "frame": 3718,
                "key": "track:0",
                "bbox": [
                  505.0137939453125,
                  176.4359130859375,
                  572.034423828125,
                  315.19683837890625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 38,
              "consistent_fraction": 0.18421052631578946,
              "median_patch_error": 40.792198181152344,
              "median_forward_backward_error": 6.071180820465088,
              "discontinuity": 33.27784588462428,
              "previous_mean": 0.0,
              "adaptive_ratio": 33.27784588462428,
              "appearance_previous_mean": 10.32998514175415,
              "appearance_adaptive_ratio": 3.9489116026187583
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.2501771450042725,
          "discontinuity": 22.066693601293107,
          "photometric_gain": 0.9891304347826086,
          "photometric_offset": -0.0760869565217348,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 33.36244010925293
        },
        "decision": {
          "frame": 3719,
          "previous_frame": 3718,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3719,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "754cb138ad251b22dea03b1eecd571d7eae92062daa70fb410ba1d9a03731a86",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              541.5671108737588,
              248.45919093489647,
              608.476627252996,
              372.44197329878807
            ],
            [
              609.4432273209095,
              376.66823810338974,
              690.8755194842815,
              558.0396253466606
            ],
            [
              793.3588245026767,
              151.14341190457344,
              829.2932855971158,
              204.16150657832623
            ],
            [
              444.62850118801,
              151.13759216293693,
              486.30772291496396,
              202.51232229545712
            ],
            [
              622.6580138206482,
              151.93363178893924,
              655.5227239131927,
              204.5902331583202
            ],
            [
              1018.5632147807628,
              152.44513972103596,
              1041.9878840427846,
              240.64815892279148
            ]
          ],
          "detector_scores": [
            0.9369785292987912,
            0.8958709977107377,
            0.7467534929736541,
            0.7400643943896966,
            0.7234232080417322,
            0.5088888577392855
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
        "frame": 3936,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 11,
        "raw": {
          "frame": 3936,
          "previous_frame": 3935,
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
                "frame": 3935,
                "key": "track:1",
                "bbox": [
                  494.23931884765625,
                  384.9320373535156,
                  562.01171875,
                  569.207763671875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 43,
              "consistent_fraction": 0.0,
              "median_patch_error": 37.6995849609375,
              "median_forward_backward_error": 46.148193359375,
              "discontinuity": 37.6995849609375,
              "previous_mean": 0.0,
              "adaptive_ratio": 37.6995849609375,
              "appearance_previous_mean": 6.119029998779297,
              "appearance_adaptive_ratio": 6.161039407954904
            },
            {
              "region": {
                "frame": 3935,
                "key": "track:0",
                "bbox": [
                  359.8103942871094,
                  152.11447143554688,
                  400.6177978515625,
                  290.2604064941406
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 27,
              "consistent_fraction": 0.4444444444444444,
              "median_patch_error": 24.645620346069336,
              "median_forward_backward_error": 2.1007304191589355,
              "discontinuity": 13.692011303371855,
              "previous_mean": 0.0,
              "adaptive_ratio": 13.692011303371855,
              "appearance_previous_mean": 7.193700313568115,
              "appearance_adaptive_ratio": 3.4260004270104174
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.584183692932129,
          "discontinuity": 25.69579813215468,
          "photometric_gain": 0.9891304347826086,
          "photometric_offset": 0.9130434782608745,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 31.172602653503418
        },
        "decision": {
          "frame": 3936,
          "previous_frame": 3935,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3936,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "8ce59802a9ade8ce3c1a096d29dd5a4088548405eb4a9de9cbf9f88b2096a82c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              571.8974472656846,
              374.88093546032906,
              659.6499163731933,
              557.7154709994793
            ],
            [
              676.7202160581946,
              235.4644171744585,
              770.7032005563378,
              367.84407852590084
            ],
            [
              793.321449931711,
              151.17155714333057,
              829.354510370642,
              204.1093541160226
            ],
            [
              444.98775089904666,
              151.1230712234974,
              487.0749848969281,
              203.02824607491493
            ],
            [
              622.9956734254956,
              151.8859541080892,
              655.7673182412982,
              204.55649759992957
            ],
            [
              1018.7868315521628,
              155.10780727863312,
              1042.0,
              242.5967220813036
            ]
          ],
          "detector_scores": [
            0.9262218217824424,
            0.9231796893087392,
            0.7456778120697007,
            0.7208096089590985,
            0.7176399667997799,
            0.42694388068538647
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
        "frame": 4141,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 12,
        "raw": {
          "frame": 4141,
          "previous_frame": 4140,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 4140,
                "key": "track:0",
                "bbox": [
                  706.0028686523438,
                  332.2101135253906,
                  819.197509765625,
                  526.0428466796875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 41,
              "consistent_fraction": 0.0,
              "median_patch_error": 31.635841369628906,
              "median_forward_backward_error": 30.753034591674805,
              "discontinuity": 31.635841369628906,
              "previous_mean": 0.2651489010809747,
              "adaptive_ratio": 31.635841369628906,
              "appearance_previous_mean": 11.00880479812622,
              "appearance_adaptive_ratio": 2.8736853772730675
            },
            {
              "region": {
                "frame": 4140,
                "key": "track:1",
                "bbox": [
                  692.9231567382812,
                  220.86026000976562,
                  777.9652709960938,
                  348.67413330078125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 37,
              "consistent_fraction": 0.43243243243243246,
              "median_patch_error": 30.15972137451172,
              "median_forward_backward_error": 1.508225440979004,
              "discontinuity": 17.11767969904719,
              "previous_mean": 0.0,
              "adaptive_ratio": 17.11767969904719,
              "appearance_previous_mean": 10.82217264175415,
              "appearance_adaptive_ratio": 2.7868453380746634
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9125,
          "background_patch_error": 1.356328010559082,
          "discontinuity": 24.376760534338047,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 30.897781372070312
        },
        "decision": {
          "frame": 4141,
          "previous_frame": 4140,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 4141,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "e242df1b7246a1e17c172a7d7953fd548cf32e8ca7cb713902c5e2c55bf2df6b",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              596.1831815615296,
              368.65938960015774,
              676.9418925866485,
              542.7035011202097
            ],
            [
              703.4468302950263,
              247.85167726129293,
              795.6714658513665,
              385.6464303508401
            ],
            [
              793.536927036941,
              151.1200782135129,
              829.4677218869328,
              204.1019115820527
            ],
            [
              623.2481509335339,
              151.8354875817895,
              655.7013937346637,
              204.23166340589523
            ],
            [
              445.945554997772,
              151.0862984545529,
              486.32642528787255,
              202.42576495185494
            ]
          ],
          "detector_scores": [
            0.9061156055174613,
            0.8868608039273109,
            0.7513287308435302,
            0.7472923657445207,
            0.7337996057234983
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
        "frame": 4530,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 13,
        "raw": {
          "frame": 4530,
          "previous_frame": 4529,
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
                "frame": 4529,
                "key": "track:1",
                "bbox": [
                  333.3499755859375,
                  247.27894592285156,
                  424.2557678222656,
                  417.036865234375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 48,
              "consistent_fraction": 0.2708333333333333,
              "median_patch_error": 34.052650451660156,
              "median_forward_backward_error": 5.534701347351074,
              "discontinuity": 24.8300576210022,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.8300576210022,
              "appearance_previous_mean": 9.359587669372559,
              "appearance_adaptive_ratio": 3.6382639550555065
            },
            {
              "region": {
                "frame": 4529,
                "key": "track:0",
                "bbox": [
                  521.21044921875,
                  320.71240234375,
                  597.4645385742188,
                  482.5467224121094
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 39,
              "consistent_fraction": 0.10256410256410256,
              "median_patch_error": 35.18512725830078,
              "median_forward_backward_error": 11.515429496765137,
              "discontinuity": 31.57639625744942,
              "previous_mean": 0.0,
              "adaptive_ratio": 31.57639625744942,
              "appearance_previous_mean": 9.875904083251953,
              "appearance_adaptive_ratio": 3.562724684413396
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.925,
          "background_patch_error": 8.175737380981445,
          "discontinuity": 28.20322693922581,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 34.61888885498047
        },
        "decision": {
          "frame": 4530,
          "previous_frame": 4529,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 4530,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "4798a977aa3d8604611be69c3419b8a9b25a9958139973cdcec03944476b933c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              591.0080587565899,
              217.564314737916,
              668.0646112263203,
              369.75913344323635
            ],
            [
              673.8462123349309,
              376.67133635282516,
              757.2345047518611,
              558.5143310427666
            ],
            [
              793.3933822512627,
              151.1053025946021,
              829.0606842637062,
              203.94826198369265
            ],
            [
              446.0916933119297,
              151.1358620263636,
              486.1729001700878,
              203.07361480221152
            ],
            [
              623.1076115630567,
              151.8842239715159,
              655.9602185226977,
              209.17948987707496
            ]
          ],
          "detector_scores": [
            0.9169324433020472,
            0.9155031516852873,
            0.6848591724108645,
            0.6681620391899521,
            0.5981814286910294
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
        "frame": 5108,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 14,
        "raw": {
          "frame": 5108,
          "previous_frame": 5107,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 5107,
                "key": "track:2",
                "bbox": [
                  337.9595031738281,
                  366.8771057128906,
                  424.8827819824219,
                  541.2349853515625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 58,
              "consistent_fraction": 0.25862068965517243,
              "median_patch_error": 27.633892059326172,
              "median_forward_backward_error": 5.1169233322143555,
              "discontinuity": 20.487195837086645,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.487195837086645,
              "appearance_previous_mean": 7.610119007527828,
              "appearance_adaptive_ratio": 3.6312036686931037
            },
            {
              "region": {
                "frame": 5107,
                "key": "track:0",
                "bbox": [
                  447.7589111328125,
                  202.9600067138672,
                  523.8369750976562,
                  307.0494689941406
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 28,
              "consistent_fraction": 0.7857142857142857,
              "median_patch_error": 16.3001708984375,
              "median_forward_backward_error": 0.3566722273826599,
              "discontinuity": 3.4928937639508932,
              "previous_mean": 0.0,
              "adaptive_ratio": 3.4928937639508932,
              "appearance_previous_mean": 4.862758696079254,
              "appearance_adaptive_ratio": 3.352041899915783
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.1014385223388672,
          "discontinuity": 11.990044800518769,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 21.967031478881836
        },
        "decision": {
          "frame": 5108,
          "previous_frame": 5107,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 5108,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "05881963c586827aac45b444377ad51b10fb58859e97ac09bd200f559009f221",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              577.0120694935322,
              375.14165146648884,
              663.3176725804806,
              558.1287589520216
            ],
            [
              512.7591409981251,
              244.6265006288886,
              611.0821079909801,
              376.8621859923005
            ],
            [
              446.9145690537989,
              151.17416708171368,
              484.90425738319755,
              203.41622183471918
            ],
            [
              793.6752455383539,
              151.14726366847754,
              829.2032000869513,
              203.8858507797122
            ],
            [
              623.5589337982237,
              152.08420418575406,
              655.6223537288606,
              204.4993946738541
            ]
          ],
          "detector_scores": [
            0.9294577574833932,
            0.9238335412930289,
            0.8058146858158572,
            0.774857100676177,
            0.7525591482723478
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
        "frame": 5366,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 15,
        "raw": {
          "frame": 5366,
          "previous_frame": 5365,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 5365,
                "key": "track:0",
                "bbox": [
                  390.962890625,
                  496.74493408203125,
                  464.1679382324219,
                  715.3302001953125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 43,
              "consistent_fraction": 0.023255813953488372,
              "median_patch_error": 31.810726165771484,
              "median_forward_backward_error": 42.98644256591797,
              "discontinuity": 31.07094183633494,
              "previous_mean": 0.7026565490605401,
              "adaptive_ratio": 31.07094183633494,
              "appearance_previous_mean": 11.809488296508789,
              "appearance_adaptive_ratio": 2.693658299756782
            },
            {
              "region": {
                "frame": 5365,
                "key": "track:1",
                "bbox": [
                  777.4174194335938,
                  221.05194091796875,
                  850.0545654296875,
                  383.1272888183594
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 48,
              "consistent_fraction": 0.25,
              "median_patch_error": 22.43027114868164,
              "median_forward_backward_error": 8.320993423461914,
              "discontinuity": 16.82270336151123,
              "previous_mean": 0.0,
              "adaptive_ratio": 16.82270336151123,
              "appearance_previous_mean": 8.837868213653564,
              "appearance_adaptive_ratio": 2.537973027706983
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9,
          "background_patch_error": 1.5176091194152832,
          "discontinuity": 23.946822598923085,
          "photometric_gain": 0.9891304347826086,
          "photometric_offset": 1.9021739130434838,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 27.120498657226562
        },
        "decision": {
          "frame": 5366,
          "previous_frame": 5365,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 5366,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "4ce49a32fb78e746dc270baf16424fd9192127fc882d7209cdc419fc59ca9ae5",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              590.7629605084658,
              366.4793417453766,
              662.5607485026121,
              553.9662019014359
            ],
            [
              695.1546815484762,
              244.23148645460606,
              769.5195769220591,
              372.1649241298437
            ],
            [
              445.8370975293219,
              151.12359952554107,
              485.1740084849298,
              203.79637830331922
            ],
            [
              794.1639136783779,
              151.1293413899839,
              828.9552548415959,
              204.43409148976207
            ],
            [
              623.5972105972469,
              151.77475599944592,
              655.3606381900609,
              204.49182795733213
            ]
          ],
          "detector_scores": [
            0.9458469364797786,
            0.9321263870750909,
            0.7504502547415197,
            0.739014564011844,
            0.7199074601856407
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
        "frame": 5701,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 16,
        "raw": {
          "frame": 5701,
          "previous_frame": 5700,
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
                "frame": 5700,
                "key": "track:2",
                "bbox": [
                  782.361572265625,
                  353.114013671875,
                  863.9817504882812,
                  533.2490844726562
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 38,
              "consistent_fraction": 0.05263157894736842,
              "median_patch_error": 24.71967124938965,
              "median_forward_backward_error": 11.022396087646484,
              "discontinuity": 23.418635920474404,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.418635920474404,
              "appearance_previous_mean": 6.916259348392487,
              "appearance_adaptive_ratio": 3.5741388522590793
            },
            {
              "region": {
                "frame": 5700,
                "key": "track:1",
                "bbox": [
                  908.3316650390625,
                  155.69464111328125,
                  970.2926635742188,
                  299.5162048339844
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 35,
              "consistent_fraction": 0.11428571428571428,
              "median_patch_error": 36.69416046142578,
              "median_forward_backward_error": 6.775211334228516,
              "discontinuity": 32.500542122977116,
              "previous_mean": 0.16806447121404816,
              "adaptive_ratio": 32.500542122977116,
              "appearance_previous_mean": 5.699511080980301,
              "appearance_adaptive_ratio": 6.438124242599855
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.5375,
          "background_patch_error": 2.3934240341186523,
          "discontinuity": 27.959589021725762,
          "photometric_gain": 1.0108695652173914,
          "photometric_offset": -1.9130434782608745,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 30.706915855407715
        },
        "decision": {
          "frame": 5701,
          "previous_frame": 5700,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 5701,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "dc7300989b26a05d047ae95684d1d263f7ab7469d1193fb14d02dc5d677d63bf",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              621.7308070212603,
              213.1457900851965,
              688.8579142540693,
              371.0504130870104
            ],
            [
              482.3309988602996,
              374.60165521502495,
              562.5728871002793,
              561.6980349123478
            ],
            [
              443.6866626031697,
              151.14328561723232,
              485.08489007875323,
              204.45248524099588
            ],
            [
              791.5739941112697,
              151.20181769505143,
              831.1481216438115,
              203.14892836287618
            ],
            [
              622.3436582535505,
              151.44106274843216,
              655.5679680854082,
              204.84798351675272
            ],
            [
              620.6986928246915,
              151.32975729554892,
              655.8112754561007,
              237.81523498147726
            ]
          ],
          "detector_scores": [
            0.917658147261322,
            0.9119081040365254,
            0.8050055618914558,
            0.7604557018505632,
            0.5261333046766526,
            0.432566010491044
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
        "frame": 6562,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 17,
        "raw": {
          "frame": 6562,
          "previous_frame": 6561,
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
                "frame": 6561,
                "key": "track:1",
                "bbox": [
                  796.4881591796875,
                  512.3969116210938,
                  870.3768310546875,
                  714.646484375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 50,
              "consistent_fraction": 0.0,
              "median_patch_error": 38.70216751098633,
              "median_forward_backward_error": 63.94248962402344,
              "discontinuity": 38.70216751098633,
              "previous_mean": 0.0,
              "adaptive_ratio": 38.70216751098633,
              "appearance_previous_mean": 6.947845697402954,
              "appearance_adaptive_ratio": 5.570383856603619
            },
            {
              "region": {
                "frame": 6561,
                "key": "track:2",
                "bbox": [
                  767.4655151367188,
                  173.7581329345703,
                  813.4671020507812,
                  322.03717041015625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 32,
              "consistent_fraction": 0.1875,
              "median_patch_error": 49.63059997558594,
              "median_forward_backward_error": 12.628988265991211,
              "discontinuity": 40.324862480163574,
              "previous_mean": 0.0,
              "adaptive_ratio": 40.324862480163574,
              "appearance_previous_mean": 9.578815937042236,
              "appearance_adaptive_ratio": 5.181287572679986
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.8,
          "background_patch_error": 1.3407738208770752,
          "discontinuity": 39.51351499557495,
          "photometric_gain": 0.9891304347826086,
          "photometric_offset": 0.9130434782608745,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 44.16638374328613
        },
        "decision": {
          "frame": 6562,
          "previous_frame": 6561,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 6562,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "14cf8814e1e1e5dce2ca0ad481ab8566dcaf3506c301ca4b3eaceaf25cb5a6c8",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              513.3613767176867,
              358.47754849493504,
              607.7741778343916,
              527.2160762399435
            ],
            [
              628.6065814346075,
              236.1253293454647,
              737.518543496728,
              364.77397432923317
            ],
            [
              445.2350549288094,
              151.15646370127797,
              486.37032667919993,
              202.65966594591737
            ],
            [
              791.6360818855464,
              151.2448564209044,
              831.8275144584477,
              202.9764324836433
            ],
            [
              624.4112360551953,
              151.42415708303452,
              656.293374530971,
              204.4411656856537
            ],
            [
              1020.3469490706921,
              152.57980412244797,
              1042.0,
              235.6106158196926
            ]
          ],
          "detector_scores": [
            0.9251365162852861,
            0.907293332317353,
            0.7486378390292742,
            0.7486033808153899,
            0.728744438791001,
            0.38981706160233437
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
        "frame": 6823,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 18,
        "raw": {
          "frame": 6823,
          "previous_frame": 6822,
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
                "frame": 6822,
                "key": "track:0",
                "bbox": [
                  646.1904296875,
                  395.2147521972656,
                  723.37841796875,
                  587.9050903320312
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 42,
              "consistent_fraction": 0.4523809523809524,
              "median_patch_error": 25.756732940673828,
              "median_forward_backward_error": 1.0759663581848145,
              "discontinuity": 14.104877562749955,
              "previous_mean": 0.0,
              "adaptive_ratio": 14.104877562749955,
              "appearance_previous_mean": 3.4892820939421654,
              "appearance_adaptive_ratio": 7.381671142436655
            },
            {
              "region": {
                "frame": 6822,
                "key": "track:1",
                "bbox": [
                  954.8239135742188,
                  151.00152587890625,
                  1021.5365600585938,
                  282.4638366699219
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 35,
              "consistent_fraction": 0.22857142857142856,
              "median_patch_error": 24.288265228271484,
              "median_forward_backward_error": 8.079251289367676,
              "discontinuity": 18.736661747523716,
              "previous_mean": 0.0,
              "adaptive_ratio": 18.736661747523716,
              "appearance_previous_mean": 4.511284589767456,
              "appearance_adaptive_ratio": 5.383891161147844
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.6513252258300781,
          "discontinuity": 16.420769655136837,
          "photometric_gain": 0.989010989010989,
          "photometric_offset": 0.9230769230769198,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 25.022499084472656
        },
        "decision": {
          "frame": 6823,
          "previous_frame": 6822,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 6823,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "eb13dcebb65d96a8fa0b2acd4175a75333f4e73695315abc3be0e83c0ca98783",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              680.9639136195183,
              406.41335225105286,
              790.0342212319374,
              554.7629908323288
            ],
            [
              594.7945288643241,
              227.44540674984455,
              672.4277649894357,
              369.07660929858685
            ],
            [
              791.0014232881367,
              151.20097998902202,
              831.4015632383525,
              203.17036774381995
            ],
            [
              446.1266629472375,
              151.0865468196571,
              485.94708063453436,
              202.28280768170953
            ],
            [
              624.4361906573176,
              151.3250446729362,
              655.9367379620671,
              205.17758716270328
            ]
          ],
          "detector_scores": [
            0.9416052018978948,
            0.9348099469386287,
            0.6980921296909374,
            0.691239630263639,
            0.6074519283568519
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
        "frame": 7090,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 19,
        "raw": {
          "frame": 7090,
          "previous_frame": 7089,
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
                "frame": 7089,
                "key": "track:0",
                "bbox": [
                  663.6058349609375,
                  315.33135986328125,
                  730.4653930664062,
                  487.54052734375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 38,
              "consistent_fraction": 0.02631578947368421,
              "median_patch_error": 33.078125,
              "median_forward_backward_error": 27.63378143310547,
              "discontinuity": 32.20764802631579,
              "previous_mean": 0.0,
              "adaptive_ratio": 32.20764802631579,
              "appearance_previous_mean": 4.081863112747669,
              "appearance_adaptive_ratio": 8.10368306979647
            },
            {
              "region": {
                "frame": 7089,
                "key": "track:1",
                "bbox": [
                  846.615234375,
                  218.9364776611328,
                  901.9234619140625,
                  386.916015625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 45,
              "consistent_fraction": 0.24444444444444444,
              "median_patch_error": 32.07971954345703,
              "median_forward_backward_error": 20.850067138671875,
              "discontinuity": 24.23801032172309,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.23801032172309,
              "appearance_previous_mean": 3.1427509486675262,
              "appearance_adaptive_ratio": 10.207528393892712
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9375,
          "background_patch_error": 1.0669996738433838,
          "discontinuity": 28.222829174019438,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 32.578922271728516
        },
        "decision": {
          "frame": 7090,
          "previous_frame": 7089,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7090,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "9445db912657aaa83230fe262e97f8a4d749c19bbb1ff4608d7b7be18118de8c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              609.1951749548316,
              216.40806993842125,
              693.3526484742761,
              360.61065113544464
            ],
            [
              467.4867673665285,
              347.32920511066914,
              568.251205727458,
              531.7089757174253
            ],
            [
              790.7821803614497,
              151.26069916784763,
              831.2637290433049,
              202.99181217700243
            ],
            [
              444.6586262509227,
              151.1325848698616,
              485.89150459319353,
              202.30636658519506
            ],
            [
              624.4599518440664,
              151.31307684257627,
              656.0444908477366,
              204.6497144959867
            ],
            [
              1021.269382962957,
              152.39011211693287,
              1041.985382547602,
              235.33647125959396
            ]
          ],
          "detector_scores": [
            0.9413003460165265,
            0.9290619920752895,
            0.7818184750738122,
            0.7458013176995023,
            0.5384524839797882,
            0.36067550378261637
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
        "frame": 7316,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 20,
        "raw": {
          "frame": 7316,
          "previous_frame": 7315,
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
                "frame": 7315,
                "key": "track:1",
                "bbox": [
                  957.5531005859375,
                  367.4803466796875,
                  1019.3704833984375,
                  551.7565307617188
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 40,
              "consistent_fraction": 0.125,
              "median_patch_error": 39.93013000488281,
              "median_forward_backward_error": 12.605544090270996,
              "discontinuity": 34.93886375427246,
              "previous_mean": 0.0,
              "adaptive_ratio": 34.93886375427246,
              "appearance_previous_mean": 7.143920183181763,
              "appearance_adaptive_ratio": 5.5893863566514135
            },
            {
              "region": {
                "frame": 7315,
                "key": "track:0",
                "bbox": [
                  784.7001342773438,
                  204.06887817382812,
                  843.3622436523438,
                  359.4896545410156
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 39,
              "consistent_fraction": 0.1282051282051282,
              "median_patch_error": 39.99333953857422,
              "median_forward_backward_error": 13.621450424194336,
              "discontinuity": 34.86598831568009,
              "previous_mean": 0.0,
              "adaptive_ratio": 34.86598831568009,
              "appearance_previous_mean": 8.53589153289795,
              "appearance_adaptive_ratio": 4.685314871262945
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 2.225269317626953,
          "discontinuity": 34.90242603497627,
          "photometric_gain": 0.967741935483871,
          "photometric_offset": 3.6774193548387046,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 39.961734771728516
        },
        "decision": {
          "frame": 7316,
          "previous_frame": 7315,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7316,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "522219a6710ac56080acd5f76fd307a2aafed9e4a094455901801dcb558f4ba6",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              600.8126223534346,
              234.26935164630413,
              671.441726282239,
              369.25571842491627
            ],
            [
              623.7411672696471,
              362.98044151067734,
              715.6705720797181,
              529.0055931210518
            ],
            [
              445.5842126607895,
              151.01212989911437,
              484.5042188167572,
              203.8783387877047
            ],
            [
              790.7928094528615,
              151.26800910010934,
              831.4575164653361,
              203.15269593521953
            ],
            [
              623.9785543344915,
              151.49019694328308,
              656.201255235821,
              204.7276316806674
            ]
          ],
          "detector_scores": [
            0.9308862736205273,
            0.9253771123202376,
            0.8520369224136112,
            0.8365951082703348,
            0.71885900162809
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
        "frame": 7478,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 21,
        "raw": {
          "frame": 7478,
          "previous_frame": 7477,
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
                "frame": 7477,
                "key": "track:1",
                "bbox": [
                  565.7269287109375,
                  335.8653259277344,
                  625.8790283203125,
                  511.1720886230469
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 37,
              "consistent_fraction": 0.6486486486486487,
              "median_patch_error": 32.60090637207031,
              "median_forward_backward_error": 0.5138237476348877,
              "discontinuity": 11.454372509105784,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.454372509105784,
              "appearance_previous_mean": 1.9658446609973907,
              "appearance_adaptive_ratio": 16.583663510589854
            },
            {
              "region": {
                "frame": 7477,
                "key": "track:0",
                "bbox": [
                  777.7899169921875,
                  179.60455322265625,
                  811.8869018554688,
                  322.8486633300781
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.0,
              "median_patch_error": 52.360260009765625,
              "median_forward_backward_error": 10.402121543884277,
              "discontinuity": 52.360260009765625,
              "previous_mean": 0.0,
              "adaptive_ratio": 52.360260009765625,
              "appearance_previous_mean": 4.514101803302765,
              "appearance_adaptive_ratio": 11.599264325730532
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.775,
          "background_patch_error": 4.7177581787109375,
          "discontinuity": 31.907316259435703,
          "photometric_gain": 0.989010989010989,
          "photometric_offset": -0.0769230769230802,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 42.48058319091797
        },
        "decision": {
          "frame": 7478,
          "previous_frame": 7477,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7478,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "975627f99b7856d80e4199c5f7b45c7d9f2dcfa4b94fdbeed602b261367867f7",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              694.6921131461859,
              236.89718494564295,
              774.34509088099,
              371.9732746705413
            ],
            [
              581.5399628579617,
              363.310506105423,
              673.2136961519718,
              549.7560850381851
            ],
            [
              445.92310943454504,
              151.050159227103,
              484.3885193839669,
              203.95329874381423
            ],
            [
              624.362992502749,
              151.34700183197856,
              656.1913714632392,
              204.40064218267798
            ],
            [
              791.6957360580564,
              151.2190432883799,
              830.7662483379245,
              203.17562129721045
            ]
          ],
          "detector_scores": [
            0.9381553949775184,
            0.9341040709648956,
            0.8068990601073663,
            0.7864869722337562,
            0.7819030548695356
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [
            [
              0,
              1
            ]
          ],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 7631,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 22,
        "raw": {
          "frame": 7631,
          "previous_frame": 7630,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 7630,
                "key": "track:1",
                "bbox": [
                  305.0599365234375,
                  346.3556213378906,
                  387.3372802734375,
                  527.859130859375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 46,
              "consistent_fraction": 0.3695652173913043,
              "median_patch_error": 21.52458953857422,
              "median_forward_backward_error": 2.505702018737793,
              "discontinuity": 13.569849926492443,
              "previous_mean": 0.0,
              "adaptive_ratio": 13.569849926492443,
              "appearance_previous_mean": 11.768176078796387,
              "appearance_adaptive_ratio": 1.8290506017628934
            },
            {
              "region": {
                "frame": 7630,
                "key": "track:0",
                "bbox": [
                  427.8429260253906,
                  216.485595703125,
                  482.9195251464844,
                  375.938232421875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 38,
              "consistent_fraction": 0.18421052631578946,
              "median_patch_error": 32.62737274169922,
              "median_forward_backward_error": 14.638360977172852,
              "discontinuity": 26.617067236649362,
              "previous_mean": 0.0,
              "adaptive_ratio": 26.617067236649362,
              "appearance_previous_mean": 9.622041702270508,
              "appearance_adaptive_ratio": 3.3908991200900904
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.3998370170593262,
          "discontinuity": 20.093458581570903,
          "photometric_gain": 0.989010989010989,
          "photometric_offset": -0.0769230769230802,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 27.07598114013672
        },
        "decision": {
          "frame": 7631,
          "previous_frame": 7630,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7631,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "9a1cbd5a20bc4da30224413bc282a0a0f54514ff66f31ff6b2bc546776598e38",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              550.8440370187163,
              252.64572574198246,
              622.4448134079576,
              374.49898360669613
            ],
            [
              596.3951870501041,
              365.3231390416622,
              669.4183516204357,
              554.5119147598743
            ],
            [
              791.2771369405091,
              151.16657300293446,
              830.8555794768035,
              202.8669518828392
            ],
            [
              623.6177249699831,
              151.37973761558533,
              656.0588163584471,
              204.38449634611607
            ],
            [
              445.1676714681089,
              151.11104656383395,
              486.0254975296557,
              201.92978404834867
            ]
          ],
          "detector_scores": [
            0.9351135308800717,
            0.9200790699687343,
            0.7238117256401261,
            0.7217616882147175,
            0.7140242637014428
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
        "frame": 8267,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 23,
        "raw": {
          "frame": 8267,
          "previous_frame": 8266,
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
                "frame": 8266,
                "key": "track:1",
                "bbox": [
                  777.6992797851562,
                  490.674072265625,
                  864.3963012695312,
                  705.9630737304688
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 50,
              "consistent_fraction": 0.0,
              "median_patch_error": 33.2707633972168,
              "median_forward_backward_error": 55.895957946777344,
              "discontinuity": 33.2707633972168,
              "previous_mean": 0.0,
              "adaptive_ratio": 33.2707633972168,
              "appearance_previous_mean": 5.071375370025635,
              "appearance_adaptive_ratio": 6.560501041564316
            },
            {
              "region": {
                "frame": 8266,
                "key": "track:0",
                "bbox": [
                  533.5979614257812,
                  196.84951782226562,
                  579.484375,
                  355.5962219238281
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 35,
              "consistent_fraction": 0.17142857142857143,
              "median_patch_error": 37.274803161621094,
              "median_forward_backward_error": 14.8406343460083,
              "discontinuity": 30.88483690534319,
              "previous_mean": 0.0,
              "adaptive_ratio": 30.88483690534319,
              "appearance_previous_mean": 10.963452816009521,
              "appearance_adaptive_ratio": 3.3999145877829737
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.8125,
          "background_patch_error": 1.894486904144287,
          "discontinuity": 32.077800151279995,
          "photometric_gain": 0.989010989010989,
          "photometric_offset": 1.9120879120879124,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 35.272783279418945
        },
        "decision": {
          "frame": 8267,
          "previous_frame": 8266,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 8267,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b08c3df54de3d43197f050d599d5e7d56e9b05e03250cf9eb3871e755600e19f",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              615.5214079916477,
              215.6782722324133,
              681.9266241490841,
              371.60486502945423
            ],
            [
              482.18596947193146,
              379.5433967411518,
              563.040763258934,
              560.6553055942059
            ],
            [
              791.33000177145,
              151.22282348945737,
              830.8508978486061,
              203.15486386790872
            ],
            [
              444.97925969585776,
              151.1121242158115,
              486.4984702207148,
              202.96934355422854
            ],
            [
              621.194780960679,
              151.26830166578293,
              656.1305359452963,
              237.42119742929935
            ],
            [
              1021.3244935572147,
              153.07384441047907,
              1041.9891732633114,
              234.80116868764162
            ],
            [
              623.7252937890589,
              151.49726692959666,
              655.9189000986516,
              205.3072590045631
            ]
          ],
          "detector_scores": [
            0.9109116372900058,
            0.9104418363691358,
            0.8051546196873923,
            0.7903149120863231,
            0.5222685744436355,
            0.3701511839052454,
            0.35708362956831424
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
        "frame": 8462,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 24,
        "raw": {
          "frame": 8462,
          "previous_frame": 8461,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 8461,
                "key": "track:0",
                "bbox": [
                  456.4125671386719,
                  218.439208984375,
                  504.2285461425781,
                  383.3536376953125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 35,
              "consistent_fraction": 0.14285714285714285,
              "median_patch_error": 23.960813522338867,
              "median_forward_backward_error": 12.796174049377441,
              "discontinuity": 20.537840162004745,
              "previous_mean": 0.20908861160278316,
              "adaptive_ratio": 20.537840162004745,
              "appearance_previous_mean": 12.619739055633545,
              "appearance_adaptive_ratio": 1.898677414541514
            },
            {
              "region": {
                "frame": 8461,
                "key": "track:1",
                "bbox": [
                  365.9136047363281,
                  428.87353515625,
                  433.5938415527344,
                  566.8062133789062
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 35,
              "consistent_fraction": 0.02857142857142857,
              "median_patch_error": 29.688350677490234,
              "median_forward_backward_error": 11.526407241821289,
              "discontinuity": 28.8401120867048,
              "previous_mean": 0.0,
              "adaptive_ratio": 28.8401120867048,
              "appearance_previous_mean": 10.67127275466919,
              "appearance_adaptive_ratio": 2.7820815154874725
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.875,
          "background_patch_error": 1.7028415203094482,
          "discontinuity": 24.688976124354774,
          "photometric_gain": 0.989010989010989,
          "photometric_offset": 0.9230769230769198,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 26.82458209991455
        },
        "decision": {
          "frame": 8462,
          "previous_frame": 8461,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 8462,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "d1e3f5eb5873c3054d0dac5148a77119051274a48c74c37dc6010eedc903c49a",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              685.4394596517086,
              402.87286980450153,
              792.4715646803379,
              554.583957478404
            ],
            [
              598.2645251303911,
              233.99659624695778,
              694.408831641078,
              369.37797299027443
            ],
            [
              791.0256099402905,
              151.22696571424603,
              830.9684469997883,
              203.35048295930028
            ],
            [
              445.22767566889524,
              151.16361156478524,
              486.3542902544141,
              202.89422784373164
            ],
            [
              623.4780667051673,
              151.5632920563221,
              656.0478417649865,
              204.63439794629812
            ]
          ],
          "detector_scores": [
            0.9384346460862958,
            0.9367162731348283,
            0.7523598413766159,
            0.7495088383069038,
            0.6506055870129196
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
        "frame": 8747,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 25,
        "raw": {
          "frame": 8747,
          "previous_frame": 8746,
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
                "frame": 8746,
                "key": "track:0",
                "bbox": [
                  779.52978515625,
                  354.9048156738281,
                  831.18798828125,
                  535.2417602539062
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 37,
              "consistent_fraction": 0.0,
              "median_patch_error": 27.265731811523438,
              "median_forward_backward_error": 36.849517822265625,
              "discontinuity": 27.265731811523438,
              "previous_mean": 0.33838812510172517,
              "adaptive_ratio": 27.265731811523438,
              "appearance_previous_mean": 5.155346393585205,
              "appearance_adaptive_ratio": 5.288826342581009
            },
            {
              "region": {
                "frame": 8746,
                "key": "track:1",
                "bbox": [
                  742.957763671875,
                  202.6806640625,
                  833.5768432617188,
                  354.2640380859375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 45,
              "consistent_fraction": 0.26666666666666666,
              "median_patch_error": 23.644132614135742,
              "median_forward_backward_error": 7.703745365142822,
              "discontinuity": 17.339030583699547,
              "previous_mean": 0.10452262745347153,
              "adaptive_ratio": 17.339030583699547,
              "appearance_previous_mean": 4.588116690516472,
              "appearance_adaptive_ratio": 5.153341601578617
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.5125,
          "background_patch_error": 6.338080883026123,
          "discontinuity": 22.302381197611492,
          "photometric_gain": 1.021978021978022,
          "photometric_offset": -3.8461538461538396,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 25.45493221282959
        },
        "decision": {
          "frame": 8747,
          "previous_frame": 8746,
          "decision": "unknown",
          "reason": "participant_count_unresolved_raw_barrier_fallback",
          "raw_hypothesis": true,
          "detector_frame": 8747,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "ef3f3b333d77c119bf482e349b26aa7152dd40eda34464c9ca85d8cfac5ef3f6",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              715.1219419836998,
              360.35839638113976,
              821.0253868699074,
              560.5632673799992
            ],
            [
              302.6996466964483,
              486.77640280127525,
              394.551327124238,
              646.4719318449497
            ],
            [
              576.9253680929542,
              210.55157026648521,
              617.7907167449594,
              354.7837700545788
            ],
            [
              793.0715403035283,
              151.22779500111938,
              828.7479370161891,
              204.20284673944116
            ],
            [
              258.6732635907829,
              303.66121469438076,
              296.56237310543656,
              446.893909111619
            ],
            [
              620.9627197571099,
              151.56563679128885,
              655.8669571094215,
              204.24164431542158
            ],
            [
              447.4777057096362,
              151.1578675955534,
              483.96420062333345,
              203.87419445812702
            ]
          ],
          "detector_scores": [
            0.9333512707723802,
            0.9258633739041982,
            0.8758715706766218,
            0.8184125305587971,
            0.7636291648689543,
            0.7506765604889506,
            0.7317591708651477
          ],
          "admitted_indices": [
            0,
            1,
            2
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 10138,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 26,
        "raw": {
          "frame": 10138,
          "previous_frame": 10137,
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
                "frame": 10137,
                "key": "track:13",
                "bbox": [
                  732.4099731445312,
                  346.4452209472656,
                  831.256591796875,
                  539.3746948242188
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 53,
              "consistent_fraction": 0.03773584905660377,
              "median_patch_error": 28.59612274169922,
              "median_forward_backward_error": 17.98021697998047,
              "discontinuity": 27.517023770314342,
              "previous_mean": 0.0,
              "adaptive_ratio": 27.517023770314342,
              "appearance_previous_mean": 8.683283805847168,
              "appearance_adaptive_ratio": 3.293238293379643
            },
            {
              "region": {
                "frame": 10137,
                "key": "track:14",
                "bbox": [
                  801.4293212890625,
                  263.1840515136719,
                  849.23046875,
                  421.2202453613281
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 42,
              "consistent_fraction": 0.14285714285714285,
              "median_patch_error": 31.67488670349121,
              "median_forward_backward_error": 11.775520324707031,
              "discontinuity": 27.149902888706755,
              "previous_mean": 0.0,
              "adaptive_ratio": 27.149902888706755,
              "appearance_previous_mean": 9.059186935424805,
              "appearance_adaptive_ratio": 3.4964381383532968
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 1.107886791229248,
          "discontinuity": 27.33346332951055,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 30.135504722595215
        },
        "decision": {
          "frame": 10138,
          "previous_frame": 10137,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 10138,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "788a7ab918478fe04e271ec419b5132d64dbda94a7a8f801ca430dced90ef066",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              484.28725861757994,
              372.76824927330017,
              574.2399209812284,
              561.5616277456284
            ],
            [
              629.5754566863179,
              233.88297973573208,
              683.2257329747081,
              368.2472719103098
            ],
            [
              790.9371840469539,
              151.2181382291019,
              831.3395026214421,
              203.23146134987473
            ],
            [
              445.5342446155846,
              151.1444243080914,
              485.88511506840587,
              202.8857623822987
            ],
            [
              622.8043603412807,
              151.307850651443,
              655.7916799075902,
              204.62877395004034
            ],
            [
              232.0,
              333.36769964918494,
              242.79338782001287,
              387.2742636539042
            ]
          ],
          "detector_scores": [
            0.9326542533443369,
            0.9162379328605362,
            0.7615933005582737,
            0.731757673306296,
            0.6851175331891464,
            0.5927383144011898
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
        "frame": 11065,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 27,
        "raw": {
          "frame": 11065,
          "previous_frame": 11064,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 11064,
                "key": "track:5",
                "bbox": [
                  269.7456359863281,
                  465.0084228515625,
                  360.017578125,
                  696.5629272460938
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 74,
              "consistent_fraction": 0.43243243243243246,
              "median_patch_error": 25.55410385131836,
              "median_forward_backward_error": 3.720242500305176,
              "discontinuity": 14.50368056426177,
              "previous_mean": 0.0,
              "adaptive_ratio": 14.50368056426177,
              "appearance_previous_mean": 8.221779346466064,
              "appearance_adaptive_ratio": 3.1080989618509016
            },
            {
              "region": {
                "frame": 11064,
                "key": "track:6",
                "bbox": [
                  559.6863403320312,
                  204.823486328125,
                  611.2857055664062,
                  346.5099182128906
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 29,
              "consistent_fraction": 0.5172413793103449,
              "median_patch_error": 22.589994430541992,
              "median_forward_backward_error": 0.7799885869026184,
              "discontinuity": 10.905514552675443,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.905514552675443,
              "appearance_previous_mean": 5.435622215270996,
              "appearance_adaptive_ratio": 4.155916937545255
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9375,
          "background_patch_error": 1.9787769317626953,
          "discontinuity": 12.704597558468606,
          "photometric_gain": 1.010989010989011,
          "photometric_offset": 0.0879120879120876,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 24.072049140930176
        },
        "decision": {
          "frame": 11065,
          "previous_frame": 11064,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 11065,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "d6e82faff72d4e857bc17278bf274677fca6e52ed6b6f1d7c138b29439733cdd",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              689.3661583289504,
              238.63318125158548,
              758.9747668877244,
              371.3434881195426
            ],
            [
              583.0915205255151,
              346.3091064840555,
              658.5801092609763,
              555.4699557870626
            ],
            [
              790.7629182450473,
              151.2037330530584,
              831.8440985567868,
              203.00182044878602
            ],
            [
              444.842241730541,
              151.04148539155722,
              486.3618384934962,
              202.67722199112177
            ],
            [
              622.7350834086537,
              151.40052451193333,
              655.9662067219615,
              204.3220388367772
            ],
            [
              232.0,
              334.28102653846145,
              243.001729327254,
              387.31920510903
            ]
          ],
          "detector_scores": [
            0.935577765087869,
            0.9278933141552775,
            0.8296180112767816,
            0.7970947053349965,
            0.7764480160117236,
            0.5109608491849138
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
        "frame": 12335,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 28,
        "raw": {
          "frame": 12335,
          "previous_frame": 12334,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 12334,
                "key": "track:4",
                "bbox": [
                  360.24127197265625,
                  371.7724609375,
                  428.59112548828125,
                  564.8223266601562
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 49,
              "consistent_fraction": 0.20408163265306123,
              "median_patch_error": 26.326034545898438,
              "median_forward_backward_error": 3.9037485122680664,
              "discontinuity": 20.95337443449059,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.95337443449059,
              "appearance_previous_mean": 10.082447528839111,
              "appearance_adaptive_ratio": 2.611075780022394
            },
            {
              "region": {
                "frame": 12334,
                "key": "track:2",
                "bbox": [
                  692.2069091796875,
                  227.76905822753906,
                  742.7692260742188,
                  379.46820068359375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 32,
              "consistent_fraction": 0.40625,
              "median_patch_error": 24.030258178710938,
              "median_forward_backward_error": 2.0313737392425537,
              "discontinuity": 14.26796579360962,
              "previous_mean": 0.0,
              "adaptive_ratio": 14.26796579360962,
              "appearance_previous_mean": 7.956845283508301,
              "appearance_adaptive_ratio": 3.020073574701406
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.925,
          "background_patch_error": 1.0764243602752686,
          "discontinuity": 17.610670114050105,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 25.178146362304688
        },
        "decision": {
          "frame": 12335,
          "previous_frame": 12334,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 12335,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "f76b5f0af62372137e8e81b7b28a6a42af96cb658e9518cf11bcb689beeab6f5",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              654.66800314188,
              369.38283084332943,
              740.2423850893974,
              561.2577719837427
            ],
            [
              595.2603591680527,
              221.12414440512657,
              660.7828040122986,
              369.07185247540474
            ],
            [
              793.0520277358592,
              151.14996411278844,
              830.106826748699,
              203.47021177783608
            ],
            [
              446.9742699973285,
              151.04916787147522,
              485.37037133052945,
              202.57045025378466
            ],
            [
              623.0728833265603,
              151.49308681860566,
              656.1450002603233,
              204.75350585207343
            ],
            [
              232.0,
              333.336298301816,
              243.87190339434892,
              387.1277850717306
            ]
          ],
          "detector_scores": [
            0.9455097322180983,
            0.9322537960026848,
            0.7872348580588281,
            0.7597874433341587,
            0.6509165042826053,
            0.608938967615713
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
        "frame": 12553,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 29,
        "raw": {
          "frame": 12553,
          "previous_frame": 12552,
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
                "frame": 12552,
                "key": "track:2",
                "bbox": [
                  777.0023193359375,
                  438.534423828125,
                  888.0574951171875,
                  639.5573120117188
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 69,
              "consistent_fraction": 0.08695652173913043,
              "median_patch_error": 22.772180557250977,
              "median_forward_backward_error": 21.482664108276367,
              "discontinuity": 20.79199094357698,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.79199094357698,
              "appearance_previous_mean": 3.25825534760952,
              "appearance_adaptive_ratio": 6.98907179695361
            },
            {
              "region": {
                "frame": 12552,
                "key": "track:1",
                "bbox": [
                  680.9183959960938,
                  227.782958984375,
                  744.8908081054688,
                  382.7179870605469
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 28,
              "consistent_fraction": 0.14285714285714285,
              "median_patch_error": 29.35448455810547,
              "median_forward_backward_error": 18.268341064453125,
              "discontinuity": 25.160986764090403,
              "previous_mean": 0.0,
              "adaptive_ratio": 25.160986764090403,
              "appearance_previous_mean": 2.896860711276531,
              "appearance_adaptive_ratio": 10.1332053846559
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9375,
          "background_patch_error": 1.2004677057266235,
          "discontinuity": 22.976488853833693,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 26.063332557678223
        },
        "decision": {
          "frame": 12553,
          "previous_frame": 12552,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 12553,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "d336d57ef32475367be651fcfa1a7655d88bd00fec257b41a7060d477956f629",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              477.5917849764228,
              376.1444824039936,
              567.6737646833062,
              562.9383113086224
            ],
            [
              629.237830273807,
              232.06281712651253,
              684.9093991592526,
              369.3153007924557
            ],
            [
              446.30609015747905,
              151.0769237242639,
              485.49255533888936,
              203.5834915228188
            ],
            [
              792.9045240096748,
              151.26948245242238,
              830.0756953544915,
              203.53401635214686
            ],
            [
              622.6555259041488,
              151.37006190046668,
              655.7544441409409,
              204.51352201774716
            ],
            [
              232.01825012732297,
              332.0626673139632,
              243.71455663163215,
              387.3620544038713
            ]
          ],
          "detector_scores": [
            0.9312151848987482,
            0.9111781639467226,
            0.6642322926114217,
            0.6574262111948768,
            0.558634579694863,
            0.5447592975954878
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
        "frame": 13064,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 30,
        "raw": {
          "frame": 13064,
          "previous_frame": 13063,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 13063,
                "key": "track:0",
                "bbox": [
                  947.6930541992188,
                  332.5740966796875,
                  1037.8748779296875,
                  522.8191528320312
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 61,
              "consistent_fraction": 0.4918032786885246,
              "median_patch_error": 25.82653045654297,
              "median_forward_backward_error": 1.1625851392745972,
              "discontinuity": 13.124958100866099,
              "previous_mean": 0.0,
              "adaptive_ratio": 13.124958100866099,
              "appearance_previous_mean": 9.028273582458496,
              "appearance_adaptive_ratio": 2.86062780670744
            },
            {
              "region": {
                "frame": 13063,
                "key": "track:2",
                "bbox": [
                  761.9630737304688,
                  251.03062438964844,
                  823.3455200195312,
                  408.0911865234375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 33,
              "consistent_fraction": 0.12121212121212122,
              "median_patch_error": 32.164329528808594,
              "median_forward_backward_error": 13.248587608337402,
              "discontinuity": 28.265622919256035,
              "previous_mean": 0.0,
              "adaptive_ratio": 28.265622919256035,
              "appearance_previous_mean": 6.102466106414795,
              "appearance_adaptive_ratio": 5.270710065066657
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.5755031108856201,
          "discontinuity": 20.695290510061067,
          "photometric_gain": 0.989010989010989,
          "photometric_offset": 1.9120879120879124,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 28.99542999267578
        },
        "decision": {
          "frame": 13064,
          "previous_frame": 13063,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 13064,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "4299e78dabe4b125c6819ccda53b7af38b6ed2ba6db40daf024d2ea9b511e449",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              651.7093076631427,
              372.7140130698681,
              739.1281032636762,
              556.5729915201664
            ],
            [
              607.6900352612138,
              231.85423674434423,
              668.6538506373763,
              368.6881283894181
            ],
            [
              792.826692506671,
              151.13447286561131,
              829.7592743188143,
              203.39297864958644
            ],
            [
              446.0989005751908,
              151.05622943863273,
              486.61865363642573,
              202.9644015096128
            ],
            [
              232.0,
              334.3542058430612,
              244.43849205318838,
              387.3542624749243
            ],
            [
              623.5705013275146,
              151.28548726812005,
              655.9857268333435,
              204.99330025538802
            ]
          ],
          "detector_scores": [
            0.944851149397688,
            0.9104028708590236,
            0.7321264742502643,
            0.7316685590232341,
            0.5538164937912105,
            0.4645968449190146
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
        "frame": 13468,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 31,
        "raw": {
          "frame": 13468,
          "previous_frame": 13467,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 13467,
                "key": "track:0",
                "bbox": [
                  626.7264404296875,
                  315.8958740234375,
                  696.788818359375,
                  497.4617919921875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 34,
              "consistent_fraction": 0.2647058823529412,
              "median_patch_error": 34.74053955078125,
              "median_forward_backward_error": 3.8869290351867676,
              "discontinuity": 25.54451437557445,
              "previous_mean": 0.9191757038101765,
              "adaptive_ratio": 25.54451437557445,
              "appearance_previous_mean": 14.302862644195557,
              "appearance_adaptive_ratio": 2.4289221266401375
            },
            {
              "region": {
                "frame": 13467,
                "key": "track:1",
                "bbox": [
                  311.1780090332031,
                  221.76434326171875,
                  356.7760314941406,
                  367.06866455078125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.46153846153846156,
              "median_patch_error": 23.302932739257812,
              "median_forward_backward_error": 2.5278890132904053,
              "discontinuity": 12.547733013446514,
              "previous_mean": 0.0,
              "adaptive_ratio": 12.547733013446514,
              "appearance_previous_mean": 7.461699485778809,
              "appearance_adaptive_ratio": 3.1230060636548926
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.2676091194152832,
          "discontinuity": 19.046123694510484,
          "photometric_gain": 0.989010989010989,
          "photometric_offset": -0.0769230769230802,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 29.02173614501953
        },
        "decision": {
          "frame": 13468,
          "previous_frame": 13467,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 13468,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "c96555e82b969cca28b18ff78c0571353a61aa07be40d4f5bace5379e463b10e",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              607.2629675716162,
              349.6526059359312,
              695.1504449993372,
              557.1483819037676
            ],
            [
              536.4963025301695,
              242.84326443821192,
              606.3531233817339,
              371.34766402095556
            ],
            [
              445.14040396362543,
              151.0412475503981,
              486.9651077017188,
              202.6326362453401
            ],
            [
              792.5420440807939,
              151.21473478525877,
              829.9836696013808,
              203.30442386120558
            ],
            [
              623.2402979284525,
              151.33239038661122,
              656.0232583135366,
              204.56480730697513
            ],
            [
              232.0,
              334.611987773329,
              242.9499802114442,
              387.17019867524505
            ]
          ],
          "detector_scores": [
            0.9405543184605304,
            0.9318737783855495,
            0.728755561239742,
            0.7170271684485662,
            0.653178658053465,
            0.46429890517519756
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [
            [
              0,
              0
            ]
          ],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 13863,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 32,
        "raw": {
          "frame": 13863,
          "previous_frame": 13862,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 13862,
                "key": "track:0",
                "bbox": [
                  877.1738891601562,
                  373.8122863769531,
                  981.773193359375,
                  570.6537475585938
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 72,
              "consistent_fraction": 0.2777777777777778,
              "median_patch_error": 27.74277114868164,
              "median_forward_backward_error": 4.5497283935546875,
              "discontinuity": 20.036445829603405,
              "previous_mean": 0.23101217568583954,
              "adaptive_ratio": 20.036445829603405,
              "appearance_previous_mean": 10.967403411865234,
              "appearance_adaptive_ratio": 2.5295660337129338
            },
            {
              "region": {
                "frame": 13862,
                "key": "track:1",
                "bbox": [
                  743.9982299804688,
                  222.30630493164062,
                  817.6057739257812,
                  372.06158447265625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.3333333333333333,
              "median_patch_error": 17.205215454101562,
              "median_forward_backward_error": 2.4727845191955566,
              "discontinuity": 11.470143636067709,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.470143636067709,
              "appearance_previous_mean": 6.264065980911255,
              "appearance_adaptive_ratio": 2.746652973728521
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 1.418225646018982,
          "discontinuity": 15.753294732835556,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 22.4739933013916
        },
        "decision": {
          "frame": 13863,
          "previous_frame": 13862,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 13863,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6d6c25c558a5c81dede13ca6c179a34cbb58485ea73502bcf43b669aa2d1664d",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              485.5944452509284,
              366.6218022853136,
              578.8613443151116,
              564.5646312683821
            ],
            [
              628.1877605319023,
              221.43102264404297,
              691.9949219822884,
              368.58975476026535
            ],
            [
              445.7402362562716,
              151.0708240456879,
              484.84035911783576,
              204.17798076197505
            ],
            [
              792.1639003865421,
              151.24696752429008,
              830.7201456911862,
              203.32831742614508
            ],
            [
              623.313057038933,
              151.37785172462463,
              655.5852145217359,
              204.63164067268372
            ],
            [
              232.0,
              333.7535390481353,
              244.29378478135914,
              387.2643227353692
            ]
          ],
          "detector_scores": [
            0.9321071977415664,
            0.9117771658336669,
            0.8006044014519186,
            0.783134822041103,
            0.599863239617151,
            0.5182514124093803
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
        "frame": 15143,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 33,
        "raw": {
          "frame": 15143,
          "previous_frame": 15142,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 15142,
                "key": "track:1",
                "bbox": [
                  980.699462890625,
                  343.79229736328125,
                  1041.9971923828125,
                  533.0279541015625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 51,
              "consistent_fraction": 0.5098039215686274,
              "median_patch_error": 27.216482162475586,
              "median_forward_backward_error": 0.9106783270835876,
              "discontinuity": 13.341412824742935,
              "previous_mean": 0.0,
              "adaptive_ratio": 13.341412824742935,
              "appearance_previous_mean": 10.329613208770752,
              "appearance_adaptive_ratio": 2.634801672860935
            },
            {
              "region": {
                "frame": 15142,
                "key": "track:3",
                "bbox": [
                  726.4430541992188,
                  206.45831298828125,
                  763.6123657226562,
                  354.4244689941406
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 25,
              "consistent_fraction": 0.32,
              "median_patch_error": 31.462940216064453,
              "median_forward_backward_error": 3.111708641052246,
              "discontinuity": 21.394799346923826,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.394799346923826,
              "appearance_previous_mean": 6.802951335906982,
              "appearance_adaptive_ratio": 4.624895675792711
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.30070161819458,
          "discontinuity": 17.368106085833382,
          "photometric_gain": 1.011111111111111,
          "photometric_offset": -0.9333333333333371,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 29.33971118927002
        },
        "decision": {
          "frame": 15143,
          "previous_frame": 15142,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 15143,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "829eca8483d3d1bdae97b4fb3446e62ac61d999bf98bc1945ba9a3adeb20c40c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              583.501204483211,
              348.9772212356329,
              665.8754408434033,
              558.4481985718012
            ],
            [
              687.2725456655025,
              239.36018800735474,
              760.4625650942326,
              370.46429669857025
            ],
            [
              793.436260715127,
              151.17564043402672,
              828.8340530246496,
              203.9434883221984
            ],
            [
              445.1515490449965,
              151.15090495347977,
              485.8080424629152,
              203.39302285015583
            ],
            [
              623.7791136540473,
              151.28904857113957,
              656.1974381171167,
              204.35461044684052
            ]
          ],
          "detector_scores": [
            0.9439951236411865,
            0.9270882850098258,
            0.6900986423433254,
            0.6379472902837849,
            0.6162347756917999
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
        "frame": 15878,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 34,
        "raw": {
          "frame": 15878,
          "previous_frame": 15877,
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
                "frame": 15877,
                "key": "track:2",
                "bbox": [
                  430.5641174316406,
                  346.0796203613281,
                  523.9520874023438,
                  492.287109375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 44,
              "consistent_fraction": 0.22727272727272727,
              "median_patch_error": 26.170351028442383,
              "median_forward_backward_error": 5.487256050109863,
              "discontinuity": 20.22254397652366,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.22254397652366,
              "appearance_previous_mean": 6.67520546913147,
              "appearance_adaptive_ratio": 3.9205311580989406
            },
            {
              "region": {
                "frame": 15877,
                "key": "track:3",
                "bbox": [
                  559.1965942382812,
                  197.9942626953125,
                  599.1224975585938,
                  341.61273193359375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 23,
              "consistent_fraction": 0.17391304347826086,
              "median_patch_error": 29.182043075561523,
              "median_forward_backward_error": 4.381974697113037,
              "discontinuity": 24.10690514937691,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.10690514937691,
              "appearance_previous_mean": 5.918030738830566,
              "appearance_adaptive_ratio": 4.931039456095838
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 0.7675382494926453,
          "discontinuity": 22.164724562950283,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 27.676197052001953
        },
        "decision": {
          "frame": 15878,
          "previous_frame": 15877,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 15878,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "2eb04a3535586a890568d01a672b62d4e2a54f1e85802a3962ab0eb9c2eecdcb",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              482.67968737334013,
              369.63864690065384,
              574.5184469297528,
              559.7988921999931
            ],
            [
              628.3782724738121,
              235.25052009522915,
              683.8220272660255,
              368.7410048991442
            ],
            [
              792.9841976873577,
              151.30231084674597,
              829.7119435556233,
              204.26456546783447
            ],
            [
              445.0683796107769,
              151.0340618006885,
              486.0374030172825,
              203.38905111327767
            ],
            [
              624.1345371939242,
              151.3651935234666,
              655.9957373403013,
              204.68039179593325
            ],
            [
              232.0,
              334.0868113413453,
              242.47064326703548,
              387.51547458022833
            ]
          ],
          "detector_scores": [
            0.9362901542635919,
            0.9164617339664903,
            0.718793465961853,
            0.6876952349568325,
            0.6102431062175949,
            0.4599201574430645
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
        "frame": 16236,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 35,
        "raw": {
          "frame": 16236,
          "previous_frame": 16235,
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
                "frame": 16235,
                "key": "track:0",
                "bbox": [
                  817.3096923828125,
                  357.19219970703125,
                  898.4402465820312,
                  553.0386352539062
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 58,
              "consistent_fraction": 0.1724137931034483,
              "median_patch_error": 27.699050903320312,
              "median_forward_backward_error": 8.727397918701172,
              "discontinuity": 22.92335247171336,
              "previous_mean": 0.0,
              "adaptive_ratio": 22.92335247171336,
              "appearance_previous_mean": 5.649624407291412,
              "appearance_adaptive_ratio": 4.9028128077986715
            },
            {
              "region": {
                "frame": 16235,
                "key": "track:1",
                "bbox": [
                  691.970458984375,
                  205.42710876464844,
                  745.577392578125,
                  347.6649475097656
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.5,
              "median_patch_error": 19.60891342163086,
              "median_forward_backward_error": 1.0620431900024414,
              "discontinuity": 9.80445671081543,
              "previous_mean": 0.0,
              "adaptive_ratio": 9.80445671081543,
              "appearance_previous_mean": 2.9801763594150543,
              "appearance_adaptive_ratio": 6.579782890929205
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.487811803817749,
          "discontinuity": 16.363904591264394,
          "photometric_gain": 0.989010989010989,
          "photometric_offset": 1.9120879120879124,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 23.653982162475586
        },
        "decision": {
          "frame": 16236,
          "previous_frame": 16235,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 16236,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "81709aa2185b691c44950c844e1570ce9394a10f60597e181d45113462231279",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              654.6545753329992,
              376.1171875,
              742.3499958664179,
              552.293214559555
            ],
            [
              604.8174648433924,
              232.94821767508984,
              665.0914046615362,
              369.1983671337366
            ],
            [
              444.874992005527,
              151.00107133761048,
              483.98056746274233,
              204.19851087406278
            ],
            [
              792.2745138481259,
              151.25269044563174,
              830.0843449756503,
              203.84312987700105
            ],
            [
              624.0827058516443,
              151.3324093297124,
              656.1447075642645,
              204.92573442310095
            ],
            [
              232.0,
              333.7807581797242,
              242.43567250017077,
              387.67388942092657
            ]
          ],
          "detector_scores": [
            0.9477564656825911,
            0.9119361776665743,
            0.8069169651522452,
            0.8022193890469436,
            0.6495460565258472,
            0.4890309293298978
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
        "frame": 17206,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 36,
        "raw": {
          "frame": 17206,
          "previous_frame": 17205,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 17205,
                "key": "track:4",
                "bbox": [
                  255.49072265625,
                  443.1848449707031,
                  370.55865478515625,
                  662.0558471679688
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 71,
              "consistent_fraction": 0.5492957746478874,
              "median_patch_error": 21.062429428100586,
              "median_forward_backward_error": 0.6834670901298523,
              "discontinuity": 9.492925939425616,
              "previous_mean": 0.0,
              "adaptive_ratio": 9.492925939425616,
              "appearance_previous_mean": 5.865681529045105,
              "appearance_adaptive_ratio": 3.5907898040160755
            },
            {
              "region": {
                "frame": 17205,
                "key": "track:3",
                "bbox": [
                  336.12054443359375,
                  257.0253601074219,
                  388.5115966796875,
                  407.968017578125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 23,
              "consistent_fraction": 0.5652173913043478,
              "median_patch_error": 23.251771926879883,
              "median_forward_backward_error": 0.8577649593353271,
              "discontinuity": 10.109466055165168,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.109466055165168,
              "appearance_previous_mean": 3.9867842495441437,
              "appearance_adaptive_ratio": 5.832212247135905
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.925,
          "background_patch_error": 1.316291093826294,
          "discontinuity": 9.801195997295391,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 22.157100677490234
        },
        "decision": {
          "frame": 17206,
          "previous_frame": 17205,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 17206,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "ec491d5e1597ff0e6e508c1ef669c811dfac3095da4f41a8272622092c45d5a6",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              609.6922965794802,
              345.8939747363329,
              687.4524420946836,
              554.9954184740782
            ],
            [
              537.5601259693503,
              242.8330267444253,
              605.3979294076562,
              370.2615255340934
            ],
            [
              791.5334104448557,
              151.27064008638263,
              830.6639042943716,
              203.7796578593552
            ],
            [
              446.78968892246485,
              151.1427404768765,
              484.56188597530127,
              204.46923304721713
            ],
            [
              623.1461222171783,
              151.41446452960372,
              656.3620193004608,
              204.73481111600995
            ]
          ],
          "detector_scores": [
            0.9402958764655941,
            0.9259757894157193,
            0.6847599545245832,
            0.6075588047488943,
            0.6003321802519613
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
        "frame": 17351,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 37,
        "raw": {
          "frame": 17351,
          "previous_frame": 17350,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 17350,
                "key": "track:0",
                "bbox": [
                  487.1849670410156,
                  322.10906982421875,
                  559.077880859375,
                  510.21710205078125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 51,
              "consistent_fraction": 0.0392156862745098,
              "median_patch_error": 23.398738861083984,
              "median_forward_backward_error": 10.591300964355469,
              "discontinuity": 22.481141258688535,
              "previous_mean": 0.0,
              "adaptive_ratio": 22.481141258688535,
              "appearance_previous_mean": 9.809417724609375,
              "appearance_adaptive_ratio": 2.3853341266508004
            },
            {
              "region": {
                "frame": 17350,
                "key": "track:1",
                "bbox": [
                  692.3527221679688,
                  214.20965576171875,
                  751.996826171875,
                  360.2896423339844
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 31,
              "consistent_fraction": 0.5806451612903226,
              "median_patch_error": 23.144203186035156,
              "median_forward_backward_error": 0.5795701146125793,
              "discontinuity": 9.705633594143775,
              "previous_mean": 0.0,
              "adaptive_ratio": 9.705633594143775,
              "appearance_previous_mean": 5.800240993499756,
              "appearance_adaptive_ratio": 3.9902140638591606
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 0.7691326141357422,
          "discontinuity": 16.093387426416154,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 23.27147102355957
        },
        "decision": {
          "frame": 17351,
          "previous_frame": 17350,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 17351,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6ebb3823ba09a2dea6d9b05fd6df90235c94a6fe4a043e6ac48759c136cfd867",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              685.9333767071366,
              241.85807584226131,
              758.4460008963943,
              370.34192426502705
            ],
            [
              582.7712959498167,
              348.2560868412256,
              658.3652492314577,
              556.7917632907629
            ],
            [
              791.5889623463154,
              151.21767096593976,
              830.5210625827312,
              203.90362572297454
            ],
            [
              446.24901593476534,
              151.10704956948757,
              485.7764961645007,
              203.83450655639172
            ],
            [
              623.0591130331159,
              151.30298858880997,
              656.2013533040881,
              204.59257578849792
            ],
            [
              232.0,
              335.3421706557274,
              242.66018357872963,
              387.65715634822845
            ],
            [
              1018.3397654797882,
              151.75505517423153,
              1041.9565127585083,
              242.618569791317
            ]
          ],
          "detector_scores": [
            0.9363233116510765,
            0.9320986574746024,
            0.8251903071703409,
            0.8004981916318692,
            0.7798432018471927,
            0.4856186252552188,
            0.3762635512458459
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [
            [
              1,
              0
            ]
          ],
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
      "activity_interval": 105,
      "scene": 1,
      "participant_observation": 178,
      "rally_start": 101,
      "contact": 1261,
      "stroke": 616,
      "format_decision": 1,
      "rally_end": 47,
      "identity_ambiguity": 38,
      "broadcast_score": 477,
      "match_phase": 1,
      "highlight": 2,
      "shuttle_turn": 21
    },
    "live_counts": {
      "calibration": 1,
      "activity_interval": 105,
      "scene": 1,
      "participant_observation": 178,
      "format_decision": 1,
      "rally_start": 47,
      "stroke": 586,
      "contact": 586,
      "rally_end": 47,
      "identity_ambiguity": 38,
      "broadcast_score": 477,
      "match_phase": 1,
      "highlight": 2,
      "shuttle_turn": 21
    },
    "categories": {
      "event_status": {
        "confirmed": 1807,
        "provisional": 284
      },
      "stroke_actor": {
        "unknown": 586
      },
      "stroke_physical_event_status": {
        "ambiguous": 192,
        "insufficient": 306,
        "probable": 88
      },
      "stroke_contact_status": {
        "estimated": 586
      },
      "stroke_classification_status": {
        "unknown": 422,
        "estimated": 164
      },
      "stroke_stroke": {
        "unknown": 422,
        "push": 73,
        "lift": 26,
        "clear": 7,
        "drive": 16,
        "net_shot": 14,
        "drop": 25,
        "smash": 2,
        "rush": 1
      },
      "stroke_attribution_reason": {
        "nearest_proximity": 581,
        "ambiguous_proximity": 5
      },
      "stroke_classification_abstention_reason": {
        "missing_required_evidence": 416,
        "unresolved_initial_contact": 6
      },
      "contact_actor": {
        "unknown": 586
      },
      "contact_physical_event_status": {
        "ambiguous": 192,
        "insufficient": 306,
        "probable": 88
      },
      "contact_contact_status": {
        "estimated": 586
      },
      "contact_attribution_reason": {
        "nearest_proximity": 581,
        "ambiguous_proximity": 5
      },
      "contact_trajectory_reliability": {
        "insufficient": 144,
        "ambiguous": 124,
        "probable": 318
      },
      "contact_trajectory_reasons": {
        "coherent_motion_change_unavailable": 144,
        "association_unresolved": 124,
        "supported_turn": 251,
        "supported_launch": 67
      },
      "contact_impact_reliability": {
        "ambiguous": 192,
        "insufficient": 306,
        "probable": 88
      },
      "contact_impact_reasons": {
        "no_fresh_swing_or_racket_overlap": 26,
        "association_unresolved": 124,
        "fresh_player_observation_unavailable": 306,
        "coherent_motion_and_fresh_contact_cue": 88,
        "coherent_motion_change_unavailable": 42
      },
      "contact_attribution_reliability": {
        "probable": 201,
        "insufficient": 385
      },
      "contact_attribution_reasons": {
        "geometric_attribution_not_verified_identity": 201,
        "fresh_player_observation_unavailable": 385
      },
      "rally_end_reason": {
        "stationary": 27,
        "cut": 6,
        "gap": 14
      },
      "rally_phase": {
        "unknown": 3,
        "match_play": 44
      },
      "rally_official": {
        "False": 18,
        "True": 29
      },
      "rally_match_format_known": {
        "True": 47
      },
      "rally_match_format": {
        "singles": 47
      },
      "rally_winner": {
        "None": 47
      },
      "rally_score_transition_status": {
        "unavailable": 37,
        "candidate": 10
      },
      "rally_admission_reason": {
        "duration_policy": 46,
        "independent_contact_and_observed_motion_witnesses": 1
      }
    },
    "physical_accuracy_validated": false
  },
  "ocr": {
    "readout_count": 521,
    "label_counts": {
      "AXELSEN": 521,
      "NG K.L.A.": 521
    },
    "context_counts": {
      "{\"acquisition_policy\":\"main_camera\",\"actual_replay_status\":\"unknown\",\"analysis_excluded\":false,\"view\":\"main\"}": 521
    },
    "previously_source_reviewed_branding_strings": {},
    "readouts": [
      {
        "f": 960,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.95818,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 990,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99835,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1020,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.9436,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1050,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.998,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1080,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.9788,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1110,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97915,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1140,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
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
        "f": 1170,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1200,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99852,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1230,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
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
        "f": 1260,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99849,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1290,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.9984,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1320,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99819,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1350,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99826,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1380,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1410,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1440,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97763,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1470,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99849,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1500,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97762,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1530,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97778,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1560,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97835,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1590,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99864,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1620,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97852,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1650,
        "r": [
          [
            "AXELSEN",
            1
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97863,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1680,
        "r": [
          [
            "AXELSEN",
            2
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99815,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1710,
        "r": [
          [
            "AXELSEN",
            2
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99818,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1740,
        "r": [
          [
            "AXELSEN",
            2
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99852,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1770,
        "r": [
          [
            "AXELSEN",
            2
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99829,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1800,
        "r": [
          [
            "AXELSEN",
            2
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1830,
        "r": [
          [
            "AXELSEN",
            2
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1860,
        "r": [
          [
            "AXELSEN",
            2
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99856,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1890,
        "r": [
          [
            "AXELSEN",
            2
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.9986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1920,
        "r": [
          [
            "AXELSEN",
            2
          ],
          [
            "NG K.L.A.",
            1
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
        "f": 1950,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99729,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1980,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
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
        "f": 2010,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2040,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99832,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2070,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99832,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2100,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99657,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2130,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99843,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2160,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97376,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2190,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99852,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2220,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97828,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2250,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97828,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2280,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2310,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2340,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2370,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2400,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2430,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2460,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99804,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2490,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.98596,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2520,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99858,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2550,
        "r": [
          [
            "AXELSEN",
            4
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99766,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2580,
        "r": [
          [
            "AXELSEN",
            4
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99798,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2610,
        "r": [
          [
            "AXELSEN",
            4
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.97652,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2640,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99753,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2670,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.9975,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2700,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99829,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2730,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99829,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2760,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99819,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2790,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.9902,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2820,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99872,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2850,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99808,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2880,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.9986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2910,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.9986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2940,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2970,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3000,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99809,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3030,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99809,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3060,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99834,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3090,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.9981,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3120,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
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
        "f": 3150,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99006,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3180,
        "r": [
          [
            "AXELSEN",
            5
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99419,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3210,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            2
          ]
        ],
        "c": 0.99836,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3240,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            2
          ]
        ],
        "c": 0.99814,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3270,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            2
          ]
        ],
        "c": 0.99816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3300,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            2
          ]
        ],
        "c": 0.99822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3330,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            2
          ]
        ],
        "c": 0.99818,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3360,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.99828,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3390,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.99829,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3420,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.98602,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3450,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.98602,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3480,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.97771,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3510,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.97816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3540,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.97963,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3570,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.97943,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3600,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.97779,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3630,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.97809,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3660,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.99688,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3690,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.97797,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3720,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99866,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3750,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3780,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99849,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3810,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99514,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3840,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.96544,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3870,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.9782,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3900,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99817,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3930,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.9982,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3960,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            5
          ]
        ],
        "c": 0.99817,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3990,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            5
          ]
        ],
        "c": 0.99811,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4020,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            5
          ]
        ],
        "c": 0.99846,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4050,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            5
          ]
        ],
        "c": 0.99846,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4080,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            5
          ]
        ],
        "c": 0.99726,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4110,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            5
          ]
        ],
        "c": 0.99726,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4140,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            5
          ]
        ],
        "c": 0.99861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4170,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99446,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4200,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99872,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4230,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4260,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99844,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4290,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99844,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4320,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4350,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4380,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99823,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4410,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99836,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4440,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4470,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4500,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.9983,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4530,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.97024,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4560,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99826,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4590,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.97927,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4620,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4650,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4680,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4710,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99843,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4740,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99672,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4770,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99672,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4800,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99818,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4830,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99036,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4860,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99864,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4890,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99864,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4920,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99838,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4950,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99837,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4980,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5010,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5040,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.9483,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5070,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.94733,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5100,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99847,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5130,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99848,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5160,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99819,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5190,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99819,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5220,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5250,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.97315,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5280,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99867,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5310,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99867,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5340,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.9987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5370,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5400,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.9987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5430,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.9987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5460,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5490,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5520,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5550,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5580,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.9986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5610,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99859,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5640,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.9766,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5670,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99849,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5700,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99873,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5790,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.98499,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5820,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5850,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5880,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 5910,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99846,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5940,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99852,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5970,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99857,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6000,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6030,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6060,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99849,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6090,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99848,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6120,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.97713,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6150,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.97718,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6180,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99814,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6210,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99814,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6240,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6270,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99805,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6300,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.9983,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6330,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99831,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6360,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99832,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6390,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99833,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6420,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99829,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6450,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99834,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6480,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6510,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6540,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99828,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6570,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99825,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6600,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6630,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99825,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6660,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99837,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6690,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.94921,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6720,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99829,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6750,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99866,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6780,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99856,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6810,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6840,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99843,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6870,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99837,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6900,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99856,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6930,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6960,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99867,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6990,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.95145,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7020,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99699,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7050,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7080,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99835,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7110,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.9987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7140,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99847,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7170,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99843,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7200,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99858,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7230,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99858,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7260,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7290,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7320,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99414,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7350,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99414,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7380,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99871,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7410,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7440,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7470,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7500,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            13
          ]
        ],
        "c": 0.99816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7530,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            13
          ]
        ],
        "c": 0.99839,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7560,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            13
          ]
        ],
        "c": 0.99855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7590,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            13
          ]
        ],
        "c": 0.99855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7620,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 7650,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99849,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7680,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7710,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7740,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7770,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99856,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7800,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99856,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7830,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99856,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7860,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7890,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7920,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99833,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7950,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99833,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7980,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8010,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99826,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8040,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99839,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8070,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99838,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8100,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8130,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8160,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99857,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8190,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8220,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8250,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8280,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99817,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8310,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99817,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8340,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99846,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8370,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.9986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8400,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8430,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.9984,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8460,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8490,
        "r": [
          [
            "AXELSEN",
            20
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.97696,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8520,
        "r": [
          [
            "AXELSEN",
            20
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8550,
        "r": [
          [
            "AXELSEN",
            20
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99817,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8580,
        "r": [
          [
            "AXELSEN",
            20
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99847,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8610,
        "r": [
          [
            "AXELSEN",
            20
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99798,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8640,
        "r": [
          [
            "AXELSEN",
            20
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8670,
        "r": [
          [
            "AXELSEN",
            20
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8700,
        "r": [
          [
            "AXELSEN",
            20
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99837,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8730,
        "r": [
          [
            "AXELSEN",
            20
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99839,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10050,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.98294,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10080,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10110,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            1
          ]
        ],
        "c": 0.99349,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10140,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.9928,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10170,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.998,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10200,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.99139,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10230,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.94853,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10260,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.99832,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10290,
        "r": [
          [
            "AXELSEN",
            0
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.99967,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10320,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.99242,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10350,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.9918,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10380,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10410,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
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
        "f": 10440,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.99967,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10470,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
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
        "f": 10500,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.95097,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10530,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.95223,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10560,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.9997,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10590,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
          ]
        ],
        "c": 0.9997,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10620,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
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
        "f": 10650,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
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
        "f": 10680,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
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
        "f": 10710,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
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
        "f": 10740,
        "r": [
          [
            "AXELSEN",
            3
          ],
          [
            "NG K.L.A.",
            3
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
        "f": 10770,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 10800,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 10830,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 10860,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99973,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10890,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99973,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10920,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 10950,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 10980,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11010,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11040,
        "r": [
          [
            "AXELSEN",
            6
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.95162,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11070,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11100,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11130,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11160,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11190,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11220,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99962,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11250,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99962,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11280,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99782,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11310,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99784,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11340,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11370,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11400,
        "r": [
          [
            "AXELSEN",
            7
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99809,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11430,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99177,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11460,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99966,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11490,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99969,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11520,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11550,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11580,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11610,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11640,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.95093,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11670,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.95093,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11700,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.94711,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11730,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11760,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11790,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11820,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99009,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11850,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99009,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11880,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11910,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11940,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 11970,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 12000,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99951,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12030,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12060,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 12090,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 12120,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 12150,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 12180,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99081,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12210,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 12240,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 12270,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
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
        "f": 12300,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12330,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            4
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12360,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            6
          ]
        ],
        "c": 0.99964,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12390,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            6
          ]
        ],
        "c": 0.99267,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12420,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            6
          ]
        ],
        "c": 0.99055,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12450,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            6
          ]
        ],
        "c": 0.98981,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12480,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
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
        "f": 12510,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
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
        "f": 12540,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.98968,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12570,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99175,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12600,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
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
        "f": 12630,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.9995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12660,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.9486,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12690,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.94862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12720,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
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
        "f": 12750,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
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
        "f": 12780,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
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
        "f": 12810,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
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
        "f": 12840,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99031,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12870,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99031,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12900,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99784,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12930,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99786,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12960,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99203,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12990,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13020,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
          ]
        ],
        "c": 0.99801,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13050,
        "r": [
          [
            "AXELSEN",
            8
          ],
          [
            "NG K.L.A.",
            7
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
        "f": 13080,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99923,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13110,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99923,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13140,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.94795,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13170,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.94795,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13200,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99966,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13230,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99963,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13260,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.98956,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13290,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.98956,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13320,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99945,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13350,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13380,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13410,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13440,
        "r": [
          [
            "AXELSEN",
            9
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99837,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13470,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13500,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13530,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13560,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13590,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13620,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13650,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13680,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13710,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13740,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13770,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13800,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13830,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13860,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            8
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
        "f": 13890,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99979,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13920,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 13950,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 13980,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14010,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14040,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14070,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14100,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14130,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
          ]
        ],
        "c": 0.99516,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14160,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14190,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14220,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14250,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14280,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14310,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14340,
        "r": [
          [
            "AXELSEN",
            10
          ],
          [
            "NG K.L.A.",
            9
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
        "f": 14370,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
          ]
        ],
        "c": 0.99024,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14400,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14430,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14460,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14490,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14520,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14550,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14580,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14610,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14640,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14670,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14700,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14730,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14760,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14790,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14820,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14850,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14880,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14910,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14940,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 14970,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15000,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15030,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15060,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15090,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15120,
        "r": [
          [
            "AXELSEN",
            11
          ],
          [
            "NG K.L.A.",
            10
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15150,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15180,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15210,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15240,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15270,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15300,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15330,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15360,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15390,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15420,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15450,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15480,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15510,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15540,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15570,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15600,
        "r": [
          [
            "AXELSEN",
            13
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15630,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15660,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15690,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15720,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15750,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15780,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15810,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15840,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15870,
        "r": [
          [
            "AXELSEN",
            14
          ],
          [
            "NG K.L.A.",
            10
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
        "f": 15900,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
          ]
        ],
        "c": 0.96922,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15930,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
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
        "f": 15960,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
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
        "f": 15990,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
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
        "f": 16020,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
          ]
        ],
        "c": 0.99981,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16050,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16080,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
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
        "f": 16110,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
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
        "f": 16140,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
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
        "f": 16170,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
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
        "f": 16200,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
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
        "f": 16230,
        "r": [
          [
            "AXELSEN",
            15
          ],
          [
            "NG K.L.A.",
            11
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
        "f": 16260,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16290,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99385,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16320,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16350,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.97696,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16380,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16410,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16440,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16470,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16500,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16530,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16560,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16590,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16620,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99222,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16650,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99238,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16680,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16710,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16740,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16770,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16800,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16830,
        "r": [
          [
            "AXELSEN",
            16
          ],
          [
            "NG K.L.A.",
            12
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
        "f": 16860,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 16890,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 16920,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 16950,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 16980,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 17010,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 17040,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 17070,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 17100,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 17130,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 17160,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 17190,
        "r": [
          [
            "AXELSEN",
            17
          ],
          [
            "NG K.L.A.",
            13
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
        "f": 17220,
        "r": [
          [
            "AXELSEN",
            18
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17250,
        "r": [
          [
            "AXELSEN",
            18
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17280,
        "r": [
          [
            "AXELSEN",
            18
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17310,
        "r": [
          [
            "AXELSEN",
            18
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17340,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17370,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17400,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17430,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17460,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17490,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17520,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17550,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17580,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17610,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17640,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17670,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17700,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17730,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17760,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17790,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17820,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17850,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17880,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
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
        "f": 17910,
        "r": [
          [
            "AXELSEN",
            19
          ],
          [
            "NG K.L.A.",
            14
          ]
        ],
        "c": 0.99987,
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
      "camera_rows": 17915,
      "player_rows": 35554,
      "nonfinite_projected_court_rows": 0,
      "player_projected_court_rows": 34751,
      "projected_court_on_propagated_box": 18499,
      "racket_rows": 13504,
      "shuttle_rows": 17915
    },
    "categories": {
      "player_id": {
        "None": 35554
      },
      "detector_matched": {
        "True": 16635,
        "False": 18919
      }
    },
    "invalid_geometry_frame_count": 6,
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

Reproducibility artifacts: [predictions](run/predicted_rallies.csv), [worker receipt](run/inference.json), [parent receipt](run.executor.json), [complete evaluation](evaluation/supplemental_metrics.json), [per-rally comparison](evaluation/per_rally_comparison.csv), [failure case index](evaluation/failure_case_index.json), [technical analysis](analysis/technical_analysis.json), [source/proxy PTS and scene-pixel audit](timestamps/timestamp_audit.json), [frozen plan](protocol/plan.json). All command logs, stage samples, exact effective config, source snapshots, model manifest/lock and cache catalogue are preserved.

Failures and observations are recorded for the later consolidated analysis. No pipeline component, model, numerical threshold or matcher was changed during this video evaluation. No final aggregate or generalisation claim is made from this individual video.
