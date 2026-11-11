# Test 10 evaluation

Status: completed fresh end-to-end inference; unchanged pipeline and predictions. Comparison measures agreement with the supplied legacy rally CSV. Independent physical component accuracy is unavailable without reviewed component labels.

| Input / provenance | Value |
|---|---|
| Drive file | Test_10.mp4 (1Zr3JVT1ICpJlFqGE9r7sUaxmrfwWQ72l) |
| Video SHA256 | `cf71d8e02086df5e192e3cf834804407ca5d9e0f2f6bdf26512b39b6b264214f` |
| Annotation | `/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test10_Full/Test10_Full_rally.csv` |
| Annotation SHA256 | `509cabed282eac89217d41a7d1b860991456f5d09cab24bb58b2acaba824d0cf` |
| Reference rows | 93 |
| Canonical frames / FPS | 37133 / 30.0 |
| Frozen bindings | [Source, profile, manifest, model lock](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/frozen_pipeline.json) |

| Detection / overlap | Value |
|---|---|
| ground_truth_count | 93 |
| predicted_count | 98 |
| matched_count | 85 |
| true_positives | 85 |
| false_positives | 13 |
| false_negatives | 8 |
| precision | 0.867347 |
| recall | 0.913978 |
| f1 | 0.890052 |
| mean_iou | 0.844965 |
| median_iou | 0.895425 |
| minimum_iou | 0.510067 |
| percent_strictly_exceeding | {'0.5': 100.0, '0.75': 78.82352941176471, '0.9': 48.23529411764706, '0.95': 23.529411764705884} |

Boundary and duration statistics condition on matched intervals; all missed rallies and false detections remain in detection metrics. Signed errors are prediction minus reference. Matching: IoU ≥ 0.5, maximum cardinality then total IoU; zero-origin half-open frame intervals.

| Error | MAE | Median absolute | RMSE | P90 absolute | Maximum absolute | Signed bias |
|---|---|---|---|---|---|---|
| start_frame | 23.988235 | 7.000000 | 50.296415 | 52.800000 | 206.000000 | 15.658824 |
| end_frame | 18.058824 | 7.000000 | 30.619678 | 45.600000 | 136.000000 | -10.341176 |
| start_time_sec | 0.799608 | 0.233333 | 1.676547 | 1.760000 | 6.866667 | 0.521961 |
| end_time_sec | 0.601961 | 0.233333 | 1.020656 | 1.520000 | 4.533333 | -0.344706 |
| duration_sec | 1.227451 | 0.600000 | 2.052227 | 3.180000 | 7.433333 | -0.866667 |

| Boundary tolerance | Within / matched | Within / all reference |
|---|---|---|
| start ±1 frames | 7 / 85 (0.082353) | 7 / 93 (0.075269) |
| start ±3 frames | 15 / 85 (0.176471) | 15 / 93 (0.161290) |
| start ±5 frames | 32 / 85 (0.376471) | 32 / 93 (0.344086) |
| start ±10 frames | 54 / 85 (0.635294) | 54 / 93 (0.580645) |
| start ±15 frames | 62 / 85 (0.729412) | 62 / 93 (0.666667) |
| start ±30 frames | 69 / 85 (0.811765) | 69 / 93 (0.741935) |
| end ±1 frames | 10 / 85 (0.117647) | 10 / 93 (0.107527) |
| end ±3 frames | 17 / 85 (0.200000) | 17 / 93 (0.182796) |
| end ±5 frames | 32 / 85 (0.376471) | 32 / 93 (0.344086) |
| end ±10 frames | 46 / 85 (0.541176) | 46 / 93 (0.494624) |
| end ±15 frames | 57 / 85 (0.670588) | 57 / 93 (0.612903) |
| end ±30 frames | 70 / 85 (0.823529) | 70 / 93 (0.752688) |

Missed rally IDs: [9, 15, 30, 37, 40, 43, 55, 85].

| False detection ID | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| 28 | 11073 | 11131 | 369.100000 | 371.033333 |
| 32 | 12209 | 12280 | 406.966667 | 409.333333 |
| 33 | 12313 | 12471 | 410.433333 | 415.700000 |
| 37 | 14065 | 14227 | 468.833333 | 474.233333 |
| 40 | 15556 | 15657 | 518.533333 | 521.900000 |
| 43 | 16643 | 17055 | 554.766667 | 568.500000 |
| 44 | 17174 | 17340 | 572.466667 | 578.000000 |
| 45 | 17376 | 17655 | 579.200000 | 588.500000 |
| 61 | 24185 | 24347 | 806.166667 | 811.566667 |
| 68 | 26206 | 26355 | 873.533333 | 878.500000 |
| 85 | 32693 | 32831 | 1089.766667 | 1094.366667 |
| 89 | 34122 | 34223 | 1137.400000 | 1140.766667 |
| 90 | 34246 | 34335 | 1141.533333 | 1144.500000 |

| Runtime / resources | Value |
|---|---|
| parent_completed_elapsed_s | 4433.866512 |
| worker_elapsed_s | 4421.865935 |
| worker_source_fps | 8.397586 |
| media_ready_time_s | 2.797784 |
| model_staging_time_s | 1.758922 |
| component_initialization_including_models_s | 8.983048 |
| worker_final_cpu_s | 45227.636703 |
| worker_maxrss_bytes | 2881126400 |
| sampled_worker_tree_peak_rss_bytes | 3048800256 |
| sampled_worker_gpu_peak_mib | 2124 |
| sampled_cpu_seconds_max_observed | 45227.040000 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| sample_count | 2140 |
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
      "frames": 37133,
      "raw_shuttle_present": 25049,
      "detector_executed_frames": 15535,
      "person_rows": 72858,
      "scene_telemetry_present": 3649,
      "scene_raw_hypotheses": 54,
      "actual_content_epoch_increments": 53,
      "content_epoch_decreases": 0,
      "detailed_diagnostic_frames": 3600,
      "person_current_detector_matches": 30799,
      "person_propagated_or_unmatched": 42059,
      "pose_present_rows": 58682,
      "pose_current_source_rows": 58682,
      "pose_present_without_current_source": 0,
      "pose_current_on_propagated_box": 27883,
      "racket_present_rows": 27103,
      "racket_current_source_rows": 27103,
      "racket_present_without_current_source": 0,
      "racket_current_on_propagated_box": 0,
      "scene_decision_records": 54,
      "scene_positive_correspondence_vetoes": 1,
      "scene_current_detector_probes": 54
    },
    "categories": {
      "view": {
        "main": 36787,
        "none": 346
      },
      "calibration_state": {
        "REACQUIRING": 48,
        "VALID": 36739,
        "LOST": 346
      },
      "player_population": {
        "0": 511,
        "2": 36236,
        "1": 386
      },
      "association_status": {
        "missing": 11738,
        "observed": 25028,
        "invalid": 346,
        "ambiguous": 21
      },
      "association_reason": {
        "no_accepted_raw_observation": 11738,
        "fresh_selection_retained": 25028,
        "image_view_invalid": 346,
        "coobserved_competing_static_hypothesis": 21
      },
      "scene_raw_status": {
        "unknown": 108,
        "measured": 3487,
        "hypothesis": 54
      },
      "person_detector_match": {
        "True": 30799,
        "False": 42059
      },
      "person_identity_method": {
        "bytetrack_v1": 72858
      },
      "scene_decision": {
        "barrier": 53,
        "no_barrier": 1
      },
      "scene_decision_reason": {
        "raw_change_and_current_layout_discontinuity": 53,
        "complete_current_layout_correspondence": 1
      }
    },
    "scene_records": [
      {
        "frame": 593,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 1,
        "raw": {
          "frame": 593,
          "previous_frame": 592,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 592,
                "key": "track:0",
                "bbox": [
                  244.64588928222656,
                  477.9393005371094,
                  323.2628479003906,
                  717.46630859375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 63,
              "consistent_fraction": 0.14285714285714285,
              "median_patch_error": 32.31986999511719,
              "median_forward_backward_error": 7.876485824584961,
              "discontinuity": 27.702745710100448,
              "previous_mean": 0.0,
              "adaptive_ratio": 27.702745710100448,
              "appearance_previous_mean": 11.420422077178955,
              "appearance_adaptive_ratio": 2.8300066124264265
            },
            {
              "region": {
                "frame": 592,
                "key": "track:2",
                "bbox": [
                  629.0388793945312,
                  179.83749389648438,
                  682.81201171875,
                  303.5419006347656
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 30,
              "consistent_fraction": 0.8333333333333334,
              "median_patch_error": 24.140625,
              "median_forward_backward_error": 0.19526314735412598,
              "discontinuity": 4.023437499999999,
              "previous_mean": 0.0,
              "adaptive_ratio": 4.023437499999999,
              "appearance_previous_mean": 8.756962299346924,
              "appearance_adaptive_ratio": 2.756735061175307
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.9486961364746094,
          "discontinuity": 15.863091605050224,
          "photometric_gain": 1.0087719298245614,
          "photometric_offset": -0.7105263157894797,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 28.230247497558594
        },
        "decision": {
          "frame": 593,
          "previous_frame": 592,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 593,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "d417640df440980d72c1baa104a71077692512a33594207da13b570af8df6368",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              479.4250639677048,
              355.7386336028576,
              567.8696652650833,
              553.1384820044041
            ],
            [
              627.3487977981567,
              195.78595440089703,
              676.1723718643188,
              331.1246266514063
            ],
            [
              233.02545255422592,
              303.963522605598,
              282.15851241350174,
              405.19974387437105
            ],
            [
              999.25789514184,
              194.42712596803904,
              1048.7969525754452,
              292.5650730654597
            ],
            [
              960.4897519052029,
              117.10298325121403,
              1001.3731230795383,
              204.42784498631954
            ],
            [
              476.8726178109646,
              133.06912225857377,
              511.00239554047585,
              181.73300088569522
            ],
            [
              769.8300335109234,
              129.56085947528481,
              803.7765090763569,
              179.44904961809516
            ],
            [
              318.86852648854256,
              120.45328705757856,
              348.15792939066887,
              179.98154773563147
            ],
            [
              621.7608039677143,
              126.6183906905353,
              657.7328626811504,
              178.84098109975457
            ],
            [
              1004.0803668498993,
              124.95417627692223,
              1039.096831560135,
              212.2138071358204
            ]
          ],
          "detector_scores": [
            0.9094741351258137,
            0.9031460271392897,
            0.8670279535766359,
            0.7589070143557927,
            0.7232175596966981,
            0.5472950174422313,
            0.5312306286431685,
            0.5091793950987067,
            0.4841398774240056,
            0.3676187322749823
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
        "frame": 1253,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 2,
        "raw": {
          "frame": 1253,
          "previous_frame": 1252,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 1252,
                "key": "track:0",
                "bbox": [
                  953.4678955078125,
                  498.3719482421875,
                  1048.8846435546875,
                  648.030517578125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 45,
              "consistent_fraction": 0.1111111111111111,
              "median_patch_error": 23.222009658813477,
              "median_forward_backward_error": 8.495440483093262,
              "discontinuity": 20.641786363389755,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.641786363389755,
              "appearance_previous_mean": 4.764916181564331,
              "appearance_adaptive_ratio": 4.873540010768804
            },
            {
              "region": {
                "frame": 1252,
                "key": "track:1",
                "bbox": [
                  655.5823364257812,
                  169.04940795898438,
                  714.3116455078125,
                  296.45245361328125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 30,
              "consistent_fraction": 0.9666666666666667,
              "median_patch_error": 17.157276153564453,
              "median_forward_backward_error": 0.12284485995769501,
              "discontinuity": 0.5719092051188149,
              "previous_mean": 0.0,
              "adaptive_ratio": 0.5719092051188149,
              "appearance_previous_mean": 4.825467586517334,
              "appearance_adaptive_ratio": 3.5555675892431613
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 2.006093978881836,
          "discontinuity": 10.606847784254285,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 20.189642906188965
        },
        "decision": {
          "frame": 1253,
          "previous_frame": 1252,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 1253,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "0240dad901d785a1cbe87a25480a5e73fc575712c322f0184abc7c220a410953",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              613.8427478075027,
              333.384109467268,
              690.2409619092941,
              528.2179045975208
            ],
            [
              544.1119660139084,
              211.77386528998613,
              605.8999701738358,
              332.4979162141681
            ],
            [
              960.8519803881645,
              117.68166671693325,
              1001.8850057721138,
              206.64943377673626
            ],
            [
              998.1203182637691,
              195.7123199403286,
              1048.9716064035892,
              292.3901786208153
            ],
            [
              769.5614076852798,
              129.75386928021908,
              803.5860952138901,
              179.3940253853798
            ],
            [
              621.6182052195072,
              127.23242282122374,
              657.2912777364254,
              179.59601841121912
            ],
            [
              318.8394641280174,
              119.95938860997558,
              348.2588170170784,
              179.93571979179978
            ],
            [
              477.0774952173233,
              133.0302522443235,
              510.54815423488617,
              181.45214979723096
            ]
          ],
          "detector_scores": [
            0.9175092905622856,
            0.890341628336454,
            0.6627023572766944,
            0.5705621018050285,
            0.45440477357780806,
            0.44326490514539774,
            0.41851981639431657,
            0.4163129224245696
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
        "frame": 2116,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 3,
        "raw": {
          "frame": 2116,
          "previous_frame": 2115,
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
                "frame": 2115,
                "key": "track:4",
                "bbox": [
                  740.204833984375,
                  298.76416015625,
                  814.3247680664062,
                  466.4183654785156
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 36,
              "consistent_fraction": 0.027777777777777776,
              "median_patch_error": 22.203868865966797,
              "median_forward_backward_error": 13.076128005981445,
              "discontinuity": 21.587094730801052,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.587094730801052,
              "appearance_previous_mean": 4.0447138249874115,
              "appearance_adaptive_ratio": 5.489601941377374
            },
            {
              "region": {
                "frame": 2115,
                "key": "track:6",
                "bbox": [
                  554.122802734375,
                  225.94894409179688,
                  595.7113037109375,
                  365.6016845703125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.4230769230769231,
              "median_patch_error": 18.344493865966797,
              "median_forward_backward_error": 5.707169532775879,
              "discontinuity": 10.583361845750074,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.583361845750074,
              "appearance_previous_mean": 4.70075099915266,
              "appearance_adaptive_ratio": 3.902460238645592
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 3.491567611694336,
          "discontinuity": 16.085228288275562,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7043478260869591,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 20.274181365966797
        },
        "decision": {
          "frame": 2116,
          "previous_frame": 2115,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2116,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "279138bf7d8f233bdd748ebd7f8c711b92e764f6d4c1328aa9e36358a7ebb331",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              581.1094285845757,
              340.9837814718485,
              662.9917820096016,
              534.4100816100836
            ],
            [
              682.2232097387314,
              205.74115934967995,
              738.8818660974503,
              333.22545859217644
            ],
            [
              997.2224614024162,
              195.26708576083183,
              1048.9342635273933,
              293.3420655429363
            ],
            [
              959.6809850633144,
              116.66799008101225,
              1001.449119001627,
              208.88064040988684
            ],
            [
              621.8637784421444,
              127.01866981759667,
              657.4864565432072,
              179.13364486023784
            ],
            [
              477.0853364765644,
              133.26974065229297,
              510.6386091411114,
              180.63289654627442
            ],
            [
              769.21216994524,
              129.84882428497076,
              804.4148003458977,
              179.23484756797552
            ],
            [
              319.16828176379204,
              120.02659208327532,
              347.9058144390583,
              179.77707578986883
            ],
            [
              1007.561873793602,
              121.56321085244417,
              1043.8876692056656,
              204.19115624576807
            ],
            [
              233.04114571213722,
              309.0569790750742,
              260.0327055156231,
              363.08722446858883
            ],
            [
              233.16798746585846,
              309.0477965325117,
              282.4303072690964,
              402.14644308388233
            ]
          ],
          "detector_scores": [
            0.9388404044484926,
            0.9066642592157029,
            0.7629742435895142,
            0.7432779376211442,
            0.558967041081856,
            0.5344967276988662,
            0.5220625097221809,
            0.4919813594385119,
            0.45052404576921173,
            0.41101667209120707,
            0.388453990086924
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
        "frame": 2441,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 4,
        "raw": {
          "frame": 2441,
          "previous_frame": 2440,
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
                "frame": 2440,
                "key": "track:0",
                "bbox": [
                  595.7941284179688,
                  316.53369140625,
                  657.6397094726562,
                  499.83087158203125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 43,
              "consistent_fraction": 0.27906976744186046,
              "median_patch_error": 30.538476943969727,
              "median_forward_backward_error": 2.9016599655151367,
              "discontinuity": 22.016111285187474,
              "previous_mean": 0.0,
              "adaptive_ratio": 22.016111285187474,
              "appearance_previous_mean": 7.464250326156616,
              "appearance_adaptive_ratio": 4.091298604624124
            },
            {
              "region": {
                "frame": 2440,
                "key": "track:1",
                "bbox": [
                  513.7794189453125,
                  229.728515625,
                  568.0587768554688,
                  367.5592956542969
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 29,
              "consistent_fraction": 0.06896551724137931,
              "median_patch_error": 26.345521926879883,
              "median_forward_backward_error": 12.443619728088379,
              "discontinuity": 24.52858938019851,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.52858938019851,
              "appearance_previous_mean": 5.853387117385864,
              "appearance_adaptive_ratio": 4.500902024509504
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.0741920471191406,
          "discontinuity": 23.272350332692994,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 28.441999435424805
        },
        "decision": {
          "frame": 2441,
          "previous_frame": 2440,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 2441,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6479e853fad3f98882324d194cfe9ddd0b5d03c1b07e4f423ccce383938a6aa9",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              613.941043972969,
              336.71964514255524,
              691.6330126523972,
              530.4742990732193
            ],
            [
              546.0767645835876,
              196.8289611041546,
              606.5801215171814,
              332.5607231557369
            ],
            [
              960.7743824720383,
              116.05714022368193,
              1002.0965510606766,
              208.11143293231726
            ],
            [
              997.9602951705456,
              195.76000134646893,
              1048.8920417129993,
              292.06031273305416
            ],
            [
              769.2630948126316,
              129.87368908897042,
              804.205901235342,
              179.31832210347056
            ],
            [
              621.6049074530602,
              127.15485233068466,
              657.2364831566811,
              180.3074409365654
            ],
            [
              233.054046779871,
              311.41415928676724,
              259.4406486451626,
              363.77329648658633
            ],
            [
              477.20599216222763,
              132.8606867901981,
              510.9848237633705,
              180.70083086565137
            ],
            [
              318.9756366610527,
              119.71571673825383,
              347.99489837884903,
              179.94815104827285
            ],
            [
              1006.7107924222946,
              121.36175851523876,
              1043.8713513612747,
              202.18652564287186
            ]
          ],
          "detector_scores": [
            0.9110649482176777,
            0.9049934669893357,
            0.7859204699497124,
            0.6834431097910179,
            0.6030360123301776,
            0.5902877921282371,
            0.5167850341269057,
            0.513287395217508,
            0.5108824468984579,
            0.4680118558825521
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
        "frame": 4147,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 5,
        "raw": {
          "frame": 4147,
          "previous_frame": 4146,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 4146,
                "key": "track:0",
                "bbox": [
                  686.2717895507812,
                  380.9805908203125,
                  750.7354736328125,
                  580.61865234375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 43,
              "consistent_fraction": 0.16279069767441862,
              "median_patch_error": 25.16680908203125,
              "median_forward_backward_error": 6.038288116455078,
              "discontinuity": 21.069886673328487,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.069886673328487,
              "appearance_previous_mean": 4.843006111681461,
              "appearance_adaptive_ratio": 5.196526393251545
            },
            {
              "region": {
                "frame": 4146,
                "key": "track:2",
                "bbox": [
                  865.5111694335938,
                  126.83805084228516,
                  911.86181640625,
                  229.06060791015625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 19,
              "consistent_fraction": 1.0,
              "median_patch_error": 17.417375564575195,
              "median_forward_backward_error": 0.07282648235559464,
              "discontinuity": 0.0,
              "previous_mean": 0.0,
              "adaptive_ratio": 0.0,
              "appearance_previous_mean": 4.062411338090897,
              "appearance_adaptive_ratio": 4.2874475563964864
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.023242473602295,
          "discontinuity": 10.534943336664243,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 21.292092323303223
        },
        "decision": {
          "frame": 4147,
          "previous_frame": 4146,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 4147,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "cef0e0aab9439f6e5e1879516a80b8c1d792554e43c24ce87b426bad9d6cd9ee",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              484.46685230731964,
              352.524203017354,
              568.1718128919601,
              539.4679580181837
            ],
            [
              619.238613307476,
              205.359208650887,
              675.7257803082466,
              333.26045214384794
            ],
            [
              960.2048568725586,
              116.73563572764397,
              1000.0446186065674,
              206.60188983380795
            ],
            [
              998.3399738371372,
              195.25471407175064,
              1049.0,
              292.5424695312977
            ],
            [
              769.1407216191292,
              129.4071824774146,
              804.2210776209831,
              179.18479263037443
            ],
            [
              233.0755399465561,
              304.5198591351509,
              262.6168450117111,
              363.67860037088394
            ],
            [
              621.8101648390293,
              126.66899318993092,
              657.4200330674648,
              178.82924403250217
            ],
            [
              476.9091566503048,
              132.77185806259513,
              510.73458591103554,
              181.0659973062575
            ],
            [
              318.9443780183792,
              120.16156033799052,
              347.94374096393585,
              179.88982540741563
            ],
            [
              1003.4774334430695,
              124.22603364288807,
              1038.7908294200897,
              210.27436617016792
            ],
            [
              233.0,
              304.7793667688966,
              283.5868557691574,
              404.4080932363868
            ]
          ],
          "detector_scores": [
            0.9365316692275554,
            0.8996805612773047,
            0.7232317815753276,
            0.6239162128313339,
            0.5869082238461723,
            0.533497389005882,
            0.5287544198401647,
            0.5068653083350971,
            0.49787248464928485,
            0.4130658802650212,
            0.35279961368985935
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
        "frame": 4665,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 6,
        "raw": {
          "frame": 4665,
          "previous_frame": 4664,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 4664,
                "key": "track:2",
                "bbox": [
                  583.8019409179688,
                  344.3742980957031,
                  674.7523803710938,
                  539.4570922851562
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 42,
              "consistent_fraction": 0.23809523809523808,
              "median_patch_error": 29.484304428100586,
              "median_forward_backward_error": 7.897126197814941,
              "discontinuity": 22.464231945219492,
              "previous_mean": 0.0,
              "adaptive_ratio": 22.464231945219492,
              "appearance_previous_mean": 6.062092833220959,
              "appearance_adaptive_ratio": 4.8637170758130335
            },
            {
              "region": {
                "frame": 4664,
                "key": "track:3",
                "bbox": [
                  710.6587524414062,
                  194.37718200683594,
                  753.8792724609375,
                  325.7758483886719
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 29,
              "consistent_fraction": 0.7241379310344828,
              "median_patch_error": 16.887968063354492,
              "median_forward_backward_error": 0.33171942830085754,
              "discontinuity": 4.65874981058055,
              "previous_mean": 0.19229497512181584,
              "adaptive_ratio": 4.65874981058055,
              "appearance_previous_mean": 4.669005140662193,
              "appearance_adaptive_ratio": 3.6170377959702384
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.139810085296631,
          "discontinuity": 13.56149087790002,
          "photometric_gain": 1.0087719298245614,
          "photometric_offset": -0.7105263157894797,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 23.18613624572754
        },
        "decision": {
          "frame": 4665,
          "previous_frame": 4664,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 4665,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "16ea2f67e5a84d94f3535e4e64930837c03caedf13fd24a495adc2baa72110de",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              616.4220585227013,
              344.11199513077736,
              700.1496902108192,
              533.0452093780041
            ],
            [
              553.9023671448231,
              197.4909656047821,
              602.4463400542736,
              333.51477283239365
            ],
            [
              960.9075455665588,
              116.75708915293217,
              1001.4808077812195,
              207.16720271110535
            ],
            [
              997.7325855493546,
              195.41449672728777,
              1048.9313300848007,
              292.3881670758128
            ],
            [
              768.9102943837643,
              129.69059496372938,
              804.7892428934574,
              179.23608473688364
            ],
            [
              233.02995151281357,
              312.3020502105355,
              282.1177907586098,
              400.4767920002341
            ],
            [
              621.7175273299217,
              126.96789778023958,
              657.6294489502907,
              179.52906466275454
            ],
            [
              476.81014612317085,
              133.10882392525673,
              511.01394388079643,
              180.98402570188046
            ],
            [
              319.17486453056335,
              119.92217502743006,
              347.7957191467285,
              179.95709761232138
            ]
          ],
          "detector_scores": [
            0.9330418791744423,
            0.9115399112889493,
            0.7184343969367422,
            0.6618344100129828,
            0.5655880290025217,
            0.555475145825559,
            0.5483702479376252,
            0.470659149118121,
            0.37692986463161077
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
        "frame": 6573,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 7,
        "raw": {
          "frame": 6573,
          "previous_frame": 6572,
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
                "frame": 6572,
                "key": "track:0",
                "bbox": [
                  632.2188720703125,
                  305.61181640625,
                  697.0269165039062,
                  489.4652099609375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 46,
              "consistent_fraction": 0.1956521739130435,
              "median_patch_error": 29.56639862060547,
              "median_forward_backward_error": 8.555028915405273,
              "discontinuity": 23.7816684557044,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.7816684557044,
              "appearance_previous_mean": 3.061844438314438,
              "appearance_adaptive_ratio": 9.656401301981864
            },
            {
              "region": {
                "frame": 6572,
                "key": "track:1",
                "bbox": [
                  697.31201171875,
                  223.2177734375,
                  745.2183227539062,
                  366.4092102050781
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 24,
              "consistent_fraction": 0.16666666666666666,
              "median_patch_error": 28.64834976196289,
              "median_forward_backward_error": 10.942153930664062,
              "discontinuity": 23.873624801635742,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.873624801635742,
              "appearance_previous_mean": 3.0707553438842297,
              "appearance_adaptive_ratio": 9.329414607718407
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.1343894004821777,
          "discontinuity": 23.82764662867007,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7043478260869591,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 29.10737419128418
        },
        "decision": {
          "frame": 6573,
          "previous_frame": 6572,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 6573,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "51f789fd0011b7e7355f8e1450861d8ee79b6e0939c68f2c81795d99f6848526",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              675.0276604890823,
              348.8557955920696,
              746.5690420866013,
              545.3040319979191
            ],
            [
              600.4934348464012,
              206.34026984870434,
              652.564788877964,
              336.78294236958027
            ],
            [
              960.9475255012512,
              117.29244879633188,
              999.012460231781,
              208.49260925501585
            ],
            [
              997.643275141716,
              195.19971045851707,
              1048.8093596696854,
              291.961843252182
            ],
            [
              769.4095708727837,
              129.93435847759247,
              804.5775106549263,
              178.86239099502563
            ],
            [
              233.0735503733158,
              305.58606504648924,
              282.84310951828957,
              400.66749013215303
            ],
            [
              621.1418080627918,
              126.99803658947349,
              658.087222546339,
              180.0999883301556
            ],
            [
              477.21274212002754,
              133.0435266084969,
              510.7531745135784,
              180.86169489845634
            ],
            [
              318.96030828356743,
              120.01400503516197,
              347.9255976974964,
              179.80830284953117
            ],
            [
              1003.1790658533573,
              123.69450922310352,
              1040.971853107214,
              201.68165992200375
            ]
          ],
          "detector_scores": [
            0.9301078337896483,
            0.8920118409784229,
            0.7417047982121187,
            0.6982704836647908,
            0.6276852597740166,
            0.5941398048067313,
            0.5809204008763483,
            0.5589384759272832,
            0.5275362781521719,
            0.4964758741317516
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
        "frame": 8034,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 8,
        "raw": {
          "frame": 8034,
          "previous_frame": 8033,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 8033,
                "key": "track:3",
                "bbox": [
                  769.8992919921875,
                  331.72540283203125,
                  819.642822265625,
                  518.9580078125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 33,
              "consistent_fraction": 0.030303030303030304,
              "median_patch_error": 21.51622772216797,
              "median_forward_backward_error": 13.922897338867188,
              "discontinuity": 20.86422082149621,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.86422082149621,
              "appearance_previous_mean": 4.4086772836744785,
              "appearance_adaptive_ratio": 4.880427016475777
            },
            {
              "region": {
                "frame": 8033,
                "key": "track:2",
                "bbox": [
                  703.6588745117188,
                  160.41539001464844,
                  743.4014282226562,
                  283.3052062988281
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 24,
              "consistent_fraction": 0.7916666666666666,
              "median_patch_error": 29.299213409423828,
              "median_forward_backward_error": 0.39117658138275146,
              "discontinuity": 6.104002793629966,
              "previous_mean": 0.0,
              "adaptive_ratio": 6.104002793629966,
              "appearance_previous_mean": 4.499362006783485,
              "appearance_adaptive_ratio": 6.511859540363884
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.0268211364746094,
          "discontinuity": 13.484111807563089,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": -0.28695652173912833,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 25.4077205657959
        },
        "decision": {
          "frame": 8034,
          "previous_frame": 8033,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 8034,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "0b5707beb255ece943b40fe7aa52902b3b575a5f1cc3833f8648a4c35a8f0bfb",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              578.8261371850967,
              343.34358493983746,
              661.7811578512192,
              536.4902299195528
            ],
            [
              685.5479006171227,
              213.50673570483923,
              749.9306913018227,
              333.60129676014185
            ],
            [
              996.6096637248993,
              195.58055228739977,
              1048.8766434192657,
              293.4431514069438
            ],
            [
              961.9764023721218,
              116.94373670220375,
              999.282979875803,
              206.74107591807842
            ],
            [
              233.0424543619156,
              308.67232264205813,
              259.63820004463196,
              361.6586861498654
            ]
          ],
          "detector_scores": [
            0.9363195303604811,
            0.911965659677768,
            0.8222513040431165,
            0.6775068360168078,
            0.4140294374354806
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
        "frame": 8542,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 9,
        "raw": {
          "frame": 8542,
          "previous_frame": 8541,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 8541,
                "key": "track:2",
                "bbox": [
                  636.454345703125,
                  380.2024841308594,
                  706.7210083007812,
                  567.059814453125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 48,
              "consistent_fraction": 0.041666666666666664,
              "median_patch_error": 25.009105682373047,
              "median_forward_backward_error": 4.860365867614746,
              "discontinuity": 23.96705961227417,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.96705961227417,
              "appearance_previous_mean": 10.21890926361084,
              "appearance_adaptive_ratio": 2.4473361135938014
            },
            {
              "region": {
                "frame": 8541,
                "key": "track:1",
                "bbox": [
                  647.6870727539062,
                  224.13650512695312,
                  689.7706909179688,
                  357.5704650878906
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 23,
              "consistent_fraction": 0.7391304347826086,
              "median_patch_error": 25.130102157592773,
              "median_forward_backward_error": 0.3687816560268402,
              "discontinuity": 6.555678823719855,
              "previous_mean": 0.0,
              "adaptive_ratio": 6.555678823719855,
              "appearance_previous_mean": 7.420351266860962,
              "appearance_adaptive_ratio": 3.3866458950296545
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.9208829402923584,
          "discontinuity": 15.261369217997013,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 25.06960391998291
        },
        "decision": {
          "frame": 8542,
          "previous_frame": 8541,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 8542,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "5b75639e4ade8a70dbaa2aa5b2e2dc860eb0b3338ef4fb9ba58cef7d6d5a1a2c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              488.9945251941681,
              344.2114451825619,
              550.2007167339325,
              533.5505241453648
            ],
            [
              634.2354418635368,
              195.33341176062822,
              673.4440301060677,
              330.8615541383624
            ],
            [
              997.1845850348473,
              195.83437352627516,
              1048.9383855462074,
              292.79466412216425
            ],
            [
              233.0,
              306.02153017371893,
              294.00831031799316,
              406.4426495805383
            ],
            [
              769.2466249763966,
              129.6281408444047,
              804.5106935203075,
              179.33620377629995
            ],
            [
              477.09586495161057,
              133.4292575456202,
              511.1022952198982,
              180.91514059528708
            ],
            [
              961.4596209824085,
              117.37478467822075,
              999.7017082870007,
              205.36705780029297
            ],
            [
              621.4459224641323,
              126.54105159640312,
              658.1507095396519,
              179.03681348264217
            ],
            [
              319.3529457747936,
              119.95579623803496,
              347.9036865532398,
              179.7072650976479
            ],
            [
              1001.1277033686638,
              124.9640003144741,
              1040.2800667881966,
              209.5970116108656
            ]
          ],
          "detector_scores": [
            0.9354281559228776,
            0.8706680003423669,
            0.7829754042019826,
            0.7295401008922077,
            0.5132808433346356,
            0.4754398988471249,
            0.47390889919994517,
            0.46159942129452625,
            0.4041177803569609,
            0.35426037309391384
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
        "frame": 10332,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 10,
        "raw": {
          "frame": 10332,
          "previous_frame": 10331,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 10331,
                "key": "track:0",
                "bbox": [
                  1001.9478149414062,
                  322.22259521484375,
                  1048.8798828125,
                  507.8136291503906
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 42,
              "consistent_fraction": 0.47619047619047616,
              "median_patch_error": 40.185691833496094,
              "median_forward_backward_error": 1.1996421813964844,
              "discontinuity": 21.04964810325986,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.04964810325986,
              "appearance_previous_mean": 6.4733912870287895,
              "appearance_adaptive_ratio": 6.207826786868132
            },
            {
              "region": {
                "frame": 10331,
                "key": "track:3",
                "bbox": [
                  797.20263671875,
                  187.812255859375,
                  844.8267211914062,
                  317.6845397949219
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.8461538461538461,
              "median_patch_error": 18.557682037353516,
              "median_forward_backward_error": 0.13947194814682007,
              "discontinuity": 2.855028005746695,
              "previous_mean": 0.0,
              "adaptive_ratio": 2.855028005746695,
              "appearance_previous_mean": 5.564200833439827,
              "appearance_adaptive_ratio": 3.335192706529435
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 2.012648820877075,
          "discontinuity": 11.952338054503278,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 29.371686935424805
        },
        "decision": {
          "frame": 10332,
          "previous_frame": 10331,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 10332,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "91e3d97c21568e5072086568e8405a95768dba8e978047be1e0a766805361f22",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              480.74923515319824,
              355.87783801555634,
              567.0537548065186,
              546.81607234478
            ],
            [
              624.0674853920937,
              197.4228709116578,
              677.5527405142784,
              334.7265247926116
            ],
            [
              962.012693464756,
              117.1005501523614,
              999.1493167281151,
              207.3372217938304
            ],
            [
              318.97835275530815,
              120.67979664728045,
              348.2478204071522,
              179.9160625524819
            ],
            [
              769.1365312039852,
              129.2351174838841,
              803.636463791132,
              179.2324075959623
            ],
            [
              1001.2724999189377,
              196.88949073851109,
              1049.0,
              289.56909443438053
            ],
            [
              477.10850459337234,
              133.15873910859227,
              511.0242869257927,
              180.53773076459765
            ],
            [
              621.8620548546314,
              126.84233888238668,
              657.9462470710278,
              179.28992449492216
            ],
            [
              233.0,
              306.83767675608397,
              292.5468236207962,
              404.7748175933957
            ]
          ],
          "detector_scores": [
            0.9243142956371684,
            0.8870805142380823,
            0.6098467648952541,
            0.5668989169046054,
            0.5277145462275812,
            0.4853718314774275,
            0.4695254868243116,
            0.4674596034820452,
            0.4646365800396201
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
        "frame": 11007,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 11,
        "raw": {
          "frame": 11007,
          "previous_frame": 11006,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 11006,
                "key": "track:0",
                "bbox": [
                  480.24261474609375,
                  282.818115234375,
                  527.946044921875,
                  453.47760009765625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.24242424242424243,
              "median_patch_error": 27.774518966674805,
              "median_forward_backward_error": 4.256013870239258,
              "discontinuity": 21.041302247480914,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.041302247480914,
              "appearance_previous_mean": 8.96405553817749,
              "appearance_adaptive_ratio": 3.0984322719091195
            },
            {
              "region": {
                "frame": 11006,
                "key": "track:2",
                "bbox": [
                  455.2845764160156,
                  281.8223876953125,
                  502.3404541015625,
                  389.0056457519531
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 26,
              "consistent_fraction": 0.34615384615384615,
              "median_patch_error": 29.689908981323242,
              "median_forward_backward_error": 3.6781835556030273,
              "discontinuity": 19.412632795480583,
              "previous_mean": 0.0,
              "adaptive_ratio": 19.412632795480583,
              "appearance_previous_mean": 12.135522842407227,
              "appearance_adaptive_ratio": 2.446529034379362
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.8389668464660645,
          "discontinuity": 20.22696752148075,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7043478260869591,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 28.732213973999023
        },
        "decision": {
          "frame": 11007,
          "previous_frame": 11006,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 11007,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "49e64a1509b331717b7daac6d4a63773256453f53062ca0f31ef175a476a6d06",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              478.0603656768799,
              352.65175054967403,
              561.3988313674927,
              547.3794790655375
            ],
            [
              625.66482847929,
              195.84221351146698,
              676.4554870724678,
              333.76099693775177
            ],
            [
              962.4452196955681,
              118.71077588945627,
              1001.0139344334602,
              206.1045525148511
            ],
            [
              999.815104842186,
              196.3591851592064,
              1048.9256273508072,
              291.26415330171585
            ],
            [
              768.926081776619,
              129.66144359856844,
              805.2431954145432,
              179.06596026569605
            ],
            [
              476.96060740947723,
              132.9850245565176,
              511.81546223163605,
              181.1835214793682
            ],
            [
              621.0399568080902,
              126.69201369583607,
              658.2614462375641,
              179.77020721137524
            ],
            [
              233.0,
              304.05269499123096,
              292.85674715042114,
              403.81522814929485
            ],
            [
              319.3146787881851,
              120.57759504020214,
              348.13477647304535,
              179.67143531143665
            ],
            [
              997.1133114993572,
              124.8552440032363,
              1036.2735693752766,
              204.7961410060525
            ]
          ],
          "detector_scores": [
            0.9289036918481998,
            0.9015512704324327,
            0.7601804147596768,
            0.567337311119816,
            0.5510104974035678,
            0.5353603360217921,
            0.5213424144389058,
            0.501504059069607,
            0.4445130800228785,
            0.3768486215295474
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
        "frame": 11365,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 12,
        "raw": {
          "frame": 11365,
          "previous_frame": 11364,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 11364,
                "key": "track:0",
                "bbox": [
                  603.0393676757812,
                  332.2367858886719,
                  661.2263793945312,
                  520.0336303710938
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 41,
              "consistent_fraction": 0.04878048780487805,
              "median_patch_error": 24.443878173828125,
              "median_forward_backward_error": 18.92435073852539,
              "discontinuity": 23.251493872665776,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.251493872665776,
              "appearance_previous_mean": 10.19520616531372,
              "appearance_adaptive_ratio": 2.397585470806019
            },
            {
              "region": {
                "frame": 11364,
                "key": "track:3",
                "bbox": [
                  688.3026123046875,
                  224.2183837890625,
                  730.5132446289062,
                  369.0421447753906
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 23,
              "consistent_fraction": 0.08695652173913043,
              "median_patch_error": 28.5699405670166,
              "median_forward_backward_error": 16.201860427856445,
              "discontinuity": 26.08559790901516,
              "previous_mean": 0.0,
              "adaptive_ratio": 26.08559790901516,
              "appearance_previous_mean": 7.881803035736084,
              "appearance_adaptive_ratio": 3.6247975796249325
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.6227679252624512,
          "discontinuity": 24.66854589084047,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 26.506909370422363
        },
        "decision": {
          "frame": 11365,
          "previous_frame": 11364,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 11365,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "867b118dede4beb2527c7e93fc618da3885e72cbaea61af12d80458b29b659a5",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              481.25376296043396,
              349.96384988725185,
              565.8634884357452,
              533.0254604965448
            ],
            [
              621.9151653647423,
              206.23042299598455,
              681.7500682473183,
              333.94286534935236
            ],
            [
              233.0,
              304.8546462059021,
              294.99291956424713,
              404.36063635349274
            ],
            [
              994.3936803936958,
              195.59377166628838,
              1048.8806955218315,
              294.26237258315086
            ],
            [
              962.0635134577751,
              118.15313804149628,
              999.6935265660286,
              208.32461546361446
            ],
            [
              768.9388004541397,
              129.33102785795927,
              804.9801887273788,
              179.2941950187087
            ],
            [
              319.18788263201714,
              120.44836129248142,
              348.35308387875557,
              179.84097327291965
            ],
            [
              477.2507020831108,
              132.84413851052523,
              510.68291932344437,
              180.7346170321107
            ],
            [
              621.136830329895,
              126.52505316957831,
              657.977707862854,
              179.36900478973985
            ],
            [
              1004.5236267447472,
              124.37672081589699,
              1036.0707316994667,
              190.4173653125763
            ]
          ],
          "detector_scores": [
            0.9250513327160076,
            0.9153087032628033,
            0.8273191272531523,
            0.7827801478769362,
            0.7726948550472633,
            0.6584712270378752,
            0.6215977759516956,
            0.5854981417209929,
            0.5619432811674026,
            0.5224947372147222
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
        "frame": 11470,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 13,
        "raw": {
          "frame": 11470,
          "previous_frame": 11469,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 11469,
                "key": "track:0",
                "bbox": [
                  714.5990600585938,
                  340.2255859375,
                  787.34716796875,
                  536.4401245117188
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 49,
              "consistent_fraction": 0.02040816326530612,
              "median_patch_error": 21.710636138916016,
              "median_forward_backward_error": 9.74591064453125,
              "discontinuity": 21.26756193199936,
              "previous_mean": 0.0,
              "adaptive_ratio": 21.26756193199936,
              "appearance_previous_mean": 3.89576256275177,
              "appearance_adaptive_ratio": 5.572884843264349
            },
            {
              "region": {
                "frame": 11469,
                "key": "track:1",
                "bbox": [
                  674.615234375,
                  188.80809020996094,
                  727.358154296875,
                  320.53155517578125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 35,
              "consistent_fraction": 0.7714285714285715,
              "median_patch_error": 21.949617385864258,
              "median_forward_backward_error": 0.26107898354530334,
              "discontinuity": 5.017055402483258,
              "previous_mean": 0.0,
              "adaptive_ratio": 5.017055402483258,
              "appearance_previous_mean": 4.514278866350651,
              "appearance_adaptive_ratio": 4.862264391656503
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.1690759658813477,
          "discontinuity": 13.14230866724131,
          "photometric_gain": 1.0087719298245614,
          "photometric_offset": -0.7105263157894797,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 21.830126762390137
        },
        "decision": {
          "frame": 11470,
          "previous_frame": 11469,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 11470,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "7b48ccd5a981a943e8a16d962fb1bce893eb8c48cb7786182de6a5bfae38d838",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              591.093772828579,
              335.64007322490215,
              664.3827019333839,
              531.7499118596315
            ],
            [
              687.2730232477188,
              217.18641969561577,
              753.2098697423935,
              335.69455447793007
            ],
            [
              994.5092124342918,
              195.3903077840805,
              1048.8458042740822,
              293.3847707808018
            ],
            [
              961.308054715395,
              118.2844474837184,
              1000.7512180507183,
              205.57037963718176
            ],
            [
              233.07761615514755,
              309.31132267415524,
              293.55020385980606,
              404.24721087515354
            ],
            [
              1003.471520960331,
              124.6114461235702,
              1038.6843895316124,
              186.9940799959004
            ],
            [
              768.6951788067818,
              129.43093153834343,
              805.2099000811577,
              179.62480778992176
            ],
            [
              621.5691012144089,
              127.29311053827405,
              658.9627791643143,
              180.82842880114913
            ],
            [
              477.15348505973816,
              133.3844651579857,
              510.7951166629791,
              180.8761537373066
            ],
            [
              319.1822376549244,
              120.15004550293088,
              348.1840598285198,
              179.71958638355136
            ]
          ],
          "detector_scores": [
            0.9373827213480384,
            0.9181620313772526,
            0.8276671571306714,
            0.76127315772788,
            0.5867865992252288,
            0.5367074006457659,
            0.5218237174842226,
            0.45632778639157573,
            0.4374314186407883,
            0.42808314310658613
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
        "frame": 12290,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 14,
        "raw": {
          "frame": 12290,
          "previous_frame": 12289,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 12289,
                "key": "track:5",
                "bbox": [
                  783.459228515625,
                  410.0462341308594,
                  845.0586547851562,
                  592.00048828125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 39,
              "consistent_fraction": 0.0,
              "median_patch_error": 33.694801330566406,
              "median_forward_backward_error": 66.16104125976562,
              "discontinuity": 33.694801330566406,
              "previous_mean": 0.0,
              "adaptive_ratio": 33.694801330566406,
              "appearance_previous_mean": 7.110632658004761,
              "appearance_adaptive_ratio": 4.738650265196114
            },
            {
              "region": {
                "frame": 12289,
                "key": "track:4",
                "bbox": [
                  730.86376953125,
                  172.90664672851562,
                  796.4657592773438,
                  310.45989990234375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 38,
              "consistent_fraction": 0.4473684210526316,
              "median_patch_error": 27.61217498779297,
              "median_forward_backward_error": 4.18648099899292,
              "discontinuity": 15.25935986167506,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.25935986167506,
              "appearance_previous_mean": 10.471938610076904,
              "appearance_adaptive_ratio": 2.6367777749596826
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 2.3945932388305664,
          "discontinuity": 24.477080596120732,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 0.2149122807017534,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 30.653488159179688
        },
        "decision": {
          "frame": 12290,
          "previous_frame": 12289,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 12290,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "2c5dcd153b8298cdb8f963ee77ba6de55d763bd423982b6af11b16f29e5e8685",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              503.94349759817123,
              349.18804417550564,
              587.4469109177589,
              529.4356545358896
            ],
            [
              618.7305805683136,
              205.00417324900627,
              673.9221751689911,
              334.6026200354099
            ],
            [
              997.3497302532196,
              195.82472360879183,
              1048.9949295520782,
              293.9161898121238
            ],
            [
              233.0,
              303.76839128509164,
              263.22720777988434,
              364.00411554798484
            ],
            [
              987.7294490337372,
              121.72903272509575,
              1043.216807603836,
              208.93006759881973
            ],
            [
              477.1487930715084,
              132.85557086765766,
              511.0744153559208,
              180.4466636776924
            ],
            [
              319.01245364546776,
              120.09073700010777,
              348.23875561356544,
              179.75528787076473
            ],
            [
              769.54311850667,
              129.16243151947856,
              804.933838814497,
              178.8753010816872
            ],
            [
              620.6530828475952,
              126.59436670318246,
              657.6918659210205,
              178.99281838163733
            ],
            [
              959.8781336843967,
              126.51786842569709,
              999.936523526907,
              201.6395755596459
            ]
          ],
          "detector_scores": [
            0.9139799949597556,
            0.8770392334223291,
            0.6673235304167754,
            0.5255534742173715,
            0.46412788597662247,
            0.4619842335442416,
            0.44340082333511,
            0.4376677607284297,
            0.4302673911340912,
            0.352654493959715
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
        "frame": 12522,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 15,
        "raw": {
          "frame": 12522,
          "previous_frame": 12521,
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
                "frame": 12521,
                "key": "track:0",
                "bbox": [
                  593.4246215820312,
                  301.298828125,
                  651.958740234375,
                  465.21771240234375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 38,
              "consistent_fraction": 0.02631578947368421,
              "median_patch_error": 38.490787506103516,
              "median_forward_backward_error": 42.44577407836914,
              "discontinuity": 37.47787204541658,
              "previous_mean": 0.0,
              "adaptive_ratio": 37.47787204541658,
              "appearance_previous_mean": 10.35014533996582,
              "appearance_adaptive_ratio": 3.7188644450697756
            },
            {
              "region": {
                "frame": 12521,
                "key": "track:1",
                "bbox": [
                  617.1781005859375,
                  212.40737915039062,
                  667.24951171875,
                  308.8580017089844
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 26,
              "consistent_fraction": 0.46153846153846156,
              "median_patch_error": 43.49213409423828,
              "median_forward_backward_error": 1.5666849613189697,
              "discontinuity": 23.418841435359074,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.418841435359074,
              "appearance_previous_mean": 11.031108856201172,
              "appearance_adaptive_ratio": 3.9426801658102617
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.9449405670166016,
          "discontinuity": 30.44835674038783,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 40.9914608001709
        },
        "decision": {
          "frame": 12522,
          "previous_frame": 12521,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 12522,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "5e578930840688f08f5f01f67060f272b71112b50e12a316d715106c33e1667a",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              688.1636711359024,
              352.5935669541359,
              768.1099342107773,
              532.412457048893
            ],
            [
              606.9767928719521,
              204.93045172840357,
              666.662439763546,
              337.0950342640281
            ],
            [
              995.1550713777542,
              193.95438539981842,
              1048.8906935453415,
              295.42853716015816
            ],
            [
              233.1299363076687,
              304.64006842300296,
              260.94059839844704,
              362.75340651348233
            ],
            [
              769.4715029895306,
              129.68713318184018,
              804.7103226482868,
              178.76582996174693
            ],
            [
              620.9462538361549,
              126.89269853010774,
              657.7678527235985,
              179.91729513928294
            ],
            [
              318.79266583919525,
              119.34703582152724,
              347.96910536289215,
              179.91565016284585
            ],
            [
              477.0007241368294,
              133.16829738393426,
              511.49806374311447,
              181.05765328928828
            ]
          ],
          "detector_scores": [
            0.918825891933266,
            0.8917790202582965,
            0.7661334880888698,
            0.5199052933045503,
            0.5171792807458778,
            0.4898664524319525,
            0.4827698771562893,
            0.47930481900614225
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
        "frame": 15023,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 16,
        "raw": {
          "frame": 15023,
          "previous_frame": 15022,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 15022,
                "key": "track:0",
                "bbox": [
                  511.9674987792969,
                  339.7577209472656,
                  572.9156494140625,
                  515.9434204101562
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 36,
              "consistent_fraction": 0.0,
              "median_patch_error": 33.28833770751953,
              "median_forward_backward_error": 67.44436645507812,
              "discontinuity": 33.28833770751953,
              "previous_mean": 0.0,
              "adaptive_ratio": 33.28833770751953,
              "appearance_previous_mean": 6.477342128753662,
              "appearance_adaptive_ratio": 5.1391970727852705
            },
            {
              "region": {
                "frame": 15022,
                "key": "track:1",
                "bbox": [
                  464.85089111328125,
                  234.5614013671875,
                  524.2772216796875,
                  373.9817810058594
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 36,
              "consistent_fraction": 0.25,
              "median_patch_error": 17.534757614135742,
              "median_forward_backward_error": 4.7970685958862305,
              "discontinuity": 13.151068210601807,
              "previous_mean": 0.0,
              "adaptive_ratio": 13.151068210601807,
              "appearance_previous_mean": 9.072863578796387,
              "appearance_adaptive_ratio": 1.9326596792566253
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.9046555757522583,
          "discontinuity": 23.21970295906067,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7043478260869591,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 25.411547660827637
        },
        "decision": {
          "frame": 15023,
          "previous_frame": 15022,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 15023,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "67aff55722316ee435c556eaf1fa8fc236234f8feae5e6360550f0a82a7ec792",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              594.2960433959961,
              353.3264566510916,
              655.7947158813477,
              529.442032828927
            ],
            [
              705.4448702335358,
              184.38579573482275,
              746.4715058803558,
              328.5353191867471
            ],
            [
              233.0,
              308.80858763307333,
              293.03052550554276,
              411.74957267194986
            ],
            [
              995.7528583407402,
              194.8321017548442,
              1048.919939815998,
              293.8940215781331
            ],
            [
              1002.1470275521278,
              123.01804359257221,
              1041.4003013968468,
              210.971982806921
            ],
            [
              769.4858570992947,
              129.76422484219074,
              804.4229182302952,
              178.80979757010937
            ],
            [
              477.0806672871113,
              132.84817534685135,
              511.7776481807232,
              181.2153121381998
            ],
            [
              620.7734603881836,
              128.0419138930738,
              657.4600601196289,
              180.97901974990964
            ],
            [
              319.097438365221,
              120.22708217799664,
              347.9718427360058,
              179.7574781179428
            ]
          ],
          "detector_scores": [
            0.9108743271924805,
            0.8790227406238881,
            0.8736609769792806,
            0.7399453128101966,
            0.4397383005662445,
            0.4168717536332481,
            0.40334466910528755,
            0.40071855587275074,
            0.3529896276734094
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
        "frame": 15344,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 17,
        "raw": {
          "frame": 15344,
          "previous_frame": 15343,
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
                "frame": 15343,
                "key": "track:0",
                "bbox": [
                  654.9099731445312,
                  389.92572021484375,
                  708.4785766601562,
                  566.6723022460938
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 37,
              "consistent_fraction": 0.13513513513513514,
              "median_patch_error": 37.90965270996094,
              "median_forward_backward_error": 24.829402923583984,
              "discontinuity": 32.78672666807432,
              "previous_mean": 0.0,
              "adaptive_ratio": 32.78672666807432,
              "appearance_previous_mean": 5.503419406712055,
              "appearance_adaptive_ratio": 6.888381551245348
            },
            {
              "region": {
                "frame": 15343,
                "key": "track:1",
                "bbox": [
                  831.635986328125,
                  137.368408203125,
                  882.2659912109375,
                  253.35763549804688
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.72,
              "median_patch_error": 30.956066131591797,
              "median_forward_backward_error": 0.32620102167129517,
              "discontinuity": 8.667698516845704,
              "previous_mean": 0.0,
              "adaptive_ratio": 8.667698516845704,
              "appearance_previous_mean": 7.105690009891987,
              "appearance_adaptive_ratio": 4.356517957931908
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 2.5166525840759277,
          "discontinuity": 20.727212592460013,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 34.43285942077637
        },
        "decision": {
          "frame": 15344,
          "previous_frame": 15343,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 15344,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "3e096226e268ef05f10e4b2545aea10695dedebdf034515b316d55e04ca73358",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              625.2345942854881,
              192.5858245715499,
              691.7516422867775,
              335.28106055408716
            ],
            [
              495.4884192943573,
              352.6315251290798,
              556.7248146533966,
              527.4774360954762
            ],
            [
              233.0,
              305.5109963864088,
              293.83253479003906,
              411.7842271476984
            ],
            [
              995.6653110384941,
              195.30276204645634,
              1049.0,
              293.39839796721935
            ],
            [
              769.0576170384884,
              128.98179798573256,
              804.7118608057499,
              179.67448241263628
            ],
            [
              621.985546708107,
              126.82326127961278,
              657.2750982046127,
              180.73773973807693
            ],
            [
              476.9622762799263,
              133.2842246927321,
              511.80737322568893,
              180.94869078323245
            ],
            [
              318.85718181729317,
              120.347108181566,
              348.0447137057781,
              179.90790640190244
            ],
            [
              1002.4700862169266,
              123.19977454096079,
              1039.9321240186691,
              212.36858613044024
            ]
          ],
          "detector_scores": [
            0.908219411477724,
            0.904827949753387,
            0.8943857586467061,
            0.6121608087300605,
            0.575726041987345,
            0.5659755476152001,
            0.5410338737338605,
            0.4521993808165581,
            0.44405052305198867
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
        "frame": 15672,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 18,
        "raw": {
          "frame": 15672,
          "previous_frame": 15671,
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
                "frame": 15671,
                "key": "track:1",
                "bbox": [
                  725.4532470703125,
                  311.73388671875,
                  789.2345581054688,
                  477.57513427734375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.0,
              "median_patch_error": 33.73596954345703,
              "median_forward_backward_error": 67.31825256347656,
              "discontinuity": 33.73596954345703,
              "previous_mean": 0.12057114498955858,
              "adaptive_ratio": 33.73596954345703,
              "appearance_previous_mean": 6.46869683265686,
              "appearance_adaptive_ratio": 5.215265209700792
            },
            {
              "region": {
                "frame": 15671,
                "key": "track:2",
                "bbox": [
                  762.4800415039062,
                  159.9736328125,
                  799.7626342773438,
                  293.80572509765625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.3,
              "median_patch_error": 42.74720001220703,
              "median_forward_backward_error": 2.800851345062256,
              "discontinuity": 29.92304000854492,
              "previous_mean": 0.0,
              "adaptive_ratio": 29.92304000854492,
              "appearance_previous_mean": 8.873334884643555,
              "appearance_adaptive_ratio": 4.817489767706903
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.95,
          "background_patch_error": 1.9250637292861938,
          "discontinuity": 31.829504776000974,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": -0.28695652173912833,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 38.24158477783203
        },
        "decision": {
          "frame": 15672,
          "previous_frame": 15671,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 15672,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "86d936c45c1748aea9712f7629b071d53bbf232efedd47d2311fca5caae05d15",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              635.6776924729347,
              346.0093723535538,
              688.0351924300194,
              525.3146998882294
            ],
            [
              564.8164044618607,
              186.37819211184978,
              616.0754107236862,
              332.7657174617052
            ],
            [
              233.0,
              309.1464676260948,
              295.57165282964706,
              410.99721360206604
            ],
            [
              995.4714606404305,
              194.27852365374565,
              1048.8974511027336,
              296.30009058117867
            ],
            [
              769.8863419294357,
              129.45665319636464,
              804.1114398241043,
              179.40398917719722
            ],
            [
              621.6503408551216,
              126.59478825703263,
              657.3539850115776,
              181.52110592648387
            ],
            [
              477.4856085181236,
              132.9123133905232,
              511.51667362451553,
              180.65520682558417
            ],
            [
              1003.0404994487762,
              119.32389388978481,
              1043.983430147171,
              205.73518428206444
            ],
            [
              319.0856225192547,
              119.93121323361993,
              348.1740739643574,
              179.70863514766097
            ]
          ],
          "detector_scores": [
            0.9048424848896667,
            0.8993557671719132,
            0.8816059945155953,
            0.8016852404688215,
            0.5750508125876006,
            0.5663590038597601,
            0.46411875412041237,
            0.3884336005594276,
            0.3550771065094772
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
        "frame": 16197,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 19,
        "raw": {
          "frame": 16197,
          "previous_frame": 16196,
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
                "frame": 16196,
                "key": "track:2",
                "bbox": [
                  396.1658020019531,
                  551.4999389648438,
                  457.89697265625,
                  717.1106567382812
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 36,
              "consistent_fraction": 0.1111111111111111,
              "median_patch_error": 43.38690185546875,
              "median_forward_backward_error": 14.501699447631836,
              "discontinuity": 38.566134982638886,
              "previous_mean": 0.0,
              "adaptive_ratio": 38.566134982638886,
              "appearance_previous_mean": 6.514845609664917,
              "appearance_adaptive_ratio": 6.659697628306544
            },
            {
              "region": {
                "frame": 16196,
                "key": "track:1",
                "bbox": [
                  643.8638305664062,
                  161.0242462158203,
                  683.4075317382812,
                  296.5769348144531
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 30,
              "consistent_fraction": 0.03333333333333333,
              "median_patch_error": 40.79478454589844,
              "median_forward_backward_error": 20.529556274414062,
              "discontinuity": 39.43495839436849,
              "previous_mean": 0.0,
              "adaptive_ratio": 39.43495839436849,
              "appearance_previous_mean": 13.39516019821167,
              "appearance_adaptive_ratio": 3.0454868730382763
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.85,
          "background_patch_error": 5.289682388305664,
          "discontinuity": 39.00054668850369,
          "photometric_gain": 0.9736842105263158,
          "photometric_offset": 5.131578947368425,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 42.090843200683594
        },
        "decision": {
          "frame": 16197,
          "previous_frame": 16196,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 16197,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "371a3a4948b6c08ebb80f2c5fd0f7492ddb036f2ea936038e792f6087834b542",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              696.3097348213196,
              211.99509858340025,
              762.9985518455505,
              331.94504833966494
            ],
            [
              233.0,
              310.99820706248283,
              295.76254242658615,
              411.75793501734734
            ],
            [
              995.4482970833778,
              194.84550441801548,
              1049.0,
              295.0256691426039
            ],
            [
              769.9328453540802,
              129.4464213512838,
              804.1040408611298,
              179.34233692660928
            ],
            [
              318.82039523124695,
              120.26056821644306,
              348.81655716896057,
              179.7387556284666
            ],
            [
              477.45108357071877,
              133.22536981850863,
              511.4449745118618,
              181.02463691681623
            ],
            [
              580.8877089619637,
              362.5022451877594,
              671.1441685557365,
              530.26418197155
            ]
          ],
          "detector_scores": [
            0.8376476549151826,
            0.8152373015956355,
            0.6668334332627195,
            0.4980760907709697,
            0.47719928555956753,
            0.4226384379701314,
            0.3791709284298199
          ],
          "admitted_indices": [
            0,
            6
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 17718,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 20,
        "raw": {
          "frame": 17718,
          "previous_frame": 17717,
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
                "frame": 17717,
                "key": "track:0",
                "bbox": [
                  762.9285278320312,
                  364.8894348144531,
                  809.9168090820312,
                  538.3552856445312
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.2903225806451613,
              "median_patch_error": 22.485755920410156,
              "median_forward_backward_error": 3.5317227840423584,
              "discontinuity": 15.957633233839466,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.957633233839466,
              "appearance_previous_mean": 5.756980020552874,
              "appearance_adaptive_ratio": 3.9058249012736246
            },
            {
              "region": {
                "frame": 17717,
                "key": "track:1",
                "bbox": [
                  911.0560302734375,
                  154.7518768310547,
                  959.7037353515625,
                  292.7131042480469
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 27,
              "consistent_fraction": 0.2222222222222222,
              "median_patch_error": 42.01240158081055,
              "median_forward_backward_error": 8.547386169433594,
              "discontinuity": 32.676312340630425,
              "previous_mean": 0.0,
              "adaptive_ratio": 32.676312340630425,
              "appearance_previous_mean": 4.209537986665964,
              "appearance_adaptive_ratio": 9.980288030156293
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 2.801835298538208,
          "discontinuity": 24.316972787234945,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7043478260869591,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 32.24907875061035
        },
        "decision": {
          "frame": 17718,
          "previous_frame": 17717,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 17718,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "0c512f1c832ff95f5720a777d9bf91b316b04dfa0275afd9b9993e9caf3d93d2",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              691.6718374490738,
              350.6993880420923,
              747.3391908407211,
              527.6466716378927
            ],
            [
              593.0645203590393,
              190.72033423185349,
              651.5281710624695,
              337.063962996006
            ],
            [
              998.6408128142357,
              194.7112486809492,
              1048.9145289063454,
              291.386724665761
            ],
            [
              233.0,
              306.23337472975254,
              295.92584550380707,
              411.35088811814785
            ],
            [
              1002.7274251282215,
              124.0865405574441,
              1038.3484434783459,
              207.2365712299943
            ],
            [
              622.0417365729809,
              126.51807462051511,
              657.3005705177784,
              181.43726253136992
            ],
            [
              769.6663656532764,
              130.3304358124733,
              804.2162427604198,
              178.81774294376373
            ]
          ],
          "detector_scores": [
            0.9276647402885904,
            0.8424044160229146,
            0.7910378975917979,
            0.7736368386525232,
            0.49415984488888115,
            0.40977021617802317,
            0.3965373846957673
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
        "frame": 18260,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 21,
        "raw": {
          "frame": 18260,
          "previous_frame": 18259,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 18259,
                "key": "track:0",
                "bbox": [
                  557.0613403320312,
                  371.22198486328125,
                  605.468994140625,
                  550.2303466796875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 31,
              "consistent_fraction": 0.1935483870967742,
              "median_patch_error": 27.964427947998047,
              "median_forward_backward_error": 5.883002281188965,
              "discontinuity": 22.55195802257907,
              "previous_mean": 0.0,
              "adaptive_ratio": 22.55195802257907,
              "appearance_previous_mean": 12.49929141998291,
              "appearance_adaptive_ratio": 2.2372810592519397
            },
            {
              "region": {
                "frame": 18259,
                "key": "track:2",
                "bbox": [
                  426.2354736328125,
                  166.48863220214844,
                  485.5498352050781,
                  306.2513732910156
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 38,
              "consistent_fraction": 0.631578947368421,
              "median_patch_error": 24.300878524780273,
              "median_forward_backward_error": 0.4635762870311737,
              "discontinuity": 8.95295524597168,
              "previous_mean": 0.0,
              "adaptive_ratio": 8.95295524597168,
              "appearance_previous_mean": 8.254942893981934,
              "appearance_adaptive_ratio": 2.9437972905295613
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.0242700576782227,
          "discontinuity": 15.752456634275374,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 26.13265323638916
        },
        "decision": {
          "frame": 18260,
          "previous_frame": 18259,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 18260,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "a53bcc95bc73cbf463b711c90101d69db53eeba438d3a76fd4ad8de3fe6ba0d1",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              504.06102073192596,
              353.20633213222027,
              588.4380770921707,
              533.2098811417818
            ],
            [
              233.0,
              305.42097172886133,
              295.54485362768173,
              411.1731527671218
            ],
            [
              621.5546224713326,
              202.1115302965045,
              677.8912202715874,
              334.4208524301648
            ],
            [
              999.4916965961456,
              195.16397002339363,
              1048.9754016399384,
              292.0534670650959
            ],
            [
              769.8058820068836,
              129.95432042703032,
              804.9649424254894,
              179.09160402789712
            ],
            [
              477.5658602118492,
              132.79127015918493,
              511.58729511499405,
              181.16840510815382
            ],
            [
              621.5560040771961,
              126.68384379893541,
              657.5531353652477,
              180.03513089567423
            ],
            [
              1002.2145392894745,
              128.47868721187115,
              1039.9042122364044,
              210.7136344462633
            ],
            [
              319.2898083627224,
              120.009432092309,
              348.0581649839878,
              179.83463163673878
            ]
          ],
          "detector_scores": [
            0.9062219929329026,
            0.868553512627076,
            0.8463912593062032,
            0.6056830024782428,
            0.5733285083075134,
            0.49358939491764875,
            0.4616705257612447,
            0.3667654705033604,
            0.3658632031245085
          ],
          "admitted_indices": [
            0,
            2
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 18448,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 22,
        "raw": {
          "frame": 18448,
          "previous_frame": 18447,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 18447,
                "key": "track:2",
                "bbox": [
                  522.0054931640625,
                  353.1600646972656,
                  589.2777709960938,
                  525.0576171875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 38,
              "consistent_fraction": 0.02631578947368421,
              "median_patch_error": 28.830249786376953,
              "median_forward_backward_error": 45.78654479980469,
              "discontinuity": 28.07155900252493,
              "previous_mean": 0.0,
              "adaptive_ratio": 28.07155900252493,
              "appearance_previous_mean": 9.432628154754639,
              "appearance_adaptive_ratio": 3.0564387054571522
            },
            {
              "region": {
                "frame": 18447,
                "key": "track:1",
                "bbox": [
                  539.5726928710938,
                  219.3564910888672,
                  600.9098510742188,
                  357.871826171875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 28,
              "consistent_fraction": 0.14285714285714285,
              "median_patch_error": 21.160289764404297,
              "median_forward_backward_error": 10.127436637878418,
              "discontinuity": 18.137391226632257,
              "previous_mean": 0.0,
              "adaptive_ratio": 18.137391226632257,
              "appearance_previous_mean": 7.264703989028931,
              "appearance_adaptive_ratio": 2.91275319632573
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.1193666458129883,
          "discontinuity": 23.10447511457859,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 24.995269775390625
        },
        "decision": {
          "frame": 18448,
          "previous_frame": 18447,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 18448,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "42dc339fdf4ba710d4eeeac7cf6bce59f49459f3d647d91feab564a737d503f7",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              559.8867678642273,
              207.16533321142197,
              625.4567790031433,
              332.43511843681335
            ],
            [
              616.3182693719864,
              353.0827068835497,
              682.3186362981796,
              529.495973393321
            ],
            [
              233.0,
              311.1990408152342,
              295.52692770957947,
              411.2446015626192
            ],
            [
              1000.49301430583,
              195.62785337865353,
              1048.9070463478565,
              292.17614839971066
            ],
            [
              1003.6659930050373,
              123.0306947901845,
              1040.6458184421062,
              209.85033340007067
            ],
            [
              769.1186083257198,
              129.98321748524904,
              805.0633145868778,
              179.02446470409632
            ],
            [
              477.6227370798588,
              132.74180860444903,
              510.9547947347164,
              181.0882571823895
            ],
            [
              960.7045878171921,
              122.34349786490202,
              1003.124794125557,
              209.56749825924635
            ],
            [
              621.4769318401814,
              126.83697781711817,
              657.62778159976,
              181.29761136323214
            ],
            [
              319.0535416007042,
              120.31057275086641,
              348.1938496232033,
              179.7647224292159
            ]
          ],
          "detector_scores": [
            0.92060243453556,
            0.8926267517233599,
            0.8568124148189024,
            0.7056606478644446,
            0.48860580332905146,
            0.3883104221394564,
            0.3700824282190433,
            0.3663526566219565,
            0.3617762055846995,
            0.36098958981933155
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
        "frame": 18857,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 23,
        "raw": {
          "frame": 18857,
          "previous_frame": 18856,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 18856,
                "key": "track:2",
                "bbox": [
                  532.3511962890625,
                  356.1959533691406,
                  602.2608032226562,
                  534.8724365234375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 36,
              "consistent_fraction": 0.0,
              "median_patch_error": 29.733489990234375,
              "median_forward_backward_error": 76.82762145996094,
              "discontinuity": 29.733489990234375,
              "previous_mean": 0.0,
              "adaptive_ratio": 29.733489990234375,
              "appearance_previous_mean": 7.042233467102051,
              "appearance_adaptive_ratio": 4.222167601959667
            },
            {
              "region": {
                "frame": 18856,
                "key": "track:0",
                "bbox": [
                  472.5622863769531,
                  174.47915649414062,
                  537.8624267578125,
                  311.5133056640625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 39,
              "consistent_fraction": 0.46153846153846156,
              "median_patch_error": 23.242063522338867,
              "median_forward_backward_error": 1.1607893705368042,
              "discontinuity": 12.51495728125939,
              "previous_mean": 0.0,
              "adaptive_ratio": 12.51495728125939,
              "appearance_previous_mean": 7.959662199020386,
              "appearance_adaptive_ratio": 2.9199811425664928
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.834183692932129,
          "discontinuity": 21.124223635746883,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 26.48777675628662
        },
        "decision": {
          "frame": 18857,
          "previous_frame": 18856,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 18857,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "1ea4e7c07c59c128283ca5be4ecebeb871a4ce909ebd49f9cbeaba8ac851d529",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              699.0551270246506,
              203.3246248140931,
              757.9740115404129,
              330.5012722238898
            ],
            [
              233.01195567846298,
              312.3106050044298,
              295.18055349588394,
              410.9865189641714
            ],
            [
              589.5203745365143,
              351.74777413904667,
              661.482335805893,
              528.5130930989981
            ],
            [
              1000.0288099348545,
              196.97749468684196,
              1049.0,
              290.9922144114971
            ],
            [
              770.2120498120785,
              130.31473293155432,
              803.8859249651432,
              179.8241248652339
            ],
            [
              477.8884948194027,
              132.76342698559165,
              511.042825371027,
              180.81431132927537
            ],
            [
              621.8995801210403,
              127.49999496340752,
              657.5779875516891,
              179.49614222347736
            ],
            [
              319.20193579792976,
              120.38804014399648,
              348.1616015136242,
              179.82229889556766
            ],
            [
              1002.7132184505463,
              122.81396570801735,
              1041.6754400730133,
              214.97645112872124
            ]
          ],
          "detector_scores": [
            0.8912245801994255,
            0.8863300746801246,
            0.8844942349172601,
            0.5831867818653241,
            0.4911974227730124,
            0.4669207237801025,
            0.4577936586554697,
            0.42569907133225215,
            0.3517642859249203
          ],
          "admitted_indices": [
            0,
            2
          ],
          "matched_pairs": [],
          "iou_threshold": 0.3,
          "previous_region_count": 2,
          "version": "detector-layout-scene-decision:v1"
        }
      },
      {
        "frame": 19870,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 24,
        "raw": {
          "frame": 19870,
          "previous_frame": 19869,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 19869,
                "key": "track:2",
                "bbox": [
                  567.5549926757812,
                  186.64686584472656,
                  621.0358276367188,
                  329.7591552734375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.26666666666666666,
              "median_patch_error": 32.02398681640625,
              "median_forward_backward_error": 2.826036214828491,
              "discontinuity": 23.48425699869792,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.48425699869792,
              "appearance_previous_mean": 9.480282306671143,
              "appearance_adaptive_ratio": 3.3779570882474057
            },
            {
              "region": {
                "frame": 19869,
                "key": "track:3",
                "bbox": [
                  233.0,
                  522.2198486328125,
                  258.8054504394531,
                  687.5716552734375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 12,
              "consistent_fraction": 0.3333333333333333,
              "median_patch_error": 21.000709533691406,
              "median_forward_backward_error": 13.139999389648438,
              "discontinuity": 14.00047302246094,
              "previous_mean": 0.7285806898977244,
              "adaptive_ratio": 14.00047302246094,
              "appearance_previous_mean": 8.314359664916992,
              "appearance_adaptive_ratio": 2.5258360691690225
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.1979520320892334,
          "discontinuity": 18.74236501057943,
          "photometric_gain": 0.991304347826087,
          "photometric_offset": 0.7043478260869591,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 26.512348175048828
        },
        "decision": {
          "frame": 19870,
          "previous_frame": 19869,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 19870,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "fe2e9b13715f652481c63a2363a6c465d3d0ecc892856de9c73b8e6d9dc7e776",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              604.274341404438,
              205.99354180693626,
              661.3368036150932,
              337.2301468551159
            ],
            [
              676.635281264782,
              349.5747831761837,
              762.3866418004036,
              529.6780938208103
            ],
            [
              999.4671255946159,
              195.64494005590677,
              1048.9463742375374,
              293.67693050950766
            ],
            [
              769.8066450059414,
              130.15993789955974,
              804.9275068342686,
              179.1345566995442
            ],
            [
              621.0775155127048,
              126.90926284715533,
              657.5890236794949,
              180.18442739918828
            ],
            [
              477.3086048960686,
              132.6515685878694,
              511.1966031193733,
              181.13731322064996
            ],
            [
              233.0,
              306.26374722644687,
              260.92674282193184,
              362.9535162933171
            ],
            [
              318.8973745405674,
              120.0067080296576,
              347.96302112936974,
              179.63505567237735
            ]
          ],
          "detector_scores": [
            0.8962534126929327,
            0.8851794007684745,
            0.6421628652657176,
            0.5426999787353086,
            0.4880140145253316,
            0.4727922288465524,
            0.44373730139059575,
            0.42866765898772047
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
        "frame": 20811,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 25,
        "raw": {
          "frame": 20811,
          "previous_frame": 20810,
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
                "frame": 20810,
                "key": "track:6",
                "bbox": [
                  771.8931274414062,
                  342.46697998046875,
                  851.3379516601562,
                  509.2945556640625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 37,
              "consistent_fraction": 0.02702702702702703,
              "median_patch_error": 26.37074851989746,
              "median_forward_backward_error": 31.43427848815918,
              "discontinuity": 25.65802558692726,
              "previous_mean": 0.0,
              "adaptive_ratio": 25.65802558692726,
              "appearance_previous_mean": 3.2337372228503227,
              "appearance_adaptive_ratio": 8.154882942731325
            },
            {
              "region": {
                "frame": 20810,
                "key": "track:4",
                "bbox": [
                  679.7527465820312,
                  174.72515869140625,
                  727.8994140625,
                  316.9755859375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 31,
              "consistent_fraction": 0.8387096774193549,
              "median_patch_error": 27.45627784729004,
              "median_forward_backward_error": 0.28710001707077026,
              "discontinuity": 4.428431910853231,
              "previous_mean": 0.0,
              "adaptive_ratio": 4.428431910853231,
              "appearance_previous_mean": 5.267821587622166,
              "appearance_adaptive_ratio": 5.212074363301185
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.9648171663284302,
          "discontinuity": 15.043228748890245,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 26.91351318359375
        },
        "decision": {
          "frame": 20811,
          "previous_frame": 20810,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 20811,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "bb420cfcdeb70a5845afd73de08dc5d2e4d174d49a0492848ea2219fe613052b",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              706.0499649643898,
              187.60861157625914,
              761.6596526503563,
              327.4309763982892
            ],
            [
              598.7476078867912,
              349.52061350643635,
              653.8622763752937,
              528.7368098944426
            ],
            [
              1000.9310441613197,
              195.0066937804222,
              1048.9709543585777,
              290.63935551047325
            ],
            [
              769.7114753127098,
              130.03467454761267,
              804.9223862290382,
              178.5913731083274
            ],
            [
              621.7301365733147,
              126.88602240011096,
              657.6126082539558,
              180.16417448595166
            ],
            [
              477.3107312619686,
              132.86251963302493,
              511.12317433953285,
              180.41864638403058
            ],
            [
              318.9885058104992,
              120.63394121080637,
              347.9825764000416,
              179.9648413732648
            ],
            [
              233.0,
              309.22060153633356,
              296.8500106334686,
              403.89995589107275
            ]
          ],
          "detector_scores": [
            0.9126574446937339,
            0.8961613755549981,
            0.717882233871992,
            0.674070284185917,
            0.6447240799987606,
            0.5627091527111979,
            0.4695626608930522,
            0.4244257319416239
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
        "frame": 21843,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 26,
        "raw": {
          "frame": 21843,
          "previous_frame": 21842,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 21842,
                "key": "track:0",
                "bbox": [
                  686.7581176757812,
                  345.5242919921875,
                  745.4032592773438,
                  516.2562866210938
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 32,
              "consistent_fraction": 0.125,
              "median_patch_error": 26.33035659790039,
              "median_forward_backward_error": 9.298665046691895,
              "discontinuity": 23.039062023162842,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.039062023162842,
              "appearance_previous_mean": 8.217970848083496,
              "appearance_adaptive_ratio": 3.2039973230181102
            },
            {
              "region": {
                "frame": 21842,
                "key": "track:1",
                "bbox": [
                  656.4562377929688,
                  168.89149475097656,
                  708.3162231445312,
                  300.73919677734375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 28,
              "consistent_fraction": 0.42857142857142855,
              "median_patch_error": 31.41748046875,
              "median_forward_backward_error": 1.5540766716003418,
              "discontinuity": 17.952845982142858,
              "previous_mean": 0.0,
              "adaptive_ratio": 17.952845982142858,
              "appearance_previous_mean": 13.750195026397705,
              "appearance_adaptive_ratio": 2.284875262382427
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.436366081237793,
          "discontinuity": 20.49595400265285,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 28.873918533325195
        },
        "decision": {
          "frame": 21843,
          "previous_frame": 21842,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 21843,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "5f236fa6dde85627c4cfd594171e4bd3ec5fc7bcb2d87bc706f99d53e67557ed",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              506.56753343343735,
              353.53589560091496,
              589.2000942826271,
              532.3529721349478
            ],
            [
              625.4908646941185,
              200.2559143975377,
              684.748198568821,
              335.8201637789607
            ],
            [
              233.0,
              304.6306773945689,
              297.7306179404259,
              404.2591289356351
            ],
            [
              999.4063242971897,
              195.39687394350767,
              1048.9304257333279,
              292.5458923652768
            ],
            [
              769.4314060211182,
              129.8308486789465,
              805.3882503509521,
              179.05541683733463
            ],
            [
              477.09655803442,
              133.0307035818696,
              510.9754367470741,
              181.0161141976714
            ],
            [
              318.9803043305874,
              120.05331951379776,
              348.05206099152565,
              179.97223231196404
            ],
            [
              621.6745075583458,
              126.74543648213148,
              657.8635650277138,
              179.9437086954713
            ]
          ],
          "detector_scores": [
            0.9087078903124469,
            0.884785818738334,
            0.8603082441404195,
            0.6628701038238527,
            0.5217444748010741,
            0.4918552689611598,
            0.48235100909602335,
            0.4319376094541022
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
        "frame": 22495,
        "raw_hypothesis": true,
        "actual_barrier": false,
        "epoch": 26,
        "raw": {
          "frame": 22495,
          "previous_frame": 22494,
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
                "frame": 22494,
                "key": "track:0",
                "bbox": [
                  715.8423461914062,
                  348.9405212402344,
                  774.2523193359375,
                  524.6529541015625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 41,
              "consistent_fraction": 0.4878048780487805,
              "median_patch_error": 22.99227523803711,
              "median_forward_backward_error": 1.1413838863372803,
              "discontinuity": 11.776531219482422,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.776531219482422,
              "appearance_previous_mean": 3.394575610756874,
              "appearance_adaptive_ratio": 6.773239978858689
            },
            {
              "region": {
                "frame": 22494,
                "key": "track:1",
                "bbox": [
                  592.388427734375,
                  159.49716186523438,
                  646.1832275390625,
                  289.8531494140625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 26,
              "consistent_fraction": 0.5,
              "median_patch_error": 39.21251678466797,
              "median_forward_backward_error": 1.0806670188903809,
              "discontinuity": 19.606258392333984,
              "previous_mean": 0.0,
              "adaptive_ratio": 19.606258392333984,
              "appearance_previous_mean": 5.649659868329763,
              "appearance_adaptive_ratio": 6.94068628882973
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 2.1743552684783936,
          "discontinuity": 15.691394805908203,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 31.10239601135254
        },
        "decision": {
          "frame": 22495,
          "previous_frame": 22494,
          "decision": "no_barrier",
          "reason": "complete_current_layout_correspondence",
          "raw_hypothesis": true,
          "detector_frame": 22495,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "81a973323862b3226a09866c2282d00ccf00664a4eca9cfcebae0850eaf339c9",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              688.1490069627762,
              349.61834985017776,
              767.1686791181564,
              530.7267548441887
            ],
            [
              602.5673210024834,
              204.7592779546976,
              661.3818843960762,
              337.9296971410513
            ],
            [
              1000.6108338236809,
              195.30006776750088,
              1049.0,
              291.57231833040714
            ],
            [
              770.2918546497822,
              129.89908312633634,
              804.3836404979229,
              179.432242449373
            ],
            [
              233.0,
              306.53748459368944,
              288.31670820713043,
              411.5480607673526
            ],
            [
              477.44500693678856,
              132.72360160201788,
              511.09361496567726,
              180.82843109220266
            ],
            [
              620.3919243812561,
              126.6898990534246,
              658.1794800758362,
              178.91462472453713
            ],
            [
              319.11068445444107,
              119.96927450597286,
              347.5736560225487,
              179.69177070260048
            ]
          ],
          "detector_scores": [
            0.9271244411549384,
            0.9033252757794376,
            0.6404294458287666,
            0.5499299026549481,
            0.5452198584927885,
            0.4742993323768823,
            0.46243001815830803,
            0.3533231083540833
          ],
          "admitted_indices": [
            0,
            1
          ],
          "matched_pairs": [
            [
              0,
              0
            ],
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
        "frame": 22953,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 27,
        "raw": {
          "frame": 22953,
          "previous_frame": 22952,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 22952,
                "key": "track:0",
                "bbox": [
                  712.0546875,
                  312.5039367675781,
                  769.3565673828125,
                  480.609375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 27,
              "consistent_fraction": 0.0,
              "median_patch_error": 37.70535659790039,
              "median_forward_backward_error": 65.47057342529297,
              "discontinuity": 37.70535659790039,
              "previous_mean": 0.0,
              "adaptive_ratio": 37.70535659790039,
              "appearance_previous_mean": 4.537592031061649,
              "appearance_adaptive_ratio": 8.309551925292535
            },
            {
              "region": {
                "frame": 22952,
                "key": "track:1",
                "bbox": [
                  635.1657104492188,
                  182.52154541015625,
                  677.5241088867188,
                  294.9305419921875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 19,
              "consistent_fraction": 0.9473684210526315,
              "median_patch_error": 27.66935920715332,
              "median_forward_backward_error": 0.39145463705062866,
              "discontinuity": 1.4562820635343867,
              "previous_mean": 0.0,
              "adaptive_ratio": 1.4562820635343867,
              "appearance_previous_mean": 5.253401450812817,
              "appearance_adaptive_ratio": 5.266941707428862
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 2.26108980178833,
          "discontinuity": 19.58081933071739,
          "photometric_gain": 1.008849557522124,
          "photometric_offset": -0.7168141592920421,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 32.687357902526855
        },
        "decision": {
          "frame": 22953,
          "previous_frame": 22952,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 22953,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "9213694d3be86dddccbd727548b96a076a65e4ff3f37541f98150b5c7a1933fd",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              608.3731054663658,
              345.2202876955271,
              682.7509770989418,
              523.3699161857367
            ],
            [
              567.4692549109459,
              218.4522817581892,
              627.8886333107948,
              332.2482326179743
            ],
            [
              998.0041736960411,
              195.3590074107051,
              1048.9153800606728,
              294.99779618531466
            ],
            [
              769.5805115401745,
              130.48145977035165,
              804.7005343735218,
              179.3049423508346
            ],
            [
              318.99923491477966,
              120.50525502488017,
              348.10619592666626,
              179.89810069277883
            ],
            [
              477.46651074290276,
              132.76551871746778,
              511.1912241280079,
              180.7910227701068
            ],
            [
              620.2240341901779,
              127.25029991194606,
              658.4629813432693,
              178.30429722741246
            ],
            [
              233.13728511333466,
              311.0995586887002,
              287.84376430511475,
              411.4599560126662
            ],
            [
              960.2496823072433,
              121.79481345415115,
              1005.5942603349686,
              209.2167700380087
            ],
            [
              1004.0828108787537,
              121.0224809795618,
              1041.1147847175598,
              210.96245202422142
            ]
          ],
          "detector_scores": [
            0.9109846685259231,
            0.908457857074177,
            0.751189814628208,
            0.5083296936403985,
            0.47432406245991887,
            0.443787324403706,
            0.42957460065452235,
            0.4148237221730962,
            0.39502215611443015,
            0.3547081701134739
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
        "frame": 23356,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 28,
        "raw": {
          "frame": 23356,
          "previous_frame": 23355,
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
                "frame": 23355,
                "key": "track:0",
                "bbox": [
                  592.9446411132812,
                  398.3100891113281,
                  658.4984130859375,
                  590.4381713867188
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 45,
              "consistent_fraction": 0.1111111111111111,
              "median_patch_error": 37.687923431396484,
              "median_forward_backward_error": 40.32377243041992,
              "discontinuity": 33.50037638346354,
              "previous_mean": 0.0,
              "adaptive_ratio": 33.50037638346354,
              "appearance_previous_mean": 4.683655723929405,
              "appearance_adaptive_ratio": 8.046689520505103
            },
            {
              "region": {
                "frame": 23355,
                "key": "track:2",
                "bbox": [
                  739.4065551757812,
                  206.11767578125,
                  794.9955444335938,
                  353.7286071777344
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 29,
              "consistent_fraction": 0.7241379310344828,
              "median_patch_error": 19.99433135986328,
              "median_forward_backward_error": 0.6295629739761353,
              "discontinuity": 5.515677616514009,
              "previous_mean": 0.0,
              "adaptive_ratio": 5.515677616514009,
              "appearance_previous_mean": 5.24971666932106,
              "appearance_adaptive_ratio": 3.8086496127893175
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 2.384956121444702,
          "discontinuity": 19.508026999988775,
          "photometric_gain": 0.9824561403508771,
          "photometric_offset": 1.4210526315789451,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 28.841127395629883
        },
        "decision": {
          "frame": 23356,
          "previous_frame": 23355,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 23356,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "9fffbf0c061a92d2d05b604a4d154202494d55bd4633b72efdc64817c204ff2c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              504.05034786462784,
              351.20562839508057,
              587.6411260962486,
              532.0684324502945
            ],
            [
              621.6753921508789,
              202.099479354918,
              678.8297729492188,
              333.74364449828863
            ],
            [
              233.0,
              305.3341866210103,
              294.9501794576645,
              411.42789959162474
            ],
            [
              998.2111896276474,
              195.12145265191793,
              1048.947270989418,
              293.6534609571099
            ],
            [
              769.8345689475536,
              129.8513742275536,
              804.6623297035694,
              179.4366596005857
            ],
            [
              477.18760722875595,
              133.25641359388828,
              511.1629825234413,
              181.2814686000347
            ],
            [
              620.8349699676037,
              127.51036198064685,
              657.7042851746082,
              178.35430634394288
            ],
            [
              319.1331199705601,
              119.78433608263731,
              348.08255967497826,
              179.73489291220903
            ],
            [
              1001.3797818422318,
              123.96565082669258,
              1036.7592638731003,
              206.88279132544994
            ]
          ],
          "detector_scores": [
            0.9148583627189552,
            0.8642193305665617,
            0.8602612471564715,
            0.7574779346680078,
            0.5103520856511444,
            0.4789152090911329,
            0.45452323057311783,
            0.4366474926371829,
            0.378791717606405
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
        "frame": 23880,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 29,
        "raw": {
          "frame": 23880,
          "previous_frame": 23879,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 23879,
                "key": "track:0",
                "bbox": [
                  593.0252075195312,
                  367.9007873535156,
                  648.7748413085938,
                  543.7083740234375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 36,
              "consistent_fraction": 0.2222222222222222,
              "median_patch_error": 30.238378524780273,
              "median_forward_backward_error": 2.0622763633728027,
              "discontinuity": 23.51873885260688,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.51873885260688,
              "appearance_previous_mean": 10.332535743713379,
              "appearance_adaptive_ratio": 2.9265205826341516
            },
            {
              "region": {
                "frame": 23879,
                "key": "track:1",
                "bbox": [
                  536.2327880859375,
                  246.61148071289062,
                  604.174072265625,
                  325.13482666015625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 22,
              "consistent_fraction": 0.09090909090909091,
              "median_patch_error": 19.997554779052734,
              "median_forward_backward_error": 13.78917121887207,
              "discontinuity": 18.179595253684305,
              "previous_mean": 0.0,
              "adaptive_ratio": 18.179595253684305,
              "appearance_previous_mean": 7.357461929321289,
              "appearance_adaptive_ratio": 2.7179963649363343
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.9543650150299072,
          "discontinuity": 20.849167053145592,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 25.117966651916504
        },
        "decision": {
          "frame": 23880,
          "previous_frame": 23879,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 23880,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b5a145cae81809d1ea84871524658a3cc80b22101fbe10d26781b9f8d2e0741c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              624.129680454731,
              352.61468130350113,
              680.2053872942924,
              525.6975807547569
            ],
            [
              566.6339350938797,
              189.5643923357129,
              622.2043055295944,
              330.822881154716
            ],
            [
              769.93475741148,
              130.20717484131455,
              804.6550386548042,
              179.28880416974425
            ],
            [
              621.6084184646606,
              127.1455071233213,
              657.7485284805298,
              180.57033245638013
            ],
            [
              477.2543483674526,
              132.66999553143978,
              511.4949220716953,
              180.8634063154459
            ],
            [
              999.2197603881359,
              195.38912101835012,
              1048.939268618822,
              293.58923814445734
            ],
            [
              233.0,
              311.4836996346712,
              295.6295009255409,
              403.0886892527342
            ],
            [
              318.9582670331001,
              120.62800509110093,
              348.23060125112534,
              179.84266177937388
            ]
          ],
          "detector_scores": [
            0.9133068269822427,
            0.8883064056001607,
            0.6864287608348564,
            0.6239562676539364,
            0.5808652585852014,
            0.5656580881975719,
            0.4802735968360791,
            0.40953208676698094
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
        "frame": 24147,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 30,
        "raw": {
          "frame": 24147,
          "previous_frame": 24146,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 24146,
                "key": "track:0",
                "bbox": [
                  733.0665893554688,
                  339.9497985839844,
                  787.3433837890625,
                  512.7546997070312
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 28,
              "consistent_fraction": 0.0,
              "median_patch_error": 27.845947265625,
              "median_forward_backward_error": 47.56684112548828,
              "discontinuity": 27.845947265625,
              "previous_mean": 0.0,
              "adaptive_ratio": 27.845947265625,
              "appearance_previous_mean": 6.967970609664917,
              "appearance_adaptive_ratio": 3.9962779445426055
            },
            {
              "region": {
                "frame": 24146,
                "key": "track:2",
                "bbox": [
                  817.901123046875,
                  127.49111938476562,
                  858.1468505859375,
                  249.66766357421875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 24,
              "consistent_fraction": 0.8333333333333334,
              "median_patch_error": 28.476261138916016,
              "median_forward_backward_error": 0.43841880559921265,
              "discontinuity": 4.746043523152668,
              "previous_mean": 0.0,
              "adaptive_ratio": 4.746043523152668,
              "appearance_previous_mean": 10.205729484558105,
              "appearance_adaptive_ratio": 2.7902229999337473
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 1.910856008529663,
          "discontinuity": 16.295995394388832,
          "photometric_gain": 1.0,
          "photometric_offset": -1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 28.161104202270508
        },
        "decision": {
          "frame": 24147,
          "previous_frame": 24146,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 24147,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "5507484b45739e3f7dfad4796322c1c56f2bc2bd20a307d1ef73df02fab3410a",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              504.72409123182297,
              350.6412044465542,
              589.2908881306648,
              530.159031778574
            ],
            [
              622.6941600441933,
              200.5174931436777,
              680.2036728262901,
              336.1830345839262
            ],
            [
              233.0,
              305.0783446729183,
              297.62498968839645,
              403.94954803586006
            ],
            [
              999.4797272384167,
              195.44105461984873,
              1048.9667487442493,
              290.78657402843237
            ],
            [
              319.02402022480965,
              120.35799297690392,
              348.0845842063427,
              179.7126101255417
            ],
            [
              476.77229103446007,
              132.65848986059427,
              511.1584121286869,
              180.5347913429141
            ],
            [
              769.7382030785084,
              129.35951023548841,
              804.673093765974,
              179.20619107037783
            ],
            [
              621.5254081189632,
              127.09838473424315,
              657.3614098131657,
              179.351125407964
            ]
          ],
          "detector_scores": [
            0.9228843554041695,
            0.8687911227173324,
            0.7951160393931325,
            0.6695386165174158,
            0.459202948318248,
            0.45767766827889717,
            0.4569199385080297,
            0.42608300361012436
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
        "frame": 24679,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 31,
        "raw": {
          "frame": 24679,
          "previous_frame": 24678,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 24678,
                "key": "track:0",
                "bbox": [
                  561.2132568359375,
                  317.2216491699219,
                  640.7473754882812,
                  473.0399169921875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 32,
              "consistent_fraction": 0.5,
              "median_patch_error": 22.394027709960938,
              "median_forward_backward_error": 1.0194153785705566,
              "discontinuity": 11.197013854980469,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.197013854980469,
              "appearance_previous_mean": 3.5606576949357986,
              "appearance_adaptive_ratio": 6.289295301205503
            },
            {
              "region": {
                "frame": 24678,
                "key": "track:1",
                "bbox": [
                  467.5657653808594,
                  149.30352783203125,
                  510.9372253417969,
                  265.8365783691406
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 26,
              "consistent_fraction": 0.6538461538461539,
              "median_patch_error": 29.705535888671875,
              "median_forward_backward_error": 0.3813543915748596,
              "discontinuity": 10.28268549992488,
              "previous_mean": 0.0,
              "adaptive_ratio": 10.28268549992488,
              "appearance_previous_mean": 3.6522109173238277,
              "appearance_adaptive_ratio": 8.133576225777981
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 2.255314588546753,
          "discontinuity": 10.739849677452675,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": -0.2807017543859587,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 26.049781799316406
        },
        "decision": {
          "frame": 24679,
          "previous_frame": 24678,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 24679,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "72beeb49a95db14ba00e0f6e2fac328a938c21e297cb954c973c76c1ed1b204d",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              589.4323773384094,
              352.3876378983259,
              660.3759446144104,
              528.7301200181246
            ],
            [
              695.1868616342545,
              189.2869457527995,
              753.4463933706284,
              331.2866545394063
            ],
            [
              998.6776981949806,
              196.04635096341372,
              1048.9335765242577,
              292.6253002807498
            ],
            [
              477.5431115925312,
              133.02625435590744,
              511.3347074687481,
              180.78094671666622
            ],
            [
              318.7106221616268,
              120.19995839521289,
              348.0498723089695,
              179.98491329327226
            ],
            [
              770.4612130820751,
              129.72766650095582,
              803.4228544533253,
              179.2665076367557
            ],
            [
              621.4723462462425,
              126.97218892350793,
              657.7288637757301,
              179.8746448867023
            ],
            [
              1003.166950583458,
              121.52439124137163,
              1045.1138664484024,
              210.9929917678237
            ]
          ],
          "detector_scores": [
            0.9176688116940731,
            0.8770892590494529,
            0.7321405949326635,
            0.4828152421023479,
            0.48113919579652753,
            0.4753630760352385,
            0.4611506697693885,
            0.35590976962593684
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
        "frame": 25078,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 32,
        "raw": {
          "frame": 25078,
          "previous_frame": 25077,
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
                "frame": 25077,
                "key": "track:2",
                "bbox": [
                  487.9009704589844,
                  374.8525390625,
                  560.3270874023438,
                  541.5614624023438
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 27,
              "consistent_fraction": 0.0,
              "median_patch_error": 29.25159454345703,
              "median_forward_backward_error": 62.090484619140625,
              "discontinuity": 29.25159454345703,
              "previous_mean": 0.0,
              "adaptive_ratio": 29.25159454345703,
              "appearance_previous_mean": 4.33159738779068,
              "appearance_adaptive_ratio": 6.753073271746692
            },
            {
              "region": {
                "frame": 25077,
                "key": "track:1",
                "bbox": [
                  642.2000732421875,
                  205.6271209716797,
                  709.1865234375,
                  343.5651550292969
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 30,
              "consistent_fraction": 0.4,
              "median_patch_error": 20.690086364746094,
              "median_forward_backward_error": 4.142693519592285,
              "discontinuity": 12.414051818847655,
              "previous_mean": 0.0,
              "adaptive_ratio": 12.414051818847655,
              "appearance_previous_mean": 4.929669663310051,
              "appearance_adaptive_ratio": 4.197053307392129
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.484339475631714,
          "discontinuity": 20.832823181152342,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 24.970840454101562
        },
        "decision": {
          "frame": 25078,
          "previous_frame": 25077,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 25078,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "a49e62ef146909a5fb21b76fffde042b40bbcb40e1f7052e57c328a0883148b2",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              686.8844591379166,
              350.33240708708763,
              766.5578664541245,
              530.6125504076481
            ],
            [
              605.3669834136963,
              205.13189490139484,
              663.1246137619019,
              337.9108921736479
            ],
            [
              997.7020443081856,
              196.75647675246,
              1048.8882343173027,
              293.7364520803094
            ],
            [
              770.0144239366055,
              129.81071031838655,
              803.4605058729649,
              179.555246822536
            ],
            [
              621.5287002623081,
              127.13038846105337,
              657.6831127107143,
              180.27795507758856
            ],
            [
              477.36624324321747,
              132.29473470896482,
              510.8681517839432,
              180.96393316239119
            ],
            [
              233.0,
              304.82356806471944,
              260.2371558248997,
              362.8133450560272
            ],
            [
              318.83578288555145,
              120.12507989257574,
              347.77343714237213,
              179.80204827338457
            ],
            [
              960.3027928173542,
              122.5862166583538,
              1005.0050685107708,
              214.698060631752
            ]
          ],
          "detector_scores": [
            0.9115109928343781,
            0.9054697007484275,
            0.7526652414676676,
            0.5076824340716722,
            0.48620991046408696,
            0.4682711519691903,
            0.45368764018109115,
            0.432918337783008,
            0.35099664600932473
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
        "frame": 25371,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 33,
        "raw": {
          "frame": 25371,
          "previous_frame": 25370,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 25370,
                "key": "track:0",
                "bbox": [
                  760.9238891601562,
                  399.08489990234375,
                  811.5951538085938,
                  561.6131591796875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 28,
              "consistent_fraction": 0.0,
              "median_patch_error": 30.688350677490234,
              "median_forward_backward_error": 34.27605438232422,
              "discontinuity": 30.688350677490234,
              "previous_mean": 0.0,
              "adaptive_ratio": 30.688350677490234,
              "appearance_previous_mean": 11.517609596252441,
              "appearance_adaptive_ratio": 2.6644722084932884
            },
            {
              "region": {
                "frame": 25370,
                "key": "track:1",
                "bbox": [
                  769.1240844726562,
                  175.50836181640625,
                  820.6209106445312,
                  313.54949951171875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 36,
              "consistent_fraction": 0.5555555555555556,
              "median_patch_error": 32.28950500488281,
              "median_forward_backward_error": 0.7017278075218201,
              "discontinuity": 14.35089111328125,
              "previous_mean": 0.0,
              "adaptive_ratio": 14.35089111328125,
              "appearance_previous_mean": 15.294819831848145,
              "appearance_adaptive_ratio": 2.1111399388730896
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.7625,
          "background_patch_error": 3.2363946437835693,
          "discontinuity": 22.519620895385742,
          "photometric_gain": 1.0175438596491229,
          "photometric_offset": -3.4385964912280684,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 31.488927841186523
        },
        "decision": {
          "frame": 25371,
          "previous_frame": 25370,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 25371,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "30f497ace52b0e8a923cf35e89ad579d07cb0ee57a09a5c3cfdf2214b2c94803",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              545.3575391769409,
              209.0661057755351,
              607.3281402587891,
              331.04666209965944
            ],
            [
              608.7231366038322,
              336.34360994398594,
              690.5067561268806,
              529.729147657752
            ],
            [
              996.5588133335114,
              194.76594529300928,
              1048.9359567165375,
              293.7260690256953
            ],
            [
              960.5252268016338,
              117.53380670398474,
              999.4454591572285,
              206.75454273074865
            ],
            [
              233.04109859466553,
              310.8949882276356,
              263.892479121685,
              364.30298806354403
            ],
            [
              999.2063516676426,
              122.80015981942415,
              1042.4865308701992,
              205.93641667813063
            ],
            [
              318.776384472847,
              119.45399594679475,
              348.2492324113846,
              179.8528707139194
            ],
            [
              769.5605094134808,
              129.44421277567744,
              804.7942707836628,
              178.87947996333241
            ],
            [
              620.0890608727932,
              127.1798248142004,
              659.3956564962864,
              179.33883848786354
            ],
            [
              476.63280203938484,
              132.49412738904357,
              511.13409039378166,
              180.77032310143113
            ]
          ],
          "detector_scores": [
            0.9210799725258099,
            0.8996567592239568,
            0.7839861234698918,
            0.5969254337872926,
            0.5565923511122685,
            0.4862744729810246,
            0.4599956067439408,
            0.4291009784773433,
            0.40247972126138126,
            0.3744595767739948
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
        "frame": 25652,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 34,
        "raw": {
          "frame": 25652,
          "previous_frame": 25651,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 25651,
                "key": "track:1",
                "bbox": [
                  649.5458374023438,
                  386.5860900878906,
                  721.46728515625,
                  586.8141479492188
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 55,
              "consistent_fraction": 0.09090909090909091,
              "median_patch_error": 24.27395248413086,
              "median_forward_backward_error": 8.539508819580078,
              "discontinuity": 22.067229531028055,
              "previous_mean": 0.0,
              "adaptive_ratio": 22.067229531028055,
              "appearance_previous_mean": 5.120712544769049,
              "appearance_adaptive_ratio": 4.740346635728924
            },
            {
              "region": {
                "frame": 25651,
                "key": "track:0",
                "bbox": [
                  733.7998046875,
                  154.87289428710938,
                  776.7005004882812,
                  251.01150512695312
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 21,
              "consistent_fraction": 1.0,
              "median_patch_error": 17.281179428100586,
              "median_forward_backward_error": 0.06898517161607742,
              "discontinuity": 0.0,
              "previous_mean": 0.0,
              "adaptive_ratio": 0.0,
              "appearance_previous_mean": 2.2740044742822647,
              "appearance_adaptive_ratio": 7.599448296404508
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.6397746801376343,
          "discontinuity": 11.033614765514027,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 20.777565956115723
        },
        "decision": {
          "frame": 25652,
          "previous_frame": 25651,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 25652,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "22712df3dd9ecd2ff5a5b4c467953534fe9e4d313741aead53e2992fc8be43ec",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              489.5603482723236,
              356.5212666541338,
              569.0684492588043,
              541.9577650278807
            ],
            [
              621.6594877243042,
              204.02213148027658,
              676.7365655899048,
              333.5435347184539
            ],
            [
              959.8476091623306,
              117.95983727276325,
              1000.0259965658188,
              208.05579240620136
            ],
            [
              621.3368242383003,
              126.5172750428319,
              657.930775821209,
              179.58077832311392
            ],
            [
              769.5539646446705,
              129.70374561101198,
              805.0381660163403,
              179.33442591875792
            ],
            [
              1001.236379057169,
              195.60648243129253,
              1048.980984300375,
              290.41335682570934
            ],
            [
              233.0,
              302.978456646204,
              287.5994222164154,
              406.8606156408787
            ],
            [
              477.11352184414864,
              132.9833933264017,
              511.05997917056084,
              180.73979023098946
            ],
            [
              318.94109803438187,
              120.48666770756245,
              348.2325102686882,
              179.85451798141003
            ],
            [
              1001.0481827557087,
              125.17864912003279,
              1042.4947688281536,
              209.4133470132947
            ]
          ],
          "detector_scores": [
            0.9267882494257832,
            0.9017063578659197,
            0.6166616217556734,
            0.5918894601508745,
            0.5799407741731961,
            0.5599248632607733,
            0.5584376408718122,
            0.5530713453188477,
            0.5359387641608377,
            0.42299999591041765
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
        "frame": 26654,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 35,
        "raw": {
          "frame": 26654,
          "previous_frame": 26653,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 26653,
                "key": "track:2",
                "bbox": [
                  563.930908203125,
                  378.2615966796875,
                  624.8179321289062,
                  581.4981689453125
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 46,
              "consistent_fraction": 0.13043478260869565,
              "median_patch_error": 22.537982940673828,
              "median_forward_backward_error": 10.577412605285645,
              "discontinuity": 19.598246035368547,
              "previous_mean": 0.13240349811056376,
              "adaptive_ratio": 19.598246035368547,
              "appearance_previous_mean": 6.149641834199429,
              "appearance_adaptive_ratio": 3.664926112499016
            },
            {
              "region": {
                "frame": 26653,
                "key": "track:1",
                "bbox": [
                  639.4227294921875,
                  172.32315063476562,
                  676.4832763671875,
                  288.50494384765625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 23,
              "consistent_fraction": 0.7391304347826086,
              "median_patch_error": 26.88258171081543,
              "median_forward_backward_error": 0.32151728868484497,
              "discontinuity": 7.012847402821418,
              "previous_mean": 0.0,
              "adaptive_ratio": 7.012847402821418,
              "appearance_previous_mean": 5.154301151633263,
              "appearance_adaptive_ratio": 5.215562870690442
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.7856788635253906,
          "discontinuity": 13.305546719094982,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 24.71028232574463
        },
        "decision": {
          "frame": 26654,
          "previous_frame": 26653,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 26654,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "dd31578a369f4ee40be916b206cac6129fd0487b2c2be55ac434b583c9cc159e",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              490.14168363809586,
              354.6008597612381,
              569.9271697402,
              537.8720926046371
            ],
            [
              623.61615473032,
              200.51210000365973,
              677.4627370238304,
              332.75280050188303
            ],
            [
              998.6818718910217,
              195.01008453965187,
              1048.9275546073914,
              291.9807765185833
            ],
            [
              770.0661908388138,
              129.58604960888624,
              804.6645563840866,
              179.40485290437937
            ],
            [
              960.2028262615204,
              117.60307441651821,
              999.9827396869659,
              208.12424908578396
            ],
            [
              318.9747003912926,
              120.21195435151458,
              348.0669911503792,
              179.75324195995927
            ],
            [
              233.15414708852768,
              303.9407541155815,
              289.7164770960808,
              402.4013640284538
            ],
            [
              621.3395646512508,
              126.37666621431708,
              657.6027971804142,
              179.65686191990972
            ],
            [
              476.977358430624,
              133.3320893831551,
              511.06380024552345,
              180.479033973068
            ],
            [
              1004.6642845571041,
              124.15424118936062,
              1040.7134639322758,
              196.65654557943344
            ]
          ],
          "detector_scores": [
            0.9250906313120503,
            0.9074135054940408,
            0.7429656332700069,
            0.6495294489149285,
            0.6466656151811003,
            0.5711160452893737,
            0.5632959701163405,
            0.5623829366847236,
            0.558286426406609,
            0.5183760570904962
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
        "frame": 27455,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 36,
        "raw": {
          "frame": 27455,
          "previous_frame": 27454,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 27454,
                "key": "track:0",
                "bbox": [
                  612.17578125,
                  366.75933837890625,
                  683.1573486328125,
                  551.1107177734375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 41,
              "consistent_fraction": 0.14634146341463414,
              "median_patch_error": 22.118764877319336,
              "median_forward_backward_error": 18.324974060058594,
              "discontinuity": 18.881872456248214,
              "previous_mean": 0.0,
              "adaptive_ratio": 18.881872456248214,
              "appearance_previous_mean": 5.150156036019325,
              "appearance_adaptive_ratio": 4.294775677207528
            },
            {
              "region": {
                "frame": 27454,
                "key": "track:1",
                "bbox": [
                  667.6329345703125,
                  139.75828552246094,
                  705.05517578125,
                  260.74371337890625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 24,
              "consistent_fraction": 0.875,
              "median_patch_error": 23.002727508544922,
              "median_forward_backward_error": 0.17670413851737976,
              "discontinuity": 2.8753409385681152,
              "previous_mean": 0.0,
              "adaptive_ratio": 2.8753409385681152,
              "appearance_previous_mean": 4.317584335803986,
              "appearance_adaptive_ratio": 5.327684584593422
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.7963080406188965,
          "discontinuity": 10.878606697408165,
          "photometric_gain": 1.002212389380531,
          "photometric_offset": -0.18141592920353844,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 22.56074619293213
        },
        "decision": {
          "frame": 27455,
          "previous_frame": 27454,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 27455,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "6522546ca3d7a07639ae658b0e4a5b98c176b77955061de8f7c56d7c4342b295",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              667.9397366642952,
              352.6715544164181,
              754.009003341198,
              547.9596013128757
            ],
            [
              604.7931503653526,
              198.40874790400267,
              656.3059039711952,
              333.91179866343737
            ],
            [
              997.2331859469414,
              195.01861642301083,
              1048.9093368649483,
              292.8938713222742
            ],
            [
              960.9257374703884,
              117.36816353350878,
              1001.0820769369602,
              208.19006188958883
            ],
            [
              769.8411015570164,
              130.10649449378252,
              805.1295252740383,
              179.03400465101004
            ],
            [
              233.0,
              304.90641943365335,
              292.3036336302757,
              403.26667203754187
            ],
            [
              319.0092162191868,
              120.80157072469592,
              348.1888080537319,
              179.86599845066667
            ],
            [
              620.5665721297264,
              126.98518148809671,
              659.022326529026,
              181.39346904307604
            ],
            [
              477.34144577383995,
              132.226568993181,
              510.7768031656742,
              180.51885706558824
            ],
            [
              1005.8732915222645,
              124.12702118232846,
              1041.1412024199963,
              186.21378840133548
            ]
          ],
          "detector_scores": [
            0.9241385105348534,
            0.8641306748672948,
            0.8012571707915173,
            0.740779239378524,
            0.6515360048669074,
            0.6286753809669501,
            0.611493335160127,
            0.6049767043412168,
            0.5241605087300604,
            0.4398611858985567
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
        "frame": 28500,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 37,
        "raw": {
          "frame": 28500,
          "previous_frame": 28499,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 28499,
                "key": "track:2",
                "bbox": [
                  721.2791137695312,
                  391.13287353515625,
                  792.0564575195312,
                  573.8209838867188
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 47,
              "consistent_fraction": 0.0,
              "median_patch_error": 24.00113296508789,
              "median_forward_backward_error": 17.11852264404297,
              "discontinuity": 24.00113296508789,
              "previous_mean": 0.0,
              "adaptive_ratio": 24.00113296508789,
              "appearance_previous_mean": 5.094068765640259,
              "appearance_adaptive_ratio": 4.711584014526207
            },
            {
              "region": {
                "frame": 28499,
                "key": "track:3",
                "bbox": [
                  700.00244140625,
                  170.24072265625,
                  745.9683227539062,
                  293.91851806640625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 25,
              "consistent_fraction": 0.8,
              "median_patch_error": 28.65894317626953,
              "median_forward_backward_error": 0.3498556911945343,
              "discontinuity": 5.731788635253905,
              "previous_mean": 0.0,
              "adaptive_ratio": 5.731788635253905,
              "appearance_previous_mean": 3.9424603283405304,
              "appearance_adaptive_ratio": 7.269304137381827
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.5284862518310547,
          "discontinuity": 14.866460800170898,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 26.33003807067871
        },
        "decision": {
          "frame": 28500,
          "previous_frame": 28499,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 28500,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "4f0516b22e0ccebc6c74321e6f7ce6153357f91624e009a259b77f2aec15c8e1",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              594.3915003538132,
              335.46215000748634,
              666.66319668293,
              531.0969707667828
            ],
            [
              681.0886362195015,
              213.42981129139662,
              746.57635897398,
              333.1100032404065
            ],
            [
              962.1119456589222,
              118.66634777933359,
              1000.3589939773083,
              207.66371525079012
            ],
            [
              998.5677427351475,
              195.11873088032007,
              1048.9235921800137,
              291.72207533568144
            ],
            [
              233.0584317445755,
              310.3263556137681,
              293.6354560852051,
              403.84368761628866
            ],
            [
              1007.2670020163059,
              122.87029355019331,
              1043.5023957192898,
              203.2849804237485
            ],
            [
              770.023677200079,
              129.49060431867838,
              804.5569750368595,
              179.2208904698491
            ],
            [
              622.122612953186,
              127.15265979245305,
              658.4970092773438,
              181.23551235720515
            ],
            [
              318.90877240896225,
              120.4158924818039,
              348.11312371492386,
              179.76830105483532
            ],
            [
              477.65760400891304,
              132.80640027672052,
              510.81686517596245,
              180.47790906578302
            ]
          ],
          "detector_scores": [
            0.9296765748383065,
            0.9135154587237955,
            0.7264147111481488,
            0.6693819251702727,
            0.600283212117756,
            0.5058911696652099,
            0.44049664147934675,
            0.43776293924867704,
            0.424594645241362,
            0.4212549999407677
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
        "frame": 28649,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 38,
        "raw": {
          "frame": 28649,
          "previous_frame": 28648,
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
                "frame": 28648,
                "key": "track:0",
                "bbox": [
                  526.9649047851562,
                  416.7134704589844,
                  653.1380615234375,
                  570.8085327148438
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 53,
              "consistent_fraction": 0.20754716981132076,
              "median_patch_error": 23.389667510986328,
              "median_forward_backward_error": 6.8830461502075195,
              "discontinuity": 18.535208216253316,
              "previous_mean": 0.0,
              "adaptive_ratio": 18.535208216253316,
              "appearance_previous_mean": 7.160271167755127,
              "appearance_adaptive_ratio": 3.2665896253087587
            },
            {
              "region": {
                "frame": 28648,
                "key": "track:2",
                "bbox": [
                  650.9295654296875,
                  219.433349609375,
                  702.112548828125,
                  360.8843994140625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 26,
              "consistent_fraction": 0.38461538461538464,
              "median_patch_error": 26.686790466308594,
              "median_forward_backward_error": 3.4525084495544434,
              "discontinuity": 16.422640286959137,
              "previous_mean": 0.0,
              "adaptive_ratio": 16.422640286959137,
              "appearance_previous_mean": 6.881873607635498,
              "appearance_adaptive_ratio": 3.877837924355276
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.1805200576782227,
          "discontinuity": 17.478924251606227,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 25.03822898864746
        },
        "decision": {
          "frame": 28649,
          "previous_frame": 28648,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 28649,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "9c8b78cd813de362e4caffd264eacecb945617474fa742c0612e8b0d7c5b0bac",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              613.6281596422195,
              333.6259347498417,
              687.7310780286789,
              527.2824582755566
            ],
            [
              544.0471962094307,
              212.97806135565042,
              607.0331088900566,
              334.04514714330435
            ],
            [
              233.04859179258347,
              312.6018437296152,
              292.13731199502945,
              410.525742277503
            ],
            [
              995.6944782733917,
              195.7204256877303,
              1048.8612983226776,
              293.96973631531
            ],
            [
              959.4207035899162,
              116.8604660704732,
              1000.0943472981453,
              207.3994101509452
            ],
            [
              1006.3126087486744,
              123.17315708100796,
              1041.7643203437328,
              199.73964381217957
            ],
            [
              770.0957988500595,
              130.0684538409114,
              804.7183128595352,
              179.75838079303503
            ],
            [
              621.7891200482845,
              127.4216019846499,
              658.0042988359928,
              180.9257802478969
            ],
            [
              318.91122099757195,
              120.0644311234355,
              348.3913736641407,
              179.98415953665972
            ],
            [
              477.19581934809685,
              133.25955004617572,
              510.7232108414173,
              180.94210629537702
            ]
          ],
          "detector_scores": [
            0.9248231994134681,
            0.9139851308421094,
            0.8578463906673576,
            0.7907394871308259,
            0.6566383814977818,
            0.5286497425334904,
            0.5089019666106878,
            0.5038071135035116,
            0.49937784703892735,
            0.44607817015660123
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
        "frame": 29128,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 39,
        "raw": {
          "frame": 29128,
          "previous_frame": 29127,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 29127,
                "key": "track:0",
                "bbox": [
                  704.4622802734375,
                  319.9671325683594,
                  795.5250854492188,
                  501.31304931640625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 39,
              "consistent_fraction": 0.20512820512820512,
              "median_patch_error": 17.643495559692383,
              "median_forward_backward_error": 4.52902364730835,
              "discontinuity": 14.024316983345228,
              "previous_mean": 0.0,
              "adaptive_ratio": 14.024316983345228,
              "appearance_previous_mean": 2.5915355309844017,
              "appearance_adaptive_ratio": 6.80812412129671
            },
            {
              "region": {
                "frame": 29127,
                "key": "track:1",
                "bbox": [
                  757.0639038085938,
                  140.82427978515625,
                  791.9906005859375,
                  259.2477722167969
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 18,
              "consistent_fraction": 1.0,
              "median_patch_error": 19.256271362304688,
              "median_forward_backward_error": 0.08335678279399872,
              "discontinuity": 0.0,
              "previous_mean": 0.0,
              "adaptive_ratio": 0.0,
              "appearance_previous_mean": 4.1081172078847885,
              "appearance_adaptive_ratio": 4.687371461881797
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 2.213399887084961,
          "discontinuity": 7.012158491672614,
          "photometric_gain": 1.0089285714285714,
          "photometric_offset": -0.7321428571428612,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 18.449883460998535
        },
        "decision": {
          "frame": 29128,
          "previous_frame": 29127,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 29128,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "48aa71ccf8a00c349451b0942a052a970d8fa68bb9692b1b4b82af9b0b4d16e9",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              574.0083422660828,
              343.28026022017,
              661.8964953422546,
              534.3297297805548
            ],
            [
              694.0657804310322,
              198.52963763475418,
              744.5110132396221,
              332.91895228624344
            ],
            [
              233.02134269475937,
              309.30768448114395,
              291.87186735868454,
              410.4820747971535
            ],
            [
              960.0762428939342,
              120.09446683526039,
              1000.2685618698597,
              203.6494091451168
            ],
            [
              997.6316629648209,
              195.2205178067088,
              1048.9532655477524,
              292.59255654364824
            ],
            [
              319.05833998322487,
              120.62972567230463,
              347.9225305020809,
              179.88860427588224
            ],
            [
              1005.0865027010441,
              122.4134620577097,
              1035.6908296048641,
              196.46630565822124
            ],
            [
              477.52107429504395,
              132.4737553410232,
              511.0926923751831,
              180.40720028057694
            ],
            [
              620.5558141469955,
              126.89103293418884,
              658.1135946512222,
              180.13364161551
            ],
            [
              769.5902694165707,
              129.69336942955852,
              804.9034191668034,
              178.86919771507382
            ]
          ],
          "detector_scores": [
            0.9422489035113045,
            0.883987651944996,
            0.8549687351599186,
            0.7576572890808588,
            0.7015373866003984,
            0.4927202839208915,
            0.4566990354679705,
            0.4268241873776853,
            0.4240428883849343,
            0.41809620156156624
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
        "frame": 29689,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 40,
        "raw": {
          "frame": 29689,
          "previous_frame": 29688,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 29688,
                "key": "track:0",
                "bbox": [
                  587.016357421875,
                  339.2743835449219,
                  660.2806396484375,
                  460.63385009765625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 37,
              "consistent_fraction": 0.0,
              "median_patch_error": 34.23533248901367,
              "median_forward_backward_error": 29.458295822143555,
              "discontinuity": 34.23533248901367,
              "previous_mean": 0.0,
              "adaptive_ratio": 34.23533248901367,
              "appearance_previous_mean": 8.713949203491211,
              "appearance_adaptive_ratio": 3.9287964262285824
            },
            {
              "region": {
                "frame": 29688,
                "key": "track:3",
                "bbox": [
                  606.8404541015625,
                  228.00433349609375,
                  647.736083984375,
                  343.40850830078125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 20,
              "consistent_fraction": 0.7,
              "median_patch_error": 28.177722930908203,
              "median_forward_backward_error": 0.4011939764022827,
              "discontinuity": 8.453316879272462,
              "previous_mean": 0.0,
              "adaptive_ratio": 8.453316879272462,
              "appearance_previous_mean": 9.503790855407715,
              "appearance_adaptive_ratio": 2.964892994764811
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.8421556949615479,
          "discontinuity": 21.344324684143068,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 31.206527709960938
        },
        "decision": {
          "frame": 29689,
          "previous_frame": 29688,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 29689,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "0a319f36282759d139bf50def8ac43f5cd0d03728fa1d73bbd9e204379bc0258",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              492.64832705259323,
              351.588500097394,
              574.9426391720772,
              536.6439871042967
            ],
            [
              622.3616201281548,
              212.00980714708567,
              680.4443853497505,
              336.2150497660041
            ],
            [
              233.0,
              306.10840234160423,
              291.36629992723465,
              410.54983499646187
            ],
            [
              996.4266533851624,
              196.09145722538233,
              1048.8643260002136,
              296.54016091674566
            ],
            [
              961.5506853759289,
              118.08531827479601,
              1000.6523595154285,
              207.74809017032385
            ],
            [
              769.5909761786461,
              130.08639279007912,
              804.2714963555336,
              179.0198963433504
            ],
            [
              620.9187098741531,
              126.8294150494039,
              657.9852284193039,
              180.17164332047105
            ],
            [
              319.16858726739883,
              120.86923011764884,
              348.1449508070946,
              179.89409593120217
            ],
            [
              477.0085365176201,
              133.0688587874174,
              511.3673933148384,
              180.76485435664654
            ],
            [
              1002.2938531935215,
              123.47116357833147,
              1042.570770829916,
              211.1888035312295
            ]
          ],
          "detector_scores": [
            0.9145904097463501,
            0.9135759039591602,
            0.8350913543555317,
            0.7806953158695454,
            0.7218654793685197,
            0.5874646481594225,
            0.5717229356161713,
            0.5404409550765704,
            0.5247584585999736,
            0.45313824752660026
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
        "frame": 30530,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 41,
        "raw": {
          "frame": 30530,
          "previous_frame": 30529,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 30529,
                "key": "track:3",
                "bbox": [
                  627.9120483398438,
                  353.5629577636719,
                  689.5184326171875,
                  543.1678466796875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 45,
              "consistent_fraction": 0.0,
              "median_patch_error": 35.01565933227539,
              "median_forward_backward_error": 18.876737594604492,
              "discontinuity": 35.01565933227539,
              "previous_mean": 0.18623837180759584,
              "adaptive_ratio": 35.01565933227539,
              "appearance_previous_mean": 9.08655834197998,
              "appearance_adaptive_ratio": 3.853566775717791
            },
            {
              "region": {
                "frame": 30529,
                "key": "track:4",
                "bbox": [
                  746.6742553710938,
                  209.9554443359375,
                  812.0540771484375,
                  345.89202880859375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 29,
              "consistent_fraction": 0.3793103448275862,
              "median_patch_error": 20.786422729492188,
              "median_forward_backward_error": 5.996240615844727,
              "discontinuity": 12.90191755623653,
              "previous_mean": 0.3404182365962436,
              "adaptive_ratio": 12.90191755623653,
              "appearance_previous_mean": 9.854538917541504,
              "appearance_adaptive_ratio": 2.1093247389273038
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.75,
          "background_patch_error": 3.160430908203125,
          "discontinuity": 23.95878844425596,
          "photometric_gain": 1.008849557522124,
          "photometric_offset": -1.7256637168141538,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 27.90104103088379
        },
        "decision": {
          "frame": 30530,
          "previous_frame": 30529,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 30530,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b23d9909a1875af6808d19eddb590725f67b240fec9cdb2bcbed5c34e029c587",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              593.2668762207031,
              354.1434555053711,
              659.937162399292,
              529.9866895675659
            ],
            [
              695.1308070421219,
              190.1410046890378,
              754.4786003828049,
              329.92233216017485
            ],
            [
              997.1814692020416,
              194.9729144871235,
              1048.943252325058,
              294.9445016980171
            ],
            [
              233.04495918750763,
              310.46314983814955,
              298.38652658462524,
              404.78401846438646
            ],
            [
              770.4839297831059,
              130.40402903407812,
              804.3691891133785,
              178.48805575817823
            ],
            [
              318.88646760582924,
              119.99890011921525,
              348.4616273343563,
              179.96735924109817
            ],
            [
              620.6605988442898,
              127.45202259346843,
              658.0738381445408,
              179.59014644101262
            ],
            [
              1002.9022187888622,
              123.02277690917253,
              1040.4996843636036,
              202.47968427091837
            ],
            [
              477.00551187992096,
              133.36924339830875,
              511.7853435277939,
              181.10548819601536
            ],
            [
              960.4246583580971,
              121.76760948449373,
              1000.7967867255211,
              205.68899206072092
            ]
          ],
          "detector_scores": [
            0.9079231007544974,
            0.8918483516291573,
            0.7718486200633741,
            0.7356714076246171,
            0.6033252247510833,
            0.5933055593190243,
            0.5559980933784009,
            0.5364164252943401,
            0.5352146761543836,
            0.38331222764223416
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
        "frame": 31564,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 42,
        "raw": {
          "frame": 31564,
          "previous_frame": 31563,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 31563,
                "key": "track:5",
                "bbox": [
                  503.50927734375,
                  346.7003479003906,
                  585.4041748046875,
                  528.2807006835938
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 35,
              "consistent_fraction": 0.0,
              "median_patch_error": 35.31657409667969,
              "median_forward_backward_error": 59.994293212890625,
              "discontinuity": 35.31657409667969,
              "previous_mean": 0.12134223235280876,
              "adaptive_ratio": 35.31657409667969,
              "appearance_previous_mean": 10.237174034118652,
              "appearance_adaptive_ratio": 3.4498362515842675
            },
            {
              "region": {
                "frame": 31563,
                "key": "track:6",
                "bbox": [
                  613.7262573242188,
                  196.40834045410156,
                  685.8366088867188,
                  336.46405029296875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 43,
              "consistent_fraction": 0.4883720930232558,
              "median_patch_error": 22.838151931762695,
              "median_forward_backward_error": 1.0989680290222168,
              "discontinuity": 11.684635872064636,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.684635872064636,
              "appearance_previous_mean": 7.956012725830078,
              "appearance_adaptive_ratio": 2.8705524637506046
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9625,
          "background_patch_error": 2.0485048294067383,
          "discontinuity": 23.50060498437216,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 0.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 29.07736301422119
        },
        "decision": {
          "frame": 31564,
          "previous_frame": 31563,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 31564,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "acc0ec3f43d73ba0a0ea919ce8c6322167c147dda3ac8e2650e2458428275e8e",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              582.088754594326,
              348.8925624191761,
              662.0248585343361,
              528.2823840081692
            ],
            [
              696.6918787956238,
              214.22581034898758,
              760.7545685768127,
              332.22841042280197
            ],
            [
              998.565835237503,
              195.41058360785246,
              1048.9597404003143,
              292.7859947755933
            ],
            [
              770.2485080957413,
              130.1712694503367,
              804.5798057317734,
              179.63058353587985
            ],
            [
              621.1735302805901,
              127.23820773139596,
              658.0567162632942,
              180.6582401804626
            ],
            [
              477.4811718761921,
              133.06376806646585,
              511.00925037264824,
              181.29510036855936
            ],
            [
              233.0,
              310.7381541579962,
              298.23295098543167,
              403.86022444069386
            ],
            [
              1002.4399933516979,
              121.69309984147549,
              1045.4038653671741,
              212.24591854214668
            ]
          ],
          "detector_scores": [
            0.9278662230581369,
            0.9022059971921376,
            0.5695612388942923,
            0.49484283140058155,
            0.4425385051776922,
            0.42962063791877975,
            0.4122196739605925,
            0.35956539331223897
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
        "frame": 31726,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 43,
        "raw": {
          "frame": 31726,
          "previous_frame": 31725,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 31725,
                "key": "track:0",
                "bbox": [
                  602.9378662109375,
                  373.66729736328125,
                  678.9785766601562,
                  552.2724609375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 45,
              "consistent_fraction": 0.022222222222222223,
              "median_patch_error": 35.679351806640625,
              "median_forward_backward_error": 41.535213470458984,
              "discontinuity": 34.88647732204861,
              "previous_mean": 0.0,
              "adaptive_ratio": 34.88647732204861,
              "appearance_previous_mean": 9.78156852722168,
              "appearance_adaptive_ratio": 3.6476104734477444
            },
            {
              "region": {
                "frame": 31725,
                "key": "track:2",
                "bbox": [
                  705.1542358398438,
                  182.11024475097656,
                  754.4322509765625,
                  324.30328369140625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 27,
              "consistent_fraction": 0.5925925925925926,
              "median_patch_error": 26.596654891967773,
              "median_forward_backward_error": 0.5062170624732971,
              "discontinuity": 10.835674215246131,
              "previous_mean": 0.6913895077175567,
              "adaptive_ratio": 10.835674215246131,
              "appearance_previous_mean": 12.719388008117676,
              "appearance_adaptive_ratio": 2.091032593312937
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 2.3261055946350098,
          "discontinuity": 22.86107576864737,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 0.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 31.1380033493042
        },
        "decision": {
          "frame": 31726,
          "previous_frame": 31725,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 31726,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "7cbbaa4a0d9d5877f4728fc3294691cb3d944e793129f3e1b50878746a6e8ff7",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              688.9642212986946,
              354.32404550909996,
              746.4862582087517,
              526.6521436274052
            ],
            [
              603.0486578941345,
              204.5492295846343,
              658.1980595588684,
              338.72647515684366
            ],
            [
              999.6859832108021,
              194.7099977657199,
              1048.9276108443737,
              292.33254946023226
            ],
            [
              770.140069514513,
              129.7416144348681,
              804.3659729659557,
              179.73038182780147
            ],
            [
              319.07475358247757,
              119.8929343111813,
              348.11894196271896,
              179.64290940389037
            ],
            [
              477.6095593869686,
              132.65183205902576,
              510.93402352929115,
              181.18240344524384
            ],
            [
              621.1295635998249,
              126.71439499780536,
              657.8745190799236,
              180.0690224505961
            ],
            [
              1003.3494259119034,
              122.24122523516417,
              1039.4068645238876,
              207.74838342517614
            ],
            [
              233.0,
              308.37043280899525,
              298.65834879875183,
              404.21713392436504
            ]
          ],
          "detector_scores": [
            0.8990653545277958,
            0.8372907453559312,
            0.7806385712387827,
            0.44287496718420255,
            0.4336208534109191,
            0.41318438101015137,
            0.4090368213864544,
            0.4056499078070917,
            0.36412619027343307
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
        "frame": 32033,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 44,
        "raw": {
          "frame": 32033,
          "previous_frame": 32032,
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
                "frame": 32032,
                "key": "track:0",
                "bbox": [
                  445.8158264160156,
                  391.0544128417969,
                  511.50347900390625,
                  584.847412109375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 34,
              "consistent_fraction": 0.0,
              "median_patch_error": 36.53358840942383,
              "median_forward_backward_error": 71.29375457763672,
              "discontinuity": 36.53358840942383,
              "previous_mean": 0.0,
              "adaptive_ratio": 36.53358840942383,
              "appearance_previous_mean": 2.8243870437145233,
              "appearance_adaptive_ratio": 12.93505027603309
            },
            {
              "region": {
                "frame": 32032,
                "key": "track:1",
                "bbox": [
                  476.0755920410156,
                  190.82949829101562,
                  549.2471923828125,
                  332.0155029296875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 33,
              "consistent_fraction": 0.5454545454545454,
              "median_patch_error": 18.776432037353516,
              "median_forward_backward_error": 0.6971856951713562,
              "discontinuity": 8.53474183516069,
              "previous_mean": 0.0,
              "adaptive_ratio": 8.53474183516069,
              "appearance_previous_mean": 5.253277316689491,
              "appearance_adaptive_ratio": 3.574232028014474
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.9285714626312256,
          "discontinuity": 22.534165122292258,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 0.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 27.655010223388672
        },
        "decision": {
          "frame": 32033,
          "previous_frame": 32032,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 32033,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "2eaea91325df26da9c385e347cb1ea2d62706be546ed4bc0c2f21f5d8c86eb1e",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              509.437707901001,
              351.6034194380045,
              591.4729347229004,
              529.6955699771643
            ],
            [
              622.5680159330368,
              202.61701918393373,
              681.3310662508011,
              336.30982606858015
            ],
            [
              999.5412611365318,
              196.25787477195263,
              1049.0,
              291.84724475443363
            ],
            [
              233.0,
              305.2575783729553,
              299.2022728919983,
              404.6544044017792
            ],
            [
              770.2436063587666,
              130.0868005976081,
              804.5050394237041,
              179.51964385062456
            ],
            [
              477.7769829630852,
              133.22481996566057,
              511.01902800798416,
              181.28029099851847
            ],
            [
              621.2554918825626,
              127.20510658994317,
              657.4638675153255,
              180.27853929623961
            ],
            [
              319.0903707444668,
              120.08538280799985,
              348.2516080439091,
              179.84666654095054
            ]
          ],
          "detector_scores": [
            0.9108530727150651,
            0.8803052673282348,
            0.6979083876961912,
            0.6958571139507735,
            0.5174989727588303,
            0.45765056506601676,
            0.4482158710929215,
            0.40729195943419594
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
        "frame": 32206,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 45,
        "raw": {
          "frame": 32206,
          "previous_frame": 32205,
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
                "frame": 32205,
                "key": "track:0",
                "bbox": [
                  566.1629638671875,
                  321.7315368652344,
                  619.8885498046875,
                  492.0140075683594
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 39,
              "consistent_fraction": 0.1794871794871795,
              "median_patch_error": 28.115291595458984,
              "median_forward_backward_error": 21.254831314086914,
              "discontinuity": 23.06895720653045,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.06895720653045,
              "appearance_previous_mean": 7.023189544677734,
              "appearance_adaptive_ratio": 4.003208430671663
            },
            {
              "region": {
                "frame": 32205,
                "key": "track:1",
                "bbox": [
                  553.5043334960938,
                  270.5116271972656,
                  594.69970703125,
                  379.8844909667969
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 23,
              "consistent_fraction": 0.08695652173913043,
              "median_patch_error": 29.577665328979492,
              "median_forward_backward_error": 28.89417266845703,
              "discontinuity": 27.005694430807363,
              "previous_mean": 0.0,
              "adaptive_ratio": 27.005694430807363,
              "appearance_previous_mean": 8.894452095031738,
              "appearance_adaptive_ratio": 3.3254061085450086
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.7128684520721436,
          "discontinuity": 25.037325818668904,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 28.84647846221924
        },
        "decision": {
          "frame": 32206,
          "previous_frame": 32205,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 32206,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "f28f52cda4bcdb5dd451b0ab435374b9bf8afd64ee09dad0769bd62ad23be1af",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              561.8976716399193,
              214.49898640811443,
              625.1882610917091,
              331.4314078837633
            ],
            [
              617.3779899477959,
              350.02936485409737,
              691.0676181912422,
              526.6040131747723
            ],
            [
              998.1779292523861,
              195.92818758636713,
              1048.9542671740055,
              294.4958630129695
            ],
            [
              769.9974099695683,
              130.14155906811357,
              804.6816843450069,
              178.9827102534473
            ],
            [
              621.0356812775135,
              127.17816150933504,
              657.3551325500011,
              180.88379210978746
            ],
            [
              318.8272561430931,
              120.43385892361403,
              348.17181688547134,
              179.93263832479715
            ],
            [
              477.4187929034233,
              133.28407348319888,
              511.20489579439163,
              181.2703042961657
            ],
            [
              233.0,
              311.00377432256937,
              297.13277930021286,
              403.65186228603125
            ]
          ],
          "detector_scores": [
            0.925848349302129,
            0.9071402478375441,
            0.6977111061031435,
            0.5674785815635174,
            0.5245819826915284,
            0.48027907193037,
            0.4731564189765259,
            0.3606807815555976
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
        "frame": 32859,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 46,
        "raw": {
          "frame": 32859,
          "previous_frame": 32858,
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
                "frame": 32858,
                "key": "track:0",
                "bbox": [
                  734.8411254882812,
                  299.21795654296875,
                  786.8939819335938,
                  466.0817565917969
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 28,
              "consistent_fraction": 0.14285714285714285,
              "median_patch_error": 27.261621475219727,
              "median_forward_backward_error": 5.930110931396484,
              "discontinuity": 23.36710412161691,
              "previous_mean": 0.0,
              "adaptive_ratio": 23.36710412161691,
              "appearance_previous_mean": 4.441149279475212,
              "appearance_adaptive_ratio": 6.138415927879167
            },
            {
              "region": {
                "frame": 32858,
                "key": "track:1",
                "bbox": [
                  766.7252197265625,
                  198.94424438476562,
                  829.2230224609375,
                  353.91888427734375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 38,
              "consistent_fraction": 0.4473684210526316,
              "median_patch_error": 24.310195922851562,
              "median_forward_backward_error": 2.2510645389556885,
              "discontinuity": 13.434581957365335,
              "previous_mean": 0.0,
              "adaptive_ratio": 13.434581957365335,
              "appearance_previous_mean": 4.370890274643898,
              "appearance_adaptive_ratio": 5.561840813959153
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.8518991470336914,
          "discontinuity": 18.40084303949112,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 0.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 25.785908699035645
        },
        "decision": {
          "frame": 32859,
          "previous_frame": 32858,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 32859,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "44a913e73e791199aca6f23f740486d00099cf66c23a55e7fb80ea4ea073fb0f",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              688.1988846063614,
              352.61048409342766,
              766.445659995079,
              532.9360819160938
            ],
            [
              605.4249105453491,
              206.2955988869071,
              664.1967763900757,
              338.33967200666666
            ],
            [
              233.0,
              304.54095973819494,
              299.249396443367,
              405.0333034172654
            ],
            [
              999.6563341617584,
              195.7899683266878,
              1048.930120229721,
              292.28989462554455
            ],
            [
              770.4313542842865,
              130.18599405139685,
              804.6130068302155,
              179.40071984380484
            ],
            [
              621.6644304990768,
              126.84344087913632,
              657.386733174324,
              180.87576196715236
            ],
            [
              318.88631865382195,
              120.09003364667296,
              348.1230047047138,
              179.85667844489217
            ],
            [
              477.50842249393463,
              133.08561555296183,
              511.2373946905136,
              181.62171296030283
            ]
          ],
          "detector_scores": [
            0.9049620574173346,
            0.8928157205226619,
            0.8334660810965951,
            0.7437626950605556,
            0.5953895216329305,
            0.5382775669931411,
            0.5069467127470406,
            0.5036216340875842
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
        "frame": 33371,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 47,
        "raw": {
          "frame": 33371,
          "previous_frame": 33370,
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
                "frame": 33370,
                "key": "track:0",
                "bbox": [
                  617.8829345703125,
                  347.8324890136719,
                  694.9610595703125,
                  519.2366943359375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 47,
              "consistent_fraction": 0.0,
              "median_patch_error": 41.83967590332031,
              "median_forward_backward_error": 51.167999267578125,
              "discontinuity": 41.83967590332031,
              "previous_mean": 0.0,
              "adaptive_ratio": 41.83967590332031,
              "appearance_previous_mean": 4.641829319298267,
              "appearance_adaptive_ratio": 9.013617913388824
            },
            {
              "region": {
                "frame": 33370,
                "key": "track:1",
                "bbox": [
                  577.2047729492188,
                  207.41148376464844,
                  682.8931274414062,
                  321.9983215332031
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 44,
              "consistent_fraction": 0.45454545454545453,
              "median_patch_error": 27.54290771484375,
              "median_forward_backward_error": 1.443692684173584,
              "discontinuity": 15.02340420809659,
              "previous_mean": 0.0,
              "adaptive_ratio": 15.02340420809659,
              "appearance_previous_mean": 5.673575945198536,
              "appearance_adaptive_ratio": 4.8545939951950245
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.7751559019088745,
          "discontinuity": 28.431540055708453,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 0.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 34.69129180908203
        },
        "decision": {
          "frame": 33371,
          "previous_frame": 33370,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 33371,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "96c24cdb2888e164809e6397f874305d9936335423b8c2648322516aafa8582f",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              509.64314007759094,
              351.2209601253271,
              559.1934297084808,
              527.7492925077677
            ],
            [
              623.5899118185043,
              190.3730792477727,
              690.4893652200699,
              336.86118184775114
            ],
            [
              997.9832398593426,
              194.8718881905079,
              1048.8247397243977,
              291.5480973124504
            ],
            [
              770.1790554225445,
              129.060349047184,
              804.1716392338276,
              179.9618859142065
            ],
            [
              621.1815782487392,
              126.56486938893795,
              657.4604476988316,
              180.7950321137905
            ],
            [
              477.26394817233086,
              133.4968000948429,
              511.24870136380196,
              181.3849050849676
            ],
            [
              1002.5429191887379,
              122.15864191949368,
              1041.9002132117748,
              210.34270371496677
            ],
            [
              233.0,
              306.32461822777987,
              290.34273517131805,
              410.5053198263049
            ],
            [
              318.9331093430519,
              120.23627846688032,
              347.8550962805748,
              179.8634943291545
            ],
            [
              960.8600876331329,
              125.2025814652443,
              1005.0456244945526,
              212.74742099642754
            ]
          ],
          "detector_scores": [
            0.9151344413550917,
            0.899967125614293,
            0.6539799541292872,
            0.5730710522804588,
            0.5336691066590649,
            0.5187320020361835,
            0.5010590537445926,
            0.4484879524703995,
            0.41449225324920436,
            0.38389186949531107
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
        "frame": 34352,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 48,
        "raw": {
          "frame": 34352,
          "previous_frame": 34351,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 34351,
                "key": "track:2",
                "bbox": [
                  705.7149047851562,
                  325.37274169921875,
                  750.2391967773438,
                  498.7105407714844
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 27,
              "consistent_fraction": 0.0,
              "median_patch_error": 36.028839111328125,
              "median_forward_backward_error": 22.932798385620117,
              "discontinuity": 36.028839111328125,
              "previous_mean": 0.0,
              "adaptive_ratio": 36.028839111328125,
              "appearance_previous_mean": 7.886798143386841,
              "appearance_adaptive_ratio": 4.56824663904181
            },
            {
              "region": {
                "frame": 34351,
                "key": "track:3",
                "bbox": [
                  759.0567016601562,
                  251.97415161132812,
                  812.0069580078125,
                  390.1683349609375
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 35,
              "consistent_fraction": 0.5428571428571428,
              "median_patch_error": 19.78153419494629,
              "median_forward_backward_error": 0.7510067224502563,
              "discontinuity": 9.042987060546876,
              "previous_mean": 0.0,
              "adaptive_ratio": 9.042987060546876,
              "appearance_previous_mean": 12.198377132415771,
              "appearance_adaptive_ratio": 1.6216529445035075
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 2.55452823638916,
          "discontinuity": 22.5359130859375,
          "photometric_gain": 0.9824561403508771,
          "photometric_offset": 1.4385964912280684,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 27.905186653137207
        },
        "decision": {
          "frame": 34352,
          "previous_frame": 34351,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 34352,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "a9b4f3c0e98b9ecd8bbcac3d4028f049b02ab48943f3109e3c822d712c46bb19",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              506.90545386075974,
              352.6963069587946,
              590.1554420590401,
              531.8433685153723
            ],
            [
              621.555418908596,
              201.42353150248528,
              681.0353174805641,
              336.2111595571041
            ],
            [
              233.0,
              304.98199670761824,
              295.84986782073975,
              411.4726117923856
            ],
            [
              998.0320505201817,
              195.47800014913082,
              1048.9222303330898,
              292.5244985073805
            ],
            [
              769.7098945975304,
              129.25728571787477,
              804.6288352608681,
              179.40210134908557
            ],
            [
              318.9691785275936,
              120.22542116418481,
              348.45960584282875,
              179.71230083331466
            ],
            [
              621.8004115223885,
              127.3465081229806,
              657.2614037394524,
              179.84994962066412
            ],
            [
              477.8619631230831,
              133.0164601020515,
              510.9625007212162,
              180.49376544728875
            ],
            [
              1001.9393002986908,
              122.52331349253654,
              1040.7217581272125,
              209.88210114836693
            ]
          ],
          "detector_scores": [
            0.9171319455552474,
            0.8468746928260218,
            0.8468263313948615,
            0.7575328540248238,
            0.5297895300707048,
            0.5269189412595949,
            0.4621540773463138,
            0.46089391310722955,
            0.4303288766666842
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
        "frame": 34535,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 49,
        "raw": {
          "frame": 34535,
          "previous_frame": 34534,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "correspondence_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 34534,
                "key": "track:0",
                "bbox": [
                  974.7173461914062,
                  488.83026123046875,
                  1047.073486328125,
                  709.3126220703125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 41,
              "consistent_fraction": 0.0975609756097561,
              "median_patch_error": 25.260948181152344,
              "median_forward_backward_error": 13.155330657958984,
              "discontinuity": 22.79646543177163,
              "previous_mean": 0.497369877127714,
              "adaptive_ratio": 22.79646543177163,
              "appearance_previous_mean": 12.80752182006836,
              "appearance_adaptive_ratio": 1.9723525390814063
            },
            {
              "region": {
                "frame": 34534,
                "key": "track:1",
                "bbox": [
                  689.6739501953125,
                  174.9984130859375,
                  743.4485473632812,
                  306.539794921875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 27,
              "consistent_fraction": 0.7407407407407407,
              "median_patch_error": 31.44614601135254,
              "median_forward_backward_error": 0.21116101741790771,
              "discontinuity": 8.152704521461771,
              "previous_mean": 0.0,
              "adaptive_ratio": 8.152704521461771,
              "appearance_previous_mean": 10.774908065795898,
              "appearance_adaptive_ratio": 2.9184607255421384
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 2.3108348846435547,
          "discontinuity": 15.4745849766167,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": false,
          "appearance_discontinuity": 28.35354709625244
        },
        "decision": {
          "frame": 34535,
          "previous_frame": 34534,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 34535,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "d70b5e5bcffe2ec2ef7f7fa32a7d4c20f39e1c4fbb438991fd681de3495039fc",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              597.1856424212456,
              341.8756427913904,
              668.6644580960274,
              525.4512191861868
            ],
            [
              694.1555270552635,
              213.71438763290644,
              759.5385456681252,
              332.249511025846
            ],
            [
              233.0,
              311.035294637084,
              295.99224162101746,
              411.5191247612238
            ],
            [
              998.3132658302784,
              195.18263294547796,
              1048.9495706260204,
              293.6907043233514
            ],
            [
              769.6911889612675,
              129.44556449726224,
              804.6138838231564,
              179.47909907624125
            ],
            [
              621.784029841423,
              127.17183132842183,
              658.0040875673294,
              180.01904540881515
            ],
            [
              477.4367780983448,
              133.27820609509945,
              511.6373414695263,
              181.09020228683949
            ],
            [
              319.1208998262882,
              120.47342312708497,
              348.80408319830894,
              179.7950170300901
            ],
            [
              1002.7662864029408,
              122.83239036053419,
              1041.755152195692,
              213.84780026227236
            ],
            [
              960.3960838913918,
              121.42099141329527,
              1002.2639579176903,
              207.38745085150003
            ]
          ],
          "detector_scores": [
            0.9320510491230678,
            0.9057797207492219,
            0.807892693569097,
            0.7231777551284658,
            0.6311500526097349,
            0.5639906068537733,
            0.5471652935579193,
            0.510222440848172,
            0.5074005682475685,
            0.3798785693833692
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
        "frame": 34728,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 50,
        "raw": {
          "frame": 34728,
          "previous_frame": 34727,
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
                "frame": 34727,
                "key": "track:0",
                "bbox": [
                  686.2200927734375,
                  332.43841552734375,
                  759.324462890625,
                  496.1334228515625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 33,
              "consistent_fraction": 0.0,
              "median_patch_error": 36.323768615722656,
              "median_forward_backward_error": 37.92601776123047,
              "discontinuity": 36.323768615722656,
              "previous_mean": 0.0,
              "adaptive_ratio": 36.323768615722656,
              "appearance_previous_mean": 5.450520992279053,
              "appearance_adaptive_ratio": 6.664274601854973
            },
            {
              "region": {
                "frame": 34727,
                "key": "track:1",
                "bbox": [
                  656.8698120117188,
                  184.077392578125,
                  730.3063354492188,
                  329.9198303222656
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 39,
              "consistent_fraction": 0.41025641025641024,
              "median_patch_error": 30.67942237854004,
              "median_forward_backward_error": 3.203615665435791,
              "discontinuity": 18.09299268478002,
              "previous_mean": 0.0,
              "adaptive_ratio": 18.09299268478002,
              "appearance_previous_mean": 7.776006460189819,
              "appearance_adaptive_ratio": 3.9453956906552166
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.7867417335510254,
          "discontinuity": 27.20838065025134,
          "photometric_gain": 0.9912280701754386,
          "photometric_offset": 0.7192982456140413,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 33.50159549713135
        },
        "decision": {
          "frame": 34728,
          "previous_frame": 34727,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 34728,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "e055335401fa9f9f9d40365c3ee53ed0ceb87d6d8cc7a99fcf2f3fd85695f956",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              505.86717933416367,
              351.92571568489075,
              586.1733165383339,
              533.7569205760956
            ],
            [
              622.6961541771889,
              202.9596095830202,
              682.1426023840904,
              335.6611875742674
            ],
            [
              233.0,
              304.9903223961592,
              296.2025192975998,
              411.82414646446705
            ],
            [
              997.2430319786072,
              195.1971719712019,
              1048.9151520729065,
              294.07347063720226
            ],
            [
              769.6153769493103,
              129.1687983572483,
              805.1073937416077,
              179.4625370502472
            ],
            [
              477.5693408250809,
              132.7467710264027,
              511.35220324993134,
              181.09203742071986
            ],
            [
              621.5512376129627,
              127.29432479664683,
              657.4280399978161,
              180.52836951985955
            ],
            [
              318.82095152139664,
              120.7165543101728,
              348.42847031354904,
              180.12930465117097
            ],
            [
              1002.9964628517628,
              122.64946806430817,
              1039.7171239554882,
              208.9288029372692
            ]
          ],
          "detector_scores": [
            0.9198356014334317,
            0.8922769963178534,
            0.8778861668873205,
            0.7691588993975483,
            0.6988533584048022,
            0.6287953696579595,
            0.616370312556582,
            0.5919797605453571,
            0.4004373540083958
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
        "frame": 36362,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 51,
        "raw": {
          "frame": 36362,
          "previous_frame": 36361,
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
                "frame": 36361,
                "key": "track:2",
                "bbox": [
                  735.9568481445312,
                  353.60235595703125,
                  799.0106811523438,
                  527.4100341796875
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 37,
              "consistent_fraction": 0.0,
              "median_patch_error": 19.248937606811523,
              "median_forward_backward_error": 58.61508560180664,
              "discontinuity": 19.248937606811523,
              "previous_mean": 0.0,
              "adaptive_ratio": 19.248937606811523,
              "appearance_previous_mean": 6.375177383422852,
              "appearance_adaptive_ratio": 3.0193571800627628
            },
            {
              "region": {
                "frame": 36361,
                "key": "track:1",
                "bbox": [
                  783.4971923828125,
                  181.28268432617188,
                  842.8899536132812,
                  316.09820556640625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 38,
              "consistent_fraction": 0.15789473684210525,
              "median_patch_error": 48.537452697753906,
              "median_forward_backward_error": 8.734328269958496,
              "discontinuity": 40.87364437705592,
              "previous_mean": 0.0,
              "adaptive_ratio": 40.87364437705592,
              "appearance_previous_mean": 5.64395546913147,
              "appearance_adaptive_ratio": 8.599900010412941
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 2.2112386226654053,
          "discontinuity": 30.06129099193372,
          "photometric_gain": 1.008849557522124,
          "photometric_offset": -0.7256637168141538,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 33.893195152282715
        },
        "decision": {
          "frame": 36362,
          "previous_frame": 36361,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 36362,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "b57ae5d9427c22cd0ca90d4a36278e47d0faf6a1e0cb9195a246b1202f92633c",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              627.9169037938118,
              351.59336629509926,
              690.508026778698,
              526.7163297832012
            ],
            [
              562.7984361052513,
              207.74183559417725,
              619.1709890961647,
              331.3861091732979
            ],
            [
              999.2106256783009,
              195.3913937434554,
              1048.9467496573925,
              292.8697740212083
            ],
            [
              770.0405969321728,
              129.01476395502687,
              804.8314905464649,
              179.5051162801683
            ],
            [
              622.0337509214878,
              126.94845131784678,
              657.8732362687588,
              180.80646447092295
            ],
            [
              1001.710476577282,
              122.7705227509141,
              1040.2148926854134,
              210.36553635448217
            ],
            [
              318.9401344060898,
              120.15746393427253,
              348.2214604616165,
              179.7664292640984
            ],
            [
              233.0,
              311.617854565382,
              299.14650708436966,
              404.0691227018833
            ],
            [
              477.46422934532166,
              132.97437573969364,
              510.98538613319397,
              180.70869605243206
            ],
            [
              960.819441974163,
              121.528240211308,
              1003.2540996670723,
              211.9863284304738
            ]
          ],
          "detector_scores": [
            0.9153980019846294,
            0.9144648748052077,
            0.7076752556428307,
            0.6068533443288875,
            0.5819225920294576,
            0.519744970839707,
            0.473361704551698,
            0.45659444671298366,
            0.45020464440553115,
            0.3505160339135972
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
        "frame": 36729,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 52,
        "raw": {
          "frame": 36729,
          "previous_frame": 36728,
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
                "frame": 36728,
                "key": "track:0",
                "bbox": [
                  756.2418212890625,
                  310.8332824707031,
                  819.7389526367188,
                  466.76458740234375
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 31,
              "consistent_fraction": 0.0,
              "median_patch_error": 33.79407501220703,
              "median_forward_backward_error": 53.374656677246094,
              "discontinuity": 33.79407501220703,
              "previous_mean": 0.0,
              "adaptive_ratio": 33.79407501220703,
              "appearance_previous_mean": 4.893565908074379,
              "appearance_adaptive_ratio": 6.905817893746325
            },
            {
              "region": {
                "frame": 36728,
                "key": "track:1",
                "bbox": [
                  715.4158935546875,
                  178.81201171875,
                  759.85791015625,
                  317.89471435546875
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 31,
              "consistent_fraction": 0.5161290322580645,
              "median_patch_error": 22.867347717285156,
              "median_forward_backward_error": 0.9497649669647217,
              "discontinuity": 11.064845669654108,
              "previous_mean": 0.0,
              "adaptive_ratio": 11.064845669654108,
              "appearance_previous_mean": 6.331136800348759,
              "appearance_adaptive_ratio": 3.611886528186451
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.9762613773345947,
          "discontinuity": 22.429460340930568,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 28.330711364746094
        },
        "decision": {
          "frame": 36729,
          "previous_frame": 36728,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 36729,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "d105162ffdbfa20d79bc70d17d49a7b8bb475acdc0c893b54150191a9dd90faa",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              696.8856714367867,
              347.9890625476837,
              767.7459775805473,
              530.6341962814331
            ],
            [
              593.7988659143448,
              195.40066334605217,
              659.9437345266342,
              338.28817370533943
            ],
            [
              233.0,
              305.63163410127163,
              297.03505766391754,
              404.2399894744158
            ],
            [
              1001.6467251181602,
              194.91687989979982,
              1049.0,
              290.2723516449332
            ],
            [
              770.0831683278084,
              129.19723491370678,
              804.695243537426,
              179.65617689490318
            ],
            [
              621.0963169038296,
              126.85455248877406,
              657.813166052103,
              180.87108363583684
            ],
            [
              1002.4235387146473,
              123.46535804867744,
              1042.201594799757,
              210.10609287023544
            ],
            [
              477.5679455399513,
              133.15509862452745,
              511.1432418227196,
              180.68663320690393
            ],
            [
              319.0688593387604,
              120.16505648568273,
              348.3411023616791,
              179.76361126825213
            ]
          ],
          "detector_scores": [
            0.9365827812528582,
            0.8526335874861449,
            0.8318745703652166,
            0.6976439211948671,
            0.5306104984981974,
            0.5172581037056204,
            0.509808950619356,
            0.4723184922568682,
            0.4254342300758469
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
        "frame": 36951,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 53,
        "raw": {
          "frame": 36951,
          "previous_frame": 36950,
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
                "frame": 36950,
                "key": "track:0",
                "bbox": [
                  436.45098876953125,
                  304.65301513671875,
                  483.594970703125,
                  466.97637939453125
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 29,
              "consistent_fraction": 0.0,
              "median_patch_error": 37.64491271972656,
              "median_forward_backward_error": 40.9168586730957,
              "discontinuity": 37.64491271972656,
              "previous_mean": 0.0,
              "adaptive_ratio": 37.64491271972656,
              "appearance_previous_mean": 4.50465914607048,
              "appearance_adaptive_ratio": 8.356883728387109
            },
            {
              "region": {
                "frame": 36950,
                "key": "track:1",
                "bbox": [
                  566.1500854492188,
                  241.6282196044922,
                  664.4027709960938,
                  340.9146728515625
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 31,
              "consistent_fraction": 0.5806451612903226,
              "median_patch_error": 21.94316864013672,
              "median_forward_backward_error": 0.5966386198997498,
              "discontinuity": 9.201973945863784,
              "previous_mean": 0.0,
              "adaptive_ratio": 9.201973945863784,
              "appearance_previous_mean": 2.954205524176359,
              "appearance_adaptive_ratio": 7.427773206894445
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 1.0,
          "background_patch_error": 1.6957907676696777,
          "discontinuity": 23.423443332795173,
          "photometric_gain": 1.0,
          "photometric_offset": 0.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 29.79404067993164
        },
        "decision": {
          "frame": 36951,
          "previous_frame": 36950,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 36951,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "f75c8cbfe5874620bc1a884d38080e1a0223a2babfd1d5e7e1406bba337e7a0f",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              508.4653643965721,
              353.91838240623474,
              556.6503964066505,
              532.6853673458099
            ],
            [
              624.5570754408836,
              200.643762268126,
              683.1273575425148,
              336.44441171735525
            ],
            [
              233.0,
              305.2934287786484,
              296.30816274881363,
              404.1149987578392
            ],
            [
              999.7925234138966,
              195.71760310977697,
              1049.0,
              291.76860205084085
            ],
            [
              318.78809240460396,
              120.46941378340125,
              348.2912444770336,
              179.87766449525952
            ],
            [
              1003.3854039013386,
              123.53179401904345,
              1040.7540366351604,
              210.83223312348127
            ],
            [
              770.0537214279175,
              129.0382403805852,
              804.8108758926392,
              179.6408497467637
            ],
            [
              620.9953791201115,
              126.84554635733366,
              657.0874141156673,
              180.68399391323328
            ],
            [
              477.3538331091404,
              133.04643853753805,
              511.1094008386135,
              180.91991744190454
            ]
          ],
          "detector_scores": [
            0.8845545312400778,
            0.8430940911159728,
            0.8066561400383876,
            0.6532847269918314,
            0.5445607420307779,
            0.4952028077661259,
            0.4449406393037858,
            0.4330935902965166,
            0.4103920888016031
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
      "activity_interval": 262,
      "scene": 7,
      "participant_observation": 391,
      "format_decision": 1,
      "rally_start": 188,
      "contact": 2304,
      "stroke": 1114,
      "rally_end": 98,
      "identity_ambiguity": 84,
      "shuttle_turn": 38,
      "broadcast_score": 1117,
      "match_phase": 1,
      "highlight": 5
    },
    "live_counts": {
      "calibration": 1,
      "activity_interval": 262,
      "scene": 7,
      "participant_observation": 391,
      "format_decision": 1,
      "rally_start": 98,
      "stroke": 1090,
      "contact": 1090,
      "rally_end": 98,
      "identity_ambiguity": 84,
      "shuttle_turn": 38,
      "broadcast_score": 1117,
      "match_phase": 1,
      "highlight": 5
    },
    "categories": {
      "event_status": {
        "confirmed": 3672,
        "provisional": 611
      },
      "stroke_actor": {
        "unknown": 1090
      },
      "stroke_physical_event_status": {
        "insufficient": 553,
        "probable": 146,
        "ambiguous": 391
      },
      "stroke_contact_status": {
        "estimated": 1090
      },
      "stroke_classification_status": {
        "unknown": 804,
        "estimated": 286
      },
      "stroke_stroke": {
        "unknown": 804,
        "lift": 48,
        "push": 136,
        "net_shot": 44,
        "drop": 39,
        "drive": 8,
        "clear": 10,
        "rush": 1
      },
      "stroke_attribution_reason": {
        "nearest_proximity": 1086,
        "ambiguous_proximity": 4
      },
      "stroke_classification_abstention_reason": {
        "missing_required_evidence": 801,
        "unresolved_initial_contact": 3
      },
      "contact_actor": {
        "unknown": 1090
      },
      "contact_physical_event_status": {
        "insufficient": 553,
        "probable": 146,
        "ambiguous": 391
      },
      "contact_contact_status": {
        "estimated": 1090
      },
      "contact_attribution_reason": {
        "nearest_proximity": 1086,
        "ambiguous_proximity": 4
      },
      "contact_trajectory_reliability": {
        "insufficient": 268,
        "probable": 559,
        "ambiguous": 263
      },
      "contact_trajectory_reasons": {
        "coherent_motion_change_unavailable": 268,
        "supported_launch": 137,
        "supported_turn": 422,
        "association_unresolved": 263
      },
      "contact_impact_reliability": {
        "insufficient": 553,
        "probable": 146,
        "ambiguous": 391
      },
      "contact_impact_reasons": {
        "fresh_player_observation_unavailable": 553,
        "coherent_motion_and_fresh_contact_cue": 146,
        "association_unresolved": 263,
        "coherent_motion_change_unavailable": 73,
        "no_fresh_swing_or_racket_overlap": 55
      },
      "contact_attribution_reliability": {
        "insufficient": 739,
        "probable": 351
      },
      "contact_attribution_reasons": {
        "fresh_player_observation_unavailable": 739,
        "geometric_attribution_not_verified_identity": 351
      },
      "rally_end_reason": {
        "cut": 19,
        "gap": 36,
        "stationary": 42,
        "flush": 1
      },
      "rally_phase": {
        "unknown": 5,
        "match_play": 93
      },
      "rally_official": {
        "False": 56,
        "True": 42
      },
      "rally_match_format_known": {
        "True": 98
      },
      "rally_match_format": {
        "singles": 98
      },
      "rally_winner": {
        "None": 98
      },
      "rally_score_transition_status": {
        "unavailable": 66,
        "candidate": 32
      },
      "rally_admission_reason": {
        "duration_policy": 96,
        "independent_contact_and_observed_motion_witnesses": 2
      }
    },
    "physical_accuracy_validated": false
  },
  "ocr": {
    "readout_count": 1166,
    "label_counts": {
      "SHI Y.Q.": 1166,
      "AXELSEN": 1166
    },
    "context_counts": {
      "{\"acquisition_policy\":\"main_camera\",\"actual_replay_status\":\"unknown\",\"analysis_excluded\":false,\"view\":\"main\"}": 1166
    },
    "previously_source_reviewed_branding_strings": {},
    "readouts": [
      {
        "f": 1320,
        "r": [
          [
            "SHI Y.Q.",
            2
          ],
          [
            "AXELSEN",
            2
          ]
        ],
        "c": 0.93979,
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
            2
          ],
          [
            "AXELSEN",
            2
          ]
        ],
        "c": 0.93445,
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
            2
          ],
          [
            "AXELSEN",
            2
          ]
        ],
        "c": 0.93576,
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
            2
          ],
          [
            "AXELSEN",
            2
          ]
        ],
        "c": 0.9377,
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
            "AXELSEN",
            2
          ]
        ],
        "c": 0.94506,
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
            "AXELSEN",
            2
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
        "f": 1530,
        "r": [
          [
            "SHI Y.Q.",
            3
          ],
          [
            "AXELSEN",
            2
          ]
        ],
        "c": 0.96165,
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
            "AXELSEN",
            2
          ]
        ],
        "c": 0.93611,
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
            "AXELSEN",
            2
          ]
        ],
        "c": 0.9362,
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
            "AXELSEN",
            2
          ]
        ],
        "c": 0.93612,
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
            "AXELSEN",
            2
          ]
        ],
        "c": 0.93656,
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
            "AXELSEN",
            2
          ]
        ],
        "c": 0.94048,
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
            "AXELSEN",
            3
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
        "f": 1740,
        "r": [
          [
            "SHI Y.Q.",
            3
          ],
          [
            "AXELSEN",
            3
          ]
        ],
        "c": 0.9401,
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
            "AXELSEN",
            3
          ]
        ],
        "c": 0.94013,
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
            "AXELSEN",
            3
          ]
        ],
        "c": 0.94348,
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
            "AXELSEN",
            3
          ]
        ],
        "c": 0.9476,
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
            "AXELSEN",
            3
          ]
        ],
        "c": 0.94113,
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
            "AXELSEN",
            3
          ]
        ],
        "c": 0.76609,
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
            "AXELSEN",
            3
          ]
        ],
        "c": 0.77729,
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
            "AXELSEN",
            3
          ]
        ],
        "c": 0.62176,
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
            3
          ],
          [
            "AXELSEN",
            3
          ]
        ],
        "c": 0.83547,
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
            3
          ],
          [
            "AXELSEN",
            3
          ]
        ],
        "c": 0.75664,
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
            3
          ],
          [
            "AXELSEN",
            3
          ]
        ],
        "c": 0.60739,
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
            3
          ],
          [
            "AXELSEN",
            3
          ]
        ],
        "c": 0.61581,
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
            3
          ],
          [
            "AXELSEN",
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
        "f": 2130,
        "r": [
          [
            "SHI Y.Q.",
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.95995,
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
            3
          ],
          [
            "AXELSEN",
            5
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
        "f": 2190,
        "r": [
          [
            "SHI Y.Q.",
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.95309,
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
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.86991,
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
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.86991,
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
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.93048,
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
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.93048,
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
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.94989,
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
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.94861,
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
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.94876,
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
            3
          ],
          [
            "AXELSEN",
            5
          ]
        ],
        "c": 0.94783,
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
            "AXELSEN",
            6
          ]
        ],
        "c": 0.86114,
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
            "AXELSEN",
            6
          ]
        ],
        "c": 0.83611,
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
            "AXELSEN",
            6
          ]
        ],
        "c": 0.9238,
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
            "AXELSEN",
            6
          ]
        ],
        "c": 0.93137,
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
            "AXELSEN",
            6
          ]
        ],
        "c": 0.90774,
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
            "AXELSEN",
            6
          ]
        ],
        "c": 0.90774,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.90252,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.91878,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.90638,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.90902,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.87153,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.87095,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.86914,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.87266,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.90476,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.90649,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.89773,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.95217,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.95911,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.9589,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.95435,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.83528,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.92935,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.91565,
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
            4
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.85779,
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
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.94107,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3244,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95139,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3274,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.94161,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3304,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.93283,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3334,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.93283,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3364,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.93331,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3394,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.93503,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3424,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
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
        "f": 3454,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.94146,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3484,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.94313,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3514,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95596,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3544,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.96395,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3574,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.96491,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3604,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.96191,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3634,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
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
        "f": 3664,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
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
        "f": 3694,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
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
        "f": 3724,
        "r": [
          [
            "SHI Y.Q.",
            4
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95533,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3754,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.94705,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3784,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
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
        "f": 3814,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.94346,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3844,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.951,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3874,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
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
        "f": 3904,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95524,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3934,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95486,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3964,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95585,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3994,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95796,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4024,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95334,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4054,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95774,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4084,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
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
        "f": 4114,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95007,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4144,
        "r": [
          [
            "SHI Y.Q.",
            6
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95311,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4174,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95088,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4204,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.93961,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4234,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.94667,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4264,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.9467,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4294,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.94677,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4324,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.95149,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4354,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.93825,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4384,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.94412,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4414,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.94412,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4444,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            8
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
        "f": 4474,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.95671,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4504,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.95737,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4534,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.95079,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4564,
        "r": [
          [
            "SHI Y.Q.",
            7
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.94457,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4594,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.97678,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4624,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.94792,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4654,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.94829,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4684,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95259,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4714,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
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
        "f": 4744,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95233,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4774,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
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
        "f": 4804,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94076,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4834,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94035,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4864,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
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
        "f": 4894,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.93835,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4924,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94545,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4954,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94301,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4984,
        "r": [
          [
            "SHI Y.Q.",
            8
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94366,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5014,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94484,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5044,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95258,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5074,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95248,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5104,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
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
        "f": 5134,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
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
        "f": 5164,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95194,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5194,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
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
        "f": 5224,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
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
        "f": 5254,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
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
        "f": 5284,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.9488,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5314,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94892,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5344,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94227,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5374,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94365,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5404,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95072,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5434,
        "r": [
          [
            "SHI Y.Q.",
            9
          ],
          [
            "AXELSEN",
            10
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
        "f": 5464,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
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
        "f": 5494,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.96273,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5524,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.96066,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5554,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.96176,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5584,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
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
        "f": 5614,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95153,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5644,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94781,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5674,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5704,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95585,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5734,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95303,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5764,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95263,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5794,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
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
        "f": 5824,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.96095,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5854,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.9604,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5884,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95825,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5914,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            11
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
        "f": 5944,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.96537,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5974,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.96522,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6004,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            11
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
        "f": 6034,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.9633,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6064,
        "r": [
          [
            "SHI Y.Q.",
            10
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.94826,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6094,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.9503,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6124,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.94792,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6154,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.94884,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6184,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.94957,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6244,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
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
        "f": 6274,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95076,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6304,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
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
        "f": 6334,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95982,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6364,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.96164,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6394,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95603,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6424,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
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
        "f": 6454,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95722,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6484,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95665,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6514,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
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
        "f": 6544,
        "r": [
          [
            "SHI Y.Q.",
            11
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95225,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6574,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.9516,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6604,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
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
        "f": 6634,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95341,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6664,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95548,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6694,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
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
        "f": 6724,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
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
        "f": 6754,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
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
        "f": 6784,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95099,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6814,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95116,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6844,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95378,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6874,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
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
        "f": 6904,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95523,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6934,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.9562,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6964,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95092,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6994,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.96062,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7024,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.95365,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7054,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.96903,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7084,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.95248,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7114,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
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
        "f": 7144,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.97117,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7174,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.97068,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7204,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.97361,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7234,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.97366,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7264,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.93393,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7294,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.93337,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7324,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.9558,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7384,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94799,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7414,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94718,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7444,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94436,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7474,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.95635,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7504,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.95621,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7534,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.95562,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7564,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
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
        "f": 7594,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.94238,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7624,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.947,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7654,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.94667,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7684,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.94654,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7714,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.94671,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7744,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.94793,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7774,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.94818,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7804,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.95334,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7834,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.95334,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7864,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.95144,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7894,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.95123,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7924,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.94473,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7954,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.95087,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7984,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.95845,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8014,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.95844,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8044,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.96469,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8074,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.96473,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8104,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.96534,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8134,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9434,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8164,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.93432,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8194,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.93409,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8224,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.93064,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8254,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.93022,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8284,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9431,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8314,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9431,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8344,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94401,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8374,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94484,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8404,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94326,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8434,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94256,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8464,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
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
        "f": 8494,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
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
        "f": 8524,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94574,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8554,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95006,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8584,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95049,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8614,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
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
        "f": 8644,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95738,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8674,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95788,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8704,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95199,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8734,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95204,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8764,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95919,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8794,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95852,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8824,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95186,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8854,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
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
        "f": 8884,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8914,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94804,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8944,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95766,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8974,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9575,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9004,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9545,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9034,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9547,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9064,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
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
        "f": 9094,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
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
        "f": 9124,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9452,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9154,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94563,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9184,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94644,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9214,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9484,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9244,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
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
        "f": 9274,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94912,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9304,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9751,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9334,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.97532,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9364,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9546,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9394,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95492,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9424,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95719,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9454,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95748,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9484,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94999,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9514,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95019,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9544,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94876,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9574,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
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
        "f": 9604,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.97015,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9634,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
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
        "f": 9664,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.96548,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9694,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.96573,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9724,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
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
        "f": 9754,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95603,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9784,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.97752,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9814,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.97793,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9844,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95759,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9874,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95314,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9904,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95299,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9934,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95306,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9964,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95007,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9994,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94835,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10024,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9723,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10054,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.96914,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10084,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9422,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10114,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94196,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10144,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94644,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10174,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9647,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10204,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94825,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10234,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.96262,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10264,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95798,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10294,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9578,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10324,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95537,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10354,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95805,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10384,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
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
        "f": 10414,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95262,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10444,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.9481,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10474,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94823,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10504,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94751,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10534,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94859,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10564,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94547,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10594,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
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
        "f": 10624,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94616,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10654,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95103,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10684,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.95204,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10718,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.95589,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10748,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.96141,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10778,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.96182,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10808,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.96,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10838,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
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
        "f": 10868,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.96007,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10898,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.95924,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10928,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
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
        "f": 10958,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.95524,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10988,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.95663,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11018,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.96737,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11048,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.97155,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11078,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            18
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
        "f": 11108,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.96108,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11138,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.95898,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11168,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.9725,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11198,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.95334,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11228,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.94242,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11258,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            18
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
        "f": 11288,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.98336,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11318,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            18
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
        "f": 11348,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.98317,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11378,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.98093,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11408,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            18
          ]
        ],
        "c": 0.9683,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11438,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            18
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
        "f": 11468,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            18
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
        "f": 11498,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97191,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11528,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
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
        "f": 11558,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96452,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11588,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97142,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11618,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
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
        "f": 11648,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96126,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11678,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9784,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11708,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
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
        "f": 11738,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96746,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11768,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.95619,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11798,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
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
        "f": 11828,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96266,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11858,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96347,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11888,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
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
        "f": 11918,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.95949,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11948,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.95153,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11978,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96655,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12008,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94845,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12038,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94845,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12068,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
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
        "f": 12098,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.95385,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12338,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9697,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12368,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98574,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12398,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98574,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12428,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9831,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12458,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97973,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12488,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98419,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12518,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 12548,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98206,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12578,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98198,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12608,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97901,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12638,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98462,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12668,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97894,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12698,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97956,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12728,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98568,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12758,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98674,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12788,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97876,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12818,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98208,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12848,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9877,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12878,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98777,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12908,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98717,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12938,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98562,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12968,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9872,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12998,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98711,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13028,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98668,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13058,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13088,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94925,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13118,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9874,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13148,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98131,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13178,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98381,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13208,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98083,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13238,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13268,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98212,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13298,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98235,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13328,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98513,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13358,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98476,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13388,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98301,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13418,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98668,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13448,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98072,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13478,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98052,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13508,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98064,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13538,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98077,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13568,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99226,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13598,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 13628,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99235,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13658,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99237,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13688,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98434,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13718,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98556,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13748,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98485,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13778,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98457,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13808,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98426,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13838,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98628,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13868,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97603,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13898,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9754,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13928,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97985,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13958,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97978,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13988,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98015,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14018,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98719,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14048,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9846,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14078,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98652,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14108,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98622,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14138,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9852,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14168,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98172,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14198,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98187,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14228,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99028,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14258,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98296,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14288,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96073,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14318,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96233,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14348,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98889,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14378,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14408,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97864,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14438,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97885,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14468,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98373,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14498,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98441,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14528,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98743,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14558,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98715,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14588,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98209,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14618,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 14648,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9818,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14678,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97254,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14708,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98883,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14738,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98828,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14768,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98603,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14798,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98613,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14828,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98764,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14858,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97698,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14888,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98588,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14918,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9856,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14948,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98349,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14978,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 15008,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98601,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15038,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98196,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15068,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97674,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15098,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97686,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15128,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97677,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15158,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97664,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15188,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97705,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15218,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
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
        "f": 15248,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9834,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15278,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9821,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15308,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98839,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15338,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98803,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15368,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98778,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15398,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98314,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15428,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98693,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15458,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98342,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15488,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 15518,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97812,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15548,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98156,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15578,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 15608,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96653,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15638,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 15668,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97817,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15698,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98041,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15728,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98733,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15758,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 15788,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98535,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15818,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98541,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15848,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98494,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15878,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98392,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15908,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9563,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15938,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99239,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15968,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97729,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15998,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9774,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16028,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98205,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16058,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98192,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16088,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97794,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16118,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97794,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16148,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9802,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16178,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98864,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16208,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97665,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16238,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97316,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16268,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97409,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16298,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97274,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16328,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9812,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16358,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98112,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16388,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 16418,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98226,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16448,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98343,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16478,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98377,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16508,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98371,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16538,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97689,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16568,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98255,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16598,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98389,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16628,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98051,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16658,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98028,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16688,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 16718,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98156,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16748,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97885,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16778,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 16808,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97919,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16838,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98543,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16868,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98215,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16898,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99058,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16928,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98877,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16958,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98886,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16988,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97971,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17018,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98607,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17048,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98452,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17078,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98464,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17108,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97428,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17138,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9786,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17168,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97624,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17198,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98663,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17228,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98037,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17258,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9804,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17288,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98143,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17318,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98152,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17348,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98129,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17378,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98478,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17408,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9751,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17438,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.975,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17468,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97392,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17498,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98269,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17528,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97672,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17558,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97721,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17588,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98106,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17618,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98112,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17648,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98232,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17678,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98374,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17708,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17738,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97975,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17768,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17798,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97683,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17828,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98061,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17858,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98245,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17888,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.985,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17918,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98531,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17948,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98616,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17978,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98503,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18008,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9905,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18038,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99046,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18068,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99073,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18098,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98642,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18128,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98558,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18158,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98247,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18188,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 18218,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98982,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18248,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98819,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18278,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98079,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18308,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9827,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18338,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98269,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18368,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 18398,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96716,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18428,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97488,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18458,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98266,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18488,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98259,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18518,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98259,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18548,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 18578,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9824,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18608,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98443,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18638,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98336,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18668,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98607,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18698,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98686,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18728,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98404,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18758,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98467,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18788,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99183,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18818,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99152,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18848,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98914,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18878,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99079,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18908,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99467,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18938,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99472,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18968,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18998,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99357,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19028,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98068,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19058,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98355,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19088,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98217,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19118,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98202,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19148,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98352,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19178,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98365,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19208,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98742,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19238,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98747,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19268,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98623,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19298,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19328,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9852,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19358,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98506,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19388,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.92399,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19418,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.92341,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19448,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99012,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19478,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98955,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19508,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98759,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19538,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98773,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19568,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19598,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98996,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19628,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98544,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19658,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97588,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19688,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 19718,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97305,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19748,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97472,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19778,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98583,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19808,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9858,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19838,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98526,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19868,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98805,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19898,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97785,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19928,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98061,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19958,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97973,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19988,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20018,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94638,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20048,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97336,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20078,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97201,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20108,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9713,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20138,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9896,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20168,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98018,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20198,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98068,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20228,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97537,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20258,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97613,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20288,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98683,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20318,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98208,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20348,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98302,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20378,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97706,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20408,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98458,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20438,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98484,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20468,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98409,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20498,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98417,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20528,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20558,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98066,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20588,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 20618,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94221,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20648,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9785,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20678,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98115,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20708,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97973,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20738,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20768,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98065,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20798,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98038,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20828,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97873,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20858,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9859,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20888,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98472,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20918,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9836,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20948,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97456,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 20978,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98391,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21008,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98363,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21038,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98347,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21068,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98476,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21098,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98261,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21128,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97425,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21158,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98471,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21188,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98574,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21218,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98645,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21248,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98885,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21278,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98868,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21308,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98546,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21338,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98536,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21368,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98587,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21398,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98123,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21428,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97911,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21458,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97901,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21488,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 21518,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9746,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21548,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97522,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21578,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98055,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21608,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98108,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21638,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97999,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21668,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9758,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21698,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97541,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21728,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97446,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21758,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98775,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21788,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98888,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21818,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98882,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21848,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98154,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21878,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98177,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21908,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97952,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21938,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97362,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21968,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97687,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 21998,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97712,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22028,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98266,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22058,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98225,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22088,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98463,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22118,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97961,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22148,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98319,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22178,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98249,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22208,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98529,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22238,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98529,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22268,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22298,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98873,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22328,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98604,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22358,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98656,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22388,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98338,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22418,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97941,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22448,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98095,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22478,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98043,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22508,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97496,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22538,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97593,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22568,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97492,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22598,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9836,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22628,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98756,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22658,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98719,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22688,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 22718,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98251,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22748,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98049,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22778,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98058,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22808,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9774,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22838,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97858,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22868,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 22898,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98555,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22928,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98516,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22958,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98418,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 22988,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97951,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23018,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97844,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23048,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98334,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23078,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98325,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23108,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23138,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98323,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23168,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98288,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23198,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9808,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23228,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99178,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23258,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99178,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23288,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98897,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23318,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98878,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23348,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98865,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23378,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98574,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23408,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98563,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23438,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98458,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23468,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98327,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23498,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98371,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23540,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97643,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23570,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97664,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23600,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 23630,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.971,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23660,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98392,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23690,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98483,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23720,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98203,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23750,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98183,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23780,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98368,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23810,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98262,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23840,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97075,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23870,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97017,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23900,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98364,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23930,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98394,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23960,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9808,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 23990,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98095,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24020,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98363,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24050,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98311,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24080,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9837,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24110,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98441,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24140,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98745,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24170,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98009,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24200,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9885,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24230,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9868,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24260,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98824,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24290,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98814,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24320,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98717,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24350,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98912,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24380,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 24410,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 24440,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9901,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24470,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9901,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24500,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 24530,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96376,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24560,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97343,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24590,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97348,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24620,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24650,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 24680,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98809,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24710,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 24740,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97965,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24770,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98217,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24800,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98307,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24830,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97443,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24860,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98208,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24890,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98174,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24920,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98579,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24950,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98572,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 24980,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98307,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25010,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98382,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25040,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25070,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25100,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97197,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25130,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98333,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25160,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98478,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25190,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98498,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25220,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98526,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25250,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98503,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25280,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98587,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25310,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98478,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25340,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98817,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25370,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25430,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.95471,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25460,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96068,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25490,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97475,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25520,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98881,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25550,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98959,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25580,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98861,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25610,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98847,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25640,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 25670,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25700,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98042,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25730,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98004,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25760,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98914,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25790,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 25820,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98814,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25850,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9883,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25880,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 25910,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97964,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25940,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98526,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 25970,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98293,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26000,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97997,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26030,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94289,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26060,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98774,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26090,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98638,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26120,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97639,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26150,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98035,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26180,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98038,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26210,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98058,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26240,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97585,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26270,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97726,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26300,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97976,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26330,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97965,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26360,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97732,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26390,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9773,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26420,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97335,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26450,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97442,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26480,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97901,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26510,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97895,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26540,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96203,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26570,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 26600,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97185,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26630,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97206,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26660,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97815,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26690,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97572,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26720,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97735,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26750,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97742,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26780,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97674,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26810,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98379,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26840,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98073,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26870,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9815,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26900,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97954,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26930,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 26960,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96863,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 26990,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 27020,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98814,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27050,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 27080,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97576,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27110,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9751,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27140,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98377,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27170,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97741,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27200,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97699,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27230,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97695,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27260,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 27290,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 27320,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98127,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27350,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.982,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27380,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98008,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27410,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97984,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27440,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98014,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27470,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97513,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27500,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 27530,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97938,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27560,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98992,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27590,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99045,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27620,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98974,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27650,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98934,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27680,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98779,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27710,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9868,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27740,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98493,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27770,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9848,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27800,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98204,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27830,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9772,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27860,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 27890,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9798,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27920,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98127,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27950,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98472,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 27980,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97825,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28010,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97868,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28040,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97485,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28070,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97563,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28100,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97658,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28130,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97507,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28160,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97671,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28190,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98921,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28220,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98003,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28250,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98005,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28280,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97109,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28310,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97142,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28340,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97081,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28370,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97081,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28400,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 28430,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9879,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28460,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9893,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28490,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98937,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28520,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97725,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28550,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97558,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28580,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 28610,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 28640,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 28670,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98436,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28700,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98854,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28730,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97758,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28760,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 28790,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98466,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28820,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98635,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28850,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98662,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28880,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98585,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28910,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98605,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28940,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98487,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 28970,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98509,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29000,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98869,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29030,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9855,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29060,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96541,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29090,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96665,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29120,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97354,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29150,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 29180,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 29210,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98188,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29240,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97622,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29270,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97476,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29300,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97728,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29330,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97611,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29360,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97794,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29390,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99092,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29420,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97957,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29450,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98107,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29480,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98022,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29510,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.99162,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29540,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29570,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97815,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29600,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98281,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29630,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98221,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29660,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98092,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29690,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98538,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29720,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98835,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29750,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98619,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29780,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97622,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29810,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98732,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29840,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97604,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29870,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9815,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29900,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 29930,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9716,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 29960,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
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
        "f": 29990,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30020,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30050,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.94841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30080,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9754,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30110,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97508,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30140,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97819,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30170,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.9795,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30200,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98133,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30230,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98132,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30260,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.96424,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30290,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.982,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30320,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98196,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30350,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97367,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30380,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97104,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30410,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.97882,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30440,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98028,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30470,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.98017,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 30500,
        "r": [
          [
            "SHI Y.Q.",
            21
          ],
          [
            "AXELSEN",
            19
          ]
        ],
        "c": 0.92241,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31024,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.8275,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31054,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.81228,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31084,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.85169,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31114,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.82503,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31144,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.83993,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31174,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.7717,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31204,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.79657,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31234,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.79718,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31264,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.79064,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31294,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.77868,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31324,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.97923,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31354,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.74733,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31384,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.8607,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31414,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.74822,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31444,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.78873,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31474,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.82509,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31504,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            6
          ]
        ],
        "c": 0.77434,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31534,
        "r": [
          [
            "SHI Y.Q.",
            12
          ],
          [
            "AXELSEN",
            7
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
        "f": 31564,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.98692,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31594,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.98452,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31624,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.98832,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31654,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.98608,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31684,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.99166,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31714,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            7
          ]
        ],
        "c": 0.99155,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31744,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.9827,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31774,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.98534,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31804,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.98815,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31834,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.98793,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31864,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.985,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31894,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
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
        "f": 31924,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.98987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31954,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.98309,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 31984,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.9845,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32014,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            8
          ]
        ],
        "c": 0.98427,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32044,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98666,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32074,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98843,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32104,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98778,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32134,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98778,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32164,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98569,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32194,
        "r": [
          [
            "SHI Y.Q.",
            13
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98834,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32224,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98133,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32254,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98123,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32284,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98054,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32314,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.90178,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32344,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98522,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32374,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98793,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32404,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98874,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32434,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98844,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32464,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
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
        "f": 32494,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98767,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32524,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
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
        "f": 32554,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32584,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.99043,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32614,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98874,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32644,
        "r": [
          [
            "SHI Y.Q.",
            14
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98699,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32674,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98775,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32704,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.95367,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32734,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.95363,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32764,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.94877,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32794,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.96722,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32824,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.97165,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32854,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            9
          ]
        ],
        "c": 0.98951,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32884,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.98349,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32914,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.95112,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32944,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.94569,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 32974,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.99109,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33004,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.99373,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33034,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.99344,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33064,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
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
        "f": 33094,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
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
        "f": 33124,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.99334,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33154,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.99358,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33184,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.98996,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33214,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.98997,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33244,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.98859,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33274,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
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
        "f": 33304,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.98974,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33334,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.99074,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33364,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            10
          ]
        ],
        "c": 0.98875,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33394,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
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
        "f": 33424,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
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
        "f": 33454,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.99366,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33484,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.99281,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33514,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.9746,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33544,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.97556,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33574,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.97536,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33604,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.95433,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33634,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.94991,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33664,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.91337,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33694,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.91369,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33724,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            11
          ]
        ],
        "c": 0.91295,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33754,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.94544,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33784,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.95906,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33814,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.96072,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33844,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.99174,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33874,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.99192,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33904,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.99374,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33934,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.9956,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33964,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.99429,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 33994,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
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
        "f": 34024,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.99374,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34054,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.99376,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34084,
        "r": [
          [
            "SHI Y.Q.",
            15
          ],
          [
            "AXELSEN",
            12
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
        "f": 34114,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.92338,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34144,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.98923,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34174,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            12
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
        "f": 34204,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.9946,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34234,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.99464,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34264,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
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
        "f": 34294,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            12
          ]
        ],
        "c": 0.99491,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34324,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            12
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
        "f": 34354,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.98688,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34384,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.99033,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34414,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.98759,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34444,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.9956,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34474,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.99595,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34504,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.99551,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34534,
        "r": [
          [
            "SHI Y.Q.",
            16
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.99496,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34564,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.98796,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34594,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.94471,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34624,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.98929,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34654,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.93817,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34684,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            13
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
        "f": 34714,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            13
          ]
        ],
        "c": 0.94492,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34744,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98797,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34774,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98671,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34804,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98616,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34834,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98803,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34864,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
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
        "f": 34894,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94774,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34924,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.95798,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34954,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94722,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 34984,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.9503,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35014,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99153,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35044,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
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
        "f": 35074,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94878,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35104,
        "r": [
          [
            "SHI Y.Q.",
            17
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94882,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35134,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98798,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35164,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
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
        "f": 35194,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99192,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35224,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98966,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35254,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98947,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35284,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.9916,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35314,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99202,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35344,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.9935,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35374,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99059,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35404,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99215,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35434,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99162,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35464,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99014,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35494,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99046,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35524,
        "r": [
          [
            "SHI Y.Q.",
            18
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98808,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35554,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.9866,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35584,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94877,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35614,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94897,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35644,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
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
        "f": 35674,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94486,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35704,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99198,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35734,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
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
        "f": 35764,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
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
        "f": 35794,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99143,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35824,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98951,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35854,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.94332,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35884,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
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
        "f": 35914,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.9547,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35944,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.95566,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 35974,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.95611,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36004,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99219,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36034,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
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
        "f": 36064,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99508,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36094,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.96145,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36124,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.9909,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36154,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.9917,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36184,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98972,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36214,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98982,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36244,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99067,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36274,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99246,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36304,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
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
        "f": 36334,
        "r": [
          [
            "SHI Y.Q.",
            19
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.9908,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36364,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98707,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36394,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98772,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36424,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99427,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36454,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99142,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36484,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.99046,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36514,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98666,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36544,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98624,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36574,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98639,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36604,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.96433,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36634,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98635,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36664,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98563,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36694,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98591,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36724,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            15
          ]
        ],
        "c": 0.98553,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36754,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.99311,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36784,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.9901,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36814,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            16
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
        "f": 36844,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            16
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
        "f": 36874,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            16
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
        "f": 36904,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            16
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
        "f": 36934,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            16
          ]
        ],
        "c": 0.99197,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36964,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.98079,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 36994,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.98538,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 37024,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.96719,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 37054,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.96789,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 37084,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.94876,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 37114,
        "r": [
          [
            "SHI Y.Q.",
            20
          ],
          [
            "AXELSEN",
            17
          ]
        ],
        "c": 0.99335,
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
      "camera_rows": 37133,
      "player_rows": 72838,
      "nonfinite_projected_court_rows": 0,
      "player_projected_court_rows": 71891,
      "projected_court_on_propagated_box": 41577,
      "racket_rows": 27085,
      "shuttle_rows": 37133
    },
    "categories": {
      "player_id": {
        "None": 72838
      },
      "detector_matched": {
        "True": 30781,
        "False": 42057
      }
    },
    "invalid_geometry_frame_count": 394,
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

Test10 retry: the original failed attempt is retained at /home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10. Only the original frame-count deadline was extended to 1800 seconds in a separate preparation process. Original command arguments, inference components, profile, checkpoints and evaluator are unchanged. See frame_count_retry_receipt.json and retry_configuration.json.
