# Test 9 evaluation

Status: completed fresh end-to-end inference; unchanged pipeline and predictions. Comparison measures agreement with the supplied legacy rally CSV. Independent physical component accuracy is unavailable without reviewed component labels.

| Input / provenance | Value |
|---|---|
| Drive file | test_9.mp4 (1iwjp0Aph_00mznu-PNxsLKb_Y3B0-e1u) |
| Video SHA256 | `f2aabeb9610c437b38b840ae45885b4b71854702a6b30dd4aee4c54d1417dd4a` |
| Annotation | `/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test9_Full/Test9_Full_rally.csv` |
| Annotation SHA256 | `39dd99a09db0c9e4a669c504cebed0fbad69927e339884127c48bf63da073435` |
| Reference rows | 82 |
| Canonical frames / FPS | 33157 / 30.0 |
| Frozen bindings | [Source, profile, manifest, model lock](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/frozen_pipeline.json) |

| Detection / overlap | Value |
|---|---|
| ground_truth_count | 82 |
| predicted_count | 84 |
| matched_count | 69 |
| true_positives | 69 |
| false_positives | 15 |
| false_negatives | 13 |
| precision | 0.821429 |
| recall | 0.841463 |
| f1 | 0.831325 |
| mean_iou | 0.862791 |
| median_iou | 0.909814 |
| minimum_iou | 0.522222 |
| percent_strictly_exceeding | {'0.5': 100.0, '0.75': 81.15942028985508, '0.9': 56.52173913043478, '0.95': 24.63768115942029} |

Boundary and duration statistics condition on matched intervals; all missed rallies and false detections remain in detection metrics. Signed errors are prediction minus reference. Matching: IoU ≥ 0.5, maximum cardinality then total IoU; zero-origin half-open frame intervals.

| Error | MAE | Median absolute | RMSE | P90 absolute | Maximum absolute | Signed bias |
|---|---|---|---|---|---|---|
| start_frame | 22.869565 | 6.000000 | 55.743980 | 35.400000 | 286.000000 | 3.072464 |
| end_frame | 18.884058 | 9.000000 | 40.080535 | 30.800000 | 184.000000 | -6.275362 |
| start_time_sec | 0.762319 | 0.200000 | 1.858133 | 1.180000 | 9.533333 | 0.102415 |
| end_time_sec | 0.629469 | 0.300000 | 1.336018 | 1.026667 | 6.133333 | -0.209179 |
| duration_sec | 1.250725 | 0.633333 | 2.218735 | 4.180000 | 9.033333 | -0.311594 |

| Boundary tolerance | Within / matched | Within / all reference |
|---|---|---|
| start ±1 frames | 9 / 69 (0.130435) | 9 / 82 (0.109756) |
| start ±3 frames | 15 / 69 (0.217391) | 15 / 82 (0.182927) |
| start ±5 frames | 32 / 69 (0.463768) | 32 / 82 (0.390244) |
| start ±10 frames | 50 / 69 (0.724638) | 50 / 82 (0.609756) |
| start ±15 frames | 54 / 69 (0.782609) | 54 / 82 (0.658537) |
| start ±30 frames | 59 / 69 (0.855072) | 59 / 82 (0.719512) |
| end ±1 frames | 10 / 69 (0.144928) | 10 / 82 (0.121951) |
| end ±3 frames | 16 / 69 (0.231884) | 16 / 82 (0.195122) |
| end ±5 frames | 27 / 69 (0.391304) | 27 / 82 (0.329268) |
| end ±10 frames | 39 / 69 (0.565217) | 39 / 82 (0.475610) |
| end ±15 frames | 48 / 69 (0.695652) | 48 / 82 (0.585366) |
| end ±30 frames | 62 / 69 (0.898551) | 62 / 82 (0.756098) |

Missed rally IDs: [5, 7, 16, 24, 32, 33, 41, 42, 46, 50, 52, 55, 71].

| False detection ID | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| 5 | 1694 | 1923 | 56.466667 | 64.100000 |
| 6 | 1962 | 2279 | 65.400000 | 75.966667 |
| 8 | 2733 | 2887 | 91.100000 | 96.233333 |
| 9 | 3004 | 3161 | 100.133333 | 105.366667 |
| 14 | 4495 | 4618 | 149.833333 | 153.933333 |
| 33 | 13026 | 13225 | 434.200000 | 440.833333 |
| 34 | 13259 | 13468 | 441.966667 | 448.933333 |
| 35 | 13715 | 13770 | 457.166667 | 459.000000 |
| 36 | 13820 | 13910 | 460.666667 | 463.666667 |
| 41 | 15827 | 15959 | 527.566667 | 531.966667 |
| 48 | 18807 | 19094 | 626.900000 | 636.466667 |
| 49 | 19155 | 19487 | 638.500000 | 649.566667 |
| 54 | 20896 | 20968 | 696.533333 | 698.933333 |
| 62 | 24508 | 24587 | 816.933333 | 819.566667 |
| 83 | 32913 | 33023 | 1097.100000 | 1100.766667 |

| Runtime / resources | Value |
|---|---|
| parent_completed_elapsed_s | 3729.349836 |
| worker_elapsed_s | 3718.272271 |
| worker_source_fps | 8.917314 |
| media_ready_time_s | 2.317508 |
| model_staging_time_s | 1.677650 |
| component_initialization_including_models_s | 9.012962 |
| worker_final_cpu_s | 39141.091468 |
| worker_maxrss_bytes | 2807271424 |
| sampled_worker_tree_peak_rss_bytes | 3005173760 |
| sampled_worker_gpu_peak_mib | 2122 |
| sampled_cpu_seconds_max_observed | 39140.930000 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| sample_count | 1801 |
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
      "frames": 33157,
      "raw_shuttle_present": 21018,
      "detector_executed_frames": 13184,
      "person_rows": 63796,
      "scene_telemetry_present": 3641,
      "scene_raw_hypotheses": 46,
      "actual_content_epoch_increments": 46,
      "content_epoch_decreases": 0,
      "detailed_diagnostic_frames": 3600,
      "person_current_detector_matches": 26158,
      "person_propagated_or_unmatched": 37638,
      "pose_present_rows": 49379,
      "pose_current_source_rows": 49379,
      "pose_present_without_current_source": 0,
      "pose_current_on_propagated_box": 23221,
      "racket_present_rows": 23611,
      "racket_current_source_rows": 23611,
      "racket_present_without_current_source": 0,
      "racket_current_on_propagated_box": 0,
      "scene_decision_records": 46,
      "scene_positive_correspondence_vetoes": 0,
      "scene_current_detector_probes": 46
    },
    "categories": {
      "view": {
        "main": 32206,
        "none": 951
      },
      "calibration_state": {
        "REACQUIRING": 24,
        "VALID": 32182,
        "LOST": 951
      },
      "player_population": {
        "0": 1089,
        "2": 31728,
        "1": 340
      },
      "association_status": {
        "missing": 11188,
        "observed": 21018,
        "invalid": 951
      },
      "association_reason": {
        "no_accepted_raw_observation": 11188,
        "fresh_selection_retained": 21018,
        "image_view_invalid": 951
      },
      "scene_raw_status": {
        "unknown": 140,
        "measured": 3455,
        "hypothesis": 46
      },
      "person_detector_match": {
        "True": 26158,
        "False": 37638
      },
      "person_identity_method": {
        "bytetrack_v1": 63796
      },
      "scene_decision": {
        "barrier": 46
      },
      "scene_decision_reason": {
        "raw_change_and_current_layout_discontinuity": 46
      }
    },
    "scene_records": [
      {
        "frame": 949,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 1,
        "raw": {
          "frame": 949,
          "previous_frame": 948,
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
                "frame": 948,
                "key": "track:7",
                "bbox": [
                  518.9902954101562,
                  319.9866027832031,
                  588.3721923828125,
                  485.0115661621094
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 37,
              "consistent_fraction": 0.0,
              "median_patch_error": 26.93246841430664,
              "median_forward_backward_error": 12.641191482543945,
              "discontinuity": 26.93246841430664,
              "previous_mean": 0.0,
              "adaptive_ratio": 26.93246841430664,
              "appearance_previous_mean": 8.045032739639282,
              "appearance_adaptive_ratio": 3.347713960392686
            },
            {
              "region": {
                "frame": 948,
                "key": "track:6",
                "bbox": [
                  519.8656005859375,
                  188.89564514160156,
                  574.6292114257812,
                  321.19970703125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 38,
              "consistent_fraction": 0.39473684210526316,
              "median_patch_error": 20.686756134033203,
              "median_forward_backward_error": 2.8784704208374023,
              "discontinuity": 12.520931344283255,
              "previous_mean": 0.0714848160743714,
              "adaptive_ratio": 12.520931344283255,
              "appearance_previous_mean": 6.390040397644043,
              "appearance_adaptive_ratio": 3.2373435607168064
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.7586450576782227,
          "discontinuity": 19.726699879294948,
          "photometric_gain": 1.008695652173913,
          "photometric_offset": -0.7130434782608717,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 23.809612274169922
        },
        "decision": {
          "frame": 949,
          "previous_frame": 948,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 949,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "7b4bce095b27ba155224fc19f4970857d6ba2867f0b00b583743bda804f79bd6",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              506.5258536376059,
              368.1394153833389,
              590.912821110338,
              546.3000034093857
            ],
            [
              625.9173014238477,
              199.9100472331047,
              675.8496293947101,
              332.3458545804024
            ],
            [
              232.03697319328785,
              298.12390518188477,
              283.9259890243411,
              411.95080947875977
            ],
            [
              622.918519180268,
              128.60481855273247,
              656.8064474053681,
              178.91794064641
            ],
            [
              478.59307329542935,
              128.75260689854622,
              509.0663104187697,
              180.6827127635479
            ],
            [
              769.9235719870776,
              129.63400161266327,
              806.4642172623426,
              178.8892719745636
            ],
            [
              965.0996585525572,
              118.31281584501266,
              1002.1479365192354,
              212.28841465711594
            ],
            [
              1022.8537069559097,
              194.43425059318542,
              1049.0,
              257.24188804626465
            ]
          ],
          "detector_scores": [
            0.9351136755432918,
            0.9013708297432631,
            0.8617843813243412,
            0.5721998185457278,
            0.5691534376801493,
            0.5651057445962391,
            0.4553401557993666,
            0.4358648210318444
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
        "frame": 1268,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 2,
        "raw": {
          "frame": 1268,
          "previous_frame": 1267,
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
                "frame": 1267,
                "key": "track:0",
                "bbox": [
                  554.904541015625,
                  297.6107482910156,
                  614.3351440429688,
                  456.63458251953125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.06451612903225806,
              "median_patch_error": 28.273242950439453,
              "median_forward_backward_error": 16.930950164794922,
              "discontinuity": 26.449162760088523,
              "previous_mean": 0.0,
              "adaptive_ratio": 26.449162760088523,
              "appearance_previous_mean": 3.486022487282753,
              "appearance_adaptive_ratio": 8.110459141781835
            },
            {
              "region": {
                "frame": 1267,
                "key": "track:2",
                "bbox": [
                  536.6669311523438,
                  234.8956756591797,
                  588.4739990234375,
                  354.85394287109375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 29,
              "consistent_fraction": 0.13793103448275862,
              "median_patch_error": 34.19862365722656,
              "median_forward_backward_error": 14.685673713684082,
              "discontinuity": 29.481572118298757,
              "previous_mean": 0.0,
              "adaptive_ratio": 29.481572118298757,
              "appearance_previous_mean": 2.855229601264,
              "appearance_adaptive_ratio": 11.977538913888731
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.1941609382629395,
          "discontinuity": 27.965367439193642,
          "photometric_gain": 1.008695652173913,
          "photometric_offset": -0.7130434782608717,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 31.235933303833008
        },
        "decision": {
          "frame": 1268,
          "previous_frame": 1267,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 1268,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "74d7f63d53ae8daff74133c511bfb0050f094531c7a2b75cefa2528164fc7fa3",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              650.857643827796,
              375.50012040138245,
              723.1013156324625,
              560.3640878200531
            ],
            [
              640.1570727191865,
              204.01201486587524,
              696.6205624975264,
              335.6016821861267
            ],
            [
              297.7665164861828,
              140.50908237695694,
              341.7389866616577,
              245.12198156118393
            ],
            [
              232.09470043703914,
              300.96452009677887,
              284.7584550194442,
              411.63349664211273
            ],
            [
              770.1820099819452,
              129.90881744027138,
              806.2161030303687,
              178.87450048327446
            ],
            [
              478.0881493743509,
              129.31146815419197,
              508.2004139367491,
              179.91047379374504
            ],
            [
              622.9955456517637,
              128.62884029746056,
              656.8384535051882,
              179.53098621964455
            ],
            [
              965.0586785096675,
              118.51055693626404,
              1002.5184978228062,
              213.5334928035736
            ],
            [
              993.4943405427039,
              195.0471355319023,
              1049.0,
              294.92640167474747
            ]
          ],
          "detector_scores": [
            0.9314607717916071,
            0.9221422850138719,
            0.8441517250951293,
            0.8208252040455662,
            0.7672768132354149,
            0.7568612423897307,
            0.7493007271162828,
            0.4839608881817537,
            0.46644268098537506
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
        "frame": 1961,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 3,
        "raw": {
          "frame": 1961,
          "previous_frame": 1960,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 1960,
                "key": "track:2",
                "bbox": [
                  546.6950073242188,
                  304.8218688964844,
                  613.0911254882812,
                  461.2859802246094
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 36,
              "consistent_fraction": 0.08333333333333333,
              "median_patch_error": 25.464143753051758,
              "median_forward_backward_error": 19.663484573364258,
              "discontinuity": 23.342131773630776,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.342131773630776,
              "appearance_previous_mean": 8.549869060516357,
              "appearance_adaptive_ratio": 2.9783080387331555
            },
            {
              "region": {
                "frame": 1960,
                "key": "track:1",
                "bbox": [
                  644.5242309570312,
                  189.12030029296875,
                  678.402587890625,
                  319.9821472167969
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 21,
              "consistent_fraction": 0.5238095238095238,
              "median_patch_error": 28.037769317626953,
              "median_forward_backward_error": 0.8314119577407837,
              "discontinuity": 13.351318722679501,
              "previous_mean": 0.0,
              "adaptive_ratio": 13.351318722679501,
              "appearance_previous_mean": 10.919235229492188,
              "appearance_adaptive_ratio": 2.5677411218231336
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.4212372303009033,
          "discontinuity": 18.34672524815514,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 26.750956535339355
        },
        "decision": {
          "frame": 1961,
          "previous_frame": 1960,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 1961,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "1045a204a84163a522b1913aee35ebf9dd6731b9eb34feb379974bd8293daee9",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              619.0694934949279,
              203.8718956708908,
              671.9188444986939,
              335.00324976444244
            ],
            [
              660.1001416929066,
              362.52216398715973,
              732.677381824702,
              530.1597408056259
            ],
            [
              232.0731550604105,
              298.6850520372391,
              283.3547124043107,
              411.9077686071396
            ],
            [
              993.4652897417545,
              195.52516090869904,
              1049.0,
              293.75483906269073
            ],
            [
              769.8508749827743,
              130.16692957282066,
              806.1474357023835,
              178.82400158047676
            ],
            [
              623.3522359207273,
              128.4191801249981,
              656.5399561449885,
              178.4517517387867
            ],
            [
              477.08417408540845,
              129.38262924551964,
              508.4724246971309,
              179.82374492287636
            ],
            [
              965.406105697155,
              118.41939455270767,
              1002.2802492976189,
              213.13948386907578
            ]
          ],
          "detector_scores": [
            0.908238250136514,
            0.8941802361460006,
            0.8711298733126952,
            0.46921171794366767,
            0.4666838309743922,
            0.4660364879510933,
            0.4222101916015896,
            0.3960525403550212
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
      },
      {
        "frame": 2638,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 4,
        "raw": {
          "frame": 2638,
          "previous_frame": 2637,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 2637,
                "key": "track:0",
                "bbox": [
                  495.96539306640625,
                  366.5898742675781,
                  561.1968994140625,
                  539.6467895507812
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 37,
              "consistent_fraction": 0.0,
              "median_patch_error": 23.912521362304688,
              "median_forward_backward_error": 11.073590278625488,
              "discontinuity": 23.912521362304688,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.912521362304688,
              "appearance_previous_mean": 9.994490623474121,
              "appearance_adaptive_ratio": 2.3925702932915063
            },
            {
              "region": {
                "frame": 2637,
                "key": "track:1",
                "bbox": [
                  559.11962890625,
                  183.39219665527344,
                  594.0902709960938,
                  316.2540588378906
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.64,
              "median_patch_error": 17.11139488220215,
              "median_forward_backward_error": 0.3808985650539398,
              "discontinuity": 6.160102157592773,
              "previous_mean": 0.0,
              "adaptive_ratio": 6.160102157592773,
              "appearance_previous_mean": 9.915957927703857,
              "appearance_adaptive_ratio": 1.7256421423890076
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.3422619104385376,
          "discontinuity": 15.036311759948731,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 20.511958122253418
        },
        "decision": {
          "frame": 2638,
          "previous_frame": 2637,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2638,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b42631292159dc9db5cd80bbee26f18db1cecc8367e508b63f130ec6ee1f39ed",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              675.4241728819907,
              367.32223546504974,
              748.5296536646783,
              547.7486330270767
            ],
            [
              606.2713815122843,
              210.79038763046265,
              653.6677039116621,
              334.1755414009094
            ],
            [
              232.04404643177986,
              299.01075917482376,
              283.5525378584862,
              412.0404297709465
            ],
            [
              964.9408348258585,
              120.10979288816452,
              1002.6743251625448,
              214.31908279657364
            ],
            [
              993.3767996933311,
              227.399870544672,
              1027.05083549954,
              294.25613579154015
            ],
            [
              622.4769774414599,
              128.6791716814041,
              657.0641092918813,
              178.8334904909134
            ],
            [
              770.1182701811194,
              129.97555649280548,
              805.2001330628991,
              178.9606763124466
            ]
          ],
          "detector_scores": [
            0.9215172322102005,
            0.8999646786982872,
            0.8493195682649223,
            0.42049094503926876,
            0.40646250461491995,
            0.3745551918613565,
            0.36306948886318374
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
        "frame": 2918,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 5,
        "raw": {
          "frame": 2918,
          "previous_frame": 2917,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 2917,
                "key": "track:4",
                "bbox": [
                  268.8650207519531,
                  453.0882873535156,
                  350.1380615234375,
                  651.3834228515625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 56,
              "consistent_fraction": 0.4107142857142857,
              "median_patch_error": 25.648632049560547,
              "median_forward_backward_error": 2.9210777282714844,
              "discontinuity": 15.114372457776751,
              "previous_mean": 0.21764728479218062,
              "adaptive_ratio": 15.114372457776751,
              "appearance_previous_mean": 6.257688261568546,
              "appearance_adaptive_ratio": 4.098739179303809
            },
            {
              "region": {
                "frame": 2917,
                "key": "track:3",
                "bbox": [
                  597.4896240234375,
                  184.79632568359375,
                  646.654296875,
                  309.1088562011719
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.5333333333333333,
              "median_patch_error": 23.463966369628906,
              "median_forward_backward_error": 0.6651265621185303,
              "discontinuity": 10.94985097249349,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.94985097249349,
              "appearance_previous_mean": 4.225871808826923,
              "appearance_adaptive_ratio": 5.5524557845360585
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.4412556886672974,
          "discontinuity": 13.03211171513512,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 24.556299209594727
        },
        "decision": {
          "frame": 2918,
          "previous_frame": 2917,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2918,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "42d91b5f3be0590431d557987ffd7c3f909064f2a201cfb1e8aaba09ce596e29",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              614.2724986299872,
              356.76891481876373,
              688.9345971122384,
              533.4310306310654
            ],
            [
              548.3835715949535,
              211.29739606380463,
              610.6257328689098,
              333.2028948068619
            ],
            [
              232.03520792722702,
              302.2923112511635,
              284.3306427896023,
              411.9628662467003
            ],
            [
              477.2235342320055,
              129.5136014521122,
              509.3250223342329,
              179.560565918684
            ],
            [
              770.563652895391,
              130.28426161408424,
              805.5361423268914,
              178.81558892130852
            ],
            [
              622.6886221896857,
              128.70857927203178,
              657.1541911233217,
              178.76903703808784
            ],
            [
              965.0169330108911,
              118.83711314201355,
              1002.870832754299,
              213.20297122001648
            ]
          ],
          "detector_scores": [
            0.9174972718310004,
            0.9092975134560781,
            0.8295615884895888,
            0.525376075296571,
            0.5074153469546656,
            0.49938690693110904,
            0.45000164637936785
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
        "frame": 3533,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 6,
        "raw": {
          "frame": 3533,
          "previous_frame": 3532,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 3532,
                "key": "track:2",
                "bbox": [
                  709.4983520507812,
                  335.4508056640625,
                  799.2628173828125,
                  536.0870361328125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 41,
              "consistent_fraction": 0.0,
              "median_patch_error": 25.702096939086914,
              "median_forward_backward_error": 16.408710479736328,
              "discontinuity": 25.702096939086914,
              "previous_mean": 0.0,
              "adaptive_ratio": 25.702096939086914,
              "appearance_previous_mean": 3.840950921177864,
              "appearance_adaptive_ratio": 6.691597332674358
            },
            {
              "region": {
                "frame": 3532,
                "key": "track:1",
                "bbox": [
                  744.5091552734375,
                  180.7457733154297,
                  791.3997192382812,
                  310.1341247558594
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 24,
              "consistent_fraction": 0.875,
              "median_patch_error": 20.894912719726562,
              "median_forward_backward_error": 0.08174829185009003,
              "discontinuity": 2.6118640899658203,
              "previous_mean": 0.0,
              "adaptive_ratio": 2.6118640899658203,
              "appearance_previous_mean": 4.130031242966652,
              "appearance_adaptive_ratio": 5.059262627930507
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.5099561214447021,
          "discontinuity": 14.156980514526367,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 23.29850482940674
        },
        "decision": {
          "frame": 3533,
          "previous_frame": 3532,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3533,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "7735ed62bfa243b3c570cf0768872c20ffc4347484c02a42084eaa348c6acd46",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              508.1851154714823,
              371.933859705925,
              593.8933602422476,
              554.1640635728836
            ],
            [
              626.6955646201968,
              194.10795599222183,
              677.7230149582028,
              333.44085878133774
            ],
            [
              232.05406279489398,
              299.61065107584,
              283.62264631316066,
              411.9680799841881
            ],
            [
              965.8421309795231,
              118.45253574848175,
              1002.7882639560848,
              212.78485333919525
            ],
            [
              478.3078336920589,
              128.43184730410576,
              509.21816895343363,
              180.1618576347828
            ],
            [
              622.684601644054,
              128.7170378267765,
              657.0430432762951,
              179.39686557650566
            ],
            [
              770.543186461553,
              129.68360555171967,
              806.118766868487,
              178.98443186283112
            ],
            [
              993.6060514487326,
              195.79864805936813,
              1048.5656684599817,
              295.3003037571907
            ],
            [
              1006.9294807408005,
              123.13799220323563,
              1045.5810007359833,
              205.2803437113762
            ]
          ],
          "detector_scores": [
            0.9362796861562139,
            0.8960232067084611,
            0.8415790736132326,
            0.6586277720082628,
            0.6550640142275622,
            0.635296798204198,
            0.6187679481973749,
            0.5103891437909566,
            0.45934706356251287
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
        "frame": 3708,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 7,
        "raw": {
          "frame": 3708,
          "previous_frame": 3707,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 3707,
                "key": "track:0",
                "bbox": [
                  407.5088195800781,
                  387.0173645019531,
                  487.9994812011719,
                  540.9745483398438
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 42,
              "consistent_fraction": 0.07142857142857142,
              "median_patch_error": 25.962974548339844,
              "median_forward_backward_error": 8.72596549987793,
              "discontinuity": 24.10847636631557,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.10847636631557,
              "appearance_previous_mean": 6.698164701461792,
              "appearance_adaptive_ratio": 3.8761325983330543
            },
            {
              "region": {
                "frame": 3707,
                "key": "track:1",
                "bbox": [
                  479.449951171875,
                  205.61447143554688,
                  520.4707641601562,
                  343.4568786621094
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.4,
              "median_patch_error": 20.431264877319336,
              "median_forward_backward_error": 3.0290565490722656,
              "discontinuity": 12.258758926391602,
              "previous_mean": 0.0,
              "adaptive_ratio": 12.258758926391602,
              "appearance_previous_mean": 7.841393947601318,
              "appearance_adaptive_ratio": 2.6055654152625833
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.4722931385040283,
          "discontinuity": 18.183617646353586,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 23.19711971282959
        },
        "decision": {
          "frame": 3708,
          "previous_frame": 3707,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 3708,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "02a3d829fab6105260d6c5e24fd8f217730da5507c2d316598e75ea28a59994a",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              601.7025868520141,
              355.205325961113,
              671.4594857469201,
              533.053053021431
            ],
            [
              677.4407215230167,
              211.68928462266922,
              742.1581327803433,
              332.4301831126213
            ],
            [
              232.04528211802244,
              300.7872897386551,
              284.38637041300535,
              411.96001613140106
            ],
            [
              478.4768335688859,
              128.53526610136032,
              509.2918262016028,
              180.06540578603745
            ],
            [
              771.2344661727548,
              129.8847956955433,
              805.4135598167777,
              178.76387378573418
            ],
            [
              622.4955446925014,
              128.73727318644524,
              657.397183040157,
              179.4567088186741
            ],
            [
              964.9774093125015,
              118.57053327560425,
              1002.2741789128631,
              213.02890765666962
            ]
          ],
          "detector_scores": [
            0.9100459110818133,
            0.8984169078928508,
            0.8327888345411869,
            0.49241529476095913,
            0.4886376157263838,
            0.4696210949360518,
            0.4416596007810036
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
        "frame": 4363,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 8,
        "raw": {
          "frame": 4363,
          "previous_frame": 4362,
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
                "frame": 4362,
                "key": "track:3",
                "bbox": [
                  502.7006530761719,
                  315.3088684082031,
                  554.01513671875,
                  472.226806640625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 30,
              "consistent_fraction": 0.03333333333333333,
              "median_patch_error": 22.389881134033203,
              "median_forward_backward_error": 16.891159057617188,
              "discontinuity": 21.643551762898763,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.643551762898763,
              "appearance_previous_mean": 3.6549037471413612,
              "appearance_adaptive_ratio": 6.125983796849692
            },
            {
              "region": {
                "frame": 4362,
                "key": "track:4",
                "bbox": [
                  498.0058288574219,
                  202.56082153320312,
                  542.9342651367188,
                  340.7644348144531
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 26,
              "consistent_fraction": 0.34615384615384615,
              "median_patch_error": 19.742773056030273,
              "median_forward_backward_error": 3.6417343616485596,
              "discontinuity": 12.908736228942871,
              "previous_mean": 0.0,
              "adaptive_ratio": 12.908736228942871,
              "appearance_previous_mean": 4.745624199509621,
              "appearance_adaptive_ratio": 4.1602057444983425
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.134601593017578,
          "discontinuity": 17.27614399592082,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7130434782608717,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 21.06632709503174
        },
        "decision": {
          "frame": 4363,
          "previous_frame": 4362,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 4363,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "e93debc4dd25487a33cb5502c8ae78eab016a7e85354f25fb085713d513d32ec",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              613.8511265777051,
              362.54491901397705,
              692.7800496555865,
              533.4454326629639
            ],
            [
              545.7621545381844,
              202.56413334608078,
              608.0926704220474,
              331.7720864415169
            ],
            [
              232.0284390449524,
              303.23865509033203,
              284.493089877069,
              411.80486154556274
            ],
            [
              622.8023053240031,
              128.73125398159027,
              658.0298848319799,
              180.69412469863892
            ],
            [
              770.4430760927498,
              129.95522704720497,
              805.7009360007942,
              178.80376622080803
            ],
            [
              478.7688405327499,
              128.97442480921745,
              509.22879250720143,
              180.16173830628395
            ],
            [
              964.9288584087044,
              118.50004225969315,
              1002.0812901165336,
              213.5410242676735
            ],
            [
              1005.898649059236,
              123.25727939605713,
              1040.7324494495988,
              211.8363937139511
            ]
          ],
          "detector_scores": [
            0.9318958433796496,
            0.8849508882165508,
            0.8298411300772397,
            0.5511577176500118,
            0.5076775476439229,
            0.4986029899710467,
            0.4912286459608206,
            0.43518513862826014
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
        "frame": 5691,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 9,
        "raw": {
          "frame": 5691,
          "previous_frame": 5690,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 5690,
                "key": "track:0",
                "bbox": [
                  648.1998291015625,
                  358.3981018066406,
                  723.4671020507812,
                  536.84130859375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 42,
              "consistent_fraction": 0.14285714285714285,
              "median_patch_error": 26.602821350097656,
              "median_forward_backward_error": 9.497990608215332,
              "discontinuity": 22.80241830008371,
              "previous_mean": 0.0,
              "adaptive_ratio": 22.80241830008371,
              "appearance_previous_mean": 10.582235336303711,
              "appearance_adaptive_ratio": 2.5139132238756097
            },
            {
              "region": {
                "frame": 5690,
                "key": "track:2",
                "bbox": [
                  700.8267822265625,
                  170.9122314453125,
                  754.8201293945312,
                  297.03851318359375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 23,
              "consistent_fraction": 0.6086956521739131,
              "median_patch_error": 25.854591369628906,
              "median_forward_backward_error": 0.43471238017082214,
              "discontinuity": 10.117014014202615,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.117014014202615,
              "appearance_previous_mean": 10.737227439880371,
              "appearance_adaptive_ratio": 2.407939248227098
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.4610614776611328,
          "discontinuity": 16.459716157143163,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 26.22870635986328
        },
        "decision": {
          "frame": 5691,
          "previous_frame": 5690,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 5691,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6c5e3d5e62ca05eca098ccfa928037ff14420e2ddc6283eddc47e0b2b6aca38c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              583.313816383481,
              355.9767755270004,
              661.0062923282385,
              535.0907799005508
            ],
            [
              688.3389415591955,
              212.63111692667007,
              752.3062669187784,
              332.1825856566429
            ],
            [
              232.11419140920043,
              302.81452947854996,
              284.32783966884017,
              412.0092391371727
            ],
            [
              477.2017834149301,
              128.5572569668293,
              509.24713909998536,
              180.789107888937
            ],
            [
              623.2743192072958,
              128.87932458519936,
              657.6982156876475,
              179.6779759824276
            ],
            [
              965.2384678144008,
              118.5026353597641,
              1002.7831172924489,
              213.91815280914307
            ],
            [
              771.3124057129025,
              129.93775230646133,
              805.428534142673,
              178.64547008275986
            ],
            [
              993.5349203571677,
              195.66697824001312,
              1048.5614166036248,
              293.8624917268753
            ],
            [
              1009.0171833001077,
              122.69157510995865,
              1045.1618520058692,
              211.45987099409103
            ]
          ],
          "detector_scores": [
            0.9179157947867647,
            0.9016713585249206,
            0.816792937729393,
            0.6078459555503957,
            0.576963459682105,
            0.5610831723926502,
            0.5548702241611624,
            0.5513943365278752,
            0.4533971534358045
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
        "frame": 6128,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 10,
        "raw": {
          "frame": 6128,
          "previous_frame": 6127,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 6127,
                "key": "track:0",
                "bbox": [
                  750.9122924804688,
                  295.8313903808594,
                  806.2303466796875,
                  454.3553466796875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.06451612903225806,
              "median_patch_error": 24.73518943786621,
              "median_forward_backward_error": 19.95641326904297,
              "discontinuity": 23.13937076445549,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.13937076445549,
              "appearance_previous_mean": 8.976757526397705,
              "appearance_adaptive_ratio": 2.75547037614953
            },
            {
              "region": {
                "frame": 6127,
                "key": "track:2",
                "bbox": [
                  674.2705078125,
                  197.6710205078125,
                  722.2437744140625,
                  330.4246520996094
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 27,
              "consistent_fraction": 0.48148148148148145,
              "median_patch_error": 19.50205421447754,
              "median_forward_backward_error": 1.2041230201721191,
              "discontinuity": 10.112176259358726,
              "previous_mean": 0.08770970061973302,
              "adaptive_ratio": 10.112176259358726,
              "appearance_previous_mean": 4.767963409423828,
              "appearance_adaptive_ratio": 4.090227323458888
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.7804704904556274,
          "discontinuity": 16.625773511907106,
          "photometric_gain": 0.9913793103448276,
          "photometric_offset": 0.7068965517241281,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 22.118621826171875
        },
        "decision": {
          "frame": 6128,
          "previous_frame": 6127,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 6128,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "7b8f7679bca5c0882d6481372959590ed9b1bdd7e9db552c9b7f74758676a2dd",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              619.3270397260785,
              362.1209907531738,
              692.9982761070132,
              532.4575395584106
            ],
            [
              557.9699706807733,
              195.03210014104843,
              599.536154948175,
              332.03235107660294
            ],
            [
              232.02536200359464,
              301.7470396757126,
              284.0961393676698,
              411.79425966739655
            ],
            [
              993.3296046964824,
              195.82016390562057,
              1048.727092910558,
              296.1696394085884
            ],
            [
              770.4686131011695,
              129.36732536554337,
              805.8992103803903,
              178.6885568499565
            ],
            [
              478.8234222549945,
              129.1031917333603,
              509.51280098967254,
              180.3531848192215
            ],
            [
              622.4705859608948,
              128.8937587440014,
              657.9945262484252,
              180.0824307501316
            ],
            [
              965.0707979742438,
              114.5004768371582,
              1002.3145121987909,
              213.9762657880783
            ]
          ],
          "detector_scores": [
            0.9273028848165664,
            0.88071629973149,
            0.8353117460085553,
            0.5710291456168617,
            0.5136183188767873,
            0.5133653027105161,
            0.48629103060076506,
            0.40289250366203416
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
        "frame": 7874,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 11,
        "raw": {
          "frame": 7874,
          "previous_frame": 7873,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 7873,
                "key": "track:7",
                "bbox": [
                  483.96142578125,
                  402.3509826660156,
                  551.82080078125,
                  585.26220703125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 44,
              "consistent_fraction": 0.06818181818181818,
              "median_patch_error": 29.17169761657715,
              "median_forward_backward_error": 15.24881649017334,
              "discontinuity": 27.18271823362871,
              "previous_mean": 0.0,
              "adaptive_ratio": 27.18271823362871,
              "appearance_previous_mean": 10.802206993103027,
              "appearance_adaptive_ratio": 2.7005312558075065
            },
            {
              "region": {
                "frame": 7873,
                "key": "track:8",
                "bbox": [
                  395.4036560058594,
                  236.06820678710938,
                  455.5024719238281,
                  376.8558349609375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 34,
              "consistent_fraction": 0.38235294117647056,
              "median_patch_error": 21.625389099121094,
              "median_forward_backward_error": 1.2733876705169678,
              "discontinuity": 13.356857972986559,
              "previous_mean": 0.3262402934412805,
              "adaptive_ratio": 13.356857972986559,
              "appearance_previous_mean": 10.08499813079834,
              "appearance_adaptive_ratio": 2.1443126531753958
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.141439914703369,
          "discontinuity": 20.269788103307633,
          "photometric_gain": 0.9913793103448276,
          "photometric_offset": 0.7068965517241281,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 25.39854335784912
        },
        "decision": {
          "frame": 7874,
          "previous_frame": 7873,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 7874,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "448b5b54ef051fa93dc048d8ebec62b3adb12423ceeec31e2a0a32da52f50903",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              509.1275879777968,
              369.05893325805664,
              577.3305962048471,
              551.3663702011108
            ],
            [
              630.8291603252292,
              201.16549319028854,
              675.3286811187863,
              331.9132612347603
            ],
            [
              232.0,
              299.0023235678673,
              284.39259754121304,
              411.88753324747086
            ],
            [
              966.659555690363,
              115.64603042602539,
              1002.1746848654002,
              211.93713450431824
            ],
            [
              992.773682847619,
              197.16896605491638,
              1049.0,
              294.50391912460327
            ],
            [
              771.141820140183,
              130.02799907326698,
              805.450593881309,
              178.2944630086422
            ],
            [
              622.4363200161606,
              128.5829929113388,
              657.5466919448227,
              178.90251743793488
            ],
            [
              477.78608648106456,
              131.808924138546,
              508.3199117965996,
              181.88127344846725
            ]
          ],
          "detector_scores": [
            0.935410296339864,
            0.886493311469548,
            0.8480966226249533,
            0.5520330674168825,
            0.4784251986432088,
            0.40257433132793347,
            0.37933263455104715,
            0.37848645894881744
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
        "frame": 8124,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 12,
        "raw": {
          "frame": 8124,
          "previous_frame": 8123,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 8123,
                "key": "track:0",
                "bbox": [
                  909.3997192382812,
                  462.3171081542969,
                  1004.8724975585938,
                  637.8080444335938
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 59,
              "consistent_fraction": 0.23728813559322035,
              "median_patch_error": 28.92424964904785,
              "median_forward_backward_error": 10.544485092163086,
              "discontinuity": 22.060868376392428,
              "previous_mean": 0.0,
              "adaptive_ratio": 22.060868376392428,
              "appearance_previous_mean": 9.228121757507324,
              "appearance_adaptive_ratio": 3.1343593430068477
            },
            {
              "region": {
                "frame": 8123,
                "key": "track:1",
                "bbox": [
                  770.4314575195312,
                  179.78016662597656,
                  813.4957885742188,
                  311.28125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 23,
              "consistent_fraction": 0.9565217391304348,
              "median_patch_error": 23.751205444335938,
              "median_forward_backward_error": 0.10512261092662811,
              "discontinuity": 1.032661106275475,
              "previous_mean": 0.0,
              "adaptive_ratio": 1.032661106275475,
              "appearance_previous_mean": 6.302809715270996,
              "appearance_adaptive_ratio": 3.7683519759115445
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.4549319744110107,
          "discontinuity": 11.546764741333952,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 26.337727546691895
        },
        "decision": {
          "frame": 8124,
          "previous_frame": 8123,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 8124,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "1554f8170eb40cfb109b03a749b90e8f4b9d062cdbcd1fbf8bf4cd6d707a6842",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              583.96892792359,
              363.80147564411163,
              662.4592249952257,
              534.2478617429733
            ],
            [
              686.0228698775172,
              197.4625325202942,
              739.6430456116796,
              331.9067211151123
            ],
            [
              232.04534907639027,
              302.1947418451309,
              284.47434762120247,
              412.0139893293381
            ],
            [
              992.8344201743603,
              196.6104765534401,
              1048.5856129229069,
              295.2624582648277
            ],
            [
              966.1861859001219,
              115.75178301334381,
              1003.4319788776338,
              213.74624633789062
            ],
            [
              770.6428007297218,
              129.71923199295998,
              805.913772303611,
              178.27650865912437
            ],
            [
              622.4652505964041,
              129.30552697181702,
              658.0807960182428,
              178.64291369915009
            ]
          ],
          "detector_scores": [
            0.9466488330222657,
            0.8989846678998129,
            0.8391337476281238,
            0.6319116806832004,
            0.42646352609567734,
            0.39563881595665057,
            0.35661425074593994
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
        "frame": 9255,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 13,
        "raw": {
          "frame": 9255,
          "previous_frame": 9254,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 9254,
                "key": "track:4",
                "bbox": [
                  1013.9368896484375,
                  500.7380065917969,
                  1049.0,
                  709.2232055664062
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 34,
              "consistent_fraction": 0.17647058823529413,
              "median_patch_error": 29.21371841430664,
              "median_forward_backward_error": 7.980626106262207,
              "discontinuity": 24.058356341193704,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.058356341193704,
              "appearance_previous_mean": 6.475782986730337,
              "appearance_adaptive_ratio": 4.511225665555669
            },
            {
              "region": {
                "frame": 9254,
                "key": "track:5",
                "bbox": [
                  712.62451171875,
                  204.51145935058594,
                  774.3997802734375,
                  340.26019287109375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 26,
              "consistent_fraction": 0.6153846153846154,
              "median_patch_error": 14.1837797164917,
              "median_forward_backward_error": 0.3584480881690979,
              "discontinuity": 5.455299890958345,
              "previous_mean": 0.0,
              "adaptive_ratio": 5.455299890958345,
              "appearance_previous_mean": 3.2886550053954124,
              "appearance_adaptive_ratio": 4.312942431851805
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.596796989440918,
          "discontinuity": 14.756828116076026,
          "photometric_gain": 0.9913793103448276,
          "photometric_offset": 0.7068965517241281,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 21.69874906539917
        },
        "decision": {
          "frame": 9255,
          "previous_frame": 9254,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 9255,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "5228e560b9f4ff32222237a53f42eb9ba9e9f1ac6643e7fd9cc5921e479b7990",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              579.5619625076652,
              364.83058297634125,
              664.6130778566003,
              538.0568090677261
            ],
            [
              684.1157859936357,
              211.82652616500854,
              744.548111282289,
              331.80020666122437
            ],
            [
              232.04203463718295,
              302.62273186445236,
              285.046309042722,
              412.1692035794258
            ],
            [
              965.2144738920033,
              116.12290841341019,
              1001.9815023653209,
              212.54916578531265
            ],
            [
              770.4314268585294,
              130.3463009595871,
              805.7508610729128,
              178.59943222999573
            ],
            [
              478.6543295495212,
              128.34362682700157,
              508.8330563791096,
              180.57809379696846
            ],
            [
              622.6503174379468,
              129.4345302581787,
              658.0195169374347,
              179.08691668510437
            ],
            [
              993.4682876504958,
              195.24481236934662,
              1048.841731723398,
              296.24028646945953
            ],
            [
              1008.0276908017695,
              123.90107500553131,
              1041.220578994602,
              208.40187168121338
            ]
          ],
          "detector_scores": [
            0.9495675510744441,
            0.8961232088872022,
            0.7975646607366661,
            0.5691102903690616,
            0.5368622453200824,
            0.5336454915038219,
            0.5280842516351784,
            0.4301243228620494,
            0.36667488601193265
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
        "frame": 10034,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 14,
        "raw": {
          "frame": 10034,
          "previous_frame": 10033,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 10033,
                "key": "track:0",
                "bbox": [
                  527.9124145507812,
                  295.9463806152344,
                  602.8107299804688,
                  445.67535400390625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 35,
              "consistent_fraction": 0.08571428571428572,
              "median_patch_error": 27.287803649902344,
              "median_forward_backward_error": 14.433372497558594,
              "discontinuity": 24.948849051339284,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.948849051339284,
              "appearance_previous_mean": 10.150651931762695,
              "appearance_adaptive_ratio": 2.6882808940099006
            },
            {
              "region": {
                "frame": 10033,
                "key": "track:2",
                "bbox": [
                  441.0558166503906,
                  238.3150177001953,
                  479.82867431640625,
                  389.93524169921875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.46153846153846156,
              "median_patch_error": 19.418615341186523,
              "median_forward_backward_error": 2.275951862335205,
              "discontinuity": 10.456177491408127,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.456177491408127,
              "appearance_previous_mean": 8.206065654754639,
              "appearance_adaptive_ratio": 2.3663733825886797
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.675,
          "background_patch_error": 1.7577593326568604,
          "discontinuity": 17.702513271373704,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 23.353209495544434
        },
        "decision": {
          "frame": 10034,
          "previous_frame": 10033,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 10034,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "057caf44de0aba3edf0624c508febbf9a3001f1db09f2a6d2e506251f6a01880",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              633.4816841091961,
              353.7016124725342,
              680.3637571129948,
              527.9973707199097
            ],
            [
              566.4122962672263,
              216.25167208909988,
              615.4838165920228,
              327.84374636411667
            ],
            [
              232.0,
              299.413791179657,
              287.79029643535614,
              411.9477252960205
            ],
            [
              623.7445891294628,
              127.4354268014431,
              659.7885311450809,
              180.4930125772953
            ],
            [
              476.5173030216247,
              128.67681723833084,
              509.39994570426643,
              180.72440201044083
            ],
            [
              1008.1131114177406,
              124.48938745260239,
              1045.5763243027031,
              208.71862000226974
            ],
            [
              967.79766532965,
              121.1494791507721,
              1002.8312542717904,
              210.85314524173737
            ],
            [
              993.004307249561,
              213.70226460695267,
              1033.7124474253505,
              295.03722113370895
            ],
            [
              768.8669415507466,
              129.2818861603737,
              805.7959027495235,
              180.6000892519951
            ],
            [
              999.8700448032469,
              196.77098715305328,
              1048.9361536744982,
              297.47656643390656
            ],
            [
              1025.6526991259307,
              195.9805046916008,
              1048.9776130784303,
              258.1325972676277
            ]
          ],
          "detector_scores": [
            0.8937089906665566,
            0.8489524489521525,
            0.5003324746595551,
            0.4948034965521399,
            0.47838950255288465,
            0.45424222871893843,
            0.4321002472669191,
            0.42575293071785675,
            0.41366033490403514,
            0.3647133660785735,
            0.35464186829341315
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
        "frame": 10568,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 15,
        "raw": {
          "frame": 10568,
          "previous_frame": 10567,
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
                "frame": 10567,
                "key": "track:0",
                "bbox": [
                  435.8642272949219,
                  327.52752685546875,
                  502.90606689453125,
                  505.72320556640625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 34,
              "consistent_fraction": 0.029411764705882353,
              "median_patch_error": 36.461524963378906,
              "median_forward_backward_error": 29.11797332763672,
              "discontinuity": 35.38912717033835,
              "previous_mean": 0.0,
              "adaptive_ratio": 35.38912717033835,
              "appearance_previous_mean": 4.1071605533361435,
              "appearance_adaptive_ratio": 8.877550436581332
            },
            {
              "region": {
                "frame": 10567,
                "key": "track:1",
                "bbox": [
                  461.44415283203125,
                  220.78892517089844,
                  518.5650024414062,
                  353.3563537597656
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 32,
              "consistent_fraction": 0.46875,
              "median_patch_error": 23.575397491455078,
              "median_forward_backward_error": 2.736001491546631,
              "discontinuity": 12.52442991733551,
              "previous_mean": 0.0,
              "adaptive_ratio": 12.52442991733551,
              "appearance_previous_mean": 4.109322194010019,
              "appearance_adaptive_ratio": 5.737052579089543
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.591872215270996,
          "discontinuity": 23.95677854383693,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 30.018461227416992
        },
        "decision": {
          "frame": 10568,
          "previous_frame": 10567,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 10568,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "1f23aadb34ed141cbaf5915ce6d88f20241f7431e23b0d350c72831720478ee8",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              689.257674280554,
              351.6961501836777,
              756.4508529268205,
              533.1779991388321
            ],
            [
              600.3330569192767,
              202.79484122991562,
              658.869827337563,
              333.7384915947914
            ],
            [
              623.983709635213,
              128.74321207404137,
              657.4905990939587,
              178.91940012574196
            ],
            [
              232.0,
              299.39989399909973,
              284.14623944461346,
              411.46730875968933
            ],
            [
              477.1380223091692,
              128.7518060207367,
              509.28913264907897,
              180.60500466823578
            ],
            [
              771.3456672821194,
              129.63644096255302,
              805.0104689206928,
              178.90597108006477
            ],
            [
              968.7089687157422,
              122.11144125461578,
              1001.0667795371264,
              208.08612847328186
            ],
            [
              1009.5719775091857,
              126.09108799695969,
              1042.8245529998094,
              171.5846008658409
            ],
            [
              1007.6937602907419,
              125.6411002278328,
              1044.0938629955053,
              207.15177255868912
            ]
          ],
          "detector_scores": [
            0.9271808014527276,
            0.887646709264675,
            0.6682687071468187,
            0.6263388055240887,
            0.5295346072729371,
            0.5291518378129723,
            0.46030168672787536,
            0.4512268483493899,
            0.3744525400693211
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
        "frame": 10857,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 16,
        "raw": {
          "frame": 10857,
          "previous_frame": 10856,
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
                "frame": 10856,
                "key": "track:0",
                "bbox": [
                  518.0255737304688,
                  369.9788818359375,
                  570.5897827148438,
                  553.1828002929688
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 31,
              "consistent_fraction": 0.0,
              "median_patch_error": 24.663265228271484,
              "median_forward_backward_error": 47.49745559692383,
              "discontinuity": 24.663265228271484,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.663265228271484,
              "appearance_previous_mean": 7.186224460601807,
              "appearance_adaptive_ratio": 3.4320198824134796
            },
            {
              "region": {
                "frame": 10856,
                "key": "track:1",
                "bbox": [
                  590.3770751953125,
                  209.92010498046875,
                  644.0250244140625,
                  344.7463684082031
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.7272727272727273,
              "median_patch_error": 23.122732162475586,
              "median_forward_backward_error": 0.24895578622817993,
              "discontinuity": 6.306199680675159,
              "previous_mean": 0.0,
              "adaptive_ratio": 6.306199680675159,
              "appearance_previous_mean": 6.543225526809692,
              "appearance_adaptive_ratio": 3.533843066807699
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.1198625564575195,
          "discontinuity": 15.484732454473322,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 23.892998695373535
        },
        "decision": {
          "frame": 10857,
          "previous_frame": 10856,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 10857,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "852637fd825501f25878eb7e928c66a07a86cf8bed653cf9c74dc7e1b94a37f0",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              689.6575405225158,
              350.7829658985138,
              767.819686807692,
              531.8861396312714
            ],
            [
              608.8865531794727,
              212.01303201913834,
              658.1474408991635,
              332.105591237545
            ],
            [
              232.0199566371739,
              299.45278865098953,
              284.8427373431623,
              411.67756098508835
            ],
            [
              1009.2220804709941,
              126.39619261026382,
              1042.112271187827,
              193.33849829435349
            ],
            [
              624.2238984312862,
              129.31862097978592,
              657.3613420519978,
              178.5266097187996
            ],
            [
              770.5058465190232,
              129.5312460064888,
              806.0096262507141,
              178.87562721967697
            ],
            [
              993.2779402285814,
              197.01483035087585,
              1048.6137719601393,
              295.0076689720154
            ],
            [
              968.3180672861636,
              122.88022887706757,
              1000.3537200950086,
              206.99436450004578
            ],
            [
              478.0513542294502,
              128.50659283995628,
              508.78436851501465,
              181.03407552838326
            ]
          ],
          "detector_scores": [
            0.9282876054668756,
            0.8799059116784147,
            0.7795086743517187,
            0.6260108718586576,
            0.6177600397997081,
            0.533871668640525,
            0.5262525434687475,
            0.5212016451043898,
            0.49737062493875683
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
        "frame": 11623,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 17,
        "raw": {
          "frame": 11623,
          "previous_frame": 11622,
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
                "frame": 11622,
                "key": "track:2",
                "bbox": [
                  580.069091796875,
                  376.0618896484375,
                  641.5587768554688,
                  557.7713623046875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 39,
              "consistent_fraction": 0.07692307692307693,
              "median_patch_error": 32.975730895996094,
              "median_forward_backward_error": 39.188323974609375,
              "discontinuity": 30.439136211688705,
              "previous_mean": 0.0,
              "adaptive_ratio": 30.439136211688705,
              "appearance_previous_mean": 9.486465454101562,
              "appearance_adaptive_ratio": 3.4760819037968167
            },
            {
              "region": {
                "frame": 11622,
                "key": "track:4",
                "bbox": [
                  451.8457336425781,
                  139.1565399169922,
                  487.6336975097656,
                  256.3465576171875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 18,
              "consistent_fraction": 0.8888888888888888,
              "median_patch_error": 30.686189651489258,
              "median_forward_backward_error": 0.13052502274513245,
              "discontinuity": 3.4095766279432524,
              "previous_mean": 0.0,
              "adaptive_ratio": 3.4095766279432524,
              "appearance_previous_mean": 7.607266902923584,
              "appearance_adaptive_ratio": 4.033799529197024
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.8916170597076416,
          "discontinuity": 16.92435641981598,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 31.830960273742676
        },
        "decision": {
          "frame": 11623,
          "previous_frame": 11622,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 11623,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "5c389d69e6ff37b4eb39ac4a01a9237c9cc08dc168821e622c6c6878cd3c5b63",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              681.7881335578859,
              348.2460970878601,
              761.4447358287871,
              531.2434363365173
            ],
            [
              603.5899088867009,
              212.3906883597374,
              657.179022025317,
              334.1916828751564
            ],
            [
              232.0,
              299.22399002313614,
              285.2024011723697,
              411.8318986296654
            ],
            [
              623.9536346755922,
              128.9161282479763,
              657.3985419906676,
              178.6575383245945
            ],
            [
              993.421021129936,
              196.64570599794388,
              1048.736284468323,
              294.857934653759
            ],
            [
              771.3842824772,
              129.88020384311676,
              805.4954438135028,
              178.765895485878
            ],
            [
              477.03382291458547,
              128.98653894662857,
              509.41938493587077,
              180.59835439920425
            ],
            [
              1009.9817490242422,
              126.35715153813362,
              1043.1648125983775,
              177.93551370501518
            ],
            [
              967.9882805850357,
              122.08204054832458,
              1000.7944385502487,
              207.40622222423553
            ]
          ],
          "detector_scores": [
            0.8980490698244591,
            0.894491335514219,
            0.8605170484915191,
            0.6770810941130952,
            0.6397328716563854,
            0.6122082429316738,
            0.6117760490825761,
            0.5205332129311228,
            0.514665806331917
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
        "frame": 12122,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 18,
        "raw": {
          "frame": 12122,
          "previous_frame": 12121,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 12121,
                "key": "track:0",
                "bbox": [
                  738.1340942382812,
                  379.89483642578125,
                  795.5690307617188,
                  578.0538940429688
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 42,
              "consistent_fraction": 0.0,
              "median_patch_error": 23.10891342163086,
              "median_forward_backward_error": 66.65326690673828,
              "discontinuity": 23.10891342163086,
              "previous_mean": 0.13079244068690712,
              "adaptive_ratio": 23.10891342163086,
              "appearance_previous_mean": 8.37942910194397,
              "appearance_adaptive_ratio": 2.7578147795617425
            },
            {
              "region": {
                "frame": 12121,
                "key": "track:1",
                "bbox": [
                  609.2590942382812,
                  226.88223266601562,
                  651.2826538085938,
                  361.4205322265625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.28,
              "median_patch_error": 32.22434997558594,
              "median_forward_backward_error": 4.448274612426758,
              "discontinuity": 23.201531982421873,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.201531982421873,
              "appearance_previous_mean": 10.966907501220703,
              "appearance_adaptive_ratio": 2.938326047885342
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.4827806949615479,
          "discontinuity": 23.155222702026364,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 27.6666316986084
        },
        "decision": {
          "frame": 12122,
          "previous_frame": 12121,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 12122,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "1f51fa1450a63409d9543b8d31357338e33e85fafb48064c3ae6216affd9b91d",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              502.017972830683,
              349.2628585100174,
              581.4823071919382,
              530.7145632505417
            ],
            [
              624.0498934164643,
              201.64656603336334,
              683.7492315396667,
              333.79812371730804
            ],
            [
              232.0,
              299.1073142886162,
              285.5468624085188,
              411.6411107182503
            ],
            [
              1007.8312699515373,
              126.11621123552322,
              1041.990455655381,
              198.97361224889755
            ],
            [
              623.867214249447,
              129.518489331007,
              657.4981106054038,
              178.91717877984047
            ],
            [
              968.1201246548444,
              122.67430460453033,
              1000.9323758315295,
              209.80664348602295
            ],
            [
              478.39889402873814,
              129.0852603316307,
              509.12569640390575,
              180.55142158269882
            ],
            [
              769.9630135092884,
              129.23361319303513,
              806.7014720644802,
              178.67326444387436
            ],
            [
              1022.7461094241589,
              196.50247049331665,
              1048.952448906377,
              255.71233534812927
            ],
            [
              992.5572034008801,
              195.94674390554428,
              1049.0,
              294.05510169267654
            ]
          ],
          "detector_scores": [
            0.9218836927266452,
            0.8934322304325376,
            0.8560747231638669,
            0.635754507620179,
            0.6236418253351139,
            0.571170238564365,
            0.5674829119672774,
            0.5511257499119906,
            0.3930030935575512,
            0.3924364770095405
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
        "frame": 12932,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 19,
        "raw": {
          "frame": 12932,
          "previous_frame": 12931,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 12931,
                "key": "track:0",
                "bbox": [
                  758.4696655273438,
                  331.4062805175781,
                  815.03662109375,
                  507.9601745605469
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 32,
              "consistent_fraction": 0.0,
              "median_patch_error": 34.40015411376953,
              "median_forward_backward_error": 54.22718811035156,
              "discontinuity": 34.40015411376953,
              "previous_mean": 0.0,
              "adaptive_ratio": 34.40015411376953,
              "appearance_previous_mean": 8.25311803817749,
              "appearance_adaptive_ratio": 4.168140326436674
            },
            {
              "region": {
                "frame": 12931,
                "key": "track:2",
                "bbox": [
                  771.7600708007812,
                  199.7911376953125,
                  839.601806640625,
                  329.7485046386719
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 28,
              "consistent_fraction": 0.5714285714285714,
              "median_patch_error": 21.881874084472656,
              "median_forward_backward_error": 0.2838533818721771,
              "discontinuity": 9.377946036202568,
              "previous_mean": 0.0,
              "adaptive_ratio": 9.377946036202568,
              "appearance_previous_mean": 11.30513048171997,
              "appearance_adaptive_ratio": 1.9355702368809398
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.573377251625061,
          "discontinuity": 21.88905007498605,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 28.141014099121094
        },
        "decision": {
          "frame": 12932,
          "previous_frame": 12931,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 12932,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "d5e77c0c031c0840309b538582b9a14f5befbc1168dbad81d4718d8fd733bba2",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              594.0341006442904,
              355.4583023786545,
              656.691123791039,
              532.9199925661087
            ],
            [
              674.002482380718,
              219.2207349538803,
              735.9802737571299,
              326.4260641336441
            ],
            [
              232.03480008989573,
              303.1030979156494,
              285.59915689378977,
              411.49504804611206
            ],
            [
              1007.0476013887674,
              125.81816077232361,
              1042.1983309518546,
              206.80479741096497
            ],
            [
              623.8506131395698,
              129.79309862852097,
              657.5797709003091,
              179.3355651497841
            ],
            [
              478.59215261787176,
              129.03082817792892,
              508.91213116794825,
              180.31702369451523
            ],
            [
              770.8241772521287,
              129.56840535998344,
              806.0530167948455,
              178.99344804883003
            ],
            [
              968.629463262856,
              121.16879659891129,
              1001.375745229423,
              206.8868173956871
            ],
            [
              992.9400926530361,
              201.0686856508255,
              1048.6311933100224,
              295.0831855535507
            ]
          ],
          "detector_scores": [
            0.9166205093376356,
            0.8990685998414777,
            0.7707910578483701,
            0.6770185368843435,
            0.6301437557975099,
            0.6191924810540216,
            0.6001599820354767,
            0.5674954349687695,
            0.5183943904995488
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
        "frame": 13520,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 20,
        "raw": {
          "frame": 13520,
          "previous_frame": 13519,
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
                "frame": 13519,
                "key": "track:0",
                "bbox": [
                  577.07080078125,
                  349.527099609375,
                  635.4668579101562,
                  527.5015869140625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 38,
              "consistent_fraction": 0.0,
              "median_patch_error": 29.323484420776367,
              "median_forward_backward_error": 72.0381088256836,
              "discontinuity": 29.323484420776367,
              "previous_mean": 0.0,
              "adaptive_ratio": 29.323484420776367,
              "appearance_previous_mean": 8.46481704711914,
              "appearance_adaptive_ratio": 3.464160448778527
            },
            {
              "region": {
                "frame": 13519,
                "key": "track:2",
                "bbox": [
                  467.282958984375,
                  211.30905151367188,
                  535.1358032226562,
                  345.89642333984375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 32,
              "consistent_fraction": 0.28125,
              "median_patch_error": 22.803607940673828,
              "median_forward_backward_error": 4.52517032623291,
              "discontinuity": 16.390093207359314,
              "previous_mean": 0.0,
              "adaptive_ratio": 16.390093207359314,
              "appearance_previous_mean": 6.539505243301392,
              "appearance_adaptive_ratio": 3.4870540036698094
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 4.670245170593262,
          "discontinuity": 22.85678881406784,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 26.063546180725098
        },
        "decision": {
          "frame": 13520,
          "previous_frame": 13519,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 13520,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "3ae7cd589a7457b553edeba5ce33f114c3d0dcd3a2aed5077571c4c49fce1c8a",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              691.696380212903,
              355.5374171733856,
              750.7040627449751,
              530.8228676319122
            ],
            [
              601.8314451873302,
              206.38603699207306,
              657.2422459423542,
              330.7734216451645
            ],
            [
              232.04085982218385,
              298.940915286541,
              285.05746065452695,
              411.6320050358772
            ],
            [
              623.4532182700932,
              129.42463746666908,
              657.5163948051631,
              178.6540089547634
            ],
            [
              771.1301724277437,
              129.6400850713253,
              806.0855631269515,
              178.99556842446327
            ],
            [
              478.2951389942318,
              128.86303624510765,
              509.1448647584766,
              180.36927810311317
            ],
            [
              992.9980846866965,
              197.78656446933746,
              1048.7061440721154,
              294.6934403181076
            ],
            [
              966.9823802430183,
              121.90540224313736,
              1003.1991113703698,
              209.87717121839523
            ],
            [
              1008.1608025152236,
              125.87277191877365,
              1044.3364333789796,
              210.54314357042313
            ],
            [
              1009.3847086504102,
              125.66279736161232,
              1042.0407063886523,
              176.63259336352348
            ]
          ],
          "detector_scores": [
            0.9256798101265568,
            0.9013755774915222,
            0.8823560150417392,
            0.6676685416059182,
            0.6338350017316318,
            0.6092788843793789,
            0.5805621140833467,
            0.49871933740291424,
            0.44351933208345445,
            0.3746389748111916
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
        "frame": 13963,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 21,
        "raw": {
          "frame": 13963,
          "previous_frame": 13962,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 13962,
                "key": "track:3",
                "bbox": [
                  589.1167602539062,
                  288.3623962402344,
                  642.2804565429688,
                  448.47662353515625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.2727272727272727,
              "median_patch_error": 28.750566482543945,
              "median_forward_backward_error": 3.103971242904663,
              "discontinuity": 20.909502896395598,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.909502896395598,
              "appearance_previous_mean": 3.6067355275154114,
              "appearance_adaptive_ratio": 7.971354224120081
            },
            {
              "region": {
                "frame": 13962,
                "key": "track:4",
                "bbox": [
                  623.2603759765625,
                  183.85450744628906,
                  662.313720703125,
                  294.9651794433594
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 19,
              "consistent_fraction": 0.7368421052631579,
              "median_patch_error": 27.9907169342041,
              "median_forward_backward_error": 0.534101128578186,
              "discontinuity": 7.365978140580028,
              "previous_mean": 0.0,
              "adaptive_ratio": 7.365978140580028,
              "appearance_previous_mean": 6.370500355958939,
              "appearance_adaptive_ratio": 4.393801957490153
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 2.2616920471191406,
          "discontinuity": 14.137740518487814,
          "photometric_gain": 1.0087719298245614,
          "photometric_offset": -0.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 28.370641708374023
        },
        "decision": {
          "frame": 13963,
          "previous_frame": 13962,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 13963,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "f578024f7194986d7b8c603dbd725d4aa74d02e579d3be903c0b3b500c820575",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              555.3200597949326,
              218.39568853378296,
              613.1120157651603,
              327.24512577056885
            ],
            [
              614.2538233324885,
              353.6815193891525,
              684.3098191693425,
              530.6073695421219
            ],
            [
              232.0778086669743,
              302.91557317972183,
              284.90509993210435,
              411.6154550909996
            ],
            [
              966.9288850724697,
              121.58819037675858,
              1001.608401209116,
              209.29130500555038
            ],
            [
              623.5037535764277,
              129.71527579426765,
              657.442825820297,
              178.86808428168297
            ],
            [
              770.6497857049108,
              130.48980495333672,
              806.5471528097987,
              178.96044912934303
            ],
            [
              1008.8436911255121,
              125.45148035883904,
              1041.9638564437628,
              180.13809290528297
            ],
            [
              476.47290201485157,
              128.10040092468262,
              509.7289806455374,
              181.356094956398
            ],
            [
              1005.4501710422337,
              125.4927014708519,
              1043.5285121910274,
              213.7313807606697
            ],
            [
              1022.4669462926686,
              195.8306900560856,
              1048.890246104449,
              259.165865033865
            ]
          ],
          "detector_scores": [
            0.876985486505331,
            0.8732093892513286,
            0.8052993295626969,
            0.5887629471830956,
            0.5695819304243477,
            0.47188176220096456,
            0.4634148439113902,
            0.4183267324070655,
            0.36737937827295375,
            0.3639355955263622
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
        "frame": 14763,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 22,
        "raw": {
          "frame": 14763,
          "previous_frame": 14762,
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
                "frame": 14762,
                "key": "track:1",
                "bbox": [
                  733.3621826171875,
                  313.8852233886719,
                  791.2164306640625,
                  474.83453369140625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 30,
              "consistent_fraction": 0.0,
              "median_patch_error": 40.29230499267578,
              "median_forward_backward_error": 56.6151123046875,
              "discontinuity": 40.29230499267578,
              "previous_mean": 0.12555491223054777,
              "adaptive_ratio": 40.29230499267578,
              "appearance_previous_mean": 8.36692190170288,
              "appearance_adaptive_ratio": 4.815666438152754
            },
            {
              "region": {
                "frame": 14762,
                "key": "track:2",
                "bbox": [
                  709.38671875,
                  199.2215118408203,
                  779.8305053710938,
                  323.15185546875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 38,
              "consistent_fraction": 0.6052631578947368,
              "median_patch_error": 27.504852294921875,
              "median_forward_backward_error": 0.6881716847419739,
              "discontinuity": 10.857178537469162,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.857178537469162,
              "appearance_previous_mean": 4.415957927703857,
              "appearance_adaptive_ratio": 6.22851321167895
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.6161068677902222,
          "discontinuity": 25.57474176507247,
          "photometric_gain": 1.0087719298245614,
          "photometric_offset": -0.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 33.89857864379883
        },
        "decision": {
          "frame": 14763,
          "previous_frame": 14762,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 14763,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "ab2d925d12daca67f5d3e07147b92f748a8d7b3d9a55e85b46ded81744908da4",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              593.8977003619075,
              355.4956246614456,
              657.0174910500646,
              534.1078251600266
            ],
            [
              676.1806624345481,
              218.1371449828148,
              736.4884147234261,
              324.6320381760597
            ],
            [
              232.03724407032132,
              303.0824770331383,
              285.38530099764466,
              411.6512995362282
            ],
            [
              1007.5060775075108,
              125.67754131555557,
              1041.7016763892025,
              202.16482347249985
            ],
            [
              623.8673557750881,
              129.63282898068428,
              657.286624122411,
              178.87608847022057
            ],
            [
              967.4058158304542,
              121.98901480436325,
              999.7737008426338,
              209.5832651257515
            ],
            [
              772.0470029227436,
              130.50803697109222,
              805.9041546471417,
              178.3936823606491
            ],
            [
              477.4148586373776,
              129.7446053624153,
              509.21925854869187,
              180.04320150613785
            ],
            [
              992.7253876030445,
              195.3802502155304,
              1048.458757251501,
              296.3207046985626
            ]
          ],
          "detector_scores": [
            0.9185882869278748,
            0.8923883198837654,
            0.7801992806152412,
            0.6823903223177239,
            0.6545035311908389,
            0.5958695887706905,
            0.5739360027300163,
            0.5575668930654497,
            0.5213501489196952
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
        "frame": 15121,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 23,
        "raw": {
          "frame": 15121,
          "previous_frame": 15120,
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
                "frame": 15120,
                "key": "track:2",
                "bbox": [
                  607.6216430664062,
                  394.9516296386719,
                  669.162109375,
                  589.2378540039062
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 42,
              "consistent_fraction": 0.0,
              "median_patch_error": 33.780967712402344,
              "median_forward_backward_error": 66.80207824707031,
              "discontinuity": 33.780967712402344,
              "previous_mean": 0.0,
              "adaptive_ratio": 33.780967712402344,
              "appearance_previous_mean": 3.3730334043502808,
              "appearance_adaptive_ratio": 10.015011315581468
            },
            {
              "region": {
                "frame": 15120,
                "key": "track:1",
                "bbox": [
                  765.135986328125,
                  145.41397094726562,
                  805.9376831054688,
                  258.9137268066406
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 20,
              "consistent_fraction": 0.65,
              "median_patch_error": 27.03677749633789,
              "median_forward_backward_error": 0.3302950859069824,
              "discontinuity": 9.462872123718261,
              "previous_mean": 0.0,
              "adaptive_ratio": 9.462872123718261,
              "appearance_previous_mean": 3.142361044883728,
              "appearance_adaptive_ratio": 8.603969152544751
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9,
          "background_patch_error": 2.342616081237793,
          "discontinuity": 21.621919918060303,
          "photometric_gain": 1.0087719298245614,
          "photometric_offset": -0.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 30.408872604370117
        },
        "decision": {
          "frame": 15121,
          "previous_frame": 15120,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 15121,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "121aa686cabeb3d0b2fd3ccadcc2d2fba548cd1434de9b79a3f06ebae2847550",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              501.67378551512957,
              352.18517673015594,
              585.5735821649432,
              533.8796139955521
            ],
            [
              626.4548690710217,
              219.1302518248558,
              674.831130227074,
              333.61339861154556
            ],
            [
              232.0,
              299.85928577184677,
              284.97497403249145,
              411.27561670541763
            ],
            [
              477.02558551356196,
              129.0370309650898,
              509.1062708683312,
              180.46063324809074
            ],
            [
              623.5532297231257,
              129.7418424487114,
              657.2885537408292,
              178.61527079343796
            ],
            [
              771.878868939355,
              129.97071680426598,
              806.1334520559758,
              178.59999445080757
            ],
            [
              967.1665035802871,
              120.94719898700714,
              1000.9037785213441,
              205.25755655765533
            ],
            [
              1006.2990844473243,
              124.13516539335251,
              1042.0636791959405,
              210.46250504255295
            ],
            [
              993.0937742814422,
              196.11026066541672,
              1048.9987643137574,
              295.38478833436966
            ]
          ],
          "detector_scores": [
            0.9234595282597844,
            0.8913713075884552,
            0.8712720382802793,
            0.6252690787201518,
            0.6082517726290962,
            0.5968160916415478,
            0.5089644123388217,
            0.4838084588029041,
            0.46400656470966334
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
        "frame": 15456,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 24,
        "raw": {
          "frame": 15456,
          "previous_frame": 15455,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 15455,
                "key": "track:0",
                "bbox": [
                  541.4887084960938,
                  327.7205505371094,
                  589.7481689453125,
                  499.1063232421875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 32,
              "consistent_fraction": 0.0,
              "median_patch_error": 35.81526184082031,
              "median_forward_backward_error": 38.846275329589844,
              "discontinuity": 35.81526184082031,
              "previous_mean": 0.0,
              "adaptive_ratio": 35.81526184082031,
              "appearance_previous_mean": 7.377586364746094,
              "appearance_adaptive_ratio": 4.854604212017643
            },
            {
              "region": {
                "frame": 15455,
                "key": "track:2",
                "bbox": [
                  858.4385375976562,
                  221.64334106445312,
                  919.7583618164062,
                  349.4940490722656
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.64,
              "median_patch_error": 18.941326141357422,
              "median_forward_backward_error": 0.44549891352653503,
              "discontinuity": 6.818877410888672,
              "previous_mean": 0.0,
              "adaptive_ratio": 6.818877410888672,
              "appearance_previous_mean": 8.685693264007568,
              "appearance_adaptive_ratio": 2.1807500639986817
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.4055414199829102,
          "discontinuity": 21.317069625854494,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 27.378293991088867
        },
        "decision": {
          "frame": 15456,
          "previous_frame": 15455,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 15456,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6eff49130ce698ff8d67591c252f6f24cb36136a5fd68152b51e12e5ea29e611",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              684.9544912911952,
              350.36630749702454,
              764.4426384828985,
              532.6190736293793
            ],
            [
              602.6960877217352,
              210.75003165006638,
              658.8924623094499,
              331.055931866169
            ],
            [
              232.0,
              301.02521699666977,
              285.20196898654103,
              411.54977852106094
            ],
            [
              992.8126373998821,
              195.71924871206284,
              1048.727092910558,
              295.019294321537
            ],
            [
              623.0166862346232,
              129.71714144945145,
              657.2868493460119,
              177.8124102950096
            ],
            [
              769.799852706492,
              129.38632613420486,
              806.2602057680488,
              178.65893584489822
            ],
            [
              1007.7075461056083,
              125.0821288228035,
              1041.3999893758446,
              173.53124338388443
            ],
            [
              477.5871973019093,
              131.4533642232418,
              508.3055568356067,
              180.52471724152565
            ],
            [
              968.231359243393,
              121.83877563476562,
              1000.9598302841187,
              209.93123161792755
            ],
            [
              1003.7860425524414,
              124.38357520103455,
              1042.56280817464,
              213.94573605060577
            ]
          ],
          "detector_scores": [
            0.9067160582254413,
            0.9028856920238979,
            0.8568899107990008,
            0.6717600875280115,
            0.5671195904128908,
            0.5074575377083681,
            0.4455920847807082,
            0.41526919704211324,
            0.4049328460064775,
            0.36635487046895926
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
        "frame": 15978,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 25,
        "raw": {
          "frame": 15978,
          "previous_frame": 15977,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 15977,
                "key": "track:0",
                "bbox": [
                  609.719482421875,
                  360.06396484375,
                  695.3637084960938,
                  531.323974609375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 41,
              "consistent_fraction": 0.0975609756097561,
              "median_patch_error": 33.44820022583008,
              "median_forward_backward_error": 56.46571731567383,
              "discontinuity": 30.184961179407633,
              "previous_mean": 0.0,
              "adaptive_ratio": 30.184961179407633,
              "appearance_previous_mean": 9.796839237213135,
              "appearance_adaptive_ratio": 3.4141828212080516
            },
            {
              "region": {
                "frame": 15977,
                "key": "track:3",
                "bbox": [
                  806.4207153320312,
                  221.7346954345703,
                  851.6171264648438,
                  354.2827453613281
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 27,
              "consistent_fraction": 0.8148148148148148,
              "median_patch_error": 16.922760009765625,
              "median_forward_backward_error": 0.12134191393852234,
              "discontinuity": 3.1338444462528945,
              "previous_mean": 0.0,
              "adaptive_ratio": 3.1338444462528945,
              "appearance_previous_mean": 13.227819919586182,
              "appearance_adaptive_ratio": 1.2793309942712794
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.4153202772140503,
          "discontinuity": 16.659402812830265,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 25.18548011779785
        },
        "decision": {
          "frame": 15978,
          "previous_frame": 15977,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 15978,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "7b926dc0fa23859030a31edfa8918719f0ee451d6ce5054c3c592f493ed34971",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              508.01200982928276,
              351.40658581256866,
              588.182894974947,
              532.9934805631638
            ],
            [
              623.9909700527787,
              199.46161532402039,
              686.038185082376,
              332.75360465049744
            ],
            [
              232.00796195864677,
              299.47981655597687,
              284.20560716837645,
              411.6948131322861
            ],
            [
              967.072714690119,
              121.03263819217682,
              1000.646364685148,
              208.61629581451416
            ],
            [
              1004.7915228828788,
              124.44435012340546,
              1042.1514311805367,
              212.99924075603485
            ],
            [
              623.4693095833063,
              128.60500672459602,
              657.1841139048338,
              179.45807191729546
            ],
            [
              770.1493434291333,
              129.74191817641258,
              806.6223729271442,
              178.62178567051888
            ],
            [
              477.12559848837554,
              129.82092970609665,
              509.31061411090195,
              180.34902209043503
            ],
            [
              992.8442447930574,
              196.12961024045944,
              1049.0,
              296.00535160303116
            ],
            [
              1019.8952686507255,
              195.7346374988556,
              1049.0,
              258.59980964660645
            ]
          ],
          "detector_scores": [
            0.9223563942196178,
            0.9005323915874337,
            0.8100192452971958,
            0.5177211413566992,
            0.5069053550608169,
            0.4994677307232193,
            0.4772368774894642,
            0.4511147976686771,
            0.45090133654897124,
            0.35181946906552075
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
        "frame": 18063,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 26,
        "raw": {
          "frame": 18063,
          "previous_frame": 18062,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 18062,
                "key": "track:4",
                "bbox": [
                  489.4532775878906,
                  341.3471374511719,
                  550.552490234375,
                  513.63330078125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 40,
              "consistent_fraction": 0.575,
              "median_patch_error": 23.54574203491211,
              "median_forward_backward_error": 0.8351969718933105,
              "discontinuity": 10.006940364837648,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.006940364837648,
              "appearance_previous_mean": 7.923540353775024,
              "appearance_adaptive_ratio": 2.9716188703063997
            },
            {
              "region": {
                "frame": 18062,
                "key": "track:3",
                "bbox": [
                  560.2862548828125,
                  216.08827209472656,
                  615.2137451171875,
                  342.86688232421875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 25,
              "consistent_fraction": 0.08,
              "median_patch_error": 23.18083953857422,
              "median_forward_backward_error": 5.479190826416016,
              "discontinuity": 21.326372375488283,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.326372375488283,
              "appearance_previous_mean": 9.38784408569336,
              "appearance_adaptive_ratio": 2.4692399369841205
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.5513392686843872,
          "discontinuity": 15.666656370162965,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7130434782608717,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 23.363290786743164
        },
        "decision": {
          "frame": 18063,
          "previous_frame": 18062,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 18063,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6c7740d1fcfba1b50f709cbeb238939f5fe6c24f3761c810671cea564192a1fd",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              505.15334405750036,
              353.47964310646057,
              586.6994445100427,
              533.6340634822845
            ],
            [
              620.5582671500742,
              215.03775244951248,
              673.840905752033,
              331.798035800457
            ],
            [
              232.0,
              299.3934043645859,
              285.0010208375752,
              411.7491718530655
            ],
            [
              622.9059066586196,
              129.930695861578,
              657.6777340359986,
              179.10445109009743
            ],
            [
              771.2913260012865,
              129.8453323841095,
              805.9908322542906,
              178.53873991966248
            ],
            [
              478.5395416021347,
              128.96918123960495,
              509.0153383612633,
              180.91560298204422
            ],
            [
              966.8239217437804,
              122.38677340745926,
              1002.3025981746614,
              203.68758362531662
            ],
            [
              1003.120085278526,
              125.92145335674286,
              1044.2906521167606,
              207.77859139442444
            ],
            [
              1008.9807533826679,
              125.9527633190155,
              1042.6497733984143,
              171.82474946975708
            ],
            [
              1023.5392837924883,
              196.07214668393135,
              1049.0,
              257.81301948428154
            ]
          ],
          "detector_scores": [
            0.9130393772124135,
            0.9072897225527531,
            0.8769886244401875,
            0.646227504543395,
            0.636319898907908,
            0.6121245807002923,
            0.46435749482252014,
            0.4075478762651902,
            0.4041754240981679,
            0.39595365716201697
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
        "frame": 18753,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 27,
        "raw": {
          "frame": 18753,
          "previous_frame": 18752,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 18752,
                "key": "track:0",
                "bbox": [
                  662.5540161132812,
                  376.5465087890625,
                  726.106201171875,
                  554.8356323242188
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 37,
              "consistent_fraction": 0.21621621621621623,
              "median_patch_error": 25.31391716003418,
              "median_forward_backward_error": 3.4381473064422607,
              "discontinuity": 19.840637774080843,
              "previous_mean": 0.13556580210841004,
              "adaptive_ratio": 19.840637774080843,
              "appearance_previous_mean": 11.649535655975342,
              "appearance_adaptive_ratio": 2.172955035083311
            },
            {
              "region": {
                "frame": 18752,
                "key": "track:1",
                "bbox": [
                  347.60272216796875,
                  244.70266723632812,
                  396.4186096191406,
                  403.0609130859375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.3939393939393939,
              "median_patch_error": 19.650936126708984,
              "median_forward_backward_error": 3.6626598834991455,
              "discontinuity": 11.909658258611506,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.909658258611506,
              "appearance_previous_mean": 6.481363534927368,
              "appearance_adaptive_ratio": 3.0319138898492906
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 1.7846159934997559,
          "discontinuity": 15.875148016346174,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 22.482426643371582
        },
        "decision": {
          "frame": 18753,
          "previous_frame": 18752,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 18753,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "e2e882d648405d60650ef6c4b3202501325ab78070cdc21ff8884623d9d79c7b",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              680.8817242197692,
              350.70327281951904,
              762.4095815606415,
              532.9529914855957
            ],
            [
              608.4110300689936,
              209.68795293569565,
              660.1919811815023,
              331.4375076889992
            ],
            [
              232.0,
              298.58047437667847,
              284.8670097514987,
              411.68186140060425
            ],
            [
              477.757977662608,
              129.10055503249168,
              508.8570989985019,
              180.5618100464344
            ],
            [
              771.2652700655162,
              130.0331003665924,
              805.3430191762745,
              178.75236546993256
            ],
            [
              623.4483713973314,
              129.90473732352257,
              657.7198280226439,
              178.59144869446754
            ],
            [
              992.8474344462156,
              195.47032487392426,
              1048.4144308120012,
              297.2927271127701
            ],
            [
              1008.4067923408002,
              125.52624195814133,
              1041.7056543249637,
              178.02113419771194
            ],
            [
              966.7226015590131,
              122.14523416757584,
              1002.037229988724,
              206.3378512263298
            ],
            [
              319.39903029985726,
              122.60759997367859,
              347.51176582090557,
              179.36115193367004
            ]
          ],
          "detector_scores": [
            0.9208544789940989,
            0.9023122603664203,
            0.869684102760841,
            0.7105701526592997,
            0.6893782201980869,
            0.6804885063567289,
            0.556122278179122,
            0.5409546588151711,
            0.47664031475541774,
            0.3541096372889537
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
        "frame": 19532,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 28,
        "raw": {
          "frame": 19532,
          "previous_frame": 19531,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 19531,
                "key": "track:0",
                "bbox": [
                  944.1815795898438,
                  335.0559387207031,
                  1005.217529296875,
                  500.54949951171875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 41,
              "consistent_fraction": 0.7073170731707317,
              "median_patch_error": 27.251628875732422,
              "median_forward_backward_error": 0.3129560053348541,
              "discontinuity": 7.976086500214368,
              "previous_mean": 0.0,
              "adaptive_ratio": 7.976086500214368,
              "appearance_previous_mean": 6.1224667355418205,
              "appearance_adaptive_ratio": 4.451086474269056
            },
            {
              "region": {
                "frame": 19531,
                "key": "track:1",
                "bbox": [
                  760.0198974609375,
                  265.0968017578125,
                  810.6410522460938,
                  401.13983154296875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.2692307692307692,
              "median_patch_error": 20.596370697021484,
              "median_forward_backward_error": 13.535208702087402,
              "discontinuity": 15.051193970900316,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.051193970900316,
              "appearance_previous_mean": 5.150722846388817,
              "appearance_adaptive_ratio": 3.9987340245770833
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.5958404541015625,
          "discontinuity": 11.513640235557343,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 23.923999786376953
        },
        "decision": {
          "frame": 19532,
          "previous_frame": 19531,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 19532,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "4dc9159b73176b941df54748572a4c6003aebe32c9d5f75029d78b07a97516f7",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              505.9731244854629,
              352.0426985025406,
              587.0877391286194,
              534.1392911672592
            ],
            [
              613.548629976809,
              213.25088161230087,
              671.8237757906318,
              332.21428114175797
            ],
            [
              232.0,
              299.18473094701767,
              285.17740439623594,
              411.4510479569435
            ],
            [
              623.160874992609,
              129.71020433306694,
              657.5821996629238,
              179.54560855031013
            ],
            [
              478.62447829172015,
              128.88317063450813,
              509.1541643626988,
              180.81038507819176
            ],
            [
              769.9636587444693,
              129.39394479990005,
              806.5134407933801,
              178.86684280633926
            ],
            [
              967.3033695276827,
              122.32756352424622,
              1002.0019657555968,
              210.22179651260376
            ],
            [
              992.3919805847108,
              195.89675903320312,
              1048.8820589222014,
              298.0084686279297
            ],
            [
              1004.8931017704308,
              123.66034811735153,
              1043.4437550716102,
              213.14357775449753
            ],
            [
              1008.9003302957863,
              124.07506284117699,
              1041.651071080938,
              173.64355674386024
            ],
            [
              1022.7846013549715,
              195.9324772655964,
              1048.9702507015318,
              260.0193299949169
            ]
          ],
          "detector_scores": [
            0.9129925706837777,
            0.8909341248421585,
            0.883379258977205,
            0.6156643535197982,
            0.586738963882419,
            0.5292433159583874,
            0.49714675662620433,
            0.46952750585450814,
            0.4647575673482143,
            0.3876854057729961,
            0.3614766801667516
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
        "frame": 19721,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 29,
        "raw": {
          "frame": 19721,
          "previous_frame": 19720,
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
                "frame": 19720,
                "key": "track:0",
                "bbox": [
                  796.4705810546875,
                  374.0206604003906,
                  848.4615478515625,
                  559.864990234375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.0,
              "median_patch_error": 40.857852935791016,
              "median_forward_backward_error": 67.92015075683594,
              "discontinuity": 40.857852935791016,
              "previous_mean": 0.0,
              "adaptive_ratio": 40.857852935791016,
              "appearance_previous_mean": 4.193859923630953,
              "appearance_adaptive_ratio": 9.742302718689082
            },
            {
              "region": {
                "frame": 19720,
                "key": "track:1",
                "bbox": [
                  688.0435180664062,
                  195.1092529296875,
                  733.9503784179688,
                  327.61627197265625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 24,
              "consistent_fraction": 0.5833333333333334,
              "median_patch_error": 21.107851028442383,
              "median_forward_backward_error": 0.27615296840667725,
              "discontinuity": 8.794937928517658,
              "previous_mean": 0.0,
              "adaptive_ratio": 8.794937928517658,
              "appearance_previous_mean": 5.689608193933964,
              "appearance_adaptive_ratio": 3.709895358163106
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.4803004264831543,
          "discontinuity": 24.826395432154335,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 30.9828519821167
        },
        "decision": {
          "frame": 19721,
          "previous_frame": 19720,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 19721,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "824fb120de6526e2ee5f696c2fc232cf7c7372027f0d4345cacec50e7cea14e7",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              685.1905012764037,
              351.80595993995667,
              763.7081660591066,
              533.4761092662811
            ],
            [
              606.221427526325,
              212.5299768447876,
              657.6914787627757,
              332.6655035018921
            ],
            [
              232.02331064268947,
              300.8997201323509,
              285.236878644675,
              411.70178467035294
            ],
            [
              769.9753536321223,
              129.74962404370308,
              806.4086372517049,
              178.95347759127617
            ],
            [
              623.2634628210217,
              130.0985015630722,
              658.0098247136921,
              179.38012516498566
            ],
            [
              478.7780183944851,
              129.70720505714417,
              509.33400388620794,
              180.93722438812256
            ],
            [
              993.2349925227463,
              196.6030506491661,
              1048.5854272656143,
              295.94133645296097
            ],
            [
              1008.8549218699336,
              125.01917845010757,
              1042.025573797524,
              175.89903289079666
            ],
            [
              967.5662526451051,
              121.74889832735062,
              1002.7501296438277,
              209.75881570577621
            ]
          ],
          "detector_scores": [
            0.9151259234249322,
            0.9035535636903744,
            0.8670966020757329,
            0.7313445194324856,
            0.699191643456344,
            0.6815203344371312,
            0.5614377801519572,
            0.539526900125219,
            0.484755116702103
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
        "frame": 20004,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 30,
        "raw": {
          "frame": 20004,
          "previous_frame": 20003,
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
                "frame": 20003,
                "key": "track:2",
                "bbox": [
                  686.5476684570312,
                  328.7524108886719,
                  748.70263671875,
                  502.1837158203125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 33,
              "consistent_fraction": 0.0,
              "median_patch_error": 39.47870635986328,
              "median_forward_backward_error": 24.417484283447266,
              "discontinuity": 39.47870635986328,
              "previous_mean": 0.0,
              "adaptive_ratio": 39.47870635986328,
              "appearance_previous_mean": 4.625195097178221,
              "appearance_adaptive_ratio": 8.535576452536844
            },
            {
              "region": {
                "frame": 20003,
                "key": "track:1",
                "bbox": [
                  699.520263671875,
                  196.0514678955078,
                  753.6192626953125,
                  326.4090576171875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.6153846153846154,
              "median_patch_error": 21.083900451660156,
              "median_forward_backward_error": 0.376714289188385,
              "discontinuity": 8.109192481407751,
              "previous_mean": 0.0,
              "adaptive_ratio": 8.109192481407751,
              "appearance_previous_mean": 2.9192530792206526,
              "appearance_adaptive_ratio": 7.222361295680773
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.5549886226654053,
          "discontinuity": 23.793949420635517,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 30.28130340576172
        },
        "decision": {
          "frame": 20004,
          "previous_frame": 20003,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 20004,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6a547eedda5cf5bcbeaf825476aeb536c2ec4e79c75acf37aa1e269ad5cbed44",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              504.71798988059163,
              352.0253316164017,
              586.4639001898468,
              533.8071907758713
            ],
            [
              626.3515583965927,
              213.8401027917862,
              674.0640308167785,
              332.6901310682297
            ],
            [
              232.02727183885872,
              300.4056404829025,
              282.71903553046286,
              409.64921057224274
            ],
            [
              623.1162061523646,
              129.7162327170372,
              657.5835281778127,
              178.57446044683456
            ],
            [
              992.9113827310503,
              196.3946571946144,
              1048.6674025692046,
              295.79416769742966
            ],
            [
              967.9011068772525,
              122.11669170856476,
              1000.7280219364911,
              208.2590171098709
            ],
            [
              478.1434661168605,
              128.77558681368828,
              509.55799180082977,
              180.4887993633747
            ],
            [
              769.2401872761548,
              130.0648578107357,
              806.6310242526233,
              179.01779106259346
            ],
            [
              1008.6109879706055,
              126.11089423298836,
              1041.712608864531,
              174.38380190730095
            ],
            [
              1005.4281584788114,
              126.17953795194626,
              1043.527929348871,
              208.9912856221199
            ]
          ],
          "detector_scores": [
            0.9205890845274324,
            0.9130182489312195,
            0.7724147554475237,
            0.5538636246139322,
            0.5423844675364059,
            0.5369815159281073,
            0.47408080953999293,
            0.4629230469208478,
            0.42661258685502707,
            0.36819502310911456
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
        "frame": 21241,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 31,
        "raw": {
          "frame": 21241,
          "previous_frame": 21240,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 21240,
                "key": "track:4",
                "bbox": [
                  713.5357055664062,
                  345.07086181640625,
                  790.0517578125,
                  526.892578125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 32,
              "consistent_fraction": 0.0,
              "median_patch_error": 34.207977294921875,
              "median_forward_backward_error": 32.864227294921875,
              "discontinuity": 34.207977294921875,
              "previous_mean": 0.0,
              "adaptive_ratio": 34.207977294921875,
              "appearance_previous_mean": 7.663141250610352,
              "appearance_adaptive_ratio": 4.463962776648191
            },
            {
              "region": {
                "frame": 21240,
                "key": "track:6",
                "bbox": [
                  469.1586608886719,
                  185.0855712890625,
                  536.911376953125,
                  284.5545654296875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 31,
              "consistent_fraction": 0.6129032258064516,
              "median_patch_error": 26.536848068237305,
              "median_forward_backward_error": 0.48662668466567993,
              "discontinuity": 10.272328284478956,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.272328284478956,
              "appearance_previous_mean": 9.32151746749878,
              "appearance_adaptive_ratio": 2.8468377772999953
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.75,
          "background_patch_error": 3.5654053688049316,
          "discontinuity": 22.240152789700417,
          "photometric_gain": 1.017391304347826,
          "photometric_offset": -3.426086956521729,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 30.37241268157959
        },
        "decision": {
          "frame": 21241,
          "previous_frame": 21240,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 21241,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "51c1d7ed10846d1dc31f83ca5809cd509e923791bcef9c3c2ecdb4e2ccabe00f",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              635.721433904022,
              367.1003578901291,
              694.208722088486,
              536.557932972908
            ],
            [
              559.0445916131139,
              196.23255860805511,
              603.384897582233,
              332.6198741197586
            ],
            [
              232.0,
              300.4429489970207,
              285.538690444082,
              411.0211165547371
            ],
            [
              965.302916765213,
              117.0257157087326,
              1002.1940069198608,
              212.31265211105347
            ],
            [
              992.9279244914651,
              196.2246966958046,
              1048.3717296347022,
              294.20568507909775
            ],
            [
              623.6780142504722,
              128.06224104762077,
              657.3622094672173,
              180.48444846272469
            ],
            [
              771.1329862009734,
              129.81411650776863,
              805.6836287844926,
              178.77646753191948
            ],
            [
              476.1789167355746,
              128.4715745151043,
              509.67585374601185,
              180.40414038300514
            ]
          ],
          "detector_scores": [
            0.9113352221906054,
            0.9026293845966517,
            0.854105195602676,
            0.6252624868276537,
            0.559814295638556,
            0.45776347704517145,
            0.4347775396750094,
            0.4342470197519734
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
        "frame": 21874,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 32,
        "raw": {
          "frame": 21874,
          "previous_frame": 21873,
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
                "frame": 21873,
                "key": "track:2",
                "bbox": [
                  457.9787292480469,
                  346.21661376953125,
                  535.906494140625,
                  503.83123779296875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 40,
              "consistent_fraction": 0.025,
              "median_patch_error": 23.657703399658203,
              "median_forward_backward_error": 31.304656982421875,
              "discontinuity": 23.066260814666748,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.066260814666748,
              "appearance_previous_mean": 4.346619978547096,
              "appearance_adaptive_ratio": 5.442781636402923
            },
            {
              "region": {
                "frame": 21873,
                "key": "track:1",
                "bbox": [
                  447.387939453125,
                  198.18218994140625,
                  512.5640258789062,
                  320.845458984375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.3870967741935484,
              "median_patch_error": 20.9783878326416,
              "median_forward_backward_error": 4.115595817565918,
              "discontinuity": 12.857721574844852,
              "previous_mean": 0.13887860698084664,
              "adaptive_ratio": 12.857721574844852,
              "appearance_previous_mean": 4.34091567248106,
              "appearance_adaptive_ratio": 4.83271028866851
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.5695507526397705,
          "discontinuity": 17.9619911947558,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 22.318045616149902
        },
        "decision": {
          "frame": 21874,
          "previous_frame": 21873,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 21874,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "eb585f1068220b8d84aba430028cd92f872aa21fc5c033881dd081ba13904487",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              581.7854094617069,
              362.63268971443176,
              660.6521221287549,
              532.1830289363861
            ],
            [
              685.7482157833874,
              211.8077411055565,
              743.2539308182895,
              332.57806783914566
            ],
            [
              232.04234508052468,
              302.0613279938698,
              285.4599047936499,
              411.60355895757675
            ],
            [
              965.0008873511106,
              115.87595808506012,
              1002.4730513524264,
              213.84652817249298
            ],
            [
              992.8180427663028,
              196.27052801847458,
              1048.719057906419,
              295.01121670007706
            ],
            [
              622.7497962675989,
              128.23566436767578,
              657.8048697151244,
              179.7351917028427
            ],
            [
              1010.6450218763202,
              122.75714612007141,
              1045.788197318092,
              207.68061351776123
            ],
            [
              770.1723344977945,
              129.5436171591282,
              806.2831435743719,
              178.55359861254692
            ],
            [
              478.5985349677503,
              128.61614099144936,
              509.38215151801705,
              180.36983343958855
            ]
          ],
          "detector_scores": [
            0.9422725371673656,
            0.8818534296986148,
            0.833542444774508,
            0.556712030547519,
            0.5341992803706731,
            0.42177775936497663,
            0.4070980118923113,
            0.402142968388242,
            0.38014100485306423
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
        "frame": 22539,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 33,
        "raw": {
          "frame": 22539,
          "previous_frame": 22538,
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
                "frame": 22538,
                "key": "track:3",
                "bbox": [
                  602.1090698242188,
                  293.6165771484375,
                  661.0557250976562,
                  453.2177429199219
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 38,
              "consistent_fraction": 0.2894736842105263,
              "median_patch_error": 34.85154342651367,
              "median_forward_backward_error": 7.375494003295898,
              "discontinuity": 24.762938750417607,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.762938750417607,
              "appearance_previous_mean": 8.454542636871338,
              "appearance_adaptive_ratio": 4.12222694040499
            },
            {
              "region": {
                "frame": 22538,
                "key": "track:1",
                "bbox": [
                  610.2564086914062,
                  209.56033325195312,
                  659.0335693359375,
                  320.5546569824219
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.2727272727272727,
              "median_patch_error": 33.12677001953125,
              "median_forward_backward_error": 12.134570121765137,
              "discontinuity": 24.09219637784091,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.09219637784091,
              "appearance_previous_mean": 5.790302753448486,
              "appearance_adaptive_ratio": 5.721077365048346
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.383751392364502,
          "discontinuity": 24.42756756412926,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 33.98915672302246
        },
        "decision": {
          "frame": 22539,
          "previous_frame": 22538,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 22539,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "baf5455f2e1449094d8c6dbb16065cf84e0cd78cc7305e2fb27f75645a678bc6",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              618.222500577569,
              363.40367114543915,
              692.9928159564734,
              533.1785498857498
            ],
            [
              546.6102309636772,
              210.44983786344528,
              609.3752823062241,
              332.30326348543167
            ],
            [
              232.028064686805,
              301.353613615036,
              285.92732898518443,
              411.1267635822296
            ],
            [
              992.282789748162,
              196.72581213712692,
              1049.0,
              295.0371018052101
            ],
            [
              964.0589839909226,
              117.10812121629715,
              1003.6785028483719,
              214.22286731004715
            ],
            [
              770.2480081059039,
              130.07321080565453,
              805.5954461358488,
              178.50101605057716
            ],
            [
              622.4291082955897,
              128.36957159638405,
              658.0158433578908,
              179.40943178534508
            ],
            [
              1007.5148566626012,
              122.95681941509247,
              1046.4948104955256,
              209.6447330713272
            ],
            [
              477.0064293332398,
              129.4488152563572,
              509.85515151545405,
              180.67827007174492
            ]
          ],
          "detector_scores": [
            0.921251310210513,
            0.9140770423741879,
            0.7524230024077766,
            0.4734437262091076,
            0.39876135734484247,
            0.39530388616665374,
            0.3634896063661335,
            0.3587205496116006,
            0.35295042327281795
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
        "frame": 23584,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 34,
        "raw": {
          "frame": 23584,
          "previous_frame": 23583,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 23583,
                "key": "track:0",
                "bbox": [
                  918.6609497070312,
                  363.6593322753906,
                  969.6106567382812,
                  538.7448120117188
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 40,
              "consistent_fraction": 0.25,
              "median_patch_error": 31.185693740844727,
              "median_forward_backward_error": 3.356595039367676,
              "discontinuity": 23.389270305633545,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.389270305633545,
              "appearance_previous_mean": 7.106699846684933,
              "appearance_adaptive_ratio": 4.388210338641492
            },
            {
              "region": {
                "frame": 23583,
                "key": "track:2",
                "bbox": [
                  708.4227294921875,
                  180.13197326660156,
                  756.5057373046875,
                  309.1760559082031
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.88,
              "median_patch_error": 20.30605125427246,
              "median_forward_backward_error": 0.16416588425636292,
              "discontinuity": 2.4367261505126954,
              "previous_mean": 0.0,
              "adaptive_ratio": 2.4367261505126954,
              "appearance_previous_mean": 3.9383858367800713,
              "appearance_adaptive_ratio": 5.155932429127918
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.7785217761993408,
          "discontinuity": 12.91299822807312,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7217391304347842,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 25.745872497558594
        },
        "decision": {
          "frame": 23584,
          "previous_frame": 23583,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 23584,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "4cb79c4aee1171e6820600a7189585661365692cc17d3766c6d8f6a4c27caf42",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              580.1755385547876,
              365.51814460754395,
              662.5293882340193,
              535.0726327896118
            ],
            [
              690.9728935267776,
              197.3801132440567,
              741.4443733189255,
              331.48909890651703
            ],
            [
              232.04598213732243,
              301.9486543536186,
              286.2344274520874,
              411.0211165547371
            ],
            [
              477.446151021868,
              129.3319444656372,
              509.53882801160216,
              181.30301213264465
            ],
            [
              622.4528313409537,
              128.60848101973534,
              658.1338772643358,
              180.08091619610786
            ],
            [
              964.3492348194122,
              116.66547673940659,
              1001.7122962474823,
              213.2890483736992
            ],
            [
              770.1083040367812,
              131.01026538014412,
              805.8420888055116,
              178.69467243552208
            ],
            [
              993.0595281198621,
              194.76174306869507,
              1048.3954694196582,
              293.5643632411957
            ],
            [
              1008.8189408779144,
              122.18231320381165,
              1044.7716399431229,
              205.45451283454895
            ],
            [
              319.4696211591363,
              122.21451812982559,
              347.9443366602063,
              179.20603865385056
            ]
          ],
          "detector_scores": [
            0.9423681205169785,
            0.9001196308069369,
            0.7505380258656634,
            0.6204676795041504,
            0.5942182210938768,
            0.5719698574224696,
            0.5409007820149863,
            0.498564724096085,
            0.4405269621131309,
            0.3771149410723429
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
        "frame": 24902,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 35,
        "raw": {
          "frame": 24902,
          "previous_frame": 24901,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 24901,
                "key": "track:3",
                "bbox": [
                  543.3776245117188,
                  374.7183532714844,
                  615.3444213867188,
                  561.146728515625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 41,
              "consistent_fraction": 0.34146341463414637,
              "median_patch_error": 24.36947250366211,
              "median_forward_backward_error": 2.5152621269226074,
              "discontinuity": 16.048189209728704,
              "previous_mean": 0.0,
              "adaptive_ratio": 16.048189209728704,
              "appearance_previous_mean": 4.723993848543614,
              "appearance_adaptive_ratio": 5.158658813913381
            },
            {
              "region": {
                "frame": 24901,
                "key": "track:5",
                "bbox": [
                  721.1810302734375,
                  197.5768585205078,
                  782.0281372070312,
                  315.77471923828125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.6923076923076923,
              "median_patch_error": 18.759105682373047,
              "median_forward_backward_error": 0.28754109144210815,
              "discontinuity": 5.772032517653246,
              "previous_mean": 0.0,
              "adaptive_ratio": 5.772032517653246,
              "appearance_previous_mean": 5.081721456721425,
              "appearance_adaptive_ratio": 3.6914864071427997
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.9431688785552979,
          "discontinuity": 10.910110863690974,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 21.564289093017578
        },
        "decision": {
          "frame": 24902,
          "previous_frame": 24901,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 24902,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "08959e16d8146613e6e60a56f390109137acd4846dbd5b6aa2036c73140af426",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              520.5843244995922,
              365.16879665851593,
              571.1609411034733,
              551.9263972043991
            ],
            [
              627.1829089261591,
              192.7838869690895,
              679.2117947004735,
              333.0411266684532
            ],
            [
              232.0,
              300.37148040533066,
              285.68239223212004,
              411.35576874017715
            ],
            [
              993.2199177592993,
              195.5415410399437,
              1049.0,
              294.62527161836624
            ],
            [
              965.9963056650013,
              117.38084650039673,
              1003.767268339172,
              213.31844449043274
            ]
          ],
          "detector_scores": [
            0.9197424456006,
            0.8768070254967318,
            0.7986046139445871,
            0.44393445751478955,
            0.3594779381640337
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
        "frame": 25108,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 36,
        "raw": {
          "frame": 25108,
          "previous_frame": 25107,
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
                "frame": 25107,
                "key": "track:0",
                "bbox": [
                  747.0145874023438,
                  333.3879089355469,
                  809.3040771484375,
                  498.43603515625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 34,
              "consistent_fraction": 0.0,
              "median_patch_error": 25.246349334716797,
              "median_forward_backward_error": 21.170536041259766,
              "discontinuity": 25.246349334716797,
              "previous_mean": 0.0,
              "adaptive_ratio": 25.246349334716797,
              "appearance_previous_mean": 7.426764488220215,
              "appearance_adaptive_ratio": 3.399373896231756
            },
            {
              "region": {
                "frame": 25107,
                "key": "track:1",
                "bbox": [
                  683.383056640625,
                  218.11563110351562,
                  728.1571044921875,
                  330.4903259277344
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 19,
              "consistent_fraction": 0.3684210526315789,
              "median_patch_error": 27.937570571899414,
              "median_forward_backward_error": 3.208738327026367,
              "discontinuity": 17.644781413831208,
              "previous_mean": 0.0,
              "adaptive_ratio": 17.644781413831208,
              "appearance_previous_mean": 7.940830707550049,
              "appearance_adaptive_ratio": 3.5182176274500727
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 2.0055980682373047,
          "discontinuity": 21.445565374274004,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7217391304347842,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 26.591959953308105
        },
        "decision": {
          "frame": 25108,
          "previous_frame": 25107,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 25108,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "9221fb83d429d640a5e303bdce4debdf7620fd30c0ccdbde296201a0ffcdfecc",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              559.7937933560461,
              197.09950309991837,
              606.2872399929911,
              332.8111714720726
            ],
            [
              631.1177265420556,
              363.0005794763565,
              691.1489833816886,
              532.3269666433334
            ],
            [
              232.062484331429,
              302.5702640414238,
              285.8236439526081,
              411.4202244877815
            ],
            [
              992.6766479983926,
              196.59174197912216,
              1048.7447486147285,
              295.1183186173439
            ],
            [
              965.6510044056922,
              117.9991654753685,
              1002.0668088477105,
              212.67177122831345
            ],
            [
              477.0238476395607,
              129.99631506204605,
              509.9009906053543,
              181.05787926912308
            ],
            [
              622.8026796821505,
              129.1806198656559,
              657.6945238467306,
              179.74769136309624
            ],
            [
              769.7707075551152,
              129.89833489060402,
              805.9094169661403,
              178.92708763480186
            ],
            [
              1002.5735649932176,
              124.61347073316574,
              1044.2426794897765,
              211.12888127565384
            ]
          ],
          "detector_scores": [
            0.9240795869454823,
            0.9186816309181773,
            0.7611188711458853,
            0.6492115550491216,
            0.6430282408228707,
            0.6221900168604547,
            0.590957530675542,
            0.5787890591408323,
            0.4193059856094226
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
        "frame": 25550,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 37,
        "raw": {
          "frame": 25550,
          "previous_frame": 25549,
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
                "frame": 25549,
                "key": "track:2",
                "bbox": [
                  901.0952758789062,
                  298.2935485839844,
                  957.6831665039062,
                  455.82550048828125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 40,
              "consistent_fraction": 0.525,
              "median_patch_error": 31.573022842407227,
              "median_forward_backward_error": 0.8195891380310059,
              "discontinuity": 14.997185850143431,
              "previous_mean": 0.3509735671841366,
              "adaptive_ratio": 14.997185850143431,
              "appearance_previous_mean": 5.77132960036397,
              "appearance_adaptive_ratio": 5.4706670782441655
            },
            {
              "region": {
                "frame": 25549,
                "key": "track:0",
                "bbox": [
                  725.3616333007812,
                  201.5406951904297,
                  774.2847290039062,
                  338.2886047363281
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 28,
              "consistent_fraction": 0.32142857142857145,
              "median_patch_error": 23.86741828918457,
              "median_forward_backward_error": 4.518866539001465,
              "discontinuity": 16.195748124803817,
              "previous_mean": 0.0,
              "adaptive_ratio": 16.195748124803817,
              "appearance_previous_mean": 4.093962654471397,
              "appearance_adaptive_ratio": 5.829906206671608
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.7741992473602295,
          "discontinuity": 15.596466987473624,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 27.7202205657959
        },
        "decision": {
          "frame": 25550,
          "previous_frame": 25549,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 25550,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "9a7c026707378217c6a31e1d3b1b086743255036cea1a7f332f3be2ce9e1d6a1",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              663.7194119133055,
              366.9279557466507,
              743.8223586641252,
              541.9992207288742
            ],
            [
              605.5160789489746,
              205.2327132821083,
              660.5845398306847,
              333.2083701491356
            ],
            [
              232.089200720191,
              298.7706885933876,
              285.3825039640069,
              411.3186392188072
            ],
            [
              965.5138204060495,
              117.95271915197372,
              1002.3606997765601,
              213.5468071103096
            ],
            [
              622.729157872498,
              129.1506798863411,
              657.7902514860034,
              179.9776809811592
            ],
            [
              1005.1116097513586,
              123.43905800580978,
              1044.7240431960672,
              210.17668575048447
            ],
            [
              770.564914451912,
              129.72836291790009,
              805.3623960148543,
              179.60435259342194
            ],
            [
              1021.0485291425139,
              197.04077512025833,
              1049.0,
              254.9506477713585
            ],
            [
              477.73250609077513,
              130.77681064605713,
              508.81668353639543,
              180.52221822738647
            ],
            [
              993.126842584461,
              201.6966197490692,
              1045.0030267573893,
              292.37871527671814
            ]
          ],
          "detector_scores": [
            0.9387562403511935,
            0.9053232382499445,
            0.8153487461422754,
            0.6667875608349545,
            0.6077560442113973,
            0.46653880681434085,
            0.4487508640305355,
            0.38614579073582833,
            0.36990931173892955,
            0.36816967701666575
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
        "frame": 26713,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 38,
        "raw": {
          "frame": 26713,
          "previous_frame": 26712,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 26712,
                "key": "track:3",
                "bbox": [
                  676.9839477539062,
                  400.9997863769531,
                  742.2430419921875,
                  590.7213745117188
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 45,
              "consistent_fraction": 0.022222222222222223,
              "median_patch_error": 32.984622955322266,
              "median_forward_backward_error": 13.55185604095459,
              "discontinuity": 32.25163133409288,
              "previous_mean": 0.0,
              "adaptive_ratio": 32.25163133409288,
              "appearance_previous_mean": 9.79076337814331,
              "appearance_adaptive_ratio": 3.368953132802334
            },
            {
              "region": {
                "frame": 26712,
                "key": "track:2",
                "bbox": [
                  432.95892333984375,
                  213.57525634765625,
                  475.2806091308594,
                  340.0108947753906
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 17,
              "consistent_fraction": 0.7647058823529411,
              "median_patch_error": 19.02019500732422,
              "median_forward_backward_error": 0.16365110874176025,
              "discontinuity": 4.475340001723347,
              "previous_mean": 0.25595237992026565,
              "adaptive_ratio": 4.475340001723347,
              "appearance_previous_mean": 11.123618125915527,
              "appearance_adaptive_ratio": 1.7098928417015182
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.5595946311950684,
          "discontinuity": 18.36348566790811,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 1.7130434782608717,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 26.002408981323242
        },
        "decision": {
          "frame": 26713,
          "previous_frame": 26712,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 26713,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6ba0108b9135041c1409d43d65bf19dbb3c1383475c9d3348a509bcf49e1f418",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              664.0258651450276,
              365.88590586185455,
              747.8182849213481,
              542.7940219640732
            ],
            [
              605.2490459345281,
              207.81712532043457,
              664.4650846458972,
              334.14073419570923
            ],
            [
              965.4053265452385,
              116.52608728408813,
              1002.4866271615028,
              212.38467144966125
            ],
            [
              623.0804747324437,
              129.02904284000397,
              657.6959573645145,
              180.38341164588928
            ],
            [
              232.10435461625457,
              299.05447471141815,
              284.731787327677,
              411.02949249744415
            ],
            [
              993.2874026633799,
              196.02315545082092,
              1048.6921589039266,
              296.3697578907013
            ],
            [
              1003.4900393914431,
              121.97503960132599,
              1045.59295280464,
              216.78937089443207
            ],
            [
              770.1247149240226,
              129.7640949189663,
              806.2027874458581,
              178.60922864079475
            ],
            [
              478.2407307550311,
              131.84874084591866,
              508.2698908522725,
              180.8540684878826
            ],
            [
              1022.434879321605,
              195.84860768914223,
              1049.0,
              260.62284764647484
            ]
          ],
          "detector_scores": [
            0.9344539206357751,
            0.9114058993580716,
            0.611612500987964,
            0.5680357142694906,
            0.5169530469729536,
            0.4780670579159419,
            0.45580625049157003,
            0.41410926235361534,
            0.3849444325256762,
            0.3555102356561094
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
        "frame": 27109,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 39,
        "raw": {
          "frame": 27109,
          "previous_frame": 27108,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 27108,
                "key": "track:3",
                "bbox": [
                  511.1617431640625,
                  331.9627685546875,
                  585.4082641601562,
                  499.6988525390625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 47,
              "consistent_fraction": 0.0425531914893617,
              "median_patch_error": 26.410112380981445,
              "median_forward_backward_error": 17.43865394592285,
              "discontinuity": 25.286277811577982,
              "previous_mean": 0.0,
              "adaptive_ratio": 25.286277811577982,
              "appearance_previous_mean": 8.48940634727478,
              "appearance_adaptive_ratio": 3.110949258479006
            },
            {
              "region": {
                "frame": 27108,
                "key": "track:2",
                "bbox": [
                  578.7086181640625,
                  234.5316925048828,
                  619.1373901367188,
                  373.63165283203125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 23,
              "consistent_fraction": 0.2608695652173913,
              "median_patch_error": 22.664257049560547,
              "median_forward_backward_error": 5.652692794799805,
              "discontinuity": 16.75184216706649,
              "previous_mean": 0.0,
              "adaptive_ratio": 16.75184216706649,
              "appearance_previous_mean": 10.067106246948242,
              "appearance_adaptive_ratio": 2.251317955090722
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.7357568740844727,
          "discontinuity": 21.019059989322237,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 24.537184715270996
        },
        "decision": {
          "frame": 27109,
          "previous_frame": 27108,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 27109,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b0cea589ea22a470fe482add2496717e5248e71a6b29b63a042aff4a96df7b7f",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              524.3608905784786,
              371.13838839530945,
              586.1054476983845,
              550.367333650589
            ],
            [
              626.977071294561,
              203.35419356822968,
              675.1878113653511,
              333.5488740205765
            ],
            [
              232.0,
              299.35274547338486,
              285.24164486303926,
              411.4202428460121
            ],
            [
              478.4904611185193,
              128.48896434903145,
              509.8153265044093,
              180.1827171742916
            ],
            [
              966.4727251045406,
              118.04000794887543,
              1002.8071903474629,
              211.37121450901031
            ],
            [
              622.8186872974038,
              129.3787763118744,
              657.6690690144897,
              180.08867943286896
            ],
            [
              992.8829132504761,
              196.38550102710724,
              1048.6326633505523,
              296.020960688591
            ],
            [
              769.9279927611351,
              130.180969029665,
              806.4264877438545,
              178.31756684184074
            ],
            [
              1010.9755299016833,
              122.81352883577347,
              1047.1875039413571,
              212.32551664113998
            ]
          ],
          "detector_scores": [
            0.9228674196666763,
            0.9040852595507731,
            0.7640705857066877,
            0.6223171184286863,
            0.6091753538174227,
            0.5932557382541226,
            0.4974452479483168,
            0.49720528652017787,
            0.3867640118546172
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
        "frame": 27473,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 40,
        "raw": {
          "frame": 27473,
          "previous_frame": 27472,
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
                "frame": 27472,
                "key": "track:2",
                "bbox": [
                  547.5474243164062,
                  296.2786865234375,
                  599.7819213867188,
                  447.5494384765625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 36,
              "consistent_fraction": 0.19444444444444445,
              "median_patch_error": 30.275793075561523,
              "median_forward_backward_error": 5.070608615875244,
              "discontinuity": 24.388833310869007,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.388833310869007,
              "appearance_previous_mean": 7.473869562149048,
              "appearance_adaptive_ratio": 4.0508859331572244
            },
            {
              "region": {
                "frame": 27472,
                "key": "track:3",
                "bbox": [
                  593.04443359375,
                  205.12525939941406,
                  642.0841674804688,
                  342.09832763671875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 32,
              "consistent_fraction": 0.53125,
              "median_patch_error": 28.34027862548828,
              "median_forward_backward_error": 0.9113630056381226,
              "discontinuity": 13.284505605697632,
              "previous_mean": 0.0,
              "adaptive_ratio": 13.284505605697632,
              "appearance_previous_mean": 5.4607603549957275,
              "appearance_adaptive_ratio": 5.18980449298813
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.410856008529663,
          "discontinuity": 18.836669458283318,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 29.308035850524902
        },
        "decision": {
          "frame": 27473,
          "previous_frame": 27472,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 27473,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "a24bcb9c707ecfb16788abd03f42e9c129ff896de2ce81fe9743bfc8edfedc31",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              625.6271525546908,
              365.09657537937164,
              693.638556368649,
              532.2544883489609
            ],
            [
              552.7101824041456,
              196.2753700017929,
              603.6253648642451,
              332.11322367191315
            ],
            [
              992.4180973917246,
              196.2982948422432,
              1048.8059789985418,
              296.79874843358994
            ],
            [
              232.16684503480792,
              303.83828997612,
              285.8126840852201,
              411.4662072658539
            ],
            [
              965.4217937383801,
              116.7437516450882,
              1003.4579298105091,
              213.54201102256775
            ],
            [
              623.067437633872,
              129.62239921092987,
              657.9692799001932,
              180.33426666259766
            ],
            [
              770.6840759981424,
              130.2718468606472,
              805.6865719091147,
              178.7411417067051
            ],
            [
              477.2045621871948,
              130.62052243947983,
              509.2262450456619,
              180.68281143903732
            ]
          ],
          "detector_scores": [
            0.9293335058597041,
            0.9136931827331574,
            0.631993529933903,
            0.5608915173089308,
            0.43849306689359313,
            0.4285239051408537,
            0.4093337740668246,
            0.36743107852603385
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
        "frame": 29207,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 41,
        "raw": {
          "frame": 29207,
          "previous_frame": 29206,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 29206,
                "key": "track:8",
                "bbox": [
                  653.8040771484375,
                  363.23126220703125,
                  714.61572265625,
                  542.0387573242188
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 39,
              "consistent_fraction": 0.0,
              "median_patch_error": 35.3731575012207,
              "median_forward_backward_error": 49.42143249511719,
              "discontinuity": 35.3731575012207,
              "previous_mean": 0.0,
              "adaptive_ratio": 35.3731575012207,
              "appearance_previous_mean": 5.117028132081032,
              "appearance_adaptive_ratio": 6.912832329267434
            },
            {
              "region": {
                "frame": 29206,
                "key": "track:10",
                "bbox": [
                  803.4092407226562,
                  207.4824676513672,
                  868.0078125,
                  340.6147766113281
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 28,
              "consistent_fraction": 0.8928571428571429,
              "median_patch_error": 17.043651580810547,
              "median_forward_backward_error": 0.16694234311580658,
              "discontinuity": 1.826105526515415,
              "previous_mean": 0.0,
              "adaptive_ratio": 1.826105526515415,
              "appearance_previous_mean": 4.327664539217949,
              "appearance_adaptive_ratio": 3.9383023860464244
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.0001771450042725,
          "discontinuity": 18.599631513868058,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 26.208404541015625
        },
        "decision": {
          "frame": 29207,
          "previous_frame": 29206,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 29207,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "c7f44d51097fa993afda32bef697e721c7a354277d84eb20d5570d36cc492547",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              509.4233963508159,
              355.83172714710236,
              559.9119018297642,
              533.3817204236984
            ],
            [
              626.8160440288484,
              206.43521869182587,
              684.8538102544844,
              332.42637836933136
            ],
            [
              232.0,
              298.5337664484978,
              285.28552389889956,
              411.4390967488289
            ],
            [
              478.0570472124964,
              124.97906571626663,
              508.7659169193357,
              180.76501041650772
            ],
            [
              622.740712756291,
              129.06010955572128,
              656.8554015811533,
              179.5635468363762
            ],
            [
              770.3954778239131,
              129.63773292303085,
              806.373414106667,
              178.4970162510872
            ],
            [
              992.9545982703567,
              196.61138528585434,
              1048.5390646830201,
              295.79959255456924
            ],
            [
              967.6289211120456,
              122.42672550678253,
              999.931113878265,
              208.84447944164276
            ],
            [
              1009.1799834407866,
              124.38868796825409,
              1040.10724395141,
              170.00018000602722
            ],
            [
              1004.5602060705423,
              124.0527736544609,
              1041.0524434894323,
              209.2100790143013
            ]
          ],
          "detector_scores": [
            0.900765314060328,
            0.8862342459284924,
            0.8288719941941182,
            0.7687156394062138,
            0.7157589986996333,
            0.6892238119031839,
            0.5047598831343002,
            0.4362714798039154,
            0.42307343473011827,
            0.37946652123502006
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
        "frame": 29592,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 42,
        "raw": {
          "frame": 29592,
          "previous_frame": 29591,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 29591,
                "key": "track:0",
                "bbox": [
                  882.7637329101562,
                  444.9051513671875,
                  951.0254516601562,
                  650.7774658203125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 49,
              "consistent_fraction": 0.02040816326530612,
              "median_patch_error": 28.76027488708496,
              "median_forward_backward_error": 15.610570907592773,
              "discontinuity": 28.173330501634247,
              "previous_mean": 0.1469530192288484,
              "adaptive_ratio": 28.173330501634247,
              "appearance_previous_mean": 12.758201599121094,
              "appearance_adaptive_ratio": 2.2542577544053106
            },
            {
              "region": {
                "frame": 29591,
                "key": "track:2",
                "bbox": [
                  855.0156860351562,
                  187.40713500976562,
                  901.7333374023438,
                  310.8313293457031
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 23,
              "consistent_fraction": 0.43478260869565216,
              "median_patch_error": 32.45500183105469,
              "median_forward_backward_error": 3.192445993423462,
              "discontinuity": 18.344131469726566,
              "previous_mean": 0.0,
              "adaptive_ratio": 18.344131469726566,
              "appearance_previous_mean": 3.503649353981018,
              "appearance_adaptive_ratio": 9.263199182354743
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 3.113166093826294,
          "discontinuity": 23.25873098568041,
          "photometric_gain": 0.9826086956521739,
          "photometric_offset": 2.4260869565217433,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 30.607638359069824
        },
        "decision": {
          "frame": 29592,
          "previous_frame": 29591,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 29592,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "5a283d7421ba6a2297fa149be8f313055017591e38edc98bd16767614726d537",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              615.1706477403641,
              353.09014570713043,
              687.8606518507004,
              528.9002193212509
            ],
            [
              557.6983449310064,
              218.0290195941925,
              622.0591907054186,
              327.0834815502167
            ],
            [
              232.04164810478687,
              302.52082991600037,
              286.0599826425314,
              411.63502955436707
            ],
            [
              992.9655246585608,
              196.549742937088,
              1048.728282943368,
              296.53764390945435
            ],
            [
              1008.0521869119257,
              124.16772371530533,
              1041.808885866776,
              193.15274053812027
            ],
            [
              622.3120513726026,
              129.39437392354012,
              657.6400379966944,
              179.1434210240841
            ],
            [
              967.3598793465644,
              121.00303095579147,
              1002.4335946124047,
              207.44728499650955
            ],
            [
              478.49242269434035,
              128.5158293247223,
              509.87160653434694,
              180.05883812904358
            ],
            [
              770.4539172612131,
              129.84904763102531,
              806.2369620837271,
              178.6091552078724
            ]
          ],
          "detector_scores": [
            0.9180248778638189,
            0.9091779659391677,
            0.7001930861320302,
            0.5606702458410889,
            0.5594454198691917,
            0.49340441339933494,
            0.4742825683057475,
            0.44915702368233884,
            0.43795788760160353
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
        "frame": 30166,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 43,
        "raw": {
          "frame": 30166,
          "previous_frame": 30165,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 30165,
                "key": "track:0",
                "bbox": [
                  513.5645141601562,
                  353.8259582519531,
                  565.3821411132812,
                  516.25048828125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.0,
              "median_patch_error": 36.466270446777344,
              "median_forward_backward_error": 67.92784118652344,
              "discontinuity": 36.466270446777344,
              "previous_mean": 0.0,
              "adaptive_ratio": 36.466270446777344,
              "appearance_previous_mean": 8.165514945983887,
              "appearance_adaptive_ratio": 4.465887416532482
            },
            {
              "region": {
                "frame": 30165,
                "key": "track:1",
                "bbox": [
                  479.45196533203125,
                  191.78256225585938,
                  542.1522827148438,
                  313.47283935546875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.6666666666666666,
              "median_patch_error": 17.775156021118164,
              "median_forward_backward_error": 0.21979236602783203,
              "discontinuity": 5.925052007039389,
              "previous_mean": 0.0,
              "adaptive_ratio": 5.925052007039389,
              "appearance_previous_mean": 7.0649094581604,
              "appearance_adaptive_ratio": 2.5159778941804807
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 3.0078654289245605,
          "discontinuity": 21.195661226908367,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 0.728070175438603,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 27.120713233947754
        },
        "decision": {
          "frame": 30166,
          "previous_frame": 30165,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 30166,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "7c51f188d19a427757731a5e430ec286f1b1f184e0a0ffb5ca714f3e17b9d36d",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              685.5401380900294,
              198.6348156929016,
              735.825053608045,
              323.48917865753174
            ],
            [
              594.7016725279391,
              355.2172679901123,
              653.2314123176038,
              532.5063724517822
            ],
            [
              232.0,
              300.1563540697098,
              285.97132367640734,
              411.33925092220306
            ],
            [
              1007.9195043407381,
              124.20804986357689,
              1041.7158091701567,
              198.83991613984108
            ],
            [
              966.8858673647046,
              121.43596851825714,
              1000.0460737869143,
              207.2827080488205
            ],
            [
              622.8004883173853,
              129.12074679136276,
              657.335626995191,
              179.06448751688004
            ],
            [
              993.1353067308664,
              196.30723071098328,
              1048.7964343875647,
              296.2405159473419
            ],
            [
              477.33149394765496,
              129.1009221971035,
              509.94172259792686,
              180.22217360138893
            ],
            [
              770.6093595903367,
              130.5242656469345,
              806.4210352022201,
              178.60235118865967
            ]
          ],
          "detector_scores": [
            0.9177145536067736,
            0.9044595987612472,
            0.8484173791313387,
            0.5823712472598152,
            0.5496190171057765,
            0.5485569471699452,
            0.5480771227700565,
            0.4457393367342619,
            0.42092627274350564
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
        "frame": 30406,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 44,
        "raw": {
          "frame": 30406,
          "previous_frame": 30405,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 30405,
                "key": "track:3",
                "bbox": [
                  636.7147827148438,
                  329.7330322265625,
                  699.911376953125,
                  503.94970703125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 47,
              "consistent_fraction": 0.0425531914893617,
              "median_patch_error": 37.653133392333984,
              "median_forward_backward_error": 28.82975959777832,
              "discontinuity": 36.050872396915516,
              "previous_mean": 0.0,
              "adaptive_ratio": 36.050872396915516,
              "appearance_previous_mean": 5.5040037631988525,
              "appearance_adaptive_ratio": 6.841044267464398
            },
            {
              "region": {
                "frame": 30405,
                "key": "track:0",
                "bbox": [
                  689.8924560546875,
                  239.027099609375,
                  739.8374633789062,
                  377.3984680175781
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.3,
              "median_patch_error": 22.243125915527344,
              "median_forward_backward_error": 11.487777709960938,
              "discontinuity": 15.57018814086914,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.57018814086914,
              "appearance_previous_mean": 8.805910110473633,
              "appearance_adaptive_ratio": 2.5259315205899804
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.181830883026123,
          "discontinuity": 25.81053026889233,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 1.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 29.948129653930664
        },
        "decision": {
          "frame": 30406,
          "previous_frame": 30405,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 30406,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "7a0aac8afa731828d802d9e4bf658dea016935744d91297a7f21d1eedba29141",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              624.5604661889374,
              218.96134692430496,
              673.4070277027786,
              332.74128168821335
            ],
            [
              498.1975383684039,
              352.61710917949677,
              581.2627415731549,
              535.1072655916214
            ],
            [
              232.0,
              300.9416916370392,
              284.8304230906069,
              411.6441352367401
            ],
            [
              478.8319031409919,
              129.32393339276314,
              509.8922890610993,
              180.13939175009727
            ],
            [
              622.80389710702,
              129.41104090213776,
              657.3011008258909,
              179.77909541130066
            ],
            [
              771.5256209392101,
              130.34549549221992,
              805.7663741093129,
              178.73255464434624
            ],
            [
              993.1626135706902,
              196.91989994049072,
              1048.556711256504,
              294.7253928184509
            ],
            [
              966.9106221776456,
              121.7256338596344,
              1001.2241347450763,
              211.17196345329285
            ],
            [
              1003.488828053698,
              125.44231730699539,
              1040.9780786130577,
              212.34000128507614
            ],
            [
              1008.7596416343004,
              125.28419327735901,
              1039.884006274864,
              169.67218267917633
            ]
          ],
          "detector_scores": [
            0.9015130890031907,
            0.8990684267604199,
            0.774572976787276,
            0.7083854766001675,
            0.702626011593777,
            0.6622472958734579,
            0.4913915558351937,
            0.48897564297515494,
            0.4232284704658811,
            0.42166158833058776
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
        "frame": 31886,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 45,
        "raw": {
          "frame": 31886,
          "previous_frame": 31885,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 31885,
                "key": "track:9",
                "bbox": [
                  970.34716796875,
                  520.8037719726562,
                  1049.0,
                  717.9180297851562
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 50,
              "consistent_fraction": 0.04,
              "median_patch_error": 32.06122589111328,
              "median_forward_backward_error": 15.244346618652344,
              "discontinuity": 30.77877685546875,
              "previous_mean": 1.0003395477930708,
              "adaptive_ratio": 30.76832953707796,
              "appearance_previous_mean": 13.762152671813965,
              "appearance_adaptive_ratio": 2.329666488642968
            },
            {
              "region": {
                "frame": 31885,
                "key": "track:8",
                "bbox": [
                  746.7869262695312,
                  192.20697021484375,
                  801.2647094726562,
                  321.8895568847656
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.7741935483870968,
              "median_patch_error": 22.54166603088379,
              "median_forward_backward_error": 0.22530172765254974,
              "discontinuity": 5.0900536198769855,
              "previous_mean": 0.0,
              "adaptive_ratio": 5.0900536198769855,
              "appearance_previous_mean": 11.605601787567139,
              "appearance_adaptive_ratio": 1.9423091058519903
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.317424774169922,
          "discontinuity": 17.934415237672866,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 1.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 27.301445960998535
        },
        "decision": {
          "frame": 31886,
          "previous_frame": 31885,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 31886,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "0e96e7137c69bd7bd791ab07faae9982ce8fd6bbaca9d8bc380a4b491abcc432",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              556.7465499937534,
              214.31340551376343,
              622.6922151148319,
              326.7478013038635
            ],
            [
              611.0537855401635,
              352.35754215717316,
              683.9777665361762,
              527.7334803342819
            ],
            [
              232.1326140910387,
              304.46792221069336,
              284.51430959254503,
              411.3766007423401
            ],
            [
              622.9672968294472,
              129.35306790471077,
              657.6778481695801,
              179.5227571427822
            ],
            [
              770.6325469687581,
              129.96505558490753,
              806.1206645295024,
              178.78674125671387
            ],
            [
              992.7413419559598,
              196.15986001491547,
              1048.4382253810763,
              295.5798307657242
            ],
            [
              478.7400043029338,
              131.66923865675926,
              508.16623168997467,
              182.2551089823246
            ],
            [
              1007.9062191918492,
              124.13811647891998,
              1040.9127378985286,
              173.95241332054138
            ],
            [
              966.4709202721715,
              121.4579570889473,
              1002.9383343979716,
              211.70757859945297
            ],
            [
              1005.0356241781265,
              123.72413378953934,
              1042.0383248012513,
              209.52449125051498
            ]
          ],
          "detector_scores": [
            0.9185601469802185,
            0.8915678415530515,
            0.5874443091941566,
            0.5373243656713979,
            0.5137199284027203,
            0.48557777039221023,
            0.4334161595201969,
            0.40499167604257097,
            0.4048184110264266,
            0.38143887351728073
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
        "frame": 32177,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 46,
        "raw": {
          "frame": 32177,
          "previous_frame": 32176,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 32176,
                "key": "track:1",
                "bbox": [
                  698.8521118164062,
                  327.55126953125,
                  772.9305419921875,
                  500.84429931640625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.0,
              "median_patch_error": 36.19330978393555,
              "median_forward_backward_error": 53.16599655151367,
              "discontinuity": 36.19330978393555,
              "previous_mean": 0.0,
              "adaptive_ratio": 36.19330978393555,
              "appearance_previous_mean": 7.312570810317993,
              "appearance_adaptive_ratio": 4.949464521132159
            },
            {
              "region": {
                "frame": 32176,
                "key": "track:0",
                "bbox": [
                  689.7763061523438,
                  231.58370971679688,
                  748.6527099609375,
                  350.1092224121094
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 29,
              "consistent_fraction": 0.41379310344827586,
              "median_patch_error": 27.657737731933594,
              "median_forward_backward_error": 1.254711389541626,
              "discontinuity": 16.213156601478314,
              "previous_mean": 0.0,
              "adaptive_ratio": 16.213156601478314,
              "appearance_previous_mean": 9.43443489074707,
              "appearance_adaptive_ratio": 2.93157333239527
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.668473720550537,
          "discontinuity": 26.203233192706932,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 31.92552375793457
        },
        "decision": {
          "frame": 32177,
          "previous_frame": 32176,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 32177,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "aef36d571995e4573c15e27e1e502a1f3cb6e7949b4f5a95740d3d52d5d1c427",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              593.7746552303433,
              356.5039504766464,
              653.2855846807361,
              530.8091999292374
            ],
            [
              692.9607474636286,
              195.65382915735245,
              735.7922653127462,
              326.15767139196396
            ],
            [
              232.08829069510102,
              303.24540174007416,
              284.7796442992985,
              411.6873780488968
            ],
            [
              623.3392216488719,
              129.33169892430305,
              657.455764003098,
              178.95245870947838
            ],
            [
              992.052583836019,
              197.7088724374771,
              1048.2313483729959,
              294.9392753839493
            ],
            [
              1007.5671389736235,
              125.73182889819145,
              1041.5269561372697,
              173.69056299328804
            ],
            [
              967.8388310298324,
              121.46312493085861,
              1001.90935472399,
              211.7233299612999
            ],
            [
              771.862744146958,
              130.2296894788742,
              805.83372814022,
              178.63116443157196
            ]
          ],
          "detector_scores": [
            0.8936984361664861,
            0.872268076314083,
            0.6611659089370294,
            0.4944565183518006,
            0.4154929129025539,
            0.40986086639099134,
            0.399581787136175,
            0.3883718679824879
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
      "activity_interval": 190,
      "scene": 5,
      "participant_observation": 363,
      "format_decision": 1,
      "rally_start": 142,
      "rally_end": 84,
      "contact": 1858,
      "stroke": 905,
      "identity_ambiguity": 62,
      "broadcast_score": 956,
      "match_phase": 1,
      "shuttle_turn": 41,
      "highlight": 3
    },
    "live_counts": {
      "calibration": 1,
      "activity_interval": 190,
      "scene": 5,
      "participant_observation": 363,
      "format_decision": 1,
      "rally_start": 84,
      "rally_end": 84,
      "stroke": 885,
      "contact": 885,
      "identity_ambiguity": 62,
      "broadcast_score": 956,
      "match_phase": 1,
      "shuttle_turn": 41,
      "highlight": 3
    },
    "categories": {
      "event_status": {
        "confirmed": 3011,
        "provisional": 550
      },
      "rally_end_reason": {
        "stationary": 39,
        "gap": 39,
        "cut": 6
      },
      "rally_phase": {
        "unknown": 4,
        "match_play": 80
      },
      "rally_official": {
        "False": 44,
        "True": 40
      },
      "rally_match_format_known": {
        "True": 84
      },
      "rally_match_format": {
        "singles": 84
      },
      "rally_winner": {
        "None": 84
      },
      "rally_score_transition_status": {
        "unavailable": 57,
        "candidate": 27
      },
      "rally_admission_reason": {
        "duration_policy": 83,
        "independent_contact_and_observed_motion_witnesses": 1
      },
      "stroke_actor": {
        "unknown": 885
      },
      "stroke_physical_event_status": {
        "insufficient": 481,
        "ambiguous": 283,
        "probable": 121
      },
      "stroke_contact_status": {
        "estimated": 885
      },
      "stroke_classification_status": {
        "unknown": 670,
        "estimated": 215
      },
      "stroke_stroke": {
        "unknown": 670,
        "lift": 38,
        "push": 103,
        "net_shot": 25,
        "drop": 24,
        "smash": 5,
        "clear": 9,
        "drive": 11
      },
      "stroke_attribution_reason": {
        "nearest_proximity": 877,
        "ambiguous_proximity": 8
      },
      "stroke_classification_abstention_reason": {
        "missing_required_evidence": 668,
        "unresolved_initial_contact": 2
      },
      "contact_actor": {
        "unknown": 885
      },
      "contact_physical_event_status": {
        "insufficient": 481,
        "ambiguous": 283,
        "probable": 121
      },
      "contact_contact_status": {
        "estimated": 885
      },
      "contact_attribution_reason": {
        "nearest_proximity": 877,
        "ambiguous_proximity": 8
      },
      "contact_trajectory_reliability": {
        "probable": 480,
        "insufficient": 215,
        "ambiguous": 190
      },
      "contact_trajectory_reasons": {
        "supported_turn": 380,
        "coherent_motion_change_unavailable": 215,
        "supported_launch": 100,
        "association_unresolved": 190
      },
      "contact_impact_reliability": {
        "insufficient": 481,
        "ambiguous": 283,
        "probable": 121
      },
      "contact_impact_reasons": {
        "fresh_player_observation_unavailable": 481,
        "no_fresh_swing_or_racket_overlap": 34,
        "association_unresolved": 190,
        "coherent_motion_change_unavailable": 59,
        "coherent_motion_and_fresh_contact_cue": 121
      },
      "contact_attribution_reliability": {
        "insufficient": 613,
        "probable": 272
      },
      "contact_attribution_reasons": {
        "fresh_player_observation_unavailable": 613,
        "geometric_attribution_not_verified_identity": 272
      }
    },
    "physical_accuracy_validated": false
  },
  "ocr": {
    "readout_count": 1005,
    "label_counts": {
      "SHI Y.Q.": 1005,
      "CHRISTIE": 1005
    },
    "context_counts": {
      "{\"acquisition_policy\":\"main_camera\",\"actual_replay_status\":\"unknown\",\"analysis_excluded\":false,\"view\":\"main\"}": 1005
    },
    "previously_source_reviewed_branding_strings": {},
    "readouts": [
      {
        "f": 1320,
        "r": [
          [
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
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
        "f": 1350,
        "r": [
          [
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.94901,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.9466,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.94651,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.94951,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.94445,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95559,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95456,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.94776,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95346,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.96137,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95666,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95366,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.9529,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95592,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95549,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95444,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95447,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95527,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95948,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.9473,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.9462,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95707,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95729,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.94801,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.9557,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95503,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95503,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.9586,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95821,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.94618,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.94842,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95276,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.95842,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.95118,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.95353,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.89057,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.95521,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.78121,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.9465,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.95158,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.90741,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.83965,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.9123,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.87754,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.661,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.91335,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.91112,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.95549,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.86961,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.82917,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.94986,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.87846,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            3
          ]
        ],
        "c": 0.91099,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.9543,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95424,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95692,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.94347,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95647,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95633,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.96326,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.96312,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95178,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95148,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.94672,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.82255,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95586,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.89417,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95102,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95102,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.93122,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.93122,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95754,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95584,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95384,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95281,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95559,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95505,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95576,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95416,
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
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95682,
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
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95118,
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
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.94902,
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
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95102,
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
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.94538,
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
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.94577,
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
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.94794,
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
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95241,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95628,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95905,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.96225,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.96225,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95285,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95285,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95191,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95321,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95586,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95569,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95655,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95735,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.9512,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95125,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.85352,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.85007,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.88873,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.85893,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.91115,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.91115,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.87951,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.81245,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.86012,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.91557,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.93243,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.92635,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.92193,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.88695,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.88582,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.91554,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.90906,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.95544,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.88166,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.86061,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.69469,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95381,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95489,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.94426,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.94891,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.94891,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.94944,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.94904,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.94533,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.94735,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95934,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95794,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
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
        "f": 5370,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95604,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.94919,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95106,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96124,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96137,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95356,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95167,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95042,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96283,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.9508,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95874,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95714,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5730,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95717,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5760,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95602,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95267,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95847,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95874,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.96396,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.96198,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.9508,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.94834,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95304,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95312,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95111,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95214,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.96673,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95183,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94447,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94567,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94472,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94775,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95114,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95819,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.9577,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.9581,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95743,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95781,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95184,
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
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95171,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95181,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95861,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.9502,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.9502,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94831,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94831,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94784,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94567,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96246,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96246,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95654,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94805,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94163,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94163,
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
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95953,
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
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.97404,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.9574,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95779,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94832,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95095,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94608,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94608,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.99163,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96009,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96542,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96412,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94918,
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
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94918,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95265,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95183,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95445,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95718,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95073,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95392,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96714,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95042,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95179,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95206,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95428,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.9513,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95866,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95848,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95773,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95026,
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
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94376,
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
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.94582,
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
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95089,
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
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95583,
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
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96521,
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
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96495,
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
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96105,
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
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.9612,
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
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95543,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.9432,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95859,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.96161,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.9527,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95331,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95858,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95344,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95086,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95082,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.94755,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.945,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.9539,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95599,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
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
        "f": 8550,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95014,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95478,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95539,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95394,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95472,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95482,
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
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95424,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8760,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95383,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8790,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.94091,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8820,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.9472,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8850,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95612,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8880,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.96023,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8910,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95468,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8940,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.94336,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8970,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.94594,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9000,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95126,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9030,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.94906,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9060,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.94194,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9090,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.9468,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9120,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95451,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9150,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.95712,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9180,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.96518,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9210,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.96398,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9240,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            12
          ]
        ],
        "c": 0.96733,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9270,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95114,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9300,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96633,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9330,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96782,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9360,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95641,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9390,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.9581,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9420,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9450,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96045,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9480,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96634,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9510,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.94903,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9540,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.94651,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9570,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95135,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9600,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95359,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9630,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95128,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9660,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.94393,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9690,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.94414,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9720,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.9487,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9750,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.94962,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9780,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95415,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9810,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95497,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9840,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96228,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9870,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.9579,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9900,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95308,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9930,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95165,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9960,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95481,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9990,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.95664,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10020,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96224,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95361,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.95532,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.96268,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.96246,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.96888,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.9621,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.96583,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            2
          ]
        ],
        "c": 0.96407,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.96782,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.96545,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.96208,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95929,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.96017,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95506,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95576,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95595,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95404,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95399,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.9665,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.96531,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.96938,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.96766,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.95659,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            4
          ]
        ],
        "c": 0.9607,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.96281,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.96263,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.97162,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.97216,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.96186,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.96121,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95515,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.95321,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.96595,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            5
          ]
        ],
        "c": 0.96566,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.90621,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.86476,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.81398,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.81398,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.85885,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.85081,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.88427,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.82341,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.84658,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.89541,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.85683,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.85858,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.84927,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.84175,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.88232,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.88952,
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
            "SHI Y.Q.",
            0
          ],
          [
            "CHRISTIE",
            6
          ]
        ],
        "c": 0.96874,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96485,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.95421,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.94986,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96189,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.93776,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.92574,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.92574,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.9685,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96866,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96704,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.93297,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.9514,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.9514,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.94952,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.95512,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.9711,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.9695,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.94499,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.94499,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.95964,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.93498,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.91491,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.91008,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.9666,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.95237,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.86071,
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
            "SHI Y.Q.",
            2
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.86071,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.9695,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96643,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96916,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96781,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96599,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96418,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96868,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96861,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96648,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96648,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.94661,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.94753,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.95644,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.95678,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.95875,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96555,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96762,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.96762,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            7
          ]
        ],
        "c": 0.94516,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95606,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96238,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96238,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96349,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96359,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.9719,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.97229,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96801,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.9658,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96551,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.97118,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95228,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95205,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95509,
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
            "SHI Y.Q.",
            3
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96047,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96717,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.9676,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96402,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96397,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96514,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96439,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96142,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96201,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96611,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96594,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96586,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96676,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96059,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96019,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.9687,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96957,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96938,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96819,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96659,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96457,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96589,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96621,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.97078,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96608,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96338,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96026,
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
            "SHI Y.Q.",
            4
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96163,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96599,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95595,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.95645,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96135,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96084,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96905,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96905,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96296,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96393,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96372,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96576,
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
            "SHI Y.Q.",
            5
          ],
          [
            "CHRISTIE",
            8
          ]
        ],
        "c": 0.96711,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.76688,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.96678,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.966,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95829,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.95829,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.9704,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.9704,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.97006,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.97256,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            9
          ]
        ],
        "c": 0.97194,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.97317,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.83661,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.8859,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.83839,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.93714,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96817,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96624,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96944,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.97095,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.83737,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.95323,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96766,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96749,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.96794,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.84287,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.84664,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.8474,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            10
          ]
        ],
        "c": 0.80227,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.9595,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.96241,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.96377,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.96827,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.89435,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95789,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95597,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.97137,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95517,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.96049,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.95969,
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
            "SHI Y.Q.",
            6
          ],
          [
            "CHRISTIE",
            11
          ]
        ],
        "c": 0.96362,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96456,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96542,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96563,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96567,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.9641,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96782,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96782,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96832,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96876,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96834,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96833,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96701,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96701,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96363,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.97053,
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
            "SHI Y.Q.",
            7
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96608,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17667,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.9652,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17697,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96288,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17727,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            13
          ]
        ],
        "c": 0.96436,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17757,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.95991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17787,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.9727,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17817,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.97198,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17847,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.96773,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17877,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.96776,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17907,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.96833,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17937,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.96802,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17967,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.9658,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17997,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.96611,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18027,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.96297,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18057,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            14
          ]
        ],
        "c": 0.96412,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18087,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96146,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18117,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96729,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18147,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.9714,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18177,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96744,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18207,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96775,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18237,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96924,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18267,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96406,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18297,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96261,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18327,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96734,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18357,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96699,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18387,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96308,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18417,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96135,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18447,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96638,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18477,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96697,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18507,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.9648,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18537,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96713,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18567,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96677,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18597,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96137,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18627,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.96813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18657,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.9667,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18687,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.97,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18717,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.97,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18747,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            15
          ]
        ],
        "c": 0.9679,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18777,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96756,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18807,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96818,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18837,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.97218,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18867,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.97027,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18897,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.97382,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18927,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.97175,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18957,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.97171,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18987,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96921,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19017,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.9696,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19047,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96677,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19077,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96981,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19107,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96416,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19137,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96467,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19167,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96414,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19197,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96826,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19227,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96106,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19257,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.9637,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19287,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96564,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19317,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96758,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19347,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.97158,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19377,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96836,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19407,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96681,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19437,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            16
          ]
        ],
        "c": 0.96041,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19467,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            17
          ]
        ],
        "c": 0.95899,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19497,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            17
          ]
        ],
        "c": 0.95834,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19527,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            17
          ]
        ],
        "c": 0.96896,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19557,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            17
          ]
        ],
        "c": 0.95637,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19587,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            17
          ]
        ],
        "c": 0.96379,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19617,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            17
          ]
        ],
        "c": 0.96615,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19647,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            17
          ]
        ],
        "c": 0.97101,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19677,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            17
          ]
        ],
        "c": 0.9643,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19707,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "CHRISTIE",
            17
          ]
        ],
        "c": 0.97277,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19737,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            18
          ]
        ],
        "c": 0.96512,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19767,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            18
          ]
        ],
        "c": 0.9696,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19797,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            18
          ]
        ],
        "c": 0.96936,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19827,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            18
          ]
        ],
        "c": 0.96897,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19857,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            18
          ]
        ],
        "c": 0.9638,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19887,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            18
          ]
        ],
        "c": 0.96659,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19917,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            18
          ]
        ],
        "c": 0.96402,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19947,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            18
          ]
        ],
        "c": 0.96509,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19977,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "CHRISTIE",
            18
          ]
        ],
        "c": 0.96734,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20007,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96562,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20037,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96748,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20067,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.97092,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20097,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.97145,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20127,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96597,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20157,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96386,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20187,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.95742,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20217,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96938,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20247,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.97268,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20277,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96729,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20307,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96499,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20337,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96448,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20367,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96545,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20397,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96415,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20427,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96629,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20457,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96116,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20487,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96316,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20517,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.95728,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20547,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.9655,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20577,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96618,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20607,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96974,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20637,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96241,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20667,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96575,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20697,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96748,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20727,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96422,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20757,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96872,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20787,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.98164,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20817,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96749,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20847,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "CHRISTIE",
            19
          ]
        ],
        "c": 0.96545,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20877,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.95463,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20907,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.96565,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20937,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.96654,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20967,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.96318,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20997,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.96295,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21027,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.962,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21057,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.96545,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21087,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.96905,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21117,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.96849,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21147,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.97014,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21177,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.96769,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21207,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.96978,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21237,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            20
          ]
        ],
        "c": 0.97281,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21477,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96057,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21507,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96293,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21537,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96513,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21567,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9687,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21597,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9674,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21627,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96693,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21657,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96814,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21687,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98689,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21717,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96552,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21747,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96941,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21777,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97073,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21807,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21837,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96333,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21867,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96704,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21897,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96715,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21927,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96446,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21957,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96458,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21987,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97292,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22017,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97028,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22047,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22077,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96884,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22107,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96576,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22137,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96518,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22167,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96505,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22197,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96326,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22227,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96315,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22257,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96513,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22287,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96979,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22317,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
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
        "f": 22347,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96445,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22377,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96585,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22407,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96486,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22437,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9644,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22467,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96929,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22497,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.93929,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22527,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97506,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22557,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96965,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22587,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96819,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22617,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96787,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22647,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9673,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22677,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96756,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22707,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96877,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22737,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9694,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22767,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96381,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22797,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96509,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22827,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96613,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22857,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96613,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22887,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96426,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22917,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96706,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22947,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96682,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22977,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96648,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23007,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96295,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23037,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97115,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23067,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9692,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23097,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96871,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23127,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98047,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23157,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96609,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23187,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97158,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23217,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96503,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23247,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9657,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23277,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9657,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23307,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96662,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23337,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96669,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23367,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96942,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23397,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96904,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23427,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97097,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23457,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97258,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23487,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96747,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23517,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96204,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23547,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96368,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23577,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9649,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23607,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97062,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23637,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23667,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96995,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23697,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96561,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23727,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96453,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23757,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96485,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23787,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9676,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23817,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96811,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23847,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96712,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23877,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96661,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23907,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96925,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23937,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97805,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23967,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98794,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23997,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98295,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24027,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97103,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24057,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97077,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24087,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
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
        "f": 24117,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99252,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24147,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96905,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24177,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96757,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24207,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96752,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24237,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9676,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24267,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98918,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24297,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98884,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24327,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96293,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24357,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96404,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24387,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96747,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24417,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24447,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96999,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24477,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97064,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24507,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9894,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24537,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97231,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24567,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96328,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24597,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96401,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24627,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96457,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24657,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24687,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96832,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24717,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96952,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24747,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9644,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24777,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96409,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24807,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96241,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24837,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9616,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24867,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96485,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24897,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98829,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24927,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96725,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24957,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96695,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24987,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96857,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25017,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96881,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25047,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9703,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25077,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9694,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25107,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96572,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25137,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96404,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25167,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9666,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25197,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9644,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25227,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96673,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25257,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96599,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25287,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96494,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25317,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9639,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25347,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96597,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25377,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96431,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25407,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97265,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25437,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96357,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25467,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.964,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25497,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97184,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25527,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97501,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25557,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96968,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25587,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9698,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25617,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96628,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25647,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97059,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25677,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96753,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25707,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96423,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25737,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96673,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25767,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
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
        "f": 25797,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9712,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25827,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96916,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25857,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97045,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25887,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97096,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25917,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97001,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25947,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96785,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25977,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96781,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26007,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.8984,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26037,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96764,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26067,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96554,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26097,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96538,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26127,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96947,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26157,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96455,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26187,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96696,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26217,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96687,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26247,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96599,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26277,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96656,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26307,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
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
        "f": 26337,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96576,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26367,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96637,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26397,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96637,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26427,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96828,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26457,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96677,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26487,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97026,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26517,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97026,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26547,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96627,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26577,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96627,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26607,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96777,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26637,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96768,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26667,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96739,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26697,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96739,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26727,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96525,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26757,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96525,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26787,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96303,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26817,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97133,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26847,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96792,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26877,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96793,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26907,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96869,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26937,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9679,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26967,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96604,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26997,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97866,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27027,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97062,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27057,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97482,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27087,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98024,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27117,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98954,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27147,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96336,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27215,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96515,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27245,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98145,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27275,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97802,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27305,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96421,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27335,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96531,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27365,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96773,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27395,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96924,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27425,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97896,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27455,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97097,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27485,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96769,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27515,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96946,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27545,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96684,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27575,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96647,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27605,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96375,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27635,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96375,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27665,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96602,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27695,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96725,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27725,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96642,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27755,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96104,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27785,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96019,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27815,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9615,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27845,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96891,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27875,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9654,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27905,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9684,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27935,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9703,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27965,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96736,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27995,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9672,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28025,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96925,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28055,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97018,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28085,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96775,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28115,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9671,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28145,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97234,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28175,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97247,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28205,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96634,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28235,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96582,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28265,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96686,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28295,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96709,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28385,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97028,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28415,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96983,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28445,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96758,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28475,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96154,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28505,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99117,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28535,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.91954,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28565,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96924,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28595,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96849,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28625,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98737,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28655,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9622,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28685,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9672,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28715,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96747,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28745,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9729,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28775,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96766,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28805,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96769,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28835,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99093,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28865,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28895,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28925,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98927,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28955,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96495,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28985,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96431,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29015,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96456,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29045,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96775,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29075,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96666,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29105,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96915,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29135,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96915,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29165,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29195,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9681,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29225,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96825,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29255,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96518,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29285,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96798,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29315,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96948,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29345,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96436,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29375,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96677,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29405,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96745,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29435,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96786,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29465,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98895,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29495,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96667,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29525,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9684,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29555,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29585,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96633,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29615,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96697,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29645,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
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
        "f": 29675,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99002,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29705,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99141,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29735,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99034,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29765,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97229,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29795,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97207,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29825,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96843,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29855,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99019,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29885,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96598,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29915,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96328,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29945,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96494,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29975,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96481,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30005,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96545,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30035,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96959,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30065,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96732,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30095,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96823,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30125,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30155,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.965,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30185,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96941,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30215,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96896,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30245,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96652,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30275,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96652,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30305,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99013,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30335,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98911,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30365,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96763,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30395,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9676,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30425,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96408,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30455,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96429,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30485,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96052,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30515,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96083,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30545,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9641,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30575,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96454,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30605,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96669,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30635,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96432,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30665,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96781,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30695,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96834,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30725,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96766,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30755,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96858,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30785,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96623,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30815,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9667,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30845,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96902,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30875,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96821,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30905,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96694,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30935,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96443,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30965,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96407,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30995,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96477,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31025,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96949,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31055,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96706,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31085,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96367,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31115,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96364,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31145,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9702,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31175,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96924,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31205,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.79326,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31235,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.91742,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31265,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96802,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31295,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
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
        "f": 31325,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
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
        "f": 31355,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99008,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31385,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96864,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31415,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97001,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31445,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96618,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31475,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9679,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31505,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.968,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31535,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9671,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31565,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9675,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31595,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96875,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31625,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96912,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31655,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96907,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31685,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9709,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31715,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96734,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31745,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97094,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31775,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97234,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31805,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96882,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31835,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96561,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31865,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98821,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31895,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96296,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31925,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96416,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31955,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9646,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31985,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96204,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32015,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96272,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32045,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.95684,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32075,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.95717,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32105,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96679,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32135,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96805,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32165,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.95317,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32195,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96994,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32225,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96561,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32255,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96348,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32285,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98439,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32315,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96032,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32345,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99051,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32375,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96898,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32405,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96711,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32435,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96412,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32465,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97011,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32495,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96644,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32525,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
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
        "f": 32555,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.99199,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32585,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9667,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32615,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96616,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32645,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96409,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32675,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96536,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32705,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97184,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32735,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97161,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32765,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.97291,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32795,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96545,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32825,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96509,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32855,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.98879,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32885,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96787,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32915,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96832,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32945,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9665,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32975,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96632,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33005,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96418,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33035,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96678,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33065,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96958,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33095,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.9687,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33125,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96792,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33155,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "CHRISTIE",
            21
          ]
        ],
        "c": 0.96585,
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
      "camera_rows": 33157,
      "player_rows": 63784,
      "nonfinite_projected_court_rows": 0,
      "player_projected_court_rows": 63046,
      "projected_court_on_propagated_box": 37226,
      "racket_rows": 23601,
      "shuttle_rows": 33157
    },
    "categories": {
      "player_id": {
        "None": 63784
      },
      "detector_matched": {
        "True": 26147,
        "False": 37637
      }
    },
    "invalid_geometry_frame_count": 975,
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
