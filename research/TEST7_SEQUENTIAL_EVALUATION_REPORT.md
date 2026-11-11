# Test 7 evaluation

Status: completed fresh end-to-end inference; unchanged pipeline and predictions. Comparison measures agreement with the supplied legacy rally CSV. Independent physical component accuracy is unavailable without reviewed component labels.

| Input / provenance | Value |
|---|---|
| Drive file | Test7_Full.mp4 (1WS9suAtgbuwB2qc4IteGgFL6xf5hs0Gq) |
| Video SHA256 | `1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c` |
| Annotation | `/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test7_Full/Test7_Full_rally.csv` |
| Annotation SHA256 | `77e39aea68c9f627730a7b909bfabdd1a3e8f87cb977ea76327253f3af77a7d3` |
| Reference rows | 30 |
| Canonical frames / FPS | 10725 / 30.0 |
| Frozen bindings | [Source, profile, manifest, model lock](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/frozen_pipeline.json) |

| Detection / overlap | Value |
|---|---|
| ground_truth_count | 30 |
| predicted_count | 32 |
| matched_count | 28 |
| true_positives | 28 |
| false_positives | 4 |
| false_negatives | 2 |
| precision | 0.875000 |
| recall | 0.933333 |
| f1 | 0.903226 |
| mean_iou | 0.833985 |
| median_iou | 0.838456 |
| minimum_iou | 0.541176 |
| percent_strictly_exceeding | {'0.5': 100.0, '0.75': 82.14285714285714, '0.9': 35.714285714285715, '0.95': 10.714285714285714} |

Boundary and duration statistics condition on matched intervals; all missed rallies and false detections remain in detection metrics. Signed errors are prediction minus reference. Matching: IoU ≥ 0.5, maximum cardinality then total IoU; zero-origin half-open frame intervals.

| Error | MAE | Median absolute | RMSE | P90 absolute | Maximum absolute | Signed bias |
|---|---|---|---|---|---|---|
| start_frame | 23.464286 | 9.000000 | 50.821466 | 47.600000 | 227.000000 | 21.321429 |
| end_frame | 14.964286 | 9.500000 | 20.303941 | 33.400000 | 49.000000 | -9.750000 |
| start_time_sec | 0.782143 | 0.300000 | 1.694049 | 1.586667 | 7.566667 | 0.710714 |
| end_time_sec | 0.498810 | 0.316667 | 0.676798 | 1.113333 | 1.633333 | -0.325000 |
| duration_sec | 1.178571 | 0.566667 | 2.017326 | 1.963333 | 8.000000 | -1.035714 |

| Boundary tolerance | Within / matched | Within / all reference |
|---|---|---|
| start ±1 frames | 1 / 28 (0.035714) | 1 / 30 (0.033333) |
| start ±3 frames | 4 / 28 (0.142857) | 4 / 30 (0.133333) |
| start ±5 frames | 9 / 28 (0.321429) | 9 / 30 (0.300000) |
| start ±10 frames | 17 / 28 (0.607143) | 17 / 30 (0.566667) |
| start ±15 frames | 20 / 28 (0.714286) | 20 / 30 (0.666667) |
| start ±30 frames | 24 / 28 (0.857143) | 24 / 30 (0.800000) |
| end ±1 frames | 2 / 28 (0.071429) | 2 / 30 (0.066667) |
| end ±3 frames | 6 / 28 (0.214286) | 6 / 30 (0.200000) |
| end ±5 frames | 9 / 28 (0.321429) | 9 / 30 (0.300000) |
| end ±10 frames | 15 / 28 (0.535714) | 15 / 30 (0.500000) |
| end ±15 frames | 18 / 28 (0.642857) | 18 / 30 (0.600000) |
| end ±30 frames | 25 / 28 (0.892857) | 25 / 30 (0.833333) |

Missed rally IDs: [3, 22].

| False detection ID | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| 3 | 1118 | 1455 | 37.266667 | 48.500000 |
| 4 | 1491 | 1615 | 49.700000 | 53.833333 |
| 5 | 1648 | 1943 | 54.933333 | 64.766667 |
| 22 | 6830 | 7018 | 227.666667 | 233.933333 |

| Runtime / resources | Value |
|---|---|
| parent_completed_elapsed_s | 1039.893208 |
| worker_elapsed_s | 1034.103667 |
| worker_source_fps | 10.371301 |
| media_ready_time_s | 1.810870 |
| model_staging_time_s | 1.687080 |
| component_initialization_including_models_s | 8.671007 |
| worker_final_cpu_s | 12506.818761 |
| worker_maxrss_bytes | 2926637056 |
| sampled_worker_tree_peak_rss_bytes | 2906685440 |
| sampled_worker_gpu_peak_mib | 2122 |
| sampled_cpu_seconds_max_observed | 12506.370000 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| sample_count | 502 |
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
      "frames": 10725,
      "raw_shuttle_present": 6489,
      "detector_executed_frames": 4071,
      "person_rows": 20210,
      "scene_telemetry_present": 3607,
      "scene_raw_hypotheses": 13,
      "actual_content_epoch_increments": 13,
      "content_epoch_decreases": 0,
      "detailed_diagnostic_frames": 3600,
      "person_current_detector_matches": 8052,
      "person_propagated_or_unmatched": 12158,
      "pose_present_rows": 15036,
      "pose_current_source_rows": 15036,
      "pose_present_without_current_source": 0,
      "pose_current_on_propagated_box": 6984,
      "racket_present_rows": 6671,
      "racket_current_source_rows": 6671,
      "racket_present_without_current_source": 0,
      "racket_current_on_propagated_box": 0,
      "scene_decision_records": 13,
      "scene_positive_correspondence_vetoes": 0,
      "scene_current_detector_probes": 13
    },
    "categories": {
      "view": {
        "main": 10230,
        "none": 495
      },
      "calibration_state": {
        "REACQUIRING": 36,
        "VALID": 10194,
        "LOST": 495
      },
      "player_population": {
        "0": 552,
        "2": 10037,
        "1": 136
      },
      "association_status": {
        "missing": 3741,
        "observed": 6487,
        "invalid": 495,
        "ambiguous": 2
      },
      "association_reason": {
        "no_accepted_raw_observation": 3741,
        "fresh_selection_retained": 6487,
        "image_view_invalid": 495,
        "coobserved_competing_static_hypothesis": 2
      },
      "scene_raw_status": {
        "unknown": 255,
        "measured": 3339,
        "hypothesis": 13
      },
      "person_detector_match": {
        "True": 8052,
        "False": 12158
      },
      "person_identity_method": {
        "bytetrack_v1": 20210
      },
      "scene_decision": {
        "barrier": 13
      },
      "scene_decision_reason": {
        "raw_change_and_current_layout_discontinuity": 13
      }
    },
    "scene_records": [
      {
        "frame": 1967,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 1,
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
                "key": "track:2",
                "bbox": [
                  404.84393310546875,
                  333.9048767089844,
                  456.91400146484375,
                  492.8191833496094
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 35,
              "consistent_fraction": 0.17142857142857143,
              "median_patch_error": 30.77147102355957,
              "median_forward_backward_error": 12.865859985351562,
              "discontinuity": 25.49636170523507,
              "previous_mean": 0.0,
              "adaptive_ratio": 25.49636170523507,
              "appearance_previous_mean": 9.463860511779785,
              "appearance_adaptive_ratio": 3.251471319263205
            },
            {
              "region": {
                "frame": 1966,
                "key": "track:0",
                "bbox": [
                  547.1536865234375,
                  245.2483673095703,
                  589.9750366210938,
                  382.1310119628906
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 25,
              "consistent_fraction": 0.64,
              "median_patch_error": 20.90263557434082,
              "median_forward_backward_error": 0.5698110461235046,
              "discontinuity": 7.524948806762695,
              "previous_mean": 0.0,
              "adaptive_ratio": 7.524948806762695,
              "appearance_previous_mean": 8.883663177490234,
              "appearance_adaptive_ratio": 2.3529297719554156
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.6792446374893188,
          "discontinuity": 16.510655255998884,
          "photometric_gain": 1.0098039215686274,
          "photometric_offset": -0.7254901960784252,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 25.837053298950195
        },
        "decision": {
          "frame": 1967,
          "previous_frame": 1966,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 1967,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6a798fa367f4904953986a0afecf4c230c15630e6b570da52e5804d8b40c8ba1",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              541.3108479306102,
              382.3961183279753,
              602.0433911755681,
              560.6022564917803
            ],
            [
              632.5491068214178,
              241.04043266177177,
              688.0458848625422,
              374.31712141633034
            ],
            [
              793.4994860813022,
              151.20806681364775,
              830.6957417801023,
              202.44202023744583
            ],
            [
              452.5275711975992,
              155.85760889947414,
              485.4288682974875,
              204.74382592737675
            ],
            [
              622.37339406088,
              152.38210339471698,
              655.944940995425,
              204.94300000742078
            ]
          ],
          "detector_scores": [
            0.9279868641574766,
            0.8853797449401791,
            0.4892393279258036,
            0.48904415520027833,
            0.4704010072243618
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
        "frame": 2842,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 2,
        "raw": {
          "frame": 2842,
          "previous_frame": 2841,
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
                "frame": 2841,
                "key": "track:0",
                "bbox": [
                  870.6766357421875,
                  518.4119262695312,
                  943.37939453125,
                  715.0299682617188
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 56,
              "consistent_fraction": 0.017857142857142856,
              "median_patch_error": 37.45911407470703,
              "median_forward_backward_error": 24.817546844482422,
              "discontinuity": 36.790201323372976,
              "previous_mean": 0.0,
              "adaptive_ratio": 36.790201323372976,
              "appearance_previous_mean": 7.919359922409058,
              "appearance_adaptive_ratio": 4.730068394632584
            },
            {
              "region": {
                "frame": 2841,
                "key": "track:2",
                "bbox": [
                  647.1536865234375,
                  257.60125732421875,
                  693.1268310546875,
                  398.561767578125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.24,
              "median_patch_error": 30.694089889526367,
              "median_forward_backward_error": 3.481647253036499,
              "discontinuity": 23.32750831604004,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.32750831604004,
              "appearance_previous_mean": 7.677667856216431,
              "appearance_adaptive_ratio": 3.9978402900920065
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 1.050736904144287,
          "discontinuity": 30.058854819706507,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 34.0766019821167
        },
        "decision": {
          "frame": 2842,
          "previous_frame": 2841,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2842,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "18651b7ec94c5d0f95d63030e68d4e1b20da016678de72aef65daf4228c180d3",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              622.1300323754549,
              384.2769325375557,
              679.5872825831175,
              559.900326192379
            ],
            [
              538.8392650783062,
              242.33547566831112,
              593.6019614040852,
              362.8854818493128
            ],
            [
              452.3220246359706,
              155.49898021295667,
              484.962795086205,
              204.52378075942397
            ],
            [
              793.0655445605516,
              151.14828449115157,
              830.5887568444014,
              202.42942307516932
            ],
            [
              621.7387188673019,
              152.25226106494665,
              656.228236079216,
              204.70724469423294
            ]
          ],
          "detector_scores": [
            0.923405112567174,
            0.8665471245782675,
            0.4557688748973142,
            0.4553581311095727,
            0.4374642748304433
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
        "frame": 3384,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 3,
        "raw": {
          "frame": 3384,
          "previous_frame": 3383,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 3383,
                "key": "track:2",
                "bbox": [
                  739.211669921875,
                  397.9945983886719,
                  790.7786865234375,
                  577.2691650390625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.0,
              "median_patch_error": 23.475872039794922,
              "median_forward_backward_error": 15.906622886657715,
              "discontinuity": 23.475872039794922,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.475872039794922,
              "appearance_previous_mean": 8.22464895248413,
              "appearance_adaptive_ratio": 2.8543311909627938
            },
            {
              "region": {
                "frame": 3383,
                "key": "track:1",
                "bbox": [
                  728.0264892578125,
                  208.61947631835938,
                  767.7079467773438,
                  335.0721435546875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 20,
              "consistent_fraction": 0.15,
              "median_patch_error": 23.947067260742188,
              "median_forward_backward_error": 7.175207614898682,
              "discontinuity": 20.35500717163086,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.35500717163086,
              "appearance_previous_mean": 5.162609815597534,
              "appearance_adaptive_ratio": 4.638558426087541
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.2295563220977783,
          "discontinuity": 21.91543960571289,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 23.711469650268555
        },
        "decision": {
          "frame": 3384,
          "previous_frame": 3383,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3384,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "0acda2b5f950613fab22cd4b3d84d75e9b6173e57f9405d6ce1e2de425d97abf",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              546.0144735947251,
              379.17296229302883,
              601.4333582744002,
              555.5738313347101
            ],
            [
              631.7120836004615,
              236.54217018187046,
              687.8968422189355,
              372.03853575885296
            ],
            [
              793.2099795043468,
              151.1191521063447,
              830.6368615925312,
              202.40490017831326
            ],
            [
              452.69508085027337,
              155.44123953580856,
              484.927214410156,
              204.7108775600791
            ],
            [
              621.8826317861676,
              151.56023379787803,
              655.3449668809772,
              204.09381445869803
            ]
          ],
          "detector_scores": [
            0.9298334708468193,
            0.9010832120700363,
            0.5030271637112643,
            0.49844289329369273,
            0.49130086474096135
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
        "frame": 5666,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 4,
        "raw": {
          "frame": 5666,
          "previous_frame": 5665,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 5665,
                "key": "track:0",
                "bbox": [
                  513.6345825195312,
                  333.2555847167969,
                  580.89306640625,
                  488.159912109375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.41935483870967744,
              "median_patch_error": 20.82341194152832,
              "median_forward_backward_error": 3.011958122253418,
              "discontinuity": 12.091013385403539,
              "previous_mean": 0.0,
              "adaptive_ratio": 12.091013385403539,
              "appearance_previous_mean": 4.209360837936401,
              "appearance_adaptive_ratio": 4.946929651138389
            },
            {
              "region": {
                "frame": 5665,
                "key": "track:1",
                "bbox": [
                  651.7438354492188,
                  198.3332977294922,
                  704.8827514648438,
                  311.0414123535156
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.19230769230769232,
              "median_patch_error": 22.81806182861328,
              "median_forward_backward_error": 6.328315734863281,
              "discontinuity": 18.42997301541842,
              "previous_mean": 0.0,
              "adaptive_ratio": 18.42997301541842,
              "appearance_previous_mean": 9.158234119415283,
              "appearance_adaptive_ratio": 2.4915351072145473
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.6,
          "background_patch_error": 3.703869104385376,
          "discontinuity": 15.260493200410979,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 21.8207368850708
        },
        "decision": {
          "frame": 5666,
          "previous_frame": 5665,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 5666,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b7b3a970c36b4f6a2572c20a9dd3291ee44568a48601f8bee5a1ad3988e2b9df",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              686.108490422368,
              396.22820241749287,
              770.5422509163618,
              562.2348823994398
            ],
            [
              608.4570392481983,
              227.3324721902609,
              654.069323528558,
              362.43869407474995
            ],
            [
              794.5543626770377,
              151.15592277050018,
              831.1041282191873,
              202.4622051641345
            ],
            [
              452.8571137674153,
              155.8060668259859,
              484.61647982522845,
              204.5870275646448
            ],
            [
              622.4719405993819,
              151.27047380805016,
              656.5346707478166,
              235.04678493738174
            ]
          ],
          "detector_scores": [
            0.9313732600741083,
            0.9004364190115444,
            0.6652189077758315,
            0.5533463110071242,
            0.5300850594994173
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
        "frame": 6293,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 5,
        "raw": {
          "frame": 6293,
          "previous_frame": 6292,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 6292,
                "key": "track:2",
                "bbox": [
                  546.9710693359375,
                  352.6015319824219,
                  599.9176025390625,
                  509.2771911621094
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 30,
              "consistent_fraction": 0.03333333333333333,
              "median_patch_error": 31.374858856201172,
              "median_forward_backward_error": 18.041015625,
              "discontinuity": 30.329030227661132,
              "previous_mean": 0.20423538344246991,
              "adaptive_ratio": 30.329030227661132,
              "appearance_previous_mean": 10.79370403289795,
              "appearance_adaptive_ratio": 2.9067740564846196
            },
            {
              "region": {
                "frame": 6292,
                "key": "track:1",
                "bbox": [
                  407.55224609375,
                  158.35086059570312,
                  453.9424743652344,
                  282.1579895019531
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 24,
              "consistent_fraction": 0.625,
              "median_patch_error": 19.57245635986328,
              "median_forward_backward_error": 0.730311393737793,
              "discontinuity": 7.3396711349487305,
              "previous_mean": 0.0,
              "adaptive_ratio": 7.3396711349487305,
              "appearance_previous_mean": 8.417587757110596,
              "appearance_adaptive_ratio": 2.3251858994080368
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.5263605117797852,
          "discontinuity": 18.834350681304933,
          "photometric_gain": 0.9900990099009901,
          "photometric_offset": -0.26732673267326845,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 25.473657608032227
        },
        "decision": {
          "frame": 6293,
          "previous_frame": 6292,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 6293,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "efa8fca0c8ff52d8cb9d9a3e96417c4a95093f3389a8c73eded2a56225d69372",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              584.3426996171474,
              380.2586714029312,
              665.5904182493687,
              547.8452733755112
            ],
            [
              669.0616079308093,
              247.75927702337503,
              711.8550843261182,
              373.2075903043151
            ],
            [
              623.1247101426125,
              151.0,
              656.6698269248009,
              205.036793615669
            ],
            [
              794.8961773589253,
              151.0,
              832.4942051693797,
              202.30792202427983
            ],
            [
              453.11627500504255,
              155.92246586829424,
              484.4461533501744,
              204.45501940697432
            ]
          ],
          "detector_scores": [
            0.9474733657251774,
            0.8942196638995541,
            0.5621786134704486,
            0.554275742303955,
            0.4997804165027644
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
        "frame": 7019,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 6,
        "raw": {
          "frame": 7019,
          "previous_frame": 7018,
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
                "frame": 7018,
                "key": "track:2",
                "bbox": [
                  605.0897216796875,
                  384.0787353515625,
                  664.5032348632812,
                  546.0892333984375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 37,
              "consistent_fraction": 0.02702702702702703,
              "median_patch_error": 37.073482513427734,
              "median_forward_backward_error": 29.048625946044922,
              "discontinuity": 36.07149649955131,
              "previous_mean": 0.0,
              "adaptive_ratio": 36.07149649955131,
              "appearance_previous_mean": 7.889491081237793,
              "appearance_adaptive_ratio": 4.699096827879451
            },
            {
              "region": {
                "frame": 7018,
                "key": "track:0",
                "bbox": [
                  468.45892333984375,
                  250.3932647705078,
                  549.3212280273438,
                  392.73443603515625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 31,
              "consistent_fraction": 0.0967741935483871,
              "median_patch_error": 19.346725463867188,
              "median_forward_backward_error": 10.786463737487793,
              "discontinuity": 17.474461709299394,
              "previous_mean": 0.0,
              "adaptive_ratio": 17.474461709299394,
              "appearance_previous_mean": 6.13155460357666,
              "appearance_adaptive_ratio": 3.1552724740609586
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.2242064476013184,
          "discontinuity": 26.772979104425353,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 28.21010398864746
        },
        "decision": {
          "frame": 7019,
          "previous_frame": 7018,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7019,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "ad3f45b2c685309e50f580bd4708a45b9bb3c8ab94e9b40df1a6ef353dc133d1",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              681.2327715456486,
              401.82011327147484,
              763.4679561555386,
              566.9141398966312
            ],
            [
              597.9068867564201,
              238.70046714693308,
              663.8107417225838,
              374.34387328475714
            ],
            [
              794.2042936645448,
              151.05316276103258,
              831.9559205211699,
              202.46210834383965
            ],
            [
              452.7788915000856,
              155.7150894254446,
              484.45760018005967,
              204.73911540955305
            ],
            [
              622.9939957037568,
              151.07441060617566,
              656.9531054124236,
              205.57379264757037
            ],
            [
              1016.871424017474,
              153.17118669301271,
              1041.8678318876773,
              238.40884441882372
            ]
          ],
          "detector_scores": [
            0.9309696106383879,
            0.9074449086204505,
            0.790986896651338,
            0.6664527978325151,
            0.6463110042912343,
            0.5118318161632077
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
        "frame": 7431,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 7,
        "raw": {
          "frame": 7431,
          "previous_frame": 7430,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 7430,
                "key": "track:0",
                "bbox": [
                  544.1725463867188,
                  436.6958312988281,
                  611.7987060546875,
                  617.621826171875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 45,
              "consistent_fraction": 0.24444444444444444,
              "median_patch_error": 37.568382263183594,
              "median_forward_backward_error": 4.699180603027344,
              "discontinuity": 28.38499993218316,
              "previous_mean": 0.0,
              "adaptive_ratio": 28.38499993218316,
              "appearance_previous_mean": 4.138144809752703,
              "appearance_adaptive_ratio": 9.078556693966613
            },
            {
              "region": {
                "frame": 7430,
                "key": "track:1",
                "bbox": [
                  320.9808044433594,
                  152.14247131347656,
                  367.4364318847656,
                  271.77227783203125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 27,
              "consistent_fraction": 0.8888888888888888,
              "median_patch_error": 20.158658981323242,
              "median_forward_backward_error": 0.3637866973876953,
              "discontinuity": 2.2398509979248056,
              "previous_mean": 0.0,
              "adaptive_ratio": 2.2398509979248056,
              "appearance_previous_mean": 3.2528344616293907,
              "appearance_adaptive_ratio": 6.1972594114812365
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 1.261763095855713,
          "discontinuity": 15.312425465053982,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 28.863520622253418
        },
        "decision": {
          "frame": 7431,
          "previous_frame": 7430,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7431,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "906d8d8839c736bb8dd4d103e6ae615319c0c8f9eb4c66e2e219e299edfc099c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              499.8094345331192,
              394.963148444891,
              584.7571451663971,
              563.288716584444
            ],
            [
              633.9146848097444,
              223.82488338649273,
              678.8552195653319,
              359.2173902541399
            ],
            [
              794.4149126186967,
              151.0439227372408,
              831.6793514117599,
              202.64647944271564
            ],
            [
              623.6715523786843,
              151.5821257084608,
              655.9750554971397,
              204.20401910692453
            ],
            [
              451.6031133271754,
              155.74767997860909,
              484.4849476478994,
              204.48137978464365
            ],
            [
              1003.0778846219182,
              151.2694635093212,
              1041.9093637987971,
              237.83384552598
            ]
          ],
          "detector_scores": [
            0.9256756110001705,
            0.8982763018801273,
            0.8178901724096123,
            0.6521642961233269,
            0.6002290931331563,
            0.5153887529817195
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
        "frame": 7706,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 8,
        "raw": {
          "frame": 7706,
          "previous_frame": 7705,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 7705,
                "key": "track:0",
                "bbox": [
                  416.12738037109375,
                  419.27252197265625,
                  475.8901062011719,
                  596.5226440429688
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 32,
              "consistent_fraction": 0.0,
              "median_patch_error": 36.07419204711914,
              "median_forward_backward_error": 36.25651168823242,
              "discontinuity": 36.07419204711914,
              "previous_mean": 0.0,
              "adaptive_ratio": 36.07419204711914,
              "appearance_previous_mean": 5.966570854187012,
              "appearance_adaptive_ratio": 6.046051061608403
            },
            {
              "region": {
                "frame": 7705,
                "key": "track:1",
                "bbox": [
                  345.6779479980469,
                  236.7090606689453,
                  398.0001525878906,
                  378.4903259277344
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 27,
              "consistent_fraction": 0.3333333333333333,
              "median_patch_error": 28.900510787963867,
              "median_forward_backward_error": 4.48319673538208,
              "discontinuity": 19.267007191975914,
              "previous_mean": 0.15943830891659366,
              "adaptive_ratio": 19.267007191975914,
              "appearance_previous_mean": 11.939997673034668,
              "appearance_adaptive_ratio": 2.4204787621720296
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9375,
          "background_patch_error": 1.6355229616165161,
          "discontinuity": 27.670599619547527,
          "photometric_gain": 0.9900990099009901,
          "photometric_offset": 0.722772277227719,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 32.487351417541504
        },
        "decision": {
          "frame": 7706,
          "previous_frame": 7705,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7706,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b0c2689c24ece212718697206cfa863e7516eeb577f55295268cca6a766fa421",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              685.1663440540433,
              394.77891205251217,
              769.6970804855227,
              561.2511040121317
            ],
            [
              602.0807929039001,
              230.6324361860752,
              650.0989271402359,
              374.0064208805561
            ],
            [
              794.1203230880201,
              151.0731708854437,
              831.3156946636736,
              202.45368076860905
            ],
            [
              452.231468398124,
              155.89591816440225,
              484.30839459225535,
              204.44613509252667
            ],
            [
              623.2374373525381,
              152.02553529664874,
              656.3828097730875,
              204.60015934333205
            ]
          ],
          "detector_scores": [
            0.9314616241640483,
            0.9101795944573093,
            0.7078071249049486,
            0.5469060629058988,
            0.5040035584249962
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
        "frame": 8276,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 9,
        "raw": {
          "frame": 8276,
          "previous_frame": 8275,
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
                "frame": 8275,
                "key": "track:0",
                "bbox": [
                  758.609375,
                  401.6812744140625,
                  808.9769287109375,
                  563.598388671875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 34,
              "consistent_fraction": 0.0,
              "median_patch_error": 28.2763614654541,
              "median_forward_backward_error": 30.95090103149414,
              "discontinuity": 28.2763614654541,
              "previous_mean": 0.0,
              "adaptive_ratio": 28.2763614654541,
              "appearance_previous_mean": 9.314891338348389,
              "appearance_adaptive_ratio": 3.0356083005545553
            },
            {
              "region": {
                "frame": 8275,
                "key": "track:2",
                "bbox": [
                  800.583740234375,
                  240.620849609375,
                  861.9346313476562,
                  359.2674560546875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.12,
              "median_patch_error": 44.97037887573242,
              "median_forward_backward_error": 13.630105018615723,
              "discontinuity": 39.57393341064453,
              "previous_mean": 0.0,
              "adaptive_ratio": 39.57393341064453,
              "appearance_previous_mean": 10.916985511779785,
              "appearance_adaptive_ratio": 4.119303705881803
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.925,
          "background_patch_error": 1.3713152408599854,
          "discontinuity": 33.925147438049315,
          "photometric_gain": 0.9900990099009901,
          "photometric_offset": 0.722772277227719,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 36.62337017059326
        },
        "decision": {
          "frame": 8276,
          "previous_frame": 8275,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 8276,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "ead7542dc3eb4f363cbc46c3bd0e0fca65ec7e8beb773e743b7120401f809ec7",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              671.2886522784829,
              239.8243529200554,
              716.9871310219169,
              366.5341672897339
            ],
            [
              594.258344385773,
              374.97217385470867,
              642.827770140022,
              532.5673423558474
            ],
            [
              621.021335914731,
              151.0,
              656.8672126978636,
              204.24266934767365
            ],
            [
              794.288719881326,
              151.0917224958539,
              831.4857390038669,
              202.2191904336214
            ],
            [
              452.32617669552565,
              155.61927521973848,
              484.34182078391314,
              204.67456573992968
            ]
          ],
          "detector_scores": [
            0.9164339118238227,
            0.9106038729774005,
            0.6480551444802296,
            0.5630137285011386,
            0.5524644911328607
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
        "frame": 8977,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 10,
        "raw": {
          "frame": 8977,
          "previous_frame": 8976,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 8976,
                "key": "track:3",
                "bbox": [
                  557.6295166015625,
                  390.5475158691406,
                  616.7679443359375,
                  555.9519653320312
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 39,
              "consistent_fraction": 0.5384615384615384,
              "median_patch_error": 32.77381134033203,
              "median_forward_backward_error": 0.915249228477478,
              "discontinuity": 15.126374464768631,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.126374464768631,
              "appearance_previous_mean": 11.69711971282959,
              "appearance_adaptive_ratio": 2.8018702163392573
            },
            {
              "region": {
                "frame": 8976,
                "key": "track:2",
                "bbox": [
                  444.66705322265625,
                  174.534423828125,
                  486.58197021484375,
                  299.2979736328125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 24,
              "consistent_fraction": 0.2916666666666667,
              "median_patch_error": 28.442672729492188,
              "median_forward_backward_error": 1.1934099197387695,
              "discontinuity": 20.146893183390297,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.146893183390297,
              "appearance_previous_mean": 6.769628524780273,
              "appearance_adaptive_ratio": 4.201511593343354
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.2331349849700928,
          "discontinuity": 17.636633824079464,
          "photometric_gain": 0.9900990099009901,
          "photometric_offset": 0.722772277227719,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 30.60824203491211
        },
        "decision": {
          "frame": 8977,
          "previous_frame": 8976,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 8977,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "febedc54a6bef235248a067cdfad2b67de63fd6a43fc162dcb5eb304285968cc",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              622.8143497258425,
              230.3564309924841,
              673.4246606081724,
              370.19896699488163
            ],
            [
              500.294917717576,
              394.40237371623516,
              584.6473268121481,
              561.0977069884539
            ],
            [
              620.8280675001442,
              151.03265369683504,
              656.5633926801383,
              203.66835030168295
            ],
            [
              794.779114022851,
              151.11604754254222,
              831.9319722503424,
              202.37150349095464
            ],
            [
              452.1806132122874,
              155.75863540545106,
              484.16004747897387,
              204.4631502069533
            ]
          ],
          "detector_scores": [
            0.921057924625653,
            0.9170860540691247,
            0.6254650266314006,
            0.6134087831911247,
            0.5326789220144924
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
        "frame": 9195,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 11,
        "raw": {
          "frame": 9195,
          "previous_frame": 9194,
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
                "frame": 9194,
                "key": "track:1",
                "bbox": [
                  430.61016845703125,
                  473.5200500488281,
                  494.32574462890625,
                  658.8898315429688
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 42,
              "consistent_fraction": 0.0,
              "median_patch_error": 44.65373229980469,
              "median_forward_backward_error": 48.24778747558594,
              "discontinuity": 44.65373229980469,
              "previous_mean": 0.0,
              "adaptive_ratio": 44.65373229980469,
              "appearance_previous_mean": 6.085530042648315,
              "appearance_adaptive_ratio": 7.337689895023864
            },
            {
              "region": {
                "frame": 9194,
                "key": "track:0",
                "bbox": [
                  626.3606567382812,
                  237.22586059570312,
                  677.0507202148438,
                  378.70703125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 26,
              "consistent_fraction": 0.5769230769230769,
              "median_patch_error": 26.442991256713867,
              "median_forward_backward_error": 0.70071941614151,
              "discontinuity": 11.187419377840484,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.187419377840484,
              "appearance_previous_mean": 6.685621976852417,
              "appearance_adaptive_ratio": 3.9552028739087035
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.7625,
          "background_patch_error": 17.89976692199707,
          "discontinuity": 27.920575838822586,
          "photometric_gain": 0.98989898989899,
          "photometric_offset": 0.7373737373737299,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 35.54836177825928
        },
        "decision": {
          "frame": 9195,
          "previous_frame": 9194,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 9195,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "710fd95bd18491602c3b0b9cb55c49c1bf6aa31d0ff270867e3cd351891317a6",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              627.3444066271186,
              370.48277674615383,
              702.5999610200524,
              533.5035861879587
            ],
            [
              527.1272314414382,
              235.7465220466256,
              578.7197639122605,
              365.7995748743415
            ],
            [
              619.5399589166045,
              151.03012584522367,
              658.5265488997102,
              203.6361028291285
            ],
            [
              794.4152777343988,
              151.06440233439207,
              831.0237333625555,
              202.83456759899855
            ],
            [
              452.10649925097823,
              156.23622466251254,
              484.1558999456465,
              204.51197289302945
            ]
          ],
          "detector_scores": [
            0.9421174688421738,
            0.8957589380188749,
            0.6622321504216006,
            0.6488174782194953,
            0.573466610624893
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
        "frame": 9881,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 12,
        "raw": {
          "frame": 9881,
          "previous_frame": 9880,
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
                "frame": 9880,
                "key": "track:1",
                "bbox": [
                  742.9022216796875,
                  403.34722900390625,
                  797.386474609375,
                  569.3776245117188
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 34,
              "consistent_fraction": 0.0,
              "median_patch_error": 32.59977340698242,
              "median_forward_backward_error": 25.765514373779297,
              "discontinuity": 32.59977340698242,
              "previous_mean": 0.0,
              "adaptive_ratio": 32.59977340698242,
              "appearance_previous_mean": 3.4286422729492188,
              "appearance_adaptive_ratio": 9.508070778973696
            },
            {
              "region": {
                "frame": 9880,
                "key": "track:2",
                "bbox": [
                  813.2859497070312,
                  185.14431762695312,
                  854.6264038085938,
                  305.7394714355469
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 24,
              "consistent_fraction": 0.3333333333333333,
              "median_patch_error": 32.56235885620117,
              "median_forward_backward_error": 5.7159881591796875,
              "discontinuity": 21.70823923746745,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.70823923746745,
              "appearance_previous_mean": 4.775297813117504,
              "appearance_adaptive_ratio": 6.818916878179619
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.925,
          "background_patch_error": 1.1611748933792114,
          "discontinuity": 27.154006322224937,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 32.5810661315918
        },
        "decision": {
          "frame": 9881,
          "previous_frame": 9880,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 9881,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "5d8f354ea43e4345f17561d3ae0c747c8e7081e905a5c0a1120e517742f089c9",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              494.9103512689471,
              398.6901741325855,
              545.3993290737271,
              566.510794967413
            ],
            [
              676.5143949054182,
              212.99211943894625,
              720.4185291267931,
              352.03095438331366
            ],
            [
              622.2809881046414,
              151.0554464571178,
              656.3445027992129,
              204.30645708367229
            ],
            [
              794.4811509437859,
              151.07080299779773,
              831.3478640727699,
              201.99701521918178
            ],
            [
              451.6319363452494,
              155.70616091042757,
              484.7687360905111,
              204.43623626977205
            ]
          ],
          "detector_scores": [
            0.9109391077069006,
            0.8994400290693138,
            0.5465484861147654,
            0.49610825291784677,
            0.47143176730763364
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
        "frame": 10435,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 13,
        "raw": {
          "frame": 10435,
          "previous_frame": 10434,
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
                "frame": 10434,
                "key": "track:0",
                "bbox": [
                  714.3770751953125,
                  341.0911560058594,
                  797.5843505859375,
                  490.2862243652344
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 27,
              "consistent_fraction": 0.037037037037037035,
              "median_patch_error": 29.276714324951172,
              "median_forward_backward_error": 25.187780380249023,
              "discontinuity": 28.192391572175204,
              "previous_mean": 0.0,
              "adaptive_ratio": 28.192391572175204,
              "appearance_previous_mean": 5.603050708770752,
              "appearance_adaptive_ratio": 5.225138205357089
            },
            {
              "region": {
                "frame": 10434,
                "key": "track:1",
                "bbox": [
                  813.0923461914062,
                  365.073974609375,
                  919.3463134765625,
                  432.6128845214844
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 27,
              "consistent_fraction": 0.3333333333333333,
              "median_patch_error": 21.626983642578125,
              "median_forward_backward_error": 2.918900966644287,
              "discontinuity": 14.417989095052086,
              "previous_mean": 0.0,
              "adaptive_ratio": 14.417989095052086,
              "appearance_previous_mean": 5.752303123474121,
              "appearance_adaptive_ratio": 3.7597086207648323
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.1308815479278564,
          "discontinuity": 21.305190333613645,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 25.45184898376465
        },
        "decision": {
          "frame": 10435,
          "previous_frame": 10434,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 10435,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "d1d06aaba9973a7aa9ca554733896bde16f7275b8910c150b7d76ac2725cbcf1",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              688.1670972406864,
              399.2310628145933,
              774.0959733426571,
              565.4564724713564
            ],
            [
              601.9056942760944,
              218.53420993685722,
              645.9240674674511,
              362.02272883057594
            ],
            [
              794.1854358911514,
              151.12828899547458,
              831.4133812189102,
              202.58687813207507
            ],
            [
              451.72345516085625,
              155.80379996821284,
              484.83084347844124,
              204.40242283418775
            ],
            [
              622.2451328374445,
              151.14501785859466,
              656.4492050074041,
              205.28673731163144
            ]
          ],
          "detector_scores": [
            0.9298621802922309,
            0.9097978482125895,
            0.6205285383600199,
            0.4985672274705733,
            0.48981771595602314
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
      "activity_interval": 98,
      "scene": 14,
      "participant_observation": 130,
      "format_decision": 1,
      "rally_start": 60,
      "rally_end": 32,
      "contact": 544,
      "stroke": 262,
      "shuttle_turn": 22,
      "identity_ambiguity": 41,
      "broadcast_score": 261,
      "match_phase": 1
    },
    "live_counts": {
      "calibration": 1,
      "activity_interval": 98,
      "scene": 14,
      "participant_observation": 130,
      "format_decision": 1,
      "rally_start": 32,
      "rally_end": 32,
      "stroke": 250,
      "contact": 250,
      "shuttle_turn": 22,
      "identity_ambiguity": 41,
      "broadcast_score": 261,
      "match_phase": 1
    },
    "categories": {
      "event_status": {
        "confirmed": 908,
        "provisional": 225
      },
      "rally_end_reason": {
        "stationary": 11,
        "cut": 11,
        "gap": 10
      },
      "rally_phase": {
        "unknown": 3,
        "match_play": 29
      },
      "rally_official": {
        "False": 11,
        "True": 21
      },
      "rally_match_format_known": {
        "True": 32
      },
      "rally_match_format": {
        "singles": 32
      },
      "rally_winner": {
        "None": 32
      },
      "rally_score_transition_status": {
        "unavailable": 23,
        "candidate": 9
      },
      "rally_admission_reason": {
        "duration_policy": 32
      },
      "stroke_actor": {
        "unknown": 250
      },
      "stroke_physical_event_status": {
        "insufficient": 126,
        "probable": 34,
        "ambiguous": 90
      },
      "stroke_contact_status": {
        "estimated": 250
      },
      "stroke_classification_status": {
        "unknown": 184,
        "estimated": 66
      },
      "stroke_stroke": {
        "unknown": 184,
        "push": 27,
        "lift": 8,
        "net_shot": 10,
        "drop": 14,
        "clear": 3,
        "drive": 3,
        "smash": 1
      },
      "stroke_attribution_reason": {
        "nearest_proximity": 250
      },
      "stroke_classification_abstention_reason": {
        "missing_required_evidence": 182,
        "unresolved_initial_contact": 2
      },
      "contact_actor": {
        "unknown": 250
      },
      "contact_physical_event_status": {
        "insufficient": 126,
        "probable": 34,
        "ambiguous": 90
      },
      "contact_contact_status": {
        "estimated": 250
      },
      "contact_attribution_reason": {
        "nearest_proximity": 250
      },
      "contact_trajectory_reliability": {
        "insufficient": 64,
        "probable": 130,
        "ambiguous": 56
      },
      "contact_trajectory_reasons": {
        "coherent_motion_change_unavailable": 64,
        "supported_turn": 100,
        "association_unresolved": 56,
        "supported_launch": 30
      },
      "contact_impact_reliability": {
        "insufficient": 126,
        "probable": 34,
        "ambiguous": 90
      },
      "contact_impact_reasons": {
        "fresh_player_observation_unavailable": 126,
        "coherent_motion_and_fresh_contact_cue": 34,
        "no_fresh_swing_or_racket_overlap": 17,
        "association_unresolved": 56,
        "coherent_motion_change_unavailable": 17
      },
      "contact_attribution_reliability": {
        "insufficient": 167,
        "probable": 83
      },
      "contact_attribution_reasons": {
        "fresh_player_observation_unavailable": 167,
        "geometric_attribution_not_verified_identity": 83
      }
    },
    "physical_accuracy_validated": false
  },
  "ocr": {
    "readout_count": 289,
    "label_counts": {
      "TAI T.Y.": 289,
      "MARIN": 289
    },
    "context_counts": {
      "{\"acquisition_policy\":\"main_camera\",\"actual_replay_status\":\"unknown\",\"analysis_excluded\":false,\"view\":\"main\"}": 289
    },
    "previously_source_reviewed_branding_strings": {},
    "readouts": [
      {
        "f": 992,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.98749,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1022,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.99241,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1052,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.99241,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1082,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.99336,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1112,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.99324,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1142,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.99335,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1172,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.9931,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1202,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.97836,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1232,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.97836,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1262,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.94122,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1292,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.94122,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1322,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.943,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1352,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.943,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1382,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.94027,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1412,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.94131,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1442,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.9933,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1472,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.9933,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1502,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.9936,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1532,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.9936,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1562,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.9942,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1592,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.9942,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1622,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.9942,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1652,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99652,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1682,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99697,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1712,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99737,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1742,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.93916,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1772,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.93916,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1802,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99386,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1832,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99386,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1862,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99426,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1892,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99426,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1922,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.9942,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1952,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99204,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1982,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.97608,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2012,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99354,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2042,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99172,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2072,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.98194,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2102,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.97907,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2132,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.97907,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2162,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.93708,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2192,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.93708,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2222,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.95626,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2252,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.9588,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2282,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99701,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2312,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99701,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2342,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.94684,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2395,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.95884,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2425,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.9922,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2455,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.9967,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2485,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99156,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2515,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99156,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2545,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99146,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2575,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99146,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2605,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99433,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2635,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.99433,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2665,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.94114,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2695,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.94114,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2725,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.94308,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2755,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.93841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2785,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.95011,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2815,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            7
          ]
        ],
        "c": 0.94883,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2845,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.93777,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2875,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.99487,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2905,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.94,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2935,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.99309,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2965,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.93761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2995,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.93761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3025,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.93761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3055,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.93761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3085,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.98227,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3115,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.98227,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3145,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.93954,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3175,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.9396,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3205,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.9392,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3235,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.9438,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3265,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.94548,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3295,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.94548,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3325,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.94482,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3355,
        "r": [
          [
            "TAI T.Y.",
            4
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.94482,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3385,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.99211,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3415,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.99116,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3445,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.99288,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3475,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.93804,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3505,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            8
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
        "f": 3535,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            8
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
        "f": 3565,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.99209,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3710,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.99316,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3740,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.99186,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3770,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.95476,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3800,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.9921,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3830,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.9921,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3860,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            8
          ]
        ],
        "c": 0.97874,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3890,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.98298,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3920,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.94056,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3950,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.94056,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3980,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99487,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4010,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.9383,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4040,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.94297,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4070,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.94297,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4100,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99453,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4130,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99453,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4160,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.938,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4190,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.938,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4220,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.9382,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4250,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.9382,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4280,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.87966,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4310,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.98978,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4340,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99128,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4370,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99128,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4404,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.98252,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4434,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
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
        "f": 4464,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.99269,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4494,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.93782,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4524,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.99085,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4554,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            12
          ]
        ],
        "c": 0.99274,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4584,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            12
          ]
        ],
        "c": 0.93976,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4614,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            12
          ]
        ],
        "c": 0.9398,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4644,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            12
          ]
        ],
        "c": 0.94665,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4674,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            12
          ]
        ],
        "c": 0.94059,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4704,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            12
          ]
        ],
        "c": 0.94024,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4734,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            14
          ]
        ],
        "c": 0.93888,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4764,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            14
          ]
        ],
        "c": 0.99273,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4794,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            14
          ]
        ],
        "c": 0.99214,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4824,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            14
          ]
        ],
        "c": 0.99172,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4854,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.98975,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4884,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.99154,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4914,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.9915,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4944,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.99361,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4974,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.99361,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5004,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.99113,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5034,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.9927,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5064,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.99333,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5094,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.99333,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5124,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.93816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5154,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.93816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5184,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.94099,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5214,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.94082,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5244,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            18
          ]
        ],
        "c": 0.93581,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5274,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.99049,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5304,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.99171,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5334,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.99221,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5364,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.93789,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5394,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.98866,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5424,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99283,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5454,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.9929,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5484,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99005,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5514,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99005,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5544,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99044,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5574,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99088,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5604,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.9926,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5634,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.9926,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5664,
        "r": [
          [
            "TAI T.Y.",
            8
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99348,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6384,
        "r": [
          [
            "TAI T.Y.",
            1
          ],
          [
            "MARIN",
            3
          ]
        ],
        "c": 0.89605,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6414,
        "r": [
          [
            "TAI T.Y.",
            1
          ],
          [
            "MARIN",
            3
          ]
        ],
        "c": 0.99285,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6444,
        "r": [
          [
            "TAI T.Y.",
            1
          ],
          [
            "MARIN",
            3
          ]
        ],
        "c": 0.991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6474,
        "r": [
          [
            "TAI T.Y.",
            1
          ],
          [
            "MARIN",
            3
          ]
        ],
        "c": 0.991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6504,
        "r": [
          [
            "TAI T.Y.",
            1
          ],
          [
            "MARIN",
            3
          ]
        ],
        "c": 0.99104,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6534,
        "r": [
          [
            "TAI T.Y.",
            1
          ],
          [
            "MARIN",
            3
          ]
        ],
        "c": 0.99104,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6564,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            4
          ]
        ],
        "c": 0.99228,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6594,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            4
          ]
        ],
        "c": 0.9924,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6624,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            4
          ]
        ],
        "c": 0.99314,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6654,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            4
          ]
        ],
        "c": 0.9912,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6684,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            4
          ]
        ],
        "c": 0.99126,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6714,
        "r": [
          [
            "TAI T.Y.",
            2
          ],
          [
            "MARIN",
            4
          ]
        ],
        "c": 0.99136,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6825,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.98995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6855,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.992,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6885,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.99204,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6915,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.99229,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6945,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.99229,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6975,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.99321,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7005,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            5
          ]
        ],
        "c": 0.9932,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7035,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.9919,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7065,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99172,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7095,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7125,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7155,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99053,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7185,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99053,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7215,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99118,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7245,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99118,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7275,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99243,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7305,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99228,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7335,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99101,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7365,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99119,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7395,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99228,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7425,
        "r": [
          [
            "TAI T.Y.",
            3
          ],
          [
            "MARIN",
            6
          ]
        ],
        "c": 0.99228,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7455,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99264,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7485,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99176,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7515,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99328,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7545,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99328,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7575,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.94201,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7605,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.94201,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7635,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99231,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7665,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99231,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7695,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            9
          ]
        ],
        "c": 0.99282,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7725,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            10
          ]
        ],
        "c": 0.98906,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7755,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            10
          ]
        ],
        "c": 0.99145,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7785,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            10
          ]
        ],
        "c": 0.99145,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7815,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            10
          ]
        ],
        "c": 0.99269,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7845,
        "r": [
          [
            "TAI T.Y.",
            5
          ],
          [
            "MARIN",
            10
          ]
        ],
        "c": 0.99269,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7925,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.99422,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7955,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.99406,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7985,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.94102,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8015,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.92306,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8045,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.99362,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8075,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.99339,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8105,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.94328,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8135,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.94328,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8165,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.93896,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8195,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.93896,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8225,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.99387,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8255,
        "r": [
          [
            "TAI T.Y.",
            6
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.99387,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8285,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.94056,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8315,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.94038,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8345,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.94203,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8375,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.94203,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8405,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.9427,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8435,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.9383,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8465,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
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
        "f": 8495,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
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
        "f": 8525,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.994,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8555,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.994,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8585,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            11
          ]
        ],
        "c": 0.93997,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8615,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.94045,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8645,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.94148,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8675,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.94148,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8705,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.93738,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8735,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.93738,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8765,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.99444,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8795,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.99444,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8825,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.99404,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8855,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.99404,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8885,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.99409,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8915,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.99262,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8945,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.99214,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8975,
        "r": [
          [
            "TAI T.Y.",
            7
          ],
          [
            "MARIN",
            13
          ]
        ],
        "c": 0.99214,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9005,
        "r": [
          [
            "TAI T.Y.",
            9
          ],
          [
            "MARIN",
            15
          ]
        ],
        "c": 0.93811,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9035,
        "r": [
          [
            "TAI T.Y.",
            9
          ],
          [
            "MARIN",
            15
          ]
        ],
        "c": 0.9388,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9065,
        "r": [
          [
            "TAI T.Y.",
            9
          ],
          [
            "MARIN",
            15
          ]
        ],
        "c": 0.94229,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9095,
        "r": [
          [
            "TAI T.Y.",
            9
          ],
          [
            "MARIN",
            15
          ]
        ],
        "c": 0.94186,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9125,
        "r": [
          [
            "TAI T.Y.",
            9
          ],
          [
            "MARIN",
            15
          ]
        ],
        "c": 0.99416,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9155,
        "r": [
          [
            "TAI T.Y.",
            9
          ],
          [
            "MARIN",
            15
          ]
        ],
        "c": 0.99416,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9185,
        "r": [
          [
            "TAI T.Y.",
            9
          ],
          [
            "MARIN",
            15
          ]
        ],
        "c": 0.99404,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9215,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99005,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9245,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99329,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9275,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.96953,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9305,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99355,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9335,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.94182,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9365,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.90802,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9395,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.94118,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9425,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99589,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9455,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99589,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9485,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99563,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9515,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99563,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9545,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99364,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9575,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99364,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9605,
        "r": [
          [
            "TAI T.Y.",
            12
          ],
          [
            "MARIN",
            16
          ]
        ],
        "c": 0.99347,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9635,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            17
          ]
        ],
        "c": 0.9373,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9665,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            17
          ]
        ],
        "c": 0.99309,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9695,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            17
          ]
        ],
        "c": 0.99309,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9725,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            17
          ]
        ],
        "c": 0.99266,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9755,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            17
          ]
        ],
        "c": 0.99272,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9785,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            17
          ]
        ],
        "c": 0.99337,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9815,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            17
          ]
        ],
        "c": 0.99253,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9845,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            17
          ]
        ],
        "c": 0.99466,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9875,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            17
          ]
        ],
        "c": 0.99466,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9905,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.93862,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9935,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.93832,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9965,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.93972,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9995,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.94068,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10025,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.94142,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10055,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.94187,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10085,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.94055,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10115,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.94055,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10246,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.99331,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10276,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.99194,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10306,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.93778,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10336,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.94081,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10366,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.93935,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10396,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.99151,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10426,
        "r": [
          [
            "TAI T.Y.",
            13
          ],
          [
            "MARIN",
            19
          ]
        ],
        "c": 0.99151,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10456,
        "r": [
          [
            "TAI T.Y.",
            16
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.93882,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10486,
        "r": [
          [
            "TAI T.Y.",
            16
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.9385,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10516,
        "r": [
          [
            "TAI T.Y.",
            16
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99401,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10546,
        "r": [
          [
            "TAI T.Y.",
            16
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99401,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10576,
        "r": [
          [
            "TAI T.Y.",
            16
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99389,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10606,
        "r": [
          [
            "TAI T.Y.",
            16
          ],
          [
            "MARIN",
            20
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
        "f": 10636,
        "r": [
          [
            "TAI T.Y.",
            16
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.93768,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10666,
        "r": [
          [
            "TAI T.Y.",
            16
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.93768,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10696,
        "r": [
          [
            "TAI T.Y.",
            16
          ],
          [
            "MARIN",
            20
          ]
        ],
        "c": 0.99433,
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
      "camera_rows": 10725,
      "player_rows": 20196,
      "nonfinite_projected_court_rows": 0,
      "player_projected_court_rows": 19777,
      "projected_court_on_propagated_box": 11948,
      "racket_rows": 6657,
      "shuttle_rows": 10725
    },
    "categories": {
      "player_id": {
        "None": 20196
      },
      "detector_matched": {
        "True": 8038,
        "False": 12158
      }
    },
    "invalid_geometry_frame_count": 531,
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
