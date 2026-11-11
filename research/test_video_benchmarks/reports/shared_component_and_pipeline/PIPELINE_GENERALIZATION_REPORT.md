# Pipeline generalization report

**Final scope clarification:** the user requested Video2 only. Completed additional local-video checks are preserved as incidental historical context. The extra amateur run was interrupted and is not a completed benchmark. No further video inference is running. The additional Video2 repeat was not performed: preparation timed out during its300second FFprobe count before a new plan or NN run was created. The original full fresh Video2 run, independent completion proof, unchanged evaluation and failure analysis are complete. Nothing was deleted.

Fresh Test1 preserves every frozen matched-profile prediction boundary and every evaluation metric. Fresh Test2 recovers one legacy-reference match and adds two predictions: recall rises, precision falls, F1 changes slightly, and mean IoU decreases. This supports specific technical corrections and a measured segmentation tradeoff; it does not establish broad sporting generalization or justify production promotion.

All Test1/Test2 results here measure agreement with unchanged legacy references. Both recordings are exposed development/validation material. The original Test2 CSV is not certified independent physical ground truth. No rally reference, target count or manual interval entered inference. No unmatched prediction was removed.

## Producer integrity and reporting failure

The original Test1/Test2 neural runs completed all17,268/29,296 frames and committed analysed sessions, live events, predictions and perception caches. Their original workers then failed while publishing the completion catalogue because its allowlist still accepted only codec20 after the pipeline emitted21. Both failed receipts and all original outputs remain preserved. Independent, explicit posthoc completion proofs verify the complete cache population, committed session/event ledgers, exact production CSV export, source/model/configuration hashes, full rational source/proxy PTS and source-bound scene probe pixels. They create no inference.json, predictions, neural observations or substitute success status for the failed workers.

The benchmark catalogue has since been corrected and tested for strict21 decoding and exact historical20 compatibility. Subsequent India/doubles fresh workers exited successfully with complete catalogues. Lost Test1/Test2 worker-only initialization, final CPU and NN-only elapsed fields remain unavailable; external PID samples and failure-inclusive parent times are reported separately. See the [Test1 proof](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/completion_test1_v1/REPORT.md), [Test2 proof](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/completion_test2_v1/REPORT.md), [implementation](PIPELINE_REPAIR_IMPLEMENTATION_REPORT.md) and [performance](PIPELINE_PERFORMANCE_REPORT.md).

## Fresh per-video legacy-reference agreement

Matching is unchanged: IoU≥0.5; maximum cardinality, then total IoU with the existing boundary-distance tie-break. Frames are zero-origin and exported intervals half-open. The seven-column CSV contract is unchanged.

| Metric | Test1 | Test2 |
|---|---:|---:|
| GT rally count | 36 | 73 |
| Predicted rally count | 36 | 75 |
| TP | 36 | 68 |
| FP | 0 | 7 |
| FN | 0 | 5 |
| Precision | 100.0000% | 90.6667% |
| Recall | 100.0000% | 93.1507% |
| F1 | 100.0000% | 91.8919% |
| Mean IoU | 0.871026 | 0.848135 |
| Median IoU | 0.919257 | 0.881085 |
| Minimum IoU | 0.538071 | 0.504087 |
| Start MAE (s) | 0.941667 | 0.796078 |
| End MAE (s) | 0.349074 | 0.705392 |
| Duration MAE (s) | 1.111111 | 1.302451 |
| Observed frames/parent wall-second |8.476242|8.040606|
| Parent elapsed, including failed finalization (s) |2037.223530|3643.506591|
| Sampled process-tree peak RSS (bytes) |3,068,030,976|3,052,724,224|
| Sampled worker-tree GPU memory (MiB) |2126|2122|

Throughput uses the complete frame population divided by each original failed parent duration. It is not pure neural latency. Two physical GTX1080Ti devices were used; jobs shared CPU/RAM and overlapped for part of the run. Resolution, source content, duration, OCR availability and concurrency affect performance. Historical worker timings have a different scope; the performance report retains both increases and decreases without a controlled end-to-end speed claim.

Complete per-rally rows, IoU/error distributions, start/end RMSE, median, signed bias, P90/P95, duration errors, topology and unmatched cases are in [Test1 evaluation](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/evaluation_test1_v1/supplemental_metrics.json) and [Test2 evaluation](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/evaluation_test2_v1/supplemental_metrics.json). Unmatched intervals receive no artificial boundary errors.

| Tolerance | Test1 start matched/all-ref | Test1 end matched/all-ref | Test2 start matched/all-ref | Test2 end matched/all-ref |
|---|---:|---:|---:|---:|
|±1 frames|2.78% / 2.78% (1)|11.11% / 11.11% (4)|14.71% / 13.70% (10)|13.24% / 12.33% (9)|
|±3 frames|16.67% / 16.67% (6)|25.00% / 25.00% (9)|26.47% / 24.66% (18)|22.06% / 20.55% (15)|
|±5 frames|33.33% / 33.33% (12)|47.22% / 47.22% (17)|35.29% / 32.88% (24)|35.29% / 32.88% (24)|
|±10 frames|47.22% / 47.22% (17)|63.89% / 63.89% (23)|48.53% / 45.21% (33)|50.00% / 46.58% (34)|
|±15 frames|47.22% / 47.22% (17)|72.22% / 72.22% (26)|58.82% / 54.79% (40)|61.76% / 57.53% (42)|
|±30 frames|69.44% / 69.44% (25)|94.44% / 94.44% (34)|76.47% / 71.23% (52)|82.35% / 76.71% (56)|

Test1 denominators are36matched/36references; Test2 denominators are68matched/73references. The count in parentheses is the shared number within tolerance. Starts and ends use independent errors. See the [exportable PNG](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/rally_plots_v1/cross_video_boundaries.png) and [SVG](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/rally_plots_v1/cross_video_boundaries.svg).

## Frozen baseline comparison

| Test2 metric | Frozen | Fresh repair |
|---|---:|---:|
| Predictions |73|75|
| TP / FP / FN |67 /6 /6|68 /7 /5|
| Precision |91.7808%|90.6667%|
| Recall |91.7808%|93.1507%|
| F1 |91.7808%|91.8919%|
| Mean IoU |0.849962|0.848135|
| Start MAE (s) |0.828856|0.796078|
| End MAE (s) |0.720896|0.705392|
| Duration MAE (s) |1.319900|1.302451|

Fresh Test1 exactly equals the latest frozen matched-profile baseline, including all per-rally comparison rows; the older historical Test1 profile is kept separately. [The explicit regression receipt](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/test1_frozen_regression_verification_v2.json) binds full replay coverage and equality. Own-source diagnostic replay reproduces the complete fresh event output for both videos; it is not another neural inference run.

Test2 newly matches GT32. GT31/39/56/58/63 remain unmatched. A new short prediction[11715,11751) remains unmatched; all six former unmatched prediction intervals remain and are not suppressed. Two new short admissions retain disjoint observed shuttle motion and simultaneous opposite-court episode witnesses, with no named identity or physical-impact certainty manufactured. The legacy boundary/coverage ambiguity for several intervals remains unresolved.

For the same67previously matched references, mean IoU changes0.849962→0.851146, start MAE0.828856→0.801493s, and end MAE0.720896→0.707960s. This [fixed-cohort diagnostic](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/test2_common_matched_cohort_v1.json) separates boundary changes from the additional weak match; the primary mean IoU above always retains all68matches. The full failure review and source packages retain difficult gaps, retrieval, preparation and edits rather than adjusting the reference or extending intervals to improve scores.

## Aggregation and generalization limits

The current two-video macro precision/recall/F1 are95.3333%/96.5753%/95.9459%; macro mean IoU is0.859580. Micro counts are109references,111predictions,104TP,7FP and5FN: precision93.6937%, recall95.4128%, F1 94.5455%. The frozen micro F1 was94.4954%. Matched errors are weighted by matched count; macro values give each recording equal weight. [All aggregate statistics and both tolerance denominators](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/cross_video_aggregate_v1.json) remain machine-readable.

Persistent shared patterns include weak launch observations, reference boundaries during preparation/retrieval, anonymous identity, estimated contacts and unreviewed shot labels. Test2 additionally exposes short exchanges, G39/G55/G69 flight/association gaps, a missed one-person same-camera edit11346 and more scene/scoreboard integration. Removing false resets7703/23639 and branding ownership errors improves the evidence chain; neither correction certifies physical rally boundaries, identity, hits, shot classes or scores.

Physical sporting accuracy for shuttle localization, court registration, contact timing, hitter attribution, tracking identity, pose and OCR remains unvalidated without independent reviewed component labels. No HOTA/IDF1/PCK/AP/shot macro-F1 was manufactured from rally rows. Source-level visual review identifies plausible causes and uncertainty; it is not certified human adjudication.

## Additional video execution

The full Test7 original completed fresh inference successfully, including all10,725frames, a catalogue published before success and exact own-source semantic replay. Its full source/proxy rationalPTS match, and all13scene-probe pixel hashes match actual decoded images. The extra amateur canonical-input run was later interrupted under the Video2-only scope clarification. India4800frames and doubles3600frames completed fresh inference successfully; Denmark3300frames completed before scope clarification; its results are incidental technical context. These three prepared clips are contiguous diagnostics, not completed full original matches. Their published contact alignment is agent-draft and is not an independent component accuracy oracle.

The amateur original is VFR; this experiment uses its existing30FPS canonical proxy as the input. Exact original-to-proxy frame mapping has not been certified. Native VFR/source-frame accuracy is not claimed, and the full-upload benchmark correctly rejects unsupported unmapped rate conversion. Other Part2 references have no locally available matching originals. No prospective independent match was identified; remaining untouched matches should be reserved for a future prespecified validation after annotation and media binding.

No further benchmark results are awaited under the clarified scope. The production default is unchanged; this experimental profile is not promoted.

## Test7 unchanged-reference validation

The original31-row coarse reference remains primary for historical comparability. Exact Fraction(seconds)×actualFPS conversion reproduces the archived seven-column reference byte for byte, with no offset, rounding, endpoint change or row removal. [Original-reference binding](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/test7_reference_validation_v1/binding.json). The separate30-row fine legacy CSV is sensitivity only.

| Test7 metric | Frozen coarse | Fresh coarse | Fresh fine sensitivity |
|---|---:|---:|---:|
| References / predictions |31 /32|31 /32|30 /32|
| TP / FP / FN |29 /3 /2|29 /3 /2|28 /4 /2|
| Precision |90.6250%|90.6250%|87.5000%|
| Recall |93.5484%|93.5484%|93.3333%|
| F1 |92.0635%|92.0635%|90.3226%|
| Mean IoU |0.774815|0.779333|0.833985|
| Start MAE (s) |1.128736|1.129885|0.782143|
| End MAE (s) |0.658621|0.629885|0.498810|
| Duration MAE (s) |1.122989|1.095402|1.178571|

[Coarse results](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/evaluation_test7_coarse_v1/supplemental_metrics.json) retain all boundaries, tolerance denominators29matched/31references, topology and20significant cases. [Fine sensitivity](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/evaluation_test7_fine_v1/supplemental_metrics.json) retains28matched/30reference denominators. These reference definitions are not interchangeable sporting truth.

All10725raw shuttle/association/geometry fields equal the frozen Test7 run. Of32intervals,30are identical; row30ends25frames earlier, and row31starts one frame later. Source review supports reducing post-exchange walking in row30, but its precise physical landing is unlabelled. Start MAE rises slightly; detection counts remain unchanged. [Actual source/trace review](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/test7_boundary_source_review_v2/report.json) and [full technical comparison](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/analysis_test7_vs_frozen_v1/technical_analysis.json).

Across Test1/Test2/Test7coarse, micro counts are140references,143predictions,133TP,10FP and7FN. Micro precision93.0070%, recall95.0000%, F1 93.9929%; the frozen micro F1 is93.9502%. [Full macro/micro aggregate](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/cross_video_three_aggregate_v1.json). This descriptive mixture of legacy reference resolutions does not establish physical accuracy or broad deployment generalization.

The additional full Test2 repetition was not performed. Its preparation timed out in the300second FFprobe count; no new NN run was launched. Exact semantic replay is verified for the completed first run, while whole latest-profile NN repetition remains unvalidated.
