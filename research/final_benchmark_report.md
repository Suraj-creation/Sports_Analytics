# Final Test 1 pipeline investigation and benchmark

This is an exploratory development benchmark on one exposed source, not held-out validation. The original video, all 36 labels, matching policy and frozen baseline remain unchanged.

Fresh full-video candidate completed at production source `3653b0deee367297037de449d882e9945e6d9c28`. All 1766 frozen artifact hashes, original media/CSV hashes and active checkpoint bytes were rechecked. The final prediction CSV has exactly seven columns.

## Dataset and conventions

The sole source is `Test1_Full_rev.mp4`: 1920 × 1080, 30 FPS, 17,268 decoded frames, 575.6 seconds. Production uses its normal 1280 × 720 CFR proxy; the original is unmodified. Ground truth is `Part2/dataset/Test1_Full/Test1_Full_rally.csv`, with 36 intervals and exactly `Start_Frame,End_Frame,Start_Time_sec,End_Time_sec,Duration_sec,Start_Time,End_Time`.

Frame indices use the established zero-origin arithmetic convention, seconds=frame/30, duration=end timestamp−start timestamp. Human-readable MM:SS truncates to whole seconds. The evaluator measures timestamp spans [start,end), without an inclusive extra frame; production event payload duration is not substituted for that span. The unavailable human annotation-tool history leaves possible one-frame physical-boundary ambiguity. No offset was fitted and no annotations were changed.

Source SHA256: `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`. Annotation SHA256: `30651cf7238924d6a5072b1dd71d34ca5839cd5b842f696e745229033ae4f887`.

## Diagnosis and implementation

Seven independent audits, an exact 49-interval/end-reason/432-live-contact baseline replay and 55 baseline diagnostic packages preceded production edits. See root_cause_analysis.md, improvement_strategy.md, experiment_matrix.md and implementation_roadmap.md for evidence, alternative explanations, risks and ownership.

Implemented separately: parameter-sized stationary history; post-contact history rebasing; recovery based on observed motion onset rather than confirmation; injected model-root correctness; an optional typed sport-owned observation/provider retaining observed/reconstructed/missing/invalid distinctions and legacy compatibility; strict frame-aligned participant-motion and reconstruction quality helpers; bounded observed image-exit/re-entry support; isolated experiment/resource reporting.

Selected provider: `rally-evidence-v2`, image-exit recovery enabled, generic reconstruction and motion guards disabled. The regular GPU profile remains unchanged. The explicit exploratory profile is config/profiles/gpu-rtx4000-rally-evidence.yaml. No detector/pose/racket/outcome/scoring capability was removed, and no weight/environment replacement was performed.

Production entry point: `SessionRunner._ensure_media` then `SessionRunner._analyse`, using the normal `BadmintonSession`/perception/`BadmintonMatchEngine` chain. The research wrapper isolates output and records resources; it does not substitute predictions or consume labels inside inference. TrackNetV3 remains 512 × 288, eight-frame windows, step8, threshold0.5, batch4, CUDA FP16. RF-DETR Small, RTMPose M Body7, geometric racket/contact and production analytics remain active. The effective configuration and actual backend records are preserved in each experiment's metadata/inference JSON.

Verified unchanged active checkpoint artifacts:

| Artifact | SHA256 |
| --- | --- |
| `models/cache/tracknetv3/TrackNet_best.pt` | `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a` |
| `models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx` | `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e` |
| `models/cache/rtmpose_m_body7/rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504.zip` | `f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741` |

## Baseline versus fresh production inference

| Metric | Frozen baseline | Fresh candidate |
| --- | --- | --- |
| predicted_count | 49 | 39 |
| true_positives | 30 | 35 |
| false_positives | 19 | 4 |
| false_negatives | 6 | 1 |
| precision | 0.61224 | 0.89744 |
| recall | 0.83333 | 0.97222 |
| f1 | 0.70588 | 0.93333 |
| start_time_sec.mae (seconds) | 1.6478 | 1.5257 |
| start_time_sec.rmse (seconds) | 2.5084 | 2.4133 |
| start_time_sec.median_absolute_error (seconds) | 0.76667 | 0.96667 |
| start_time_sec.mean_signed_error (seconds) | 1.6011 | 1.3067 |
| end_time_sec.mae (seconds) | 1.3467 | 0.54381 |
| end_time_sec.rmse (seconds) | 3.2154 | 1.3177 |
| end_time_sec.median_absolute_error (seconds) | 0.23333 | 0.2 |
| end_time_sec.mean_signed_error (seconds) | -1.1133 | -0.28095 |
| duration_sec.mae (seconds) | 2.8456 | 1.8943 |
| duration_sec.rmse (seconds) | 4.3464 | 2.7849 |
| duration_sec.median_absolute_error (seconds) | 1.9333 | 1.4333 |
| duration_sec.mean_signed_error (seconds) | -2.7144 | -1.5876 |
| mean_iou | 0.76331 | 0.81781 |
| median_iou | 0.76795 | 0.84281 |
| minimum_iou | 0.504 | 0.53299 |

The start median worsened from 23 to 29 frames, and maximum start error from 202 to 297 frames. GT31 is newly matched but still starts 9.9 seconds late. GT27 still ends 218 frames early; GT23 remains missed. Common matched rows GT4 and GT22 have worse starts. These are unresolved failures, even though aggregate detection and end-boundary quality improve.

## Every rally experiment

All rows use the frozen maximum-cardinality one-to-one assignment, IoU>=0.5 and the same boundary-span convention. Conditional errors and IoU must be read with TP/FP/FN.

| Experiment | Evidence scope | Pred | TP | FP | FN | F1 | Start MAE frames | End MAE frames | Mean IoU |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| frozen-production | fresh full video (original baseline) | 49 | 30 | 19 | 6 | 0.7059 | 49.433 | 40.4 | 0.76331 |
| fsm_correctness/combined | fixed recorded FSM inputs | 48 | 31 | 17 | 5 | 0.7381 | 50.548 | 39.226 | 0.7625 |
| fsm_correctness/contact_history_only | fixed recorded FSM inputs | 49 | 30 | 19 | 6 | 0.7059 | 50.2 | 40.433 | 0.76008 |
| fsm_correctness/control | fixed recorded FSM inputs | 49 | 30 | 19 | 6 | 0.7059 | 49.433 | 40.4 | 0.76331 |
| fsm_correctness/motion_onset_clock_only | fixed recorded FSM inputs | 48 | 31 | 17 | 5 | 0.7381 | 49.806 | 39.194 | 0.76563 |
| evidence_ablations/combined | fixed recorded evidence; first factorial | 43 | 28 | 15 | 8 | 0.7089 | 52.429 | 32.929 | 0.80197 |
| evidence_ablations/disabled | fixed recorded evidence; first factorial | 48 | 31 | 17 | 5 | 0.7381 | 50.548 | 39.226 | 0.7625 |
| evidence_ablations/motion_only | fixed recorded evidence; first factorial | 47 | 27 | 20 | 9 | 0.6506 | 46.926 | 40.296 | 0.78369 |
| evidence_ablations/reconstruction_only | fixed recorded evidence; first factorial | 44 | 32 | 12 | 4 | 0.8000 | 55.25 | 31.781 | 0.77991 |
| image_exit_factorial/all_signals | fixed recorded evidence; extended factorial | 36 | 32 | 4 | 4 | 0.8889 | 46.281 | 17.594 | 0.82617 |
| image_exit_factorial/combined | fixed recorded evidence; extended factorial | 43 | 28 | 15 | 8 | 0.7089 | 52.429 | 32.929 | 0.80197 |
| image_exit_factorial/disabled | fixed recorded evidence; extended factorial | 48 | 31 | 17 | 5 | 0.7381 | 50.548 | 39.226 | 0.7625 |
| image_exit_factorial/exit_motion | fixed recorded evidence; extended factorial | 36 | 32 | 4 | 4 | 0.8889 | 46.281 | 17.594 | 0.82617 |
| image_exit_factorial/exit_only | fixed recorded evidence; extended factorial | 39 | 35 | 4 | 1 | 0.9333 | 45.771 | 16.314 | 0.81781 |
| image_exit_factorial/exit_reconstruction | fixed recorded evidence; extended factorial | 39 | 35 | 4 | 1 | 0.9333 | 45.771 | 16.314 | 0.81781 |
| image_exit_factorial/motion_only | fixed recorded evidence; extended factorial | 47 | 27 | 20 | 9 | 0.6506 | 46.926 | 40.296 | 0.78369 |
| image_exit_factorial/reconstruction_only | fixed recorded evidence; extended factorial | 44 | 32 | 12 | 4 | 0.8000 | 55.25 | 31.781 | 0.77991 |
| image_exit_factorial_verified/all_signals | fixed recorded evidence; verified extended factorial | 36 | 32 | 4 | 4 | 0.8889 | 46.281 | 17.594 | 0.82617 |
| image_exit_factorial_verified/combined | fixed recorded evidence; verified extended factorial | 43 | 28 | 15 | 8 | 0.7089 | 52.429 | 32.929 | 0.80197 |
| image_exit_factorial_verified/disabled | fixed recorded evidence; verified extended factorial | 48 | 31 | 17 | 5 | 0.7381 | 50.548 | 39.226 | 0.7625 |
| image_exit_factorial_verified/exit_motion | fixed recorded evidence; verified extended factorial | 36 | 32 | 4 | 4 | 0.8889 | 46.281 | 17.594 | 0.82617 |
| image_exit_factorial_verified/exit_only | fixed recorded evidence; verified extended factorial | 39 | 35 | 4 | 1 | 0.9333 | 45.771 | 16.314 | 0.81781 |
| image_exit_factorial_verified/exit_reconstruction | fixed recorded evidence; verified extended factorial | 39 | 35 | 4 | 1 | 0.9333 | 45.771 | 16.314 | 0.81781 |
| image_exit_factorial_verified/motion_only | fixed recorded evidence; verified extended factorial | 47 | 27 | 20 | 9 | 0.6506 | 46.926 | 40.296 | 0.78369 |
| image_exit_factorial_verified/reconstruction_only | fixed recorded evidence; verified extended factorial | 44 | 32 | 12 | 4 | 0.8000 | 55.25 | 31.781 | 0.77991 |
| evidence_feature_replay_v1 | recorded-perception semantic replay; rejected combined signals | 43 | 28 | 15 | 8 | 0.7089 | 52.429 | 32.929 | 0.80197 |
| generic-interpolation-pilot | rejected pilot; source validation changed mid-run | 44 | 32 | 12 | 4 | 0.8000 | 62.906 | 36.562 | 0.75497 |
| fresh_image_exit_v1 | fresh full original video | 39 | 35 | 4 | 1 | 0.9333 | 45.771 | 16.314 | 0.81781 |

The verified factorial repeats preserve the earlier predictions/metrics while fixing ambiguous inherited provenance and separately measuring the FSM loop. They are repeats, not independent datasets. The generic pilot is rejected, including its incorrect adjacent-rally join. Motion guarding is rejected despite higher conditional IoU because it loses recall. Contact-history correctness alone is not claimed as an accuracy gain. All original artifacts remain available.

Actual paired TrackNet inference compared 2160 frames/strategy on GPU1: step8/4 accepted 1582/1567 detections in 20.355/29.722 seconds (1.46× component cost), with the upper-image gap still 0/17 for both. It uses fixed background/context and measures continuity, not localization accuracy or a full rally benchmark. No alternative backbone or new weights were adopted. See shuttle_model_comparison.md for primary-source code/weight/data license separation and measured/unmeasured alternatives.

## Fresh boundary and duration detail

| Quantity | MAE | RMSE | Median absolute | Signed bias | P90 absolute | Maximum absolute |
| --- | --- | --- | --- | --- | --- | --- |
| start_frame | 45.771 | 72.4 | 29 | 39.2 | 98.2 | 297 |
| end_frame | 16.314 | 39.53 | 6 | -8.4286 | 27 | 218 |
| start_time_sec | 1.5257 | 2.4133 | 0.96667 | 1.3067 | 3.2733 | 9.9 |
| end_time_sec | 0.54381 | 1.3177 | 0.2 | -0.28095 | 0.9 | 7.2667 |
| duration_sec | 1.8943 | 2.7849 | 1.4333 | -1.5876 | 3.9867 | 9.2333 |

Interval overlap: `{"mean_iou": 0.8178082897707567, "median_iou": 0.842809364548495, "minimum_iou": 0.5329949238578683, "percent_strictly_exceeding": {"0.5": 100.0, "0.75": 68.57142857142857, "0.9": 45.714285714285715, "0.95": 20.0}}`.

Raw IoU and duration distributions, all-GT coverage, fragmentation, no-overlap predictions, merge/split topology and every missed/extra interval are in comparison.json/metrics.json. The comparison CSV contains all 36 ground-truth rows, preserving null errors for misses.

| Tolerance | Seconds | Start count | Start / matched | Start / all GT | End count | End / matched | End / all GT |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ±1 frames | 0.033333 | 0/35 | 0 | 0 | 4/35 | 0.11429 | 0.11111 |
| ±3 frames | 0.1 | 3/35 | 0.085714 | 0.083333 | 9/35 | 0.25714 | 0.25 |
| ±5 frames | 0.16667 | 9/35 | 0.25714 | 0.25 | 17/35 | 0.48571 | 0.47222 |
| ±10 frames | 0.33333 | 14/35 | 0.4 | 0.38889 | 22/35 | 0.62857 | 0.61111 |
| ±15 frames | 0.5 | 15/35 | 0.42857 | 0.41667 | 24/35 | 0.68571 | 0.66667 |
| ±30 frames | 1 | 20/35 | 0.57143 | 0.55556 | 32/35 | 0.91429 | 0.88889 |

## Fragmentation and evidence completeness

| Diagnostic | Frozen baseline | Fresh candidate |
| --- | --- | --- |
| gt_with_multiple_predictions_count | 11 | 3 |
| predictions_without_gt_overlap_count | 0 | 0 |

Fresh multi-segment labels are 23, 27 and 31. The sole unmatched label (23) has partial predicted coverage. All four unmatched predictions overlap annotated play; their IoUs/matching remain insufficient or another segment owns the one-to-one match. No false positive was hidden.

All 17268 perception frame identities are contiguous in 288 cache chunks: no decoded/perception frame indices are missing. Camera-lost state is separately recorded on 285 frames; it does not mean those video frames were dropped. Complete original/proxy PTS grids agree.

Forty fresh diagnostic packages contain all 36 labels and four extra predictions, source-frame overlays, raw shuttle/player/pose observations, inferred contact events, logs and exact FSM transitions. The fresh observations replay to exactly 39 intervals/end reasons and 447 live contact timestamps. This establishes semantic reproduction; only one independent fresh GPU run was performed, so full model-inference determinism is not established. See fresh_image_exit_v1/post_run_validation.json and failure_cases/index.json for hashes and provenance.

## Failure resolution and limitations

Fresh missed GT rows: [23]. Unmatched predictions: 4. See regression_report.md for every common/new match, worsened boundary and unresolved severe outlier. A newly matched partial interval can increase maximum conditional error; this is reported rather than hidden behind F1. remaining_failure_review.md records source-frame observations around the unresolved same-camera edit/preparation and mixed physical/model visibility losses. Visual diagnostics do not authorize changing the supplied annotations.

The new cue is bounded by two observed moving brackets, top 10% image exit/re-entry, at most 2 seconds, existing speed bounds and the same temporal context. It cannot start an exchange, generate a contact, fill coordinates, cross a signaled discontinuity, or recover an already published interval. Its availability depends on actual future anchors within the existing 40-frame-minimum window; no future evidence was invented and no hidden lookahead increase occurred. Physical nonvisibility, poor model localization and uncertain annotation start semantics remain distinct limitations.

OSNet/ReID remains explicitly unavailable at startup; no embeddings or named players were fabricated. All related analytics still execute, but no unlabeled contact, winner, score or shot accuracy is claimed. Real evidence here is singles footage; four-player tests establish contracts, not real doubles quality. Pretrained model training overlap with Test1 is unknown. No independent generalization is proven.

## Runtime and reliability

Fresh whole-run inference time: 1509.996s; 11.4358 frames/s; final frame 17267. The CPU regression suite overlapped startup, so baseline/fresh walltime is not an isolated algorithm-cost experiment. No speedup is claimed.

Per-stage wall aggregates overlap and must not be summed:

```json
{
  "media_ready_wall_seconds": 1.4486502520740032,
  "court_scene_wall_seconds": 105.55362986866385,
  "decode_perception_cache_wall_seconds": 1302.995411339216,
  "semantic_ingest_wall_seconds": 83.72861067252234,
  "perception_court": 99.6248697899282,
  "perception_shuttle": 216.65174994803965,
  "perception_players": 529.9603853514418,
  "perception_ocr": 345.6012304164469
}
```

Measured resource scopes and sampling:

```json
{
  "sampling_interval_s": 2,
  "samples": 741,
  "peak_process_rss_bytes": 2945028096,
  "mean_process_cpu_percent": 442.939127445297,
  "peak_sampled_process_gpu_memory_mib": 2890.0,
  "torch_peak_allocated_bytes": 1133421056,
  "scope_note": "CPU/RSS=current worker process; GPU=nvidia-smi current PID sum, sampled not instantaneous peak; Torch allocator excludes ORT/FFmpeg. CPU percent may exceed100 for multiple cores."
}
```

Baseline CPU/RSS/GPU peaks and per-stage totals were not recorded and remain unavailable. Actual model runtime/fallback/checkpoint records are in inference.json and benchmark_metadata.json; TrackNet is CUDA FP16. ONNX session CUDA-provider ordering does not prove every graph node or tensor is CUDA FP16. Original and fresh source/proxy alignment audits remain separate from browser/HLS mux-origin observations.

## Reproduction and next work

```bash
source ../gpu-env.sh
python research/run_pipeline_experiment.py --output artifacts/benchmarking/experiments/NEW_RUN \
  --rally-implementation rally-evidence-v2 \
  --rally-params '{"use_reconstruction":false,"motion_guard":false,"use_exit_recovery":true}'
```

Use a new directory; existing runs are never overwritten. Tests and exact commands are in component_test_report.md. Predictions and all raw observations/events/resources/logs remain at artifacts/benchmarking/experiments/fresh_image_exit_v1/. Only small reports/results are versioned.

Highest-impact next work: independently review the remaining hard-edit and start-convention cases; label shuttle visibility/location around early misses and static attractors; test background/context and candidate association independently; collect match-disjoint amateur/doubles/cut footage before promotion. Do not expand a generic merge budget or fit a temporal model on these 36 intervals and describe it as held-out performance. Main and the frozen baseline remain untouched.
