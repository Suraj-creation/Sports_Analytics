# Test 1 rally boundary benchmark

Real full-video production inference completed on `Benchmarking` at production commit `301baf08be5e989dd0ed93cb885733c3cf6f356a`. This report evaluates rally starts and ends only.

## A. Dataset

Original: `Test1_Full_rev.mp4`, 1920×1080, 30 FPS, 17268 decoded frames, 575.6 seconds. The only downloaded video is the original Test 1 file (1,026,166,541 bytes). No original transcoding or trimming was performed.

Source SHA-256: `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`.

Ground truth: `Part2/dataset/Test1_Full/Test1_Full_rally.csv`, 36 manually annotated intervals as identified by the user. SHA-256: `30651cf7238924d6a5072b1dd71d34ca5839cd5b842f696e745229033ae4f887`. All seven columns were validated; annotations were not edited.

`Start_Frame` and `End_Frame` are rally boundary frame indices; `Start_Time_sec` and `End_Time_sec` are the corresponding seconds; `Duration_sec` is end minus start; `Start_Time` and `End_Time` are MM:SS truncated to whole seconds. Source FPS was independently measured. Packet PTS and full decode establish a zero-origin CFR grid; the related Part2 shuttle file enumerates the same 0..17267 frames. No frame offset was fitted. Original annotation-tool history is unavailable, so a possible one-frame human labeling convention remains a limitation. Boundary-span IoU/duration use [start time,end time), without adding one inclusive frame.

## B. Production configuration

Entry point: `bai_engine.runtime.runner.SessionRunner._ensure_media()` and `_analyse()` in a fresh isolated repository. The host selects the existing badminton plugin, VOD TrackNetV3, and `rally-fsm-v1`. The normal 720p CFR proxy is analyzed. All current final `rally_end` events are exported, including non-official exchanges; outcomes, scoring and shot count never filter predictions.

Frozen profile: `gpu-rtx4000`; SHA-256 `ae83f0a05dc9c86543c95ec50c9475b65dc677a91e18b69065092c8df2cc6395`. Actual full-video inference elapsed time: 1469.2 seconds. Final processed frame: 17267.

TrackNetV3: 512×288, 8-frame non-overlapping windows, step 8, threshold 0.5, batch 4, CUDA FP16. RF-DETR Small, RTMPose M Body7 and geometric racket/contact evidence remain in the production composition. Format is inferred by the production layer. See `PIPELINE_TRACE.md` for the complete upstream path and gates.

FSM defaults: start after 3 observed moving frames >3 px/frame or accepted contact; end after 10 invisible frames or 7/10 stationary observations <3 px/frame; 15-frame lookahead; resume >6 px/frame; minimum duration 2 seconds; merge gap 0.75 seconds. The match engine uses 40-frame lookahead and 45-frame backward context. No tuning was performed.

Actual execution backends from the loaded component runtime records (the legacy inspection helper could not unwrap the shuttle port):

```json
{
  "shuttle": {
    "requested_backend": "torch-cuda",
    "actual_backend": "torch-cuda",
    "device": "cuda:0",
    "dtype": "torch.float16",
    "backend_fallback": false,
    "requested_precision": "fp16",
    "checkpoint_sha256": "df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a"
  },
  "player_detector": {
    "requested_backend": "onnx-cuda",
    "providers": [
      "CUDAExecutionProvider",
      "CPUExecutionProvider"
    ],
    "actual_backend": "onnx-cuda",
    "backend_fallback": false
  },
  "pose": {
    "requested_backend": "onnx-cuda",
    "providers": [
      "CUDAExecutionProvider",
      "CPUExecutionProvider"
    ],
    "actual_backend": "onnx-cuda",
    "backend_fallback": false
  }
}
```

Model/checkpoint identifiers and actual runtime fingerprints are in `inference.json` and `benchmark_metadata.json`, including TrackNet checkpoint digest, RF-DETR/pose pins and OCR-stage hashes.

Recorded degradation:

```json
[
  {
    "stage": "player_identity",
    "reason": "osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"
  },
  {
    "stage": "player_reid",
    "reason": "baseline player_reid provider is unavailable"
  }
]
```

## C. Results

Matching was frozen before inference: maximum-cardinality one-to-one bipartite assignment of pairs with temporal IoU ≥0.5, then maximum total IoU with a tiny boundary-proximity preference. Rows are never matched by index. Boundary metrics condition on those eligible matches.

| Ground truth | Predictions | Matched / TP | FP | FN | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36 | 49 | 30 | 19 | 6 | 0.6122 | 0.8333 | 0.7059 |

Signed errors are prediction minus annotation. Timing errors use precise seconds, not MM:SS.

| Boundary / unit | MAE | Median absolute | RMSE | Maximum absolute | P90 absolute |
| --- | --- | --- | --- | --- | --- |
| start_frame | 49.4333 | 23 | 75.2531 | 202 | 117.6 |
| start_time_sec | 1.64778 | 0.766667 | 2.50844 | 6.73333 | 3.92 |
| end_frame | 40.4 | 7 | 96.4631 | 442 | 103.8 |
| end_time_sec | 1.34667 | 0.233333 | 3.21544 | 14.7333 | 3.46 |

Duration (seconds): MAE 2.84556; RMSE 4.34638; median absolute error 1.93333; mean signed error -2.71444; median signed error -1.93333.

Interval overlap:

```json
{
  "mean_iou": 0.7633148904564976,
  "median_iou": 0.7679480019856078,
  "minimum_iou": 0.5040000000000002,
  "percent_strictly_exceeding": {
    "0.5": 100.0,
    "0.75": 50.0,
    "0.9": 36.666666666666664,
    "0.95": 6.666666666666667
  }
}
```

| Tolerance | Seconds | Starts within / matched | Start accuracy / all GT | Ends within / matched | End accuracy / all GT |
| --- | --- | --- | --- | --- | --- |
| ±1 frames | 0.0333333 | 0/30 (0) | 0 | 4/30 (0.133333) | 0.111111 |
| ±3 frames | 0.1 | 3/30 (0.1) | 0.0833333 | 8/30 (0.266667) | 0.222222 |
| ±5 frames | 0.166667 | 7/30 (0.233333) | 0.194444 | 12/30 (0.4) | 0.333333 |
| ±10 frames | 0.333333 | 12/30 (0.4) | 0.333333 | 17/30 (0.566667) | 0.472222 |
| ±15 frames | 0.5 | 14/30 (0.466667) | 0.388889 | 18/30 (0.6) | 0.5 |
| ±30 frames | 1 | 18/30 (0.6) | 0.5 | 24/30 (0.8) | 0.666667 |

## D. Failure analysis

Missed ground-truth rally IDs (one-based CSV rows): [5, 23, 25, 28, 29, 31].

Every label is represented in `rally_comparison.csv` with matched/missed status, signed and absolute frame errors, time errors, durations and IoU. False positives are listed below and separately in `metrics.json`; they are not discarded to force 36 rows.

```json
[
  {
    "pred_rally": 2,
    "start_frame": 891,
    "end_frame": 1023,
    "start": 29.7,
    "end": 34.1
  },
  {
    "pred_rally": 5,
    "start_frame": 1585,
    "end_frame": 1654,
    "start": 52.833333333333336,
    "end": 55.13333333333333
  },
  {
    "pred_rally": 7,
    "start_frame": 2309,
    "end_frame": 2423,
    "start": 76.96666666666667,
    "end": 80.76666666666667
  },
  {
    "pred_rally": 21,
    "start_frame": 8110,
    "end_frame": 8266,
    "start": 270.3333333333333,
    "end": 275.53333333333336
  },
  {
    "pred_rally": 24,
    "start_frame": 9548,
    "end_frame": 9646,
    "start": 318.26666666666665,
    "end": 321.53333333333336
  },
  {
    "pred_rally": 25,
    "start_frame": 9685,
    "end_frame": 9947,
    "start": 322.8333333333333,
    "end": 331.56666666666666
  },
  {
    "pred_rally": 28,
    "start_frame": 10769,
    "end_frame": 10908,
    "start": 358.96666666666664,
    "end": 363.6
  },
  {
    "pred_rally": 29,
    "start_frame": 10949,
    "end_frame": 11085,
    "start": 364.96666666666664,
    "end": 369.5
  },
  {
    "pred_rally": 31,
    "start_frame": 11634,
    "end_frame": 11745,
    "start": 387.8,
    "end": 391.5
  },
  {
    "pred_rally": 32,
    "start_frame": 11801,
    "end_frame": 11867,
    "start": 393.3666666666667,
    "end": 395.56666666666666
  },
  {
    "pred_rally": 35,
    "start_frame": 12771,
    "end_frame": 12954,
    "start": 425.7,
    "end": 431.8
  },
  {
    "pred_rally": 36,
    "start_frame": 13176,
    "end_frame": 13252,
    "start": 439.2,
    "end": 441.73333333333335
  },
  {
    "pred_rally": 37,
    "start_frame": 13273,
    "end_frame": 13439,
    "start": 442.43333333333334,
    "end": 447.96666666666664
  },
  {
    "pred_rally": 38,
    "start_frame": 13686,
    "end_frame": 13843,
    "start": 456.2,
    "end": 461.43333333333334
  },
  {
    "pred_rally": 39,
    "start_frame": 13883,
    "end_frame": 13982,
    "start": 462.76666666666665,
    "end": 466.06666666666666
  },
  {
    "pred_rally": 41,
    "start_frame": 14491,
    "end_frame": 14646,
    "start": 483.03333333333336,
    "end": 488.2
  },
  {
    "pred_rally": 42,
    "start_frame": 14701,
    "end_frame": 14969,
    "start": 490.03333333333336,
    "end": 498.96666666666664
  },
  {
    "pred_rally": 43,
    "start_frame": 14994,
    "end_frame": 15171,
    "start": 499.8,
    "end": 505.7
  },
  {
    "pred_rally": 45,
    "start_frame": 15668,
    "end_frame": 15735,
    "start": 522.2666666666667,
    "end": 524.5
  }
]
```

Matched boundaries exceeding ±15 frames:

| GT rally | Pred rally | Start error (frames) | End error (frames) | IoU |
| --- | --- | --- | --- | --- |
| 1 | 1 | 96 | 2 | 0.793249 |
| 2 | 3 | 179 | -7 | 0.504 |
| 3 | 4 | 4 | -103 | 0.597744 |
| 6 | 8 | 103 | -7 | 0.556452 |
| 8 | 10 | 72 | 3 | 0.696356 |
| 9 | 11 | 112 | -14 | 0.608696 |
| 10 | 12 | 97 | -111 | 0.648649 |
| 11 | 13 | 29 | -18 | 0.728324 |
| 12 | 14 | 25 | 16 | 0.910284 |
| 13 | 15 | 21 | -2 | 0.935028 |
| 14 | 16 | 69 | -17 | 0.686131 |
| 15 | 17 | 87 | -5 | 0.532995 |
| 16 | 18 | 30 | 39 | 0.867562 |
| 19 | 22 | 202 | -1 | 0.611111 |
| 20 | 23 | 32 | -442 | 0.630841 |
| 21 | 26 | 5 | -24 | 0.908805 |
| 22 | 27 | -6 | 29 | 0.742647 |
| 26 | 33 | 70 | -1 | 0.678733 |
| 27 | 34 | 4 | -218 | 0.568932 |
| 33 | 46 | 168 | 5 | 0.512676 |
| 35 | 48 | 8 | -92 | 0.805068 |
| 36 | 49 | 8 | -22 | 0.8125 |

Per-label raw-perception diagnostic evidence:

| GT rally | Match status | Raw observed shuttle fraction | Camera lost frames | Overlapping production segments / end reasons |
| --- | --- | --- | --- | --- |
| 1 | matched | 0.835 | 0 | 339–717 (gap) |
| 2 | matched | 0.832 | 0 | 891–1023 (gap); 1066–1255 (stationary) |
| 3 | matched | 0.884 | 0 | 1402–1561 (gap); 1585–1654 (stationary) |
| 4 | matched | 0.837 | 0 | 1889–2167 (gap) |
| 5 | missed | 0.684 | 0 | 2309–2423 (gap) |
| 6 | matched | 0.679 | 16 | 2661–2799 (gap) |
| 7 | matched | 0.973 | 0 | 2983–3377 (stationary) |
| 8 | matched | 0.739 | 14 | 3523–3698 (stationary) |
| 9 | matched | 0.765 | 15 | 3863–4059 (stationary) |
| 10 | matched | 0.766 | 0 | 4344–4728 (gap) |
| 11 | matched | 0.971 | 0 | 4901–5027 (stationary) |
| 12 | matched | 0.905 | 0 | 5455–5887 (stationary) |
| 13 | matched | 0.904 | 2 | 5979–6310 (stationary) |
| 14 | matched | 0.640 | 10 | 6451–6639 (gap) |
| 15 | matched | 0.687 | 0 | 6803–6908 (stationary) |
| 16 | matched | 0.919 | 15 | 7006–7497 (stationary) |
| 17 | matched | 0.943 | 0 | 7535–7731 (gap) |
| 18 | matched | 0.935 | 0 | 7953–8052 (stationary) |
| 19 | matched | 0.851 | 0 | 8110–8266 (gap); 8308–8627 (gap) |
| 20 | matched | 0.896 | 14 | 8715–9525 (gap); 9548–9646 (gap); 9685–9947 (gap) |
| 21 | matched | 0.953 | 0 | 10250–10539 (stationary) |
| 22 | matched | 0.912 | 0 | 10601–10737 (stationary) |
| 23 | missed | 0.850 | 0 | 10601–10737 (stationary); 10769–10908 (gap); 10949–11085 (stationary) |
| 24 | matched | 0.730 | 0 | 11274–11397 (stationary) |
| 25 | missed | 0.698 | 0 | 11634–11745 (gap); 11801–11867 (gap) |
| 26 | matched | 0.716 | 0 | 12046–12196 (stationary) |
| 27 | matched | 0.936 | 0 | 12455–12748 (stationary); 12771–12954 (stationary) |
| 28 | missed | 0.638 | 0 | 13176–13252 (gap); 13273–13439 (gap) |
| 29 | missed | 0.782 | 0 | 13686–13843 (gap); 13883–13982 (stationary) |
| 30 | matched | 0.923 | 0 | 14222–14331 (gap) |
| 31 | missed | 0.774 | 21 | 14491–14646 (gap); 14701–14969 (gap); 14994–15171 (stationary) |
| 32 | matched | 0.871 | 0 | 15354–15529 (stationary) |
| 33 | matched | 0.775 | 0 | 15668–15735 (gap); 15764–15951 (gap) |
| 34 | matched | 0.941 | 0 | 15983–16385 (stationary) |
| 35 | matched | 0.874 | 0 | 16521–16934 (gap) |
| 36 | matched | 0.845 | 0 | 17074–17204 (stationary) |

Production end-reason counts: `{"gap": 26, "stationary": 23}`.

Among the 30 matched rallies, starts are late in 28 and early in 2; ends are early in 21 and late in 8. Exact boundaries account for the remainder. Ground-truth intervals overlapping multiple production segments: [2, 3, 19, 20, 23, 25, 27, 28, 29, 31, 33]. Those overlaps identify possible fragmentation for review; the table preserves each segment's actual end gate rather than assigning a guessed perception failure.

6 of 6 policy-missed labels have some overlapping production segment: [5, 23, 25, 28, 29, 31]. Thus these false negatives reflect inadequate interval agreement, not complete absence of detections throughout each such annotated rally. The table above gives the exact fragment boundaries; the diagnostic JSON records each label's main-view and camera-lost/replay coverage. These are observed associations, not proof that every dropout or split has the same cause.

These recorded reasons locate the final segmentation gate (gap/stationary/cut/flush); they do not prove why perception lost the shuttle or whether a manual boundary is correct. `boundary_diagnostics.json` also records view/calibration/replay counts. Raw visibility is before the engine's spike removal and temporal validity gates, so it must not be treated as the FSM's observed-motion coverage. No model-output-derived annotation or causal claim substitutes for frame review.

## E. Limitations

One supplied video cannot establish generalization. The checkpoint training overlap with this source and any prior detector tuning exposure to Test 1/Part2 are unknown. This is a current-state baseline, not independently held-out validation. The user identifies the CSV as manual ground truth, but independent annotation review/tool provenance is unavailable. The older Part2 result tables use similar schemas and are not used to generate or correct predictions. Potential sub-frame/one-frame human labeling ambiguity remains; no data-driven offset correction is applied.

The configured optional OSNet appearance checkpoint was unavailable; production degradation is retained above. Actual providers are reported separately from requested profile names. Raw inference runs on the production proxy rather than directly on original pixels, as the application does. Timeline audits prevent silent source/proxy frame-count or FPS mismatch. Boundary error statistics cover only IoU-qualified matched intervals; poor/non-overlapping segments are reflected in FP/FN rather than conditional MAE. No shot, player, outcome or score accuracy is measured.

## F. Next steps

1. Prioritize interval continuity: review policy-missed labels [5, 23, 25, 28, 29, 31] and the 11 labels overlapping multiple production segments. Inspect the recorded gap and stationary gates against original frames and postprocessing evidence before any threshold changes.
2. Prioritize late starts (28 of 30 matched) and the largest early ends (GT row, signed frame error): [(20, -442), (27, -218)]. Inspect observed motion, spike rejection and accepted-contact support around those exact boundaries. The recorded end reason locates a gate, not its root cause.
3. Review start runs/contact support against the 1.60111-second mean signed start error; obtain independent annotation-tool/frame-base confirmation before applying any offset.
4. Keep this unchanged baseline. Any model restoration or threshold experiment must use a separate output, be marked exploratory on Test 1, and be validated on an independently held-out annotated source before claiming improvement in generalization.

## Reproduction and evidence

See `scripts/benchmarking/README.md` for commands and `PIPELINE_TRACE.md` for the inspected production path. `predicted_rallies.csv` has exactly the original seven columns. `metrics.json`, `metrics.md`, `rally_comparison.csv`, `benchmark_metadata.json`, source/annotation audits and this report are small review artifacts. Original media, isolated runtime, raw events and `execution.log` remain on disk and are ignored by Git. Main and production code remain unchanged. The synthetic evaluator suite passed before expensive inference.
