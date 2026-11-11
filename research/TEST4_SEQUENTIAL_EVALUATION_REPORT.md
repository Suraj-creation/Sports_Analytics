# Test 4 evaluation

Status: completed fresh end-to-end inference; unchanged pipeline and predictions. Comparison measures agreement with the supplied legacy rally CSV. Independent physical component accuracy is unavailable without reviewed component labels.

| Input / provenance | Value |
|---|---|
| Drive file | Test4_Full_Rev.mp4 (1W8gjgQz8QX2MkvqmtsQFb3-3y9wfRuy7) |
| Video SHA256 | `adff61dad4741ea6e8220c5d3292ddb0578b3c91b9e724f49b6f6608203558ed` |
| Annotation | `/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test4_Full/Test4_Full_rally.csv` |
| Annotation SHA256 | `313d62a10401d502cc206f8a398b07297d9886a4d193df3629be128002dde39c` |
| Reference rows | 41 |
| Canonical frames / FPS | 20034 / 30.0 |
| Frozen bindings | [Source, profile, manifest, model lock](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/frozen_pipeline.json) |

| Detection / overlap | Value |
|---|---|
| ground_truth_count | 41 |
| predicted_count | 46 |
| matched_count | 38 |
| true_positives | 38 |
| false_positives | 8 |
| false_negatives | 3 |
| precision | 0.826087 |
| recall | 0.926829 |
| f1 | 0.873563 |
| mean_iou | 0.821815 |
| median_iou | 0.861752 |
| minimum_iou | 0.519403 |
| percent_strictly_exceeding | {'0.5': 100.0, '0.75': 76.3157894736842, '0.9': 42.10526315789474, '0.95': 18.42105263157895} |

Boundary and duration statistics condition on matched intervals; all missed rallies and false detections remain in detection metrics. Signed errors are prediction minus reference. Matching: IoU ≥ 0.5, maximum cardinality then total IoU; zero-origin half-open frame intervals.

| Error | MAE | Median absolute | RMSE | P90 absolute | Maximum absolute | Signed bias |
|---|---|---|---|---|---|---|
| start_frame | 31.289474 | 19.000000 | 43.298535 | 78.700000 | 104.000000 | 23.868421 |
| end_frame | 26.842105 | 11.000000 | 54.005360 | 59.200000 | 248.000000 | -12.526316 |
| start_time_sec | 1.042982 | 0.633333 | 1.443285 | 2.623333 | 3.466667 | 0.795614 |
| end_time_sec | 0.894737 | 0.366667 | 1.800179 | 1.973333 | 8.266667 | -0.417544 |
| duration_sec | 1.532456 | 0.750000 | 2.431127 | 3.366667 | 9.633333 | -1.213158 |

| Boundary tolerance | Within / matched | Within / all reference |
|---|---|---|
| start ±1 frames | 0 / 38 (0.000000) | 0 / 41 (0.000000) |
| start ±3 frames | 1 / 38 (0.026316) | 1 / 41 (0.024390) |
| start ±5 frames | 5 / 38 (0.131579) | 5 / 41 (0.121951) |
| start ±10 frames | 15 / 38 (0.394737) | 15 / 41 (0.365854) |
| start ±15 frames | 18 / 38 (0.473684) | 18 / 41 (0.439024) |
| start ±30 frames | 24 / 38 (0.631579) | 24 / 41 (0.585366) |
| end ±1 frames | 4 / 38 (0.105263) | 4 / 41 (0.097561) |
| end ±3 frames | 7 / 38 (0.184211) | 7 / 41 (0.170732) |
| end ±5 frames | 8 / 38 (0.210526) | 8 / 41 (0.195122) |
| end ±10 frames | 19 / 38 (0.500000) | 19 / 41 (0.463415) |
| end ±15 frames | 23 / 38 (0.605263) | 23 / 41 (0.560976) |
| end ±30 frames | 31 / 38 (0.815789) | 31 / 41 (0.756098) |

Missed rally IDs: [1, 14, 25].

| False detection ID | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| 1 | 363 | 435 | 12.100000 | 14.500000 |
| 5 | 2380 | 2449 | 79.333333 | 81.633333 |
| 7 | 2971 | 3143 | 99.033333 | 104.766667 |
| 10 | 4271 | 4336 | 142.366667 | 144.533333 |
| 17 | 6787 | 6978 | 226.233333 | 232.600000 |
| 28 | 12988 | 13085 | 432.933333 | 436.166667 |
| 31 | 13959 | 14072 | 465.300000 | 469.066667 |
| 45 | 19575 | 19702 | 652.500000 | 656.733333 |

| Runtime / resources | Value |
|---|---|
| parent_completed_elapsed_s | 2012.031731 |
| worker_elapsed_s | 2004.809194 |
| worker_source_fps | 9.992971 |
| media_ready_time_s | 2.099887 |
| model_staging_time_s | 1.662672 |
| component_initialization_including_models_s | 9.244474 |
| worker_final_cpu_s | 23291.818427 |
| worker_maxrss_bytes | 3013013504 |
| sampled_worker_tree_peak_rss_bytes | 2992701440 |
| sampled_worker_gpu_peak_mib | 2126 |
| sampled_cpu_seconds_max_observed | 23291.270000 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| sample_count | 971 |
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
      "frames": 20034,
      "raw_shuttle_present": 12921,
      "detector_executed_frames": 7642,
      "person_rows": 36906,
      "scene_telemetry_present": 3602,
      "scene_raw_hypotheses": 2,
      "actual_content_epoch_increments": 2,
      "content_epoch_decreases": 0,
      "detailed_diagnostic_frames": 3600,
      "person_current_detector_matches": 15142,
      "person_propagated_or_unmatched": 21764,
      "pose_present_rows": 28576,
      "pose_current_source_rows": 28576,
      "pose_present_without_current_source": 0,
      "pose_current_on_propagated_box": 13434,
      "racket_present_rows": 12411,
      "racket_current_source_rows": 12411,
      "racket_present_without_current_source": 0,
      "racket_current_on_propagated_box": 0,
      "scene_decision_records": 2,
      "scene_positive_correspondence_vetoes": 0,
      "scene_current_detector_probes": 2
    },
    "categories": {
      "view": {
        "main": 18621,
        "none": 1213,
        "alt": 200
      },
      "calibration_state": {
        "REACQUIRING": 86,
        "VALID": 18535,
        "LOST": 1413
      },
      "player_population": {
        "0": 1491,
        "2": 18363,
        "1": 180
      },
      "association_status": {
        "missing": 5700,
        "observed": 12915,
        "invalid": 1413,
        "ambiguous": 6
      },
      "association_reason": {
        "no_accepted_raw_observation": 5700,
        "fresh_selection_retained": 12915,
        "image_view_invalid": 1413,
        "coobserved_competing_static_hypothesis": 6
      },
      "scene_raw_status": {
        "unknown": 328,
        "measured": 3272,
        "hypothesis": 2
      },
      "person_detector_match": {
        "True": 15142,
        "False": 21764
      },
      "person_identity_method": {
        "bytetrack_v1": 36906
      },
      "scene_decision": {
        "barrier": 2
      },
      "scene_decision_reason": {
        "raw_change_and_current_layout_discontinuity": 2
      }
    },
    "scene_records": [
      {
        "frame": 5693,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 1,
        "raw": {
          "frame": 5693,
          "previous_frame": 5692,
          "status": "hypothesis",
          "hypothesis": true,
          "reasons": [
            "appearance_discontinuity",
            "edit_or_multi_region_occlusion_not_independently_resolved"
          ],
          "regions": [
            {
              "region": {
                "frame": 5692,
                "key": "track:3",
                "bbox": [
                  944.853271484375,
                  340.0277404785156,
                  1003.4039916992188,
                  504.4166564941406
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 36,
              "consistent_fraction": 0.6944444444444444,
              "median_patch_error": 19.170635223388672,
              "median_forward_backward_error": 0.494015097618103,
              "discontinuity": 5.857694096035428,
              "previous_mean": 0.13093801446863096,
              "adaptive_ratio": 5.857694096035428,
              "appearance_previous_mean": 4.885310277342796,
              "appearance_adaptive_ratio": 3.9241387209935636
            },
            {
              "region": {
                "frame": 5692,
                "key": "track:2",
                "bbox": [
                  828.97705078125,
                  238.6452178955078,
                  903.5490112304688,
                  370.8943786621094
                ],
                "detector_matched": true,
                "detector_observed": true
              },
              "features": 35,
              "consistent_fraction": 0.5142857142857142,
              "median_patch_error": 17.635204315185547,
              "median_forward_backward_error": 0.9505965113639832,
              "discontinuity": 8.565670667375837,
              "previous_mean": 0.0,
              "adaptive_ratio": 8.565670667375837,
              "appearance_previous_mean": 3.489583358168602,
              "appearance_adaptive_ratio": 5.053670454354995
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.975,
          "background_patch_error": 1.2847931385040283,
          "discontinuity": 7.211682381705632,
          "photometric_gain": 1.0,
          "photometric_offset": 1.0,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": false,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 18.40291976928711
        },
        "decision": {
          "frame": 5693,
          "previous_frame": 5692,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 5693,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "f7bd651db7123147085322afbed50559adb25566c2cbae8e240974dbd0553b94",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              715.2684331275523,
              222.83459278941154,
              768.2827292345464,
              362.91042360663414
            ],
            [
              589.5470359437168,
              392.9683851748705,
              652.2043871171772,
              566.7662195414305
            ],
            [
              793.1969409566373,
              154.81821778416634,
              830.300884546712,
              206.21664363145828
            ],
            [
              622.5339394621551,
              153.0548360683024,
              657.3139637894928,
              207.04908979311585
            ],
            [
              446.59826866723597,
              153.1976460032165,
              484.87939288280904,
              206.33960330113769
            ]
          ],
          "detector_scores": [
            0.9259684350389746,
            0.924208081236398,
            0.7945230168530376,
            0.7885228333852904,
            0.7719391273178557
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
        "frame": 13498,
        "raw_hypothesis": true,
        "actual_barrier": true,
        "epoch": 2,
        "raw": {
          "frame": 13498,
          "previous_frame": 13497,
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
                "frame": 13497,
                "key": "track:1",
                "bbox": [
                  703.1509399414062,
                  238.37437438964844,
                  775.4228515625,
                  386.8092041015625
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 23,
              "consistent_fraction": 0.0,
              "median_patch_error": 20.997024536132812,
              "median_forward_backward_error": 15.556530952453613,
              "discontinuity": 20.997024536132812,
              "previous_mean": 0.0,
              "adaptive_ratio": 20.997024536132812,
              "appearance_previous_mean": 6.339728593826294,
              "appearance_adaptive_ratio": 3.3119753038923423
            },
            {
              "region": {
                "frame": 13497,
                "key": "track:0",
                "bbox": [
                  765.236083984375,
                  456.76824951171875,
                  863.31103515625,
                  565.3331909179688
                ],
                "detector_matched": false,
                "detector_observed": false
              },
              "features": 39,
              "consistent_fraction": 0.02564102564102564,
              "median_patch_error": 32.14632797241211,
              "median_forward_backward_error": 55.182193756103516,
              "discontinuity": 31.32206315260667,
              "previous_mean": 0.12094997748350496,
              "adaptive_ratio": 31.32206315260667,
              "appearance_previous_mean": 8.60751461982727,
              "appearance_adaptive_ratio": 3.73468177426775
            }
          ],
          "background_features": 80,
          "background_consistent_fraction": 0.9875,
          "background_patch_error": 1.5303287506103516,
          "discontinuity": 26.159543844369743,
          "photometric_gain": 1.0098039215686274,
          "photometric_offset": -0.7156862745098067,
          "authoritative": false,
          "source_basis": "observed_pixels_and_previous_frame_regions",
          "support_semantics": "raw_patch_intensity_and_adaptive_ratio_uncalibrated",
          "version": "foreground-scene-hypothesis:v2",
          "correspondence_hypothesis": true,
          "appearance_hypothesis": true,
          "appearance_discontinuity": 26.57167625427246
        },
        "decision": {
          "frame": 13498,
          "previous_frame": 13497,
          "decision": "barrier",
          "reason": "raw_change_and_current_layout_discontinuity",
          "raw_hypothesis": true,
          "detector_frame": 13498,
          "detector_model": "rfdetr_small@1.4.2",
          "detector_image_sha256": "ef4297dd0bc8c3e4b5c6ef6c2862df97b8867c0d9670db8f555a354a1a22801b",
          "detector_image_shape": [
            720,
            1280,
            3
          ],
          "detector_boxes": [
            [
              696.684336476028,
              380.2605783492327,
              754.4672276452184,
              556.4279000014067
            ],
            [
              606.4897366799414,
              253.43239064514637,
              654.885089751333,
              377.60920087993145
            ],
            [
              793.8800253346562,
              154.29929047077894,
              830.7781897112727,
              205.90713861584663
            ],
            [
              445.7464911788702,
              153.0845472700894,
              483.69439639151096,
              206.40969698503613
            ],
            [
              623.0529117770493,
              153.12688299641013,
              656.6772526316345,
              206.87678755447268
            ],
            [
              1014.1366112791002,
              156.8053996115923,
              1044.803279582411,
              248.05098395049572
            ]
          ],
          "detector_scores": [
            0.9454486997621274,
            0.8796629298605831,
            0.7812625889999157,
            0.7608072292283992,
            0.7509440224386729,
            0.6130880493137048
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
      "activity_interval": 150,
      "scene": 62,
      "participant_observation": 162,
      "format_decision": 1,
      "rally_start": 112,
      "contact": 1133,
      "stroke": 539,
      "rally_end": 46,
      "identity_ambiguity": 77,
      "shuttle_turn": 37,
      "broadcast_score": 504,
      "match_phase": 1,
      "highlight": 1
    },
    "live_counts": {
      "calibration": 1,
      "activity_interval": 150,
      "scene": 62,
      "participant_observation": 162,
      "format_decision": 1,
      "rally_start": 46,
      "stroke": 525,
      "contact": 525,
      "rally_end": 46,
      "identity_ambiguity": 77,
      "shuttle_turn": 37,
      "broadcast_score": 504,
      "match_phase": 1,
      "highlight": 1
    },
    "categories": {
      "event_status": {
        "confirmed": 1816,
        "provisional": 322
      },
      "stroke_actor": {
        "unknown": 525
      },
      "stroke_physical_event_status": {
        "ambiguous": 177,
        "probable": 85,
        "insufficient": 263
      },
      "stroke_contact_status": {
        "estimated": 525
      },
      "stroke_classification_status": {
        "unknown": 372,
        "estimated": 153
      },
      "stroke_stroke": {
        "unknown": 372,
        "push": 68,
        "lift": 25,
        "drive": 4,
        "drop": 23,
        "net_shot": 24,
        "clear": 7,
        "smash": 2
      },
      "stroke_attribution_reason": {
        "nearest_proximity": 523,
        "ambiguous_proximity": 2
      },
      "stroke_classification_abstention_reason": {
        "missing_required_evidence": 370,
        "unresolved_initial_contact": 2
      },
      "contact_actor": {
        "unknown": 525
      },
      "contact_physical_event_status": {
        "ambiguous": 177,
        "probable": 85,
        "insufficient": 263
      },
      "contact_contact_status": {
        "estimated": 525
      },
      "contact_attribution_reason": {
        "nearest_proximity": 523,
        "ambiguous_proximity": 2
      },
      "contact_trajectory_reliability": {
        "ambiguous": 114,
        "insufficient": 129,
        "probable": 282
      },
      "contact_trajectory_reasons": {
        "association_unresolved": 114,
        "coherent_motion_change_unavailable": 129,
        "supported_launch": 84,
        "supported_turn": 198
      },
      "contact_impact_reliability": {
        "ambiguous": 177,
        "probable": 85,
        "insufficient": 263
      },
      "contact_impact_reasons": {
        "association_unresolved": 114,
        "coherent_motion_change_unavailable": 42,
        "coherent_motion_and_fresh_contact_cue": 85,
        "fresh_player_observation_unavailable": 263,
        "no_fresh_swing_or_racket_overlap": 21
      },
      "contact_attribution_reliability": {
        "insufficient": 347,
        "probable": 178
      },
      "contact_attribution_reasons": {
        "fresh_player_observation_unavailable": 347,
        "geometric_attribution_not_verified_identity": 178
      },
      "rally_end_reason": {
        "gap": 10,
        "stationary": 26,
        "cut": 10
      },
      "rally_phase": {
        "unknown": 4,
        "match_play": 42
      },
      "rally_official": {
        "False": 16,
        "True": 30
      },
      "rally_match_format_known": {
        "True": 46
      },
      "rally_match_format": {
        "singles": 46
      },
      "rally_winner": {
        "None": 46
      },
      "rally_score_transition_status": {
        "unavailable": 27,
        "candidate": 19
      },
      "rally_admission_reason": {
        "duration_policy": 46
      }
    },
    "physical_accuracy_validated": false
  },
  "ocr": {
    "readout_count": 546,
    "label_counts": {
      "MARIN": 546,
      "AN S.Y.": 545,
      "ANS.Y.": 1
    },
    "context_counts": {
      "{\"acquisition_policy\":\"main_camera\",\"actual_replay_status\":\"unknown\",\"analysis_excluded\":false,\"view\":\"main\"}": 546
    },
    "previously_source_reviewed_branding_strings": {},
    "readouts": [
      {
        "f": 1374,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
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
        "f": 1404,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
          ]
        ],
        "c": 0.92133,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1434,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
          ]
        ],
        "c": 0.92133,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1464,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
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
        "f": 1494,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
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
        "f": 1524,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
          ]
        ],
        "c": 0.89802,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1554,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
          ]
        ],
        "c": 0.89802,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1584,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
          ]
        ],
        "c": 0.89706,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1614,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
          ]
        ],
        "c": 0.90051,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1644,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
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
        "f": 1674,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            1
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
        "f": 1737,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.97612,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1767,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.95984,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1797,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.91732,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1827,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 1857,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.91586,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1887,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 1917,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 1947,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.96945,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 1977,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.96945,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2007,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2037,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2067,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2097,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2127,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2157,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2187,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2217,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2247,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2277,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2307,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.97128,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2337,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.97128,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2367,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.97401,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2397,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.97388,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2427,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.97312,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2457,
        "r": [
          [
            "MARIN",
            2
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2525,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.96276,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2555,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
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
        "f": 2585,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.95841,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2615,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.95811,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2645,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2675,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2705,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2735,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2765,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.90494,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2795,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.90494,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2825,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.90248,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2855,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2885,
        "r": [
          [
            "MARIN",
            3
          ],
          [
            "AN S.Y.",
            2
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
        "f": 2967,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.91219,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 2997,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.91678,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3027,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.91753,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3057,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            2
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
        "f": 3087,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.96972,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3117,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.96996,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3147,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.96302,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3177,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            2
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
        "f": 3296,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.97023,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3326,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            2
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
        "f": 3356,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.91443,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3386,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.90017,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3416,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.90017,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3446,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.90695,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3476,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.90695,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3506,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            2
          ]
        ],
        "c": 0.91132,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3550,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
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
        "f": 3580,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
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
        "f": 3610,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
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
        "f": 3640,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
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
        "f": 3670,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.96449,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3700,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.90187,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3730,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.91276,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3760,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.91276,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3790,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.91094,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3820,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.91094,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3850,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.89552,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3880,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.89883,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 3910,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
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
        "f": 3940,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
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
        "f": 3970,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
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
        "f": 4000,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.96153,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4030,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.95689,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4060,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.95575,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4090,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.96403,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4120,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.96403,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4169,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.9004,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4199,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            6
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
        "f": 4229,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.89501,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4259,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.89501,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4289,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.90009,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4319,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.89986,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4349,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.95448,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4401,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.91202,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4431,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
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
        "f": 4461,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
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
        "f": 4491,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
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
        "f": 4521,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
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
        "f": 4551,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
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
        "f": 4581,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
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
        "f": 4611,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
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
        "f": 4641,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.96125,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4671,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.96125,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4725,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.92077,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4755,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.92443,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4785,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.92484,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4815,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.92591,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4845,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.92591,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4875,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.8935,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4905,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.8935,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4935,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.89278,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4965,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.89278,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 4995,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
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
        "f": 5025,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
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
        "f": 5055,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.89982,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5085,
        "r": [
          [
            "MARIN",
            8
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.89982,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5157,
        "r": [
          [
            "MARIN",
            9
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.88176,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5187,
        "r": [
          [
            "MARIN",
            9
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.89274,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5217,
        "r": [
          [
            "MARIN",
            9
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.89274,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5247,
        "r": [
          [
            "MARIN",
            9
          ],
          [
            "AN S.Y.",
            8
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
        "f": 5372,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.89859,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5402,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
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
        "f": 5432,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
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
        "f": 5462,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
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
        "f": 5492,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.96371,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5522,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
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
        "f": 5552,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.88842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5582,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.96774,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5612,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.96774,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5642,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.90435,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5672,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            8
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
        "f": 5702,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.91223,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5732,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.91223,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5762,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.9172,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5792,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.9172,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5822,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.91382,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5852,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.9099,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5882,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
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
        "f": 5912,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
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
        "f": 5942,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.96547,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 5972,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.96547,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6111,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.89063,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6141,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.96115,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6171,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.89169,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6201,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.89207,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6231,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.89483,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6261,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.90812,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6291,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.91152,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6321,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.89843,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6351,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.89843,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6381,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.91536,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6411,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.91129,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6441,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.92682,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6471,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.90718,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6501,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.96778,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6531,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.96778,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6561,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
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
        "f": 6591,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
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
        "f": 6621,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.96437,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6651,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
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
        "f": 6681,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.89786,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 6711,
        "r": [
          [
            "MARIN",
            12
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.89786,
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
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.89295,
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
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.87608,
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
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.8883,
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
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.8904,
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
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.89416,
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
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.89416,
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
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.90234,
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
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.90234,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7029,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.89839,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7059,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.89271,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7089,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.90956,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7119,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.90956,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7149,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.91613,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7179,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.91548,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7209,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.91709,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7239,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.90791,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7269,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.88823,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7299,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.88823,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7329,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.88823,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7359,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.88823,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7389,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95685,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7419,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
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
        "f": 7449,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95418,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7479,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95418,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7509,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95418,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7539,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.9567,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7569,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
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
        "f": 7599,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95397,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7629,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.901,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7659,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.901,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7711,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.95369,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7741,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            13
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
        "f": 7771,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            13
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
        "f": 7801,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.89008,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7831,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.89008,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7861,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.889,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7891,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.889,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7921,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.889,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 7951,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.89199,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8025,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 8055,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 8085,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.96088,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8115,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
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
        "f": 8145,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
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
        "f": 8175,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.96463,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8205,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.96463,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8235,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 8265,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 8309,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90035,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8339,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90874,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8369,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.91373,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8399,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.91373,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8429,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90922,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8459,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.91304,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8489,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.91279,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8519,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.91279,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8549,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.91279,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8579,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
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
        "f": 8609,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90087,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8639,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90087,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8669,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.91783,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8699,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.91783,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8729,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.95967,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8759,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.95967,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8789,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.92206,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8819,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.92206,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8849,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90654,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8879,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90654,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8909,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.96691,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8939,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90695,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8969,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90102,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 8999,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90138,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9029,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90099,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9059,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90099,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9089,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90782,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9119,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.90782,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9149,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
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
        "f": 9179,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
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
        "f": 9209,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.9651,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9239,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.95998,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9269,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.88987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9299,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            14
          ]
        ],
        "c": 0.88987,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9329,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.91482,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9359,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.9146,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9389,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.91592,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9419,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.91627,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9449,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.91731,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9479,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.91731,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9509,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.91158,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9539,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.91158,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9569,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.88739,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9599,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.88739,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9629,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.88693,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9659,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.90171,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9689,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.88595,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9719,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.88971,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9749,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.96815,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9779,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.96815,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9809,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
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
        "f": 9839,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
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
        "f": 9869,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.91434,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9899,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.9139,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9933,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.90877,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 9963,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            17
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
        "f": 9993,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.96243,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10023,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            17
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
        "f": 10053,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            17
          ]
        ],
        "c": 0.95806,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10083,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
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
        "f": 10113,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
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
        "f": 10143,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.96605,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10173,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.96705,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10203,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
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
        "f": 10233,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.94941,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10263,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
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
        "f": 10293,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
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
        "f": 10323,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.96419,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10353,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.96419,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10383,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.95753,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10413,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.95753,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10443,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
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
        "f": 10473,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
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
        "f": 10503,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.96305,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10533,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.91206,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10563,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.88976,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10593,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.88976,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10623,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
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
        "f": 10653,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
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
        "f": 10683,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.90749,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10713,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.90749,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10743,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.90669,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10773,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.90936,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10803,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.91428,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10833,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.903,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10863,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.90813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10893,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.90813,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10923,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.90443,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10953,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.90443,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 10983,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.91288,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11013,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.91288,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11043,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.91144,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11073,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.91144,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11103,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.91334,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11133,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.90805,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11163,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
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
        "f": 11193,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
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
        "f": 11223,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.96816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11253,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.96816,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11283,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            18
          ]
        ],
        "c": 0.91657,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11329,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.89454,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11359,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.96553,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11389,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
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
        "f": 11419,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.89948,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11449,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.89948,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11479,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.89948,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11509,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.89948,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11539,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.90001,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11569,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.89637,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11599,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.89842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11629,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.89842,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11659,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.97116,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11689,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.97116,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11719,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.90262,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11749,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.90262,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11779,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.9591,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11809,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.9591,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11839,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.9591,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11869,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.92979,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11899,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.89983,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11929,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.8988,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11959,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.904,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 11989,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.904,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12019,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.96507,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12049,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.96507,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12079,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.90983,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12109,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.90983,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 12139,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            19
          ]
        ],
        "c": 0.90983,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13607,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "ANS.Y.",
            4
          ]
        ],
        "c": 0.91644,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13637,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            4
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
        "f": 13667,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            4
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
        "f": 13697,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.94757,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13727,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            4
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
        "f": 13757,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.98165,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13787,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.98151,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13817,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.96878,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13847,
        "r": [
          [
            "MARIN",
            4
          ],
          [
            "AN S.Y.",
            4
          ]
        ],
        "c": 0.96878,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13877,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.95401,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13907,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.95235,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13937,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.9564,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13967,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.9564,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 13997,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.95495,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14027,
        "r": [
          [
            "MARIN",
            5
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.94715,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14057,
        "r": [
          [
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.98195,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.9505,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.95101,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.94305,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.94305,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.94305,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.98013,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.94714,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.94714,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.95003,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.95003,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.98994,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.98994,
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
            "MARIN",
            6
          ],
          [
            "AN S.Y.",
            5
          ]
        ],
        "c": 0.93604,
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
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.98665,
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
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.98459,
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
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.98144,
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
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.97824,
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
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.97824,
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
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
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
        "f": 14678,
        "r": [
          [
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
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
        "f": 14708,
        "r": [
          [
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.98465,
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
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.98465,
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
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
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
        "f": 14798,
        "r": [
          [
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
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
        "f": 14828,
        "r": [
          [
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
          ]
        ],
        "c": 0.98497,
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
            "MARIN",
            7
          ],
          [
            "AN S.Y.",
            6
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
        "f": 14906,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.96971,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14936,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            7
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
        "f": 14966,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97883,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 14996,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97883,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15026,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15056,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15086,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97799,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15116,
        "r": [
          [
            "MARIN",
            10
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.952,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15146,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15176,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15206,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.98678,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15236,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.98678,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15266,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.98614,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15296,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.98614,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15326,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15356,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15386,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15416,
        "r": [
          [
            "MARIN",
            11
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.98346,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15446,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97478,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15476,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97351,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15506,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15536,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15566,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97827,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15596,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97827,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15626,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.93751,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15656,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.93751,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15686,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.93523,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15716,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.94707,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15746,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15776,
        "r": [
          [
            "MARIN",
            13
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15828,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15858,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97769,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15888,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97769,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 15918,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15948,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
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
        "f": 15978,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
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
        "f": 16008,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.98675,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16038,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.98161,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16068,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
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
        "f": 16098,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97384,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16128,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97384,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16158,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97412,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16188,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97412,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16218,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
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
        "f": 16248,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97723,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16278,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.98761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16308,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.98761,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16338,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
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
        "f": 16368,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.94333,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16398,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97902,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16428,
        "r": [
          [
            "MARIN",
            14
          ],
          [
            "AN S.Y.",
            7
          ]
        ],
        "c": 0.97902,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16458,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            8
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
        "f": 16488,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.97789,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16518,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            8
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
        "f": 16548,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            8
          ]
        ],
        "c": 0.98283,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16578,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            8
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
        "f": 16644,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
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
        "f": 16674,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.95254,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16704,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
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
        "f": 16734,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
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
        "f": 16764,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.94648,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16794,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.94648,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16824,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
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
        "f": 16854,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
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
        "f": 16884,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.9572,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16914,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.979,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16944,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.98089,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 16974,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.98089,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17004,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
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
        "f": 17034,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
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
        "f": 17064,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.9775,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17094,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.97744,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17124,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.97942,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17154,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.97773,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17184,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.97806,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17214,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            9
          ]
        ],
        "c": 0.97955,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17244,
        "r": [
          [
            "MARIN",
            15
          ],
          [
            "AN S.Y.",
            10
          ]
        ],
        "c": 0.95422,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17274,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.97169,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17304,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.9365,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17334,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.93583,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17364,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.97204,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17394,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.97204,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17424,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
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
        "f": 17454,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
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
        "f": 17484,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.98362,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17514,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.97693,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17544,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.98505,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17574,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.98505,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17604,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
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
        "f": 17634,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
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
        "f": 17664,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
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
        "f": 17694,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
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
        "f": 17724,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            11
          ]
        ],
        "c": 0.96217,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17771,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.97384,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17801,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.98033,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17831,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.9814,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17861,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.9814,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17891,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.97945,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17921,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.97934,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17951,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.97724,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 17981,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.98027,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18011,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95485,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18041,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95485,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18071,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
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
        "f": 18101,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
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
        "f": 18131,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95211,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18161,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95211,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18191,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.9524,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18221,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.9524,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18251,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.95282,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18281,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            12
          ]
        ],
        "c": 0.94183,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18336,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
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
        "f": 18366,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.98219,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18396,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 18426,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 18456,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.97498,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18486,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 18516,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 18546,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.98781,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18576,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.98781,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18606,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.95755,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18636,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.95755,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18666,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 18696,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 18726,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 18756,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.94723,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18786,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.98184,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18816,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.98184,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18846,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.98184,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18876,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.98184,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18906,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 18936,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.97098,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18966,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.97663,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 18996,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
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
        "f": 19026,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.97663,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19056,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.9762,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19086,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.97632,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19116,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.97632,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19146,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.97633,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19176,
        "r": [
          [
            "MARIN",
            16
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.97633,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19235,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.93651,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19265,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.94257,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19295,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.94257,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19325,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.94073,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19355,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.94073,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19385,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.95067,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19415,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
          ]
        ],
        "c": 0.96229,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19445,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
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
        "f": 19475,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
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
        "f": 19505,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
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
        "f": 19535,
        "r": [
          [
            "MARIN",
            17
          ],
          [
            "AN S.Y.",
            13
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
        "f": 19569,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.94885,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19599,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            15
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
        "f": 19629,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.95137,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19659,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.94721,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19689,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            15
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
        "f": 19719,
        "r": [
          [
            "MARIN",
            18
          ],
          [
            "AN S.Y.",
            15
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
        "f": 19749,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.95427,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19779,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            15
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
        "f": 19809,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.95909,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19839,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.96055,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19869,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.94637,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19899,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.9475,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19929,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.94866,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19959,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.94866,
        "ctx": {
          "view": "main",
          "analysis_excluded": false,
          "actual_replay_status": "unknown",
          "acquisition_policy": "main_camera"
        }
      },
      {
        "f": 19989,
        "r": [
          [
            "MARIN",
            19
          ],
          [
            "AN S.Y.",
            15
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
        "f": 20019,
        "r": [
          [
            "MARIN",
            20
          ],
          [
            "AN S.Y.",
            15
          ]
        ],
        "c": 0.9489,
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
      "camera_rows": 20034,
      "player_rows": 36856,
      "nonfinite_projected_court_rows": 0,
      "player_projected_court_rows": 36454,
      "projected_court_on_propagated_box": 21558,
      "racket_rows": 12370,
      "shuttle_rows": 20034
    },
    "categories": {
      "player_id": {
        "None": 36856
      },
      "detector_matched": {
        "True": 15092,
        "False": 21764
      }
    },
    "invalid_geometry_frame_count": 1499,
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
