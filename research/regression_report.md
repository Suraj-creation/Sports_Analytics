# Regression and controlled-experiment report

**Status: fresh full-video production inference completed and independently audited.** The measured Test1 improvement is supported by a complete new inference run, not only by cached replay. It remains exploratory development evidence; no result establishes held-out generalization or warrants an automatic default promotion.

Frozen production: `301baf08be5e989dd0ed93cb885733c3cf6f356a`; frozen evidence commit: `b773e20c62d1c398cddc3d23510bd4adf823325b`. Baseline files below `outputs/benchmarking/test1` remain immutable. Current selected fresh-run code: `3653b0deee367297037de449d882e9945e6d9c28`.

## Evidence levels and independent verification

1. **Frozen full-video baseline:** real production inference,49 predictions,30TP,19FP,6FN. Original video/labels and numerical conventions are unchanged.
2. **Fixed-input controls and factorials:** production FSM/evidence behavior on the recorded baseline input trace; these establish intervention effects conditional on those same observations. They do not include perception/player/pose scheduling feedback.
3. **Recorded-perception semantic replays:** real production semantic code consuming cached observations; still not fresh model inference. The initial generic reconstruction pilot is invalid for acceptance because its source-validation implementation changed while running.
4. **Actual TrackNet component pair:** fresh GPU inference on2160fixed frames per strategy, not a rally/full-pipeline benchmark.
5. **Fresh full-video candidate:** completed new production processing of all17,268frames of the original video using an explicit opt-in profile. It produced39predictions,35TP,4FP,1FN; its complete accuracy outputs equal the selected fixed-input candidate exactly.

As a separate read-only check for this report, all27 completed rally-metric artifacts (including the eight verified-factorial repeats and fresh run) reproduced exactly using the unchanged evaluator, with36 comparison rows each. Both selected `exit_only` and fresh full-video assignments also matched an independent exact-rational ordered dynamic program:35 pairs each. Every field of the fresh36-row comparison CSV was checked against the unchanged evaluator. The original baseline audit independently verified all30 baseline pairs, full statistics/tolerances, event-to-CSV export, input/artifact hashes and86 production source hashes. See `research/benchmark_audit.md/json`. No prediction or label was edited to obtain these checks.

The primary policy stays maximum-cardinality one-to-one matching at temporal IoU>=0.5, then the documented IoU/proximity preference. Time intervals use boundary timestamp spans [start,end), with no inclusive extra frame. In particular, GT29 baseline157/315IoU remains a legitimate FN; no endpoint or threshold change was used to promote it.

## Every recorded rally experiment

P=predictions; start/end MAE are frames and conditional on each run's own matched set. Numbers from invalid pilots remain visible but are not acceptance evidence.

| Experiment | Evidence class | P | TP | FP | FN | F1 | Start MAE | End MAE | Mean IoU | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Frozen baseline | Fresh full video | 49 | 30 | 19 | 6 | .705882 | 49.433 | 40.400 | .763315 | Immutable control |
| `fresh_image_exit_v1` | Actual fresh full video | 39 | 35 | 4 | 1 | 0.933333 | 45.771 | 16.314 | 0.817808 | Confirmed Test1 gain; residual regressions remain; opt-in only |
| `evidence_ablations/combined` | Fixed recorded input | 43 | 28 | 15 | 8 | 0.708861 | 52.429 | 32.929 | 0.801974 | Rejected as preferred candidate: detection/outlier tradeoff |
| `evidence_ablations/disabled` | Fixed recorded input | 48 | 31 | 17 | 5 | 0.738095 | 50.548 | 39.226 | 0.762498 | Control/ablation only |
| `evidence_ablations/motion_only` | Fixed recorded input | 47 | 27 | 20 | 9 | 0.650602 | 46.926 | 40.296 | 0.783692 | Rejected as preferred candidate: detection/outlier tradeoff |
| `evidence_ablations/reconstruction_only` | Fixed recorded input | 44 | 32 | 12 | 4 | 0.800000 | 55.250 | 31.781 | 0.779913 | Not preferred: worse start MAE/new outliers |
| `evidence_feature_replay_v1` | Cached semantic replay | 43 | 28 | 15 | 8 | 0.708861 | 52.429 | 32.929 | 0.801974 | Combined signal rejected |
| `fsm_correctness/combined` | Fixed recorded input | 48 | 31 | 17 | 5 | 0.738095 | 50.548 | 39.226 | 0.762498 | Correctness baseline for subsequent factorials |
| `fsm_correctness/contact_history_only` | Fixed recorded input | 49 | 30 | 19 | 6 | 0.705882 | 50.200 | 40.433 | 0.760080 | Correctness repair; slight benchmark MAE regression |
| `fsm_correctness/control` | Fixed recorded input | 49 | 30 | 19 | 6 | 0.705882 | 49.433 | 40.400 | 0.763315 | Control/ablation only |
| `fsm_correctness/motion_onset_clock_only` | Fixed recorded input | 48 | 31 | 17 | 5 | 0.738095 | 49.806 | 39.194 | 0.765629 | Correctness repair; one extra matched label |
| `image_exit_factorial/all_signals` | Fixed recorded input | 36 | 32 | 4 | 4 | 0.888889 | 46.281 | 17.594 | 0.826168 | Rejected as preferred candidate: detection/outlier tradeoff |
| `image_exit_factorial/combined` | Fixed recorded input | 43 | 28 | 15 | 8 | 0.708861 | 52.429 | 32.929 | 0.801974 | Rejected as preferred candidate: detection/outlier tradeoff |
| `image_exit_factorial/disabled` | Fixed recorded input | 48 | 31 | 17 | 5 | 0.738095 | 50.548 | 39.226 | 0.762498 | Control/ablation only |
| `image_exit_factorial/exit_motion` | Fixed recorded input | 36 | 32 | 4 | 4 | 0.888889 | 46.281 | 17.594 | 0.826168 | Rejected as preferred candidate: detection/outlier tradeoff |
| `image_exit_factorial/exit_only` | Fixed recorded input | 39 | 35 | 4 | 1 | 0.933333 | 45.771 | 16.314 | 0.817808 | Favored for fresh validation; no extra reconstruction gain |
| `image_exit_factorial/exit_reconstruction` | Fixed recorded input | 39 | 35 | 4 | 1 | 0.933333 | 45.771 | 16.314 | 0.817808 | Favored for fresh validation; no extra reconstruction gain |
| `image_exit_factorial/motion_only` | Fixed recorded input | 47 | 27 | 20 | 9 | 0.650602 | 46.926 | 40.296 | 0.783692 | Rejected as preferred candidate: detection/outlier tradeoff |
| `image_exit_factorial/reconstruction_only` | Fixed recorded input | 44 | 32 | 12 | 4 | 0.800000 | 55.250 | 31.781 | 0.779913 | Not preferred: worse start MAE/new outliers |
| `image_exit_factorial_verified/all_signals` | Verified fixed-input repeat | 36 | 32 | 4 | 4 | 0.888889 | 46.281 | 17.594 | 0.826168 | Same rejected detection/outlier tradeoff reproduced |
| `image_exit_factorial_verified/combined` | Verified fixed-input repeat | 43 | 28 | 15 | 8 | 0.708861 | 52.429 | 32.929 | 0.801974 | Same rejected detection/outlier tradeoff reproduced |
| `image_exit_factorial_verified/disabled` | Verified fixed-input repeat | 48 | 31 | 17 | 5 | 0.738095 | 50.548 | 39.226 | 0.762498 | Same result as prior switch setting; measured FSM-only time |
| `image_exit_factorial_verified/exit_motion` | Verified fixed-input repeat | 36 | 32 | 4 | 4 | 0.888889 | 46.281 | 17.594 | 0.826168 | Same rejected detection/outlier tradeoff reproduced |
| `image_exit_factorial_verified/exit_only` | Verified fixed-input repeat | 39 | 35 | 4 | 1 | 0.933333 | 45.771 | 16.314 | 0.817808 | Selected result repeated exactly; exit-only fresh confirmed |
| `image_exit_factorial_verified/exit_reconstruction` | Verified fixed-input repeat | 39 | 35 | 4 | 1 | 0.933333 | 45.771 | 16.314 | 0.817808 | Selected result repeated exactly; exit-only fresh confirmed |
| `image_exit_factorial_verified/motion_only` | Verified fixed-input repeat | 47 | 27 | 20 | 9 | 0.650602 | 46.926 | 40.296 | 0.783692 | Same rejected detection/outlier tradeoff reproduced |
| `image_exit_factorial_verified/reconstruction_only` | Verified fixed-input repeat | 44 | 32 | 12 | 4 | 0.800000 | 55.250 | 31.781 | 0.779913 | Same start/outlier regressions reproduced |
| `reconstruction_semantic` | Cached semantic pilot | 44 | 32 | 12 | 4 | 0.800000 | 62.906 | 36.562 | 0.754966 | Invalid for acceptance: source changed; bad merge |

The `image_exit_feature_replay_v1` directory currently contains partial replay artifacts without final metrics. It is not counted as a successful/evaluated run and is not used for acceptance. Duplicate factorial outputs are listed deliberately: they establish which added signal changes nothing under this fixed input, rather than implying independent replications.

## Correctness repairs versus accuracy interventions

- Configured stationary history length, contact history rebasing, and motion-onset recovery clocks address independently established lifecycle/configuration defects. A correctness counterexample is different from evidence of an accuracy gain.
- Contact-history-only retains30TP/19FP/6FN, while start MAE worsens49.433→50.200frames, end MAE40.400→40.433, and mean IoU.763315→.760080. That negative accuracy result is retained.
- Motion-onset-clock-only recovers one label (GT28), raising F1to.738095 with48predictions, but start MAE49.806 is slightly worse than baseline49.433. The combined correctness control has start MAE50.548. Neither is described as a uniformly better boundary detector.
- The first generic interpolation pilot (`reconstruction_semantic`) has F1.80 but joins neighboring labels33/34 around stationary/pickup evidence and loses GT33. Its metadata status is `pilot_requires_frozen_source_repeat`, with the explicit note that invalid-value input validation changed during execution. It is diagnostic only, even though observed valid samples were not edited.
- The subsequent strict moving-bracket reconstruction-only factorial has32TP, 12FP,4FN and start MAE55.250frames; it is measured separately and does not retrospectively validate the earlier pilot.
- Motion guarding is rejected as the favored accuracy configuration: .783692 conditional IoU for motion-only does not outweigh27TP/9FN and F1.650602. Combined reconstruction/motion raises conditional IoUto.801974 but still has28TP/8FN. With exit recovery, adding motion guarding gives32TP/4FN versus exit-only35TP/1FN; higher IoU.826168 versus.817808 and a lower conditional end maximum do not justify concealing the three additional misses.

## Selected fixed-input image-exit candidate

The authoritative factorial setting is `configuration={use_reconstruction:false, motion_guard:false, use_exit_recovery:true}`, intervention `exit_only`. It uses independent observed moving exit/return brackets, bounded temporal/image geometry and the existing unchanged numeric FSM parameters; labels do not enter the segmentation decision. The inherited replay template's `overrides` field contains older settings and is not the actual factorial switch selection; the explicit configuration, intervention and input trace define this comparison. That provenance ambiguity must not be read as evidence that reconstruction was enabled.

The older factorial manifests also inherit an `elapsed_seconds` value from the
source semantic replay. That value is **not a measured per-variant FSM runtime**
and is excluded from runtime comparisons. The completed `image_exit_factorial_verified` repeat now supplies explicit actual
overrides, preserved source replay settings, measured FSM-only time and execution
logs. Independent checking confirmed that all eight prediction CSVs and metrics
JSON files are byte-identical to the corresponding original switch settings.
Every verified manifest has `overrides == configuration`; inherited values are
separated as `source_replay_overrides` and `source_replay_elapsed_seconds`.
Measured FSM-only times range0.131296–0.138145seconds; exit-only is0.131771seconds.
These timings exclude detector inference and are not full-video runtime.
This repeat repairs measurement/provenance, not accuracy.

`exit_only` and `exit_reconstruction` prediction CSVs are byte-identical. The selected predictions hash is `1e227c47b112ce385599f95c3e31e5379dface463aadbc3388346d1c4fd29bc6`, matching the factorial manifest. The original fixed-input trace hash is `ed5764e45157683179e75b347f8911e9f9f0aaa79f0fd1ab4b4aa9d04565893e`.

| Metric | Frozen baseline | Selected fixed-input and actual fresh candidate (identical) |
| --- | --- | --- |
| predicted_count | 49 | 39 |
| true_positives | 30 | 35 |
| false_positives | 19 | 4 |
| false_negatives | 6 | 1 |
| precision | 0.6122448979591837 | 0.8974358974358975 |
| recall | 0.8333333333333334 | 0.9722222222222222 |
| f1 | 0.7058823529411765 | 0.9333333333333333 |
| start_frame.mae | 49.433333 | 45.771429 |
| start_frame.rmse | 75.253128 | 72.400474 |
| start_frame.median_absolute_error | 23.000000 | 29.000000 |
| start_frame.mean_signed_error | 48.033333 | 39.200000 |
| start_frame.p90_absolute_error | 117.600000 | 98.200000 |
| start_frame.max_absolute_error | 202.000000 | 297.000000 |
| end_frame.mae | 40.400000 | 16.314286 |
| end_frame.rmse | 96.463119 | 39.530458 |
| end_frame.median_absolute_error | 7.000000 | 6.000000 |
| end_frame.mean_signed_error | -33.400000 | -8.428571 |
| end_frame.p90_absolute_error | 103.800000 | 27.000000 |
| end_frame.max_absolute_error | 442.000000 | 218.000000 |
| start_time_sec.mae | 1.647778 | 1.525714 |
| start_time_sec.rmse | 2.508438 | 2.413349 |
| start_time_sec.median_absolute_error | 0.766667 | 0.966667 |
| start_time_sec.mean_signed_error | 1.601111 | 1.306667 |
| start_time_sec.p90_absolute_error | 3.920000 | 3.273333 |
| start_time_sec.max_absolute_error | 6.733333 | 9.900000 |
| end_time_sec.mae | 1.346667 | 0.543810 |
| end_time_sec.rmse | 3.215437 | 1.317682 |
| end_time_sec.median_absolute_error | 0.233333 | 0.200000 |
| end_time_sec.mean_signed_error | -1.113333 | -0.280952 |
| end_time_sec.p90_absolute_error | 3.460000 | 0.900000 |
| end_time_sec.max_absolute_error | 14.733333 | 7.266667 |
| duration_sec.mae | 2.845556 | 1.894286 |
| duration_sec.rmse | 4.346378 | 2.784908 |
| duration_sec.median_absolute_error | 1.933333 | 1.433333 |
| duration_sec.mean_signed_error | -2.714444 | -1.587619 |
| duration_sec.p90_absolute_error | 6.783333 | 3.986667 |
| duration_sec.max_absolute_error | 15.800000 | 9.233333 |
| mean_iou | 0.763315 | 0.817808 |
| median_iou | 0.767948 | 0.842809 |
| minimum_iou | 0.504000 | 0.532995 |

This improves multiple aggregate metrics, but the start median worsens23→29frames and global maximum start error worsens202→297frames. Those regressions remain part of acceptance review.

### Common matched set and newly matched rows

All30baseline-matched GT rows remain matched. Five previously missed rows become matched: 5,25,28,29,31. There are no newly missed GT rows; GT23 remains unmatched.

| Comparison set | Count | Baseline start MAE | Candidate start MAE | Baseline end MAE | Candidate end MAE |
| --- | --- | --- | --- | --- | --- |
| Common matched GT rows | 30 | 49.433333 | 36.433333 | 40.400000 | 17.666667 |
| Newly matched GT rows | 5 | unavailable (baseline misses) | 101.800000 | unavailable (baseline misses) | 8.200000 |

The common-set start/end gains are not caused solely by selecting easier matched rows. However, GT31's newly available+297-frame (9.9-second) start error is not a worsened previously matched boundary: it was a baseline miss. It remains a severe residual failure despite becoming a TP. Newly matched mean absolute start error is101.8frames versus36.433on the common set.

### Every GT row, including unchanged controls and residual failures

Errors are prediction minus annotation; blank matched errors are unavailable, never zero.

| GT | Baseline status | Candidate status | Start error frames, baseline→candidate | End error frames, baseline→candidate |
| --- | --- | --- | --- | --- |
| 1 | matched | matched | 96 → 96 | 2 → 2 |
| 2 | matched | matched | 179 → 4 | -7 → -7 |
| 3 | matched | matched | 4 → 4 | -103 → -5 |
| 4 | matched | matched | 15 → -71 | 6 → 6 |
| 5 | missed | matched | unavailable → 99 | unavailable → -4 |
| 6 | matched | matched | 103 → 103 | -7 → -7 |
| 7 | matched | matched | 7 → 7 | 0 → 0 |
| 8 | matched | matched | 72 → 72 | 3 → 4 |
| 9 | matched | matched | 112 → 112 | -14 → -14 |
| 10 | matched | matched | 97 → 97 | -111 → -35 |
| 11 | matched | matched | 29 → 29 | -18 → -18 |
| 12 | matched | matched | 25 → 25 | 16 → 16 |
| 13 | matched | matched | 21 → 21 | -2 → 3 |
| 14 | matched | matched | 69 → 69 | -17 → -17 |
| 15 | matched | matched | 87 → 87 | -5 → -5 |
| 16 | matched | matched | 30 → 30 | 39 → 41 |
| 17 | matched | matched | 3 → 3 | -10 → -10 |
| 18 | matched | matched | 6 → 6 | -1 → -1 |
| 19 | matched | matched | 202 → 4 | -1 → -1 |
| 20 | matched | matched | 32 → 32 | -442 → -20 |
| 21 | matched | matched | 5 → 5 | -24 → -24 |
| 22 | matched | matched | -6 → -29 | 29 → 29 |
| 23 | missed | missed | unavailable → unavailable | unavailable → unavailable |
| 24 | matched | matched | 3 → 3 | 5 → 5 |
| 25 | missed | matched | unavailable → 45 | unavailable → 2 |
| 26 | matched | matched | 70 → 70 | -1 → -1 |
| 27 | matched | matched | 4 → 4 | -218 → -218 |
| 28 | missed | matched | unavailable → 61 | unavailable → -3 |
| 29 | missed | matched | unavailable → 7 | unavailable → -12 |
| 30 | matched | matched | 3 → 3 | -4 → -4 |
| 31 | missed | matched | unavailable → 297 | unavailable → 20 |
| 32 | matched | matched | 4 → 4 | -6 → -6 |
| 33 | matched | matched | 168 → 72 | 5 → 5 |
| 34 | matched | matched | -15 → -15 | -2 → -2 |
| 35 | matched | matched | 8 → 8 | -92 → 5 |
| 36 | matched | matched | 8 → 8 | -22 → -19 |

**Resolved or reduced outliers:** GT2 start+179→+4; GT19 start+202→+4; GT20 end−442→−20; GT3 end−103→−5; GT35 end−92→+5. GT33 start improves+168→+72 but remains substantially late.

**Remaining severe failures:** GT27 end remains−218frames (7.267seconds early); GT31 start is+297frames late; single-interval start delays remain GT1+96,GT6+103,GT8+72,GT9+112, GT10+97,GT14+69,GT15+87,GT26+70,GT33+72. GT23 still has insufficient single-interval agreement, not complete absence of detections.

**Worsened previously matched boundaries:** GT4 start+15→−71 (early by2.367seconds), GT22 start−6→−29; ends GT8+3→+4,GT13−2→+3,GT16+39→+41. These are true common-row regressions and are not explained away by new coverage. The GT4 early start needs original-frame and temporal-support review before any default promotion.

### Fragmentation, unmatched predictions and tolerance denominators

GT rows with multiple overlapping predictions fall11→3: remaining23,27,31. GT-dependent coverage unions are supplementary diagnostics only. All four candidate unmatched predictions overlap GT:10769–10908,10949–11085,12771–12954,14430–14646. The no-GT-overlap prediction count remains0. Cross-run overlap topology identifies9many-to-one interval associations and0one-to-many associations, not independently verified semantic merges.

| Tolerance | Start count baseline→candidate | Start all-GT accuracy baseline→candidate | End count baseline→candidate | End all-GT accuracy baseline→candidate |
| --- | --- | --- | --- | --- |
| ±1frames (0.033333s) | 0→0 | 0.000000→0.000000 | 4→4 | 0.111111→0.111111 |
| ±3frames (0.100000s) | 3→3 | 0.083333→0.083333 | 8→9 | 0.222222→0.250000 |
| ±5frames (0.166667s) | 7→9 | 0.194444→0.250000 | 12→17 | 0.333333→0.472222 |
| ±10frames (0.333333s) | 12→14 | 0.333333→0.388889 | 17→22 | 0.472222→0.611111 |
| ±15frames (0.500000s) | 14→15 | 0.388889→0.416667 | 18→24 | 0.500000→0.666667 |
| ±30frames (1.000000s) | 18→20 | 0.500000→0.555556 | 24→32 | 0.666667→0.888889 |

Matched-only start tolerance accuracy at±30frames changes60.0%→57.14% while all-GT accuracy improves50.0%→55.56% because match coverage grows30→35. At±3frames only3starts are accurate in both runs (all-GT8.33%); no±1frame start is accurate in either. The unchanged fine-tolerance limitation is not hidden behind improved F1 or mean IoU.

## Actual TrackNet step pair: no end-to-end claim

The existing checkpoint ran CUDA FP16 on physical GPU1 for12fixed180-frame windows,2160frames per strategy. Step8 accepted1582outputs in20.355seconds; step4 accepted1567in29.722seconds (1.460×component time), both using1133421056peak allocated bytes and1874853888peak reserved bytes. These are measured component allocator values, not total platform peak memory.

Both variants returned0/17 accepted observations in the upper-image gap9526–9542. Both also returned0/21 in the baseline static-T region12748–12768 under the experiment's fixed global-median/180-frame context. That context differs from baseline rolling background/60-frame chunks, so this disappearance cannot be attributed to step size. No localization ground truth exists for these observations, and no full-pipeline F1 or pretrained-model superiority is claimed. Step4 is not selected for the fresh full-video candidate.

## Fresh full-video result and independent acceptance checks

Run: `artifacts/benchmarking/experiments/fresh_image_exit_v1/`, source commit
`3653b0deee367297037de449d882e9945e6d9c28`, explicit opt-in `rally-evidence-v2`
with `use_exit_recovery=true`, `use_reconstruction=false`, `motion_guard=false`.
The complete original video was processed through production ingest, proxy,
perception and semantic stages. The worker had no ground-truth input.

Actual output is39rallies,35TP,4FP,1FN, precision0.897436, recall0.972222,
F10.933333. Actual start/end MAE are45.771429/16.314286frames
(1.525714/0.543810seconds), duration MAE1.894286seconds, meanIoU0.817808.
These are actual fresh-inference results. All tables and every36-row regression
analysis above also describe this fresh result because its prediction CSV is
**byte-identical** to the selected fixed-input `exit_only` CSV; complete metrics
are value-identical. A fixed-input match is a useful reproducibility observation,
not proof of unseen-video generalization or of repeatability across multiple
independent fresh runs. Only one new full-video run is claimed here.

Independent read-only acceptance checks performed:

- Exact seven-column schema, full-precision timestamps,30FPS arithmetic,
  chronological/disjoint/nonduplicate39intervals and positive durations passed.
- All36comparison rows, every serialized comparison field, complete metrics
  JSON and matching policy reproduce with the unchanged evaluator. An independent
  exact-fraction DP verifies the35pairs. No label, threshold, endpoint convention
  or prediction was edited.
- Independently folded raw `events.jsonl` contains exactly the39current
  `rally_end` intervals exported into the prediction CSV. Other analytics do not
  filter these intervals.
- Metadata and pipeline report `completed`/`analysed`, final frame17,267,
  media frame count17,268, and30/1FPS. The configured chunk size is64, while
  the actual canonical HLS analysis segment size is60frames; both are recorded.
- All88production source fingerprints and the experiment-runner hash match
  their Git objects at the recorded source commit. Original media and annotation
  hashes match the immutable baseline; the prediction hash matches the manifest.
- The fresh proxy SHA-256 is exactly the baseline proxy hash:
  `d352d684fb5399d804b8f50c785a3605346e7f03987ecb1d9a73ef3482535a97`.
  Thus this run did not gain accuracy by using a differently trimmed or retimed
  proxy. Independent source/proxy timeline evidence remains in the temporal audit.
- Cached TrackNetV3, RF-DETR Small and RTMPose archive bytes were independently
  hashed against the recorded registry pins. Those active checkpoint identifiers
  are unchanged from baseline. TrackNet actually reports torch-CUDA,`cuda:0`,
  FP16; detector and pose sessions actually list CUDA providers.
- Missing optional OSNet/player-ReID remains explicitly recorded in both runs.
  No identity-model restoration is credited for the improvement, and no claim is
  made that the identity degradation explains all boundary errors.
- Every recorded frozen-baseline artifact hash checked against its manifest
  remains unchanged. Rejected and invalid experiments remain preserved.

### Runtime and resource regression

| Measurement | Frozen baseline | Fresh candidate | Interpretation |
| --- | --- | --- | --- |
| Production elapsed seconds | 1469.237339 | 1509.995938 | +40.758598seconds, +2.774% in these single runs |
| Processing frames/second | 11.7530 | 11.4358 | Lower throughput in this fresh measurement |
| Peak sampled worker RSS bytes | unavailable | 2945028096 | Current worker process, not whole-system peak |
| Mean worker CPU percent | unavailable | 442.9391 | May exceed100 with multiple cores |
| Peak sampled worker GPU memory MiB | unavailable | 2890 | Sampled current PID, not instantaneous platform peak |
| Torch allocator peak bytes | unavailable | 1133421056 | Excludes ORT and FFmpeg allocations |

The runtime increase is not hidden, but one baseline/candidate run cannot isolate
causality or establish a statistically stable2.774%cost. No baseline peak-memory,
CPU-series or stage timing is invented. Fresh resource sampling used741samples
at a nominal2-second interval.

| Fresh aggregate stage | Wall seconds |
| --- | --- |
| Media ready | 1.448650 |
| Decode/perception/cache parent scope | 1302.995411 |
| Court/scene parent scope | 105.553630 |
| Semantic ingest | 83.728611 |
| Perception court substage | 99.624870 |
| Perception shuttle substage | 216.651750 |
| Perception players/pose substage | 529.960385 |
| Perception OCR substage | 345.601230 |

Parent/child wall aggregates overlap and must not be summed. The runner inserted
no extra CUDA synchronization, so these are measured aggregate wall scopes,
not isolated GPU kernel latency. A complete final frontier and an unchanged
proxy do not convert camera/view loss into decoded-frame-drop evidence; missing
or invalid perception is reported separately rather than renamed dropped frames.

### Fresh result still has genuine regressions and failures

GT23 remains the only policy FN. GT27 still ends218frames early. Newly matched
GT31 has a297-frame late selected start. The genuinely worsened common-row
boundaries remain GT4 start+15→−71,GT22 start−6→−29, and end errors for
GT8+3→+4,GT13−2→+3,GT16+39→+41. Global start maximum and median are worse
than baseline, even though common-set and total start MAE improve. No±1frame
start is accurate. These are not removed from acceptance analysis merely because
F1rose or fresh output matched the chosen replay.

The conclusion is a reproducible, actual Test1 aggregate improvement with explicit
residual and boundary-level regressions. It supports keeping the mechanism as an
opt-in exploratory candidate, not claiming universal production readiness or
promotion without independent annotations and targeted outlier review.

## Promotion and remaining regression risk

The selected mechanism remains explicitly opt-in. It has not been established as a universal improvement or a replacement for stronger perception/contact models. Future independent footage must include short true breaks, stationary pickup, cuts, doubles, occlusion, spectators and adjacent courts. Code-level negative controls support safety but are not manufactured sporting ground-truth annotations for unlabelled clips. No player identity, shot, outcome or scoring accuracy gain is claimed; those capabilities must remain available and their existing integration checks are reported separately in the component test report.

Known remaining tasks are to investigate GT27's static-cluster early termination, GT23 fragmentation, GT31's late matched fragment, the new GT4 early start and persistent single-interval onset delays. Any subsequent threshold/model experiment must be new, separately recorded and exploratory. It must not replace this preserved baseline or retroactively relabel a rejected/invalid run.
