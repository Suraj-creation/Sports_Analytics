# Test2 evaluation — 5 November 2026

The improved experimental pipeline completed two fresh full-video runs and reproduced every perception-cache byte and predicted interval. Against the requested legacy reference, Test2 has **67 TP, 6 FP and 6 FN; precision/recall/F1 0.917808**. Transfer is incomplete: real short exchanges and long-flight continuity remain problematic, and the product produces no official rallies, identity-bound heatmaps or highlights without review/confirmation.

**This is not certified independent sporting accuracy.** Repository provenance identifies `_rally.csv` files as generated legacy proposals. Source review finds omitted real activity, intervals spanning edits and boundaries in preparation/retrieval. All reference rows and extra predictions remain scored unchanged. Two previously exposed broadcast singles recordings cannot establish broad generalization.

## Source, media and pairing

Exact previously shared source: [https://drive.google.com/drive/folders/1_2QWSYd_X_BojdRwbu-AMKdx74cIQvGp?usp=sharing](https://drive.google.com/drive/folders/1_2QWSYd_X_BojdRwbu-AMKdx74cIQvGp?usp=sharing). The original user-history excerpt, live recursive folder listing and historical manifest bind the exact `Test2_Full_Rev.mp4` object; no guessed file link or mirror was substituted. `gdown 6.5.1` resolved that object from the live original folder, handled Drive confirmation and used resumable download. No pre-existing Test2 video was overwritten.

| Field | Verified value |
|---|---|
| Dataset path | /home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/video_raw/Test2_Full_Rev.mp4 |
| Bytes | 2453914397 |
| SHA256 | 4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a |
| Video duration | 976.533333 s |
| Resolution | 1920×1080 |
| Nominal / average FPS | 30/1 / 30/1 |
| Video time base | 1/15360 |
| Decoded frames | 29,296, indices 0–29,295 |
| Codec / pixel format | h264 / yuv420p |
| Audio | aac LC / 48000 Hz / 2 channels / time base 1/48000 |
| CFR verification | All 29,295 source PTS differences are exactly 512 ticks at 1/15360; no decode errors |
| Proxy | 1280×720 CFR30; every rational source/proxy presentation timestamp equal; both proxies byte-identical |


The downloaded bytes match the historical Test2 manifest exactly. Source scoreboard/court inspection identifies the Bangkok Axelsen–Antonsen recording. All legacy shuttle/player tables contain the same 29,296 zero-origin frame population; annotation endpoints fit this duration and FPS. Intended video/reference pairing is supported by identity, timeline, metadata and source inspection; independent boundary-label review is not established. See [download receipt](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/download_receipt.json), [full PTS binding](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/timestamp_completion_binding.json) and [annotation inventory](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/test2_associated_annotations_inventory.json).

## Reference validation and isolation

Primary reference: `Part2/dataset/Test2_Full/Test2_Full_rally.csv`; SHA256 `33a671408f26f9aba0824d78c1fcc257607782c854bbd0dfd4981dc3cadc2387`. It has **73** rows and the exact seven-column schema:

```text
Start_Frame,End_Frame,Start_Time_sec,End_Time_sec,Duration_sec,Start_Time,End_Time
```

No missing/malformed rows, duplicate/overlapping intervals, ordering errors or out-of-range boundaries were found. Numeric frame/time/duration fields agree at the actual source FPS. Existing zero-origin `[start,end)` benchmark semantics are preserved; no endpoint shift or fitted timing conversion was applied. The final reference end is 29,273, while inference still processed through 29,295. Original files were not modified; byte-exact snapshots and hashes are retained.

Both completed parent/worker receipts and prediction files preceded CSV access. Workers received only the input video, frozen profile and fresh output location; no reference path, count or interval entered inference. All 73 raw live `rally_end` predictions were exported, including nonofficial exchanges. Equal prediction/reference counts are incidental: six unmatched predictions and six misses remain. [Prelabel protocol](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/analysis_protocol.json), [completion-before-label receipt](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/label_access_barrier_receipt.json).

The separate `Test2_Full.csv` contains **75 coarse MM:SS rows**. Its explicit seconds×30 conversion preserves every original row, without offset/rounding/interval fitting. Separate sensitivity results are 67 TP, 6 FP, 8 FN, F1 **0.905405**, mean IoU **0.835561**. These do not replace the primary result, and one-second display precision cannot establish frame-accurate physical boundaries. [Conversion](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/test2_coarse_conversion.json), [separate metrics](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/evaluation_coarse_reference/evaluation_results.json).

## Frozen implementation

Repository root: `/home/administrator/Desktop/sport-analytics/Sports_Analytics`; active branch `Benchmarking`; initial clean HEAD `caa91761948d09f2cfe4937b0db743fff8643a12`. Task changes are research/execution/reporting guards and tests, recorded as dirty source with exact snapshots/hashes. No numerical badminton implementation or model was changed for Test2.

The selected current reference is the validated experimental association-and-scene profile, superseding the older Test1 selection as this run's predeclared reference: `rally-evidence-tracklets-v1`, reconstruction=false, motion_guard=false, exit_recovery=true, curve_exit=false, flight region `vertical_columns_to_image_top_v1`; plus `coobserved-static-hypotheses-v1`, `contact-evidence-v1` spatial_sigma_px=0.7216878364870323 and `foreground-content-continuity-v1` barrier_hypothesis_v1. Numerical YAML matches the frozen latest Test1 run; only passive diagnostic ranges differ. All 65 recorded badminton source files and 27/28 engine files match that Test1 run; the sole engine delta concerns LLM budgets. Both use initially unknown format; Test2 inferred singles at frame 96. No profile was promoted to production.

The full YAML, 284 source hashes, model manifests/checkpoints, dependency inventory, exact CLI and dirty-tree state are in [plan](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/plan.json), [configuration](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/exact_pipeline.yaml), [comparability audit](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/comparability_audit.json) and [reproduction](TEST2_REPRODUCTION.md). Full raw coordinates, association candidates/reasons and 489 contiguous cache segments are retained; detailed heatmap/player diagnostics cover 3,600 uniformly selected frames, not every heatmap tensor.

## Detection and boundary results

Unchanged IoU≥0.5 one-to-one evaluator: maximum cardinality, then total IoU, retaining its existing tiny boundary-distance tie term. No evaluator edit or matching relaxation was made. Boundaries/durations/IoUs below condition on the **67 matched pairs**; unmatched intervals have no fabricated boundary errors.

| Metric | Test2 |
|---|---|
| Reference intervals | 73 |
| Predictions | 73 |
| TP / FP / FN | 67 / 6 / 6 |
| Precision | 0.917808 |
| Recall | 0.917808 |
| F1 | 0.917808 |
| Mean IoU | 0.849962 |
| Median IoU | 0.870968 |
| Minimum IoU | 0.504087 |


| Boundary | Statistic | Frames | Seconds |
|---|---|---|---|
| Start | MAE | 24.8657 | 0.8289 |
| Start | RMSE | 41.1691 | 1.3723 |
| Start | Median absolute | 12.0000 | 0.4000 |
| Start | Signed bias | 20.1493 | 0.6716 |
| Start | P90 absolute | 73.0000 | 2.4333 |
| Start | P95 absolute | 83.8000 | 2.7933 |
| End | MAE | 21.6269 | 0.7209 |
| End | RMSE | 48.5529 | 1.6184 |
| End | Median absolute | 10.0000 | 0.3333 |
| End | Signed bias | -8.7612 | -0.2920 |
| End | P90 absolute | 46.2000 | 1.5400 |
| End | P95 absolute | 58.7000 | 1.9567 |
| Duration | MAE | 39.5970 | 1.3199 |
| Duration | RMSE | 68.2768 | 2.2759 |
| Duration | Signed bias | -28.9104 | -0.9637 |


Signed error is prediction minus reference. Duration bias is predicted minus reference duration. The largest matched start error is 167 frames; largest end error is 343 frames. Quantiles use the retained matched errors; raw signed/absolute arrays are exported.

| Tolerance | Start / matched | Start / all reference | End / matched | End / all reference |
|---|---|---|---|---|
| ±1 | 10/67 (14.93%) | 10/73 (13.70%) | 9/67 (13.43%) | 9/73 (12.33%) |
| ±3 | 18/67 (26.87%) | 18/73 (24.66%) | 16/67 (23.88%) | 16/73 (21.92%) |
| ±5 | 23/67 (34.33%) | 23/73 (31.51%) | 24/67 (35.82%) | 24/73 (32.88%) |
| ±10 | 32/67 (47.76%) | 32/73 (43.84%) | 34/67 (50.75%) | 34/73 (46.58%) |
| ±15 | 38/67 (56.72%) | 38/73 (52.05%) | 41/67 (61.19%) | 41/73 (56.16%) |
| ±30 | 49/67 (73.13%) | 49/73 (67.12%) | 54/67 (80.60%) | 54/73 (73.97%) |


| Matched IoU bin (left-inclusive; final includes 1) | Count |
|---|---|
| 0.50–0.60 | 3 |
| 0.60–0.70 | 5 |
| 0.70–0.75 | 4 |
| 0.75–0.80 | 8 |
| 0.80–0.90 | 16 |
| 0.90–0.95 | 13 |
| 0.95–1.00 | 18 |


## Misses, extras and topology

Missed reference IDs: **31, 32, 39, 56, 58, 63**. No prediction overlaps 31,32,56,58,63; 39 has fragments that fail IoU eligibility. No duplicate, overlapping or adjacent predictions were found. Positive-overlap graph candidates are splits G11/G39/G42/G55/G69/G72 and merges P41/P71; overlap alone is not proof of a physical split/merge. Source review distinguishes real continuity loss, boundary spill and reference spans crossing edits.

| Unmatched prediction | Start frame | End frame | Start seconds | End seconds |
|---|---|---|---|---|
| P11 | 3877 | 3936 | 129.2333 | 131.2000 |
| P38 | 13462 | 13533 | 448.7333 | 451.1000 |
| P39 | 13579 | 13718 | 452.6333 | 457.2667 |
| P45 | 15451 | 15609 | 515.0333 | 520.3000 |
| P56 | 20114 | 20175 | 670.4667 | 672.5000 |
| P69 | 27349 | 27649 | 911.6333 | 921.6333 |


All **40** predeclared significant cases (miss/extra, absolute matched boundary error>30 frames, or IoU<0.75) have source-bound evidence packages. [Per-rally CSV](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/evaluation/per_rally_comparison.csv), [metrics/distributions](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/evaluation/supplemental_metrics.json), [interactive exact-PTS replay](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/failure_package/index.html), [failure analysis](TEST2_FAILURE_ANALYSIS.md). No extra was removed because a visual review suggested a reference omission.

## Runtime and components

Physical hardware is two **GTX 1080 Ti** cards, not the inherited profile's RTX 4000 Ada description. Driver 580.178.04 advertises CUDA 13; installed Torch 2.14.1+cu126 uses CUDA 12.6; ORT 1.29.0. TrackNet ran CUDA FP16, checkpoint `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`. RFDETR and RTMPose staged ONNX graphs have FP32 inputs/weights despite requested fp16; runtime/provider receipts and model hashes are retained. No node-level ORT placement profile was enabled; provider lists do not prove every node ran on GPU.

| Measurement | Primary GPU 0 | Repeat GPU 1 |
|---|---|---|
| Worker seconds | 6544.650 | 6332.029 |
| Parent end-to-end seconds | 6554.688 | 6344.421 |
| Worker throughput FPS | 4.4763 | 4.6266 |
| Worker peak RSS bytes | 3105214464 | 3039739904 |
| Sampled worker GPU peak MiB | 3400 | 3400 |
| Perception cache bytes | 120010374 | 120010374 |


OCR accumulated **3805.52s (63.43min)**, the largest measured stage scope. Content/players accumulated 1475.00s, shuttle 429.24s, court 169.69s. Scopes overlap and must not be summed. This explains why full inference, rather than interval comparison, dominated elapsed time. Component initialization including model loading was 8.839s; staged-model copying 1.757s. Both NN runs shared CPU/RAM/storage; source-frame preparation and proxy auditing also ran on CPU. Historical Test1 timings are descriptive, not a controlled performance regression comparison.

All 29,296 frame payloads and all 489 cache files are byte-identical across the two independent NN processes; prediction CSVs and proxies are byte-identical; semantic event comparison has zero differences after runtime-ID normalization. Separate own-cache replay is **diagnostic, not fresh inference**: v2 strictly reproduces all 73 rallies and 812 contacts/strokes across 29,296 ordered steps. Failed v1 is preserved. [Reproducibility](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/full_reproducibility.json), [resources](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/resources_primary/resource_measurements.json), [component validation](TEST2_COMPONENT_VALIDATION.md).

## Corrections, tests and disposition

Generalized the formerly Test7-specific execution/replay path without weakening frame/source/model/cache protections. Fixed a missing parent report-digest check and a replay-only provenance substitution that made strict baseline comparison fail. Replayed format decisions now preserve their original validated provenance, with their replay origin explicitly declared. The comparator and numerical pipeline remain unchanged. Updated one stale controlled fixture to include required `production_upload` kind; failed logs are retained.

Final research+benchmark scope: **637 passed in 8.62s**. Relevant focused red/green controls, failed replay v1, strict-parity replay v2 and test logs remain in the experiment directory. Historical integrity: **7,264/7,264** files and 2,867,743,793 bytes unchanged. Original Test1 artifacts, annotations and models were not overwritten. Main application code was unchanged; prior release suite counts are not claimed as new tests here.

Demonstrated: complete-input execution, exact timestamp mapping, deterministic neural reproduction and stronger provenance guards. Not demonstrated: new physical/model accuracy improvements, broad generalization or production readiness. Unresolved: short-exchange maturity, long-flight continuity, scene false/missed barriers, pickup/contact confusion, OCR/identity/official-play evidence, and independent annotation quality. Test2 is exposed diagnostic/development-validation material; no numerical threshold was tuned to its labels and no eligible prospective blind recording was identified. See [cross-video comparison](TEST1_TEST2_COMPARISON.md), [failure analysis](TEST2_FAILURE_ANALYSIS.md) and [reproduction](TEST2_REPRODUCTION.md).

## Exportable distributions

![Boundary errors, matched IoUs and both tolerance denominators](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/evaluation/evaluation_distributions.png)

[Standalone SVG](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/evaluation/evaluation_distributions.svg), [primary resource timeline](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/resources_primary/resource_timeline.png). These are legacy-reference distributions, not certified physical timing accuracy.

## Standalone OCR execution-placement diagnostic

The full-video workers did not collect node profiles. A separate post-run diagnostic used the actual Test2 proxy frame 22,924 (exact source PTS), its cold top-left production search crop and the same verified OCR models/settings on physical GPU 1. Only process-local ORT profiling was enabled; original inference outputs and provider/model configuration remained unchanged.

| OCR stage | Executed unique CUDA nodes | Executed unique CPU nodes |
|---|---|---|
| det | 190 | 0 |
| cls | 179 | 0 |
| rec | 181 | 2 |

The two recognition CPU nodes are structural Concat/Slice operations. All profiled kernel events identify their provider; observed tensor types include float and structural int64. This sample demonstrates actual CUDA execution, despite the logged plugin-device warnings; it does not establish full-run placement or accumulator/hardware precision.

Profiled calls took 10122.24 ms cold and 8029.15 ms for one warm call; loading took 0.888 s. These two instrumented calls are not a steady-state benchmark or a controlled comparison with full-video runtime. Raw recognized text includes athlete names, but the unchanged row parser selects SXFI/LIVE branding as score labels: a retained layout/parser ambiguity, not valid sporting-score evidence. No logo blacklist, provider adjustment or parser tuning was introduced. [Raw profiles and report](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/ort_ocr_node_probe_v1/report.json), [source/model verification](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/ort_ocr_node_probe_v1/verification.json).
