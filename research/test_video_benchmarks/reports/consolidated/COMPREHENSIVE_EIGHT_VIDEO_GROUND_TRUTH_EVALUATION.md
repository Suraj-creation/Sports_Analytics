# Comprehensive eight-video evaluation against supplied ground truth

Videos: **Tests 1, 2, 3, 4, 6, 7, 9, 10**. Tests 5 and 8 were excluded at the user’s explicit request. This single document consolidates every primary saved metric, full per-rally frame/time/duration comparisons, every false detection, all supplied coarse outcome rows and their separate timing sensitivity, component coverage, runtime/resource measurements, model/configuration bindings, failure patterns and priorities. No inference, prediction edits, annotation repairs or pipeline fixes were performed for this review.

Primary result: **416 reference intervals,442 predictions,377 TP,65 FP,39 FN; precision 85.294%, recall 90.625%, F1 87.879%; pooled matched mean IoU 0.854244.** The benchmark covers 173,942 decoded frames at 30 FPS (96.634 source minutes).

Numeric scores use fractions on 0–1 unless a percent sign is shown. Displayed decimals are rounded to six places; the source artifacts retain full precision. “—” means unavailable or unmatched, never a substituted zero. All per-rally data needed to compare predictions with each primary reference are included directly below each video.

## Contents

- [Protocol, reference meanings and limits](#protocol-reference-meanings-and-limits)
- [Aggregate scores against ground truth](#aggregate-scores-against-ground-truth)
- [Reference-set sensitivity](#reference-set-sensitivity)
- [Earlier model baselines where available](#earlier-model-baselines-where-available)
- [Test1: full metrics and every GT rally](#test-1-complete-evaluation-and-ground-truth-comparison)
- [Test2: full metrics and every GT rally](#test-2-complete-evaluation-and-ground-truth-comparison)
- [Test3: full metrics and every GT rally](#test-3-complete-evaluation-and-ground-truth-comparison)
- [Test4: full metrics and every GT rally](#test-4-complete-evaluation-and-ground-truth-comparison)
- [Test6: full metrics and every GT rally](#test-6-complete-evaluation-and-ground-truth-comparison)
- [Test7: full metrics and every GT rally](#test-7-complete-evaluation-and-ground-truth-comparison)
- [Test9: full metrics and every GT rally](#test-9-complete-evaluation-and-ground-truth-comparison)
- [Test10: full metrics and every GT rally](#test-10-complete-evaluation-and-ground-truth-comparison)
- [Recurring failures, generalisation and priorities](#recurring-failures-generalisation-and-priorities)
- [Model, configuration and audit appendix](#model-configuration-and-audit-appendix)

## Protocol, reference meanings and limits

| Reference/baseline | How this report uses it | What it does not establish |
|---|---|---|
| Primary timing benchmark | `Part2/dataset/TestN_Full/TestN_Full_rally.csv`; exact seven-column zero-origin frame/time table; original saved evaluations recomputed against it | These legacy/generated rally tables are supplied benchmark references, not independently adjudicated physical truth |
| Secondary coarse/outcome reference | `TestN_Full.csv`; supplied minute:second spans, winner/reason/ball_types/score fields;425 nonblank rows across eight videos | Not the same row population or frame-accurate boundary definition as the416-row primary benchmark; not exhaustive contact/shot GT |
| GT self-comparison ideal | Identical intervals imply TP=N,FP=FN=0,P=R=F1=IoU=1 and all timing errors0 | Not an earlier model run, and not proof of perception/contact/scoring accuracy |
| Historical model baseline | Actual older saved model outputs are compared for Tests1 and2 only, with the same primary labels/matcher | No earlier equivalent model benchmark was found/claimed for Tests 3, 4, 6, 7, 9, 10 |
| Auxiliary annotations | Trajectory/player/T4/win_predictions/court files catalogued with row counts/schemas/hashes | Generated or insufficiently reviewed evidence is not silently promoted to independently labelled accuracy |

Primary matcher: temporal IoU≥0.5; one-to-one maximum-cardinality assignment, then maximum total IoU with the unchanged tiny boundary-distance tie breaker. Intervals are half-open `[start,end)`, duration=end−start, with no inclusive-frame addition. Frame0 corresponds to time0; all comparisons retain 30 FPS and original offset, with no fitted timestamp shift. Precision=TP/(TP+FP), recall=TP/(TP+FN), F1=2TP/(2TP+FP+FN). TP means an eligible matched interval, not that every physical boundary/contact is correct. All saved primary values and CSV cells were independently recomputed with this unchanged evaluator.

The entire effective numerical profile is identical across all eight records after removing only input-length-dependent passive diagnostic ranges. All eight actual model-identity sets are identical. Historical Tests 1/2 retain original failed catalogue-publication receipts and independently verified complete inference/cache/event/PTS proofs; they are not relabelled as ordinary successful workers. The pre-existing later catalogue allowlist fix precedes Tests3+. Test 10’s original frame-count attempt timed out after 300 seconds; the separate retry extended only that deadline to 1800 seconds and completed the same counting command in 340.145571 seconds. No inference component, model, numerical threshold or evaluator changed for that retry.

Frame-level shuttle coordinates, contacts, hitter identity, exhaustive stroke classes, physical winner/point decisions and score-sequence accuracy cannot be certified from rally-level timing CSVs. Supplied coarse winner/score fields exist, but mapping anonymous tracks/observed OCR rows to independently reviewed Player A/B identities and official point transitions is not established. These semantic accuracy fields remain unavailable; measured output/abstention coverage is reported separately.

## Aggregate scores against ground truth

| Test | GT rallies | Predictions | TP | FP | FN | Precision | Recall | F1 | Mean IoU | Start MAE f | End MAE f | Duration MAE s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 36 | 36 | 36 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 | 0.871026 | 28.250000 | 10.472222 | 1.111111 |
| 2 | 73 | 75 | 68 | 7 | 5 | 0.906667 | 0.931507 | 0.918919 | 0.848135 | 23.882353 | 21.161765 | 1.302451 |
| 3 | 19 | 24 | 18 | 6 | 1 | 0.750000 | 0.947368 | 0.837209 | 0.895795 | 28.611111 | 8.500000 | 0.992593 |
| 4 | 41 | 46 | 38 | 8 | 3 | 0.826087 | 0.926829 | 0.873563 | 0.821815 | 31.289474 | 26.842105 | 1.532456 |
| 6 | 42 | 47 | 35 | 12 | 7 | 0.744681 | 0.833333 | 0.786517 | 0.884584 | 23.485714 | 20.571429 | 1.350476 |
| 7 | 30 | 32 | 28 | 4 | 2 | 0.875000 | 0.933333 | 0.903226 | 0.833985 | 23.464286 | 14.964286 | 1.178571 |
| 9 | 82 | 84 | 69 | 15 | 13 | 0.821429 | 0.841463 | 0.831325 | 0.862791 | 22.869565 | 18.884058 | 1.250725 |
| 10 | 93 | 98 | 85 | 13 | 8 | 0.867347 | 0.913978 | 0.890052 | 0.844965 | 23.988235 | 18.058824 | 1.227451 |

| Pooled detection metric | GT ideal | Observed | Difference |
|---|---|---|---|
| ground_truth_count | 416 | 416 | 0 |
| predicted_count | 416 | 442 | 26 |
| true_positives | 416 | 377 | -39 |
| false_positives | 0 | 65 | 65 |
| false_negatives | 0 | 39 | 39 |
| precision | 1 | 0.852941 | -0.147059 |
| recall | 1 | 0.906250 | -0.093750 |
| f1 | 1 | 0.878788 | -0.121212 |

| Macro per-video metric | GT ideal | Observed |
|---|---|---|
| precision | 1 | 0.848901 |
| recall | 1 | 0.915977 |
| f1 | 1 | 0.880101 |
| mean_iou | 1 | 0.857887 |
| median_iou | 1 | 0.896121 |
| minimum_iou | 1 | 0.530311 |
| start_frame_mae | 0 | 25.730092 |
| end_frame_mae | 0 | 17.431836 |
| start_time_sec_mae | 0 | 0.857670 |
| end_time_sec_mae | 0 | 0.581061 |
| duration_sec_mae | 0 | 1.243229 |

| Macro boundary metric / units | Mean per-video MAE | Mean per-video RMSE | Mean per-video median absolute | Mean per-video signed bias | Mean per-video P90 absolute |
|---|---|---|---|---|---|
| start_frame | 25.730092 | 48.571565 | 11.000000 | 19.691549 | 62.075000 |
| end_frame | 17.431836 | 33.416482 | 8.500000 | -7.687576 | 36.012500 |
| start_time_sec | 0.857670 | 1.619052 | 0.366667 | 0.656385 | 2.069167 |
| end_time_sec | 0.581061 | 1.113883 | 0.283333 | -0.256253 | 1.200417 |
| duration_sec | 1.243229 | 2.115025 | 0.614583 | -0.912637 | 2.932500 |

Micro values pool event counts; macro values weight each video equally. The macro “median_iou” is the mean of per-video medians, not the median over all matched intervals. Exact pooled medians and quantiles appear in the distribution table below. No true-negative count or standard classification accuracy is claimed for rally events because the universe of non-rally events is undefined.

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 25.042440 | 8.000000 | 48.408765 | 286.000000 | 71.000000 | 17.222812 | 7.000000 |
| end_frame | 18.477454 | 9.000000 | 38.668077 | 343.000000 | 40.200000 | -8.408488 | -2.000000 |
| start_time_sec | 0.834748 | 0.266667 | 1.613625 | 9.533333 | 2.366667 | 0.574094 | 0.233333 |
| end_time_sec | 0.615915 | 0.300000 | 1.288936 | 11.433333 | 1.340000 | -0.280283 | -0.066667 |
| duration_sec | 1.261450 | 0.633333 | 2.150160 | 12.700000 | 3.073333 | -0.854377 | -0.500000 |

| Exact pooled distribution | N | Mean | Median | Minimum | Maximum | P90 | P95 |
|---|---|---|---|---|---|---|---|
| matched_iou | 377 | 0.854244 | 0.901345 | 0.504087 | 0.997506 | 0.975738 | 0.985565 |
| start_signed_frames | 377 | 17.222812 | 7.000000 | -286.000000 | 233.000000 | 59.800000 | 89.400000 |
| start_absolute_frames | 377 | 25.042440 | 8.000000 | 0.000000 | 286.000000 | 71.000000 | 100.000000 |
| end_signed_frames | 377 | -8.408488 | -2.000000 | -343.000000 | 184.000000 | 16.000000 | 21.200000 |
| end_absolute_frames | 377 | 18.477454 | 9.000000 | 0.000000 | 343.000000 | 40.200000 | 62.000000 |
| duration_signed_frames | 377 | -25.631300 | -15.000000 | -381.000000 | 271.000000 | 12.000000 | 27.400000 |
| duration_absolute_frames | 377 | 37.843501 | 19.000000 | 0.000000 | 381.000000 | 92.200000 | 152.000000 |
| duration_signed_seconds | 377 | -0.854377 | -0.500000 | -12.700000 | 9.033333 | 0.400000 | 0.913333 |

| Boundary | ±frames | Within | Matched denominator | Pooled matched success | All-GT denominator | Pooled all-GT success | Macro matched success | Macro all-GT success |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 37 | 377 | 9.814% | 416 | 8.894% | 9.518% | 8.548% |
| start | 3 | 77 | 377 | 20.424% | 416 | 18.510% | 21.894% | 20.039% |
| start | 5 | 138 | 377 | 36.605% | 416 | 33.173% | 36.351% | 33.115% |
| start | 10 | 216 | 377 | 57.294% | 416 | 51.923% | 56.254% | 51.342% |
| start | 15 | 243 | 377 | 64.456% | 416 | 58.413% | 62.819% | 57.346% |
| start | 30 | 292 | 377 | 77.454% | 416 | 70.192% | 76.335% | 69.821% |
| end | 1 | 46 | 377 | 12.202% | 416 | 11.058% | 11.709% | 10.655% |
| end | 3 | 84 | 377 | 22.281% | 416 | 20.192% | 22.274% | 20.299% |
| end | 5 | 144 | 377 | 38.196% | 416 | 34.615% | 39.914% | 36.617% |
| end | 10 | 205 | 377 | 54.377% | 416 | 49.279% | 55.080% | 50.573% |
| end | 15 | 253 | 377 | 67.109% | 416 | 60.817% | 68.079% | 62.361% |
| end | 30 | 326 | 377 | 86.472% | 416 | 78.365% | 88.198% | 80.893% |

| Pooled boundary/error inventory | Count | Interpretation |
|---|---|---|
| early_start_gt_ids | 36 | Only matched GT intervals; categories may overlap |
| late_start_gt_ids | 333 | Only matched GT intervals; categories may overlap |
| premature_end_gt_ids | 224 | Only matched GT intervals; categories may overlap |
| late_end_gt_ids | 138 | Only matched GT intervals; categories may overlap |
| weak_iou_gt_ids | 72 | Only matched GT intervals; categories may overlap |

The mean matched start is **0.574094s late**, mean end **-0.280283s** relative to GT, and duration bias **-0.854377s**. Thus high detection F1 coexists with systematic shortening and imperfect boundary timing. Even Test1’s100% rally-detection F1 does not imply exact timing: its start MAE is28.25frames and duration MAE1.111111seconds.

### Duration-conditioned rally recall: descriptive analysis

| GT duration bin | GT count | Matched TP | Missed FN | Recall | Matched start MAE f | Matched end MAE f |
|---|---|---|---|---|---|---|
| ≤2 s | 7 | 5 | 2 | 0.714286 | 13.200000 | 12.400000 |
| (2,5] s | 94 | 80 | 14 | 0.851064 | 9.887500 | 12.687500 |
| (5,10] s | 147 | 133 | 14 | 0.904762 | 20.443609 | 13.180451 |
| (10,20] s | 129 | 125 | 4 | 0.968992 | 36.416000 | 21.864000 |
| >20 s | 39 | 34 | 5 | 0.871795 | 38.617647 | 41.264706 |

Duration bins are an offline descriptive breakdown of the unchanged primary matching results, not tuned detection thresholds. They may reveal which rally lengths need review but do not establish causal component accuracy or hold-out performance.

### Frame occupancy agreement: separate timeline diagnostic

| Test | GT-active∩pred-active frames | Pred-only frames | GT-only frames | Both-inactive frames | Frame precision | Frame recall | Frame F1 | Timeline IoU |
|---|---|---|---|---|---|---|---|---|
| 1 | 11453 | 217 | 1167 | 4431 | 0.981405 | 0.907528 | 0.943022 | 0.892187 |
| 2 | 19169 | 728 | 2523 | 6876 | 0.963412 | 0.883690 | 0.921830 | 0.854996 |
| 3 | 6099 | 80 | 316 | 1919 | 0.987053 | 0.950740 | 0.968556 | 0.939030 |
| 4 | 11843 | 736 | 1702 | 5753 | 0.941490 | 0.874345 | 0.906676 | 0.829284 |
| 6 | 14091 | 248 | 1510 | 2066 | 0.982705 | 0.903211 | 0.941283 | 0.889078 |
| 7 | 6167 | 103 | 958 | 3497 | 0.983573 | 0.865544 | 0.920791 | 0.853210 |
| 9 | 20714 | 496 | 2334 | 9613 | 0.976615 | 0.898733 | 0.936057 | 0.879800 |
| 10 | 24254 | 902 | 3080 | 8897 | 0.964144 | 0.887320 | 0.924138 | 0.858974 |
| Pooled | 113790 | 3510 | 13590 | 43052 | 0.970077 | 0.893311 | 0.930113 | 0.869356 |

This newly derived offline diagnostic marks frames inside the supplied GT intervals as reference-active and frames inside predictions as predicted-active. It measures timeline occupancy, not the primary one-to-one rally event matcher. “Both inactive” is relative to these supplied annotations, not independently certified absence of physical play. Overall frame accuracy is intentionally not emphasized because background can dominate it.

## Reference-set sensitivity

| Test | Primary _rally GT rows | Secondary nonblank coarse rows | Blank coarse rows | Primary TP/FP/FN | Secondary TP/FP/FN | Primary F1 | Secondary F1 | ΔF1 percentage points |
|---|---|---|---|---|---|---|---|---|
| 1 | 36 | 36 | 0 | 36/0/0 | 36/0/0 | 1.000000 | 1.000000 | 0.000000 |
| 2 | 73 | 75 | 0 | 68/7/5 | 69/6/6 | 0.918919 | 0.920000 | 0.108108 |
| 3 | 19 | 22 | 0 | 18/6/1 | 22/2/0 | 0.837209 | 0.956522 | 11.931244 |
| 4 | 41 | 45 | 0 | 38/8/3 | 42/4/3 | 0.873563 | 0.923077 | 4.951370 |
| 6 | 42 | 42 | 0 | 35/12/7 | 39/8/3 | 0.786517 | 0.876404 | 8.988764 |
| 7 | 30 | 31 | 0 | 28/4/2 | 29/3/2 | 0.903226 | 0.920635 | 1.740911 |
| 9 | 82 | 78 | 10 | 69/15/13 | 71/13/7 | 0.831325 | 0.876543 | 4.521791 |
| 10 | 93 | 96 | 5 | 85/13/8 | 89/9/7 | 0.890052 | 0.917526 | 2.747342 |

| Reference family | GT | Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|
| Primary frame-accurate timing reference | 416 | 442 | 377 | 65 | 39 | 0.852941 | 0.906250 | 0.878788 |
| Secondary coarse time/outcome reference | 425 | 442 | 397 | 45 | 28 | 0.898190 | 0.934118 | 0.915802 |

The primary result remains377/65/39 against416 reference intervals. The secondary result uses425 nonblank intervals, the exact same442 predictions and unchanged IoU0.5 matcher. Its different score is a consequence of different supplied reference counts/boundaries, not a new pipeline improvement. Test3 is especially sensitive: its19-row primary versus22-row coarse reference changes F1 from83.721% to95.652%. Neither table is silently substituted for the other or declared physically authoritative. Coarse rows 79–88 in Test9 and 97–101 in Test10 are entirely blank, explicitly recorded and excluded only from the secondary positive-interval list. No nonblank interval is discarded.

## Earlier model baselines where available

### Test1: Original frozen Test1 benchmark versus selected improved run

| Metric | Earlier saved model baseline | Selected improved evaluation | Improved minus baseline |
|---|---|---|---|
| predictions | 49 | 36 | -13 |
| ground_truth_count | 36 | 36 | 0 |
| true_positives | 30 | 36 | 6 |
| false_positives | 19 | 0 | -19 |
| false_negatives | 6 | 0 | -6 |
| precision | 0.612245 | 1.000000 | 0.387755 |
| recall | 0.833333 | 1.000000 | 0.166667 |
| f1 | 0.705882 | 1.000000 | 0.294118 |
| mean_iou | 0.763315 | 0.871026 | 0.107711 |
| start_frame_mae | 49.433333 | 28.250000 | -21.183333 |
| end_frame_mae | 40.400000 | 10.472222 | -29.927778 |
| start_time_sec_mae | 1.647778 | 0.941667 | -0.706111 |
| end_time_sec_mae | 1.346667 | 0.349074 | -0.997593 |
| duration_sec_mae | 2.845556 | 1.111111 | -1.734444 |

Baseline evidence: [metrics](/home/administrator/Desktop/sport-analytics/Sports_Analytics/outputs/benchmarking/test1/metrics.json) and [predictions](/home/administrator/Desktop/sport-analytics/Sports_Analytics/outputs/benchmarking/test1/predicted_rallies.csv); independently recomputed against the same primary GT. This is a historical developmental comparison, not a prospective controlled experiment or a proof of generalisation. Matching denominators can change; matched IoU/error deltas reflect different matched populations.

### Test2: Earlier full fresh Test2 primary versus selected improved run

| Metric | Earlier saved model baseline | Selected improved evaluation | Improved minus baseline |
|---|---|---|---|
| predictions | 73 | 75 | 2 |
| ground_truth_count | 73 | 73 | 0 |
| true_positives | 67 | 68 | 1 |
| false_positives | 6 | 7 | 1 |
| false_negatives | 6 | 5 | -1 |
| precision | 0.917808 | 0.906667 | -0.011142 |
| recall | 0.917808 | 0.931507 | 0.013699 |
| f1 | 0.917808 | 0.918919 | 0.001111 |
| mean_iou | 0.849962 | 0.848135 | -0.001828 |
| start_frame_mae | 24.865672 | 23.882353 | -0.983319 |
| end_frame_mae | 21.626866 | 21.161765 | -0.465101 |
| start_time_sec_mae | 0.828856 | 0.796078 | -0.032777 |
| end_time_sec_mae | 0.720896 | 0.705392 | -0.015503 |
| duration_sec_mae | 1.319900 | 1.302451 | -0.017450 |

Baseline evidence: [metrics](/home/administrator/Desktop/sport-analytics/Sports_Analytics/artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/evaluation/evaluation_results.json) and [predictions](/home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1/predicted_rallies.csv); independently recomputed against the same primary GT. This is a historical developmental comparison, not a prospective controlled experiment or a proof of generalisation. Matching denominators can change; matched IoU/error deltas reflect different matched populations.

No older equivalent model baseline is invented for Tests 3, 4, 6, 7, 9, 10. Their sections compare directly with supplied ground truth and its identical-boundary ideal. The saved primary Test2 change includes one extra TP and one extra FP, while overall mean matched IoU slightly decreases; the report preserves those tradeoffs rather than reporting only F1 improvement.

## Test 1: complete evaluation and ground-truth comparison

Reference **36 rallies**, predictions **36**; TP/FP/FN **36/0/0**. Precision **100.000%**, recall **100.000%**, F1 **100.000%**. Matched mean IoU **0.871026**. The ground-truth benchmark for every table in this primary section is [Test1_Full_rally.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test1_Full/Test1_Full_rally.csv).

| Input / execution binding | Value |
|---|---|
| Decoded frames | 17268 |
| FPS | 30.000000 |
| Video duration seconds | 575.600000 |
| Canonical dimensions | 1280 × 720 |
| Source SHA256 | 877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6 |
| Proxy SHA256 | d352d684fb5399d804b8f50c785a3605346e7f03987ecb1d9a73ef3482535a97 |
| Prediction SHA256 | 097efc9144bedee6cf41a1c1fe7989242ae14aa356b2eb4d44decc1cd04338a8 |
| Ground-truth SHA256 | 30651cf7238924d6a5072b1dd71d34ca5839cd5b842f696e745229033ae4f887 |
| Coarse reference SHA256 | e3466ded0dace3c7df60b237db779de68c7910672ca14218a2ce8cf5f9b45545 |
| Session | UPLOADTEST1 |
| Actual completion mode | independent_recovery |
| Original parent receipt status | partial_or_failed |
| Full source/proxy PTS matches | 17268 |
| Scene probe pixel hashes verified | 13 |
| Verified saved files / logical bytes | 18 / 3191331 |
| Read-only record | [saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test1_historical) |

### Primary metric scores versus the ground-truth ideal

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 36 | 36 | 0 |
| Prediction count | 36 | 36 | 0 |
| TP / matched | 36 | 36 | 0 |
| FP | 0 | 0 | 0 |
| FN / missed | 0 | 0 | 0 |
| precision | 1 | 1.000000 | 0.000000 |
| recall | 1 | 1.000000 | 0.000000 |
| f1 | 1 | 1.000000 | 0.000000 |
| Mean matched IoU | 1 | 0.871026 | -0.128974 |
| Median matched IoU | 1 | 0.919257 | -0.080743 |
| Minimum matched IoU | 1 | 0.538071 | -0.461929 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 83.333333 |
| 0.9 | 100 | 55.555556 |
| 0.95 | 100 | 27.777778 |

A GT self-comparison has TP=N, FP=FN=0, precision/recall/F1=1, IoU=1 and every timing/duration error=0. This is the reference ideal, not a separately executed baseline model. The signed count difference alone is insufficient: false positives and misses can cancel.

### Boundary and duration errors versus zero-error ground truth

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 28.250000 | 20.500000 | 41.174088 | 106.000000 | 69.500000 | 24.194444 | 14.000000 |
| end_frame | 10.472222 | 6.000000 | 14.648663 | 44.000000 | 22.500000 | -2.194444 | -2.500000 |
| start_time_sec | 0.941667 | 0.683333 | 1.372470 | 3.533333 | 2.316667 | 0.806481 | 0.466667 |
| end_time_sec | 0.349074 | 0.200000 | 0.488289 | 1.466667 | 0.750000 | -0.073148 | -0.083333 |
| duration_sec | 1.111111 | 0.633333 | 1.527970 | 4.000000 | 2.700000 | -0.879630 | -0.566667 |

| Additional saved statistic | Value | Ground-truth ideal |
|---|---|---|
| Start P95 \|error\| frames | 89.000000 | 0 |
| End P95 \|error\| frames | 31.250000 | 0 |
| Duration mae frames | 33.333333 | 0 |
| Duration rmse frames | 45.839091 | 0 |
| Duration signed_bias frames | -26.388889 | 0 |

All error statistics above condition on eligible matched rallies. A positive start error is a late start; a negative start error is early. A positive end error is a late end; a negative end error is premature. Duration error is prediction minus GT. All 30 FPS frame errors convert by dividing by30; full signed/absolute per-rally values appear below. Misses have no invented zero error.

### Boundary tolerance scores

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 1 | 36 | 2.778% | 36 | 2.778% | 100% |
| start | 3 | 0.100000 | 6 | 36 | 16.667% | 36 | 16.667% | 100% |
| start | 5 | 0.166667 | 12 | 36 | 33.333% | 36 | 33.333% | 100% |
| start | 10 | 0.333333 | 17 | 36 | 47.222% | 36 | 47.222% | 100% |
| start | 15 | 0.500000 | 17 | 36 | 47.222% | 36 | 47.222% | 100% |
| start | 30 | 1.000000 | 25 | 36 | 69.444% | 36 | 69.444% | 100% |
| end | 1 | 0.033333 | 4 | 36 | 11.111% | 36 | 11.111% | 100% |
| end | 3 | 0.100000 | 9 | 36 | 25.000% | 36 | 25.000% | 100% |
| end | 5 | 0.166667 | 17 | 36 | 47.222% | 36 | 47.222% | 100% |
| end | 10 | 0.333333 | 23 | 36 | 63.889% | 36 | 63.889% | 100% |
| end | 15 | 0.500000 | 26 | 36 | 72.222% | 36 | 72.222% | 100% |
| end | 30 | 1.000000 | 34 | 36 | 94.444% | 36 | 94.444% | 100% |

### All saved error distributions

| Distribution / units | N | Mean | Median | Minimum | Maximum | P90 | P95 | Ideal |
|---|---|---|---|---|---|---|---|---|
| matched_iou | 36 | 0.871026 | 0.919257 | 0.538071 | 0.997506 | 0.974118 | 0.988809 | 1 |
| start_signed_frames | 36 | 24.194444 | 14.000000 | -71.000000 | 106.000000 | 68.000000 | 89.000000 | 0 |
| start_absolute_frames | 36 | 28.250000 | 20.500000 | 1.000000 | 106.000000 | 69.500000 | 89.000000 | 0 |
| end_signed_frames | 36 | -2.194444 | -2.500000 | -35.000000 | 44.000000 | 11.500000 | 22.500000 | 0 |
| end_absolute_frames | 36 | 10.472222 | 6.000000 | 0.000000 | 44.000000 | 22.500000 | 31.250000 | 0 |
| duration_signed_frames | 36 | -26.388889 | -17.000000 | -120.000000 | 77.000000 | 0.500000 | 18.500000 | 0 |
| duration_absolute_frames | 36 | 33.333333 | 19.000000 | 1.000000 | 120.000000 | 81.000000 | 93.750000 | 0 |
| duration_signed_seconds | 36 | -0.879630 | -0.566667 | -4.000000 | 2.566667 | 0.016667 | 0.616667 | 0 |

### Misses, extras, overlap topology and failure review

| Diagnostic | Observed | GT ideal / interpretation |
|---|---|---|
| Missed GT IDs | [] | [] |
| Unmatched prediction IDs | [] | [] |
| No-overlap missed GT IDs | [] | [] |
| Predictions without any GT overlap | [] | [] |
| Possible split GT IDs | [23] | Geometric overlap candidates; not adjudicated semantic splits |
| Possible merge prediction IDs | [22] | Geometric overlap candidates; not adjudicated semantic merges |
| Significant failure records | 14 | Unmatched or \|boundary error\|>30frames or IoU<0.75 |
| early_start_gt_ids | [4,22] | Direction/weak-overlap inventory, not a physical cause |
| late_start_gt_ids | [1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,24,25,26,27,28,29,30,31,32,33,34,35,36] | Direction/weak-overlap inventory, not a physical cause |
| premature_end_gt_ids | [2,3,5,6,9,10,11,14,15,17,18,19,20,21,26,27,28,29,30,32,34,36] | Direction/weak-overlap inventory, not a physical cause |
| late_end_gt_ids | [1,4,8,12,13,16,22,23,24,25,31,33,35] | Direction/weak-overlap inventory, not a physical cause |
| weak_iou_gt_ids | [5,8,9,11,14,15] | Direction/weak-overlap inventory, not a physical cause |

| Inventory validity | Ground truth | Predictions |
|---|---|---|
| count | 36 | 36 |
| duplicate_row_pairs | [] | [] |
| positive_overlap_row_pairs | [] | [] |
| adjacent_row_pairs | [] | [] |
| out_of_range_rows | [] | [] |
| out_of_order_rows | [] | [] |

| Largest matched boundary cases | P ID | GT start/end frames | Pred start/end frames | Δstart frames | Δend frames | IoU |
|---|---|---|---|---|---|---|
| 9 | 9 | 3751–4073 | 3857–4059 | 106 | -14 | 0.627329 |
| 5 | 5 | 2210–2500 | 2308–2496 | 98 | -4 | 0.648276 |
| 15 | 15 | 6716–6913 | 6802–6908 | 86 | -5 | 0.538071 |
| 4 | 4 | 1874–2161 | 1803–2167 | -71 | 6 | 0.788462 |
| 8 | 8 | 3451–3695 | 3519–3699 | 68 | 4 | 0.709677 |

Of 0 unmatched reference intervals, 0 have no positive overlap with any prediction; 0 have some overlap but fail the one-to-one IoU eligibility/assignment. This separates absence of overlap from insufficient interval agreement without inventing a causal diagnosis.

### Every GT rally compared directly with its assigned prediction: frames

G IDs are one-based CSV row IDs in the primary rally reference. P IDs are one-based rows in the preserved prediction CSV. C IDs refer to the separate coarse table, linked only by the same IoU-based temporal crosswalk. “—” denotes unavailable/unmatched, not zero.

| G | P | GT start f | GT end f | Pred start f | Pred end f | Δstart f | \|Δstart\| f | Δend f | \|Δend\| f | IoU | Status | Coarse C row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 243 | 715 | 264 | 717 | 21 | 21 | 2 | 2 | 0.951477 | matched | 1 |
| 2 | 2 | 887 | 1262 | 890 | 1255 | 3 | 3 | -7 | 7 | 0.973333 | matched | 2 |
| 3 | 3 | 1398 | 1664 | 1402 | 1659 | 4 | 4 | -5 | 5 | 0.966165 | matched | 3 |
| 4 | 4 | 1874 | 2161 | 1803 | 2167 | -71 | 71 | 6 | 6 | 0.788462 | matched | 4 |
| 5 | 5 | 2210 | 2500 | 2308 | 2496 | 98 | 98 | -4 | 4 | 0.648276 | matched | 5 |
| 6 | 6 | 2558 | 2806 | 2578 | 2799 | 20 | 20 | -7 | 7 | 0.891129 | matched | 6 |
| 7 | 7 | 2976 | 3377 | 2977 | 3377 | 1 | 1 | 0 | 0 | 0.997506 | matched | 7 |
| 8 | 8 | 3451 | 3695 | 3519 | 3699 | 68 | 68 | 4 | 4 | 0.709677 | matched | 8 |
| 9 | 9 | 3751 | 4073 | 3857 | 4059 | 106 | 106 | -14 | 14 | 0.627329 | matched | 9 |
| 10 | 10 | 4247 | 4839 | 4272 | 4804 | 25 | 25 | -35 | 35 | 0.898649 | matched | 10 |
| 11 | 11 | 4872 | 5045 | 4901 | 5027 | 29 | 29 | -18 | 18 | 0.728324 | matched | 11 |
| 12 | 12 | 5430 | 5871 | 5455 | 5887 | 25 | 25 | 16 | 16 | 0.910284 | matched | 12 |
| 13 | 13 | 5958 | 6312 | 5979 | 6315 | 21 | 21 | 3 | 3 | 0.932773 | matched | 13 |
| 14 | 14 | 6382 | 6656 | 6450 | 6639 | 68 | 68 | -17 | 17 | 0.689781 | matched | 14 |
| 15 | 15 | 6716 | 6913 | 6802 | 6908 | 86 | 86 | -5 | 5 | 0.538071 | matched | 15 |
| 16 | 16 | 6976 | 7458 | 7006 | 7502 | 30 | 30 | 44 | 44 | 0.859316 | matched | 16 |
| 17 | 17 | 7532 | 7741 | 7537 | 7731 | 5 | 5 | -10 | 10 | 0.928230 | matched | 17 |
| 18 | 18 | 7947 | 8053 | 7953 | 8052 | 6 | 6 | -1 | 1 | 0.933962 | matched | 18 |
| 19 | 19 | 8106 | 8628 | 8111 | 8627 | 5 | 5 | -1 | 1 | 0.988506 | matched | 19 |
| 20 | 20 | 8683 | 9967 | 8715 | 9947 | 32 | 32 | -20 | 20 | 0.959502 | matched | 20 |
| 21 | 21 | 10245 | 10563 | 10249 | 10538 | 4 | 4 | -25 | 25 | 0.908805 | matched | 21 |
| 22 | 22 | 10607 | 10708 | 10605 | 10738 | -2 | 2 | 30 | 30 | 0.759398 | matched | 22 |
| 23 | 23 | 10733 | 11078 | 10775 | 11085 | 42 | 42 | 7 | 7 | 0.860795 | matched | 23 |
| 24 | 24 | 11271 | 11392 | 11274 | 11397 | 3 | 3 | 5 | 5 | 0.936508 | matched | 24 |
| 25 | 25 | 11568 | 11865 | 11613 | 11867 | 45 | 45 | 2 | 2 | 0.842809 | matched | 25 |
| 26 | 26 | 11976 | 12197 | 11982 | 12196 | 6 | 6 | -1 | 1 | 0.968326 | matched | 26 |
| 27 | 27 | 12451 | 12966 | 12455 | 12954 | 4 | 4 | -12 | 12 | 0.968932 | matched | 27 |
| 28 | 28 | 13054 | 13442 | 13115 | 13439 | 61 | 61 | -3 | 3 | 0.835052 | matched | 28 |
| 29 | 29 | 13679 | 13994 | 13686 | 13982 | 7 | 7 | -12 | 12 | 0.939683 | matched | 29 |
| 30 | 30 | 14219 | 14335 | 14222 | 14331 | 3 | 3 | -4 | 4 | 0.939655 | matched | 30 |
| 31 | 31 | 14404 | 15151 | 14430 | 15171 | 26 | 26 | 20 | 20 | 0.940026 | matched | 31 |
| 32 | 32 | 15350 | 15535 | 15354 | 15529 | 4 | 4 | -6 | 6 | 0.945946 | matched | 32 |
| 33 | 33 | 15596 | 15946 | 15664 | 15951 | 68 | 68 | 5 | 5 | 0.794366 | matched | 33 |
| 34 | 34 | 15998 | 16387 | 16000 | 16385 | 2 | 2 | -2 | 2 | 0.989717 | matched | 34 |
| 35 | 35 | 16513 | 17026 | 16521 | 17031 | 8 | 8 | 5 | 5 | 0.974903 | matched | 35 |
| 36 | 36 | 17066 | 17226 | 17074 | 17207 | 8 | 8 | -19 | 19 | 0.831250 | matched | 36 |

### Every GT rally compared directly: timestamps and durations

| G | GT start s | GT end s | Pred start s | Pred end s | GT duration s | Pred duration s | Δstart s | \|Δstart\| s | Δend s | \|Δend\| s | Δduration s | \|Δduration\| s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8.100000 | 23.833333 | 8.800000 | 23.900000 | 15.733333 | 15.100000 | 0.700000 | 0.700000 | 0.066667 | 0.066667 | -0.633333 | 0.633333 |
| 2 | 29.566667 | 42.066667 | 29.666667 | 41.833333 | 12.500000 | 12.166667 | 0.100000 | 0.100000 | -0.233333 | 0.233333 | -0.333333 | 0.333333 |
| 3 | 46.600000 | 55.466667 | 46.733333 | 55.300000 | 8.866667 | 8.566667 | 0.133333 | 0.133333 | -0.166667 | 0.166667 | -0.300000 | 0.300000 |
| 4 | 62.466667 | 72.033333 | 60.100000 | 72.233333 | 9.566667 | 12.133333 | -2.366667 | 2.366667 | 0.200000 | 0.200000 | 2.566667 | 2.566667 |
| 5 | 73.666667 | 83.333333 | 76.933333 | 83.200000 | 9.666667 | 6.266667 | 3.266667 | 3.266667 | -0.133333 | 0.133333 | -3.400000 | 3.400000 |
| 6 | 85.266667 | 93.533333 | 85.933333 | 93.300000 | 8.266667 | 7.366667 | 0.666667 | 0.666667 | -0.233333 | 0.233333 | -0.900000 | 0.900000 |
| 7 | 99.200000 | 112.566667 | 99.233333 | 112.566667 | 13.366667 | 13.333333 | 0.033333 | 0.033333 | 0.000000 | 0.000000 | -0.033333 | 0.033333 |
| 8 | 115.033333 | 123.166667 | 117.300000 | 123.300000 | 8.133333 | 6.000000 | 2.266667 | 2.266667 | 0.133333 | 0.133333 | -2.133333 | 2.133333 |
| 9 | 125.033333 | 135.766667 | 128.566667 | 135.300000 | 10.733333 | 6.733333 | 3.533333 | 3.533333 | -0.466667 | 0.466667 | -4.000000 | 4.000000 |
| 10 | 141.566667 | 161.300000 | 142.400000 | 160.133333 | 19.733333 | 17.733333 | 0.833333 | 0.833333 | -1.166667 | 1.166667 | -2.000000 | 2.000000 |
| 11 | 162.400000 | 168.166667 | 163.366667 | 167.566667 | 5.766667 | 4.200000 | 0.966667 | 0.966667 | -0.600000 | 0.600000 | -1.566667 | 1.566667 |
| 12 | 181.000000 | 195.700000 | 181.833333 | 196.233333 | 14.700000 | 14.400000 | 0.833333 | 0.833333 | 0.533333 | 0.533333 | -0.300000 | 0.300000 |
| 13 | 198.600000 | 210.400000 | 199.300000 | 210.500000 | 11.800000 | 11.200000 | 0.700000 | 0.700000 | 0.100000 | 0.100000 | -0.600000 | 0.600000 |
| 14 | 212.733333 | 221.866667 | 215.000000 | 221.300000 | 9.133333 | 6.300000 | 2.266667 | 2.266667 | -0.566667 | 0.566667 | -2.833333 | 2.833333 |
| 15 | 223.866667 | 230.433333 | 226.733333 | 230.266667 | 6.566667 | 3.533333 | 2.866667 | 2.866667 | -0.166667 | 0.166667 | -3.033333 | 3.033333 |
| 16 | 232.533333 | 248.600000 | 233.533333 | 250.066667 | 16.066667 | 16.533333 | 1.000000 | 1.000000 | 1.466667 | 1.466667 | 0.466667 | 0.466667 |
| 17 | 251.066667 | 258.033333 | 251.233333 | 257.700000 | 6.966667 | 6.466667 | 0.166667 | 0.166667 | -0.333333 | 0.333333 | -0.500000 | 0.500000 |
| 18 | 264.900000 | 268.433333 | 265.100000 | 268.400000 | 3.533333 | 3.300000 | 0.200000 | 0.200000 | -0.033333 | 0.033333 | -0.233333 | 0.233333 |
| 19 | 270.200000 | 287.600000 | 270.366667 | 287.566667 | 17.400000 | 17.200000 | 0.166667 | 0.166667 | -0.033333 | 0.033333 | -0.200000 | 0.200000 |
| 20 | 289.433333 | 332.233333 | 290.500000 | 331.566667 | 42.800000 | 41.066667 | 1.066667 | 1.066667 | -0.666667 | 0.666667 | -1.733333 | 1.733333 |
| 21 | 341.500000 | 352.100000 | 341.633333 | 351.266667 | 10.600000 | 9.633333 | 0.133333 | 0.133333 | -0.833333 | 0.833333 | -0.966667 | 0.966667 |
| 22 | 353.566667 | 356.933333 | 353.500000 | 357.933333 | 3.366667 | 4.433333 | -0.066667 | 0.066667 | 1.000000 | 1.000000 | 1.066667 | 1.066667 |
| 23 | 357.766667 | 369.266667 | 359.166667 | 369.500000 | 11.500000 | 10.333333 | 1.400000 | 1.400000 | 0.233333 | 0.233333 | -1.166667 | 1.166667 |
| 24 | 375.700000 | 379.733333 | 375.800000 | 379.900000 | 4.033333 | 4.100000 | 0.100000 | 0.100000 | 0.166667 | 0.166667 | 0.066667 | 0.066667 |
| 25 | 385.600000 | 395.500000 | 387.100000 | 395.566667 | 9.900000 | 8.466667 | 1.500000 | 1.500000 | 0.066667 | 0.066667 | -1.433333 | 1.433333 |
| 26 | 399.200000 | 406.566667 | 399.400000 | 406.533333 | 7.366667 | 7.133333 | 0.200000 | 0.200000 | -0.033333 | 0.033333 | -0.233333 | 0.233333 |
| 27 | 415.033333 | 432.200000 | 415.166667 | 431.800000 | 17.166667 | 16.633333 | 0.133333 | 0.133333 | -0.400000 | 0.400000 | -0.533333 | 0.533333 |
| 28 | 435.133333 | 448.066667 | 437.166667 | 447.966667 | 12.933333 | 10.800000 | 2.033333 | 2.033333 | -0.100000 | 0.100000 | -2.133333 | 2.133333 |
| 29 | 455.966667 | 466.466667 | 456.200000 | 466.066667 | 10.500000 | 9.866667 | 0.233333 | 0.233333 | -0.400000 | 0.400000 | -0.633333 | 0.633333 |
| 30 | 473.966667 | 477.833333 | 474.066667 | 477.700000 | 3.866667 | 3.633333 | 0.100000 | 0.100000 | -0.133333 | 0.133333 | -0.233333 | 0.233333 |
| 31 | 480.133333 | 505.033333 | 481.000000 | 505.700000 | 24.900000 | 24.700000 | 0.866667 | 0.866667 | 0.666667 | 0.666667 | -0.200000 | 0.200000 |
| 32 | 511.666667 | 517.833333 | 511.800000 | 517.633333 | 6.166667 | 5.833333 | 0.133333 | 0.133333 | -0.200000 | 0.200000 | -0.333333 | 0.333333 |
| 33 | 519.866667 | 531.533333 | 522.133333 | 531.700000 | 11.666667 | 9.566667 | 2.266667 | 2.266667 | 0.166667 | 0.166667 | -2.100000 | 2.100000 |
| 34 | 533.266667 | 546.233333 | 533.333333 | 546.166667 | 12.966667 | 12.833333 | 0.066667 | 0.066667 | -0.066667 | 0.066667 | -0.133333 | 0.133333 |
| 35 | 550.433333 | 567.533333 | 550.700000 | 567.700000 | 17.100000 | 17.000000 | 0.266667 | 0.266667 | 0.166667 | 0.166667 | -0.100000 | 0.100000 |
| 36 | 568.866667 | 574.200000 | 569.133333 | 573.566667 | 5.333333 | 4.433333 | 0.266667 | 0.266667 | -0.633333 | 0.633333 | -0.900000 | 0.900000 |

### Secondary coarse/outcome annotations: full supplied baseline and comparison

[Test1_Full.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test1_Full/Test1_Full.csv) contains **36 data rows**, **36 nonblank intervals**, blank row IDs **[]**. This separate reference differs from the 36-interval primary timing table. The same unchanged predictions and matcher give secondary precision **100.000%**, recall **100.000%**, F1 **100.000%**; this reference-sensitivity analysis does not replace the primary benchmark. No labels, times or predictions were fitted or repaired.

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 36 | 36 | 0 |
| Prediction count | 36 | 36 | 0 |
| TP / matched | 36 | 36 | 0 |
| FP | 0 | 0 | 0 |
| FN / missed | 0 | 0 | 0 |
| precision | 1 | 1.000000 | 0.000000 |
| recall | 1 | 1.000000 | 0.000000 |
| f1 | 1 | 1.000000 | 0.000000 |
| Mean matched IoU | 1 | 0.842130 | -0.157870 |
| Median matched IoU | 1 | 0.865879 | -0.134121 |
| Minimum matched IoU | 1 | 0.620253 | -0.379747 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 75.000000 |
| 0.9 | 100 | 44.444444 |
| 0.95 | 100 | 19.444444 |

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 30.888889 | 22.500000 | 41.268094 | 97.000000 | 73.000000 | 30.777778 | 22.500000 |
| end_frame | 14.000000 | 12.500000 | 16.741499 | 44.000000 | 26.000000 | 0.777778 | 3.000000 |
| start_time_sec | 1.029630 | 0.750000 | 1.375603 | 3.233333 | 2.433333 | 1.025926 | 0.750000 |
| end_time_sec | 0.466667 | 0.416667 | 0.558050 | 1.466667 | 0.866667 | 0.025926 | 0.100000 |
| duration_sec | 1.159259 | 0.800000 | 1.488350 | 3.666667 | 2.483333 | -1.000000 | -0.800000 |

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 1 | 36 | 2.778% | 36 | 2.778% | 100% |
| start | 3 | 0.100000 | 4 | 36 | 11.111% | 36 | 11.111% | 100% |
| start | 5 | 0.166667 | 8 | 36 | 22.222% | 36 | 22.222% | 100% |
| start | 10 | 0.333333 | 10 | 36 | 27.778% | 36 | 27.778% | 100% |
| start | 15 | 0.500000 | 15 | 36 | 41.667% | 36 | 41.667% | 100% |
| start | 30 | 1.000000 | 22 | 36 | 61.111% | 36 | 61.111% | 100% |
| end | 1 | 0.033333 | 1 | 36 | 2.778% | 36 | 2.778% | 100% |
| end | 3 | 0.100000 | 3 | 36 | 8.333% | 36 | 8.333% | 100% |
| end | 5 | 0.166667 | 5 | 36 | 13.889% | 36 | 13.889% | 100% |
| end | 10 | 0.333333 | 16 | 36 | 44.444% | 36 | 44.444% | 100% |
| end | 15 | 0.500000 | 24 | 36 | 66.667% | 36 | 66.667% | 100% |
| end | 30 | 1.000000 | 34 | 36 | 94.444% | 36 | 94.444% | 100% |

| Cross-reference timing diagnostic | Value |
|---|---|
| Primary-to-coarse eligible matched intervals | 36 |
| Primary intervals unmatched to coarse reference | [] |
| Coarse rows unmatched to primary reference | [] |
| Primary/coarse matched mean IoU | 0.877293 |

| C source row | Supplied start | Supplied end | Supplied winner | Supplied A:B score | Supplied shot / ball_types | Win reason | Lose reason | Matched P | IoU | Δstart s | Δend s | Δduration s | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:08 | 0:24 | Player B | 0:1 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 1 | 0.943750 | 0.800000 | -0.100000 | -0.900000 | matched |
| 2 | 0:27 | 0:42 | Player A | 1:1 | Push Shot | Opponent Hit the Net | Hit the Net | 2 | 0.811111 | 2.666667 | -0.166667 | -2.833333 | matched |
| 3 | 0:44 | 0:55 | Player B | 1:2 | Push Shot | Winner Shot | Opponent Failed to Return | 3 | 0.731563 | 2.733333 | 0.300000 | -2.433333 | matched |
| 4 | 1:00 | 1:12 | Player B | 1:3 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 4 | 0.972752 | 0.100000 | 0.233333 | 0.133333 | matched |
| 5 | 1:15 | 1:23 | Player B | 1:4 | Lift Shot | Winner Shot | Opponent Failed to Return | 5 | 0.739837 | 1.933333 | 0.200000 | -1.733333 | matched |
| 6 | 1:26 | 1:34 | Player A | 2:4 | Smash | Opponent Hit the Net | Hit the Net | 6 | 0.904959 | -0.066667 | -0.700000 | -0.633333 | matched |
| 7 | 1:36 | 1:53 | Player B | 2:5 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 7 | 0.784314 | 3.233333 | -0.433333 | -3.666667 | matched |
| 8 | 1:55 | 2:03 | Player A | 3:5 | Block Shot | Opponent Hit the Net | Hit the Net | 8 | 0.686747 | 2.300000 | 0.300000 | -2.000000 | matched |
| 9 | 2:06 | 2:15 | Player B | 3:6 | Drop Shot | Opponent Hit the Net | Hit the Net | 9 | 0.691756 | 2.566667 | 0.300000 | -2.266667 | matched |
| 10 | 2:22 | 2:40 | Player A | 4:6 | Smash | Winner Shot | Opponent Failed to Return | 10 | 0.970588 | 0.400000 | 0.133333 | -0.266667 | matched |
| 11 | 2:43 | 2:47 | Player A | 5:6 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 11 | 0.795620 | 0.366667 | 0.566667 | 0.200000 | matched |
| 12 | 3:01 | 3:16 | Player A | 6:6 | Slice Shot | Opponent Hit the Net | Hit the Net | 12 | 0.929978 | 0.833333 | 0.233333 | -0.600000 | matched |
| 13 | 3:18 | 3:30 | Player A | 7:6 | Smash | Opponent Out of Bounds | Hit Out of Bounds | 13 | 0.856000 | 1.300000 | 0.500000 | -0.800000 | matched |
| 14 | 3:33 | 3:42 | Player A | 8:6 | Slice Shot | Winner Shot | Opponent Failed to Return | 14 | 0.700000 | 2.000000 | -0.700000 | -2.700000 | matched |
| 15 | 3:45 | 3:50 | Player A | 9:6 | Slice Shot | Winner Shot | Opponent Failed to Return | 15 | 0.620253 | 1.733333 | 0.266667 | -1.466667 | matched |
| 16 | 3:53 | 4:09 | Player B | 9:7 | Defensive Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 16 | 0.906250 | 0.533333 | 1.066667 | 0.533333 | matched |
| 17 | 4:11 | 4:18 | Player B | 9:8 | Hook Shot | Winner Shot | Opponent Failed to Return | 17 | 0.923810 | 0.233333 | -0.300000 | -0.533333 | matched |
| 18 | 4:24 | 4:28 | Player B | 9:9 | Defensive Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 18 | 0.659091 | 1.100000 | 0.400000 | -0.700000 | matched |
| 19 | 4:30 | 4:48 | Player A | 10:9 | Hook Shot | Opponent Hit the Net | Hit the Net | 19 | 0.955556 | 0.366667 | -0.433333 | -0.800000 | matched |
| 20 | 4:49 | 5:32 | Player A | 11:9 | Drop Shot | Opponent Hit the Net | Hit the Net | 20 | 0.955039 | 1.500000 | -0.433333 | -1.933333 | matched |
| 21 | 5:41 | 5:52 | Player A | 12:9 | Slice Shot | Opponent Out of Bounds | Hit Out of Bounds | 21 | 0.875758 | 0.633333 | -0.733333 | -1.366667 | matched |
| 22 | 5:53 | 5:57 | Player B | 12:10 | Drop Shot | Opponent Hit the Net | Hit the Net | 22 | 0.709459 | 0.500000 | 0.933333 | 0.433333 | matched |
| 23 | 5:59 | 6:09 | Player B | 12:11 | Hook Shot | Opponent Hit the Net | Hit the Net | 23 | 0.936508 | 0.166667 | 0.500000 | 0.333333 | matched |
| 24 | 6:15 | 6:19 | Player B | 12:12 | Hook Shot | Opponent Hit the Net | Hit the Net | 24 | 0.653061 | 0.800000 | 0.900000 | 0.100000 | matched |
| 25 | 6:25 | 6:36 | Player B | 12:13 | Flat Shot | Opponent Hit the Net | Hit the Net | 25 | 0.769697 | 2.100000 | -0.433333 | -2.533333 | matched |
| 26 | 6:39 | 6:48 | Player B | 12:14 | Smash | Opponent Out of Bounds | Hit Out of Bounds | 26 | 0.792593 | 0.400000 | -1.466667 | -1.866667 | matched |
| 27 | 6:55 | 7:12 | Player A | 13:14 | Defensive Drive Shot | Winner Shot | Opponent Failed to Return | 27 | 0.978431 | 0.166667 | -0.200000 | -0.366667 | matched |
| 28 | 7:17 | 7:28 | Player A | 14:14 | Drop Shot | Opponent Hit the Net | Hit the Net | 28 | 0.981818 | 0.166667 | -0.033333 | -0.200000 | matched |
| 29 | 7:35 | 7:46 | Player B | 14:15 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 29 | 0.885542 | 1.200000 | 0.066667 | -1.133333 | matched |
| 30 | 7:54 | 7:58 | Player A | 15:15 | Defensive Drive Shot | Opponent Hit the Net | Hit the Net | 30 | 0.908333 | 0.066667 | -0.300000 | -0.366667 | matched |
| 31 | 8:01 | 8:25 | Player B | 15:16 | Hook Shot | Opponent Hit the Net | Hit the Net | 31 | 0.971660 | 0.000000 | 0.700000 | 0.700000 | matched |
| 32 | 8:31 | 8:38 | Player A | 16:16 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 32 | 0.833333 | 0.800000 | -0.366667 | -1.166667 | matched |
| 33 | 8:40 | 8:52 | Player B | 16:17 | Drop Shot | Opponent Hit the Net | Hit the Net | 33 | 0.797222 | 2.133333 | -0.300000 | -2.433333 | matched |
| 34 | 8:53 | 9:07 | Player B | 16:18 | Smash | Winner Shot | Opponent Failed to Return | 34 | 0.916667 | 0.333333 | -0.833333 | -1.166667 | matched |
| 35 | 9:10 | 9:27 | Player B | 16:19 | Slice Shot | Opponent Hit the Net | Hit the Net | 35 | 0.920904 | 0.700000 | 0.700000 | 0.000000 | matched |
| 36 | 9:29 | 9:33 | Player B | 16:20 | Drop Shot | Opponent Hit the Net | Hit the Net | 36 | 0.846715 | 0.133333 | 0.566667 | 0.433333 | matched |

| Supplied semantic label inventory | Counts |
|---|---|
| win_point_player | {"Player B":20,"Player A":16} |
| ball_types | {"Lift Shot":4,"Push Shot":5,"Smash":5,"Block Shot":1,"Drop Shot":6,"Slice Shot":5,"Defensive Drive Shot":4,"Hook Shot":5,"Flat Shot":1} |
| roundscore_A | {"0":1,"1":4,"2":2,"3":2,"4":1,"5":1,"6":1,"7":1,"8":1,"9":4,"10":1,"11":1,"12":6,"13":1,"14":2,"15":2,"16":5} |
| roundscore_B | {"1":2,"2":1,"3":1,"4":2,"5":2,"6":7,"7":1,"8":1,"9":4,"10":1,"11":1,"12":1,"13":1,"14":3,"15":2,"16":2,"17":1,"18":1,"19":1,"20":1} |

The supplied winner/score/shot fields are reproduced above exactly as source strings, including missing values and taxonomy variation. The temporal crosswalk does not establish named player/team equivalence, certified point identity, or exhaustive shot labels. Current rally winners are unknown and hitter identities are anonymous; outcome/score-sequence accuracy and per-shot confusion therefore remain unscorable, rather than being reported as verified model correctness.

### Component-level observed output versus available ground truth

| Coverage diagnostic | Numerator | Denominator | Coverage | Ground-truth accuracy available? |
|---|---|---|---|---|
| Raw shuttle present / source frames | 12036 | 17268 | 69.701% | No reviewed frame/person/contact labels |
| Detector-executed / source frames | 7091 | 17268 | 41.064% | No reviewed frame/person/contact labels |
| Fresh detector-matched person rows / person rows | 14091 | 33716 | 41.793% | No reviewed frame/person/contact labels |
| Current pose rows / person rows | 26752 | 33716 | 79.345% | No reviewed frame/person/contact labels |
| Current racket rows / person rows | 11385 | 33716 | 33.767% | No reviewed frame/person/contact labels |

| All component coverage counts | Value |
|---|---|
| frames | 17268 |
| raw_shuttle_present | 12036 |
| detector_executed_frames | 7091 |
| person_rows | 33716 |
| scene_telemetry_present | 3610 |
| scene_raw_hypotheses | 13 |
| actual_content_epoch_increments | 13 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 14091 |
| person_propagated_or_unmatched | 19625 |
| pose_present_rows | 26752 |
| pose_current_source_rows | 26752 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 12661 |
| racket_present_rows | 11385 |
| racket_current_source_rows | 11385 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 13 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 13 |

#### Frame/component categories

| Field | Observed value |
|---|---|
| view | {"main":16983,"none":285} |
| calibration_state | {"REACQUIRING":42,"VALID":16941,"LOST":285} |
| player_population | {"0":354,"2":16802,"1":112} |
| association_status | {"missing":4947,"observed":11947,"invalid":285,"ambiguous":89} |
| association_reason | {"no_accepted_raw_observation":4947,"fresh_selection_retained":11947,"image_view_invalid":285,"coobserved_competing_static_hypothesis":89} |
| scene_raw_status | {"unknown":154,"measured":3443,"hypothesis":13} |
| person_detector_match | {"True":14091,"False":19625} |
| person_identity_method | {"bytetrack_v1":33716} |
| scene_decision | {"barrier":13} |
| scene_decision_reason | {"raw_change_and_current_layout_discontinuity":13} |

#### Live event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 122 |
| scene | 17 |
| participant_observation | 123 |
| format_decision | 1 |
| rally_start | 36 |
| stroke | 446 |
| contact | 446 |
| rally_end | 36 |
| shuttle_turn | 41 |
| identity_ambiguity | 50 |
| broadcast_score | 473 |
| match_phase | 1 |
| highlight | 3 |

#### Append-only event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 122 |
| scene | 17 |
| participant_observation | 123 |
| format_decision | 1 |
| rally_start | 78 |
| contact | 988 |
| stroke | 482 |
| rally_end | 36 |
| shuttle_turn | 41 |
| identity_ambiguity | 50 |
| broadcast_score | 473 |
| match_phase | 1 |
| highlight | 3 |

#### All observed event categories

| Field | Observed value |
|---|---|
| event_status | {"confirmed":1546,"provisional":250} |
| stroke_actor | {"unknown":446} |
| stroke_physical_event_status | {"ambiguous":136,"insufficient":228,"probable":82} |
| stroke_contact_status | {"estimated":446} |
| stroke_classification_status | {"unknown":309,"estimated":137} |
| stroke_stroke | {"unknown":309,"push":47,"lift":27,"drive":2,"net_shot":30,"drop":21,"clear":8,"smash":2} |
| stroke_attribution_reason | {"nearest_proximity":442,"ambiguous_proximity":4} |
| stroke_classification_abstention_reason | {"unresolved_initial_contact":6,"missing_required_evidence":303} |
| contact_actor | {"unknown":446} |
| contact_physical_event_status | {"ambiguous":136,"insufficient":228,"probable":82} |
| contact_contact_status | {"estimated":446} |
| contact_attribution_reason | {"nearest_proximity":442,"ambiguous_proximity":4} |
| contact_trajectory_reliability | {"probable":265,"ambiguous":87,"insufficient":94} |
| contact_trajectory_reasons | {"supported_turn":200,"association_unresolved":87,"coherent_motion_change_unavailable":94,"supported_launch":65} |
| contact_impact_reliability | {"ambiguous":136,"insufficient":228,"probable":82} |
| contact_impact_reasons | {"no_fresh_swing_or_racket_overlap":20,"association_unresolved":87,"fresh_player_observation_unavailable":228,"coherent_motion_change_unavailable":29,"coherent_motion_and_fresh_contact_cue":82} |
| contact_attribution_reliability | {"probable":164,"insufficient":282} |
| contact_attribution_reasons | {"geometric_attribution_not_verified_identity":164,"fresh_player_observation_unavailable":282} |
| rally_end_reason | {"gap":16,"stationary":19,"cut":1} |
| rally_phase | {"unknown":3,"match_play":33} |
| rally_official | {"False":16,"True":20} |
| rally_match_format_known | {"True":36} |
| rally_match_format | {"singles":36} |
| rally_winner | {"None":36} |
| rally_score_transition_status | {"unavailable":30,"candidate":6} |
| rally_admission_reason | {"duration_policy":36} |

#### Track/export counts

| Field | Observed value |
|---|---|
| camera_rows | 17268 |
| player_rows | 33702 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 33045 |
| projected_court_on_propagated_box | 19281 |
| racket_rows | 11376 |
| shuttle_rows | 17268 |

#### Track/export categories

| Field | Observed value |
|---|---|
| player_id | {"None":33702} |
| detector_matched | {"True":14077,"False":19625} |

| Semantic metric | Observed | Baseline comparison / limitation |
|---|---|---|
| Known rally winner output | 0/36 | Supplied coarse winner labels exist; identity/point mapping uncertified |
| Unknown stroke classification | 309/446 | Coarse one-label-per-rally ball_types is not exhaustive per-shot GT |
| Estimated stroke classification | 137/446 | Estimated coverage is not class accuracy |
| OCR saved readouts | 506 | Observed scoreboard rows, not accepted correct points |
| OCR label counts | {"AN S.Y.":491,"INTANON":506,"ANS.Y.":15} | Raw OCR labels may differ from anonymous Player A/B |
| Tracked invalid geometry frames | 327 | Geometric diagnostics, not labelled location error |
| Session degradation | [{"stage":"player_identity","reason":"osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"},{"stage":"player_reid","reason":"baseline player_reid provider is unavailable"}] | Identity/ReID unavailability remains recorded; no new models fetched |

### Runtime, resources and every saved stage latency

| Saved resource/runtime metric | Value |
|---|---|
| original_parent_status | partial_or_failed |
| worker_exit_code | 1 |
| physical_gpu_index | 0 |
| allocated_gpu_uuid | GPU-96e23501-7ac6-918a-adf7-047ff31a6ae3 |
| worker_pid | 2144591 |
| parent_failure_inclusive_elapsed_s | 2037.223530 |
| parent_failure_inclusive_source_fps | 8.476242 |
| neural_only_throughput_fps | — |
| model_loading_time_s | — |
| media_ready_time_s | — |
| model_staging_time_s | — |
| worker_final_cpu_s | — |
| worker_maxrss_bytes | — |
| sampled_worker_tree_peak_rss_bytes | 3068030976 |
| sampled_worker_gpu_peak_mib | 2126 |
| sampled_cpu_seconds_max_observed | 20603.530000 |
| sampled_cpu_seconds_last_observed | 20603.530000 |
| sampled_system_available_ram_min_bytes | 98946695168 |
| sample_count | 985 |
| resource_rows | 985 |
| sampling_error_count | 0 |

| Stage | Calls | Total wall s | P50 ms/call | P95 ms/call | Minimum ms | Maximum ms | Frame-population sum |
|---|---|---|---|---|---|---|---|
| court | 288 | 110.121063 | 321.410649 | 799.301641 | 221.940612 | 1436.911524 | 17268 |
| content_continuity_and_players | 288 | 864.606605 | 3313.881906 | 3899.481872 | 924.935154 | 4259.089757 | 17268 |
| shuttle | 288 | 256.244499 | 827.320099 | 1249.415762 | 610.819915 | 1751.743821 | 17268 |
| players | 288 | 72.005961 | 230.900594 | 520.634561 | 4.903747 | 962.023133 | 17268 |
| ocr | 288 | 392.144158 | 1277.346160 | 2133.222281 | 613.711912 | 2546.138222 | 17268 |

The historical timing key decode_perception_cache_s wraps the runner’s full _perceive call. Its name does not mean this was an observation-cache replay: the completed-worker receipts explicitly record cached_perception_used=false. It is a broad perception wall-time scope, not isolated cache decoding or pure GPU latency.

| Saved disk-use metric | Bytes / count |
|---|---|
| regular_files | 1755 |
| logical_bytes | 714102123 |
| allocated_bytes | 717713408 |
| staged_model_bytes | 361041769 |
| perception_cache_bytes | 72971704 |

Wall-time scopes overlap; they are not summable GPU kernel latency. Pure neural-only FPS and isolated model-loading time remain unavailable. For historical Tests 1/2, final worker-local timing/CPU/RSS fields were lost at catalogue publication and stay unavailable; failure-inclusive parent duration is identified explicitly. For normal runs, worker elapsed includes the runner and final catalogue verification. Current-process GPU samples cannot certify per-node ORT placement or true instantaneous memory peaks.

### Reproducibility, logs and annotation-file review

| Binding | Value |
|---|---|
| Normalized numerical profile SHA256 (passive ranges removed) | 2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb |
| Effective profile canonical SHA256 | bd83c5e3e26df1b065499fe7ba828f991856c73a9027653bc9b3f1f3d28438c7 |
| Model identity sets | 1 |
| Runtime identity sets | 1 |
| Actual model identity SHA256 | e3c96b7c2e522fd6efe6106328bebec30137f29b7303fe5e475f8aedea5d2222 |
| Actual runtime identity SHA256 | 81e41f18d858ed37c34ce9d07ae34a34268f27e57c0e5f878e07253be309066f |
| Executed plan | [plan.json](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/protocol_test1_v2/plan.json) |
| Actual completion receipt | [completion_receipt.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test1_historical/completion/completion_receipt.json) |
| Per-rally saved CSV | [per_rally_comparison.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test1_historical/evaluation/per_rally_comparison.csv) |
| Technical analysis | [technical_analysis.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test1_historical/analysis/technical_analysis.json) |
| Full original predictions | [predicted_rallies.csv](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_test1_v1/predicted_rallies.csv) |

| Annotation file | Role | Data rows | Blank rows | Bytes | Column/schema inventory | SHA256 |
|---|---|---|---|---|---|---|
| Test1_Full.csv | Secondary coarse outcome/time reference | 36 | 0 | 2663 | ["start_time","end_time","win_point_player","win_reason","ball_types","lose_reason","roundscore_A","roundscore_B"] | e3466ded0dace3c7df60b237db779de68c7910672ca14218a2ce8cf5f9b45545 |
| Test1_Full2.csv | Auxiliary historical/generated artifact; not certified independent truth | 21 | 0 | 2483 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","win_point_player","win_reason","ball_types","lose_reason","roundscore_A","roundscore_B"] | 8a6838b3d9536d64ad31c8109cf1eb283c4401b1ffbd7d2cab4868aef1068675 |
| Test1_Full_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 17268 | 0 | 368114 | ["Frame","X","Y","Visibility","Confidence"] | e4fc8b4ea366f33f324fe2b1513271daf448211b8129371b5389c79aca694f23 |
| Test1_Full_court.json | Auxiliary historical/generated artifact; not certified independent truth | — | — | 664 | ["frame_no","frame_size","corners","net","source"] | 2a277cda90bc99becef97cf3e548a00ab781ac28cfa364d2896fc08ac12b99d9 |
| Test1_Full_rally.csv | Primary timing reference | 36 | 0 | 2610 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 30651cf7238924d6a5072b1dd71d34ca5839cd5b842f696e745229033ae4f887 |
| Test1_Full_rev_T.csv | Auxiliary historical/generated artifact; not certified independent truth | 35 | 0 | 2536 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 836f73ee0253da4af68010efc84b1aba02605b904eda28b9fce3cbd72273f022 |
| Test1_Full_rev_T4.csv | Auxiliary historical/generated artifact; not certified independent truth | 38 | 0 | 2737 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 12ea3eab46656e47e8e3a7059bebdf43f2aa29298f8a006f67c15c13d416ce96 |
| player_detections.csv | Auxiliary historical/generated artifact; not certified independent truth | 17268 | 0 | 1914969 | ["frame_no","player_1_x","player_1_y","player_1_conf","player_2_x","player_2_y","player_2_conf"] | a7cb333f542ffcc76cb235898821df2abfc278a667d3f6ef09ab3f6c787d5c16 |
| win_predictions.csv | Auxiliary historical/generated artifact; not certified independent truth | 36 | 0 | 4373 | ["rally_idx","start_frame","end_frame","start_time","end_time","winner","loser","win_reason","reason_src","fault_side","fault_src","cnn_class","cnn_conf","cnn_oob","cnn_hn","cnn_wbl","score_Player A","score_Player B"] | 93fbe796053a9bef2dc86c7a8582a0ed0572b1e39a9e00f5744f2778bdb31c88 |

| Log | Lines | Warning/error-pattern lines | Distinct observed warning/error messages |
|---|---|---|---|
| fresh_test1_v1.execution.log | 57 | 24 | ["2026-11-05 22:02:31 [warning  ] perception.degraded            reason='osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`' stage=player_identity","2026-11-05 22:02:31 [warning  ] perception.degraded            reason='baseline player_reid provider is unavailable' stage=player_reid","[WARNING] 2026-11-05 22:03:20,784 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:03:32,389 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:03:47,919 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:04:03,105 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:04:17,651 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:04:31,383 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:04:42,919 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:04:57,294 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:21:59,666 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:22:12,906 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:22:27,024 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:22:41,788 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:22:54,105 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:23:09,814 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:25:55,852 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:29:30,678 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:29:31,220 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:29:37,464 [RapidOCR] main.py:164: The text detection result is empty","    raise ValueError(\"unsupported cache codec version\")","ValueError: unsupported cache codec version","    raise ValueError(f\"invalid bounded cache header/frames: {path.name}: {error}\") from error","ValueError: invalid bounded cache header/frames: seg_00000.msgpack: unsupported cache codec version"] |
| fresh_test1_v1.launch.log | 0 | 0 | [] |

Log keyword counts are diagnostic string matches, not failed-inference counts. Tests 1/2 raw original worker logs remain in their source run directories and retain the known final catalogue failure; their independent completion proof is the accepted completion record. All previously completed evaluations remain immutable.

### Duration breakdown for this video

| GT duration bin | GT count | Matched | Missed | Recall | Start MAE f | End MAE f |
|---|---|---|---|---|---|---|
| ≤2 s | 0 | 0 | 0 | — | — | — |
| (2,5] s | 4 | 4 | 0 | 1.000000 | 3.500000 | 10.000000 |
| (5,10] s | 13 | 13 | 0 | 1.000000 | 39.384615 | 8.000000 |
| (10,20] s | 17 | 17 | 0 | 1.000000 | 25.470588 | 11.352941 |
| >20 s | 2 | 2 | 0 | 1.000000 | 29.000000 | 20.000000 |

## Test 2: complete evaluation and ground-truth comparison

Reference **73 rallies**, predictions **75**; TP/FP/FN **68/7/5**. Precision **90.667%**, recall **93.151%**, F1 **91.892%**. Matched mean IoU **0.848135**. The ground-truth benchmark for every table in this primary section is [Test2_Full_rally.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test2_Full/Test2_Full_rally.csv).

| Input / execution binding | Value |
|---|---|
| Decoded frames | 29296 |
| FPS | 30.000000 |
| Video duration seconds | 976.533333 |
| Canonical dimensions | 1280 × 720 |
| Source SHA256 | 4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a |
| Proxy SHA256 | 2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd |
| Prediction SHA256 | 80bf7e4f56c907cdcade3b8baca56c7753d7bff233b1b39a19c508376724d311 |
| Ground-truth SHA256 | 33a671408f26f9aba0824d78c1fcc257607782c854bbd0dfd4981dc3cadc2387 |
| Coarse reference SHA256 | 03dcb642c93f94ff03ce8e0e86b60b850cc0a78cd8fbad8c38360245d209bd74 |
| Session | UPLOADTEST2 |
| Actual completion mode | independent_recovery |
| Original parent receipt status | partial_or_failed |
| Full source/proxy PTS matches | 29296 |
| Scene probe pixel hashes verified | 38 |
| Verified saved files / logical bytes | 18 / 5329494 |
| Read-only record | [saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test2_historical) |

### Primary metric scores versus the ground-truth ideal

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 73 | 73 | 0 |
| Prediction count | 73 | 75 | 2 |
| TP / matched | 73 | 68 | -5 |
| FP | 0 | 7 | 7 |
| FN / missed | 0 | 5 | 5 |
| precision | 1 | 0.906667 | -0.093333 |
| recall | 1 | 0.931507 | -0.068493 |
| f1 | 1 | 0.918919 | -0.081081 |
| Mean matched IoU | 1 | 0.848135 | -0.151865 |
| Median matched IoU | 1 | 0.881085 | -0.118915 |
| Minimum matched IoU | 1 | 0.504087 | -0.495913 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 79.411765 |
| 0.9 | 100 | 45.588235 |
| 0.95 | 100 | 27.941176 |

A GT self-comparison has TP=N, FP=FN=0, precision/recall/F1=1, IoU=1 and every timing/duration error=0. This is the reference ideal, not a separately executed baseline model. The signed count difference alone is insufficient: false positives and misses can cancel.

### Boundary and duration errors versus zero-error ground truth

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.882353 | 11.500000 | 40.330984 | 167.000000 | 73.000000 | 19.088235 | 6.500000 |
| end_frame | 21.161765 | 10.500000 | 48.021901 | 343.000000 | 45.400000 | -9.132353 | -2.000000 |
| start_time_sec | 0.796078 | 0.383333 | 1.344366 | 5.566667 | 2.433333 | 0.636275 | 0.216667 |
| end_time_sec | 0.705392 | 0.350000 | 1.600730 | 11.433333 | 1.513333 | -0.304412 | -0.066667 |
| duration_sec | 1.302451 | 0.633333 | 2.259934 | 12.700000 | 3.010000 | -0.940686 | -0.333333 |

| Additional saved statistic | Value | Ground-truth ideal |
|---|---|---|
| Start P95 \|error\| frames | 83.600000 | 0 |
| End P95 \|error\| frames | 58.650000 | 0 |
| Duration mae frames | 39.073529 | 0 |
| Duration rmse frames | 67.798035 | 0 |
| Duration signed_bias frames | -28.220588 | 0 |

All error statistics above condition on eligible matched rallies. A positive start error is a late start; a negative start error is early. A positive end error is a late end; a negative end error is premature. Duration error is prediction minus GT. All 30 FPS frame errors convert by dividing by30; full signed/absolute per-rally values appear below. Misses have no invented zero error.

### Boundary tolerance scores

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 10 | 68 | 14.706% | 73 | 13.699% | 100% |
| start | 3 | 0.100000 | 18 | 68 | 26.471% | 73 | 24.658% | 100% |
| start | 5 | 0.166667 | 24 | 68 | 35.294% | 73 | 32.877% | 100% |
| start | 10 | 0.333333 | 33 | 68 | 48.529% | 73 | 45.205% | 100% |
| start | 15 | 0.500000 | 40 | 68 | 58.824% | 73 | 54.795% | 100% |
| start | 30 | 1.000000 | 52 | 68 | 76.471% | 73 | 71.233% | 100% |
| end | 1 | 0.033333 | 9 | 68 | 13.235% | 73 | 12.329% | 100% |
| end | 3 | 0.100000 | 15 | 68 | 22.059% | 73 | 20.548% | 100% |
| end | 5 | 0.166667 | 24 | 68 | 35.294% | 73 | 32.877% | 100% |
| end | 10 | 0.333333 | 34 | 68 | 50.000% | 73 | 46.575% | 100% |
| end | 15 | 0.500000 | 42 | 68 | 61.765% | 73 | 57.534% | 100% |
| end | 30 | 1.000000 | 56 | 68 | 82.353% | 73 | 76.712% | 100% |

### All saved error distributions

| Distribution / units | N | Mean | Median | Minimum | Maximum | P90 | P95 | Ideal |
|---|---|---|---|---|---|---|---|---|
| matched_iou | 68 | 0.848135 | 0.881085 | 0.504087 | 0.995542 | 0.975700 | 0.984578 | 1 |
| start_signed_frames | 68 | 19.088235 | 6.500000 | -41.000000 | 167.000000 | 73.000000 | 83.600000 | 0 |
| start_absolute_frames | 68 | 23.882353 | 11.500000 | 0.000000 | 167.000000 | 73.000000 | 83.600000 | 0 |
| end_signed_frames | 68 | -9.132353 | -2.000000 | -343.000000 | 59.000000 | 18.200000 | 34.650000 | 0 |
| end_absolute_frames | 68 | 21.161765 | 10.500000 | 1.000000 | 343.000000 | 45.400000 | 58.650000 | 0 |
| duration_signed_frames | 68 | -28.220588 | -10.000000 | -381.000000 | 74.000000 | 17.600000 | 33.900000 | 0 |
| duration_absolute_frames | 68 | 39.073529 | 19.000000 | 0.000000 | 381.000000 | 90.300000 | 124.700000 | 0 |
| duration_signed_seconds | 68 | -0.940686 | -0.333333 | -12.700000 | 2.466667 | 0.586667 | 1.130000 | 0 |

### Misses, extras, overlap topology and failure review

| Diagnostic | Observed | GT ideal / interpretation |
|---|---|---|
| Missed GT IDs | [31,39,56,58,63] | [] |
| Unmatched prediction IDs | [11,32,40,41,47,58,71] | [] |
| No-overlap missed GT IDs | [56,58,63] | [] |
| Predictions without any GT overlap | [47] | [] |
| Possible split GT IDs | [11,39,42,55,69] | Geometric overlap candidates; not adjudicated semantic splits |
| Possible merge prediction IDs | [43] | Geometric overlap candidates; not adjudicated semantic merges |
| Significant failure records | 39 | Unmatched or \|boundary error\|>30frames or IoU<0.75 |
| early_start_gt_ids | [7,21,22,23,26,30,33,40,50,54,57] | Direction/weak-overlap inventory, not a physical cause |
| late_start_gt_ids | [1,2,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,24,25,27,28,29,32,34,35,37,38,41,42,43,44,45,46,48,49,51,52,53,55,59,60,61,62,64,65,66,67,68,69,70,71,72,73] | Direction/weak-overlap inventory, not a physical cause |
| premature_end_gt_ids | [3,5,7,8,10,13,14,16,17,19,22,23,24,25,27,29,30,32,33,35,42,44,45,46,47,48,49,50,51,52,55,57,59,60,61,65,66,67,69,70] | Direction/weak-overlap inventory, not a physical cause |
| late_end_gt_ids | [1,2,4,6,9,11,12,15,18,20,21,26,28,34,36,37,38,40,41,43,53,54,62,64,68,71,72,73] | Direction/weak-overlap inventory, not a physical cause |
| weak_iou_gt_ids | [6,7,8,11,24,32,34,37,41,42,48,61,67,69] | Direction/weak-overlap inventory, not a physical cause |

| Inventory validity | Ground truth | Predictions |
|---|---|---|
| count | 73 | 75 |
| duplicate_row_pairs | [] | [] |
| positive_overlap_row_pairs | [] | [] |
| adjacent_row_pairs | [] | [] |
| out_of_range_rows | [] | [] |
| out_of_order_rows | [] | [] |

| False detection P ID | Start frame | End frame | Start seconds | End seconds | Duration seconds | Positive-overlap GT IDs |
|---|---|---|---|---|---|---|
| 11 | 3877 | 3936 | 129.233333 | 131.200000 | 1.966667 | [11] |
| 32 | 11715 | 11751 | 390.500000 | 391.700000 | 1.200000 | [31] |
| 40 | 13462 | 13533 | 448.733333 | 451.100000 | 2.366667 | [39] |
| 41 | 13579 | 13718 | 452.633333 | 457.266667 | 4.633333 | [39] |
| 47 | 15451 | 15609 | 515.033333 | 520.300000 | 5.266667 | [] |
| 58 | 20114 | 20175 | 670.466667 | 672.500000 | 2.033333 | [55] |
| 71 | 27349 | 27649 | 911.633333 | 921.633333 | 10.000000 | [69] |

| Largest matched boundary cases | P ID | GT start/end frames | Pred start/end frames | Δstart frames | Δend frames | IoU |
|---|---|---|---|---|---|---|
| 69 | 70 | 26616–27668 | 26654–27325 | 38 | -343 | 0.637833 |
| 11 | 12 | 3863–4215 | 4030–4230 | 167 | 15 | 0.504087 |
| 55 | 59 | 20061–20884 | 20198–20883 | 137 | -1 | 0.832321 |
| 67 | 68 | 25520–26061 | 25629–26018 | 109 | -43 | 0.719039 |
| 5 | 5 | 1955–2410 | 2040–2404 | 85 | -6 | 0.800000 |

Of 5 unmatched reference intervals, 3 have no positive overlap with any prediction; 2 have some overlap but fail the one-to-one IoU eligibility/assignment. This separates absence of overlap from insufficient interval agreement without inventing a causal diagnosis.

### Every GT rally compared directly with its assigned prediction: frames

G IDs are one-based CSV row IDs in the primary rally reference. P IDs are one-based rows in the preserved prediction CSV. C IDs refer to the separate coarse table, linked only by the same IoU-based temporal crosswalk. “—” denotes unavailable/unmatched, not zero.

| G | P | GT start f | GT end f | Pred start f | Pred end f | Δstart f | \|Δstart\| f | Δend f | \|Δend\| f | IoU | Status | Coarse C row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 53 | 341 | 82 | 342 | 29 | 29 | 1 | 1 | 0.896194 | matched | 1 |
| 2 | 2 | 374 | 632 | 377 | 647 | 3 | 3 | 15 | 15 | 0.934066 | matched | 2 |
| 3 | 3 | 807 | 1040 | 809 | 1039 | 2 | 2 | -1 | 1 | 0.987124 | matched | 3 |
| 4 | 4 | 1159 | 1796 | 1162 | 1800 | 3 | 3 | 4 | 4 | 0.989080 | matched | 4 |
| 5 | 5 | 1955 | 2410 | 2040 | 2404 | 85 | 85 | -6 | 6 | 0.800000 | matched | 5 |
| 6 | 6 | 2477 | 2621 | 2492 | 2655 | 15 | 15 | 34 | 34 | 0.724719 | matched | 6 |
| 7 | 7 | 2811 | 2870 | 2790 | 2866 | -21 | 21 | -4 | 4 | 0.687500 | matched | 7 |
| 8 | 8 | 2927 | 3157 | 2946 | 3099 | 19 | 19 | -58 | 58 | 0.665217 | matched | 8 |
| 9 | 9 | 3189 | 3365 | 3194 | 3366 | 5 | 5 | 1 | 1 | 0.966102 | matched | 9 |
| 10 | 10 | 3428 | 3839 | 3430 | 3823 | 2 | 2 | -16 | 16 | 0.956204 | matched | 10 |
| 11 | 12 | 3863 | 4215 | 4030 | 4230 | 167 | 167 | 15 | 15 | 0.504087 | matched | 12 |
| 12 | 13 | 4270 | 4532 | 4285 | 4549 | 15 | 15 | 17 | 17 | 0.885305 | matched | 13 |
| 13 | 14 | 4606 | 4782 | 4633 | 4769 | 27 | 27 | -13 | 13 | 0.772727 | matched | 14 |
| 14 | 15 | 4854 | 5185 | 4882 | 5131 | 28 | 28 | -54 | 54 | 0.752266 | matched | 15 |
| 15 | 16 | 5221 | 5438 | 5224 | 5446 | 3 | 3 | 8 | 8 | 0.951111 | matched | 16 |
| 16 | 17 | 5535 | 5910 | 5547 | 5895 | 12 | 12 | -15 | 15 | 0.928000 | matched | 17 |
| 17 | 18 | 5971 | 6095 | 5974 | 6082 | 3 | 3 | -13 | 13 | 0.870968 | matched | 18 |
| 18 | 19 | 6186 | 6292 | 6187 | 6293 | 1 | 1 | 1 | 1 | 0.981308 | matched | 19 |
| 19 | 20 | 6439 | 6681 | 6445 | 6680 | 6 | 6 | -1 | 1 | 0.971074 | matched | 20 |
| 20 | 21 | 6790 | 6986 | 6797 | 6990 | 7 | 7 | 4 | 4 | 0.945000 | matched | 21 |
| 21 | 22 | 7029 | 7147 | 7028 | 7154 | -1 | 1 | 7 | 7 | 0.936508 | matched | 22 |
| 22 | 23 | 7220 | 7600 | 7217 | 7597 | -3 | 3 | -3 | 3 | 0.984334 | matched | 23 |
| 23 | 24 | 7664 | 8541 | 7659 | 8517 | -5 | 5 | -24 | 24 | 0.967120 | matched | 24 |
| 24 | 25 | 8593 | 8748 | 8627 | 8734 | 34 | 34 | -14 | 14 | 0.690323 | matched | 25 |
| 25 | 26 | 8772 | 9445 | 8773 | 9443 | 1 | 1 | -2 | 2 | 0.995542 | matched | 26 |
| 26 | 27 | 9550 | 10194 | 9545 | 10199 | -5 | 5 | 5 | 5 | 0.984709 | matched | 27 |
| 27 | 28 | 10353 | 10540 | 10381 | 10539 | 28 | 28 | -1 | 1 | 0.844920 | matched | 29 |
| 28 | 29 | 10968 | 11028 | 10976 | 11036 | 8 | 8 | 8 | 8 | 0.764706 | matched | 30 |
| 29 | 30 | 11075 | 11295 | 11097 | 11285 | 22 | 22 | -10 | 10 | 0.854545 | matched | 31 |
| 30 | 31 | 11394 | 11661 | 11353 | 11657 | -41 | 41 | -4 | 4 | 0.853896 | matched | 32 |
| 31 | — | 11714 | 11830 | — | — | — | — | — | — | — | missed | — |
| 32 | 33 | 11860 | 11942 | 11873 | 11926 | 13 | 13 | -16 | 16 | 0.646341 | matched | 34 |
| 33 | 34 | 11967 | 12076 | 11958 | 12059 | -9 | 9 | -17 | 17 | 0.779661 | matched | 35 |
| 34 | 35 | 12173 | 12230 | 12174 | 12268 | 1 | 1 | 38 | 38 | 0.589474 | matched | — |
| 35 | 36 | 12268 | 12559 | 12310 | 12555 | 42 | 42 | -4 | 4 | 0.841924 | matched | 37 |
| 36 | 37 | 12639 | 12735 | 12639 | 12751 | 0 | 0 | 16 | 16 | 0.857143 | matched | 38 |
| 37 | 38 | 12813 | 13037 | 12859 | 13051 | 46 | 46 | 14 | 14 | 0.747899 | matched | 39 |
| 38 | 39 | 13162 | 13362 | 13163 | 13366 | 1 | 1 | 4 | 4 | 0.975490 | matched | 40 |
| 39 | — | 13427 | 13707 | — | — | — | — | — | — | — | missed | 41 |
| 40 | 42 | 13857 | 14058 | 13856 | 14079 | -1 | 1 | 21 | 21 | 0.901345 | matched | 42 |
| 41 | 43 | 14125 | 14251 | 14131 | 14293 | 6 | 6 | 42 | 42 | 0.714286 | matched | — |
| 42 | 44 | 14280 | 14467 | 14320 | 14442 | 40 | 40 | -25 | 25 | 0.652406 | matched | — |
| 43 | 45 | 14524 | 14847 | 14533 | 14852 | 9 | 9 | 5 | 5 | 0.957317 | matched | 45 |
| 44 | 46 | 14885 | 15386 | 14966 | 15377 | 81 | 81 | -9 | 9 | 0.820359 | matched | 46 |
| 45 | 48 | 15675 | 16089 | 15681 | 16059 | 6 | 6 | -30 | 30 | 0.913043 | matched | — |
| 46 | 49 | 16170 | 16616 | 16186 | 16532 | 16 | 16 | -84 | 84 | 0.775785 | matched | 49 |
| 47 | 50 | 16659 | 17229 | 16659 | 17202 | 0 | 0 | -27 | 27 | 0.952632 | matched | 50 |
| 48 | 51 | 17293 | 17435 | 17299 | 17373 | 6 | 6 | -62 | 62 | 0.521127 | matched | — |
| 49 | 52 | 17480 | 17664 | 17485 | 17662 | 5 | 5 | -2 | 2 | 0.961957 | matched | 52 |
| 50 | 53 | 17700 | 17946 | 17684 | 17939 | -16 | 16 | -7 | 7 | 0.912214 | matched | 53 |
| 51 | 54 | 18120 | 18337 | 18131 | 18331 | 11 | 11 | -6 | 6 | 0.921659 | matched | 54 |
| 52 | 55 | 18522 | 18969 | 18595 | 18947 | 73 | 73 | -22 | 22 | 0.787472 | matched | 55 |
| 53 | 56 | 19021 | 19472 | 19050 | 19531 | 29 | 29 | 59 | 59 | 0.827451 | matched | 56 |
| 54 | 57 | 19606 | 20020 | 19567 | 20055 | -39 | 39 | 35 | 35 | 0.848361 | matched | 57 |
| 55 | 59 | 20061 | 20884 | 20198 | 20883 | 137 | 137 | -1 | 1 | 0.832321 | matched | 58 |
| 56 | — | 20947 | 21045 | — | — | — | — | — | — | — | missed | 59 |
| 57 | 60 | 21388 | 21634 | 21366 | 21623 | -22 | 22 | -11 | 11 | 0.876866 | matched | 60 |
| 58 | — | 21736 | 21809 | — | — | — | — | — | — | — | missed | — |
| 59 | 61 | 22098 | 22418 | 22111 | 22367 | 13 | 13 | -51 | 51 | 0.800000 | matched | 61 |
| 60 | 62 | 22652 | 22912 | 22656 | 22904 | 4 | 4 | -8 | 8 | 0.953846 | matched | 62 |
| 61 | 63 | 23025 | 23222 | 23098 | 23219 | 73 | 73 | -3 | 3 | 0.614213 | matched | 63 |
| 62 | 64 | 23284 | 23656 | 23289 | 23672 | 5 | 5 | 16 | 16 | 0.945876 | matched | 64 |
| 63 | — | 23879 | 24012 | — | — | — | — | — | — | — | missed | 65 |
| 64 | 65 | 24114 | 24327 | 24117 | 24330 | 3 | 3 | 3 | 3 | 0.972222 | matched | 66 |
| 65 | 66 | 24681 | 25173 | 24711 | 25156 | 30 | 30 | -17 | 17 | 0.904472 | matched | 67 |
| 66 | 67 | 25208 | 25429 | 25223 | 25427 | 15 | 15 | -2 | 2 | 0.923077 | matched | 68 |
| 67 | 68 | 25520 | 26061 | 25629 | 26018 | 109 | 109 | -43 | 43 | 0.719039 | matched | 69 |
| 68 | 69 | 26279 | 26445 | 26280 | 26455 | 1 | 1 | 10 | 10 | 0.937500 | matched | 70 |
| 69 | 70 | 26616 | 27668 | 26654 | 27325 | 38 | 38 | -343 | 343 | 0.637833 | matched | 71 |
| 70 | 72 | 27808 | 27892 | 27809 | 27891 | 1 | 1 | -1 | 1 | 0.976190 | matched | 72 |
| 71 | 73 | 27927 | 28667 | 28002 | 28671 | 75 | 75 | 4 | 4 | 0.893817 | matched | 73 |
| 72 | 74 | 28694 | 28937 | 28734 | 28958 | 40 | 40 | 21 | 21 | 0.768939 | matched | 74 |
| 73 | 75 | 29032 | 29273 | 29039 | 29274 | 7 | 7 | 1 | 1 | 0.966942 | matched | 75 |

### Every GT rally compared directly: timestamps and durations

| G | GT start s | GT end s | Pred start s | Pred end s | GT duration s | Pred duration s | Δstart s | \|Δstart\| s | Δend s | \|Δend\| s | Δduration s | \|Δduration\| s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.766667 | 11.366667 | 2.733333 | 11.400000 | 9.600000 | 8.666667 | 0.966667 | 0.966667 | 0.033333 | 0.033333 | -0.933333 | 0.933333 |
| 2 | 12.466667 | 21.066667 | 12.566667 | 21.566667 | 8.600000 | 9.000000 | 0.100000 | 0.100000 | 0.500000 | 0.500000 | 0.400000 | 0.400000 |
| 3 | 26.900000 | 34.666667 | 26.966667 | 34.633333 | 7.766667 | 7.666667 | 0.066667 | 0.066667 | -0.033333 | 0.033333 | -0.100000 | 0.100000 |
| 4 | 38.633333 | 59.866667 | 38.733333 | 60.000000 | 21.233333 | 21.266667 | 0.100000 | 0.100000 | 0.133333 | 0.133333 | 0.033333 | 0.033333 |
| 5 | 65.166667 | 80.333333 | 68.000000 | 80.133333 | 15.166667 | 12.133333 | 2.833333 | 2.833333 | -0.200000 | 0.200000 | -3.033333 | 3.033333 |
| 6 | 82.566667 | 87.366667 | 83.066667 | 88.500000 | 4.800000 | 5.433333 | 0.500000 | 0.500000 | 1.133333 | 1.133333 | 0.633333 | 0.633333 |
| 7 | 93.700000 | 95.666667 | 93.000000 | 95.533333 | 1.966667 | 2.533333 | -0.700000 | 0.700000 | -0.133333 | 0.133333 | 0.566667 | 0.566667 |
| 8 | 97.566667 | 105.233333 | 98.200000 | 103.300000 | 7.666667 | 5.100000 | 0.633333 | 0.633333 | -1.933333 | 1.933333 | -2.566667 | 2.566667 |
| 9 | 106.300000 | 112.166667 | 106.466667 | 112.200000 | 5.866667 | 5.733333 | 0.166667 | 0.166667 | 0.033333 | 0.033333 | -0.133333 | 0.133333 |
| 10 | 114.266667 | 127.966667 | 114.333333 | 127.433333 | 13.700000 | 13.100000 | 0.066667 | 0.066667 | -0.533333 | 0.533333 | -0.600000 | 0.600000 |
| 11 | 128.766667 | 140.500000 | 134.333333 | 141.000000 | 11.733333 | 6.666667 | 5.566667 | 5.566667 | 0.500000 | 0.500000 | -5.066667 | 5.066667 |
| 12 | 142.333333 | 151.066667 | 142.833333 | 151.633333 | 8.733333 | 8.800000 | 0.500000 | 0.500000 | 0.566667 | 0.566667 | 0.066667 | 0.066667 |
| 13 | 153.533333 | 159.400000 | 154.433333 | 158.966667 | 5.866667 | 4.533333 | 0.900000 | 0.900000 | -0.433333 | 0.433333 | -1.333333 | 1.333333 |
| 14 | 161.800000 | 172.833333 | 162.733333 | 171.033333 | 11.033333 | 8.300000 | 0.933333 | 0.933333 | -1.800000 | 1.800000 | -2.733333 | 2.733333 |
| 15 | 174.033333 | 181.266667 | 174.133333 | 181.533333 | 7.233333 | 7.400000 | 0.100000 | 0.100000 | 0.266667 | 0.266667 | 0.166667 | 0.166667 |
| 16 | 184.500000 | 197.000000 | 184.900000 | 196.500000 | 12.500000 | 11.600000 | 0.400000 | 0.400000 | -0.500000 | 0.500000 | -0.900000 | 0.900000 |
| 17 | 199.033333 | 203.166667 | 199.133333 | 202.733333 | 4.133333 | 3.600000 | 0.100000 | 0.100000 | -0.433333 | 0.433333 | -0.533333 | 0.533333 |
| 18 | 206.200000 | 209.733333 | 206.233333 | 209.766667 | 3.533333 | 3.533333 | 0.033333 | 0.033333 | 0.033333 | 0.033333 | 0.000000 | 0.000000 |
| 19 | 214.633333 | 222.700000 | 214.833333 | 222.666667 | 8.066667 | 7.833333 | 0.200000 | 0.200000 | -0.033333 | 0.033333 | -0.233333 | 0.233333 |
| 20 | 226.333333 | 232.866667 | 226.566667 | 233.000000 | 6.533333 | 6.433333 | 0.233333 | 0.233333 | 0.133333 | 0.133333 | -0.100000 | 0.100000 |
| 21 | 234.300000 | 238.233333 | 234.266667 | 238.466667 | 3.933333 | 4.200000 | -0.033333 | 0.033333 | 0.233333 | 0.233333 | 0.266667 | 0.266667 |
| 22 | 240.666667 | 253.333333 | 240.566667 | 253.233333 | 12.666667 | 12.666667 | -0.100000 | 0.100000 | -0.100000 | 0.100000 | -0.000000 | 0.000000 |
| 23 | 255.466667 | 284.700000 | 255.300000 | 283.900000 | 29.233333 | 28.600000 | -0.166667 | 0.166667 | -0.800000 | 0.800000 | -0.633333 | 0.633333 |
| 24 | 286.433333 | 291.600000 | 287.566667 | 291.133333 | 5.166667 | 3.566667 | 1.133333 | 1.133333 | -0.466667 | 0.466667 | -1.600000 | 1.600000 |
| 25 | 292.400000 | 314.833333 | 292.433333 | 314.766667 | 22.433333 | 22.333333 | 0.033333 | 0.033333 | -0.066667 | 0.066667 | -0.100000 | 0.100000 |
| 26 | 318.333333 | 339.800000 | 318.166667 | 339.966667 | 21.466667 | 21.800000 | -0.166667 | 0.166667 | 0.166667 | 0.166667 | 0.333333 | 0.333333 |
| 27 | 345.100000 | 351.333333 | 346.033333 | 351.300000 | 6.233333 | 5.266667 | 0.933333 | 0.933333 | -0.033333 | 0.033333 | -0.966667 | 0.966667 |
| 28 | 365.600000 | 367.600000 | 365.866667 | 367.866667 | 2.000000 | 2.000000 | 0.266667 | 0.266667 | 0.266667 | 0.266667 | 0.000000 | 0.000000 |
| 29 | 369.166667 | 376.500000 | 369.900000 | 376.166667 | 7.333333 | 6.266667 | 0.733333 | 0.733333 | -0.333333 | 0.333333 | -1.066667 | 1.066667 |
| 30 | 379.800000 | 388.700000 | 378.433333 | 388.566667 | 8.900000 | 10.133333 | -1.366667 | 1.366667 | -0.133333 | 0.133333 | 1.233333 | 1.233333 |
| 31 | 390.466667 | 394.333333 | — | — | 3.866667 | — | — | — | — | — | — | — |
| 32 | 395.333333 | 398.066667 | 395.766667 | 397.533333 | 2.733333 | 1.766667 | 0.433333 | 0.433333 | -0.533333 | 0.533333 | -0.966667 | 0.966667 |
| 33 | 398.900000 | 402.533333 | 398.600000 | 401.966667 | 3.633333 | 3.366667 | -0.300000 | 0.300000 | -0.566667 | 0.566667 | -0.266667 | 0.266667 |
| 34 | 405.766667 | 407.666667 | 405.800000 | 408.933333 | 1.900000 | 3.133333 | 0.033333 | 0.033333 | 1.266667 | 1.266667 | 1.233333 | 1.233333 |
| 35 | 408.933333 | 418.633333 | 410.333333 | 418.500000 | 9.700000 | 8.166667 | 1.400000 | 1.400000 | -0.133333 | 0.133333 | -1.533333 | 1.533333 |
| 36 | 421.300000 | 424.500000 | 421.300000 | 425.033333 | 3.200000 | 3.733333 | 0.000000 | 0.000000 | 0.533333 | 0.533333 | 0.533333 | 0.533333 |
| 37 | 427.100000 | 434.566667 | 428.633333 | 435.033333 | 7.466667 | 6.400000 | 1.533333 | 1.533333 | 0.466667 | 0.466667 | -1.066667 | 1.066667 |
| 38 | 438.733333 | 445.400000 | 438.766667 | 445.533333 | 6.666667 | 6.766667 | 0.033333 | 0.033333 | 0.133333 | 0.133333 | 0.100000 | 0.100000 |
| 39 | 447.566667 | 456.900000 | — | — | 9.333333 | — | — | — | — | — | — | — |
| 40 | 461.900000 | 468.600000 | 461.866667 | 469.300000 | 6.700000 | 7.433333 | -0.033333 | 0.033333 | 0.700000 | 0.700000 | 0.733333 | 0.733333 |
| 41 | 470.833333 | 475.033333 | 471.033333 | 476.433333 | 4.200000 | 5.400000 | 0.200000 | 0.200000 | 1.400000 | 1.400000 | 1.200000 | 1.200000 |
| 42 | 476.000000 | 482.233333 | 477.333333 | 481.400000 | 6.233333 | 4.066667 | 1.333333 | 1.333333 | -0.833333 | 0.833333 | -2.166667 | 2.166667 |
| 43 | 484.133333 | 494.900000 | 484.433333 | 495.066667 | 10.766667 | 10.633333 | 0.300000 | 0.300000 | 0.166667 | 0.166667 | -0.133333 | 0.133333 |
| 44 | 496.166667 | 512.866667 | 498.866667 | 512.566667 | 16.700000 | 13.700000 | 2.700000 | 2.700000 | -0.300000 | 0.300000 | -3.000000 | 3.000000 |
| 45 | 522.500000 | 536.300000 | 522.700000 | 535.300000 | 13.800000 | 12.600000 | 0.200000 | 0.200000 | -1.000000 | 1.000000 | -1.200000 | 1.200000 |
| 46 | 539.000000 | 553.866667 | 539.533333 | 551.066667 | 14.866667 | 11.533333 | 0.533333 | 0.533333 | -2.800000 | 2.800000 | -3.333333 | 3.333333 |
| 47 | 555.300000 | 574.300000 | 555.300000 | 573.400000 | 19.000000 | 18.100000 | 0.000000 | 0.000000 | -0.900000 | 0.900000 | -0.900000 | 0.900000 |
| 48 | 576.433333 | 581.166667 | 576.633333 | 579.100000 | 4.733333 | 2.466667 | 0.200000 | 0.200000 | -2.066667 | 2.066667 | -2.266667 | 2.266667 |
| 49 | 582.666667 | 588.800000 | 582.833333 | 588.733333 | 6.133333 | 5.900000 | 0.166667 | 0.166667 | -0.066667 | 0.066667 | -0.233333 | 0.233333 |
| 50 | 590.000000 | 598.200000 | 589.466667 | 597.966667 | 8.200000 | 8.500000 | -0.533333 | 0.533333 | -0.233333 | 0.233333 | 0.300000 | 0.300000 |
| 51 | 604.000000 | 611.233333 | 604.366667 | 611.033333 | 7.233333 | 6.666667 | 0.366667 | 0.366667 | -0.200000 | 0.200000 | -0.566667 | 0.566667 |
| 52 | 617.400000 | 632.300000 | 619.833333 | 631.566667 | 14.900000 | 11.733333 | 2.433333 | 2.433333 | -0.733333 | 0.733333 | -3.166667 | 3.166667 |
| 53 | 634.033333 | 649.066667 | 635.000000 | 651.033333 | 15.033333 | 16.033333 | 0.966667 | 0.966667 | 1.966667 | 1.966667 | 1.000000 | 1.000000 |
| 54 | 653.533333 | 667.333333 | 652.233333 | 668.500000 | 13.800000 | 16.266667 | -1.300000 | 1.300000 | 1.166667 | 1.166667 | 2.466667 | 2.466667 |
| 55 | 668.700000 | 696.133333 | 673.266667 | 696.100000 | 27.433333 | 22.833333 | 4.566667 | 4.566667 | -0.033333 | 0.033333 | -4.600000 | 4.600000 |
| 56 | 698.233333 | 701.500000 | — | — | 3.266667 | — | — | — | — | — | — | — |
| 57 | 712.933333 | 721.133333 | 712.200000 | 720.766667 | 8.200000 | 8.566667 | -0.733333 | 0.733333 | -0.366667 | 0.366667 | 0.366667 | 0.366667 |
| 58 | 724.533333 | 726.966667 | — | — | 2.433333 | — | — | — | — | — | — | — |
| 59 | 736.600000 | 747.266667 | 737.033333 | 745.566667 | 10.666667 | 8.533333 | 0.433333 | 0.433333 | -1.700000 | 1.700000 | -2.133333 | 2.133333 |
| 60 | 755.066667 | 763.733333 | 755.200000 | 763.466667 | 8.666667 | 8.266667 | 0.133333 | 0.133333 | -0.266667 | 0.266667 | -0.400000 | 0.400000 |
| 61 | 767.500000 | 774.066667 | 769.933333 | 773.966667 | 6.566667 | 4.033333 | 2.433333 | 2.433333 | -0.100000 | 0.100000 | -2.533333 | 2.533333 |
| 62 | 776.133333 | 788.533333 | 776.300000 | 789.066667 | 12.400000 | 12.766667 | 0.166667 | 0.166667 | 0.533333 | 0.533333 | 0.366667 | 0.366667 |
| 63 | 795.966667 | 800.400000 | — | — | 4.433333 | — | — | — | — | — | — | — |
| 64 | 803.800000 | 810.900000 | 803.900000 | 811.000000 | 7.100000 | 7.100000 | 0.100000 | 0.100000 | 0.100000 | 0.100000 | 0.000000 | 0.000000 |
| 65 | 822.700000 | 839.100000 | 823.700000 | 838.533333 | 16.400000 | 14.833333 | 1.000000 | 1.000000 | -0.566667 | 0.566667 | -1.566667 | 1.566667 |
| 66 | 840.266667 | 847.633333 | 840.766667 | 847.566667 | 7.366667 | 6.800000 | 0.500000 | 0.500000 | -0.066667 | 0.066667 | -0.566667 | 0.566667 |
| 67 | 850.666667 | 868.700000 | 854.300000 | 867.266667 | 18.033333 | 12.966667 | 3.633333 | 3.633333 | -1.433333 | 1.433333 | -5.066667 | 5.066667 |
| 68 | 875.966667 | 881.500000 | 876.000000 | 881.833333 | 5.533333 | 5.833333 | 0.033333 | 0.033333 | 0.333333 | 0.333333 | 0.300000 | 0.300000 |
| 69 | 887.200000 | 922.266667 | 888.466667 | 910.833333 | 35.066667 | 22.366667 | 1.266667 | 1.266667 | -11.433333 | 11.433333 | -12.700000 | 12.700000 |
| 70 | 926.933333 | 929.733333 | 926.966667 | 929.700000 | 2.800000 | 2.733333 | 0.033333 | 0.033333 | -0.033333 | 0.033333 | -0.066667 | 0.066667 |
| 71 | 930.900000 | 955.566667 | 933.400000 | 955.700000 | 24.666667 | 22.300000 | 2.500000 | 2.500000 | 0.133333 | 0.133333 | -2.366667 | 2.366667 |
| 72 | 956.466667 | 964.566667 | 957.800000 | 965.266667 | 8.100000 | 7.466667 | 1.333333 | 1.333333 | 0.700000 | 0.700000 | -0.633333 | 0.633333 |
| 73 | 967.733333 | 975.766667 | 967.966667 | 975.800000 | 8.033333 | 7.833333 | 0.233333 | 0.233333 | 0.033333 | 0.033333 | -0.200000 | 0.200000 |

### Secondary coarse/outcome annotations: full supplied baseline and comparison

[Test2_Full.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test2_Full/Test2_Full.csv) contains **75 data rows**, **75 nonblank intervals**, blank row IDs **[]**. This separate reference differs from the 73-interval primary timing table. The same unchanged predictions and matcher give secondary precision **92.000%**, recall **92.000%**, F1 **92.000%**; this reference-sensitivity analysis does not replace the primary benchmark. No labels, times or predictions were fitted or repaired.

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 75 | 75 | 0 |
| Prediction count | 75 | 75 | 0 |
| TP / matched | 75 | 69 | -6 |
| FP | 0 | 6 | 6 |
| FN / missed | 0 | 6 | 6 |
| precision | 1 | 0.920000 | -0.080000 |
| recall | 1 | 0.920000 | -0.080000 |
| f1 | 1 | 0.920000 | -0.080000 |
| Mean matched IoU | 1 | 0.833215 | -0.166785 |
| Median matched IoU | 1 | 0.871009 | -0.128991 |
| Minimum matched IoU | 1 | 0.512915 | -0.487085 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 75.362319 |
| 0.9 | 100 | 40.579710 |
| 0.95 | 100 | 15.942029 |

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 24.304348 | 17.000000 | 38.274940 | 197.000000 | 42.800000 | 6.275362 | 11.000000 |
| end_frame | 17.246377 | 9.000000 | 41.064107 | 305.000000 | 34.600000 | -3.855072 | -1.000000 |
| start_time_sec | 0.810145 | 0.566667 | 1.275831 | 6.566667 | 1.426667 | 0.209179 | 0.366667 |
| end_time_sec | 0.574879 | 0.300000 | 1.368804 | 10.166667 | 1.153333 | -0.128502 | -0.033333 |
| duration_sec | 1.096135 | 0.733333 | 1.845179 | 10.633333 | 1.873333 | -0.337681 | -0.466667 |

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 4 | 69 | 5.797% | 75 | 5.333% | 100% |
| start | 3 | 0.100000 | 6 | 69 | 8.696% | 75 | 8.000% | 100% |
| start | 5 | 0.166667 | 10 | 69 | 14.493% | 75 | 13.333% | 100% |
| start | 10 | 0.333333 | 23 | 69 | 33.333% | 75 | 30.667% | 100% |
| start | 15 | 0.500000 | 29 | 69 | 42.029% | 75 | 38.667% | 100% |
| start | 30 | 1.000000 | 58 | 69 | 84.058% | 75 | 77.333% | 100% |
| end | 1 | 0.033333 | 11 | 69 | 15.942% | 75 | 14.667% | 100% |
| end | 3 | 0.100000 | 16 | 69 | 23.188% | 75 | 21.333% | 100% |
| end | 5 | 0.166667 | 21 | 69 | 30.435% | 75 | 28.000% | 100% |
| end | 10 | 0.333333 | 38 | 69 | 55.072% | 75 | 50.667% | 100% |
| end | 15 | 0.500000 | 50 | 69 | 72.464% | 75 | 66.667% | 100% |
| end | 30 | 1.000000 | 61 | 69 | 88.406% | 75 | 81.333% | 100% |

| Cross-reference timing diagnostic | Value |
|---|---|
| Primary-to-coarse eligible matched intervals | 66 |
| Primary intervals unmatched to coarse reference | [31,34,41,42,45,48,58] |
| Coarse rows unmatched to primary reference | [11,28,33,36,43,44,47,48,51] |
| Primary/coarse matched mean IoU | 0.828493 |

| C source row | Supplied start | Supplied end | Supplied winner | Supplied A:B score | Supplied shot / ball_types | Win reason | Lose reason | Matched P | IoU | Δstart s | Δend s | Δduration s | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 00:02 | 00:11 | Player B | 0:1 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 1 | 0.879433 | 0.733333 | 0.400000 | -0.333333 | matched |
| 2 | 00:12 | 00:21 | Player B | 0:2 | Smash | Winner Shot | Opponent Failed to Return | 2 | 0.881533 | 0.566667 | 0.566667 | 0.000000 | matched |
| 3 | 00:30 | 00:36 | Player A | 1:2 | Lob | Opponent Hit the Net | Hit the Net | 3 | 0.512915 | -3.033333 | -1.366667 | 1.666667 | matched |
| 4 | 00:38 | 00:59 | Player A | 2:3 | Smash | Winner Shot | Opponent Failed to Return | 4 | 0.921212 | 0.733333 | 1.000000 | 0.266667 | matched |
| 5 | 01:07 | 01:20 | Player A | 4:5 | Smash | Opponent Out of Bounds | Out of Bounds | 5 | 0.913706 | 1.000000 | 0.133333 | -0.866667 | matched |
| 6 | 01:23 | 01:27 | Player A | 5:5 | Net Shot | Opponent Hit the Net | Hit the Net | 6 | 0.715152 | 0.066667 | 1.500000 | 1.433333 | matched |
| 7 | 01:33 | 01:36 | Player B | 5:6 | Net Shot | Opponent Hit the Net | Hit the Net | 7 | 0.844444 | 0.000000 | -0.466667 | -0.466667 | matched |
| 8 | 01:38 | 01:43 | Player B | 5:6 | Net Shot | Opponent Hit the Net | Hit the Net | 8 | 0.905660 | 0.200000 | 0.300000 | 0.100000 | matched |
| 9 | 01:48 | 01:52 | Player A | 7:6 | Smash | Winner Shot | Opponent Failed to Return | 9 | 0.697674 | -1.533333 | 0.200000 | 1.733333 | matched |
| 10 | 01:54 | 02:08 | Player A | 8:7 | Smash | Winner Shot | Opponent Failed to Return | 10 | 0.935714 | 0.333333 | -0.566667 | -0.900000 | matched |
| 11 | 02:09 | 02:12 | Player B | 9:8 | Drive Defense | Opponent Out of Bounds | Out of Bounds | 11 | 0.655556 | 0.233333 | -0.800000 | -1.033333 | matched |
| 12 | 02:13 | 02:21 | Player B | 9:9 | Drive | Opponent Out of Bounds | Out of Bounds | 12 | 0.833333 | 1.333333 | 0.000000 | -1.333333 | matched |
| 13 | 02:22 | 02:31 | Player B | 9:10 | Smash | Winner Shot | Opponent Failed to Return | 13 | 0.847751 | 0.833333 | 0.633333 | -0.200000 | matched |
| 14 | 02:35 | 02:39 | Player B | 9:11 | Lob | Opponent Out of Bounds | Out of Bounds | 14 | 0.868613 | -0.566667 | -0.033333 | 0.533333 | matched |
| 15 | 02:42 | 02:51 | Player B | 9:12 | Lob | Winner Shot | Opponent Failed to Return | 15 | 0.915129 | 0.733333 | 0.033333 | -0.700000 | matched |
| 16 | 02:53 | 03:01 | Player B | 9:13 | Smash | Winner Shot | Opponent Failed to Return | 16 | 0.804688 | 1.133333 | 0.533333 | -0.600000 | matched |
| 17 | 03:05 | 03:17 | Player A | 10:13 | Clear | Opponent Out of Bounds | Out of Bounds | 17 | 0.950413 | -0.100000 | -0.500000 | -0.400000 | matched |
| 18 | 03:19 | 03:23 | Player B | 10:14 | Lob | Opponent Out of Bounds | Out of Bounds | 18 | 0.900000 | 0.133333 | -0.266667 | -0.400000 | matched |
| 19 | 03:25 | 03:30 | Player A | 11:14 | Net Kill | Winner Shot | Opponent Failed to Return | 19 | 0.706667 | 1.233333 | -0.233333 | -1.466667 | matched |
| 20 | 03:34 | 03:43 | Player A | 13:14 | Cross Net Shot | Opponent Hit the Net | Hit the Net | 20 | 0.870370 | 0.833333 | -0.333333 | -1.166667 | matched |
| 21 | 03:46 | 03:53 | Player B | 14:15 | Push Shot | Opponent Out of Bounds | Out of Bounds | 21 | 0.919048 | 0.566667 | 0.000000 | -0.566667 | matched |
| 22 | 03:54 | 03:58 | Player B | 14:16 | Push Shot | Opponent Out of Bounds | Out of Bounds | 22 | 0.835821 | 0.266667 | 0.466667 | 0.200000 | matched |
| 23 | 04:00 | 04:13 | Player B | 14:17 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 23 | 0.939547 | 0.566667 | 0.233333 | -0.333333 | matched |
| 24 | 04:15 | 04:45 | Player A | 15:17 | Net Shot | Opponent Hit the Net | Hit the Net | 24 | 0.953333 | 0.300000 | -1.100000 | -1.400000 | matched |
| 25 | 04:47 | 04:51 | Player B | 15:20 | Smash | Opponent Hit the Net | Hit the Net | 25 | 0.830645 | 0.566667 | 0.133333 | -0.433333 | matched |
| 26 | 04:59 | 05:15 | Player B | 16:21 | Net Kill | Winner Shot | Opponent Failed to Return | 26 | 0.698671 | -6.566667 | -0.233333 | 6.333333 | matched |
| 27 | 05:18 | 05:40 | Player B | 0:1 | Net Kill | Opponent Out of Bounds | Out of Bounds | 27 | 0.990909 | 0.166667 | -0.033333 | -0.200000 | matched |
| 28 | 05:42 | 05:44 | Player B | 0:2 | Long Serve | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 29 | 05:46 | 05:52 | Player B | 0:3 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 28 | 0.877778 | 0.033333 | -0.700000 | -0.733333 | matched |
| 30 | 06:05 | 06:08 | Player B | 0:4 | Net Shot | Opponent Hit the Net | Hit the Net | 29 | 0.666667 | 0.866667 | -0.133333 | -1.000000 | matched |
| 31 | 06:09 | 06:16 | Player B | 0:5 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 30 | 0.851163 | 0.900000 | 0.166667 | -0.733333 | matched |
| 32 | 06:19 | 06:29 | Player B | 1:6 | Slice | Opponent Hit the Net | Hit the Net | 31 | 0.905363 | -0.566667 | -0.433333 | 0.133333 | matched |
| 33 | 06:30 | 06:32 | Player B | 1:8 | Net Shot | Opponent Hit the Net | Hit the Net | 32 | 0.600000 | 0.500000 | -0.300000 | -0.800000 | matched |
| 34 | 06:35 | 06:38 | Player B | 1:9 | Smash | Opponent Out of Bounds | Out of Bounds | 33 | 0.588889 | 0.766667 | -0.466667 | -1.233333 | matched |
| 35 | 06:40 | 06:42 | Player B | 1:10 | Smash | Opponent Out of Bounds | Out of Bounds | 34 | 0.578431 | -1.400000 | -0.033333 | 1.366667 | matched |
| 36 | 06:45 | 06:47 | Player B | 1:12 | Net Shot | Opponent Hit the Net | Hit the Net | — | — | — | — | — | missed |
| 37 | 06:50 | 06:59 | Player B | 1:13 | Smash | Opponent Out of Bounds | Out of Bounds | 36 | 0.907407 | 0.333333 | -0.500000 | -0.833333 | matched |
| 38 | 07:01 | 07:05 | Player A | 3:13 | Block | Opponent Hit the Net | Hit the Net | 37 | 0.917355 | 0.300000 | 0.033333 | -0.266667 | matched |
| 39 | 07:08 | 07:15 | Player B | 3:14 | Cross Net Shot | Opponent Out of Bounds | Out of Bounds | 38 | 0.905213 | 0.633333 | 0.033333 | -0.600000 | matched |
| 40 | 07:18 | 07:26 | Player B | 3:16 | Stick Smash | Opponent Hit the Net | Hit the Net | 39 | 0.845833 | 0.766667 | -0.466667 | -1.233333 | matched |
| 41 | 07:29 | 07:37 | Player A | 4:16 | Smash | Opponent Out of Bounds | Out of Bounds | 41 | 0.528226 | 3.633333 | 0.266667 | -3.366667 | matched |
| 42 | 07:41 | 07:49 | Player B | 4:17 | Lift Shot | Winner Shot | Opponent Failed to Return | 42 | 0.859438 | 0.866667 | 0.300000 | -0.566667 | matched |
| 43 | 07:50 | 07:53 | Player B | 4:18 | Block | Opponent Out of Bounds | Out of Bounds | — | — | — | — | — | missed |
| 44 | 07:57 | 08:00 | Player B | 5:19 | Defensive Slice | Opponent Out of Bounds | Out of Bounds | 44 | 0.606061 | 0.333333 | 1.400000 | 1.066667 | matched |
| 45 | 08:04 | 08:15 | Player B | 0:1 | Push Shot | Opponent Out of Bounds | Out of Bounds | 45 | 0.954819 | 0.433333 | 0.066667 | -0.366667 | matched |
| 46 | 08:19 | 08:33 | Player B | 0:2 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 46 | 0.959906 | -0.133333 | -0.433333 | -0.300000 | matched |
| 47 | 08:37 | 08:40 | Player A | 1:2 | Smash | Winner Shot | Opponent Failed to Return | 47 | 0.569620 | -1.966667 | 0.300000 | 2.266667 | matched |
| 48 | 08:44 | 08:50 | Player A | 2:2 | Smash | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 49 | 08:59 | 09:11 | Player A | 3:2 | Net Kill | Winner Shot | Opponent Failed to Return | 49 | 0.950276 | 0.533333 | 0.066667 | -0.466667 | matched |
| 50 | 09:15 | 09:34 | Player A | 4:4 | Clear | Opponent Out of Bounds | Out of Bounds | 50 | 0.952632 | 0.300000 | -0.600000 | -0.900000 | matched |
| 51 | 09:36 | 09:39 | Player A | 5:4 | Cross Net Shot | Opponent Out of Bounds | Out of Bounds | 51 | 0.763441 | 0.633333 | 0.100000 | -0.533333 | matched |
| 52 | 09:42 | 09:47 | Player B | 5:5 | Net Shot | Opponent Hit the Net | Hit the Net | 52 | 0.618812 | 0.833333 | 1.733333 | 0.900000 | matched |
| 53 | 09:49 | 09:58 | Player B | 5:5 | Net Shot | Opponent Hit the Net | Hit the Net | 53 | 0.944444 | 0.466667 | -0.033333 | -0.500000 | matched |
| 54 | 10:04 | 10:12 | Player B | 5:6 | Push Shot | Opponent Out of Bounds | Out of Bounds | 54 | 0.833333 | 0.366667 | -0.966667 | -1.333333 | matched |
| 55 | 10:20 | 10:31 | Player A | 6:6 | Push Shot | Winner Shot | Opponent Failed to Return | 55 | 0.937500 | -0.166667 | 0.566667 | 0.733333 | matched |
| 56 | 10:35 | 10:49 | Player B | 6:8 | Smash | Winner Shot | Opponent Failed to Return | 56 | 0.873181 | 0.000000 | 2.033333 | 2.033333 | matched |
| 57 | 10:53 | 11:07 | Player B | 6:9 | Block | Opponent Hit the Net | Hit the Net | 57 | 0.860656 | -0.766667 | 1.500000 | 2.266667 | matched |
| 58 | 11:10 | 11:36 | Player B | 7:10 | Net Shot | Opponent Hit the Net | Hit the Net | 59 | 0.871009 | 3.266667 | 0.100000 | -3.166667 | matched |
| 59 | 11:38 | 11:40 | Player A | 8:10 | Long Serve | Opponent Out of Bounds | Out of Bounds | — | — | — | — | — | missed |
| 60 | 11:52 | 12:01 | Player B | 8:11 | Smash | Opponent Out of Bounds | Out of Bounds | 60 | 0.951852 | 0.200000 | -0.233333 | -0.433333 | matched |
| 61 | 12:18 | 12:26 | Player A | 9:11 | Defensive Slice | Opponent Hit the Net | Hit the Net | 61 | 0.843866 | -0.966667 | -0.433333 | 0.533333 | matched |
| 62 | 12:35 | 12:44 | Player B | 9:13 | Net Kill | Winner Shot | Opponent Failed to Return | 62 | 0.918519 | 0.200000 | -0.533333 | -0.733333 | matched |
| 63 | 12:49 | 12:54 | Player B | 9:15 | Net Shot | Opponent Hit the Net | Hit the Net | 63 | 0.806667 | 0.933333 | -0.033333 | -0.966667 | matched |
| 64 | 12:57 | 13:09 | Player A | 10:15 | Push Shot | Opponent Out of Bounds | Out of Bounds | 64 | 0.939948 | -0.700000 | 0.066667 | 0.766667 | matched |
| 65 | 13:17 | 13:20 | Player A | 11:15 | Push Shot | Opponent Out of Bounds | Out of Bounds | — | — | — | — | — | missed |
| 66 | 13:23 | 13:31 | Player A | 12:15 | Block | Winner Shot | Opponent Failed to Return | 65 | 0.887500 | 0.900000 | 0.000000 | -0.900000 | matched |
| 67 | 13:43 | 13:59 | Player A | 14:15 | Smash | Winner Shot | Opponent Failed to Return | 66 | 0.927083 | 0.700000 | -0.466667 | -1.166667 | matched |
| 68 | 14:01 | 14:08 | Player B | 14:16 | Smash | Winner Shot | Opponent Failed to Return | 67 | 0.907834 | -0.233333 | -0.433333 | -0.200000 | matched |
| 69 | 14:14 | 14:27 | Player A | 15:16 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 68 | 0.957286 | 0.300000 | 0.266667 | -0.033333 | matched |
| 70 | 14:36 | 14:42 | Player A | 16:16 | Lift Shot | Winner Shot | Opponent Failed to Return | 69 | 0.972222 | 0.000000 | -0.166667 | -0.166667 | matched |
| 71 | 14:48 | 15:21 | Player A | 17:16 | Block | Opponent Hit the Net | Hit the Net | 70 | 0.677778 | 0.466667 | -10.166667 | -10.633333 | matched |
| 72 | 15:26 | 15:30 | Player B | 17:17 | Block | Opponent Hit the Net | Hit the Net | 72 | 0.683333 | 0.966667 | -0.300000 | -1.266667 | matched |
| 73 | 15:33 | 15:56 | Player B | 17:18 | Block | Winner Shot | Opponent Failed to Return | 73 | 0.969565 | 0.400000 | -0.300000 | -0.700000 | matched |
| 74 | 15:57 | 16:05 | Player B | 17:19 | Block | Opponent Out of Bounds | Out of Bounds | 74 | 0.870968 | 0.800000 | 0.266667 | -0.533333 | matched |
| 75 | 16:10 | 16:16 | Player B | 17:21 | Drive | Opponent Out of Bounds | Out of Bounds | 75 | 0.721992 | -2.033333 | -0.200000 | 1.833333 | matched |

| Secondary-reference unmatched P | Start f | End f | Start s | End s |
|---|---|---|---|---|
| 35 | 12174 | 12268 | 405.800000 | 408.933333 |
| 40 | 13462 | 13533 | 448.733333 | 451.100000 |
| 43 | 14131 | 14293 | 471.033333 | 476.433333 |
| 48 | 15681 | 16059 | 522.700000 | 535.300000 |
| 58 | 20114 | 20175 | 670.466667 | 672.500000 |
| 71 | 27349 | 27649 | 911.633333 | 921.633333 |

| Supplied semantic label inventory | Counts |
|---|---|
| win_point_player | {"Player B":48,"Player A":27} |
| ball_types | {"Lift Shot":8,"Smash":18,"Lob":4,"Net Shot":11,"Drive Defense":1,"Drive":2,"Clear":2,"Net Kill":5,"Cross Net Shot":3,"Push Shot":7,"Long Serve":2,"Slice":1,"Block":8,"Stick Smash":1,"Defensive Slice":2} |
| roundscore_A | {"0":9,"1":8,"2":2,"4":5,"5":8,"7":2,"8":3,"9":9,"10":3,"11":2,"13":1,"14":5,"15":3,"16":2,"3":4,"6":3,"12":1,"17":5} |
| roundscore_B | {"1":3,"2":7,"3":2,"5":5,"6":6,"7":1,"8":3,"9":3,"10":4,"11":3,"12":2,"13":5,"14":4,"15":6,"16":7,"17":4,"20":1,"21":2,"4":3,"18":2,"19":2} |

The supplied winner/score/shot fields are reproduced above exactly as source strings, including missing values and taxonomy variation. The temporal crosswalk does not establish named player/team equivalence, certified point identity, or exhaustive shot labels. Current rally winners are unknown and hitter identities are anonymous; outcome/score-sequence accuracy and per-shot confusion therefore remain unscorable, rather than being reported as verified model correctness.

### Component-level observed output versus available ground truth

| Coverage diagnostic | Numerator | Denominator | Coverage | Ground-truth accuracy available? |
|---|---|---|---|---|
| Raw shuttle present / source frames | 20256 | 29296 | 69.143% | No reviewed frame/person/contact labels |
| Detector-executed / source frames | 12315 | 29296 | 42.036% | No reviewed frame/person/contact labels |
| Fresh detector-matched person rows / person rows | 24591 | 58452 | 42.070% | No reviewed frame/person/contact labels |
| Current pose rows / person rows | 46816 | 58452 | 80.093% | No reviewed frame/person/contact labels |
| Current racket rows / person rows | 20568 | 58452 | 35.188% | No reviewed frame/person/contact labels |

| All component coverage counts | Value |
|---|---|
| frames | 29296 |
| raw_shuttle_present | 20256 |
| detector_executed_frames | 12315 |
| person_rows | 58452 |
| scene_telemetry_present | 3633 |
| scene_raw_hypotheses | 38 |
| actual_content_epoch_increments | 36 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 24591 |
| person_propagated_or_unmatched | 33861 |
| pose_present_rows | 46816 |
| pose_current_source_rows | 46816 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 22227 |
| racket_present_rows | 20568 |
| racket_current_source_rows | 20568 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 38 |
| scene_positive_correspondence_vetoes | 2 |
| scene_current_detector_probes | 38 |

#### Frame/component categories

| Field | Observed value |
|---|---|
| view | {"main":29227,"none":69} |
| calibration_state | {"REACQUIRING":22,"VALID":29205,"LOST":69} |
| player_population | {"0":194,"2":27842,"1":506,"3":754} |
| association_status | {"missing":8971,"observed":20227,"invalid":69,"ambiguous":29} |
| association_reason | {"no_accepted_raw_observation":8971,"fresh_selection_retained":20227,"image_view_invalid":69,"coobserved_competing_static_hypothesis":29} |
| scene_raw_status | {"unknown":162,"measured":3433,"hypothesis":38} |
| person_detector_match | {"True":24591,"False":33861} |
| person_identity_method | {"bytetrack_v1":58452} |
| scene_decision | {"barrier":36,"no_barrier":2} |
| scene_decision_reason | {"raw_change_and_current_layout_discontinuity":36,"complete_current_layout_correspondence":2} |

#### Live event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 167 |
| scene | 3 |
| participant_observation | 298 |
| rally_start | 75 |
| stroke | 819 |
| contact | 819 |
| rally_end | 75 |
| format_decision | 1 |
| shuttle_turn | 58 |
| broadcast_score | 708 |
| match_phase | 1 |
| highlight | 6 |
| identity_ambiguity | 48 |

#### Append-only event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 167 |
| scene | 3 |
| participant_observation | 298 |
| rally_start | 149 |
| contact | 1746 |
| stroke | 847 |
| rally_end | 75 |
| format_decision | 1 |
| shuttle_turn | 58 |
| broadcast_score | 708 |
| match_phase | 1 |
| highlight | 6 |
| identity_ambiguity | 48 |

#### All observed event categories

| Field | Observed value |
|---|---|
| event_status | {"confirmed":2600,"provisional":479} |
| stroke_actor | {"unknown":819} |
| stroke_physical_event_status | {"insufficient":427,"probable":109,"ambiguous":283} |
| stroke_contact_status | {"estimated":819} |
| stroke_classification_status | {"unknown":587,"estimated":232} |
| stroke_stroke | {"unknown":587,"push":105,"clear":16,"drop":51,"lift":22,"net_shot":26,"smash":1,"drive":11} |
| stroke_attribution_reason | {"nearest_proximity":815,"ambiguous_proximity":4} |
| stroke_classification_abstention_reason | {"missing_required_evidence":579,"unresolved_initial_contact":8} |
| contact_actor | {"unknown":819} |
| contact_physical_event_status | {"insufficient":427,"probable":109,"ambiguous":283} |
| contact_contact_status | {"estimated":819} |
| contact_attribution_reason | {"nearest_proximity":815,"ambiguous_proximity":4} |
| contact_trajectory_reliability | {"probable":435,"insufficient":222,"ambiguous":162} |
| contact_trajectory_reasons | {"supported_turn":330,"coherent_motion_change_unavailable":222,"supported_launch":105,"association_unresolved":162} |
| contact_impact_reliability | {"insufficient":427,"probable":109,"ambiguous":283} |
| contact_impact_reasons | {"fresh_player_observation_unavailable":427,"coherent_motion_and_fresh_contact_cue":109,"association_unresolved":162,"coherent_motion_change_unavailable":76,"no_fresh_swing_or_racket_overlap":45} |
| contact_attribution_reliability | {"insufficient":528,"probable":291} |
| contact_attribution_reasons | {"fresh_player_observation_unavailable":528,"geometric_attribution_not_verified_identity":291} |
| rally_end_reason | {"stationary":40,"gap":30,"cut":5} |
| rally_phase | {"unknown":2,"match_play":73} |
| rally_official | {"False":28,"True":47} |
| rally_match_format_known | {"False":1,"True":74} |
| rally_match_format | {"unknown":1,"singles":74} |
| rally_winner | {"None":75} |
| rally_score_transition_status | {"match_format_unknown":1,"unavailable":47,"candidate":27} |
| rally_admission_reason | {"duration_policy":73,"independent_contact_and_observed_motion_witnesses":2} |

#### Track/export counts

| Field | Observed value |
|---|---|
| camera_rows | 29296 |
| player_rows | 58440 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 56597 |
| projected_court_on_propagated_box | 32805 |
| racket_rows | 20559 |
| shuttle_rows | 29296 |

#### Track/export categories

| Field | Observed value |
|---|---|
| player_id | {"None":58440} |
| detector_matched | {"True":24579,"False":33861} |

| Semantic metric | Observed | Baseline comparison / limitation |
|---|---|---|
| Known rally winner output | 0/75 | Supplied coarse winner labels exist; identity/point mapping uncertified |
| Unknown stroke classification | 587/819 | Coarse one-label-per-rally ball_types is not exhaustive per-shot GT |
| Estimated stroke classification | 232/819 | Estimated coverage is not class accuracy |
| OCR saved readouts | 765 | Observed scoreboard rows, not accepted correct points |
| OCR label counts | {"AXELSEN":765,"ANTONSEN":765} | Raw OCR labels may differ from anonymous Player A/B |
| Tracked invalid geometry frames | 91 | Geometric diagnostics, not labelled location error |
| Session degradation | [{"stage":"player_identity","reason":"osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"},{"stage":"player_reid","reason":"baseline player_reid provider is unavailable"}] | Identity/ReID unavailability remains recorded; no new models fetched |

### Runtime, resources and every saved stage latency

| Saved resource/runtime metric | Value |
|---|---|
| original_parent_status | partial_or_failed |
| worker_exit_code | 1 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 2144773 |
| parent_failure_inclusive_elapsed_s | 3643.506591 |
| parent_failure_inclusive_source_fps | 8.040606 |
| neural_only_throughput_fps | — |
| model_loading_time_s | — |
| media_ready_time_s | — |
| model_staging_time_s | — |
| worker_final_cpu_s | — |
| worker_maxrss_bytes | — |
| sampled_worker_tree_peak_rss_bytes | 3052724224 |
| sampled_worker_gpu_peak_mib | 2122 |
| sampled_cpu_seconds_max_observed | 35651.460000 |
| sampled_cpu_seconds_last_observed | 35651.460000 |
| sampled_system_available_ram_min_bytes | 98115715072 |
| sample_count | 1761 |
| resource_rows | 1761 |
| sampling_error_count | 0 |

| Stage | Calls | Total wall s | P50 ms/call | P95 ms/call | Minimum ms | Maximum ms | Frame-population sum |
|---|---|---|---|---|---|---|---|
| court | 489 | 170.080707 | 323.079482 | 509.977051 | 115.339794 | 996.709613 | 29296 |
| content_continuity_and_players | 489 | 1509.988978 | 3393.747606 | 4099.433179 | 820.255628 | 4858.049618 | 29296 |
| shuttle | 489 | 429.485692 | 845.569769 | 1157.773762 | 239.879677 | 1672.758829 | 29296 |
| players | 489 | 143.979763 | 277.369536 | 595.891472 | 5.777207 | 935.429568 | 29296 |
| ocr | 489 | 587.193977 | 1102.111168 | 1716.329470 | 590.642066 | 3180.811513 | 29296 |

The historical timing key decode_perception_cache_s wraps the runner’s full _perceive call. Its name does not mean this was an observation-cache replay: the completed-worker receipts explicitly record cached_perception_used=false. It is a broad perception wall-time scope, not isolated cache decoding or pure GPU latency.

| Saved disk-use metric | Bytes / count |
|---|---|
| regular_files | 2962 |
| logical_bytes | 1016628907 |
| allocated_bytes | 1022640128 |
| staged_model_bytes | 361041769 |
| perception_cache_bytes | 119192401 |

Wall-time scopes overlap; they are not summable GPU kernel latency. Pure neural-only FPS and isolated model-loading time remain unavailable. For historical Tests 1/2, final worker-local timing/CPU/RSS fields were lost at catalogue publication and stay unavailable; failure-inclusive parent duration is identified explicitly. For normal runs, worker elapsed includes the runner and final catalogue verification. Current-process GPU samples cannot certify per-node ORT placement or true instantaneous memory peaks.

### Reproducibility, logs and annotation-file review

| Binding | Value |
|---|---|
| Normalized numerical profile SHA256 (passive ranges removed) | 2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb |
| Effective profile canonical SHA256 | 504816be296e38c30cea52dff6a2e52d72147f8d497044dad05bb36cb9a9a3e2 |
| Model identity sets | 1 |
| Runtime identity sets | 1 |
| Actual model identity SHA256 | e3c96b7c2e522fd6efe6106328bebec30137f29b7303fe5e475f8aedea5d2222 |
| Actual runtime identity SHA256 | 81e41f18d858ed37c34ce9d07ae34a34268f27e57c0e5f878e07253be309066f |
| Executed plan | [plan.json](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/protocol_test2_v2/plan.json) |
| Actual completion receipt | [completion_receipt.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test2_historical/completion/completion_receipt.json) |
| Per-rally saved CSV | [per_rally_comparison.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test2_historical/evaluation/per_rally_comparison.csv) |
| Technical analysis | [technical_analysis.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test2_historical/analysis/technical_analysis.json) |
| Full original predictions | [predicted_rallies.csv](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_test2_v1/predicted_rallies.csv) |

| Annotation file | Role | Data rows | Blank rows | Bytes | Column/schema inventory | SHA256 |
|---|---|---|---|---|---|---|
| Test2_Full.csv | Secondary coarse outcome/time reference | 75 | 0 | 5369 | ["start_time","end_time","win_point_player","win_reason","ball_types","lose_reason","roundscore_A","roundscore_B"] | 03dcb642c93f94ff03ce8e0e86b60b850cc0a78cd8fbad8c38360245d209bd74 |
| Test2_Full_Rev_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 29296 | 0 | 637129 | ["Frame","X","Y","Visibility","Confidence"] | cb3bd1aa62582f7b6c15ffc1869f85846d0359c42acd4ceaeb91bfb56781da24 |
| Test2_Full_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 29296 | 0 | 637129 | ["Frame","X","Y","Visibility","Confidence"] | cb3bd1aa62582f7b6c15ffc1869f85846d0359c42acd4ceaeb91bfb56781da24 |
| Test2_Full_court.json | Auxiliary historical/generated artifact; not certified independent truth | — | — | 537 | ["frame_no","frame_size","corners","net","source"] | 700d0e70c316f4f493f78df8f554e19aec0f52e5d9f8efaa928338a5955e2b92 |
| Test2_Full_rally.csv | Primary timing reference | 73 | 0 | 5070 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 33a671408f26f9aba0824d78c1fcc257607782c854bbd0dfd4981dc3cadc2387 |
| player_detections.csv | Auxiliary historical/generated artifact; not certified independent truth | 29296 | 0 | 3285287 | ["frame_no","player_1_x","player_1_y","player_1_conf","player_2_x","player_2_y","player_2_conf"] | 1091af144117f84bb62bcc1a2abc54781481f46cfd1a9526fe4fd81ab54e4982 |
| win_predictions.csv | Auxiliary historical/generated artifact; not certified independent truth | 73 | 0 | 8840 | ["rally_idx","start_frame","end_frame","start_time","end_time","winner","loser","win_reason","reason_src","fault_side","fault_src","cnn_class","cnn_conf","cnn_oob","cnn_hn","cnn_wbl","score_Player A","score_Player B"] | b527da55c3579912b12dd4dbb469789ba97403854b395a22a78f1d862e0a40a8 |

| Log | Lines | Warning/error-pattern lines | Distinct observed warning/error messages |
|---|---|---|---|
| fresh_test2_v1.execution.log | 101 | 68 | ["2026-11-05 22:02:41 [warning  ] perception.degraded            reason='osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`' stage=player_identity","2026-11-05 22:02:41 [warning  ] perception.degraded            reason='baseline player_reid provider is unavailable' stage=player_reid","[WARNING] 2026-11-05 22:03:30,849 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:03:46,015 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:04:01,074 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:04:16,374 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:04:31,119 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:04:44,755 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:12:11,843 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:12:17,677 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:12:18,048 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:12:22,195 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:12:30,287 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:12:56,232 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:13:11,201 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:13:25,497 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:13:36,090 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:13:49,108 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:14:03,480 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:14:16,710 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:21:08,664 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:21:12,916 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:21:13,334 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:21:21,388 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:21:28,776 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:21:42,645 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:22:14,113 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:22:30,852 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:22:44,460 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:22:58,065 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:23:12,284 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:23:22,819 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:23:33,156 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:23:43,940 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:23:53,709 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:24:06,779 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:24:34,737 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:24:48,982 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:25:04,121 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:25:19,455 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:25:32,818 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:25:46,700 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:26:02,548 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:26:14,543 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:26:29,739 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:26:44,239 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:27:00,338 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:30:52,170 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:30:52,817 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:30:57,380 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:31:14,050 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:31:28,207 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:31:44,975 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:31:55,816 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:32:12,108 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:32:26,739 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:32:43,001 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:32:55,570 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:45:44,306 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:45:47,977 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:45:48,353 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:45:53,141 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:46:03,651 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-05 22:46:13,532 [RapidOCR] main.py:164: The text detection result is empty","    raise ValueError(\"unsupported cache codec version\")","ValueError: unsupported cache codec version","    raise ValueError(f\"invalid bounded cache header/frames: {path.name}: {error}\") from error","ValueError: invalid bounded cache header/frames: seg_00000.msgpack: unsupported cache codec version"] |
| fresh_test2_v1.launch.log | 0 | 0 | [] |

Log keyword counts are diagnostic string matches, not failed-inference counts. Tests 1/2 raw original worker logs remain in their source run directories and retain the known final catalogue failure; their independent completion proof is the accepted completion record. All previously completed evaluations remain immutable.

### Duration breakdown for this video

| GT duration bin | GT count | Matched | Missed | Recall | Start MAE f | End MAE f |
|---|---|---|---|---|---|---|
| ≤2 s | 3 | 3 | 0 | 1.000000 | 10.000000 | 16.666667 |
| (2,5] s | 14 | 10 | 4 | 0.714286 | 5.500000 | 20.900000 |
| (5,10] s | 31 | 30 | 1 | 0.967742 | 18.933333 | 9.666667 |
| (10,20] s | 18 | 18 | 0 | 1.000000 | 39.277778 | 28.166667 |
| >20 s | 7 | 7 | 0 | 1.000000 | 37.714286 | 54.714286 |

## Test 3: complete evaluation and ground-truth comparison

Reference **19 rallies**, predictions **24**; TP/FP/FN **18/6/1**. Precision **75.000%**, recall **94.737%**, F1 **83.721%**. Matched mean IoU **0.895795**. The ground-truth benchmark for every table in this primary section is [Test3_Full_rally.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test3_Full/Test3_Full_rally.csv).

| Input / execution binding | Value |
|---|---|
| Decoded frames | 8414 |
| FPS | 30.000000 |
| Video duration seconds | 280.466667 |
| Canonical dimensions | 1280 × 720 |
| Source SHA256 | d587569affa3b4fcabab0ea6b97ecd278af15675ce5cba36c79298bb6d0db5fa |
| Proxy SHA256 | 34b9720e47e7cb86c7887e923f2f14140b2aecc5e16811c193e3612bb15833bf |
| Prediction SHA256 | dd4c2b90099eba9b77ac4d37fd1155e23003c0d1cd90c48602e7cc00f17c82c0 |
| Ground-truth SHA256 | 252e4f43e3f719a18b112ab85d087ce4b2d50aec976ee4863114a9c0bb3b98d8 |
| Coarse reference SHA256 | 85801c06250025f71c347f0f5305c7a9a52763c9aa8b02a211309e3aba14f01d |
| Session | UPLOADTEST3 |
| Actual completion mode | normal_completed_worker |
| Original parent receipt status | completed |
| Full source/proxy PTS matches | 8414 |
| Scene probe pixel hashes verified | 14 |
| Verified saved files / logical bytes | 1188 / 563026290 |
| Read-only record | [saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test3) |

### Primary metric scores versus the ground-truth ideal

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 19 | 19 | 0 |
| Prediction count | 19 | 24 | 5 |
| TP / matched | 19 | 18 | -1 |
| FP | 0 | 6 | 6 |
| FN / missed | 0 | 1 | 1 |
| precision | 1 | 0.750000 | -0.250000 |
| recall | 1 | 0.947368 | -0.052632 |
| f1 | 1 | 0.837209 | -0.162791 |
| Mean matched IoU | 1 | 0.895795 | -0.104205 |
| Median matched IoU | 1 | 0.951783 | -0.048217 |
| Minimum matched IoU | 1 | 0.505929 | -0.494071 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 83.333333 |
| 0.9 | 100 | 72.222222 |
| 0.95 | 100 | 50.000000 |

A GT self-comparison has TP=N, FP=FN=0, precision/recall/F1=1, IoU=1 and every timing/duration error=0. This is the reference ideal, not a separately executed baseline model. The signed count difference alone is insufficient: false positives and misses can cancel.

### Boundary and duration errors versus zero-error ground truth

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 28.611111 | 5.000000 | 63.108813 | 233.000000 | 88.000000 | 28.500000 | 5.000000 |
| end_frame | 8.500000 | 5.000000 | 10.596121 | 20.000000 | 17.600000 | 0.833333 | -1.000000 |
| start_time_sec | 0.953704 | 0.166667 | 2.103627 | 7.766667 | 2.933333 | 0.950000 | 0.166667 |
| end_time_sec | 0.283333 | 0.166667 | 0.353204 | 0.666667 | 0.586667 | 0.027778 | -0.033333 |
| duration_sec | 0.992593 | 0.366667 | 2.003916 | 7.200000 | 2.793333 | -0.922222 | -0.233333 |

| Additional saved statistic | Value | Ground-truth ideal |
|---|---|---|
| Start P95 \|error\| frames | 109.750000 | 0 |
| End P95 \|error\| frames | 19.150000 | 0 |
| Duration mae frames | 29.777778 | 0 |
| Duration rmse frames | 60.117478 | 0 |
| Duration signed_bias frames | -27.666667 | 0 |

All error statistics above condition on eligible matched rallies. A positive start error is a late start; a negative start error is early. A positive end error is a late end; a negative end error is premature. Duration error is prediction minus GT. All 30 FPS frame errors convert by dividing by30; full signed/absolute per-rally values appear below. Misses have no invented zero error.

### Boundary tolerance scores

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 3 | 18 | 16.667% | 19 | 15.789% | 100% |
| start | 3 | 0.100000 | 9 | 18 | 50.000% | 19 | 47.368% | 100% |
| start | 5 | 0.166667 | 9 | 18 | 50.000% | 19 | 47.368% | 100% |
| start | 10 | 0.333333 | 12 | 18 | 66.667% | 19 | 63.158% | 100% |
| start | 15 | 0.500000 | 13 | 18 | 72.222% | 19 | 68.421% | 100% |
| start | 30 | 1.000000 | 14 | 18 | 77.778% | 19 | 73.684% | 100% |
| end | 1 | 0.033333 | 2 | 18 | 11.111% | 19 | 10.526% | 100% |
| end | 3 | 0.100000 | 3 | 18 | 16.667% | 19 | 15.789% | 100% |
| end | 5 | 0.166667 | 11 | 18 | 61.111% | 19 | 57.895% | 100% |
| end | 10 | 0.333333 | 11 | 18 | 61.111% | 19 | 57.895% | 100% |
| end | 15 | 0.500000 | 14 | 18 | 77.778% | 19 | 73.684% | 100% |
| end | 30 | 1.000000 | 18 | 18 | 100.000% | 19 | 94.737% | 100% |

### All saved error distributions

| Distribution / units | N | Mean | Median | Minimum | Maximum | P90 | P95 | Ideal |
|---|---|---|---|---|---|---|---|---|
| matched_iou | 18 | 0.895795 | 0.951783 | 0.505929 | 0.992481 | 0.980082 | 0.983034 | 1 |
| start_signed_frames | 18 | 28.500000 | 5.000000 | -1.000000 | 233.000000 | 88.000000 | 109.750000 | 0 |
| start_absolute_frames | 18 | 28.611111 | 5.000000 | 0.000000 | 233.000000 | 88.000000 | 109.750000 | 0 |
| end_signed_frames | 18 | 0.833333 | -1.000000 | -20.000000 | 19.000000 | 16.300000 | 17.300000 | 0 |
| end_absolute_frames | 18 | 8.500000 | 5.000000 | 1.000000 | 20.000000 | 17.600000 | 19.150000 | 0 |
| duration_signed_frames | 18 | -27.666667 | -7.000000 | -216.000000 | 14.000000 | 2.300000 | 4.650000 | 0 |
| duration_absolute_frames | 18 | 29.777778 | 11.000000 | 1.000000 | 216.000000 | 83.800000 | 119.100000 | 0 |
| duration_signed_seconds | 18 | -0.922222 | -0.233333 | -7.200000 | 0.466667 | 0.076667 | 0.155000 | 0 |

### Misses, extras, overlap topology and failure review

| Diagnostic | Observed | GT ideal / interpretation |
|---|---|---|
| Missed GT IDs | [7] | [] |
| Unmatched prediction IDs | [7,8,9,10,19,22] | [] |
| No-overlap missed GT IDs | [] | [] |
| Predictions without any GT overlap | [] | [] |
| Possible split GT IDs | [7,8,16,17,18] | Geometric overlap candidates; not adjudicated semantic splits |
| Possible merge prediction IDs | [20] | Geometric overlap candidates; not adjudicated semantic merges |
| Significant failure records | 11 | Unmatched or \|boundary error\|>30frames or IoU<0.75 |
| early_start_gt_ids | [14] | Direction/weak-overlap inventory, not a physical cause |
| late_start_gt_ids | [1,2,3,4,6,8,9,10,11,12,13,15,16,17,18,19] | Direction/weak-overlap inventory, not a physical cause |
| premature_end_gt_ids | [3,5,6,8,9,10,12,14,17,19] | Direction/weak-overlap inventory, not a physical cause |
| late_end_gt_ids | [1,2,4,11,13,15,16,18] | Direction/weak-overlap inventory, not a physical cause |
| weak_iou_gt_ids | [8,16,18] | Direction/weak-overlap inventory, not a physical cause |

| Inventory validity | Ground truth | Predictions |
|---|---|---|
| count | 19 | 24 |
| duplicate_row_pairs | [] | [] |
| positive_overlap_row_pairs | [] | [] |
| adjacent_row_pairs | [] | [] |
| out_of_range_rows | [] | [] |
| out_of_order_rows | [] | [] |

| False detection P ID | Start frame | End frame | Start seconds | End seconds | Duration seconds | Positive-overlap GT IDs |
|---|---|---|---|---|---|---|
| 7 | 2485 | 2715 | 82.833333 | 90.500000 | 7.666667 | [7] |
| 8 | 2717 | 2990 | 90.566667 | 99.666667 | 9.100000 | [7] |
| 9 | 2993 | 3054 | 99.766667 | 101.800000 | 2.033333 | [7] |
| 10 | 3130 | 3187 | 104.333333 | 106.233333 | 1.900000 | [8] |
| 19 | 6692 | 6847 | 223.066667 | 228.233333 | 5.166667 | [16] |
| 22 | 7337 | 7394 | 244.566667 | 246.466667 | 1.900000 | [18] |

| Largest matched boundary cases | P ID | GT start/end frames | Pred start/end frames | Δstart frames | Δend frames | IoU |
|---|---|---|---|---|---|---|
| 16 | 20 | 6691–7180 | 6924–7197 | 233 | 17 | 0.505929 |
| 8 | 11 | 3117–3474 | 3205–3460 | 88 | -14 | 0.714286 |
| 18 | 23 | 7324–7666 | 7412–7678 | 88 | 12 | 0.717514 |
| 1 | 1 | 94–434 | 129–453 | 35 | 19 | 0.849582 |
| 19 | 24 | 7886–8413 | 7894–8393 | 8 | -20 | 0.946869 |

Of 1 unmatched reference intervals, 0 have no positive overlap with any prediction; 1 have some overlap but fail the one-to-one IoU eligibility/assignment. This separates absence of overlap from insufficient interval agreement without inventing a causal diagnosis.

### Every GT rally compared directly with its assigned prediction: frames

G IDs are one-based CSV row IDs in the primary rally reference. P IDs are one-based rows in the preserved prediction CSV. C IDs refer to the separate coarse table, linked only by the same IoU-based temporal crosswalk. “—” denotes unavailable/unmatched, not zero.

| G | P | GT start f | GT end f | Pred start f | Pred end f | Δstart f | \|Δstart\| f | Δend f | \|Δend\| f | IoU | Status | Coarse C row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 94 | 434 | 129 | 453 | 35 | 35 | 19 | 19 | 0.849582 | matched | 1 |
| 2 | 2 | 588 | 1227 | 595 | 1232 | 7 | 7 | 5 | 5 | 0.981366 | matched | 2 |
| 3 | 3 | 1302 | 1484 | 1305 | 1479 | 3 | 3 | -5 | 5 | 0.956044 | matched | 3 |
| 4 | 4 | 1591 | 1928 | 1593 | 1933 | 2 | 2 | 5 | 5 | 0.979532 | matched | 4 |
| 5 | 5 | 1953 | 2086 | 1953 | 2085 | 0 | 0 | -1 | 1 | 0.992481 | matched | 5 |
| 6 | 6 | 2193 | 2337 | 2196 | 2335 | 3 | 3 | -2 | 2 | 0.965278 | matched | 6 |
| 7 | — | 2484 | 3055 | — | — | — | — | — | — | — | missed | — |
| 8 | 11 | 3117 | 3474 | 3205 | 3460 | 88 | 88 | -14 | 14 | 0.714286 | matched | 10 |
| 9 | 12 | 3686 | 4211 | 3687 | 4197 | 1 | 1 | -14 | 14 | 0.971429 | matched | 11 |
| 10 | 13 | 4318 | 4644 | 4335 | 4643 | 17 | 17 | -1 | 1 | 0.944785 | matched | 12 |
| 11 | 14 | 4795 | 5434 | 4805 | 5439 | 10 | 10 | 5 | 5 | 0.976708 | matched | 13 |
| 12 | 15 | 5509 | 5691 | 5511 | 5687 | 2 | 2 | -4 | 4 | 0.967033 | matched | 14 |
| 13 | 16 | 5798 | 6125 | 5800 | 6141 | 2 | 2 | 16 | 16 | 0.947522 | matched | 15 |
| 14 | 17 | 6160 | 6296 | 6159 | 6292 | -1 | 1 | -4 | 4 | 0.963504 | matched | 16 |
| 15 | 18 | 6400 | 6539 | 6403 | 6544 | 3 | 3 | 5 | 5 | 0.944444 | matched | 17 |
| 16 | 20 | 6691 | 7180 | 6924 | 7197 | 233 | 233 | 17 | 17 | 0.505929 | matched | 19 |
| 17 | 21 | 7192 | 7272 | 7204 | 7268 | 12 | 12 | -4 | 4 | 0.800000 | matched | 20 |
| 18 | 23 | 7324 | 7666 | 7412 | 7678 | 88 | 88 | 12 | 12 | 0.717514 | matched | 21 |
| 19 | 24 | 7886 | 8413 | 7894 | 8393 | 8 | 8 | -20 | 20 | 0.946869 | matched | 22 |

### Every GT rally compared directly: timestamps and durations

| G | GT start s | GT end s | Pred start s | Pred end s | GT duration s | Pred duration s | Δstart s | \|Δstart\| s | Δend s | \|Δend\| s | Δduration s | \|Δduration\| s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3.133333 | 14.466667 | 4.300000 | 15.100000 | 11.333333 | 10.800000 | 1.166667 | 1.166667 | 0.633333 | 0.633333 | -0.533333 | 0.533333 |
| 2 | 19.600000 | 40.900000 | 19.833333 | 41.066667 | 21.300000 | 21.233333 | 0.233333 | 0.233333 | 0.166667 | 0.166667 | -0.066667 | 0.066667 |
| 3 | 43.400000 | 49.466667 | 43.500000 | 49.300000 | 6.066667 | 5.800000 | 0.100000 | 0.100000 | -0.166667 | 0.166667 | -0.266667 | 0.266667 |
| 4 | 53.033333 | 64.266667 | 53.100000 | 64.433333 | 11.233333 | 11.333333 | 0.066667 | 0.066667 | 0.166667 | 0.166667 | 0.100000 | 0.100000 |
| 5 | 65.100000 | 69.533333 | 65.100000 | 69.500000 | 4.433333 | 4.400000 | 0.000000 | 0.000000 | -0.033333 | 0.033333 | -0.033333 | 0.033333 |
| 6 | 73.100000 | 77.900000 | 73.200000 | 77.833333 | 4.800000 | 4.633333 | 0.100000 | 0.100000 | -0.066667 | 0.066667 | -0.166667 | 0.166667 |
| 7 | 82.800000 | 101.833333 | — | — | 19.033333 | — | — | — | — | — | — | — |
| 8 | 103.900000 | 115.800000 | 106.833333 | 115.333333 | 11.900000 | 8.500000 | 2.933333 | 2.933333 | -0.466667 | 0.466667 | -3.400000 | 3.400000 |
| 9 | 122.866667 | 140.366667 | 122.900000 | 139.900000 | 17.500000 | 17.000000 | 0.033333 | 0.033333 | -0.466667 | 0.466667 | -0.500000 | 0.500000 |
| 10 | 143.933333 | 154.800000 | 144.500000 | 154.766667 | 10.866667 | 10.266667 | 0.566667 | 0.566667 | -0.033333 | 0.033333 | -0.600000 | 0.600000 |
| 11 | 159.833333 | 181.133333 | 160.166667 | 181.300000 | 21.300000 | 21.133333 | 0.333333 | 0.333333 | 0.166667 | 0.166667 | -0.166667 | 0.166667 |
| 12 | 183.633333 | 189.700000 | 183.700000 | 189.566667 | 6.066667 | 5.866667 | 0.066667 | 0.066667 | -0.133333 | 0.133333 | -0.200000 | 0.200000 |
| 13 | 193.266667 | 204.166667 | 193.333333 | 204.700000 | 10.900000 | 11.366667 | 0.066667 | 0.066667 | 0.533333 | 0.533333 | 0.466667 | 0.466667 |
| 14 | 205.333333 | 209.866667 | 205.300000 | 209.733333 | 4.533333 | 4.433333 | -0.033333 | 0.033333 | -0.133333 | 0.133333 | -0.100000 | 0.100000 |
| 15 | 213.333333 | 217.966667 | 213.433333 | 218.133333 | 4.633333 | 4.700000 | 0.100000 | 0.100000 | 0.166667 | 0.166667 | 0.066667 | 0.066667 |
| 16 | 223.033333 | 239.333333 | 230.800000 | 239.900000 | 16.300000 | 9.100000 | 7.766667 | 7.766667 | 0.566667 | 0.566667 | -7.200000 | 7.200000 |
| 17 | 239.733333 | 242.400000 | 240.133333 | 242.266667 | 2.666667 | 2.133333 | 0.400000 | 0.400000 | -0.133333 | 0.133333 | -0.533333 | 0.533333 |
| 18 | 244.133333 | 255.533333 | 247.066667 | 255.933333 | 11.400000 | 8.866667 | 2.933333 | 2.933333 | 0.400000 | 0.400000 | -2.533333 | 2.533333 |
| 19 | 262.866667 | 280.433333 | 263.133333 | 279.766667 | 17.566667 | 16.633333 | 0.266667 | 0.266667 | -0.666667 | 0.666667 | -0.933333 | 0.933333 |

### Secondary coarse/outcome annotations: full supplied baseline and comparison

[Test3_Full.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test3_Full/Test3_Full.csv) contains **22 data rows**, **22 nonblank intervals**, blank row IDs **[]**. This separate reference differs from the 19-interval primary timing table. The same unchanged predictions and matcher give secondary precision **91.667%**, recall **100.000%**, F1 **95.652%**; this reference-sensitivity analysis does not replace the primary benchmark. No labels, times or predictions were fitted or repaired.

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 22 | 22 | 0 |
| Prediction count | 22 | 24 | 2 |
| TP / matched | 22 | 22 | 0 |
| FP | 0 | 2 | 2 |
| FN / missed | 0 | 0 | 0 |
| precision | 1 | 0.916667 | -0.083333 |
| recall | 1 | 1.000000 | 0.000000 |
| f1 | 1 | 0.956522 | -0.043478 |
| Mean matched IoU | 1 | 0.871584 | -0.128416 |
| Median matched IoU | 1 | 0.880833 | -0.119167 |
| Minimum matched IoU | 1 | 0.677778 | -0.322222 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 90.909091 |
| 0.9 | 100 | 31.818182 |
| 0.95 | 100 | 13.636364 |

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 14.954545 | 15.000000 | 17.759760 | 34.000000 | 25.000000 | 13.045455 | 14.000000 |
| end_frame | 15.818182 | 13.000000 | 19.537842 | 53.000000 | 27.000000 | 5.090909 | 9.000000 |
| start_time_sec | 0.498485 | 0.500000 | 0.591992 | 1.133333 | 0.833333 | 0.434848 | 0.466667 |
| end_time_sec | 0.527273 | 0.433333 | 0.651261 | 1.766667 | 0.900000 | 0.169697 | 0.300000 |
| duration_sec | 0.559091 | 0.383333 | 0.714744 | 1.833333 | 1.116667 | -0.265152 | -0.266667 |

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 0 | 22 | 0.000% | 22 | 0.000% | 100% |
| start | 3 | 0.100000 | 4 | 22 | 18.182% | 22 | 18.182% | 100% |
| start | 5 | 0.166667 | 6 | 22 | 27.273% | 22 | 27.273% | 100% |
| start | 10 | 0.333333 | 9 | 22 | 40.909% | 22 | 40.909% | 100% |
| start | 15 | 0.500000 | 12 | 22 | 54.545% | 22 | 54.545% | 100% |
| start | 30 | 1.000000 | 21 | 22 | 95.455% | 22 | 95.455% | 100% |
| end | 1 | 0.033333 | 0 | 22 | 0.000% | 22 | 0.000% | 100% |
| end | 3 | 0.100000 | 2 | 22 | 9.091% | 22 | 9.091% | 100% |
| end | 5 | 0.166667 | 3 | 22 | 13.636% | 22 | 13.636% | 100% |
| end | 10 | 0.333333 | 10 | 22 | 45.455% | 22 | 45.455% | 100% |
| end | 15 | 0.500000 | 14 | 22 | 63.636% | 22 | 63.636% | 100% |
| end | 30 | 1.000000 | 21 | 22 | 95.455% | 22 | 95.455% | 100% |

| Cross-reference timing diagnostic | Value |
|---|---|
| Primary-to-coarse eligible matched intervals | 18 |
| Primary intervals unmatched to coarse reference | [7] |
| Coarse rows unmatched to primary reference | [7,8,9,18] |
| Primary/coarse matched mean IoU | 0.855999 |

| C source row | Supplied start | Supplied end | Supplied winner | Supplied A:B score | Supplied shot / ball_types | Win reason | Lose reason | Matched P | IoU | Δstart s | Δend s | Δduration s | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:05 | 0:15 | Player B | 0:1 | Net Shot | Opponent Hit the Net | Hit the Net | 1 | 0.925926 | -0.700000 | 0.100000 | 0.800000 | matched |
| 2 | 0:19 | 0:41 | Player A | 1:1 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 2 | 0.959215 | 0.833333 | 0.066667 | -0.766667 | matched |
| 3 | 0:43 | 0:49 | Player B | 1:2 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 3 | 0.873016 | 0.500000 | 0.300000 | -0.200000 | matched |
| 4 | 0:53 | 1:04 | Player B | 1:3 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 4 | 0.953353 | 0.100000 | 0.433333 | 0.333333 | matched |
| 5 | 1:05 | 1:09 | Player B | 1:4 | Drop Shot | Opponent Out of Bounds | Hit Out of Bounds | 5 | 0.866667 | 0.100000 | 0.500000 | 0.400000 | matched |
| 6 | 1:13 | 1:18 | Player B | 4:None | Opponent Failed to Return | Opponent Out of Bounds | 2 | 6 | 0.926667 | 0.200000 | -0.166667 | -0.366667 | matched |
| 7 | 1:22 | 1:30 | Player A | 3:4 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 7 | 0.843137 | 0.833333 | 0.500000 | -0.333333 | matched |
| 8 | 1:30 | 1:39 | Player B | 3:5 | Smash | Winner Shot | Opponent Failed to Return | 8 | 0.872414 | 0.566667 | 0.666667 | 0.100000 | matched |
| 9 | 1:39 | 1:42 |  Player A | 4:5 | Smash | Winner Shot | Opponent Failed to Return | 9 | 0.677778 | 0.766667 | -0.200000 | -0.966667 | matched |
| 10 | 1:46 | 1:55 | Player B | 4:6 | Net Shot | Opponent Hit the Net | Hit the Net | 11 | 0.875000 | 0.833333 | 0.333333 | -0.500000 | matched |
| 11 | 2:02 | 2:19 | Player B | 4:7 | Net Shot | Opponent Hit the Net | Hit the Net | 12 | 0.899441 | 0.900000 | 0.900000 | 0.000000 | matched |
| 12 | 2:24 | 2:35 | Player A | 5:7 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 13 | 0.933333 | 0.500000 | -0.233333 | -0.733333 | matched |
| 13 | 2:40 | 3:01 | Player A | 6:7 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 14 | 0.978091 | 0.166667 | 0.300000 | 0.133333 | matched |
| 14 | 3:03 | 3:10 | Player B | 6:8 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 15 | 0.838095 | 0.700000 | -0.433333 | -1.133333 | matched |
| 15 | 3:13 | 3:24 | Player B | 6:9 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 16 | 0.911681 | 0.333333 | 0.700000 | 0.366667 | matched |
| 16 | 3:25 | 3:30 | Player B | 6:10 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 17 | 0.886667 | 0.300000 | -0.266667 | -0.566667 | matched |
| 17 | 3:33 | 3:39 | Player B | 6:11 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 18 | 0.783333 | 0.433333 | -0.866667 | -1.300000 | matched |
| 18 | 3:43 | 3:50 | Player A | 7:11 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 19 | 0.738095 | 0.066667 | -1.766667 | -1.833333 | matched |
| 19 | 3:50 | 3:59 | Player B | 7:12 | Smash | Winner Shot | Opponent Failed to Return | 20 | 0.828283 | 0.800000 | 0.900000 | 0.100000 | matched |
| 20 | 4:00 | 4:02 | Player A | 8:12 | Smash | Winner Shot | Opponent Failed to Return | 21 | 0.823529 | 0.133333 | 0.266667 | 0.133333 | matched |
| 21 | 4:07 | 4:15 | Player B | 8:13 | Net Shot | Opponent Hit the Net | Hit the Net | 23 | 0.888060 | 0.066667 | 0.933333 | 0.866667 | matched |
| 22 | 4:22 | 4:39 | Player B | 8:14 | Lift Shot | Opponent Hit the Net | Hit the Net | 24 | 0.893058 | 1.133333 | 0.766667 | -0.366667 | matched |

| Secondary-reference unmatched P | Start f | End f | Start s | End s |
|---|---|---|---|---|
| 10 | 3130 | 3187 | 104.333333 | 106.233333 |
| 22 | 7337 | 7394 | 244.566667 | 246.466667 |

| Supplied semantic label inventory | Counts |
|---|---|
| win_point_player | {"Player B":15,"Player A":6," Player A":1} |
| ball_types | {"Net Shot":4,"Lift Shot":11,"Push Shot":1,"Drop Shot":1,"Opponent Failed to Return":1,"Smash":4} |
| roundscore_A | {"0":1,"1":4,"4":4,"3":2,"5":1,"6":5,"7":2,"8":3} |
| roundscore_B | {"1":2,"2":1,"3":1,"4":2,"null":1,"5":2,"6":1,"7":3,"8":1,"9":1,"10":1,"11":2,"12":2,"13":1,"14":1} |

The supplied winner/score/shot fields are reproduced above exactly as source strings, including missing values and taxonomy variation. The temporal crosswalk does not establish named player/team equivalence, certified point identity, or exhaustive shot labels. Current rally winners are unknown and hitter identities are anonymous; outcome/score-sequence accuracy and per-shot confusion therefore remain unscorable, rather than being reported as verified model correctness.

### Component-level observed output versus available ground truth

| Coverage diagnostic | Numerator | Denominator | Coverage | Ground-truth accuracy available? |
|---|---|---|---|---|
| Raw shuttle present / source frames | 6225 | 8414 | 73.984% | No reviewed frame/person/contact labels |
| Detector-executed / source frames | 3557 | 8414 | 42.275% | No reviewed frame/person/contact labels |
| Fresh detector-matched person rows / person rows | 7056 | 16542 | 42.655% | No reviewed frame/person/contact labels |
| Current pose rows / person rows | 13477 | 16542 | 81.471% | No reviewed frame/person/contact labels |
| Current racket rows / person rows | 5443 | 16542 | 32.904% | No reviewed frame/person/contact labels |

| All component coverage counts | Value |
|---|---|
| frames | 8414 |
| raw_shuttle_present | 6225 |
| detector_executed_frames | 3557 |
| person_rows | 16542 |
| scene_telemetry_present | 3606 |
| scene_raw_hypotheses | 14 |
| actual_content_epoch_increments | 14 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 7056 |
| person_propagated_or_unmatched | 9486 |
| pose_present_rows | 13477 |
| pose_current_source_rows | 13477 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 6421 |
| racket_present_rows | 5443 |
| racket_current_source_rows | 5443 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 14 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 14 |

#### Frame/component categories

| Field | Observed value |
|---|---|
| view | {"main":8334,"none":80} |
| calibration_state | {"REACQUIRING":16,"VALID":8318,"LOST":80} |
| player_population | {"0":125,"2":8253,"1":36} |
| association_status | {"missing":2109,"observed":6225,"invalid":80} |
| association_reason | {"no_accepted_raw_observation":2109,"fresh_selection_retained":6225,"image_view_invalid":80} |
| scene_raw_status | {"unknown":61,"measured":3531,"hypothesis":14} |
| person_detector_match | {"True":7056,"False":9486} |
| person_identity_method | {"bytetrack_v1":16542} |
| scene_decision | {"barrier":14} |
| scene_decision_reason | {"raw_change_and_current_layout_discontinuity":14} |

#### Live event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 69 |
| scene | 6 |
| participant_observation | 70 |
| format_decision | 1 |
| rally_start | 24 |
| stroke | 273 |
| contact | 273 |
| rally_end | 24 |
| shuttle_turn | 15 |
| broadcast_score | 207 |
| identity_ambiguity | 21 |
| match_phase | 1 |
| highlight | 1 |

#### Append-only event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 69 |
| scene | 6 |
| participant_observation | 70 |
| rally_start | 52 |
| contact | 592 |
| stroke | 285 |
| format_decision | 1 |
| rally_end | 24 |
| shuttle_turn | 15 |
| broadcast_score | 207 |
| identity_ambiguity | 21 |
| match_phase | 1 |
| highlight | 1 |

#### All observed event categories

| Field | Observed value |
|---|---|
| event_status | {"confirmed":856,"provisional":130} |
| stroke_actor | {"unknown":273} |
| stroke_physical_event_status | {"insufficient":142,"ambiguous":88,"probable":43} |
| stroke_contact_status | {"estimated":273} |
| stroke_classification_status | {"unknown":191,"estimated":82} |
| stroke_stroke | {"unknown":191,"push":46,"lift":8,"drive":5,"net_shot":13,"drop":6,"clear":4} |
| stroke_attribution_reason | {"nearest_proximity":272,"ambiguous_proximity":1} |
| stroke_classification_abstention_reason | {"missing_required_evidence":189,"unresolved_initial_contact":2} |
| contact_actor | {"unknown":273} |
| contact_physical_event_status | {"insufficient":142,"ambiguous":88,"probable":43} |
| contact_contact_status | {"estimated":273} |
| contact_attribution_reason | {"nearest_proximity":272,"ambiguous_proximity":1} |
| contact_trajectory_reliability | {"insufficient":69,"probable":160,"ambiguous":44} |
| contact_trajectory_reasons | {"coherent_motion_change_unavailable":69,"supported_launch":32,"association_unresolved":44,"supported_turn":128} |
| contact_impact_reliability | {"insufficient":142,"ambiguous":88,"probable":43} |
| contact_impact_reasons | {"fresh_player_observation_unavailable":142,"no_fresh_swing_or_racket_overlap":20,"association_unresolved":44,"coherent_motion_and_fresh_contact_cue":43,"coherent_motion_change_unavailable":24} |
| contact_attribution_reliability | {"insufficient":173,"probable":100} |
| contact_attribution_reasons | {"fresh_player_observation_unavailable":173,"geometric_attribution_not_verified_identity":100} |
| rally_end_reason | {"stationary":9,"gap":4,"cut":11} |
| rally_phase | {"unknown":2,"match_play":22} |
| rally_official | {"False":7,"True":17} |
| rally_match_format_known | {"True":24} |
| rally_match_format | {"singles":24} |
| rally_winner | {"None":24} |
| rally_score_transition_status | {"unavailable":16,"candidate":8} |
| rally_admission_reason | {"duration_policy":22,"independent_contact_and_observed_motion_witnesses":2} |

#### Track/export counts

| Field | Observed value |
|---|---|
| camera_rows | 8414 |
| player_rows | 16536 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 16346 |
| projected_court_on_propagated_box | 9392 |
| racket_rows | 5438 |
| shuttle_rows | 8414 |

#### Track/export categories

| Field | Observed value |
|---|---|
| player_id | {"None":16536} |
| detector_matched | {"True":7050,"False":9486} |

| Semantic metric | Observed | Baseline comparison / limitation |
|---|---|---|
| Known rally winner output | 0/24 | Supplied coarse winner labels exist; identity/point mapping uncertified |
| Unknown stroke classification | 191/273 | Coarse one-label-per-rally ball_types is not exhaustive per-shot GT |
| Estimated stroke classification | 82/273 | Estimated coverage is not class accuracy |
| OCR saved readouts | 229 | Observed scoreboard rows, not accepted correct points |
| OCR label counts | {"GEMKE":229,"GINTING":229} | Raw OCR labels may differ from anonymous Player A/B |
| Tracked invalid geometry frames | 96 | Geometric diagnostics, not labelled location error |
| Session degradation | [{"stage":"player_identity","reason":"osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"},{"stage":"player_reid","reason":"baseline player_reid provider is unavailable"}] | Identity/ReID unavailability remains recorded; no new models fetched |

### Runtime, resources and every saved stage latency

| Saved resource/runtime metric | Value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 2311574 |
| parent_failure_inclusive_elapsed_s | — |
| parent_failure_inclusive_source_fps | — |
| neural_only_throughput_fps | — |
| model_loading_time_s | — |
| media_ready_time_s | 1.908980 |
| model_staging_time_s | 1.738413 |
| worker_final_cpu_s | 10532.777135 |
| worker_maxrss_bytes | 2858205184 |
| sampled_worker_tree_peak_rss_bytes | 2827141120 |
| sampled_worker_gpu_peak_mib | 2130 |
| sampled_cpu_seconds_max_observed | 10532.310000 |
| sampled_cpu_seconds_last_observed | 10532.310000 |
| sampled_system_available_ram_min_bytes | 101099823104 |
| sample_count | 417 |
| resource_rows | 417 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 864.429404 |
| parent_completed_source_fps | 9.733588 |
| worker_elapsed_s | 858.445222 |
| worker_source_fps | 9.801441 |
| component_initialization_including_models_s | 9.256680 |

| Stage | Calls | Total wall s | P50 ms/call | P95 ms/call | Minimum ms | Maximum ms | Frame-population sum |
|---|---|---|---|---|---|---|---|
| court | 141 | 44.980530 | 303.707892 | 397.023218 | 259.942448 | 1163.802753 | 8414 |
| content_continuity_and_players | 141 | 384.749320 | 3060.139280 | 3293.816947 | 280.580762 | 3451.395210 | 8414 |
| shuttle | 141 | 123.681311 | 858.993502 | 1076.536467 | 250.472095 | 1447.006815 | 8414 |
| players | 141 | 37.532983 | 243.661861 | 566.549821 | 10.050390 | 651.687329 | 8414 |
| ocr | 141 | 122.473012 | 858.351107 | 922.827067 | 0.023184 | 1514.934904 | 8414 |

| Runner timing scope | Seconds |
|---|---|
| component_initialization_including_models_s | 9.256680 |
| decode_perception_cache_s | 767.057136 |

| Additional completed-worker timing | Seconds |
|---|---|
| Perception completion catalogue publication | 2.184492 |
| Worker media ready | 1.908980 |
| Model staging | 1.738413 |

| Actual worker reproducibility metadata | Value |
|---|---|
| Visible Torch devices | [{"logical_index":0,"name":"NVIDIA GeForce GTX 1080 Ti","uuid":"a618f090-66bf-ad80-b0a5-0c91bee61fab"}] |
| CUDA_VISIBLE_DEVICES GPU UUID | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| Prior cached perceptions used | false |
| Worker model manifest SHA256 | b5590b8ff1437945da036b42b01729f521728259a0dfc4c3299a926216ba8df3 |
| Worker staged model pins SHA256 | 7bd228ead493bba31c1417c46346d35e3cd00e1760ba7d7b35485d3babf5219f |

The historical timing key decode_perception_cache_s wraps the runner’s full _perceive call. Its name does not mean this was an observation-cache replay: the completed-worker receipts explicitly record cached_perception_used=false. It is a broad perception wall-time scope, not isolated cache decoding or pure GPU latency.

| Saved disk-use metric | Bytes / count |
|---|---|
| regular_files | 874 |
| logical_bytes | 558805324 |
| allocated_bytes | 560607232 |
| staged_model_bytes | 361041769 |
| perception_cache_bytes | 41581068 |

Wall-time scopes overlap; they are not summable GPU kernel latency. Pure neural-only FPS and isolated model-loading time remain unavailable. For historical Tests 1/2, final worker-local timing/CPU/RSS fields were lost at catalogue publication and stay unavailable; failure-inclusive parent duration is identified explicitly. For normal runs, worker elapsed includes the runner and final catalogue verification. Current-process GPU samples cannot certify per-node ORT placement or true instantaneous memory peaks.

### Reproducibility, logs and annotation-file review

| Binding | Value |
|---|---|
| Normalized numerical profile SHA256 (passive ranges removed) | 2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb |
| Effective profile canonical SHA256 | 2ebd3bb44d6bd8cfbec992ae4d4f8e75f9f911488148318877650047b164def0 |
| Model identity sets | 1 |
| Runtime identity sets | 1 |
| Actual model identity SHA256 | e3c96b7c2e522fd6efe6106328bebec30137f29b7303fe5e475f8aedea5d2222 |
| Actual runtime identity SHA256 | 81e41f18d858ed37c34ce9d07ae34a34268f27e57c0e5f878e07253be309066f |
| Executed plan | [plan.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test3/protocol/plan.json) |
| Actual completion receipt | [inference.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test3/run/inference.json) |
| Per-rally saved CSV | [per_rally_comparison.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test3/evaluation/per_rally_comparison.csv) |
| Technical analysis | [technical_analysis.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test3/analysis/technical_analysis.json) |
| Full original predictions | [predicted_rallies.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test3/run/predicted_rallies.csv) |

| Annotation file | Role | Data rows | Blank rows | Bytes | Column/schema inventory | SHA256 |
|---|---|---|---|---|---|---|
| Test3_Full.csv | Secondary coarse outcome/time reference | 22 | 0 | 1659 | ["start_time","end_time","win_point_player","win_reason","ball_types","lose_reason","roundscore_A","roundscore_B"] | 85801c06250025f71c347f0f5305c7a9a52763c9aa8b02a211309e3aba14f01d |
| Test3_Full_Rev_T4.csv | Auxiliary historical/generated artifact; not certified independent truth | 19 | 0 | 1403 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 252e4f43e3f719a18b112ab85d087ce4b2d50aec976ee4863114a9c0bb3b98d8 |
| Test3_Full_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 8414 | 0 | 176447 | ["Frame","X","Y","Visibility","Confidence"] | a3bf0834777d8a744b8165b5570b111d3b4f7f281eab33acdcbd55667805976d |
| Test3_Full_court.json | Auxiliary historical/generated artifact; not certified independent truth | — | — | 670 | ["frame_no","frame_size","corners","net","source"] | a7a4c224cb8e9db5747ce1ff598487f760bcd6cfcd14679adee03d483092e199 |
| Test3_Full_rally.csv | Primary timing reference | 19 | 0 | 1403 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 252e4f43e3f719a18b112ab85d087ce4b2d50aec976ee4863114a9c0bb3b98d8 |
| player_detections.csv | Auxiliary historical/generated artifact; not certified independent truth | 8414 | 0 | 941945 | ["frame_no","player_1_x","player_1_y","player_1_conf","player_2_x","player_2_y","player_2_conf"] | 39106d1c9193557775c2c0830b8e365baf9fc952c43cd17f94baf7f0f279c475 |
| win_predictions.csv | Auxiliary historical/generated artifact; not certified independent truth | 19 | 0 | 2411 | ["rally_idx","start_frame","end_frame","start_time","end_time","winner","loser","win_reason","reason_src","fault_side","fault_src","cnn_class","cnn_conf","cnn_oob","cnn_hn","cnn_wbl","score_Player A","score_Player B"] | c0362fe9e0856f868f90cb5b825f1bf2e4e5aa0f50f9b6d8912d5087c9b3df42 |

| Log | Lines | Warning/error-pattern lines | Distinct observed warning/error messages |
|---|---|---|---|
| analysis.log | 1 | 0 | [] |
| download.log | 70 | 0 | [] |
| evaluation.log | 0 | 0 | [] |
| prepare.log | 0 | 0 | [] |
| run.execution.log | 26 | 10 | ["2026-11-06 00:27:39 [warning  ] perception.degraded            reason='osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`' stage=player_identity","2026-11-06 00:27:39 [warning  ] perception.degraded            reason='baseline player_reid provider is unavailable' stage=player_reid","[WARNING] 2026-11-06 00:28:28,993 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:28:52,810 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:28:57,891 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:29:13,107 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:34:54,399 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:35:06,379 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:35:52,140 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:36:03,992 [RapidOCR] main.py:164: The text detection result is empty"] |
| run.launch.log | 0 | 0 | [] |
| timestamps.log | 1 | 0 | [] |

Log keyword counts are diagnostic string matches, not failed-inference counts. Tests 1/2 raw original worker logs remain in their source run directories and retain the known final catalogue failure; their independent completion proof is the accepted completion record. All previously completed evaluations remain immutable.

### Duration breakdown for this video

| GT duration bin | GT count | Matched | Missed | Recall | Start MAE f | End MAE f |
|---|---|---|---|---|---|---|
| ≤2 s | 0 | 0 | 0 | — | — | — |
| (2,5] s | 5 | 5 | 0 | 1.000000 | 3.800000 | 3.200000 |
| (5,10] s | 2 | 2 | 0 | 1.000000 | 2.500000 | 4.500000 |
| (10,20] s | 10 | 9 | 1 | 0.900000 | 52.666667 | 13.111111 |
| >20 s | 2 | 2 | 0 | 1.000000 | 8.500000 | 5.000000 |

## Test 4: complete evaluation and ground-truth comparison

Reference **41 rallies**, predictions **46**; TP/FP/FN **38/8/3**. Precision **82.609%**, recall **92.683%**, F1 **87.356%**. Matched mean IoU **0.821815**. The ground-truth benchmark for every table in this primary section is [Test4_Full_rally.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test4_Full/Test4_Full_rally.csv).

| Input / execution binding | Value |
|---|---|
| Decoded frames | 20034 |
| FPS | 30.000000 |
| Video duration seconds | 667.800000 |
| Canonical dimensions | 1280 × 720 |
| Source SHA256 | adff61dad4741ea6e8220c5d3292ddb0578b3c91b9e724f49b6f6608203558ed |
| Proxy SHA256 | 847e1c778a65559f8132c132b39d8f3259d38a8ddd7f392c85b22d86cc658d68 |
| Prediction SHA256 | 97c35364c4d2273de919ec2bd6086ec9680c4ad5e692276a094f21bd05ee74f9 |
| Ground-truth SHA256 | 313d62a10401d502cc206f8a398b07297d9886a4d193df3629be128002dde39c |
| Coarse reference SHA256 | b22eb3d20e8ff02e9f689ba46d33ae18ae60c3780399d021eaea753725df13c4 |
| Session | UPLOADTEST4 |
| Actual completion mode | normal_completed_worker |
| Original parent receipt status | completed |
| Full source/proxy PTS matches | 20034 |
| Scene probe pixel hashes verified | 2 |
| Verified saved files / logical bytes | 2340 / 796531230 |
| Read-only record | [saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test4) |

### Primary metric scores versus the ground-truth ideal

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 41 | 41 | 0 |
| Prediction count | 41 | 46 | 5 |
| TP / matched | 41 | 38 | -3 |
| FP | 0 | 8 | 8 |
| FN / missed | 0 | 3 | 3 |
| precision | 1 | 0.826087 | -0.173913 |
| recall | 1 | 0.926829 | -0.073171 |
| f1 | 1 | 0.873563 | -0.126437 |
| Mean matched IoU | 1 | 0.821815 | -0.178185 |
| Median matched IoU | 1 | 0.861752 | -0.138248 |
| Minimum matched IoU | 1 | 0.519403 | -0.480597 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 76.315789 |
| 0.9 | 100 | 42.105263 |
| 0.95 | 100 | 18.421053 |

A GT self-comparison has TP=N, FP=FN=0, precision/recall/F1=1, IoU=1 and every timing/duration error=0. This is the reference ideal, not a separately executed baseline model. The signed count difference alone is insufficient: false positives and misses can cancel.

### Boundary and duration errors versus zero-error ground truth

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 31.289474 | 19.000000 | 43.298535 | 104.000000 | 78.700000 | 23.868421 | 12.000000 |
| end_frame | 26.842105 | 11.000000 | 54.005360 | 248.000000 | 59.200000 | -12.526316 | 0.000000 |
| start_time_sec | 1.042982 | 0.633333 | 1.443285 | 3.466667 | 2.623333 | 0.795614 | 0.400000 |
| end_time_sec | 0.894737 | 0.366667 | 1.800179 | 8.266667 | 1.973333 | -0.417544 | 0.000000 |
| duration_sec | 1.532456 | 0.750000 | 2.431127 | 9.633333 | 3.366667 | -1.213158 | -0.633333 |

| Additional saved statistic | Value | Ground-truth ideal |
|---|---|---|
| Start P95 \|error\| frames | 95.300000 | 0 |
| End P95 \|error\| frames | 107.250000 | 0 |
| Duration mae frames | 45.973684 | 0 |
| Duration rmse frames | 72.933820 | 0 |
| Duration signed_bias frames | -36.394737 | 0 |

All error statistics above condition on eligible matched rallies. A positive start error is a late start; a negative start error is early. A positive end error is a late end; a negative end error is premature. Duration error is prediction minus GT. All 30 FPS frame errors convert by dividing by30; full signed/absolute per-rally values appear below. Misses have no invented zero error.

### Boundary tolerance scores

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 0 | 38 | 0.000% | 41 | 0.000% | 100% |
| start | 3 | 0.100000 | 1 | 38 | 2.632% | 41 | 2.439% | 100% |
| start | 5 | 0.166667 | 5 | 38 | 13.158% | 41 | 12.195% | 100% |
| start | 10 | 0.333333 | 15 | 38 | 39.474% | 41 | 36.585% | 100% |
| start | 15 | 0.500000 | 18 | 38 | 47.368% | 41 | 43.902% | 100% |
| start | 30 | 1.000000 | 24 | 38 | 63.158% | 41 | 58.537% | 100% |
| end | 1 | 0.033333 | 4 | 38 | 10.526% | 41 | 9.756% | 100% |
| end | 3 | 0.100000 | 7 | 38 | 18.421% | 41 | 17.073% | 100% |
| end | 5 | 0.166667 | 8 | 38 | 21.053% | 41 | 19.512% | 100% |
| end | 10 | 0.333333 | 19 | 38 | 50.000% | 41 | 46.341% | 100% |
| end | 15 | 0.500000 | 23 | 38 | 60.526% | 41 | 56.098% | 100% |
| end | 30 | 1.000000 | 31 | 38 | 81.579% | 41 | 75.610% | 100% |

### All saved error distributions

| Distribution / units | N | Mean | Median | Minimum | Maximum | P90 | P95 | Ideal |
|---|---|---|---|---|---|---|---|---|
| matched_iou | 38 | 0.821815 | 0.861752 | 0.519403 | 0.981530 | 0.960497 | 0.975002 | 1 |
| start_signed_frames | 38 | 23.868421 | 12.000000 | -62.000000 | 104.000000 | 78.700000 | 95.300000 | 0 |
| start_absolute_frames | 38 | 31.289474 | 19.000000 | 3.000000 | 104.000000 | 78.700000 | 95.300000 | 0 |
| end_signed_frames | 38 | -12.526316 | 0.000000 | -248.000000 | 58.000000 | 20.600000 | 27.900000 | 0 |
| end_absolute_frames | 38 | 26.842105 | 11.000000 | 0.000000 | 248.000000 | 59.200000 | 107.250000 | 0 |
| duration_signed_frames | 38 | -36.394737 | -19.000000 | -289.000000 | 70.000000 | 9.900000 | 34.550000 | 0 |
| duration_absolute_frames | 38 | 45.973684 | 22.500000 | 1.000000 | 289.000000 | 101.000000 | 149.100000 | 0 |
| duration_signed_seconds | 38 | -1.213158 | -0.633333 | -9.633333 | 2.333333 | 0.330000 | 1.151667 | 0 |

### Misses, extras, overlap topology and failure review

| Diagnostic | Observed | GT ideal / interpretation |
|---|---|---|
| Missed GT IDs | [1,14,25] | [] |
| Unmatched prediction IDs | [1,5,7,10,17,28,31,45] | [] |
| No-overlap missed GT IDs | [] | [] |
| Predictions without any GT overlap | [10,31] | [] |
| Possible split GT IDs | [4,5,38,40] | Geometric overlap candidates; not adjudicated semantic splits |
| Possible merge prediction IDs | [41] | Geometric overlap candidates; not adjudicated semantic merges |
| Significant failure records | 30 | Unmatched or \|boundary error\|>30frames or IoU<0.75 |
| early_start_gt_ids | [3,4,13,21,22,35] | Direction/weak-overlap inventory, not a physical cause |
| late_start_gt_ids | [2,5,6,7,8,9,10,11,12,15,16,17,18,19,20,23,24,26,27,28,29,30,31,32,33,34,36,37,38,39,40,41] | Direction/weak-overlap inventory, not a physical cause |
| premature_end_gt_ids | [2,3,4,5,7,8,10,11,22,24,26,27,29,31,32,34,39,40] | Direction/weak-overlap inventory, not a physical cause |
| late_end_gt_ids | [6,12,13,15,16,17,18,19,20,21,23,28,30,35,36,37,41] | Direction/weak-overlap inventory, not a physical cause |
| weak_iou_gt_ids | [5,6,11,16,17,18,29,34,40] | Direction/weak-overlap inventory, not a physical cause |

| Inventory validity | Ground truth | Predictions |
|---|---|---|
| count | 41 | 46 |
| duplicate_row_pairs | [] | [] |
| positive_overlap_row_pairs | [] | [] |
| adjacent_row_pairs | [] | [] |
| out_of_range_rows | [] | [] |
| out_of_order_rows | [] | [] |

| False detection P ID | Start frame | End frame | Start seconds | End seconds | Duration seconds | Positive-overlap GT IDs |
|---|---|---|---|---|---|---|
| 1 | 363 | 435 | 12.100000 | 14.500000 | 2.400000 | [1] |
| 5 | 2380 | 2449 | 79.333333 | 81.633333 | 2.300000 | [4] |
| 7 | 2971 | 3143 | 99.033333 | 104.766667 | 5.733333 | [5] |
| 10 | 4271 | 4336 | 142.366667 | 144.533333 | 2.166667 | [] |
| 17 | 6787 | 6978 | 226.233333 | 232.600000 | 6.366667 | [14] |
| 28 | 12988 | 13085 | 432.933333 | 436.166667 | 3.233333 | [25] |
| 31 | 13959 | 14072 | 465.300000 | 469.066667 | 3.766667 | [] |
| 45 | 19575 | 19702 | 652.500000 | 656.733333 | 4.233333 | [40] |

| Largest matched boundary cases | P ID | GT start/end frames | Pred start/end frames | Δstart frames | Δend frames | IoU |
|---|---|---|---|---|---|---|
| 5 | 6 | 2502–3138 | 2543–2890 | 41 | -248 | 0.545597 |
| 40 | 44 | 19379–19714 | 19386–19560 | 7 | -154 | 0.519403 |
| 6 | 8 | 3197–3495 | 3301–3505 | 104 | 10 | 0.629870 |
| 4 | 4 | 1849–2445 | 1828–2346 | -21 | -99 | 0.805511 |
| 2 | 2 | 523–1197 | 620–1179 | 97 | -18 | 0.829377 |

Of 3 unmatched reference intervals, 0 have no positive overlap with any prediction; 3 have some overlap but fail the one-to-one IoU eligibility/assignment. This separates absence of overlap from insufficient interval agreement without inventing a causal diagnosis.

### Every GT rally compared directly with its assigned prediction: frames

G IDs are one-based CSV row IDs in the primary rally reference. P IDs are one-based rows in the preserved prediction CSV. C IDs refer to the separate coarse table, linked only by the same IoU-based temporal crosswalk. “—” denotes unavailable/unmatched, not zero.

| G | P | GT start f | GT end f | Pred start f | Pred end f | Δstart f | \|Δstart\| f | Δend f | \|Δend\| f | IoU | Status | Coarse C row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | — | 265 | 435 | — | — | — | — | — | — | — | missed | 1 |
| 2 | 2 | 523 | 1197 | 620 | 1179 | 97 | 97 | -18 | 18 | 0.829377 | matched | 2 |
| 3 | 3 | 1320 | 1721 | 1293 | 1671 | -27 | 27 | -50 | 50 | 0.820093 | matched | 3 |
| 4 | 4 | 1849 | 2445 | 1828 | 2346 | -21 | 21 | -99 | 99 | 0.805511 | matched | 4 |
| 5 | 6 | 2502 | 3138 | 2543 | 2890 | 41 | 41 | -248 | 248 | 0.545597 | matched | 5 |
| 6 | 8 | 3197 | 3495 | 3301 | 3505 | 104 | 104 | 10 | 10 | 0.629870 | matched | 7 |
| 7 | 9 | 3592 | 4081 | 3606 | 4075 | 14 | 14 | -6 | 6 | 0.959100 | matched | 8 |
| 8 | 11 | 4546 | 4668 | 4552 | 4667 | 6 | 6 | -1 | 1 | 0.942623 | matched | 10 |
| 9 | 12 | 4789 | 5036 | 4803 | 5036 | 14 | 14 | 0 | 0 | 0.943320 | matched | 11 |
| 10 | 13 | 5157 | 5235 | 5164 | 5225 | 7 | 7 | -10 | 10 | 0.782051 | matched | 12 |
| 11 | 14 | 5290 | 5661 | 5375 | 5599 | 85 | 85 | -62 | 62 | 0.603774 | matched | 13 |
| 12 | 15 | 6099 | 6320 | 6120 | 6353 | 21 | 21 | 33 | 33 | 0.787402 | matched | 14 |
| 13 | 16 | 6429 | 6705 | 6411 | 6719 | -18 | 18 | 14 | 14 | 0.896104 | matched | 15 |
| 14 | — | 6776 | 6865 | — | — | — | — | — | — | — | missed | — |
| 15 | 18 | 7114 | 7645 | 7150 | 7651 | 36 | 36 | 6 | 6 | 0.921788 | matched | 17 |
| 16 | 19 | 7790 | 7914 | 7826 | 7941 | 36 | 36 | 27 | 27 | 0.582781 | matched | 18 |
| 17 | 20 | 7959 | 8250 | 8030 | 8269 | 71 | 71 | 19 | 19 | 0.709677 | matched | 19 |
| 18 | 21 | 8309 | 8632 | 8385 | 8645 | 76 | 76 | 13 | 13 | 0.735119 | matched | 20 |
| 19 | 22 | 8827 | 9258 | 8834 | 9270 | 7 | 7 | 12 | 12 | 0.957111 | matched | 21 |
| 20 | 23 | 9361 | 9895 | 9369 | 9901 | 8 | 8 | 6 | 6 | 0.974074 | matched | 22 |
| 21 | 24 | 9942 | 10031 | 9937 | 10035 | -5 | 5 | 4 | 4 | 0.908163 | matched | 23 |
| 22 | 25 | 10522 | 11272 | 10514 | 11266 | -8 | 8 | -6 | 6 | 0.981530 | matched | 24 |
| 23 | 26 | 11527 | 12122 | 11537 | 12134 | 10 | 10 | 12 | 12 | 0.963756 | matched | 25 |
| 24 | 27 | 12398 | 12702 | 12401 | 12699 | 3 | 3 | -3 | 3 | 0.980263 | matched | 26 |
| 25 | — | 12830 | 13060 | — | — | — | — | — | — | — | missed | — |
| 26 | 29 | 13342 | 13480 | 13357 | 13473 | 15 | 15 | -7 | 7 | 0.840580 | matched | 29 |
| 27 | 30 | 13625 | 13835 | 13631 | 13825 | 6 | 6 | -10 | 10 | 0.923810 | matched | 30 |
| 28 | 32 | 14195 | 14430 | 14204 | 14488 | 9 | 9 | 58 | 58 | 0.771331 | matched | 32 |
| 29 | 33 | 14636 | 14829 | 14695 | 14809 | 59 | 59 | -20 | 20 | 0.590674 | matched | 33 |
| 30 | 34 | 14891 | 15116 | 14911 | 15118 | 20 | 20 | 2 | 2 | 0.903084 | matched | 34 |
| 31 | 35 | 15287 | 15422 | 15293 | 15396 | 6 | 6 | -26 | 26 | 0.762963 | matched | 35 |
| 32 | 36 | 15605 | 15763 | 15610 | 15746 | 5 | 5 | -17 | 17 | 0.860759 | matched | 36 |
| 33 | 37 | 15786 | 16418 | 15833 | 16418 | 47 | 47 | 0 | 0 | 0.925633 | matched | 37 |
| 34 | 38 | 16432 | 16577 | 16489 | 16569 | 57 | 57 | -8 | 8 | 0.551724 | matched | 38 |
| 35 | 39 | 16779 | 17219 | 16717 | 17227 | -62 | 62 | 8 | 8 | 0.862745 | matched | 39 |
| 36 | 40 | 17253 | 17699 | 17279 | 17719 | 26 | 26 | 20 | 20 | 0.901288 | matched | 40 |
| 37 | 41 | 17846 | 18261 | 17897 | 18283 | 51 | 51 | 22 | 22 | 0.832952 | matched | 41 |
| 38 | 42 | 18281 | 18987 | 18376 | 18987 | 95 | 95 | 0 | 0 | 0.865439 | matched | 42 |
| 39 | 43 | 19026 | 19181 | 19030 | 19178 | 4 | 4 | -3 | 3 | 0.954839 | matched | — |
| 40 | 44 | 19379 | 19714 | 19386 | 19560 | 7 | 7 | -154 | 154 | 0.519403 | matched | — |
| 41 | 46 | 19852 | 19959 | 19857 | 19965 | 5 | 5 | 6 | 6 | 0.902655 | matched | 45 |

### Every GT rally compared directly: timestamps and durations

| G | GT start s | GT end s | Pred start s | Pred end s | GT duration s | Pred duration s | Δstart s | \|Δstart\| s | Δend s | \|Δend\| s | Δduration s | \|Δduration\| s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8.833333 | 14.500000 | — | — | 5.666667 | — | — | — | — | — | — | — |
| 2 | 17.433333 | 39.900000 | 20.666667 | 39.300000 | 22.466667 | 18.633333 | 3.233333 | 3.233333 | -0.600000 | 0.600000 | -3.833333 | 3.833333 |
| 3 | 44.000000 | 57.366667 | 43.100000 | 55.700000 | 13.366667 | 12.600000 | -0.900000 | 0.900000 | -1.666667 | 1.666667 | -0.766667 | 0.766667 |
| 4 | 61.633333 | 81.500000 | 60.933333 | 78.200000 | 19.866667 | 17.266667 | -0.700000 | 0.700000 | -3.300000 | 3.300000 | -2.600000 | 2.600000 |
| 5 | 83.400000 | 104.600000 | 84.766667 | 96.333333 | 21.200000 | 11.566667 | 1.366667 | 1.366667 | -8.266667 | 8.266667 | -9.633333 | 9.633333 |
| 6 | 106.566667 | 116.500000 | 110.033333 | 116.833333 | 9.933333 | 6.800000 | 3.466667 | 3.466667 | 0.333333 | 0.333333 | -3.133333 | 3.133333 |
| 7 | 119.733333 | 136.033333 | 120.200000 | 135.833333 | 16.300000 | 15.633333 | 0.466667 | 0.466667 | -0.200000 | 0.200000 | -0.666667 | 0.666667 |
| 8 | 151.533333 | 155.600000 | 151.733333 | 155.566667 | 4.066667 | 3.833333 | 0.200000 | 0.200000 | -0.033333 | 0.033333 | -0.233333 | 0.233333 |
| 9 | 159.633333 | 167.866667 | 160.100000 | 167.866667 | 8.233333 | 7.766667 | 0.466667 | 0.466667 | 0.000000 | 0.000000 | -0.466667 | 0.466667 |
| 10 | 171.900000 | 174.500000 | 172.133333 | 174.166667 | 2.600000 | 2.033333 | 0.233333 | 0.233333 | -0.333333 | 0.333333 | -0.566667 | 0.566667 |
| 11 | 176.333333 | 188.700000 | 179.166667 | 186.633333 | 12.366667 | 7.466667 | 2.833333 | 2.833333 | -2.066667 | 2.066667 | -4.900000 | 4.900000 |
| 12 | 203.300000 | 210.666667 | 204.000000 | 211.766667 | 7.366667 | 7.766667 | 0.700000 | 0.700000 | 1.100000 | 1.100000 | 0.400000 | 0.400000 |
| 13 | 214.300000 | 223.500000 | 213.700000 | 223.966667 | 9.200000 | 10.266667 | -0.600000 | 0.600000 | 0.466667 | 0.466667 | 1.066667 | 1.066667 |
| 14 | 225.866667 | 228.833333 | — | — | 2.966667 | — | — | — | — | — | — | — |
| 15 | 237.133333 | 254.833333 | 238.333333 | 255.033333 | 17.700000 | 16.700000 | 1.200000 | 1.200000 | 0.200000 | 0.200000 | -1.000000 | 1.000000 |
| 16 | 259.666667 | 263.800000 | 260.866667 | 264.700000 | 4.133333 | 3.833333 | 1.200000 | 1.200000 | 0.900000 | 0.900000 | -0.300000 | 0.300000 |
| 17 | 265.300000 | 275.000000 | 267.666667 | 275.633333 | 9.700000 | 7.966667 | 2.366667 | 2.366667 | 0.633333 | 0.633333 | -1.733333 | 1.733333 |
| 18 | 276.966667 | 287.733333 | 279.500000 | 288.166667 | 10.766667 | 8.666667 | 2.533333 | 2.533333 | 0.433333 | 0.433333 | -2.100000 | 2.100000 |
| 19 | 294.233333 | 308.600000 | 294.466667 | 309.000000 | 14.366667 | 14.533333 | 0.233333 | 0.233333 | 0.400000 | 0.400000 | 0.166667 | 0.166667 |
| 20 | 312.033333 | 329.833333 | 312.300000 | 330.033333 | 17.800000 | 17.733333 | 0.266667 | 0.266667 | 0.200000 | 0.200000 | -0.066667 | 0.066667 |
| 21 | 331.400000 | 334.366667 | 331.233333 | 334.500000 | 2.966667 | 3.266667 | -0.166667 | 0.166667 | 0.133333 | 0.133333 | 0.300000 | 0.300000 |
| 22 | 350.733333 | 375.733333 | 350.466667 | 375.533333 | 25.000000 | 25.066667 | -0.266667 | 0.266667 | -0.200000 | 0.200000 | 0.066667 | 0.066667 |
| 23 | 384.233333 | 404.066667 | 384.566667 | 404.466667 | 19.833333 | 19.900000 | 0.333333 | 0.333333 | 0.400000 | 0.400000 | 0.066667 | 0.066667 |
| 24 | 413.266667 | 423.400000 | 413.366667 | 423.300000 | 10.133333 | 9.933333 | 0.100000 | 0.100000 | -0.100000 | 0.100000 | -0.200000 | 0.200000 |
| 25 | 427.666667 | 435.333333 | — | — | 7.666667 | — | — | — | — | — | — | — |
| 26 | 444.733333 | 449.333333 | 445.233333 | 449.100000 | 4.600000 | 3.866667 | 0.500000 | 0.500000 | -0.233333 | 0.233333 | -0.733333 | 0.733333 |
| 27 | 454.166667 | 461.166667 | 454.366667 | 460.833333 | 7.000000 | 6.466667 | 0.200000 | 0.200000 | -0.333333 | 0.333333 | -0.533333 | 0.533333 |
| 28 | 473.166667 | 481.000000 | 473.466667 | 482.933333 | 7.833333 | 9.466667 | 0.300000 | 0.300000 | 1.933333 | 1.933333 | 1.633333 | 1.633333 |
| 29 | 487.866667 | 494.300000 | 489.833333 | 493.633333 | 6.433333 | 3.800000 | 1.966667 | 1.966667 | -0.666667 | 0.666667 | -2.633333 | 2.633333 |
| 30 | 496.366667 | 503.866667 | 497.033333 | 503.933333 | 7.500000 | 6.900000 | 0.666667 | 0.666667 | 0.066667 | 0.066667 | -0.600000 | 0.600000 |
| 31 | 509.566667 | 514.066667 | 509.766667 | 513.200000 | 4.500000 | 3.433333 | 0.200000 | 0.200000 | -0.866667 | 0.866667 | -1.066667 | 1.066667 |
| 32 | 520.166667 | 525.433333 | 520.333333 | 524.866667 | 5.266667 | 4.533333 | 0.166667 | 0.166667 | -0.566667 | 0.566667 | -0.733333 | 0.733333 |
| 33 | 526.200000 | 547.266667 | 527.766667 | 547.266667 | 21.066667 | 19.500000 | 1.566667 | 1.566667 | 0.000000 | 0.000000 | -1.566667 | 1.566667 |
| 34 | 547.733333 | 552.566667 | 549.633333 | 552.300000 | 4.833333 | 2.666667 | 1.900000 | 1.900000 | -0.266667 | 0.266667 | -2.166667 | 2.166667 |
| 35 | 559.300000 | 573.966667 | 557.233333 | 574.233333 | 14.666667 | 17.000000 | -2.066667 | 2.066667 | 0.266667 | 0.266667 | 2.333333 | 2.333333 |
| 36 | 575.100000 | 589.966667 | 575.966667 | 590.633333 | 14.866667 | 14.666667 | 0.866667 | 0.866667 | 0.666667 | 0.666667 | -0.200000 | 0.200000 |
| 37 | 594.866667 | 608.700000 | 596.566667 | 609.433333 | 13.833333 | 12.866667 | 1.700000 | 1.700000 | 0.733333 | 0.733333 | -0.966667 | 0.966667 |
| 38 | 609.366667 | 632.900000 | 612.533333 | 632.900000 | 23.533333 | 20.366667 | 3.166667 | 3.166667 | 0.000000 | 0.000000 | -3.166667 | 3.166667 |
| 39 | 634.200000 | 639.366667 | 634.333333 | 639.266667 | 5.166667 | 4.933333 | 0.133333 | 0.133333 | -0.100000 | 0.100000 | -0.233333 | 0.233333 |
| 40 | 645.966667 | 657.133333 | 646.200000 | 652.000000 | 11.166667 | 5.800000 | 0.233333 | 0.233333 | -5.133333 | 5.133333 | -5.366667 | 5.366667 |
| 41 | 661.733333 | 665.300000 | 661.900000 | 665.500000 | 3.566667 | 3.600000 | 0.166667 | 0.166667 | 0.200000 | 0.200000 | 0.033333 | 0.033333 |

### Secondary coarse/outcome annotations: full supplied baseline and comparison

[Test4_Full.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test4_Full/Test4_Full.csv) contains **45 data rows**, **45 nonblank intervals**, blank row IDs **[]**. This separate reference differs from the 41-interval primary timing table. The same unchanged predictions and matcher give secondary precision **91.304%**, recall **93.333%**, F1 **92.308%**; this reference-sensitivity analysis does not replace the primary benchmark. No labels, times or predictions were fitted or repaired.

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 45 | 45 | 0 |
| Prediction count | 45 | 46 | 1 |
| TP / matched | 45 | 42 | -3 |
| FP | 0 | 4 | 4 |
| FN / missed | 0 | 3 | 3 |
| precision | 1 | 0.913043 | -0.086957 |
| recall | 1 | 0.933333 | -0.066667 |
| f1 | 1 | 0.923077 | -0.076923 |
| Mean matched IoU | 1 | 0.822935 | -0.177065 |
| Median matched IoU | 1 | 0.840000 | -0.160000 |
| Minimum matched IoU | 1 | 0.550388 | -0.449612 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 73.809524 |
| 0.9 | 100 | 35.714286 |
| 0.95 | 100 | 16.666667 |

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 19.404762 | 15.500000 | 25.120187 | 77.000000 | 36.900000 | 18.119048 | 15.000000 |
| end_frame | 27.595238 | 15.000000 | 50.645124 | 213.000000 | 67.900000 | 1.738095 | 5.000000 |
| start_time_sec | 0.646825 | 0.516667 | 0.837340 | 2.566667 | 1.230000 | 0.603968 | 0.500000 |
| end_time_sec | 0.919841 | 0.500000 | 1.688171 | 7.100000 | 2.263333 | 0.057937 | 0.166667 |
| duration_sec | 1.234921 | 0.800000 | 1.898691 | 7.633333 | 2.113333 | -0.546032 | -0.316667 |

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 5 | 42 | 11.905% | 45 | 11.111% | 100% |
| start | 3 | 0.100000 | 6 | 42 | 14.286% | 45 | 13.333% | 100% |
| start | 5 | 0.166667 | 7 | 42 | 16.667% | 45 | 15.556% | 100% |
| start | 10 | 0.333333 | 14 | 42 | 33.333% | 45 | 31.111% | 100% |
| start | 15 | 0.500000 | 21 | 42 | 50.000% | 45 | 46.667% | 100% |
| start | 30 | 1.000000 | 32 | 42 | 76.190% | 45 | 71.111% | 100% |
| end | 1 | 0.033333 | 3 | 42 | 7.143% | 45 | 6.667% | 100% |
| end | 3 | 0.100000 | 4 | 42 | 9.524% | 45 | 8.889% | 100% |
| end | 5 | 0.166667 | 10 | 42 | 23.810% | 45 | 22.222% | 100% |
| end | 10 | 0.333333 | 16 | 42 | 38.095% | 45 | 35.556% | 100% |
| end | 15 | 0.500000 | 23 | 42 | 54.762% | 45 | 51.111% | 100% |
| end | 30 | 1.000000 | 36 | 42 | 85.714% | 45 | 80.000% | 100% |

| Cross-reference timing diagnostic | Value |
|---|---|
| Primary-to-coarse eligible matched intervals | 37 |
| Primary intervals unmatched to coarse reference | [14,25,39,40] |
| Coarse rows unmatched to primary reference | [6,9,16,27,28,31,43,44] |
| Primary/coarse matched mean IoU | 0.823469 |

| C source row | Supplied start | Supplied end | Supplied winner | Supplied A:B score | Supplied shot / ball_types | Win reason | Lose reason | Matched P | IoU | Δstart s | Δend s | Δduration s | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 00:11 | 00:15 | Player B | 0:1 | Smash | Opponent Hit the Net | Hit the Net | 1 | 0.600000 | 1.100000 | -0.500000 | -1.600000 | matched |
| 2 | 00:20 | 00:40 | Player B | 1:2 | Clear | Opponent Out of Bounds | Out of Bounds | 2 | 0.931667 | 0.666667 | -0.700000 | -1.366667 | matched |
| 3 | 00:42 | 00:56 | Player A | 2:2 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 3 | 0.900000 | 1.100000 | -0.300000 | -1.400000 | matched |
| 4 | 01:00 | 01:22 | Player B | 2:3 | Clear | Winner Shot | Opponent Failed to Return | 4 | 0.784848 | 0.933333 | -3.800000 | -4.733333 | matched |
| 5 | 01:24 | 01:37 | Player B | 2:4 | Net Kill | Winner Shot | Opponent Failed to Return | 6 | 0.889744 | 0.766667 | -0.666667 | -1.433333 | matched |
| 6 | 01:39 | 01:45 | Player B | 2:5 | Push Shot | Winner Shot | Opponent Failed to Return | 7 | 0.955556 | 0.033333 | -0.233333 | -0.266667 | matched |
| 7 | 01:50 | 01:56 | Player A | 3:5 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 8 | 0.873171 | 0.033333 | 0.833333 | 0.800000 | matched |
| 8 | 01:59 | 02:16 | Player A | 5:5 | Net Shot | Opponent Hit the Net | Hit the Net | 9 | 0.919608 | 1.200000 | -0.166667 | -1.366667 | matched |
| 9 | 02:22 | 02:24 | Player B | 6:6 | Net Shot | Winner Shot | Opponent Failed to Return | 10 | 0.644737 | 0.366667 | 0.533333 | 0.166667 | matched |
| 10 | 02:31 | 02:35 | Player A | 7:8 | Smash | Winner Shot | Opponent Failed to Return | 11 | 0.715328 | 0.733333 | 0.566667 | -0.166667 | matched |
| 11 | 02:39 | 02:48 | Player B | 7:9 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 12 | 0.862963 | 1.100000 | -0.133333 | -1.233333 | matched |
| 12 | 02:51 | 02:54 | Player B | 8:10 | Net Kill | Opponent Out of Bounds | Out of Bounds | 13 | 0.589474 | 1.133333 | 0.166667 | -0.966667 | matched |
| 13 | 02:59 | 03:09 | Player B | 8:11 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 14 | 0.746667 | 0.166667 | -2.366667 | -2.533333 | matched |
| 14 | 03:24 | 03:31 | Player A | 9:11 | Net Shot | Opponent Hit the Net | Hit the Net | 15 | 0.901288 | 0.000000 | 0.766667 | 0.766667 | matched |
| 15 | 03:32 | 03:43 | Player B | 9:13 | Clear | Opponent Out of Bounds | Out of Bounds | 16 | 0.777159 | 1.700000 | 0.966667 | -0.733333 | matched |
| 16 | 03:46 | 03:53 | Player A | 10:13 | Defensive Lift | Winner Shot | Opponent Failed to Return | 17 | 0.909524 | 0.233333 | -0.400000 | -0.633333 | matched |
| 17 | 03:58 | 04:15 | Player A | 13:15 | Push Shot | Opponent Out of Bounds | Out of Bounds | 18 | 0.978474 | 0.333333 | 0.033333 | -0.300000 | matched |
| 18 | 04:20 | 04:24 | Player B | 13:16 | Block | Opponent Out of Bounds | Out of Bounds | 19 | 0.666667 | 0.866667 | 0.700000 | -0.166667 | matched |
| 19 | 04:27 | 04:35 | Player A | 14:16 | Lift Shot | Opponent Out of Bounds | Out of Bounds | 20 | 0.849421 | 0.666667 | 0.633333 | -0.033333 | matched |
| 20 | 04:39 | 04:48 | Player B | 14:17 | Net Shot | Winner Shot | Opponent Failed to Return | 21 | 0.927273 | 0.500000 | 0.166667 | -0.333333 | matched |
| 21 | 04:55 | 05:09 | Player A | 15:17 | Drive Defense | Opponent Out of Bounds | Out of Bounds | 22 | 0.963303 | -0.533333 | 0.000000 | 0.533333 | matched |
| 22 | 05:12 | 05:30 | Player A | 16:18 | Block | Opponent Hit the Net | Hit the Net | 23 | 0.981516 | 0.300000 | 0.033333 | -0.266667 | matched |
| 23 | 05:31 | 05:34 | Player A | 18:19 | Defensive Slice | Opponent Out of Bounds | Out of Bounds | 24 | 0.790476 | 0.233333 | 0.500000 | 0.266667 | matched |
| 24 | 05:50 | 06:10 | Player A | 19:19 | Clear | Opponent Out of Bounds | Out of Bounds | 25 | 0.765013 | 0.466667 | 5.533333 | 5.066667 | matched |
| 25 | 06:24 | 06:44 | Player B | 19:20 | Slice | Opponent Out of Bounds | Out of Bounds | 26 | 0.949511 | 0.566667 | 0.466667 | -0.100000 | matched |
| 26 | 06:53 | 07:01 | Player A | 1:0 | Net Shot | Opponent Hit the Net | Hit the Net | 27 | 0.741100 | 0.366667 | 2.300000 | 1.933333 | matched |
| 27 | 07:07 | 07:09 | Player B | 1:2 | Smash | Opponent Hit the Net | Hit the Net | — | — | — | — | — | missed |
| 28 | 07:12 | 07:15 | Player B | 1:4 | Net Kill | Opponent Hit the Net | Hit the Net | — | — | — | — | — | missed |
| 29 | 07:24 | 07:29 | Player A | 2:4 | Smash | Winner Shot | Opponent Failed to Return | 29 | 0.738562 | 1.233333 | 0.100000 | -1.133333 | matched |
| 30 | 07:34 | 07:41 | Player B | 4:5 | Net Kill | Winner Shot | Opponent Failed to Return | 30 | 0.923810 | 0.366667 | -0.166667 | -0.533333 | matched |
| 31 | 07:44 | 07:47 | Player A | 6:5 | Net Shot | Opponent Hit the Net | Hit the Net | — | — | — | — | — | missed |
| 32 | 07:53 | 08:01 | Player A | 7:5 | Net Shot | Winner Shot | Opponent Failed to Return | 32 | 0.758389 | 0.466667 | 1.933333 | 1.466667 | matched |
| 33 | 08:09 | 08:14 | Player A | 8:6 | Net Kill | Opponent Out of Bounds | Out of Bounds | 33 | 0.760000 | 0.833333 | -0.366667 | -1.200000 | matched |
| 34 | 08:17 | 08:23 | Player A | 11:7 | Long Serve | Opponent Out of Bounds | Out of Bounds | 34 | 0.860577 | 0.033333 | 0.933333 | 0.900000 | matched |
| 35 | 08:29 | 08:34 | Player A | 12:7 | Block | Opponent Hit the Net | Hit the Net | 35 | 0.686667 | 0.766667 | -0.800000 | -1.566667 | matched |
| 36 | 08:39 | 08:45 | Player A | 14:7 | Push Shot | Winner Shot | Opponent Failed to Return | 36 | 0.755556 | 1.333333 | -0.133333 | -1.466667 | matched |
| 37 | 08:48 | 09:07 | Player A | 15:7 | Net Shot | Winner Shot | Opponent Failed to Return | 37 | 0.974359 | -0.233333 | 0.266667 | 0.500000 | matched |
| 38 | 09:08 | 09:12 | Player B | 15:9 | Smash | Opponent Hit the Net | Hit the Net | 38 | 0.550388 | 1.633333 | 0.300000 | -1.333333 | matched |
| 39 | 09:17 | 09:34 | Player B | 15:10 | Net Shot | Opponent Hit the Net | Hit the Net | 39 | 0.972921 | 0.233333 | 0.233333 | 0.000000 | matched |
| 40 | 09:36 | 09:50 | Player B | 16:12 | Smash | Winner Shot | Opponent Failed to Return | 40 | 0.954545 | -0.033333 | 0.633333 | 0.666667 | matched |
| 41 | 09:54 | 10:09 | Player B | 16:13 | Net Shot | Opponent Hit the Net | Hit the Net | 41 | 0.805616 | 2.566667 | 0.433333 | -2.133333 | matched |
| 42 | 10:12 | 10:40 | Player A | 17:13 | Net Shot | Opponent Hit the Net | Hit the Net | 42 | 0.727381 | 0.533333 | -7.100000 | -7.633333 | matched |
| 43 | 10:46 | 10:51 | Player A | 18:13 | Net Shot | Opponent Hit the Net | Hit the Net | 44 | 0.800000 | 0.200000 | 1.000000 | 0.800000 | matched |
| 44 | 10:52 | 10:57 | Player A | 19:15 | Push Shot | Winner Shot | Opponent Failed to Return | 45 | 0.846667 | 0.500000 | -0.266667 | -0.766667 | matched |
| 45 | 11:02 | 11:05 | Player A | 20:15 | Slice Shot | Opponent Hit the Net | Hit the Net | 46 | 0.833333 | -0.100000 | 0.500000 | 0.600000 | matched |

| Secondary-reference unmatched P | Start f | End f | Start s | End s |
|---|---|---|---|---|
| 5 | 2380 | 2449 | 79.333333 | 81.633333 |
| 28 | 12988 | 13085 | 432.933333 | 436.166667 |
| 31 | 13959 | 14072 | 465.300000 | 469.066667 |
| 43 | 19030 | 19178 | 634.333333 | 639.266667 |

| Supplied semantic label inventory | Counts |
|---|---|
| win_point_player | {"Player B":20,"Player A":25} |
| ball_types | {"Smash":6,"Clear":4,"Lift Shot":5,"Net Kill":5,"Push Shot":4,"Net Shot":12,"Defensive Lift":1,"Block":3,"Drive Defense":1,"Defensive Slice":1,"Slice":1,"Long Serve":1,"Slice Shot":1} |
| roundscore_A | {"0":1,"1":4,"2":5,"3":1,"5":1,"6":2,"7":3,"8":3,"9":2,"10":1,"13":2,"14":3,"15":4,"16":3,"18":2,"19":3,"4":1,"11":1,"12":1,"17":1,"20":1} |
| roundscore_B | {"1":1,"2":3,"3":1,"4":3,"5":6,"6":2,"8":1,"9":2,"10":2,"11":2,"13":5,"15":3,"16":2,"17":2,"18":1,"19":2,"20":1,"0":1,"7":4,"12":1} |

The supplied winner/score/shot fields are reproduced above exactly as source strings, including missing values and taxonomy variation. The temporal crosswalk does not establish named player/team equivalence, certified point identity, or exhaustive shot labels. Current rally winners are unknown and hitter identities are anonymous; outcome/score-sequence accuracy and per-shot confusion therefore remain unscorable, rather than being reported as verified model correctness.

### Component-level observed output versus available ground truth

| Coverage diagnostic | Numerator | Denominator | Coverage | Ground-truth accuracy available? |
|---|---|---|---|---|
| Raw shuttle present / source frames | 12921 | 20034 | 64.495% | No reviewed frame/person/contact labels |
| Detector-executed / source frames | 7642 | 20034 | 38.145% | No reviewed frame/person/contact labels |
| Fresh detector-matched person rows / person rows | 15142 | 36906 | 41.029% | No reviewed frame/person/contact labels |
| Current pose rows / person rows | 28576 | 36906 | 77.429% | No reviewed frame/person/contact labels |
| Current racket rows / person rows | 12411 | 36906 | 33.629% | No reviewed frame/person/contact labels |

| All component coverage counts | Value |
|---|---|
| frames | 20034 |
| raw_shuttle_present | 12921 |
| detector_executed_frames | 7642 |
| person_rows | 36906 |
| scene_telemetry_present | 3602 |
| scene_raw_hypotheses | 2 |
| actual_content_epoch_increments | 2 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 15142 |
| person_propagated_or_unmatched | 21764 |
| pose_present_rows | 28576 |
| pose_current_source_rows | 28576 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 13434 |
| racket_present_rows | 12411 |
| racket_current_source_rows | 12411 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 2 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 2 |

#### Frame/component categories

| Field | Observed value |
|---|---|
| view | {"main":18621,"none":1213,"alt":200} |
| calibration_state | {"REACQUIRING":86,"VALID":18535,"LOST":1413} |
| player_population | {"0":1491,"2":18363,"1":180} |
| association_status | {"missing":5700,"observed":12915,"invalid":1413,"ambiguous":6} |
| association_reason | {"no_accepted_raw_observation":5700,"fresh_selection_retained":12915,"image_view_invalid":1413,"coobserved_competing_static_hypothesis":6} |
| scene_raw_status | {"unknown":328,"measured":3272,"hypothesis":2} |
| person_detector_match | {"True":15142,"False":21764} |
| person_identity_method | {"bytetrack_v1":36906} |
| scene_decision | {"barrier":2} |
| scene_decision_reason | {"raw_change_and_current_layout_discontinuity":2} |

#### Live event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 150 |
| scene | 62 |
| participant_observation | 162 |
| format_decision | 1 |
| rally_start | 46 |
| stroke | 525 |
| contact | 525 |
| rally_end | 46 |
| identity_ambiguity | 77 |
| shuttle_turn | 37 |
| broadcast_score | 504 |
| match_phase | 1 |
| highlight | 1 |

#### Append-only event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 150 |
| scene | 62 |
| participant_observation | 162 |
| format_decision | 1 |
| rally_start | 112 |
| contact | 1133 |
| stroke | 539 |
| rally_end | 46 |
| identity_ambiguity | 77 |
| shuttle_turn | 37 |
| broadcast_score | 504 |
| match_phase | 1 |
| highlight | 1 |

#### All observed event categories

| Field | Observed value |
|---|---|
| event_status | {"confirmed":1816,"provisional":322} |
| stroke_actor | {"unknown":525} |
| stroke_physical_event_status | {"ambiguous":177,"probable":85,"insufficient":263} |
| stroke_contact_status | {"estimated":525} |
| stroke_classification_status | {"unknown":372,"estimated":153} |
| stroke_stroke | {"unknown":372,"push":68,"lift":25,"drive":4,"drop":23,"net_shot":24,"clear":7,"smash":2} |
| stroke_attribution_reason | {"nearest_proximity":523,"ambiguous_proximity":2} |
| stroke_classification_abstention_reason | {"missing_required_evidence":370,"unresolved_initial_contact":2} |
| contact_actor | {"unknown":525} |
| contact_physical_event_status | {"ambiguous":177,"probable":85,"insufficient":263} |
| contact_contact_status | {"estimated":525} |
| contact_attribution_reason | {"nearest_proximity":523,"ambiguous_proximity":2} |
| contact_trajectory_reliability | {"ambiguous":114,"insufficient":129,"probable":282} |
| contact_trajectory_reasons | {"association_unresolved":114,"coherent_motion_change_unavailable":129,"supported_launch":84,"supported_turn":198} |
| contact_impact_reliability | {"ambiguous":177,"probable":85,"insufficient":263} |
| contact_impact_reasons | {"association_unresolved":114,"coherent_motion_change_unavailable":42,"coherent_motion_and_fresh_contact_cue":85,"fresh_player_observation_unavailable":263,"no_fresh_swing_or_racket_overlap":21} |
| contact_attribution_reliability | {"insufficient":347,"probable":178} |
| contact_attribution_reasons | {"fresh_player_observation_unavailable":347,"geometric_attribution_not_verified_identity":178} |
| rally_end_reason | {"gap":10,"stationary":26,"cut":10} |
| rally_phase | {"unknown":4,"match_play":42} |
| rally_official | {"False":16,"True":30} |
| rally_match_format_known | {"True":46} |
| rally_match_format | {"singles":46} |
| rally_winner | {"None":46} |
| rally_score_transition_status | {"unavailable":27,"candidate":19} |
| rally_admission_reason | {"duration_policy":46} |

#### Track/export counts

| Field | Observed value |
|---|---|
| camera_rows | 20034 |
| player_rows | 36856 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 36454 |
| projected_court_on_propagated_box | 21558 |
| racket_rows | 12370 |
| shuttle_rows | 20034 |

#### Track/export categories

| Field | Observed value |
|---|---|
| player_id | {"None":36856} |
| detector_matched | {"True":15092,"False":21764} |

| Semantic metric | Observed | Baseline comparison / limitation |
|---|---|---|
| Known rally winner output | 0/46 | Supplied coarse winner labels exist; identity/point mapping uncertified |
| Unknown stroke classification | 372/525 | Coarse one-label-per-rally ball_types is not exhaustive per-shot GT |
| Estimated stroke classification | 153/525 | Estimated coverage is not class accuracy |
| OCR saved readouts | 546 | Observed scoreboard rows, not accepted correct points |
| OCR label counts | {"MARIN":546,"AN S.Y.":545,"ANS.Y.":1} | Raw OCR labels may differ from anonymous Player A/B |
| Tracked invalid geometry frames | 1499 | Geometric diagnostics, not labelled location error |
| Session degradation | [{"stage":"player_identity","reason":"osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"},{"stage":"player_reid","reason":"baseline player_reid provider is unavailable"}] | Identity/ReID unavailability remains recorded; no new models fetched |

### Runtime, resources and every saved stage latency

| Saved resource/runtime metric | Value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 2318633 |
| parent_failure_inclusive_elapsed_s | — |
| parent_failure_inclusive_source_fps | — |
| neural_only_throughput_fps | — |
| model_loading_time_s | — |
| media_ready_time_s | 2.099887 |
| model_staging_time_s | 1.662672 |
| worker_final_cpu_s | 23291.818427 |
| worker_maxrss_bytes | 3013013504 |
| sampled_worker_tree_peak_rss_bytes | 2992701440 |
| sampled_worker_gpu_peak_mib | 2126 |
| sampled_cpu_seconds_max_observed | 23291.270000 |
| sampled_cpu_seconds_last_observed | 23291.270000 |
| sampled_system_available_ram_min_bytes | 101068419072 |
| sample_count | 971 |
| resource_rows | 971 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 2012.031731 |
| parent_completed_source_fps | 9.957099 |
| worker_elapsed_s | 2004.809194 |
| worker_source_fps | 9.992971 |
| component_initialization_including_models_s | 9.244474 |

| Stage | Calls | Total wall s | P50 ms/call | P95 ms/call | Minimum ms | Maximum ms | Frame-population sum |
|---|---|---|---|---|---|---|---|
| court | 334 | 96.678369 | 226.303546 | 585.943510 | 156.635148 | 1647.165207 | 20034 |
| content_continuity_and_players | 334 | 844.274076 | 3037.526499 | 3289.408636 | 47.041504 | 3905.130785 | 20034 |
| shuttle | 332 | 285.851565 | 844.108147 | 1022.689614 | 680.073915 | 1202.473292 | 19914 |
| players | 334 | 90.605268 | 268.701245 | 561.788750 | 0.627318 | 859.004682 | 20034 |
| ocr | 334 | 268.215308 | 813.583976 | 951.577693 | 0.015458 | 1766.863380 | 20034 |

| Runner timing scope | Seconds |
|---|---|
| component_initialization_including_models_s | 9.244474 |
| decode_perception_cache_s | 1741.377839 |

| Additional completed-worker timing | Seconds |
|---|---|
| Perception completion catalogue publication | 4.278957 |
| Worker media ready | 2.099887 |
| Model staging | 1.662672 |

| Actual worker reproducibility metadata | Value |
|---|---|
| Visible Torch devices | [{"logical_index":0,"name":"NVIDIA GeForce GTX 1080 Ti","uuid":"a618f090-66bf-ad80-b0a5-0c91bee61fab"}] |
| CUDA_VISIBLE_DEVICES GPU UUID | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| Prior cached perceptions used | false |
| Worker model manifest SHA256 | b5590b8ff1437945da036b42b01729f521728259a0dfc4c3299a926216ba8df3 |
| Worker staged model pins SHA256 | 7bd228ead493bba31c1417c46346d35e3cd00e1760ba7d7b35485d3babf5219f |

The historical timing key decode_perception_cache_s wraps the runner’s full _perceive call. Its name does not mean this was an observation-cache replay: the completed-worker receipts explicitly record cached_perception_used=false. It is a broad perception wall-time scope, not isolated cache decoding or pure GPU latency.

| Saved disk-use metric | Bytes / count |
|---|---|
| regular_files | 2026 |
| logical_bytes | 790605627 |
| allocated_bytes | 794619904 |
| staged_model_bytes | 361041769 |
| perception_cache_bytes | 82090525 |

Wall-time scopes overlap; they are not summable GPU kernel latency. Pure neural-only FPS and isolated model-loading time remain unavailable. For historical Tests 1/2, final worker-local timing/CPU/RSS fields were lost at catalogue publication and stay unavailable; failure-inclusive parent duration is identified explicitly. For normal runs, worker elapsed includes the runner and final catalogue verification. Current-process GPU samples cannot certify per-node ORT placement or true instantaneous memory peaks.

### Reproducibility, logs and annotation-file review

| Binding | Value |
|---|---|
| Normalized numerical profile SHA256 (passive ranges removed) | 2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb |
| Effective profile canonical SHA256 | 7dc27e7fd6703ee4692de02a506c2664c46257e04d5713fe9a0a178577620a4d |
| Model identity sets | 1 |
| Runtime identity sets | 1 |
| Actual model identity SHA256 | e3c96b7c2e522fd6efe6106328bebec30137f29b7303fe5e475f8aedea5d2222 |
| Actual runtime identity SHA256 | 81e41f18d858ed37c34ce9d07ae34a34268f27e57c0e5f878e07253be309066f |
| Executed plan | [plan.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test4/protocol/plan.json) |
| Actual completion receipt | [inference.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test4/run/inference.json) |
| Per-rally saved CSV | [per_rally_comparison.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test4/evaluation/per_rally_comparison.csv) |
| Technical analysis | [technical_analysis.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test4/analysis/technical_analysis.json) |
| Full original predictions | [predicted_rallies.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test4/run/predicted_rallies.csv) |

| Annotation file | Role | Data rows | Blank rows | Bytes | Column/schema inventory | SHA256 |
|---|---|---|---|---|---|---|
| Test4_Full.csv | Secondary coarse outcome/time reference | 45 | 0 | 3277 | ["start_time","end_time","win_point_player","win_reason","ball_types","lose_reason","roundscore_A","roundscore_B"] | b22eb3d20e8ff02e9f689ba46d33ae18ae60c3780399d021eaea753725df13c4 |
| Test4_Full_Rev_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 20034 | 0 | 426289 | ["Frame","X","Y","Visibility","Confidence"] | b2c506da9168a52b8ae00ec8ccd0cbfe50cebc473458c743a3f341b0ef3de841 |
| Test4_Full_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 20034 | 0 | 426289 | ["Frame","X","Y","Visibility","Confidence"] | b2c506da9168a52b8ae00ec8ccd0cbfe50cebc473458c743a3f341b0ef3de841 |
| Test4_Full_court.json | Auxiliary historical/generated artifact; not certified independent truth | — | — | 537 | ["frame_no","frame_size","corners","net","source"] | ae014091976dd4cf66e7a887f334284e17fcfa4b32291e595931eb54811ca999 |
| Test4_Full_rally.csv | Primary timing reference | 41 | 0 | 2887 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 313d62a10401d502cc206f8a398b07297d9886a4d193df3629be128002dde39c |
| player_detections.csv | Auxiliary historical/generated artifact; not certified independent truth | 20034 | 0 | 2149727 | ["frame_no","player_1_x","player_1_y","player_1_conf","player_2_x","player_2_y","player_2_conf"] | b6ee19ef6408a27d549a3d68a35c8d0070c34647110f131fdde3733baf2dbce3 |
| win_predictions.csv | Auxiliary historical/generated artifact; not certified independent truth | 41 | 0 | 4992 | ["rally_idx","start_frame","end_frame","start_time","end_time","winner","loser","win_reason","reason_src","fault_side","fault_src","cnn_class","cnn_conf","cnn_oob","cnn_hn","cnn_wbl","score_Player A","score_Player B"] | fef78658992ce9494a240513c0f38d83cc0d7a51b26ddfeb3ffde38d5ab5cffb |

| Log | Lines | Warning/error-pattern lines | Distinct observed warning/error messages |
|---|---|---|---|
| analysis.log | 1 | 0 | [] |
| download.log | 122 | 0 | [] |
| evaluation.log | 0 | 0 | [] |
| prepare.log | 0 | 0 | [] |
| run.execution.log | 38 | 22 | ["2026-11-06 00:46:58 [warning  ] perception.degraded            reason='osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`' stage=player_identity","2026-11-06 00:46:58 [warning  ] perception.degraded            reason='baseline player_reid provider is unavailable' stage=player_reid","[WARNING] 2026-11-06 00:47:57,522 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:48:19,836 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:48:28,873 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:48:41,537 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:48:53,360 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 00:49:31,386 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:06:12,007 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:06:17,229 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:06:17,524 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:06:22,931 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:06:27,499 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:06:35,949 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:06:50,147 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:07:02,294 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:07:17,520 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:07:30,945 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:07:41,240 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:07:55,338 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:08:05,635 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:08:18,258 [RapidOCR] main.py:164: The text detection result is empty"] |
| run.launch.log | 0 | 0 | [] |
| timestamps.log | 1 | 0 | [] |

Log keyword counts are diagnostic string matches, not failed-inference counts. Tests 1/2 raw original worker logs remain in their source run directories and retain the known final catalogue failure; their independent completion proof is the accepted completion record. All previously completed evaluations remain immutable.

### Duration breakdown for this video

| GT duration bin | GT count | Matched | Missed | Recall | Start MAE f | End MAE f |
|---|---|---|---|---|---|---|
| ≤2 s | 0 | 0 | 0 | — | — | — |
| (2,5] s | 9 | 8 | 1 | 0.888889 | 17.125000 | 11.125000 |
| (5,10] s | 13 | 11 | 2 | 0.846154 | 30.090909 | 16.909091 |
| (10,20] s | 14 | 14 | 0 | 1.000000 | 30.928571 | 33.785714 |
| >20 s | 5 | 5 | 0 | 1.000000 | 57.600000 | 54.400000 |

## Test 6: complete evaluation and ground-truth comparison

Reference **42 rallies**, predictions **47**; TP/FP/FN **35/12/7**. Precision **74.468%**, recall **83.333%**, F1 **78.652%**. Matched mean IoU **0.884584**. The ground-truth benchmark for every table in this primary section is [Test6_Full_rally.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test6_Full/Test6_Full_rally.csv).

| Input / execution binding | Value |
|---|---|
| Decoded frames | 17915 |
| FPS | 30.000000 |
| Video duration seconds | 597.166667 |
| Canonical dimensions | 1280 × 720 |
| Source SHA256 | 45f873540649ec9d2b20e2d14edbf35ba2b2e41b150bfe07f3c995a0310fdab8 |
| Proxy SHA256 | 81121025d1a6907cbf57d7b26d240d3c7634adbe6a19ab642b10e1c178c46a01 |
| Prediction SHA256 | 877a7dd7a7e91c4677e9a64ff6641a29398b59518021c3825afa3836b98bfe00 |
| Ground-truth SHA256 | 237e7710a7f534bd2c7143c0010cca8872e46581f336c18c5be639f4349c4236 |
| Coarse reference SHA256 | 7def9c0b7c86514a3c0e10c03afacbac871b6dfcc04dc84074c91f00d6c54e3f |
| Session | UPLOADTEST6 |
| Actual completion mode | normal_completed_worker |
| Original parent receipt status | completed |
| Full source/proxy PTS matches | 17915 |
| Scene probe pixel hashes verified | 37 |
| Verified saved files / logical bytes | 2137 / 789618749 |
| Read-only record | [saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test6) |

### Primary metric scores versus the ground-truth ideal

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 42 | 42 | 0 |
| Prediction count | 42 | 47 | 5 |
| TP / matched | 42 | 35 | -7 |
| FP | 0 | 12 | 12 |
| FN / missed | 0 | 7 | 7 |
| precision | 1 | 0.744681 | -0.255319 |
| recall | 1 | 0.833333 | -0.166667 |
| f1 | 1 | 0.786517 | -0.213483 |
| Mean matched IoU | 1 | 0.884584 | -0.115416 |
| Median matched IoU | 1 | 0.911392 | -0.088608 |
| Minimum matched IoU | 1 | 0.601533 | -0.398467 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 88.571429 |
| 0.9 | 100 | 60.000000 |
| 0.95 | 100 | 34.285714 |

A GT self-comparison has TP=N, FP=FN=0, precision/recall/F1=1, IoU=1 and every timing/duration error=0. This is the reference ideal, not a separately executed baseline model. The signed count difference alone is insufficient: false positives and misses can cancel.

### Boundary and duration errors versus zero-error ground truth

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.485714 | 10.000000 | 43.798239 | 206.000000 | 51.600000 | 21.828571 | 6.000000 |
| end_frame | 20.571429 | 10.000000 | 49.055654 | 263.000000 | 33.600000 | -12.114286 | -1.000000 |
| start_time_sec | 0.782857 | 0.333333 | 1.459941 | 6.866667 | 1.720000 | 0.727619 | 0.200000 |
| end_time_sec | 0.685714 | 0.333333 | 1.635188 | 8.766667 | 1.120000 | -0.403810 | -0.033333 |
| duration_sec | 1.350476 | 0.733333 | 2.408965 | 10.466667 | 2.266667 | -1.131429 | -0.600000 |

| Additional saved statistic | Value | Ground-truth ideal |
|---|---|---|
| Start P95 \|error\| frames | 64.100000 | 0 |
| End P95 \|error\| frames | 63.100000 | 0 |
| Duration mae frames | 40.514286 | 0 |
| Duration rmse frames | 72.268942 | 0 |
| Duration signed_bias frames | -33.942857 | 0 |

All error statistics above condition on eligible matched rallies. A positive start error is a late start; a negative start error is early. A positive end error is a late end; a negative end error is premature. Duration error is prediction minus GT. All 30 FPS frame errors convert by dividing by30; full signed/absolute per-rally values appear below. Misses have no invented zero error.

### Boundary tolerance scores

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 6 | 35 | 17.143% | 42 | 14.286% | 100% |
| start | 3 | 0.100000 | 9 | 35 | 25.714% | 42 | 21.429% | 100% |
| start | 5 | 0.166667 | 15 | 35 | 42.857% | 42 | 35.714% | 100% |
| start | 10 | 0.333333 | 18 | 35 | 51.429% | 42 | 42.857% | 100% |
| start | 15 | 0.500000 | 19 | 35 | 54.286% | 42 | 45.238% | 100% |
| start | 30 | 1.000000 | 25 | 35 | 71.429% | 42 | 59.524% | 100% |
| end | 1 | 0.033333 | 5 | 35 | 14.286% | 42 | 11.905% | 100% |
| end | 3 | 0.100000 | 11 | 35 | 31.429% | 42 | 26.190% | 100% |
| end | 5 | 0.166667 | 16 | 35 | 45.714% | 42 | 38.095% | 100% |
| end | 10 | 0.333333 | 18 | 35 | 51.429% | 42 | 42.857% | 100% |
| end | 15 | 0.500000 | 25 | 35 | 71.429% | 42 | 59.524% | 100% |
| end | 30 | 1.000000 | 30 | 35 | 85.714% | 42 | 71.429% | 100% |

### All saved error distributions

| Distribution / units | N | Mean | Median | Minimum | Maximum | P90 | P95 | Ideal |
|---|---|---|---|---|---|---|---|---|
| matched_iou | 35 | 0.884584 | 0.911392 | 0.601533 | 0.995781 | 0.979361 | 0.985959 | 1 |
| start_signed_frames | 35 | 21.828571 | 6.000000 | -11.000000 | 206.000000 | 51.600000 | 64.100000 | 0 |
| start_absolute_frames | 35 | 23.485714 | 10.000000 | 0.000000 | 206.000000 | 51.600000 | 64.100000 | 0 |
| end_signed_frames | 35 | -12.114286 | -1.000000 | -263.000000 | 33.000000 | 14.000000 | 17.300000 | 0 |
| end_absolute_frames | 35 | 20.571429 | 10.000000 | 1.000000 | 263.000000 | 33.600000 | 63.100000 | 0 |
| duration_signed_frames | 35 | -33.942857 | -18.000000 | -314.000000 | 27.000000 | 14.600000 | 21.300000 | 0 |
| duration_absolute_frames | 35 | 40.514286 | 22.000000 | 0.000000 | 314.000000 | 68.000000 | 131.000000 | 0 |
| duration_signed_seconds | 35 | -1.131429 | -0.600000 | -10.466667 | 0.900000 | 0.486667 | 0.710000 | 0 |

### Misses, extras, overlap topology and failure review

| Diagnostic | Observed | GT ideal / interpretation |
|---|---|---|
| Missed GT IDs | [9,19,22,26,30,40,41] | [] |
| Unmatched prediction IDs | [2,10,11,12,15,16,24,25,31,32,36,46] | [] |
| No-overlap missed GT IDs | [22] | [] |
| Predictions without any GT overlap | [] | [] |
| Possible split GT IDs | [2,8,10,11,19,26] | Geometric overlap candidates; not adjudicated semantic splits |
| Possible merge prediction IDs | [46] | Geometric overlap candidates; not adjudicated semantic merges |
| Significant failure records | 34 | Unmatched or \|boundary error\|>30frames or IoU<0.75 |
| early_start_gt_ids | [12,13,15,17,20,24,29] | Direction/weak-overlap inventory, not a physical cause |
| late_start_gt_ids | [1,2,3,4,5,6,7,8,10,11,14,16,18,23,25,27,28,31,32,33,34,35,36,37,38,39,42] | Direction/weak-overlap inventory, not a physical cause |
| premature_end_gt_ids | [3,5,7,8,10,11,14,15,18,20,21,25,28,29,31,32,33,34,36,39] | Direction/weak-overlap inventory, not a physical cause |
| late_end_gt_ids | [1,2,4,6,12,13,16,17,23,24,27,35,37,38,42] | Direction/weak-overlap inventory, not a physical cause |
| weak_iou_gt_ids | [8,10,11,18] | Direction/weak-overlap inventory, not a physical cause |

| Inventory validity | Ground truth | Predictions |
|---|---|---|
| count | 42 | 47 |
| duplicate_row_pairs | [] | [] |
| positive_overlap_row_pairs | [] | [] |
| adjacent_row_pairs | [] | [] |
| out_of_range_rows | [] | [] |
| out_of_order_rows | [] | [] |

| False detection P ID | Start frame | End frame | Start seconds | End seconds | Duration seconds | Positive-overlap GT IDs |
|---|---|---|---|---|---|---|
| 2 | 666 | 725 | 22.200000 | 24.166667 | 1.966667 | [2] |
| 10 | 3592 | 3636 | 119.733333 | 121.200000 | 1.466667 | [8] |
| 11 | 3796 | 3880 | 126.533333 | 129.333333 | 2.800000 | [9] |
| 12 | 3943 | 4140 | 131.433333 | 138.000000 | 6.566667 | [10] |
| 15 | 5111 | 5191 | 170.366667 | 173.033333 | 2.666667 | [11] |
| 16 | 5221 | 5314 | 174.033333 | 177.133333 | 3.100000 | [11] |
| 24 | 7635 | 7942 | 254.500000 | 264.733333 | 10.233333 | [19] |
| 25 | 7970 | 8232 | 265.666667 | 274.400000 | 8.733333 | [19] |
| 31 | 10341 | 10439 | 344.700000 | 347.966667 | 3.266667 | [26] |
| 32 | 10567 | 10754 | 352.233333 | 358.466667 | 6.233333 | [26] |
| 36 | 12393 | 12475 | 413.100000 | 415.833333 | 2.733333 | [30] |
| 46 | 16877 | 17205 | 562.566667 | 573.500000 | 10.933333 | [40,41] |

| Largest matched boundary cases | P ID | GT start/end frames | Pred start/end frames | Δstart frames | Δend frames | IoU |
|---|---|---|---|---|---|---|
| 11 | 14 | 4480–5317 | 4531–5054 | 51 | -263 | 0.624851 |
| 10 | 13 | 3942–4464 | 4148–4462 | 206 | -2 | 0.601533 |
| 6 | 7 | 2694–3153 | 2770–3157 | 76 | 4 | 0.827214 |
| 8 | 9 | 3349–3642 | 3372–3567 | 23 | -75 | 0.665529 |
| 32 | 38 | 13023–13421 | 13082–13420 | 59 | -1 | 0.849246 |

Of 7 unmatched reference intervals, 1 have no positive overlap with any prediction; 6 have some overlap but fail the one-to-one IoU eligibility/assignment. This separates absence of overlap from insufficient interval agreement without inventing a causal diagnosis.

### Every GT rally compared directly with its assigned prediction: frames

G IDs are one-based CSV row IDs in the primary rally reference. P IDs are one-based rows in the preserved prediction CSV. C IDs refer to the separate coarse table, linked only by the same IoU-based temporal crosswalk. “—” denotes unavailable/unmatched, not zero.

| G | P | GT start f | GT end f | Pred start f | Pred end f | Δstart f | \|Δstart\| f | Δend f | \|Δend\| f | IoU | Status | Coarse C row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 88 | 634 | 132 | 635 | 44 | 44 | 1 | 1 | 0.917733 | matched | 1 |
| 2 | 3 | 692 | 994 | 729 | 1007 | 37 | 37 | 13 | 13 | 0.841270 | matched | 2 |
| 3 | 4 | 1024 | 1654 | 1040 | 1641 | 16 | 16 | -13 | 13 | 0.953968 | matched | 3 |
| 4 | 5 | 1677 | 1894 | 1681 | 1899 | 4 | 4 | 5 | 5 | 0.959459 | matched | 4 |
| 5 | 6 | 1971 | 2565 | 1975 | 2507 | 4 | 4 | -58 | 58 | 0.895623 | matched | 5 |
| 6 | 7 | 2694 | 3153 | 2770 | 3157 | 76 | 76 | 4 | 4 | 0.827214 | matched | 6 |
| 7 | 8 | 3173 | 3330 | 3208 | 3326 | 35 | 35 | -4 | 4 | 0.751592 | matched | 7 |
| 8 | 9 | 3349 | 3642 | 3372 | 3567 | 23 | 23 | -75 | 75 | 0.665529 | matched | 8 |
| 9 | — | 3698 | 3918 | — | — | — | — | — | — | — | missed | 10 |
| 10 | 13 | 3942 | 4464 | 4148 | 4462 | 206 | 206 | -2 | 2 | 0.601533 | matched | 11 |
| 11 | 14 | 4480 | 5317 | 4531 | 5054 | 51 | 51 | -263 | 263 | 0.624851 | matched | 12 |
| 12 | 17 | 5371 | 5682 | 5367 | 5700 | -4 | 4 | 18 | 18 | 0.933934 | matched | 14 |
| 13 | 18 | 5725 | 6509 | 5714 | 6510 | -11 | 11 | 1 | 1 | 0.984925 | matched | 15 |
| 14 | 19 | 6546 | 6783 | 6565 | 6781 | 19 | 19 | -2 | 2 | 0.911392 | matched | 16 |
| 15 | 20 | 6826 | 7034 | 6825 | 7024 | -1 | 1 | -10 | 10 | 0.947368 | matched | 17 |
| 16 | 21 | 7088 | 7284 | 7091 | 7301 | 3 | 3 | 17 | 17 | 0.906103 | matched | 18 |
| 17 | 22 | 7318 | 7405 | 7317 | 7419 | -1 | 1 | 14 | 14 | 0.852941 | matched | 19 |
| 18 | 23 | 7462 | 7596 | 7479 | 7574 | 17 | 17 | -22 | 22 | 0.708955 | matched | 20 |
| 19 | — | 7623 | 8248 | — | — | — | — | — | — | — | missed | 21 |
| 20 | 26 | 8273 | 8416 | 8271 | 8412 | -2 | 2 | -4 | 4 | 0.958621 | matched | 22 |
| 21 | 27 | 8464 | 8701 | 8464 | 8700 | 0 | 0 | -1 | 1 | 0.995781 | matched | 23 |
| 22 | — | 8753 | 8826 | — | — | — | — | — | — | — | missed | — |
| 23 | 28 | 9066 | 9776 | 9086 | 9778 | 20 | 20 | 2 | 2 | 0.969101 | matched | 24 |
| 24 | 29 | 9847 | 10125 | 9838 | 10137 | -9 | 9 | 12 | 12 | 0.929766 | matched | 25 |
| 25 | 30 | 10163 | 10258 | 10164 | 10245 | 1 | 1 | -13 | 13 | 0.852632 | matched | 26 |
| 26 | — | 10331 | 10758 | — | — | — | — | — | — | — | missed | 27 |
| 27 | 33 | 10783 | 11017 | 10787 | 11021 | 4 | 4 | 4 | 4 | 0.966387 | matched | 28 |
| 28 | 34 | 11065 | 11392 | 11084 | 11366 | 19 | 19 | -26 | 26 | 0.862385 | matched | 29 |
| 29 | 35 | 11434 | 12261 | 11433 | 12238 | -1 | 1 | -23 | 23 | 0.971014 | matched | 30 |
| 30 | — | 12286 | 12476 | — | — | — | — | — | — | — | missed | — |
| 31 | 37 | 12539 | 13008 | 12583 | 13007 | 44 | 44 | -1 | 1 | 0.904051 | matched | 32 |
| 32 | 38 | 13023 | 13421 | 13082 | 13420 | 59 | 59 | -1 | 1 | 0.849246 | matched | 33 |
| 33 | 39 | 13467 | 13805 | 13477 | 13802 | 10 | 10 | -3 | 3 | 0.961538 | matched | 34 |
| 34 | 40 | 13931 | 14280 | 13932 | 14266 | 1 | 1 | -14 | 14 | 0.957020 | matched | 35 |
| 35 | 41 | 14362 | 15114 | 14366 | 15121 | 4 | 4 | 7 | 7 | 0.985507 | matched | 36 |
| 36 | 42 | 15149 | 15534 | 15151 | 15531 | 2 | 2 | -3 | 3 | 0.987013 | matched | 37 |
| 37 | 43 | 15602 | 15841 | 15634 | 15855 | 32 | 32 | 14 | 14 | 0.818182 | matched | 38 |
| 38 | 44 | 15906 | 16174 | 15912 | 16207 | 6 | 6 | 33 | 33 | 0.870432 | matched | 39 |
| 39 | 45 | 16241 | 16820 | 16245 | 16786 | 4 | 4 | -34 | 34 | 0.934370 | matched | 40 |
| 40 | — | 16876 | 17020 | — | — | — | — | — | — | — | missed | — |
| 41 | — | 17065 | 17281 | — | — | — | — | — | — | — | missed | — |
| 42 | 47 | 17311 | 17875 | 17363 | 17878 | 52 | 52 | 3 | 3 | 0.902998 | matched | — |

### Every GT rally compared directly: timestamps and durations

| G | GT start s | GT end s | Pred start s | Pred end s | GT duration s | Pred duration s | Δstart s | \|Δstart\| s | Δend s | \|Δend\| s | Δduration s | \|Δduration\| s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2.933333 | 21.133333 | 4.400000 | 21.166667 | 18.200000 | 16.766667 | 1.466667 | 1.466667 | 0.033333 | 0.033333 | -1.433333 | 1.433333 |
| 2 | 23.066667 | 33.133333 | 24.300000 | 33.566667 | 10.066667 | 9.266667 | 1.233333 | 1.233333 | 0.433333 | 0.433333 | -0.800000 | 0.800000 |
| 3 | 34.133333 | 55.133333 | 34.666667 | 54.700000 | 21.000000 | 20.033333 | 0.533333 | 0.533333 | -0.433333 | 0.433333 | -0.966667 | 0.966667 |
| 4 | 55.900000 | 63.133333 | 56.033333 | 63.300000 | 7.233333 | 7.266667 | 0.133333 | 0.133333 | 0.166667 | 0.166667 | 0.033333 | 0.033333 |
| 5 | 65.700000 | 85.500000 | 65.833333 | 83.566667 | 19.800000 | 17.733333 | 0.133333 | 0.133333 | -1.933333 | 1.933333 | -2.066667 | 2.066667 |
| 6 | 89.800000 | 105.100000 | 92.333333 | 105.233333 | 15.300000 | 12.900000 | 2.533333 | 2.533333 | 0.133333 | 0.133333 | -2.400000 | 2.400000 |
| 7 | 105.766667 | 111.000000 | 106.933333 | 110.866667 | 5.233333 | 3.933333 | 1.166667 | 1.166667 | -0.133333 | 0.133333 | -1.300000 | 1.300000 |
| 8 | 111.633333 | 121.400000 | 112.400000 | 118.900000 | 9.766667 | 6.500000 | 0.766667 | 0.766667 | -2.500000 | 2.500000 | -3.266667 | 3.266667 |
| 9 | 123.266667 | 130.600000 | — | — | 7.333333 | — | — | — | — | — | — | — |
| 10 | 131.400000 | 148.800000 | 138.266667 | 148.733333 | 17.400000 | 10.466667 | 6.866667 | 6.866667 | -0.066667 | 0.066667 | -6.933333 | 6.933333 |
| 11 | 149.333333 | 177.233333 | 151.033333 | 168.466667 | 27.900000 | 17.433333 | 1.700000 | 1.700000 | -8.766667 | 8.766667 | -10.466667 | 10.466667 |
| 12 | 179.033333 | 189.400000 | 178.900000 | 190.000000 | 10.366667 | 11.100000 | -0.133333 | 0.133333 | 0.600000 | 0.600000 | 0.733333 | 0.733333 |
| 13 | 190.833333 | 216.966667 | 190.466667 | 217.000000 | 26.133333 | 26.533333 | -0.366667 | 0.366667 | 0.033333 | 0.033333 | 0.400000 | 0.400000 |
| 14 | 218.200000 | 226.100000 | 218.833333 | 226.033333 | 7.900000 | 7.200000 | 0.633333 | 0.633333 | -0.066667 | 0.066667 | -0.700000 | 0.700000 |
| 15 | 227.533333 | 234.466667 | 227.500000 | 234.133333 | 6.933333 | 6.633333 | -0.033333 | 0.033333 | -0.333333 | 0.333333 | -0.300000 | 0.300000 |
| 16 | 236.266667 | 242.800000 | 236.366667 | 243.366667 | 6.533333 | 7.000000 | 0.100000 | 0.100000 | 0.566667 | 0.566667 | 0.466667 | 0.466667 |
| 17 | 243.933333 | 246.833333 | 243.900000 | 247.300000 | 2.900000 | 3.400000 | -0.033333 | 0.033333 | 0.466667 | 0.466667 | 0.500000 | 0.500000 |
| 18 | 248.733333 | 253.200000 | 249.300000 | 252.466667 | 4.466667 | 3.166667 | 0.566667 | 0.566667 | -0.733333 | 0.733333 | -1.300000 | 1.300000 |
| 19 | 254.100000 | 274.933333 | — | — | 20.833333 | — | — | — | — | — | — | — |
| 20 | 275.766667 | 280.533333 | 275.700000 | 280.400000 | 4.766667 | 4.700000 | -0.066667 | 0.066667 | -0.133333 | 0.133333 | -0.066667 | 0.066667 |
| 21 | 282.133333 | 290.033333 | 282.133333 | 290.000000 | 7.900000 | 7.866667 | 0.000000 | 0.000000 | -0.033333 | 0.033333 | -0.033333 | 0.033333 |
| 22 | 291.766667 | 294.200000 | — | — | 2.433333 | — | — | — | — | — | — | — |
| 23 | 302.200000 | 325.866667 | 302.866667 | 325.933333 | 23.666667 | 23.066667 | 0.666667 | 0.666667 | 0.066667 | 0.066667 | -0.600000 | 0.600000 |
| 24 | 328.233333 | 337.500000 | 327.933333 | 337.900000 | 9.266667 | 9.966667 | -0.300000 | 0.300000 | 0.400000 | 0.400000 | 0.700000 | 0.700000 |
| 25 | 338.766667 | 341.933333 | 338.800000 | 341.500000 | 3.166667 | 2.700000 | 0.033333 | 0.033333 | -0.433333 | 0.433333 | -0.466667 | 0.466667 |
| 26 | 344.366667 | 358.600000 | — | — | 14.233333 | — | — | — | — | — | — | — |
| 27 | 359.433333 | 367.233333 | 359.566667 | 367.366667 | 7.800000 | 7.800000 | 0.133333 | 0.133333 | 0.133333 | 0.133333 | 0.000000 | 0.000000 |
| 28 | 368.833333 | 379.733333 | 369.466667 | 378.866667 | 10.900000 | 9.400000 | 0.633333 | 0.633333 | -0.866667 | 0.866667 | -1.500000 | 1.500000 |
| 29 | 381.133333 | 408.700000 | 381.100000 | 407.933333 | 27.566667 | 26.833333 | -0.033333 | 0.033333 | -0.766667 | 0.766667 | -0.733333 | 0.733333 |
| 30 | 409.533333 | 415.866667 | — | — | 6.333333 | — | — | — | — | — | — | — |
| 31 | 417.966667 | 433.600000 | 419.433333 | 433.566667 | 15.633333 | 14.133333 | 1.466667 | 1.466667 | -0.033333 | 0.033333 | -1.500000 | 1.500000 |
| 32 | 434.100000 | 447.366667 | 436.066667 | 447.333333 | 13.266667 | 11.266667 | 1.966667 | 1.966667 | -0.033333 | 0.033333 | -2.000000 | 2.000000 |
| 33 | 448.900000 | 460.166667 | 449.233333 | 460.066667 | 11.266667 | 10.833333 | 0.333333 | 0.333333 | -0.100000 | 0.100000 | -0.433333 | 0.433333 |
| 34 | 464.366667 | 476.000000 | 464.400000 | 475.533333 | 11.633333 | 11.133333 | 0.033333 | 0.033333 | -0.466667 | 0.466667 | -0.500000 | 0.500000 |
| 35 | 478.733333 | 503.800000 | 478.866667 | 504.033333 | 25.066667 | 25.166667 | 0.133333 | 0.133333 | 0.233333 | 0.233333 | 0.100000 | 0.100000 |
| 36 | 504.966667 | 517.800000 | 505.033333 | 517.700000 | 12.833333 | 12.666667 | 0.066667 | 0.066667 | -0.100000 | 0.100000 | -0.166667 | 0.166667 |
| 37 | 520.066667 | 528.033333 | 521.133333 | 528.500000 | 7.966667 | 7.366667 | 1.066667 | 1.066667 | 0.466667 | 0.466667 | -0.600000 | 0.600000 |
| 38 | 530.200000 | 539.133333 | 530.400000 | 540.233333 | 8.933333 | 9.833333 | 0.200000 | 0.200000 | 1.100000 | 1.100000 | 0.900000 | 0.900000 |
| 39 | 541.366667 | 560.666667 | 541.500000 | 559.533333 | 19.300000 | 18.033333 | 0.133333 | 0.133333 | -1.133333 | 1.133333 | -1.266667 | 1.266667 |
| 40 | 562.533333 | 567.333333 | — | — | 4.800000 | — | — | — | — | — | — | — |
| 41 | 568.833333 | 576.033333 | — | — | 7.200000 | — | — | — | — | — | — | — |
| 42 | 577.033333 | 595.833333 | 578.766667 | 595.933333 | 18.800000 | 17.166667 | 1.733333 | 1.733333 | 0.100000 | 0.100000 | -1.633333 | 1.633333 |

### Secondary coarse/outcome annotations: full supplied baseline and comparison

[Test6_Full.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test6_Full/Test6_Full.csv) contains **42 data rows**, **42 nonblank intervals**, blank row IDs **[]**. This separate reference differs from the 42-interval primary timing table. The same unchanged predictions and matcher give secondary precision **82.979%**, recall **92.857%**, F1 **87.640%**; this reference-sensitivity analysis does not replace the primary benchmark. No labels, times or predictions were fitted or repaired.

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 42 | 42 | 0 |
| Prediction count | 42 | 47 | 5 |
| TP / matched | 42 | 39 | -3 |
| FP | 0 | 8 | 8 |
| FN / missed | 0 | 3 | 3 |
| precision | 1 | 0.829787 | -0.170213 |
| recall | 1 | 0.928571 | -0.071429 |
| f1 | 1 | 0.876404 | -0.123596 |
| Mean matched IoU | 1 | 0.843380 | -0.156620 |
| Median matched IoU | 1 | 0.873479 | -0.126521 |
| Minimum matched IoU | 1 | 0.511667 | -0.488333 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 82.051282 |
| 0.9 | 100 | 41.025641 |
| 0.95 | 100 | 20.512821 |

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 21.846154 | 15.000000 | 40.831109 | 218.000000 | 39.600000 | 15.743590 | 12.000000 |
| end_frame | 25.974359 | 16.000000 | 50.753047 | 278.000000 | 37.800000 | 3.153846 | 11.000000 |
| start_time_sec | 0.728205 | 0.500000 | 1.361037 | 7.266667 | 1.320000 | 0.524786 | 0.400000 |
| end_time_sec | 0.865812 | 0.533333 | 1.691768 | 9.266667 | 1.260000 | 0.105128 | 0.366667 |
| duration_sec | 1.240171 | 0.733333 | 2.242118 | 9.766667 | 2.020000 | -0.419658 | -0.100000 |

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 2 | 39 | 5.128% | 42 | 4.762% | 100% |
| start | 3 | 0.100000 | 5 | 39 | 12.821% | 42 | 11.905% | 100% |
| start | 5 | 0.166667 | 9 | 39 | 23.077% | 42 | 21.429% | 100% |
| start | 10 | 0.333333 | 15 | 39 | 38.462% | 42 | 35.714% | 100% |
| start | 15 | 0.500000 | 22 | 39 | 56.410% | 42 | 52.381% | 100% |
| start | 30 | 1.000000 | 32 | 39 | 82.051% | 42 | 76.190% | 100% |
| end | 1 | 0.033333 | 0 | 39 | 0.000% | 42 | 0.000% | 100% |
| end | 3 | 0.100000 | 3 | 39 | 7.692% | 42 | 7.143% | 100% |
| end | 5 | 0.166667 | 6 | 39 | 15.385% | 42 | 14.286% | 100% |
| end | 10 | 0.333333 | 12 | 39 | 30.769% | 42 | 28.571% | 100% |
| end | 15 | 0.500000 | 19 | 39 | 48.718% | 42 | 45.238% | 100% |
| end | 30 | 1.000000 | 32 | 39 | 82.051% | 42 | 76.190% | 100% |

| Cross-reference timing diagnostic | Value |
|---|---|
| Primary-to-coarse eligible matched intervals | 37 |
| Primary intervals unmatched to coarse reference | [22,30,40,41,42] |
| Coarse rows unmatched to primary reference | [9,13,31,41,42] |
| Primary/coarse matched mean IoU | 0.870455 |

| C source row | Supplied start | Supplied end | Supplied winner | Supplied A:B score | Supplied shot / ball_types | Win reason | Lose reason | Matched P | IoU | Δstart s | Δend s | Δduration s | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:04 | 0:21 | Player B | 0:1 | Push Shot | Winner Shot | Hit Out of Bounds | 1 | 0.966990 | 0.400000 | 0.166667 | -0.233333 | matched |
| 2 | 0:23 | 0:33 | Player A | 1:1 | Hook Shot | Opponent Hit the Net | Hit the Net | 3 | 0.823344 | 1.300000 | 0.566667 | -0.733333 | matched |
| 3 | 0:35 | 0:54 | Player A | 2:1 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 4 | 0.948419 | -0.333333 | 0.700000 | 1.033333 | matched |
| 4 | 0:56 | 1:03 | Player A | 3:1 | Block Shot | Opponent Hit the Net | Hit the Net | 5 | 0.954338 | 0.033333 | 0.300000 | 0.266667 | matched |
| 5 | 1:05 | 1:23 | Player A | 4:1 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 6 | 0.924596 | 0.833333 | 0.566667 | -0.266667 | matched |
| 6 | 1:32 | 1:45 | Player A | 5:1 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 7 | 0.957179 | 0.333333 | 0.233333 | -0.100000 | matched |
| 7 | 1:46 | 1:50 | Player B | 5:2 | Hook Shot | Opponent Hit the Net | Hit the Net | 8 | 0.630137 | 0.933333 | 0.866667 | -0.066667 | matched |
| 8 | 1:52 | 1:59 | Player A | 6:2 | Smash | Winner Shot | Opponent Failed to Return | 9 | 0.928571 | 0.400000 | -0.100000 | -0.500000 | matched |
| 9 | 2:00 | 2:01 | Player B | 6:3 | Jump Smash | Winner Shot | Opponent Failed to Return | 10 | 0.681818 | -0.266667 | 0.200000 | 0.466667 | matched |
| 10 | 2:06 | 2:10 | Player A | 7:3 | Drop Shot | Opponent Out of Bounds | Hit Out of Bounds | 11 | 0.700000 | 0.533333 | -0.666667 | -1.200000 | matched |
| 11 | 2:11 | 2:29 | Player A | 8:3 | Drop Shot | Opponent Hit the Net | Hit the Net | 13 | 0.581481 | 7.266667 | -0.266667 | -7.533333 | matched |
| 12 | 2:31 | 2:51 | Player B | 8:4 | Push Shot | Winner Shot | Opponent Failed to Return | 14 | 0.871667 | 0.033333 | -2.533333 | -2.566667 | matched |
| 13 | 2:52 | 2:57 | Player B | 8:5 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 16 | 0.577922 | 2.033333 | 0.133333 | -1.900000 | matched |
| 14 | 2:59 | 3:08 | Player A | 9:5 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 17 | 0.810811 | -0.100000 | 2.000000 | 2.100000 | matched |
| 15 | 3:11 | 3:36 | Player A | 10:5 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 18 | 0.942211 | -0.533333 | 1.000000 | 1.533333 | matched |
| 16 | 3:39 | 3:45 | Player B | 10:6 | Smash | Winner Shot | Opponent Failed to Return | 19 | 0.833333 | -0.166667 | 1.033333 | 1.200000 | matched |
| 17 | 3:47 | 3:54 | Player A | 11:6 | Drop Shot | Opponent Hit the Net | Hit the Net | 20 | 0.911215 | 0.500000 | 0.133333 | -0.366667 | matched |
| 18 | 3:57 | 4:02 | Player A | 12:6 | Smash | Winner Shot | Opponent Failed to Return | 21 | 0.714286 | -0.633333 | 1.366667 | 2.000000 | matched |
| 19 | 4:04 | 4:07 | Player B | 12:7 | Jump Smash | Winner Shot | Opponent Failed to Return | 22 | 0.882353 | -0.100000 | 0.300000 | 0.400000 | matched |
| 20 | 4:09 | 4:13 | Player A | 13:7 | Block Shot | Opponent Out of Bounds | Hit the Net | 23 | 0.791667 | 0.300000 | -0.533333 | -0.833333 | matched |
| 21 | 4:14 | 4:34 | Player A | 14:7 | Smash | Winner Shot | Opponent Failed to Return | 24 | 0.511667 | 0.500000 | -9.266667 | -9.766667 | matched |
| 22 | 4:35 | 4:40 | Player A | 15:7 | Smash | Winner Shot | Opponent Failed to Return | 26 | 0.796296 | 0.700000 | 0.400000 | -0.300000 | matched |
| 23 | 4:43 | 4:49 | Player A | 16:7 | Smash | Winner Shot | Opponent Failed to Return | 27 | 0.762712 | -0.866667 | 1.000000 | 1.866667 | matched |
| 24 | 5:03 | 5:25 | Player A | 17:7 | Drive Shot | Winner Shot | Opponent Failed to Return | 28 | 0.953757 | -0.133333 | 0.933333 | 1.066667 | matched |
| 25 | 5:27 | 5:37 | Player A | 18:7 | Net Block Shot | Opponent Hit the Net | Hit the Net | 29 | 0.831804 | 0.933333 | 0.900000 | -0.033333 | matched |
| 26 | 5:39 | 5:42 | Player B | 18:8 | Drop Shot | Opponent Hit the Net | Hit the Net | 30 | 0.781250 | -0.200000 | -0.500000 | -0.300000 | matched |
| 27 | 5:44 | 5:58 | Player B | 18:9 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | — | — | — | — | — | missed |
| 28 | 5:59 | 6:07 | Player B | 18:10 | Smash | Opponent Out of Bounds | Hit Out of Bounds | 33 | 0.888446 | 0.566667 | 0.366667 | -0.200000 | matched |
| 29 | 6:09 | 6:18 | Player B | 18:11 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 34 | 0.864865 | 0.466667 | 0.866667 | 0.400000 | matched |
| 30 | 6:20 | 6:48 | Player A | 19:11 | Smash | Winner Shot | Opponent Failed to Return | 35 | 0.958333 | 1.100000 | -0.066667 | -1.166667 | matched |
| 31 | 6:52 | 6:55 | Player A | 20:11 | Smash | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 32 | 6:58 | 7:14 | Player B | 20:12 | Net Shot | Opponent Hit the Net | Hit the Net | 37 | 0.883333 | 1.433333 | -0.433333 | -1.866667 | matched |
| 33 | 7:16 | 7:27 | Player B | 20:13 | Net Block Shot | Opponent Out of Bounds | Hit the Net | 38 | 0.964706 | 0.066667 | 0.333333 | 0.266667 | matched |
| 34 | 7:29 | 7:40 | Player A | 21:13 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 39 | 0.972892 | 0.233333 | 0.066667 | -0.166667 | matched |
| 35 | 7:43 | 7:56 | Player B | 21:14 | Net Shot | Opponent Hit the Net | Hit the Net | 40 | 0.856410 | 1.400000 | -0.466667 | -1.866667 | matched |
| 36 | 7:59 | 8:23 | Player B | 21:15 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 41 | 0.953642 | -0.133333 | 1.033333 | 1.166667 | matched |
| 37 | 8:24 | 8:37 | Player B | 21:16 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 42 | 0.873479 | 1.033333 | 0.700000 | -0.333333 | matched |
| 38 | 8:41 | 8:48 | Player B | 21:17 | Net Block Shot | Opponent Hit the Net | Hit the Net | 43 | 0.915556 | 0.133333 | 0.500000 | 0.366667 | matched |
| 39 | 8:50 | 8:59 | Player B | 21:18 | Smash | Winner Shot | Opponent Failed to Return | 44 | 0.840391 | 0.400000 | 1.233333 | 0.833333 | matched |
| 40 | 9:02 | 9:19 | Player A | 22:18 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 45 | 0.942699 | -0.500000 | 0.533333 | 1.033333 | matched |
| 41 | 9:22 | 9:33 | Player A | 23:18 | Smash | Opponent Hit the Net | Hit the Net | 46 | 0.907246 | 0.566667 | 0.500000 | -0.066667 | matched |
| 42 | 9:34 | 9:36 | Player B | 23:19 | Net Block Shot | Opponent Hit the Net | Hit the Net | — | — | — | — | — | missed |

| Secondary-reference unmatched P | Start f | End f | Start s | End s |
|---|---|---|---|---|
| 2 | 666 | 725 | 22.200000 | 24.166667 |
| 12 | 3943 | 4140 | 131.433333 | 138.000000 |
| 15 | 5111 | 5191 | 170.366667 | 173.033333 |
| 25 | 7970 | 8232 | 265.666667 | 274.400000 |
| 31 | 10341 | 10439 | 344.700000 | 347.966667 |
| 32 | 10567 | 10754 | 352.233333 | 358.466667 |
| 36 | 12393 | 12475 | 413.100000 | 415.833333 |
| 47 | 17363 | 17878 | 578.766667 | 595.933333 |

| Supplied semantic label inventory | Counts |
|---|---|
| win_point_player | {"Player B":19,"Player A":23} |
| ball_types | {"Push Shot":2,"Hook Shot":2,"Lift Shot":8,"Block Shot":2,"Smash":11,"Jump Smash":2,"Drop Shot":4,"Clear Shot":4,"Drive Shot":1,"Net Block Shot":4,"Net Shot":2} |
| roundscore_A | {"0":1,"1":1,"2":1,"3":1,"4":1,"5":2,"6":2,"7":1,"8":3,"9":1,"10":2,"11":1,"12":2,"13":1,"14":1,"15":1,"16":1,"17":1,"18":5,"19":1,"20":3,"21":6,"22":1,"23":2} |
| roundscore_B | {"1":6,"2":2,"3":3,"4":1,"5":3,"6":3,"7":7,"8":1,"9":1,"10":1,"11":3,"12":1,"13":2,"14":1,"15":1,"16":1,"17":1,"18":3,"19":1} |

The supplied winner/score/shot fields are reproduced above exactly as source strings, including missing values and taxonomy variation. The temporal crosswalk does not establish named player/team equivalence, certified point identity, or exhaustive shot labels. Current rally winners are unknown and hitter identities are anonymous; outcome/score-sequence accuracy and per-shot confusion therefore remain unscorable, rather than being reported as verified model correctness.

### Component-level observed output versus available ground truth

| Coverage diagnostic | Numerator | Denominator | Coverage | Ground-truth accuracy available? |
|---|---|---|---|---|
| Raw shuttle present / source frames | 14711 | 17915 | 82.116% | No reviewed frame/person/contact labels |
| Detector-executed / source frames | 8357 | 17915 | 46.648% | No reviewed frame/person/contact labels |
| Fresh detector-matched person rows / person rows | 16637 | 35556 | 46.791% | No reviewed frame/person/contact labels |
| Current pose rows / person rows | 32651 | 35556 | 91.830% | No reviewed frame/person/contact labels |
| Current racket rows / person rows | 13506 | 35556 | 37.985% | No reviewed frame/person/contact labels |

| All component coverage counts | Value |
|---|---|
| frames | 17915 |
| raw_shuttle_present | 14711 |
| detector_executed_frames | 8357 |
| person_rows | 35556 |
| scene_telemetry_present | 3629 |
| scene_raw_hypotheses | 37 |
| actual_content_epoch_increments | 37 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 16637 |
| person_propagated_or_unmatched | 18919 |
| pose_present_rows | 32651 |
| pose_current_source_rows | 32651 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 16014 |
| racket_present_rows | 13506 |
| racket_current_source_rows | 13506 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 37 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 37 |

#### Frame/component categories

| Field | Observed value |
|---|---|
| view | {"main":17913,"none":2} |
| calibration_state | {"REACQUIRING":4,"VALID":17909,"LOST":2} |
| player_population | {"0":124,"2":17429,"1":194,"3":168} |
| association_status | {"missing":3202,"observed":14634,"ambiguous":77,"invalid":2} |
| association_reason | {"no_accepted_raw_observation":3202,"fresh_selection_retained":14634,"coobserved_competing_static_hypothesis":77,"image_view_invalid":2} |
| scene_raw_status | {"unknown":94,"measured":3498,"hypothesis":37} |
| person_detector_match | {"True":16637,"False":18919} |
| person_identity_method | {"bytetrack_v1":35556} |
| scene_decision | {"barrier":36,"unknown":1} |
| scene_decision_reason | {"raw_change_and_current_layout_discontinuity":36,"participant_count_unresolved_raw_barrier_fallback":1} |

#### Live event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 105 |
| scene | 1 |
| participant_observation | 178 |
| format_decision | 1 |
| rally_start | 47 |
| stroke | 586 |
| contact | 586 |
| rally_end | 47 |
| identity_ambiguity | 38 |
| broadcast_score | 477 |
| match_phase | 1 |
| highlight | 2 |
| shuttle_turn | 21 |

#### Append-only event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 105 |
| scene | 1 |
| participant_observation | 178 |
| rally_start | 101 |
| contact | 1261 |
| stroke | 616 |
| format_decision | 1 |
| rally_end | 47 |
| identity_ambiguity | 38 |
| broadcast_score | 477 |
| match_phase | 1 |
| highlight | 2 |
| shuttle_turn | 21 |

#### All observed event categories

| Field | Observed value |
|---|---|
| event_status | {"confirmed":1807,"provisional":284} |
| stroke_actor | {"unknown":586} |
| stroke_physical_event_status | {"ambiguous":192,"insufficient":306,"probable":88} |
| stroke_contact_status | {"estimated":586} |
| stroke_classification_status | {"unknown":422,"estimated":164} |
| stroke_stroke | {"unknown":422,"push":73,"lift":26,"clear":7,"drive":16,"net_shot":14,"drop":25,"smash":2,"rush":1} |
| stroke_attribution_reason | {"nearest_proximity":581,"ambiguous_proximity":5} |
| stroke_classification_abstention_reason | {"missing_required_evidence":416,"unresolved_initial_contact":6} |
| contact_actor | {"unknown":586} |
| contact_physical_event_status | {"ambiguous":192,"insufficient":306,"probable":88} |
| contact_contact_status | {"estimated":586} |
| contact_attribution_reason | {"nearest_proximity":581,"ambiguous_proximity":5} |
| contact_trajectory_reliability | {"insufficient":144,"ambiguous":124,"probable":318} |
| contact_trajectory_reasons | {"coherent_motion_change_unavailable":144,"association_unresolved":124,"supported_turn":251,"supported_launch":67} |
| contact_impact_reliability | {"ambiguous":192,"insufficient":306,"probable":88} |
| contact_impact_reasons | {"no_fresh_swing_or_racket_overlap":26,"association_unresolved":124,"fresh_player_observation_unavailable":306,"coherent_motion_and_fresh_contact_cue":88,"coherent_motion_change_unavailable":42} |
| contact_attribution_reliability | {"probable":201,"insufficient":385} |
| contact_attribution_reasons | {"geometric_attribution_not_verified_identity":201,"fresh_player_observation_unavailable":385} |
| rally_end_reason | {"stationary":27,"cut":6,"gap":14} |
| rally_phase | {"unknown":3,"match_play":44} |
| rally_official | {"False":18,"True":29} |
| rally_match_format_known | {"True":47} |
| rally_match_format | {"singles":47} |
| rally_winner | {"None":47} |
| rally_score_transition_status | {"unavailable":37,"candidate":10} |
| rally_admission_reason | {"duration_policy":46,"independent_contact_and_observed_motion_witnesses":1} |

#### Track/export counts

| Field | Observed value |
|---|---|
| camera_rows | 17915 |
| player_rows | 35554 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 34751 |
| projected_court_on_propagated_box | 18499 |
| racket_rows | 13504 |
| shuttle_rows | 17915 |

#### Track/export categories

| Field | Observed value |
|---|---|
| player_id | {"None":35554} |
| detector_matched | {"True":16635,"False":18919} |

| Semantic metric | Observed | Baseline comparison / limitation |
|---|---|---|
| Known rally winner output | 0/47 | Supplied coarse winner labels exist; identity/point mapping uncertified |
| Unknown stroke classification | 422/586 | Coarse one-label-per-rally ball_types is not exhaustive per-shot GT |
| Estimated stroke classification | 164/586 | Estimated coverage is not class accuracy |
| OCR saved readouts | 521 | Observed scoreboard rows, not accepted correct points |
| OCR label counts | {"AXELSEN":521,"NG K.L.A.":521} | Raw OCR labels may differ from anonymous Player A/B |
| Tracked invalid geometry frames | 6 | Geometric diagnostics, not labelled location error |
| Session degradation | [{"stage":"player_identity","reason":"osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"},{"stage":"player_reid","reason":"baseline player_reid provider is unavailable"}] | Identity/ReID unavailability remains recorded; no new models fetched |

### Runtime, resources and every saved stage latency

| Saved resource/runtime metric | Value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 2330635 |
| parent_failure_inclusive_elapsed_s | — |
| parent_failure_inclusive_source_fps | — |
| neural_only_throughput_fps | — |
| model_loading_time_s | — |
| media_ready_time_s | 1.798781 |
| model_staging_time_s | 1.690110 |
| worker_final_cpu_s | 23014.755924 |
| worker_maxrss_bytes | 2968973312 |
| sampled_worker_tree_peak_rss_bytes | 2848849920 |
| sampled_worker_gpu_peak_mib | 2128 |
| sampled_cpu_seconds_max_observed | 23015.030000 |
| sampled_cpu_seconds_last_observed | 23015.030000 |
| sampled_system_available_ram_min_bytes | 100391387136 |
| sample_count | 962 |
| resource_rows | 962 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 1992.107158 |
| parent_completed_source_fps | 8.992990 |
| worker_elapsed_s | 1984.001834 |
| worker_source_fps | 9.029730 |
| component_initialization_including_models_s | 9.016501 |

| Stage | Calls | Total wall s | P50 ms/call | P95 ms/call | Minimum ms | Maximum ms | Frame-population sum |
|---|---|---|---|---|---|---|---|
| court | 299 | 93.286964 | 306.185025 | 376.306024 | 178.771134 | 605.825330 | 17915 |
| content_continuity_and_players | 299 | 914.214473 | 3215.431924 | 3389.970557 | 682.432422 | 4429.769526 | 17915 |
| shuttle | 299 | 265.610635 | 863.391475 | 1038.947462 | 549.085467 | 1289.570461 | 17915 |
| players | 299 | 88.361330 | 268.988960 | 552.376746 | 16.347471 | 885.766088 | 17915 |
| ocr | 299 | 257.914674 | 862.024751 | 979.719452 | 589.922505 | 1244.743495 | 17915 |

| Runner timing scope | Seconds |
|---|---|
| component_initialization_including_models_s | 9.016501 |
| decode_perception_cache_s | 1734.215831 |

| Additional completed-worker timing | Seconds |
|---|---|
| Perception completion catalogue publication | 4.200773 |
| Worker media ready | 1.798781 |
| Model staging | 1.690110 |

| Actual worker reproducibility metadata | Value |
|---|---|
| Visible Torch devices | [{"logical_index":0,"name":"NVIDIA GeForce GTX 1080 Ti","uuid":"a618f090-66bf-ad80-b0a5-0c91bee61fab"}] |
| CUDA_VISIBLE_DEVICES GPU UUID | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| Prior cached perceptions used | false |
| Worker model manifest SHA256 | b5590b8ff1437945da036b42b01729f521728259a0dfc4c3299a926216ba8df3 |
| Worker staged model pins SHA256 | 7bd228ead493bba31c1417c46346d35e3cd00e1760ba7d7b35485d3babf5219f |

The historical timing key decode_perception_cache_s wraps the runner’s full _perceive call. Its name does not mean this was an observation-cache replay: the completed-worker receipts explicitly record cached_perception_used=false. It is a broad perception wall-time scope, not isolated cache decoding or pure GPU latency.

| Saved disk-use metric | Bytes / count |
|---|---|
| regular_files | 1823 |
| logical_bytes | 783575576 |
| allocated_bytes | 787226624 |
| staged_model_bytes | 361041769 |
| perception_cache_bytes | 80086201 |

Wall-time scopes overlap; they are not summable GPU kernel latency. Pure neural-only FPS and isolated model-loading time remain unavailable. For historical Tests 1/2, final worker-local timing/CPU/RSS fields were lost at catalogue publication and stay unavailable; failure-inclusive parent duration is identified explicitly. For normal runs, worker elapsed includes the runner and final catalogue verification. Current-process GPU samples cannot certify per-node ORT placement or true instantaneous memory peaks.

### Reproducibility, logs and annotation-file review

| Binding | Value |
|---|---|
| Normalized numerical profile SHA256 (passive ranges removed) | 2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb |
| Effective profile canonical SHA256 | fb7a3c75d5bcde4ca34a304aa6f89c388a4035c14c240f433cd8211a596d2346 |
| Model identity sets | 1 |
| Runtime identity sets | 1 |
| Actual model identity SHA256 | e3c96b7c2e522fd6efe6106328bebec30137f29b7303fe5e475f8aedea5d2222 |
| Actual runtime identity SHA256 | 81e41f18d858ed37c34ce9d07ae34a34268f27e57c0e5f878e07253be309066f |
| Executed plan | [plan.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test6/protocol/plan.json) |
| Actual completion receipt | [inference.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test6/run/inference.json) |
| Per-rally saved CSV | [per_rally_comparison.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test6/evaluation/per_rally_comparison.csv) |
| Technical analysis | [technical_analysis.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test6/analysis/technical_analysis.json) |
| Full original predictions | [predicted_rallies.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test6/run/predicted_rallies.csv) |

| Annotation file | Role | Data rows | Blank rows | Bytes | Column/schema inventory | SHA256 |
|---|---|---|---|---|---|---|
| Test6_Full.csv | Secondary coarse outcome/time reference | 42 | 0 | 3073 | ["start_time","end_time","win_point_player","win_reason","ball_types","lose_reason","roundscore_A","roundscore_B"] | 7def9c0b7c86514a3c0e10c03afacbac871b6dfcc04dc84074c91f00d6c54e3f |
| Test6_Full_T4.csv | Auxiliary historical/generated artifact; not certified independent truth | 43 | 0 | 3058 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 86a7d5a0f852038653fe5738e0f54fd012d713ae73e4c3da636e418cd5a0c0fa |
| Test6_Full_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 17915 | 0 | 269848 | ["Frame","X","Y","Visibility"] | 5bc9aa9b320da6dc48d6d7129ace7d1e6619ac82b83040d1da9bd4dae232eea2 |
| Test6_Full_court.json | Auxiliary historical/generated artifact; not certified independent truth | — | — | 643 | ["frame_no","frame_size","corners","net"] | df15d759abaa30ffaf9f31c9dbc271a25b19086ef79c7b93edb78acda018f540 |
| Test6_Full_rally.csv | Primary timing reference | 42 | 0 | 2993 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 237e7710a7f534bd2c7143c0010cca8872e46581f336c18c5be639f4349c4236 |
| player_detections.csv | Auxiliary historical/generated artifact; not certified independent truth | 17915 | 0 | 2005682 | ["frame_no","player_1_x","player_1_y","player_1_conf","player_2_x","player_2_y","player_2_conf"] | b1937c49f035c6dcfc6d697ae0f734d4af59ae2350fe7b2acb52f7ee651f40ea |
| win_predictions.csv | Auxiliary historical/generated artifact; not certified independent truth | 42 | 0 | 5136 | ["rally_idx","start_frame","end_frame","start_time","end_time","winner","loser","win_reason","reason_src","fault_side","fault_src","cnn_class","cnn_conf","cnn_oob","cnn_hn","cnn_wbl","score_Player A","score_Player B"] | 8a23a1ff0454bc5cdccfc4a48e761ed0f4f6de6b90abf1fc101f5d2924cc3d9c |

| Log | Lines | Warning/error-pattern lines | Distinct observed warning/error messages |
|---|---|---|---|
| analysis.log | 1 | 0 | [] |
| download.log | 124 | 0 | [] |
| evaluation.log | 0 | 0 | [] |
| prepare.log | 0 | 0 | [] |
| run.execution.log | 37 | 21 | ["2026-11-06 01:26:54 [warning  ] perception.degraded            reason='osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`' stage=player_identity","2026-11-06 01:26:54 [warning  ] perception.degraded            reason='baseline player_reid provider is unavailable' stage=player_reid","[WARNING] 2026-11-06 01:27:47,457 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:28:23,845 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:28:35,465 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:28:48,071 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:28:59,963 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:36:59,763 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:37:06,832 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:42:29,427 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:42:29,715 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:42:36,650 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:42:36,964 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:42:55,298 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:43:07,394 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:43:20,153 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:43:34,014 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:43:47,052 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:44:01,409 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:44:13,886 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 01:44:29,018 [RapidOCR] main.py:164: The text detection result is empty"] |
| run.launch.log | 0 | 0 | [] |
| timestamps.log | 1 | 0 | [] |

Log keyword counts are diagnostic string matches, not failed-inference counts. Tests 1/2 raw original worker logs remain in their source run directories and retain the known final catalogue failure; their independent completion proof is the accepted completion record. All previously completed evaluations remain immutable.

### Duration breakdown for this video

| GT duration bin | GT count | Matched | Missed | Recall | Start MAE f | End MAE f |
|---|---|---|---|---|---|---|
| ≤2 s | 0 | 0 | 0 | — | — | — |
| (2,5] s | 6 | 4 | 2 | 0.666667 | 5.250000 | 13.250000 |
| (5,10] s | 14 | 11 | 3 | 0.785714 | 12.363636 | 16.090909 |
| (10,20] s | 15 | 14 | 1 | 0.933333 | 40.142857 | 12.928571 |
| >20 s | 7 | 6 | 1 | 0.857143 | 17.166667 | 51.500000 |

## Test 7: complete evaluation and ground-truth comparison

Reference **30 rallies**, predictions **32**; TP/FP/FN **28/4/2**. Precision **87.500%**, recall **93.333%**, F1 **90.323%**. Matched mean IoU **0.833985**. The ground-truth benchmark for every table in this primary section is [Test7_Full_rally.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test7_Full/Test7_Full_rally.csv).

| Input / execution binding | Value |
|---|---|
| Decoded frames | 10725 |
| FPS | 30.000000 |
| Video duration seconds | 357.500000 |
| Canonical dimensions | 1280 × 720 |
| Source SHA256 | 1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c |
| Proxy SHA256 | 5a0bc6a8e750e67376c436941fb15730de9f5bd10fd107e483b93f4d5691e9e6 |
| Prediction SHA256 | bfabb336d7585fbfcd54215e4d6de8e36f818930dd6dbc26d74b8dd59a09af6b |
| Ground-truth SHA256 | 77e39aea68c9f627730a7b909bfabdd1a3e8f87cb977ea76327253f3af77a7d3 |
| Coarse reference SHA256 | 5f1ebabcc0a66dae579bf7ad35ddc48a97e88d1277cc7afa5e7d369a3fcbd9ea |
| Session | UPLOADTEST7 |
| Actual completion mode | normal_completed_worker |
| Original parent receipt status | completed |
| Full source/proxy PTS matches | 10725 |
| Scene probe pixel hashes verified | 13 |
| Verified saved files / logical bytes | 1412 / 596070042 |
| Read-only record | [saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test7) |

### Primary metric scores versus the ground-truth ideal

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 30 | 30 | 0 |
| Prediction count | 30 | 32 | 2 |
| TP / matched | 30 | 28 | -2 |
| FP | 0 | 4 | 4 |
| FN / missed | 0 | 2 | 2 |
| precision | 1 | 0.875000 | -0.125000 |
| recall | 1 | 0.933333 | -0.066667 |
| f1 | 1 | 0.903226 | -0.096774 |
| Mean matched IoU | 1 | 0.833985 | -0.166015 |
| Median matched IoU | 1 | 0.838456 | -0.161544 |
| Minimum matched IoU | 1 | 0.541176 | -0.458824 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 82.142857 |
| 0.9 | 100 | 35.714286 |
| 0.95 | 100 | 10.714286 |

A GT self-comparison has TP=N, FP=FN=0, precision/recall/F1=1, IoU=1 and every timing/duration error=0. This is the reference ideal, not a separately executed baseline model. The signed count difference alone is insufficient: false positives and misses can cancel.

### Boundary and duration errors versus zero-error ground truth

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.464286 | 9.000000 | 50.821466 | 227.000000 | 47.600000 | 21.321429 | 8.000000 |
| end_frame | 14.964286 | 9.500000 | 20.303941 | 49.000000 | 33.400000 | -9.750000 | -5.500000 |
| start_time_sec | 0.782143 | 0.300000 | 1.694049 | 7.566667 | 1.586667 | 0.710714 | 0.266667 |
| end_time_sec | 0.498810 | 0.316667 | 0.676798 | 1.633333 | 1.113333 | -0.325000 | -0.183333 |
| duration_sec | 1.178571 | 0.566667 | 2.017326 | 8.000000 | 1.963333 | -1.035714 | -0.500000 |

| Additional saved statistic | Value | Ground-truth ideal |
|---|---|---|
| Start P95 \|error\| frames | 94.050000 | 0 |
| End P95 \|error\| frames | 46.000000 | 0 |
| Duration mae frames | 35.357143 | 0 |
| Duration rmse frames | 60.519772 | 0 |
| Duration signed_bias frames | -31.071429 | 0 |

All error statistics above condition on eligible matched rallies. A positive start error is a late start; a negative start error is early. A positive end error is a late end; a negative end error is premature. Duration error is prediction minus GT. All 30 FPS frame errors convert by dividing by30; full signed/absolute per-rally values appear below. Misses have no invented zero error.

### Boundary tolerance scores

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 1 | 28 | 3.571% | 30 | 3.333% | 100% |
| start | 3 | 0.100000 | 4 | 28 | 14.286% | 30 | 13.333% | 100% |
| start | 5 | 0.166667 | 9 | 28 | 32.143% | 30 | 30.000% | 100% |
| start | 10 | 0.333333 | 17 | 28 | 60.714% | 30 | 56.667% | 100% |
| start | 15 | 0.500000 | 20 | 28 | 71.429% | 30 | 66.667% | 100% |
| start | 30 | 1.000000 | 24 | 28 | 85.714% | 30 | 80.000% | 100% |
| end | 1 | 0.033333 | 2 | 28 | 7.143% | 30 | 6.667% | 100% |
| end | 3 | 0.100000 | 6 | 28 | 21.429% | 30 | 20.000% | 100% |
| end | 5 | 0.166667 | 9 | 28 | 32.143% | 30 | 30.000% | 100% |
| end | 10 | 0.333333 | 15 | 28 | 53.571% | 30 | 50.000% | 100% |
| end | 15 | 0.500000 | 18 | 28 | 64.286% | 30 | 60.000% | 100% |
| end | 30 | 1.000000 | 25 | 28 | 89.286% | 30 | 83.333% | 100% |

### All saved error distributions

| Distribution / units | N | Mean | Median | Minimum | Maximum | P90 | P95 | Ideal |
|---|---|---|---|---|---|---|---|---|
| matched_iou | 28 | 0.833985 | 0.838456 | 0.541176 | 0.969799 | 0.950028 | 0.960343 | 1 |
| start_signed_frames | 28 | 21.321429 | 8.000000 | -30.000000 | 227.000000 | 47.600000 | 94.050000 | 0 |
| start_absolute_frames | 28 | 23.464286 | 9.000000 | 0.000000 | 227.000000 | 47.600000 | 94.050000 | 0 |
| end_signed_frames | 28 | -9.750000 | -5.500000 | -49.000000 | 18.000000 | 10.800000 | 15.650000 | 0 |
| end_absolute_frames | 28 | 14.964286 | 9.500000 | 1.000000 | 49.000000 | 33.400000 | 46.000000 | 0 |
| duration_signed_frames | 28 | -31.071429 | -15.000000 | -240.000000 | 39.000000 | 2.800000 | 10.900000 | 0 |
| duration_absolute_frames | 28 | 35.357143 | 17.000000 | 1.000000 | 240.000000 | 58.900000 | 123.250000 | 0 |
| duration_signed_seconds | 28 | -1.035714 | -0.500000 | -8.000000 | 1.300000 | 0.093333 | 0.363333 | 0 |

### Misses, extras, overlap topology and failure review

| Diagnostic | Observed | GT ideal / interpretation |
|---|---|---|
| Missed GT IDs | [3,22] | [] |
| Unmatched prediction IDs | [3,4,5,22] | [] |
| No-overlap missed GT IDs | [22] | [] |
| Predictions without any GT overlap | [] | [] |
| Possible split GT IDs | [3,20] | Geometric overlap candidates; not adjudicated semantic splits |
| Possible merge prediction IDs | [] | Geometric overlap candidates; not adjudicated semantic merges |
| Significant failure records | 15 | Unmatched or \|boundary error\|>30frames or IoU<0.75 |
| early_start_gt_ids | [17] | Direction/weak-overlap inventory, not a physical cause |
| late_start_gt_ids | [1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,19,20,21,23,24,25,26,27,28,29,30] | Direction/weak-overlap inventory, not a physical cause |
| premature_end_gt_ids | [1,2,4,6,7,8,10,12,13,14,15,16,18,20,25,26,27,28,29,30] | Direction/weak-overlap inventory, not a physical cause |
| late_end_gt_ids | [5,9,11,17,19,21,23,24] | Direction/weak-overlap inventory, not a physical cause |
| weak_iou_gt_ids | [2,10,17,20,28] | Direction/weak-overlap inventory, not a physical cause |

| Inventory validity | Ground truth | Predictions |
|---|---|---|
| count | 30 | 32 |
| duplicate_row_pairs | [] | [] |
| positive_overlap_row_pairs | [] | [] |
| adjacent_row_pairs | [] | [] |
| out_of_range_rows | [] | [] |
| out_of_order_rows | [] | [] |

| False detection P ID | Start frame | End frame | Start seconds | End seconds | Duration seconds | Positive-overlap GT IDs |
|---|---|---|---|---|---|---|
| 3 | 1118 | 1455 | 37.266667 | 48.500000 | 11.233333 | [3] |
| 4 | 1491 | 1615 | 49.700000 | 53.833333 | 4.133333 | [3] |
| 5 | 1648 | 1943 | 54.933333 | 64.766667 | 9.833333 | [3] |
| 22 | 6830 | 7018 | 227.666667 | 233.933333 | 6.266667 | [20] |

| Largest matched boundary cases | P ID | GT start/end frames | Pred start/end frames | Δstart frames | Δend frames | IoU |
|---|---|---|---|---|---|---|
| 20 | 23 | 6795–7406 | 7022–7393 | 227 | -13 | 0.607201 |
| 2 | 2 | 491–993 | 598–947 | 107 | -46 | 0.695219 |
| 5 | 7 | 2328–2805 | 2398–2807 | 70 | 2 | 0.849687 |
| 6 | 8 | 3143–3383 | 3148–3334 | 5 | -49 | 0.775000 |
| 4 | 6 | 2043–2275 | 2052–2229 | 9 | -46 | 0.762931 |

Of 2 unmatched reference intervals, 1 have no positive overlap with any prediction; 1 have some overlap but fail the one-to-one IoU eligibility/assignment. This separates absence of overlap from insufficient interval agreement without inventing a causal diagnosis.

### Every GT rally compared directly with its assigned prediction: frames

G IDs are one-based CSV row IDs in the primary rally reference. P IDs are one-based rows in the preserved prediction CSV. C IDs refer to the separate coarse table, linked only by the same IoU-based temporal crosswalk. “—” denotes unavailable/unmatched, not zero.

| G | P | GT start f | GT end f | Pred start f | Pred end f | Δstart f | \|Δstart\| f | Δend f | \|Δend\| f | IoU | Status | Coarse C row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 199 | 454 | 208 | 450 | 9 | 9 | -4 | 4 | 0.949020 | matched | 1 |
| 2 | 2 | 491 | 993 | 598 | 947 | 107 | 107 | -46 | 46 | 0.695219 | matched | 2 |
| 3 | — | 1115 | 1951 | — | — | — | — | — | — | — | missed | 3 |
| 4 | 6 | 2043 | 2275 | 2052 | 2229 | 9 | 9 | -46 | 46 | 0.762931 | matched | 5 |
| 5 | 7 | 2328 | 2805 | 2398 | 2807 | 70 | 70 | 2 | 2 | 0.849687 | matched | 6 |
| 6 | 8 | 3143 | 3383 | 3148 | 3334 | 5 | 5 | -49 | 49 | 0.775000 | matched | 7 |
| 7 | 9 | 3456 | 3537 | 3461 | 3531 | 5 | 5 | -6 | 6 | 0.864198 | matched | 8 |
| 8 | 10 | 3696 | 3840 | 3713 | 3839 | 17 | 17 | -1 | 1 | 0.875000 | matched | 9 |
| 9 | 11 | 3919 | 4380 | 3957 | 4383 | 38 | 38 | 3 | 3 | 0.911638 | matched | 10 |
| 10 | 12 | 4410 | 4543 | 4416 | 4515 | 6 | 6 | -28 | 28 | 0.744361 | matched | 11 |
| 11 | 13 | 4565 | 4676 | 4583 | 4685 | 18 | 18 | 9 | 9 | 0.775000 | matched | 12 |
| 12 | 14 | 4724 | 4818 | 4726 | 4815 | 2 | 2 | -3 | 3 | 0.946809 | matched | 13 |
| 13 | 15 | 5019 | 5203 | 5021 | 5193 | 2 | 2 | -10 | 10 | 0.934783 | matched | 14 |
| 14 | 16 | 5275 | 5424 | 5288 | 5410 | 13 | 13 | -14 | 14 | 0.818792 | matched | 15 |
| 15 | 17 | 5542 | 5632 | 5549 | 5623 | 7 | 7 | -9 | 9 | 0.822222 | matched | 16 |
| 16 | 18 | 5783 | 6081 | 5789 | 6078 | 6 | 6 | -3 | 3 | 0.969799 | matched | 17 |
| 17 | 19 | 6183 | 6229 | 6153 | 6238 | -30 | 30 | 9 | 9 | 0.541176 | matched | 18 |
| 18 | 20 | 6295 | 6567 | 6295 | 6547 | 0 | 0 | -20 | 20 | 0.926471 | matched | 19 |
| 19 | 21 | 6604 | 6715 | 6609 | 6733 | 5 | 5 | 18 | 18 | 0.821705 | matched | 20 |
| 20 | 23 | 6795 | 7406 | 7022 | 7393 | 227 | 227 | -13 | 13 | 0.607201 | matched | 21 |
| 21 | 24 | 7572 | 7680 | 7586 | 7695 | 14 | 14 | 15 | 15 | 0.764228 | matched | 22 |
| 22 | — | 7791 | 7884 | — | — | — | — | — | — | — | missed | 23 |
| 23 | 25 | 8024 | 8232 | 8036 | 8233 | 12 | 12 | 1 | 1 | 0.937799 | matched | 24 |
| 24 | 26 | 8400 | 8583 | 8409 | 8599 | 9 | 9 | 16 | 16 | 0.874372 | matched | 25 |
| 25 | 27 | 8687 | 8981 | 8696 | 8976 | 9 | 9 | -5 | 5 | 0.952381 | matched | 26 |
| 26 | 28 | 9076 | 9187 | 9079 | 9182 | 3 | 3 | -5 | 5 | 0.927928 | matched | 27 |
| 27 | 29 | 9303 | 9614 | 9308 | 9608 | 5 | 5 | -6 | 6 | 0.964630 | matched | 28 |
| 28 | 30 | 9703 | 9883 | 9722 | 9855 | 19 | 19 | -28 | 28 | 0.738889 | matched | 29 |
| 29 | 31 | 10244 | 10435 | 10250 | 10408 | 6 | 6 | -27 | 27 | 0.827225 | matched | 30 |
| 30 | 32 | 10605 | 10724 | 10609 | 10701 | 4 | 4 | -23 | 23 | 0.773109 | matched | 31 |

### Every GT rally compared directly: timestamps and durations

| G | GT start s | GT end s | Pred start s | Pred end s | GT duration s | Pred duration s | Δstart s | \|Δstart\| s | Δend s | \|Δend\| s | Δduration s | \|Δduration\| s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6.633333 | 15.133333 | 6.933333 | 15.000000 | 8.500000 | 8.066667 | 0.300000 | 0.300000 | -0.133333 | 0.133333 | -0.433333 | 0.433333 |
| 2 | 16.366667 | 33.100000 | 19.933333 | 31.566667 | 16.733333 | 11.633333 | 3.566667 | 3.566667 | -1.533333 | 1.533333 | -5.100000 | 5.100000 |
| 3 | 37.166667 | 65.033333 | — | — | 27.866667 | — | — | — | — | — | — | — |
| 4 | 68.100000 | 75.833333 | 68.400000 | 74.300000 | 7.733333 | 5.900000 | 0.300000 | 0.300000 | -1.533333 | 1.533333 | -1.833333 | 1.833333 |
| 5 | 77.600000 | 93.500000 | 79.933333 | 93.566667 | 15.900000 | 13.633333 | 2.333333 | 2.333333 | 0.066667 | 0.066667 | -2.266667 | 2.266667 |
| 6 | 104.766667 | 112.766667 | 104.933333 | 111.133333 | 8.000000 | 6.200000 | 0.166667 | 0.166667 | -1.633333 | 1.633333 | -1.800000 | 1.800000 |
| 7 | 115.200000 | 117.900000 | 115.366667 | 117.700000 | 2.700000 | 2.333333 | 0.166667 | 0.166667 | -0.200000 | 0.200000 | -0.366667 | 0.366667 |
| 8 | 123.200000 | 128.000000 | 123.766667 | 127.966667 | 4.800000 | 4.200000 | 0.566667 | 0.566667 | -0.033333 | 0.033333 | -0.600000 | 0.600000 |
| 9 | 130.633333 | 146.000000 | 131.900000 | 146.100000 | 15.366667 | 14.200000 | 1.266667 | 1.266667 | 0.100000 | 0.100000 | -1.166667 | 1.166667 |
| 10 | 147.000000 | 151.433333 | 147.200000 | 150.500000 | 4.433333 | 3.300000 | 0.200000 | 0.200000 | -0.933333 | 0.933333 | -1.133333 | 1.133333 |
| 11 | 152.166667 | 155.866667 | 152.766667 | 156.166667 | 3.700000 | 3.400000 | 0.600000 | 0.600000 | 0.300000 | 0.300000 | -0.300000 | 0.300000 |
| 12 | 157.466667 | 160.600000 | 157.533333 | 160.500000 | 3.133333 | 2.966667 | 0.066667 | 0.066667 | -0.100000 | 0.100000 | -0.166667 | 0.166667 |
| 13 | 167.300000 | 173.433333 | 167.366667 | 173.100000 | 6.133333 | 5.733333 | 0.066667 | 0.066667 | -0.333333 | 0.333333 | -0.400000 | 0.400000 |
| 14 | 175.833333 | 180.800000 | 176.266667 | 180.333333 | 4.966667 | 4.066667 | 0.433333 | 0.433333 | -0.466667 | 0.466667 | -0.900000 | 0.900000 |
| 15 | 184.733333 | 187.733333 | 184.966667 | 187.433333 | 3.000000 | 2.466667 | 0.233333 | 0.233333 | -0.300000 | 0.300000 | -0.533333 | 0.533333 |
| 16 | 192.766667 | 202.700000 | 192.966667 | 202.600000 | 9.933333 | 9.633333 | 0.200000 | 0.200000 | -0.100000 | 0.100000 | -0.300000 | 0.300000 |
| 17 | 206.100000 | 207.633333 | 205.100000 | 207.933333 | 1.533333 | 2.833333 | -1.000000 | 1.000000 | 0.300000 | 0.300000 | 1.300000 | 1.300000 |
| 18 | 209.833333 | 218.900000 | 209.833333 | 218.233333 | 9.066667 | 8.400000 | 0.000000 | 0.000000 | -0.666667 | 0.666667 | -0.666667 | 0.666667 |
| 19 | 220.133333 | 223.833333 | 220.300000 | 224.433333 | 3.700000 | 4.133333 | 0.166667 | 0.166667 | 0.600000 | 0.600000 | 0.433333 | 0.433333 |
| 20 | 226.500000 | 246.866667 | 234.066667 | 246.433333 | 20.366667 | 12.366667 | 7.566667 | 7.566667 | -0.433333 | 0.433333 | -8.000000 | 8.000000 |
| 21 | 252.400000 | 256.000000 | 252.866667 | 256.500000 | 3.600000 | 3.633333 | 0.466667 | 0.466667 | 0.500000 | 0.500000 | 0.033333 | 0.033333 |
| 22 | 259.700000 | 262.800000 | — | — | 3.100000 | — | — | — | — | — | — | — |
| 23 | 267.466667 | 274.400000 | 267.866667 | 274.433333 | 6.933333 | 6.566667 | 0.400000 | 0.400000 | 0.033333 | 0.033333 | -0.366667 | 0.366667 |
| 24 | 280.000000 | 286.100000 | 280.300000 | 286.633333 | 6.100000 | 6.333333 | 0.300000 | 0.300000 | 0.533333 | 0.533333 | 0.233333 | 0.233333 |
| 25 | 289.566667 | 299.366667 | 289.866667 | 299.200000 | 9.800000 | 9.333333 | 0.300000 | 0.300000 | -0.166667 | 0.166667 | -0.466667 | 0.466667 |
| 26 | 302.533333 | 306.233333 | 302.633333 | 306.066667 | 3.700000 | 3.433333 | 0.100000 | 0.100000 | -0.166667 | 0.166667 | -0.266667 | 0.266667 |
| 27 | 310.100000 | 320.466667 | 310.266667 | 320.266667 | 10.366667 | 10.000000 | 0.166667 | 0.166667 | -0.200000 | 0.200000 | -0.366667 | 0.366667 |
| 28 | 323.433333 | 329.433333 | 324.066667 | 328.500000 | 6.000000 | 4.433333 | 0.633333 | 0.633333 | -0.933333 | 0.933333 | -1.566667 | 1.566667 |
| 29 | 341.466667 | 347.833333 | 341.666667 | 346.933333 | 6.366667 | 5.266667 | 0.200000 | 0.200000 | -0.900000 | 0.900000 | -1.100000 | 1.100000 |
| 30 | 353.500000 | 357.466667 | 353.633333 | 356.700000 | 3.966667 | 3.066667 | 0.133333 | 0.133333 | -0.766667 | 0.766667 | -0.900000 | 0.900000 |

### Secondary coarse/outcome annotations: full supplied baseline and comparison

[Test7_Full.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test7_Full/Test7_Full.csv) contains **31 data rows**, **31 nonblank intervals**, blank row IDs **[]**. This separate reference differs from the 30-interval primary timing table. The same unchanged predictions and matcher give secondary precision **90.625%**, recall **93.548%**, F1 **92.063%**; this reference-sensitivity analysis does not replace the primary benchmark. No labels, times or predictions were fitted or repaired.

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 31 | 31 | 0 |
| Prediction count | 31 | 32 | 1 |
| TP / matched | 31 | 29 | -2 |
| FP | 0 | 3 | 3 |
| FN / missed | 0 | 2 | 2 |
| precision | 1 | 0.906250 | -0.093750 |
| recall | 1 | 0.935484 | -0.064516 |
| f1 | 1 | 0.920635 | -0.079365 |
| Mean matched IoU | 1 | 0.779333 | -0.220667 |
| Median matched IoU | 1 | 0.793478 | -0.206522 |
| Minimum matched IoU | 1 | 0.584013 | -0.415987 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 62.068966 |
| 0.9 | 100 | 13.793103 |
| 0.95 | 100 | 3.448276 |

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 33.896552 | 25.000000 | 55.135257 | 242.000000 | 60.000000 | 32.103448 | 25.000000 |
| end_frame | 18.896552 | 13.000000 | 31.857441 | 135.000000 | 43.800000 | 5.172414 | 8.000000 |
| start_time_sec | 1.129885 | 0.833333 | 1.837842 | 8.066667 | 2.000000 | 1.070115 | 0.833333 |
| end_time_sec | 0.629885 | 0.433333 | 1.061915 | 4.500000 | 1.460000 | 0.172414 | 0.266667 |
| duration_sec | 1.095402 | 0.700000 | 1.826466 | 7.633333 | 2.086667 | -0.897701 | -0.600000 |

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 0 | 29 | 0.000% | 31 | 0.000% | 100% |
| start | 3 | 0.100000 | 4 | 29 | 13.793% | 31 | 12.903% | 100% |
| start | 5 | 0.166667 | 4 | 29 | 13.793% | 31 | 12.903% | 100% |
| start | 10 | 0.333333 | 5 | 29 | 17.241% | 31 | 16.129% | 100% |
| start | 15 | 0.500000 | 8 | 29 | 27.586% | 31 | 25.806% | 100% |
| start | 30 | 1.000000 | 21 | 29 | 72.414% | 31 | 67.742% | 100% |
| end | 1 | 0.033333 | 2 | 29 | 6.897% | 31 | 6.452% | 100% |
| end | 3 | 0.100000 | 7 | 29 | 24.138% | 31 | 22.581% | 100% |
| end | 5 | 0.166667 | 8 | 29 | 27.586% | 31 | 25.806% | 100% |
| end | 10 | 0.333333 | 14 | 29 | 48.276% | 31 | 45.161% | 100% |
| end | 15 | 0.500000 | 19 | 29 | 65.517% | 31 | 61.290% | 100% |
| end | 30 | 1.000000 | 24 | 29 | 82.759% | 31 | 77.419% | 100% |

| Cross-reference timing diagnostic | Value |
|---|---|
| Primary-to-coarse eligible matched intervals | 30 |
| Primary intervals unmatched to coarse reference | [] |
| Coarse rows unmatched to primary reference | [4] |
| Primary/coarse matched mean IoU | 0.756170 |

| C source row | Supplied start | Supplied end | Supplied winner | Supplied A:B score | Supplied shot / ball_types | Win reason | Lose reason | Matched P | IoU | Δstart s | Δend s | Δduration s | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 15 | Player A | 0:1 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 1 | 0.896296 | 0.933333 | 0.000000 | -0.933333 | matched |
| 2 | 19 | 31 | Player B | 0:2 | Net Shot | Opponent Hit the Net | Hit the Net | 2 | 0.880637 | 0.933333 | 0.566667 | -0.366667 | matched |
| 3 | 38 | 53 | Player B | 0:3 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 3 | 0.667373 | -0.733333 | -4.500000 | -3.766667 | matched |
| 4 | 55 | 65 | Player A | 1:3 | Smash | Winner Shot | Opponent Failed to Return | 5 | 0.970199 | -0.066667 | -0.233333 | -0.166667 | matched |
| 5 | 68 | 74 | Player A | 2:3 | Drop Shot | Opponent Out of Bounds | Hit Out of Bounds | 6 | 0.888889 | 0.400000 | 0.300000 | -0.100000 | matched |
| 6 | 78 | 92 | Player B | 2:4 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 7 | 0.775161 | 1.933333 | 1.566667 | -0.366667 | matched |
| 7 | 105 | 112 | Player A | 3:4 | Hook Shot | Opponent Out of Bounds | Hit Out of Bounds | 8 | 0.867925 | -0.066667 | -0.866667 | -0.800000 | matched |
| 8 | 115 | 117 | Player A | 4:4 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 9 | 0.604938 | 0.366667 | 0.700000 | 0.333333 | matched |
| 9 | 123 | 128 | Player B | 4:5 | Net Shot | Opponent Hit the Net | Hit the Net | 10 | 0.840000 | 0.766667 | -0.033333 | -0.800000 | matched |
| 10 | 131 | 146 | Player B | 4:6 | Net Block Shot | Opponent Hit the Net | Hit the Net | 11 | 0.933775 | 0.900000 | 0.100000 | -0.800000 | matched |
| 11 | 146 | 150 | Player B | 4:7 | Smash | Winner Shot | Opponent Failed to Return | 12 | 0.622222 | 1.200000 | 0.500000 | -0.700000 | matched |
| 12 | 151 | 156 | Player A | 5:7 | Slice Shot | Opponent Out of Bounds | Hit Out of Bounds | 13 | 0.625806 | 1.766667 | 0.166667 | -1.600000 | matched |
| 13 | 157 | 160 | Player B | 5:8 | Drop Shot | Opponent Hit the Net | Hit the Net | 14 | 0.704762 | 0.533333 | 0.500000 | -0.033333 | matched |
| 14 | 167 | 173 | Player B | 5:9 | Smash | Winner Shot | Opponent Failed to Return | 15 | 0.923497 | 0.366667 | 0.100000 | -0.266667 | matched |
| 15 | 175 | 180 | Player B | 5:10 | Net Shot | Opponent Hit the Net | Hit the Net | 16 | 0.700000 | 1.266667 | 0.333333 | -0.933333 | matched |
| 16 | 184 | 187 | Player A | 6:10 | Drop Shot | Opponent Hit the Net | Hit the Net | 17 | 0.592233 | 0.966667 | 0.433333 | -0.533333 | matched |
| 17 | 192 | 201 | Player A | 7:10 | Lift Shot | Opponent Hit the Net | Hit the Net | 18 | 0.757862 | 0.966667 | 1.600000 | 0.633333 | matched |
| 18 | 205 | 208 | Player A | 8:10 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 19 | 0.944444 | 0.100000 | -0.066667 | -0.166667 | matched |
| 19 | 209 | 218 | Player B | 8:11 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 20 | 0.884477 | 0.833333 | 0.233333 | -0.600000 | matched |
| 20 | 220 | 223 | Player B | 8:12 | Smash | Winner Shot | Opponent Failed to Return | 21 | 0.609023 | 0.300000 | 1.433333 | 1.133333 | matched |
| 21 | 226 | 246 | Player A | 9:12 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 23 | 0.584013 | 8.066667 | 0.433333 | -7.633333 | matched |
| 22 | 252 | 255 | Player A | 10:12 | Smash | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 23 | 259 | 262 | Player B | 10:13 | Push Shot | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 24 | 266 | 275 | Player B | 10:14 | Smash | Winner Shot | Opponent Failed to Return | 25 | 0.729630 | 1.866667 | -0.566667 | -2.433333 | matched |
| 25 | 278 | 286 | Player A | 11:14 | Drop Shot | Opponent Out of Bounds | Hit Out of Bounds | 26 | 0.660232 | 2.300000 | 0.633333 | -1.666667 | matched |
| 26 | 289 | 298 | Player A | 12:14 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 27 | 0.797386 | 0.866667 | 1.200000 | 0.333333 | matched |
| 27 | 302 | 306 | Player B | 12:15 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 28 | 0.827869 | 0.633333 | 0.066667 | -0.566667 | matched |
| 28 | 308 | 320 | Player A | 13:15 | Net Shot | Opponent Hit the Net | Hit the Net | 29 | 0.793478 | 2.266667 | 0.266667 | -2.000000 | matched |
| 29 | 324 | 328 | Player A | 14:15 | Hook Shot | Opponent Out of Bounds | Hit Out of Bounds | 30 | 0.874074 | 0.066667 | 0.500000 | 0.433333 | matched |
| 30 | 341 | 347 | Player B | 14:16 | Smash | Winner Shot | Opponent Failed to Return | 31 | 0.877778 | 0.666667 | -0.066667 | -0.733333 | matched |
| 31 | 353 | 357 | Player A | 15:16 | Hook Shot | Winner Shot | Opponent Failed to Return | 32 | 0.766667 | 0.633333 | -0.300000 | -0.933333 | matched |

| Secondary-reference unmatched P | Start f | End f | Start s | End s |
|---|---|---|---|---|
| 4 | 1491 | 1615 | 49.700000 | 53.833333 |
| 22 | 6830 | 7018 | 227.666667 | 233.933333 |
| 24 | 7586 | 7695 | 252.866667 | 256.500000 |

| Supplied semantic label inventory | Counts |
|---|---|
| win_point_player | {"Player A":16,"Player B":15} |
| ball_types | {"Lift Shot":5,"Net Shot":4,"Push Shot":5,"Smash":7,"Drop Shot":4,"Hook Shot":3,"Clear Shot":1,"Net Block Shot":1,"Slice Shot":1} |
| roundscore_A | {"0":3,"1":1,"2":2,"3":1,"4":4,"5":4,"6":1,"7":1,"8":3,"9":1,"10":3,"11":1,"12":2,"13":1,"14":2,"15":1} |
| roundscore_B | {"1":1,"2":1,"3":3,"4":3,"5":1,"6":1,"7":2,"8":1,"9":1,"10":4,"11":1,"12":3,"13":1,"14":3,"15":3,"16":2} |

The supplied winner/score/shot fields are reproduced above exactly as source strings, including missing values and taxonomy variation. The temporal crosswalk does not establish named player/team equivalence, certified point identity, or exhaustive shot labels. Current rally winners are unknown and hitter identities are anonymous; outcome/score-sequence accuracy and per-shot confusion therefore remain unscorable, rather than being reported as verified model correctness.

### Component-level observed output versus available ground truth

| Coverage diagnostic | Numerator | Denominator | Coverage | Ground-truth accuracy available? |
|---|---|---|---|---|
| Raw shuttle present / source frames | 6489 | 10725 | 60.503% | No reviewed frame/person/contact labels |
| Detector-executed / source frames | 4071 | 10725 | 37.958% | No reviewed frame/person/contact labels |
| Fresh detector-matched person rows / person rows | 8052 | 20210 | 39.842% | No reviewed frame/person/contact labels |
| Current pose rows / person rows | 15036 | 20210 | 74.399% | No reviewed frame/person/contact labels |
| Current racket rows / person rows | 6671 | 20210 | 33.008% | No reviewed frame/person/contact labels |

| All component coverage counts | Value |
|---|---|
| frames | 10725 |
| raw_shuttle_present | 6489 |
| detector_executed_frames | 4071 |
| person_rows | 20210 |
| scene_telemetry_present | 3607 |
| scene_raw_hypotheses | 13 |
| actual_content_epoch_increments | 13 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 8052 |
| person_propagated_or_unmatched | 12158 |
| pose_present_rows | 15036 |
| pose_current_source_rows | 15036 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 6984 |
| racket_present_rows | 6671 |
| racket_current_source_rows | 6671 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 13 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 13 |

#### Frame/component categories

| Field | Observed value |
|---|---|
| view | {"main":10230,"none":495} |
| calibration_state | {"REACQUIRING":36,"VALID":10194,"LOST":495} |
| player_population | {"0":552,"2":10037,"1":136} |
| association_status | {"missing":3741,"observed":6487,"invalid":495,"ambiguous":2} |
| association_reason | {"no_accepted_raw_observation":3741,"fresh_selection_retained":6487,"image_view_invalid":495,"coobserved_competing_static_hypothesis":2} |
| scene_raw_status | {"unknown":255,"measured":3339,"hypothesis":13} |
| person_detector_match | {"True":8052,"False":12158} |
| person_identity_method | {"bytetrack_v1":20210} |
| scene_decision | {"barrier":13} |
| scene_decision_reason | {"raw_change_and_current_layout_discontinuity":13} |

#### Live event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 98 |
| scene | 14 |
| participant_observation | 130 |
| format_decision | 1 |
| rally_start | 32 |
| rally_end | 32 |
| stroke | 250 |
| contact | 250 |
| shuttle_turn | 22 |
| identity_ambiguity | 41 |
| broadcast_score | 261 |
| match_phase | 1 |

#### Append-only event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 98 |
| scene | 14 |
| participant_observation | 130 |
| format_decision | 1 |
| rally_start | 60 |
| rally_end | 32 |
| contact | 544 |
| stroke | 262 |
| shuttle_turn | 22 |
| identity_ambiguity | 41 |
| broadcast_score | 261 |
| match_phase | 1 |

#### All observed event categories

| Field | Observed value |
|---|---|
| event_status | {"confirmed":908,"provisional":225} |
| rally_end_reason | {"stationary":11,"cut":11,"gap":10} |
| rally_phase | {"unknown":3,"match_play":29} |
| rally_official | {"False":11,"True":21} |
| rally_match_format_known | {"True":32} |
| rally_match_format | {"singles":32} |
| rally_winner | {"None":32} |
| rally_score_transition_status | {"unavailable":23,"candidate":9} |
| rally_admission_reason | {"duration_policy":32} |
| stroke_actor | {"unknown":250} |
| stroke_physical_event_status | {"insufficient":126,"probable":34,"ambiguous":90} |
| stroke_contact_status | {"estimated":250} |
| stroke_classification_status | {"unknown":184,"estimated":66} |
| stroke_stroke | {"unknown":184,"push":27,"lift":8,"net_shot":10,"drop":14,"clear":3,"drive":3,"smash":1} |
| stroke_attribution_reason | {"nearest_proximity":250} |
| stroke_classification_abstention_reason | {"missing_required_evidence":182,"unresolved_initial_contact":2} |
| contact_actor | {"unknown":250} |
| contact_physical_event_status | {"insufficient":126,"probable":34,"ambiguous":90} |
| contact_contact_status | {"estimated":250} |
| contact_attribution_reason | {"nearest_proximity":250} |
| contact_trajectory_reliability | {"insufficient":64,"probable":130,"ambiguous":56} |
| contact_trajectory_reasons | {"coherent_motion_change_unavailable":64,"supported_turn":100,"association_unresolved":56,"supported_launch":30} |
| contact_impact_reliability | {"insufficient":126,"probable":34,"ambiguous":90} |
| contact_impact_reasons | {"fresh_player_observation_unavailable":126,"coherent_motion_and_fresh_contact_cue":34,"no_fresh_swing_or_racket_overlap":17,"association_unresolved":56,"coherent_motion_change_unavailable":17} |
| contact_attribution_reliability | {"insufficient":167,"probable":83} |
| contact_attribution_reasons | {"fresh_player_observation_unavailable":167,"geometric_attribution_not_verified_identity":83} |

#### Track/export counts

| Field | Observed value |
|---|---|
| camera_rows | 10725 |
| player_rows | 20196 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 19777 |
| projected_court_on_propagated_box | 11948 |
| racket_rows | 6657 |
| shuttle_rows | 10725 |

#### Track/export categories

| Field | Observed value |
|---|---|
| player_id | {"None":20196} |
| detector_matched | {"True":8038,"False":12158} |

| Semantic metric | Observed | Baseline comparison / limitation |
|---|---|---|
| Known rally winner output | 0/32 | Supplied coarse winner labels exist; identity/point mapping uncertified |
| Unknown stroke classification | 184/250 | Coarse one-label-per-rally ball_types is not exhaustive per-shot GT |
| Estimated stroke classification | 66/250 | Estimated coverage is not class accuracy |
| OCR saved readouts | 289 | Observed scoreboard rows, not accepted correct points |
| OCR label counts | {"TAI T.Y.":289,"MARIN":289} | Raw OCR labels may differ from anonymous Player A/B |
| Tracked invalid geometry frames | 531 | Geometric diagnostics, not labelled location error |
| Session degradation | [{"stage":"player_identity","reason":"osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"},{"stage":"player_reid","reason":"baseline player_reid provider is unavailable"}] | Identity/ReID unavailability remains recorded; no new models fetched |

### Runtime, resources and every saved stage latency

| Saved resource/runtime metric | Value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 2342110 |
| parent_failure_inclusive_elapsed_s | — |
| parent_failure_inclusive_source_fps | — |
| neural_only_throughput_fps | — |
| model_loading_time_s | — |
| media_ready_time_s | 1.810870 |
| model_staging_time_s | 1.687080 |
| worker_final_cpu_s | 12506.818761 |
| worker_maxrss_bytes | 2926637056 |
| sampled_worker_tree_peak_rss_bytes | 2906685440 |
| sampled_worker_gpu_peak_mib | 2122 |
| sampled_cpu_seconds_max_observed | 12506.370000 |
| sampled_cpu_seconds_last_observed | 12506.370000 |
| sampled_system_available_ram_min_bytes | 100699070464 |
| sample_count | 502 |
| resource_rows | 502 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 1039.893208 |
| parent_completed_source_fps | 10.313559 |
| worker_elapsed_s | 1034.103667 |
| worker_source_fps | 10.371301 |
| component_initialization_including_models_s | 8.671007 |

| Stage | Calls | Total wall s | P50 ms/call | P95 ms/call | Minimum ms | Maximum ms | Frame-population sum |
|---|---|---|---|---|---|---|---|
| court | 179 | 68.672542 | 306.057158 | 919.143188 | 265.484194 | 2107.367248 | 10725 |
| content_continuity_and_players | 179 | 446.574734 | 2993.729927 | 3292.306164 | 48.957738 | 3567.469250 | 10725 |
| shuttle | 177 | 149.761735 | 842.753866 | 960.724405 | 691.230885 | 1118.235081 | 10605 |
| players | 179 | 54.752907 | 296.161325 | 645.334126 | 0.690241 | 912.387177 | 10725 |
| ocr | 179 | 141.920904 | 815.848548 | 931.442892 | 0.015961 | 1198.294183 | 10725 |

| Runner timing scope | Seconds |
|---|---|
| component_initialization_including_models_s | 8.671007 |
| decode_perception_cache_s | 927.452383 |

| Additional completed-worker timing | Seconds |
|---|---|
| Perception completion catalogue publication | 2.623090 |
| Worker media ready | 1.810870 |
| Model staging | 1.687080 |

| Actual worker reproducibility metadata | Value |
|---|---|
| Visible Torch devices | [{"logical_index":0,"name":"NVIDIA GeForce GTX 1080 Ti","uuid":"a618f090-66bf-ad80-b0a5-0c91bee61fab"}] |
| CUDA_VISIBLE_DEVICES GPU UUID | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| Prior cached perceptions used | false |
| Worker model manifest SHA256 | b5590b8ff1437945da036b42b01729f521728259a0dfc4c3299a926216ba8df3 |
| Worker staged model pins SHA256 | 7bd228ead493bba31c1417c46346d35e3cd00e1760ba7d7b35485d3babf5219f |

The historical timing key decode_perception_cache_s wraps the runner’s full _perceive call. Its name does not mean this was an observation-cache replay: the completed-worker receipts explicitly record cached_perception_used=false. It is a broad perception wall-time scope, not isolated cache decoding or pure GPU latency.

| Saved disk-use metric | Bytes / count |
|---|---|
| regular_files | 1098 |
| logical_bytes | 591504236 |
| allocated_bytes | 593846272 |
| staged_model_bytes | 361041769 |
| perception_cache_bytes | 49574950 |

Wall-time scopes overlap; they are not summable GPU kernel latency. Pure neural-only FPS and isolated model-loading time remain unavailable. For historical Tests 1/2, final worker-local timing/CPU/RSS fields were lost at catalogue publication and stay unavailable; failure-inclusive parent duration is identified explicitly. For normal runs, worker elapsed includes the runner and final catalogue verification. Current-process GPU samples cannot certify per-node ORT placement or true instantaneous memory peaks.

### Reproducibility, logs and annotation-file review

| Binding | Value |
|---|---|
| Normalized numerical profile SHA256 (passive ranges removed) | 2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb |
| Effective profile canonical SHA256 | 1132719c9be213270bdcb073f808a0744e1e94cb0a44a1ed0d8a997d2ce9141c |
| Model identity sets | 1 |
| Runtime identity sets | 1 |
| Actual model identity SHA256 | e3c96b7c2e522fd6efe6106328bebec30137f29b7303fe5e475f8aedea5d2222 |
| Actual runtime identity SHA256 | 81e41f18d858ed37c34ce9d07ae34a34268f27e57c0e5f878e07253be309066f |
| Executed plan | [plan.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test7/protocol/plan.json) |
| Actual completion receipt | [inference.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test7/run/inference.json) |
| Per-rally saved CSV | [per_rally_comparison.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test7/evaluation/per_rally_comparison.csv) |
| Technical analysis | [technical_analysis.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test7/analysis/technical_analysis.json) |
| Full original predictions | [predicted_rallies.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test7/run/predicted_rallies.csv) |

| Annotation file | Role | Data rows | Blank rows | Bytes | Column/schema inventory | SHA256 |
|---|---|---|---|---|---|---|
| Test7_Full.csv | Secondary coarse outcome/time reference | 31 | 0 | 2227 | ["start_time","end_time","win_point_player","win_reason","ball_types","lose_reason","roundscore_A","roundscore_B"] | 5f1ebabcc0a66dae579bf7ad35ddc48a97e88d1277cc7afa5e7d369a3fcbd9ea |
| Test7_Full_T4.csv | Auxiliary historical/generated artifact; not certified independent truth | 33 | 0 | 2228 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 36c89e5a396ee3f01d654a5ef3d75822703e272608b706b805f166887cefc854 |
| Test7_Full_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 10725 | 0 | 147588 | ["Frame","X","Y","Visibility"] | ab8a89adff001cbe1c90d89c4b15231599982bffbd2478832bf0d1a90380dfdd |
| Test7_Full_court.json | Auxiliary historical/generated artifact; not certified independent truth | — | — | 644 | ["frame_no","frame_size","corners","net"] | 2cdd63047b79b51564958d7bc7a6b8c4b42b1bf992f1479e28c332f87cc5ccb0 |
| Test7_Full_rally.csv | Primary timing reference | 30 | 0 | 2030 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 77e39aea68c9f627730a7b909bfabdd1a3e8f87cb977ea76327253f3af77a7d3 |
| player_detections.csv | Auxiliary historical/generated artifact; not certified independent truth | 10725 | 0 | 1186903 | ["frame_no","player_1_x","player_1_y","player_1_conf","player_2_x","player_2_y","player_2_conf"] | 2ec4903e62f0de5b78767e5812d0c9bbd48bb5581de9ad3bb43528a28988728d |
| win_predictions.csv | Auxiliary historical/generated artifact; not certified independent truth | 30 | 0 | 3722 | ["rally_idx","start_frame","end_frame","start_time","end_time","winner","loser","win_reason","reason_src","fault_side","fault_src","cnn_class","cnn_conf","cnn_oob","cnn_hn","cnn_wbl","score_Player A","score_Player B"] | d74081e4cd71a5ea17323838794059b9b9d8d1c4956507876a5024b6e298ae75 |

| Log | Lines | Warning/error-pattern lines | Distinct observed warning/error messages |
|---|---|---|---|
| analysis.log | 1 | 0 | [] |
| download.log | 75 | 0 | [] |
| evaluation.log | 0 | 0 | [] |
| prepare.log | 0 | 0 | [] |
| run.execution.log | 33 | 17 | ["2026-11-06 02:04:58 [warning  ] perception.degraded            reason='osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`' stage=player_identity","2026-11-06 02:04:58 [warning  ] perception.degraded            reason='baseline player_reid provider is unavailable' stage=player_reid","[WARNING] 2026-11-06 02:05:40,128 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:05:50,123 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:06:01,752 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:06:11,112 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:06:20,969 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:06:44,348 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:13:50,439 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:13:53,907 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:13:54,203 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:13:58,762 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:14:15,778 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:14:28,459 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:14:36,896 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:14:50,199 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:17:23,171 [RapidOCR] main.py:164: The text detection result is empty"] |
| run.launch.log | 0 | 0 | [] |
| timestamps.log | 1 | 0 | [] |

Log keyword counts are diagnostic string matches, not failed-inference counts. Tests 1/2 raw original worker logs remain in their source run directories and retain the known final catalogue failure; their independent completion proof is the accepted completion record. All previously completed evaluations remain immutable.

### Duration breakdown for this video

| GT duration bin | GT count | Matched | Missed | Recall | Start MAE f | End MAE f |
|---|---|---|---|---|---|---|
| ≤2 s | 1 | 1 | 0 | 1.000000 | 30.000000 | 9.000000 |
| (2,5] s | 12 | 11 | 1 | 0.916667 | 8.545455 | 11.909091 |
| (5,10] s | 11 | 11 | 0 | 1.000000 | 7.818182 | 19.000000 |
| (10,20] s | 4 | 4 | 0 | 1.000000 | 55.000000 | 14.250000 |
| >20 s | 2 | 1 | 1 | 0.500000 | 227.000000 | 13.000000 |

## Test 9: complete evaluation and ground-truth comparison

Reference **82 rallies**, predictions **84**; TP/FP/FN **69/15/13**. Precision **82.143%**, recall **84.146%**, F1 **83.133%**. Matched mean IoU **0.862791**. The ground-truth benchmark for every table in this primary section is [Test9_Full_rally.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test9_Full/Test9_Full_rally.csv).

| Input / execution binding | Value |
|---|---|
| Decoded frames | 33157 |
| FPS | 30.000000 |
| Video duration seconds | 1105.233333 |
| Canonical dimensions | 1280 × 720 |
| Source SHA256 | f2aabeb9610c437b38b840ae45885b4b71854702a6b30dd4aee4c54d1417dd4a |
| Proxy SHA256 | 307b8593d7c89d0675d1219d9f56f29f6e4d9f5891a24145b02d8d14f86304ed |
| Prediction SHA256 | b78dac38a83b3e63d5d358c5c9ef8c84ae95a52293cf5420c1e65f903a96b3ce |
| Ground-truth SHA256 | 39dd99a09db0c9e4a669c504cebed0fbad69927e339884127c48bf63da073435 |
| Coarse reference SHA256 | f770e681fd033bbfe8061565b58f5d09d2042a1029447e7f22a1d05af8166d3f |
| Session | UPLOADTEST9 |
| Actual completion mode | normal_completed_worker |
| Original parent receipt status | completed |
| Full source/proxy PTS matches | 33157 |
| Scene probe pixel hashes verified | 46 |
| Verified saved files / logical bytes | 3636 / 1254208433 |
| Read-only record | [saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test9) |

### Primary metric scores versus the ground-truth ideal

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 82 | 82 | 0 |
| Prediction count | 82 | 84 | 2 |
| TP / matched | 82 | 69 | -13 |
| FP | 0 | 15 | 15 |
| FN / missed | 0 | 13 | 13 |
| precision | 1 | 0.821429 | -0.178571 |
| recall | 1 | 0.841463 | -0.158537 |
| f1 | 1 | 0.831325 | -0.168675 |
| Mean matched IoU | 1 | 0.862791 | -0.137209 |
| Median matched IoU | 1 | 0.909814 | -0.090186 |
| Minimum matched IoU | 1 | 0.522222 | -0.477778 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 81.159420 |
| 0.9 | 100 | 56.521739 |
| 0.95 | 100 | 24.637681 |

A GT self-comparison has TP=N, FP=FN=0, precision/recall/F1=1, IoU=1 and every timing/duration error=0. This is the reference ideal, not a separately executed baseline model. The signed count difference alone is insufficient: false positives and misses can cancel.

### Boundary and duration errors versus zero-error ground truth

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 22.869565 | 6.000000 | 55.743980 | 286.000000 | 35.400000 | 3.072464 | 5.000000 |
| end_frame | 18.884058 | 9.000000 | 40.080535 | 184.000000 | 30.800000 | -6.275362 | -3.000000 |
| start_time_sec | 0.762319 | 0.200000 | 1.858133 | 9.533333 | 1.180000 | 0.102415 | 0.166667 |
| end_time_sec | 0.629469 | 0.300000 | 1.336018 | 6.133333 | 1.026667 | -0.209179 | -0.100000 |
| duration_sec | 1.250725 | 0.633333 | 2.218735 | 9.033333 | 4.180000 | -0.311594 | -0.400000 |

| Additional saved statistic | Value | Ground-truth ideal |
|---|---|---|
| Start P95 \|error\| frames | 139.400000 | 0 |
| End P95 \|error\| frames | 54.600000 | 0 |
| Duration mae frames | 37.521739 | 0 |
| Duration rmse frames | 66.562056 | 0 |
| Duration signed_bias frames | -9.347826 | 0 |

All error statistics above condition on eligible matched rallies. A positive start error is a late start; a negative start error is early. A positive end error is a late end; a negative end error is premature. Duration error is prediction minus GT. All 30 FPS frame errors convert by dividing by30; full signed/absolute per-rally values appear below. Misses have no invented zero error.

### Boundary tolerance scores

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 9 | 69 | 13.043% | 82 | 10.976% | 100% |
| start | 3 | 0.100000 | 15 | 69 | 21.739% | 82 | 18.293% | 100% |
| start | 5 | 0.166667 | 32 | 69 | 46.377% | 82 | 39.024% | 100% |
| start | 10 | 0.333333 | 50 | 69 | 72.464% | 82 | 60.976% | 100% |
| start | 15 | 0.500000 | 54 | 69 | 78.261% | 82 | 65.854% | 100% |
| start | 30 | 1.000000 | 59 | 69 | 85.507% | 82 | 71.951% | 100% |
| end | 1 | 0.033333 | 10 | 69 | 14.493% | 82 | 12.195% | 100% |
| end | 3 | 0.100000 | 16 | 69 | 23.188% | 82 | 19.512% | 100% |
| end | 5 | 0.166667 | 27 | 69 | 39.130% | 82 | 32.927% | 100% |
| end | 10 | 0.333333 | 39 | 69 | 56.522% | 82 | 47.561% | 100% |
| end | 15 | 0.500000 | 48 | 69 | 69.565% | 82 | 58.537% | 100% |
| end | 30 | 1.000000 | 62 | 69 | 89.855% | 82 | 75.610% | 100% |

### All saved error distributions

| Distribution / units | N | Mean | Median | Minimum | Maximum | P90 | P95 | Ideal |
|---|---|---|---|---|---|---|---|---|
| matched_iou | 69 | 0.862791 | 0.909814 | 0.522222 | 0.996000 | 0.980465 | 0.989110 | 1 |
| start_signed_frames | 69 | 3.072464 | 5.000000 | -286.000000 | 160.000000 | 30.800000 | 38.200000 | 0 |
| start_absolute_frames | 69 | 22.869565 | 6.000000 | 0.000000 | 286.000000 | 35.400000 | 139.400000 | 0 |
| end_signed_frames | 69 | -6.275362 | -3.000000 | -179.000000 | 184.000000 | 12.400000 | 18.400000 | 0 |
| end_absolute_frames | 69 | 18.884058 | 9.000000 | 0.000000 | 184.000000 | 30.800000 | 54.600000 | 0 |
| duration_signed_frames | 69 | -9.347826 | -12.000000 | -187.000000 | 271.000000 | 19.000000 | 111.800000 | 0 |
| duration_absolute_frames | 69 | 37.521739 | 19.000000 | 1.000000 | 271.000000 | 125.400000 | 167.800000 | 0 |
| duration_signed_seconds | 69 | -0.311594 | -0.400000 | -6.233333 | 9.033333 | 0.633333 | 3.726667 | 0 |

### Misses, extras, overlap topology and failure review

| Diagnostic | Observed | GT ideal / interpretation |
|---|---|---|
| Missed GT IDs | [5,7,16,24,32,33,41,42,46,50,52,55,71] | [] |
| Unmatched prediction IDs | [5,6,8,9,14,33,34,35,36,41,48,49,54,62,83] | [] |
| No-overlap missed GT IDs | [24,41,42] | [] |
| Predictions without any GT overlap | [] | [] |
| Possible split GT IDs | [5,7,12,32,33,37,46,61,81] | Geometric overlap candidates; not adjudicated semantic splits |
| Possible merge prediction IDs | [18,53,57,72] | Geometric overlap candidates; not adjudicated semantic merges |
| Significant failure records | 47 | Unmatched or \|boundary error\|>30frames or IoU<0.75 |
| early_start_gt_ids | [45,51,56,59,64] | Direction/weak-overlap inventory, not a physical cause |
| late_start_gt_ids | [1,2,3,4,6,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23,25,26,27,28,29,30,31,34,35,36,37,38,39,40,43,44,47,48,49,53,54,57,58,60,61,62,63,65,66,68,69,70,72,73,74,75,76,77,78,79,80,81,82] | Direction/weak-overlap inventory, not a physical cause |
| premature_end_gt_ids | [1,2,3,4,9,13,14,18,21,22,25,27,29,30,31,34,36,37,40,43,44,45,47,48,51,54,56,57,62,65,69,72,73,74,75,77,78,79,80,81,82] | Direction/weak-overlap inventory, not a physical cause |
| late_end_gt_ids | [6,8,10,11,15,17,20,26,28,35,38,49,53,58,59,60,61,63,67,68,70,76] | Direction/weak-overlap inventory, not a physical cause |
| weak_iou_gt_ids | [9,12,15,37,45,51,56,61,69,70,72,78,82] | Direction/weak-overlap inventory, not a physical cause |

| Inventory validity | Ground truth | Predictions |
|---|---|---|
| count | 82 | 84 |
| duplicate_row_pairs | [] | [] |
| positive_overlap_row_pairs | [] | [] |
| adjacent_row_pairs | [] | [] |
| out_of_range_rows | [] | [] |
| out_of_order_rows | [] | [] |

| False detection P ID | Start frame | End frame | Start seconds | End seconds | Duration seconds | Positive-overlap GT IDs |
|---|---|---|---|---|---|---|
| 5 | 1694 | 1923 | 56.466667 | 64.100000 | 7.633333 | [5] |
| 6 | 1962 | 2279 | 65.400000 | 75.966667 | 10.566667 | [5] |
| 8 | 2733 | 2887 | 91.100000 | 96.233333 | 5.133333 | [7] |
| 9 | 3004 | 3161 | 100.133333 | 105.366667 | 5.233333 | [7] |
| 14 | 4495 | 4618 | 149.833333 | 153.933333 | 4.100000 | [12] |
| 33 | 13026 | 13225 | 434.200000 | 440.833333 | 6.633333 | [32] |
| 34 | 13259 | 13468 | 441.966667 | 448.933333 | 6.966667 | [32] |
| 35 | 13715 | 13770 | 457.166667 | 459.000000 | 1.833333 | [33] |
| 36 | 13820 | 13910 | 460.666667 | 463.666667 | 3.000000 | [33] |
| 41 | 15827 | 15959 | 527.566667 | 531.966667 | 4.400000 | [37] |
| 48 | 18807 | 19094 | 626.900000 | 636.466667 | 9.566667 | [46] |
| 49 | 19155 | 19487 | 638.500000 | 649.566667 | 11.066667 | [46] |
| 54 | 20896 | 20968 | 696.533333 | 698.933333 | 2.400000 | [52] |
| 62 | 24508 | 24587 | 816.933333 | 819.566667 | 2.633333 | [61] |
| 83 | 32913 | 33023 | 1097.100000 | 1100.766667 | 3.666667 | [81] |

| Largest matched boundary cases | P ID | GT start/end frames | Pred start/end frames | Δstart frames | Δend frames | IoU |
|---|---|---|---|---|---|---|
| 51 | 53 | 20518–20862 | 20232–20847 | -286 | -15 | 0.522222 |
| 56 | 57 | 22208–22527 | 21979–22499 | -229 | -28 | 0.531022 |
| 70 | 72 | 27824–28295 | 27839–28479 | 15 | 184 | 0.696183 |
| 37 | 40 | 15466–15983 | 15474–15804 | 8 | -179 | 0.638298 |
| 81 | 82 | 32283–33045 | 32287–32883 | 4 | -162 | 0.782152 |

Of 13 unmatched reference intervals, 3 have no positive overlap with any prediction; 10 have some overlap but fail the one-to-one IoU eligibility/assignment. This separates absence of overlap from insufficient interval agreement without inventing a causal diagnosis.

### Every GT rally compared directly with its assigned prediction: frames

G IDs are one-based CSV row IDs in the primary rally reference. P IDs are one-based rows in the preserved prediction CSV. C IDs refer to the separate coarse table, linked only by the same IoU-based temporal crosswalk. “—” denotes unavailable/unmatched, not zero.

| G | P | GT start f | GT end f | Pred start f | Pred end f | Δstart f | \|Δstart\| f | Δend f | \|Δend\| f | IoU | Status | Coarse C row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 146 | 427 | 148 | 391 | 2 | 2 | -36 | 36 | 0.864769 | matched | 1 |
| 2 | 2 | 449 | 568 | 455 | 553 | 6 | 6 | -15 | 15 | 0.823529 | matched | 2 |
| 3 | 3 | 736 | 896 | 737 | 884 | 1 | 1 | -12 | 12 | 0.918750 | matched | 3 |
| 4 | 4 | 1017 | 1212 | 1021 | 1203 | 4 | 4 | -9 | 9 | 0.933333 | matched | 4 |
| 5 | — | 1658 | 2268 | — | — | — | — | — | — | — | missed | — |
| 6 | 7 | 2488 | 2618 | 2492 | 2627 | 4 | 4 | 9 | 9 | 0.906475 | matched | 7 |
| 7 | — | 2732 | 3181 | — | — | — | — | — | — | — | missed | — |
| 8 | 10 | 3209 | 3494 | 3210 | 3514 | 1 | 1 | 20 | 20 | 0.931148 | matched | 9 |
| 9 | 11 | 3551 | 3676 | 3585 | 3664 | 34 | 34 | -12 | 12 | 0.632000 | matched | — |
| 10 | 12 | 3753 | 3925 | 3757 | 3931 | 4 | 4 | 6 | 6 | 0.943820 | matched | 11 |
| 11 | 13 | 4004 | 4334 | 4009 | 4338 | 5 | 5 | 4 | 4 | 0.973054 | matched | 12 |
| 12 | 15 | 4490 | 4951 | 4650 | 4951 | 160 | 160 | 0 | 0 | 0.652928 | matched | 13 |
| 13 | 16 | 5131 | 5692 | 5141 | 5666 | 10 | 10 | -26 | 26 | 0.935829 | matched | 14 |
| 14 | 17 | 5759 | 6136 | 5763 | 6106 | 4 | 4 | -30 | 30 | 0.909814 | matched | 15 |
| 15 | 18 | 6277 | 6452 | 6285 | 6519 | 8 | 8 | 67 | 67 | 0.690083 | matched | 16 |
| 16 | — | 6480 | 6541 | — | — | — | — | — | — | — | missed | — |
| 17 | 19 | 6675 | 6952 | 6677 | 6967 | 2 | 2 | 15 | 15 | 0.941781 | matched | 17 |
| 18 | 20 | 7002 | 7308 | 7019 | 7307 | 17 | 17 | -1 | 1 | 0.941176 | matched | 18 |
| 19 | 21 | 7419 | 7828 | 7424 | 7828 | 5 | 5 | 0 | 0 | 0.987775 | matched | 19 |
| 20 | 22 | 7969 | 8073 | 7978 | 8087 | 9 | 9 | 14 | 14 | 0.805085 | matched | 20 |
| 21 | 23 | 8230 | 8363 | 8234 | 8350 | 4 | 4 | -13 | 13 | 0.872180 | matched | 21 |
| 22 | 24 | 8545 | 8774 | 8556 | 8758 | 11 | 11 | -16 | 16 | 0.882096 | matched | 22 |
| 23 | 25 | 8819 | 9219 | 8823 | 9219 | 4 | 4 | 0 | 0 | 0.990000 | matched | 23 |
| 24 | — | 9333 | 9380 | — | — | — | — | — | — | — | missed | 24 |
| 25 | 26 | 9752 | 9956 | 9759 | 9946 | 7 | 7 | -10 | 10 | 0.916667 | matched | 25 |
| 26 | 27 | 10154 | 10519 | 10160 | 10524 | 6 | 6 | 5 | 5 | 0.970270 | matched | 26 |
| 27 | 28 | 10665 | 10835 | 10675 | 10812 | 10 | 10 | -23 | 23 | 0.805882 | matched | 27 |
| 28 | 29 | 10900 | 11307 | 10903 | 11311 | 3 | 3 | 4 | 4 | 0.982968 | matched | 28 |
| 29 | 30 | 11391 | 11576 | 11399 | 11571 | 8 | 8 | -5 | 5 | 0.929730 | matched | 29 |
| 30 | 31 | 11611 | 12076 | 11652 | 12071 | 41 | 41 | -5 | 5 | 0.901075 | matched | 30 |
| 31 | 32 | 12124 | 12887 | 12206 | 12884 | 82 | 82 | -3 | 3 | 0.888598 | matched | 31 |
| 32 | — | 13023 | 13519 | — | — | — | — | — | — | — | missed | 32 |
| 33 | — | 13687 | 13968 | — | — | — | — | — | — | — | missed | 33 |
| 34 | 37 | 13990 | 14740 | 13991 | 14738 | 1 | 1 | -2 | 2 | 0.996000 | matched | 34 |
| 35 | 38 | 14824 | 15096 | 14828 | 15102 | 4 | 4 | 6 | 6 | 0.964029 | matched | 35 |
| 36 | 39 | 15178 | 15416 | 15189 | 15411 | 11 | 11 | -5 | 5 | 0.932773 | matched | 36 |
| 37 | 40 | 15466 | 15983 | 15474 | 15804 | 8 | 8 | -179 | 179 | 0.638298 | matched | 37 |
| 38 | 42 | 16055 | 16212 | 16063 | 16239 | 8 | 8 | 27 | 27 | 0.809783 | matched | 38 |
| 39 | 43 | 16329 | 16548 | 16359 | 16548 | 30 | 30 | 0 | 0 | 0.863014 | matched | 39 |
| 40 | 44 | 16567 | 16720 | 16587 | 16719 | 20 | 20 | -1 | 1 | 0.862745 | matched | — |
| 41 | — | 16871 | 16966 | — | — | — | — | — | — | — | missed | — |
| 42 | — | 17502 | 17701 | — | — | — | — | — | — | — | missed | — |
| 43 | 45 | 17815 | 18064 | 17819 | 18045 | 4 | 4 | -19 | 19 | 0.907631 | matched | — |
| 44 | 46 | 18100 | 18166 | 18101 | 18164 | 1 | 1 | -2 | 2 | 0.954545 | matched | 42 |
| 45 | 47 | 18528 | 18756 | 18377 | 18752 | -151 | 151 | -4 | 4 | 0.591029 | matched | — |
| 46 | — | 18785 | 19537 | — | — | — | — | — | — | — | missed | — |
| 47 | 50 | 19565 | 19695 | 19570 | 19671 | 5 | 5 | -24 | 24 | 0.776923 | matched | 46 |
| 48 | 51 | 19733 | 20008 | 19740 | 20003 | 7 | 7 | -5 | 5 | 0.956364 | matched | 47 |
| 49 | 52 | 20042 | 20159 | 20047 | 20167 | 5 | 5 | 8 | 8 | 0.896000 | matched | 48 |
| 50 | — | 20231 | 20471 | — | — | — | — | — | — | — | missed | — |
| 51 | 53 | 20518 | 20862 | 20232 | 20847 | -286 | 286 | -15 | 15 | 0.522222 | matched | 49 |
| 52 | — | 20882 | 21030 | — | — | — | — | — | — | — | missed | — |
| 53 | 55 | 21056 | 21181 | 21057 | 21184 | 1 | 1 | 3 | 3 | 0.968750 | matched | 51 |
| 54 | 56 | 21370 | 21853 | 21394 | 21847 | 24 | 24 | -6 | 6 | 0.937888 | matched | 52 |
| 55 | — | 21976 | 22179 | — | — | — | — | — | — | — | missed | — |
| 56 | 57 | 22208 | 22527 | 21979 | 22499 | -229 | 229 | -28 | 28 | 0.531022 | matched | 53 |
| 57 | 58 | 22624 | 23036 | 22631 | 23011 | 7 | 7 | -25 | 25 | 0.922330 | matched | 54 |
| 58 | 59 | 23195 | 23567 | 23199 | 23583 | 4 | 4 | 16 | 16 | 0.948454 | matched | 55 |
| 59 | 60 | 23739 | 23998 | 23729 | 24007 | -10 | 10 | 9 | 9 | 0.931655 | matched | 56 |
| 60 | 61 | 24094 | 24313 | 24101 | 24325 | 7 | 7 | 12 | 12 | 0.917749 | matched | 57 |
| 61 | 63 | 24500 | 24869 | 24622 | 24871 | 122 | 122 | 2 | 2 | 0.665768 | matched | 58 |
| 62 | 64 | 24965 | 25079 | 24970 | 25073 | 5 | 5 | -6 | 6 | 0.903509 | matched | 59 |
| 63 | 65 | 25265 | 25532 | 25274 | 25540 | 9 | 9 | 8 | 8 | 0.938182 | matched | 60 |
| 64 | 66 | 25576 | 25773 | 25569 | 25773 | -7 | 7 | 0 | 0 | 0.965686 | matched | 61 |
| 65 | 67 | 25895 | 26081 | 25896 | 26047 | 1 | 1 | -34 | 34 | 0.811828 | matched | 62 |
| 66 | 68 | 26560 | 26686 | 26561 | 26686 | 1 | 1 | 0 | 0 | 0.992063 | matched | 63 |
| 67 | 69 | 26733 | 27080 | 26733 | 27085 | 0 | 0 | 5 | 5 | 0.985795 | matched | 64 |
| 68 | 70 | 27184 | 27405 | 27218 | 27407 | 34 | 34 | 2 | 2 | 0.838565 | matched | 65 |
| 69 | 71 | 27563 | 27664 | 27590 | 27653 | 27 | 27 | -11 | 11 | 0.623762 | matched | 66 |
| 70 | 72 | 27824 | 28295 | 27839 | 28479 | 15 | 15 | 184 | 184 | 0.696183 | matched | 67 |
| 71 | — | 28324 | 28481 | — | — | — | — | — | — | — | missed | 68 |
| 72 | 73 | 28508 | 28610 | 28542 | 28609 | 34 | 34 | -1 | 1 | 0.656863 | matched | — |
| 73 | 74 | 28843 | 29156 | 28846 | 29135 | 3 | 3 | -21 | 21 | 0.923323 | matched | 69 |
| 74 | 75 | 29328 | 29540 | 29332 | 29510 | 4 | 4 | -30 | 30 | 0.839623 | matched | 70 |
| 75 | 76 | 29635 | 30131 | 29641 | 30127 | 6 | 6 | -4 | 4 | 0.979839 | matched | 71 |
| 76 | 77 | 30267 | 30356 | 30270 | 30365 | 3 | 3 | 9 | 9 | 0.877551 | matched | 72 |
| 77 | 78 | 30456 | 30893 | 30461 | 30887 | 5 | 5 | -6 | 6 | 0.974828 | matched | 73 |
| 78 | 79 | 31236 | 31386 | 31242 | 31350 | 6 | 6 | -36 | 36 | 0.720000 | matched | 74 |
| 79 | 80 | 31475 | 31818 | 31476 | 31817 | 1 | 1 | -1 | 1 | 0.994169 | matched | 75 |
| 80 | 81 | 31916 | 32138 | 31919 | 32134 | 3 | 3 | -4 | 4 | 0.968468 | matched | 76 |
| 81 | 82 | 32283 | 33045 | 32287 | 32883 | 4 | 4 | -162 | 162 | 0.782152 | matched | 77 |
| 82 | 84 | 33063 | 33156 | 33076 | 33135 | 13 | 13 | -21 | 21 | 0.634409 | matched | 78 |

### Every GT rally compared directly: timestamps and durations

| G | GT start s | GT end s | Pred start s | Pred end s | GT duration s | Pred duration s | Δstart s | \|Δstart\| s | Δend s | \|Δend\| s | Δduration s | \|Δduration\| s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4.866667 | 14.233333 | 4.933333 | 13.033333 | 9.366667 | 8.100000 | 0.066667 | 0.066667 | -1.200000 | 1.200000 | -1.266667 | 1.266667 |
| 2 | 14.966667 | 18.933333 | 15.166667 | 18.433333 | 3.966667 | 3.266667 | 0.200000 | 0.200000 | -0.500000 | 0.500000 | -0.700000 | 0.700000 |
| 3 | 24.533333 | 29.866667 | 24.566667 | 29.466667 | 5.333333 | 4.900000 | 0.033333 | 0.033333 | -0.400000 | 0.400000 | -0.433333 | 0.433333 |
| 4 | 33.900000 | 40.400000 | 34.033333 | 40.100000 | 6.500000 | 6.066667 | 0.133333 | 0.133333 | -0.300000 | 0.300000 | -0.433333 | 0.433333 |
| 5 | 55.266667 | 75.600000 | — | — | 20.333333 | — | — | — | — | — | — | — |
| 6 | 82.933333 | 87.266667 | 83.066667 | 87.566667 | 4.333333 | 4.500000 | 0.133333 | 0.133333 | 0.300000 | 0.300000 | 0.166667 | 0.166667 |
| 7 | 91.066667 | 106.033333 | — | — | 14.966667 | — | — | — | — | — | — | — |
| 8 | 106.966667 | 116.466667 | 107.000000 | 117.133333 | 9.500000 | 10.133333 | 0.033333 | 0.033333 | 0.666667 | 0.666667 | 0.633333 | 0.633333 |
| 9 | 118.366667 | 122.533333 | 119.500000 | 122.133333 | 4.166667 | 2.633333 | 1.133333 | 1.133333 | -0.400000 | 0.400000 | -1.533333 | 1.533333 |
| 10 | 125.100000 | 130.833333 | 125.233333 | 131.033333 | 5.733333 | 5.800000 | 0.133333 | 0.133333 | 0.200000 | 0.200000 | 0.066667 | 0.066667 |
| 11 | 133.466667 | 144.466667 | 133.633333 | 144.600000 | 11.000000 | 10.966667 | 0.166667 | 0.166667 | 0.133333 | 0.133333 | -0.033333 | 0.033333 |
| 12 | 149.666667 | 165.033333 | 155.000000 | 165.033333 | 15.366667 | 10.033333 | 5.333333 | 5.333333 | 0.000000 | 0.000000 | -5.333333 | 5.333333 |
| 13 | 171.033333 | 189.733333 | 171.366667 | 188.866667 | 18.700000 | 17.500000 | 0.333333 | 0.333333 | -0.866667 | 0.866667 | -1.200000 | 1.200000 |
| 14 | 191.966667 | 204.533333 | 192.100000 | 203.533333 | 12.566667 | 11.433333 | 0.133333 | 0.133333 | -1.000000 | 1.000000 | -1.133333 | 1.133333 |
| 15 | 209.233333 | 215.066667 | 209.500000 | 217.300000 | 5.833333 | 7.800000 | 0.266667 | 0.266667 | 2.233333 | 2.233333 | 1.966667 | 1.966667 |
| 16 | 216.000000 | 218.033333 | — | — | 2.033333 | — | — | — | — | — | — | — |
| 17 | 222.500000 | 231.733333 | 222.566667 | 232.233333 | 9.233333 | 9.666667 | 0.066667 | 0.066667 | 0.500000 | 0.500000 | 0.433333 | 0.433333 |
| 18 | 233.400000 | 243.600000 | 233.966667 | 243.566667 | 10.200000 | 9.600000 | 0.566667 | 0.566667 | -0.033333 | 0.033333 | -0.600000 | 0.600000 |
| 19 | 247.300000 | 260.933333 | 247.466667 | 260.933333 | 13.633333 | 13.466667 | 0.166667 | 0.166667 | 0.000000 | 0.000000 | -0.166667 | 0.166667 |
| 20 | 265.633333 | 269.100000 | 265.933333 | 269.566667 | 3.466667 | 3.633333 | 0.300000 | 0.300000 | 0.466667 | 0.466667 | 0.166667 | 0.166667 |
| 21 | 274.333333 | 278.766667 | 274.466667 | 278.333333 | 4.433333 | 3.866667 | 0.133333 | 0.133333 | -0.433333 | 0.433333 | -0.566667 | 0.566667 |
| 22 | 284.833333 | 292.466667 | 285.200000 | 291.933333 | 7.633333 | 6.733333 | 0.366667 | 0.366667 | -0.533333 | 0.533333 | -0.900000 | 0.900000 |
| 23 | 293.966667 | 307.300000 | 294.100000 | 307.300000 | 13.333333 | 13.200000 | 0.133333 | 0.133333 | 0.000000 | 0.000000 | -0.133333 | 0.133333 |
| 24 | 311.100000 | 312.666667 | — | — | 1.566667 | — | — | — | — | — | — | — |
| 25 | 325.066667 | 331.866667 | 325.300000 | 331.533333 | 6.800000 | 6.233333 | 0.233333 | 0.233333 | -0.333333 | 0.333333 | -0.566667 | 0.566667 |
| 26 | 338.466667 | 350.633333 | 338.666667 | 350.800000 | 12.166667 | 12.133333 | 0.200000 | 0.200000 | 0.166667 | 0.166667 | -0.033333 | 0.033333 |
| 27 | 355.500000 | 361.166667 | 355.833333 | 360.400000 | 5.666667 | 4.566667 | 0.333333 | 0.333333 | -0.766667 | 0.766667 | -1.100000 | 1.100000 |
| 28 | 363.333333 | 376.900000 | 363.433333 | 377.033333 | 13.566667 | 13.600000 | 0.100000 | 0.100000 | 0.133333 | 0.133333 | 0.033333 | 0.033333 |
| 29 | 379.700000 | 385.866667 | 379.966667 | 385.700000 | 6.166667 | 5.733333 | 0.266667 | 0.266667 | -0.166667 | 0.166667 | -0.433333 | 0.433333 |
| 30 | 387.033333 | 402.533333 | 388.400000 | 402.366667 | 15.500000 | 13.966667 | 1.366667 | 1.366667 | -0.166667 | 0.166667 | -1.533333 | 1.533333 |
| 31 | 404.133333 | 429.566667 | 406.866667 | 429.466667 | 25.433333 | 22.600000 | 2.733333 | 2.733333 | -0.100000 | 0.100000 | -2.833333 | 2.833333 |
| 32 | 434.100000 | 450.633333 | — | — | 16.533333 | — | — | — | — | — | — | — |
| 33 | 456.233333 | 465.600000 | — | — | 9.366667 | — | — | — | — | — | — | — |
| 34 | 466.333333 | 491.333333 | 466.366667 | 491.266667 | 25.000000 | 24.900000 | 0.033333 | 0.033333 | -0.066667 | 0.066667 | -0.100000 | 0.100000 |
| 35 | 494.133333 | 503.200000 | 494.266667 | 503.400000 | 9.066667 | 9.133333 | 0.133333 | 0.133333 | 0.200000 | 0.200000 | 0.066667 | 0.066667 |
| 36 | 505.933333 | 513.866667 | 506.300000 | 513.700000 | 7.933333 | 7.400000 | 0.366667 | 0.366667 | -0.166667 | 0.166667 | -0.533333 | 0.533333 |
| 37 | 515.533333 | 532.766667 | 515.800000 | 526.800000 | 17.233333 | 11.000000 | 0.266667 | 0.266667 | -5.966667 | 5.966667 | -6.233333 | 6.233333 |
| 38 | 535.166667 | 540.400000 | 535.433333 | 541.300000 | 5.233333 | 5.866667 | 0.266667 | 0.266667 | 0.900000 | 0.900000 | 0.633333 | 0.633333 |
| 39 | 544.300000 | 551.600000 | 545.300000 | 551.600000 | 7.300000 | 6.300000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | -1.000000 | 1.000000 |
| 40 | 552.233333 | 557.333333 | 552.900000 | 557.300000 | 5.100000 | 4.400000 | 0.666667 | 0.666667 | -0.033333 | 0.033333 | -0.700000 | 0.700000 |
| 41 | 562.366667 | 565.533333 | — | — | 3.166667 | — | — | — | — | — | — | — |
| 42 | 583.400000 | 590.033333 | — | — | 6.633333 | — | — | — | — | — | — | — |
| 43 | 593.833333 | 602.133333 | 593.966667 | 601.500000 | 8.300000 | 7.533333 | 0.133333 | 0.133333 | -0.633333 | 0.633333 | -0.766667 | 0.766667 |
| 44 | 603.333333 | 605.533333 | 603.366667 | 605.466667 | 2.200000 | 2.100000 | 0.033333 | 0.033333 | -0.066667 | 0.066667 | -0.100000 | 0.100000 |
| 45 | 617.600000 | 625.200000 | 612.566667 | 625.066667 | 7.600000 | 12.500000 | -5.033333 | 5.033333 | -0.133333 | 0.133333 | 4.900000 | 4.900000 |
| 46 | 626.166667 | 651.233333 | — | — | 25.066667 | — | — | — | — | — | — | — |
| 47 | 652.166667 | 656.500000 | 652.333333 | 655.700000 | 4.333333 | 3.366667 | 0.166667 | 0.166667 | -0.800000 | 0.800000 | -0.966667 | 0.966667 |
| 48 | 657.766667 | 666.933333 | 658.000000 | 666.766667 | 9.166667 | 8.766667 | 0.233333 | 0.233333 | -0.166667 | 0.166667 | -0.400000 | 0.400000 |
| 49 | 668.066667 | 671.966667 | 668.233333 | 672.233333 | 3.900000 | 4.000000 | 0.166667 | 0.166667 | 0.266667 | 0.266667 | 0.100000 | 0.100000 |
| 50 | 674.366667 | 682.366667 | — | — | 8.000000 | — | — | — | — | — | — | — |
| 51 | 683.933333 | 695.400000 | 674.400000 | 694.900000 | 11.466667 | 20.500000 | -9.533333 | 9.533333 | -0.500000 | 0.500000 | 9.033333 | 9.033333 |
| 52 | 696.066667 | 701.000000 | — | — | 4.933333 | — | — | — | — | — | — | — |
| 53 | 701.866667 | 706.033333 | 701.900000 | 706.133333 | 4.166667 | 4.233333 | 0.033333 | 0.033333 | 0.100000 | 0.100000 | 0.066667 | 0.066667 |
| 54 | 712.333333 | 728.433333 | 713.133333 | 728.233333 | 16.100000 | 15.100000 | 0.800000 | 0.800000 | -0.200000 | 0.200000 | -1.000000 | 1.000000 |
| 55 | 732.533333 | 739.300000 | — | — | 6.766667 | — | — | — | — | — | — | — |
| 56 | 740.266667 | 750.900000 | 732.633333 | 749.966667 | 10.633333 | 17.333333 | -7.633333 | 7.633333 | -0.933333 | 0.933333 | 6.700000 | 6.700000 |
| 57 | 754.133333 | 767.866667 | 754.366667 | 767.033333 | 13.733333 | 12.666667 | 0.233333 | 0.233333 | -0.833333 | 0.833333 | -1.066667 | 1.066667 |
| 58 | 773.166667 | 785.566667 | 773.300000 | 786.100000 | 12.400000 | 12.800000 | 0.133333 | 0.133333 | 0.533333 | 0.533333 | 0.400000 | 0.400000 |
| 59 | 791.300000 | 799.933333 | 790.966667 | 800.233333 | 8.633333 | 9.266667 | -0.333333 | 0.333333 | 0.300000 | 0.300000 | 0.633333 | 0.633333 |
| 60 | 803.133333 | 810.433333 | 803.366667 | 810.833333 | 7.300000 | 7.466667 | 0.233333 | 0.233333 | 0.400000 | 0.400000 | 0.166667 | 0.166667 |
| 61 | 816.666667 | 828.966667 | 820.733333 | 829.033333 | 12.300000 | 8.300000 | 4.066667 | 4.066667 | 0.066667 | 0.066667 | -4.000000 | 4.000000 |
| 62 | 832.166667 | 835.966667 | 832.333333 | 835.766667 | 3.800000 | 3.433333 | 0.166667 | 0.166667 | -0.200000 | 0.200000 | -0.366667 | 0.366667 |
| 63 | 842.166667 | 851.066667 | 842.466667 | 851.333333 | 8.900000 | 8.866667 | 0.300000 | 0.300000 | 0.266667 | 0.266667 | -0.033333 | 0.033333 |
| 64 | 852.533333 | 859.100000 | 852.300000 | 859.100000 | 6.566667 | 6.800000 | -0.233333 | 0.233333 | 0.000000 | 0.000000 | 0.233333 | 0.233333 |
| 65 | 863.166667 | 869.366667 | 863.200000 | 868.233333 | 6.200000 | 5.033333 | 0.033333 | 0.033333 | -1.133333 | 1.133333 | -1.166667 | 1.166667 |
| 66 | 885.333333 | 889.533333 | 885.366667 | 889.533333 | 4.200000 | 4.166667 | 0.033333 | 0.033333 | 0.000000 | 0.000000 | -0.033333 | 0.033333 |
| 67 | 891.100000 | 902.666667 | 891.100000 | 902.833333 | 11.566667 | 11.733333 | 0.000000 | 0.000000 | 0.166667 | 0.166667 | 0.166667 | 0.166667 |
| 68 | 906.133333 | 913.500000 | 907.266667 | 913.566667 | 7.366667 | 6.300000 | 1.133333 | 1.133333 | 0.066667 | 0.066667 | -1.066667 | 1.066667 |
| 69 | 918.766667 | 922.133333 | 919.666667 | 921.766667 | 3.366667 | 2.100000 | 0.900000 | 0.900000 | -0.366667 | 0.366667 | -1.266667 | 1.266667 |
| 70 | 927.466667 | 943.166667 | 927.966667 | 949.300000 | 15.700000 | 21.333333 | 0.500000 | 0.500000 | 6.133333 | 6.133333 | 5.633333 | 5.633333 |
| 71 | 944.133333 | 949.366667 | — | — | 5.233333 | — | — | — | — | — | — | — |
| 72 | 950.266667 | 953.666667 | 951.400000 | 953.633333 | 3.400000 | 2.233333 | 1.133333 | 1.133333 | -0.033333 | 0.033333 | -1.166667 | 1.166667 |
| 73 | 961.433333 | 971.866667 | 961.533333 | 971.166667 | 10.433333 | 9.633333 | 0.100000 | 0.100000 | -0.700000 | 0.700000 | -0.800000 | 0.800000 |
| 74 | 977.600000 | 984.666667 | 977.733333 | 983.666667 | 7.066667 | 5.933333 | 0.133333 | 0.133333 | -1.000000 | 1.000000 | -1.133333 | 1.133333 |
| 75 | 987.833333 | 1004.366667 | 988.033333 | 1004.233333 | 16.533333 | 16.200000 | 0.200000 | 0.200000 | -0.133333 | 0.133333 | -0.333333 | 0.333333 |
| 76 | 1008.900000 | 1011.866667 | 1009.000000 | 1012.166667 | 2.966667 | 3.166667 | 0.100000 | 0.100000 | 0.300000 | 0.300000 | 0.200000 | 0.200000 |
| 77 | 1015.200000 | 1029.766667 | 1015.366667 | 1029.566667 | 14.566667 | 14.200000 | 0.166667 | 0.166667 | -0.200000 | 0.200000 | -0.366667 | 0.366667 |
| 78 | 1041.200000 | 1046.200000 | 1041.400000 | 1045.000000 | 5.000000 | 3.600000 | 0.200000 | 0.200000 | -1.200000 | 1.200000 | -1.400000 | 1.400000 |
| 79 | 1049.166667 | 1060.600000 | 1049.200000 | 1060.566667 | 11.433333 | 11.366667 | 0.033333 | 0.033333 | -0.033333 | 0.033333 | -0.066667 | 0.066667 |
| 80 | 1063.866667 | 1071.266667 | 1063.966667 | 1071.133333 | 7.400000 | 7.166667 | 0.100000 | 0.100000 | -0.133333 | 0.133333 | -0.233333 | 0.233333 |
| 81 | 1076.100000 | 1101.500000 | 1076.233333 | 1096.100000 | 25.400000 | 19.866667 | 0.133333 | 0.133333 | -5.400000 | 5.400000 | -5.533333 | 5.533333 |
| 82 | 1102.100000 | 1105.200000 | 1102.533333 | 1104.500000 | 3.100000 | 1.966667 | 0.433333 | 0.433333 | -0.700000 | 0.700000 | -1.133333 | 1.133333 |

### Secondary coarse/outcome annotations: full supplied baseline and comparison

[Test9_Full.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test9_Full/Test9_Full.csv) contains **88 data rows**, **78 nonblank intervals**, blank row IDs **[79, 80, 81, 82, 83, 84, 85, 86, 87, 88]**. This separate reference differs from the 82-interval primary timing table. The same unchanged predictions and matcher give secondary precision **84.524%**, recall **91.026%**, F1 **87.654%**; this reference-sensitivity analysis does not replace the primary benchmark. No labels, times or predictions were fitted or repaired.

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 78 | 78 | 0 |
| Prediction count | 78 | 84 | 6 |
| TP / matched | 78 | 71 | -7 |
| FP | 0 | 13 | 13 |
| FN / missed | 0 | 7 | 7 |
| precision | 1 | 0.845238 | -0.154762 |
| recall | 1 | 0.910256 | -0.089744 |
| f1 | 1 | 0.876543 | -0.123457 |
| Mean matched IoU | 1 | 0.816791 | -0.183209 |
| Median matched IoU | 1 | 0.861314 | -0.138686 |
| Minimum matched IoU | 1 | 0.500000 | -0.500000 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 76.056338 |
| 0.9 | 100 | 28.169014 |
| 0.95 | 100 | 9.859155 |

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 26.859155 | 15.000000 | 47.734447 | 210.000000 | 41.000000 | 24.126761 | 14.000000 |
| end_frame | 24.323944 | 16.000000 | 42.898669 | 189.000000 | 42.000000 | 3.309859 | 7.000000 |
| start_time_sec | 0.895305 | 0.500000 | 1.591148 | 7.000000 | 1.366667 | 0.804225 | 0.466667 |
| end_time_sec | 0.810798 | 0.533333 | 1.429956 | 6.300000 | 1.400000 | 0.110329 | 0.233333 |
| duration_sec | 1.258216 | 0.700000 | 2.071802 | 6.866667 | 4.133333 | -0.693897 | -0.333333 |

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 1 | 71 | 1.408% | 78 | 1.282% | 100% |
| start | 3 | 0.100000 | 5 | 71 | 7.042% | 78 | 6.410% | 100% |
| start | 5 | 0.166667 | 6 | 71 | 8.451% | 78 | 7.692% | 100% |
| start | 10 | 0.333333 | 21 | 71 | 29.577% | 78 | 26.923% | 100% |
| start | 15 | 0.500000 | 37 | 71 | 52.113% | 78 | 47.436% | 100% |
| start | 30 | 1.000000 | 58 | 71 | 81.690% | 78 | 74.359% | 100% |
| end | 1 | 0.033333 | 8 | 71 | 11.268% | 78 | 10.256% | 100% |
| end | 3 | 0.100000 | 11 | 71 | 15.493% | 78 | 14.103% | 100% |
| end | 5 | 0.166667 | 18 | 71 | 25.352% | 78 | 23.077% | 100% |
| end | 10 | 0.333333 | 28 | 71 | 39.437% | 78 | 35.897% | 100% |
| end | 15 | 0.500000 | 35 | 71 | 49.296% | 78 | 44.872% | 100% |
| end | 30 | 1.000000 | 57 | 71 | 80.282% | 78 | 73.077% | 100% |

| Cross-reference timing diagnostic | Value |
|---|---|
| Primary-to-coarse eligible matched intervals | 68 |
| Primary intervals unmatched to coarse reference | [5,7,9,16,40,41,42,43,45,46,50,52,55,72] |
| Coarse rows unmatched to primary reference | [5,6,8,10,40,41,43,44,45,50] |
| Primary/coarse matched mean IoU | 0.823430 |

| C source row | Supplied start | Supplied end | Supplied winner | Supplied A:B score | Supplied shot / ball_types | Win reason | Lose reason | Matched P | IoU | Δstart s | Δend s | Δduration s | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:04 | 0:13 | Player B | 0:1 | Clear Shot | Winner Shot | Opponent Failed to Return | 1 | 0.892989 | 0.933333 | 0.033333 | -0.900000 | matched |
| 2 | 0:15 | 0:18 | Player A | 1:1 | Drop Shot | Opponent Out of Bounds | Hit Out of Bounds | 2 | 0.825243 | 0.166667 | 0.433333 | 0.266667 | matched |
| 3 | 0:24 | 0:29 | Player A | 2:1 | Smash | Opponent Hit the Net | Hit the Net | 3 | 0.810976 | 0.566667 | 0.466667 | -0.100000 | matched |
| 4 | 0:33 | 0:40 | Player B | 2:2 | Push Shot | Opponent Hit the Net | Hit the Net | 4 | 0.840376 | 1.033333 | 0.100000 | -0.933333 | matched |
| 5 | 0:50 | 1:04 | Player A | 3:2 | Net Shot | Opponent Hit the Net | Hit the Net | 5 | 0.534279 | 6.466667 | 0.100000 | -6.366667 | matched |
| 6 | 1:05 | 1:15 | Player B | 3:3 | Lift Shot | Winner Shot | Opponent Failed to Return | 6 | 0.875380 | 0.400000 | 0.966667 | 0.566667 | matched |
| 7 | 1:23 | 1:27 | Player A | 4:3 | Block Shot | Opponent Hit the Net | Hit the Net | 7 | 0.861314 | 0.066667 | 0.566667 | 0.500000 | matched |
| 8 | 1:31 | 1:36 | Player B | 4:4 | Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 8 | 0.936306 | 0.100000 | 0.233333 | 0.133333 | matched |
| 9 | 1:40 | 1:57 | Player A | 5:4 | Slice Shot | Opponent Out of Bounds | Hit Out of Bounds | 10 | 0.583658 | 7.000000 | 0.133333 | -6.866667 | matched |
| 10 | 1:59 | 2:01 | Player A | 6:4 | Smash | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 11 | 2:05 | 2:11 | Player A | 7:4 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 12 | 0.955801 | 0.233333 | 0.033333 | -0.200000 | matched |
| 12 | 2:13 | 2:24 | Player B | 7:5 | Drop Shot | Opponent Hit the Net | Hit the Net | 13 | 0.893678 | 0.633333 | 0.600000 | -0.033333 | matched |
| 13 | 2:29 | 2:45 | Player B | 7:6 | Lift Shot | Winner Shot | Opponent Failed to Return | 15 | 0.623701 | 6.000000 | 0.033333 | -5.966667 | matched |
| 14 | 2:51 | 3:09 | Player B | 7:7 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 16 | 0.972222 | 0.366667 | -0.133333 | -0.500000 | matched |
| 15 | 3:12 | 3:23 | Player B | 7:8 | Net Shot | Opponent Hit the Net | Hit the Net | 17 | 0.945087 | 0.100000 | 0.533333 | 0.433333 | matched |
| 16 | 3:29 | 3:38 | Player A | 8:8 | Smash | Opponent Out of Bounds | Hit Out of Bounds | 18 | 0.866667 | 0.500000 | -0.700000 | -1.200000 | matched |
| 17 | 3:42 | 3:52 | Player A | 9:8 | Slice Shot | Winner Shot | Opponent Failed to Return | 19 | 0.921824 | 0.566667 | 0.233333 | -0.333333 | matched |
| 18 | 3:53 | 4:04 | Player A | 10:8 | Drop Shot | Winner Shot | Opponent Failed to Return | 20 | 0.872727 | 0.966667 | -0.433333 | -1.400000 | matched |
| 19 | 4:07 | 4:20 | Player A | 11:8 | Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 21 | 0.899522 | 0.466667 | 0.933333 | 0.466667 | matched |
| 20 | 4:25 | 4:29 | Player A | 12:8 | Push Shot | Winner Shot | Opponent Failed to Return | 22 | 0.671533 | 0.933333 | 0.566667 | -0.366667 | matched |
| 21 | 4:34 | 4:38 | Player B | 12:9 | Lift Shot | Winner Shot | Opponent Failed to Return | 23 | 0.815385 | 0.466667 | 0.333333 | -0.133333 | matched |
| 22 | 4:45 | 4:51 | Player A | 13:9 | Hook Shot | Opponent Out of Bounds | Hit Out of Bounds | 24 | 0.836538 | 0.200000 | 0.933333 | 0.733333 | matched |
| 23 | 4:53 | 5:07 | Player B | 13:10 | Defensive Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 25 | 0.902098 | 1.100000 | 0.300000 | -0.800000 | matched |
| 24 | 5:10 | 5:13 | Player A | 14:10 | Slice Shot | Opponent Out of Bounds | Hit Out of Bounds | — | — | — | — | — | missed |
| 25 | 5:25 | 5:31 | Player A | 15:10 | Net Shot | Opponent Hit the Net | Hit the Net | 26 | 0.872449 | 0.300000 | 0.533333 | 0.233333 | matched |
| 26 | 5:38 | 5:51 | Player A | 16:10 | Drop Shot | Opponent Hit the Net | Hit the Net | 27 | 0.933333 | 0.666667 | -0.200000 | -0.866667 | matched |
| 27 | 5:55 | 6:01 | Player A | 17:10 | Smash | Winner Shot | Opponent Failed to Return | 28 | 0.761111 | 0.833333 | -0.600000 | -1.433333 | matched |
| 28 | 6:02 | 6:17 | Player A | 18:10 | Net Shot | Opponent Hit the Net | Hit the Net | 29 | 0.902439 | 1.433333 | 0.033333 | -1.400000 | matched |
| 29 | 6:19 | 6:25 | Player A | 19:10 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 30 | 0.751244 | 0.966667 | 0.700000 | -0.266667 | matched |
| 30 | 6:28 | 6:42 | Player B | 19:11 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 31 | 0.946636 | 0.400000 | 0.366667 | -0.033333 | matched |
| 31 | 6:46 | 7:10 | Player B | 19:12 | Clear Shot | Winner Shot | Opponent Failed to Return | 32 | 0.941667 | 0.866667 | -0.533333 | -1.400000 | matched |
| 32 | 7:14 | 7:29 | Player A | 20:12 | Smash | Opponent Hit the Net | Hit the Net | — | — | — | — | — | missed |
| 33 | 7:37 | 7:45 | Player B | 20:13 | Drive Shot | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 34 | 7:46 | 8:11 | Player B | 20:14 | Net Shot | Opponent Hit the Net | Hit the Net | 37 | 0.974934 | 0.366667 | 0.266667 | -0.100000 | matched |
| 35 | 8:14 | 8:22 | Player A | 21:14 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 38 | 0.822695 | 0.266667 | 1.400000 | 1.133333 | matched |
| 36 | 8:25 | 8:34 | Player A | 22:14 | Drop Shot | Opponent Hit the Net | Hit the Net | 39 | 0.822222 | 1.300000 | -0.300000 | -1.600000 | matched |
| 37 | 8:36 | 8:52 | Player A | 23:14 | Smash | Opponent Hit the Net | Hit the Net | 40 | 0.666667 | -0.200000 | -5.200000 | -5.000000 | matched |
| 38 | 8:55 | 9:01 | Player A | 24:14 | Slice Shot | Opponent Out of Bounds | Hit Out of Bounds | 42 | 0.883598 | 0.433333 | 0.300000 | -0.133333 | matched |
| 39 | 9:05 | 9:17 | Player B | 24:15 | Lift Shot | Winner Shot | Opponent Failed to Return | 43 | 0.525000 | 0.300000 | -5.400000 | -5.700000 | matched |
| 40 | 9:48 | 9:50 | Player A | 25:15 | Push Shot | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 41 | 9:59 | 10:01 | Player A | 26:15 | Net Shot | Opponent Hit the Net | Hit the Net | — | — | — | — | — | missed |
| 42 | 10:03 | 10:05 | Player B | 26:16 | Drive Shot | Winner Shot | Opponent Failed to Return | 46 | 0.662162 | 0.366667 | 0.466667 | 0.100000 | matched |
| 43 | 10:12 | 10:24 | Player A | 27:16 | Smash | Winner Shot | Opponent Failed to Return | 47 | 0.875000 | 0.566667 | 1.066667 | 0.500000 | matched |
| 44 | 10:26 | 10:37 | Player B | 27:17 | Clear Shot | Winner Shot | Opponent Failed to Return | 48 | 0.869697 | 0.900000 | -0.533333 | -1.433333 | matched |
| 45 | 10:38 | 10:48 | Player A | 28:17 | Drop Shot | Opponent Hit the Net | Hit the Net | 49 | 0.821326 | 0.500000 | 1.566667 | 1.066667 | matched |
| 46 | 10:52 | 10:57 | Player B | 28:18 | Slice Shot | Winner Shot | Opponent Failed to Return | 50 | 0.673333 | 0.333333 | -1.300000 | -1.633333 | matched |
| 47 | 10:57 | 11:06 | Player B | 28:19 | Push Shot | Winner Shot | Opponent Failed to Return | 51 | 0.819113 | 1.000000 | 0.766667 | -0.233333 | matched |
| 48 | 11:08 | 11:11 | Player B | 28:20 | Lift Shot | Winner Shot | Opponent Failed to Return | 52 | 0.653543 | 0.233333 | 1.233333 | 1.000000 | matched |
| 49 | 11:14 | 11:35 | Player B | 28:21 | Defensive Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 53 | 0.976190 | 0.400000 | -0.100000 | -0.500000 | matched |
| 50 | 11:36 | 11:38 | Player B | 28:22 | Net Shot | Opponent Hit the Net | Hit the Net | 54 | 0.500000 | 0.533333 | 0.933333 | 0.400000 | matched |
| 51 | 11:41 | 11:46 | Player A | 29:22 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 55 | 0.798701 | 0.900000 | 0.133333 | -0.766667 | matched |
| 52 | 11:52 | 12:09 | Player B | 29:23 | Smash | Winner Shot | Opponent Failed to Return | 56 | 0.888235 | 1.133333 | -0.766667 | -1.900000 | matched |
| 53 | 12:12 | 12:30 | Player B | 29:24 | Net Shot | Opponent Hit the Net | Hit the Net | 57 | 0.962963 | 0.633333 | -0.033333 | -0.666667 | matched |
| 54 | 12:34 | 12:47 | Player B | 29:25 | Drive Shot | Winner Shot | Opponent Failed to Return | 58 | 0.969309 | 0.366667 | 0.033333 | -0.333333 | matched |
| 55 | 12:53 | 13:05 | Player B | 29:26 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 59 | 0.893130 | 0.300000 | 1.100000 | 0.800000 | matched |
| 56 | 13:14 | 13:19 | Player A | 30:26 | Slice Shot | Opponent Out of Bounds | Hit Out of Bounds | 60 | 0.539568 | -3.033333 | 1.233333 | 4.266667 | matched |
| 57 | 13:22 | 13:30 | Player A | 31:26 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 61 | 0.750943 | 1.366667 | 0.833333 | -0.533333 | matched |
| 58 | 13:37 | 13:49 | Player A | 32:26 | Drop Shot | Opponent Hit the Net | Hit the Net | 63 | 0.686981 | 3.733333 | 0.033333 | -3.700000 | matched |
| 59 | 13:52 | 13:58 | Player B | 32:27 | Net Shot | Opponent Hit the Net | Hit the Net | 64 | 0.572222 | 0.333333 | -2.233333 | -2.566667 | matched |
| 60 | 14:02 | 14:11 | Player A | 33:27 | Smash | Winner Shot | Opponent Failed to Return | 65 | 0.914286 | 0.466667 | 0.333333 | -0.133333 | matched |
| 61 | 14:12 | 14:20 | Player B | 33:28 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 66 | 0.850000 | 0.300000 | -0.900000 | -1.200000 | matched |
| 62 | 14:23 | 14:29 | Player A | 34:28 | Drive Shot | Opponent Hit the Net | Hit the Net | 67 | 0.838889 | 0.200000 | -0.766667 | -0.966667 | matched |
| 63 | 14:45 | 14:48 | Player A | 35:28 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 68 | 0.580882 | 0.366667 | 1.533333 | 1.166667 | matched |
| 64 | 14:51 | 15:03 | Player A | 36:28 | Net Shot | Opponent Hit the Net | Hit the Net | 69 | 0.977778 | 0.100000 | -0.166667 | -0.266667 | matched |
| 65 | 15:07 | 15:14 | Player B | 36:29 | Drop Shot | Opponent Hit the Net | Hit the Net | 70 | 0.900000 | 0.266667 | -0.433333 | -0.700000 | matched |
| 66 | 15:19 | 15:22 | Player A | 37:29 | Slice Shot | Opponent Out of Bounds | Hit Out of Bounds | 71 | 0.700000 | 0.666667 | -0.233333 | -0.900000 | matched |
| 67 | 15:27 | 15:43 | Player B | 37:30 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 72 | 0.674141 | 0.966667 | 6.300000 | 5.333333 | matched |
| 68 | 15:40 | 15:50 | Player B | 37:31 | Block Shot | Opponent Hit the Net | Hit the Net | — | — | — | — | — | missed |
| 69 | 16:00 | 16:11 | Player B | 37:32 | Defensive Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 74 | 0.847761 | 1.533333 | 0.166667 | -1.366667 | matched |
| 70 | 16:17 | 16:23 | Player B | 37:33 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 75 | 0.790000 | 0.733333 | 0.666667 | -0.066667 | matched |
| 71 | 16:27 | 16:43 | Player B | 37:34 | Smash | Winner Shot | Opponent Failed to Return | 76 | 0.868472 | 1.033333 | 1.233333 | 0.200000 | matched |
| 72 | 16:49 | 16:52 | Player B | 37:35 | Net Shot | Opponent Hit the Net | Hit the Net | 77 | 0.947368 | 0.000000 | 0.166667 | 0.166667 | matched |
| 73 | 16:55 | 17:09 | Player A | 38:35 | Drop Shot | Opponent Hit the Net | Hit the Net | 78 | 0.935927 | 0.366667 | 0.566667 | 0.200000 | matched |
| 74 | 17:21 | 17:25 | Player B | 38:36 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 79 | 0.900000 | 0.400000 | 0.000000 | -0.400000 | matched |
| 75 | 17:29 | 17:40 | Player B | 38:37 | Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 80 | 0.933718 | 0.200000 | 0.566667 | 0.366667 | matched |
| 76 | 17:43 | 17:51 | Player A | 39:37 | Slice Shot | Opponent Hit the Net | Hit the Net | 81 | 0.864754 | 0.966667 | 0.133333 | -0.833333 | matched |
| 77 | 17:56 | 18:20 | Player A | 40:37 | Smash | Winner Shot | Opponent Failed to Return | 82 | 0.827778 | 0.233333 | -3.900000 | -4.133333 | matched |
| 78 | 18:22 | 18:24 | Player A | 41:37 | Net Shot | Opponent Hit the Net | Hit the Net | 84 | 0.586667 | 0.533333 | 0.500000 | -0.033333 | matched |

| Secondary-reference unmatched P | Start f | End f | Start s | End s |
|---|---|---|---|---|
| 9 | 3004 | 3161 | 100.133333 | 105.366667 |
| 11 | 3585 | 3664 | 119.500000 | 122.133333 |
| 14 | 4495 | 4618 | 149.833333 | 153.933333 |
| 33 | 13026 | 13225 | 434.200000 | 440.833333 |
| 34 | 13259 | 13468 | 441.966667 | 448.933333 |
| 35 | 13715 | 13770 | 457.166667 | 459.000000 |
| 36 | 13820 | 13910 | 460.666667 | 463.666667 |
| 41 | 15827 | 15959 | 527.566667 | 531.966667 |
| 44 | 16587 | 16719 | 552.900000 | 557.300000 |
| 45 | 17819 | 18045 | 593.966667 | 601.500000 |
| 62 | 24508 | 24587 | 816.933333 | 819.566667 |
| 73 | 28542 | 28609 | 951.400000 | 953.633333 |
| 83 | 32913 | 33023 | 1097.100000 | 1100.766667 |

| Supplied semantic label inventory | Counts |
|---|---|
| win_point_player | {"Player B":37,"Player A":41} |
| ball_types | {"Clear Shot":6,"Drop Shot":9,"Smash":11,"Push Shot":11,"Net Shot":12,"Lift Shot":8,"Block Shot":2,"Drive Shot":7,"Slice Shot":8,"Hook Shot":1,"Defensive Drive Shot":3} |
| roundscore_A | {"0":1,"1":1,"2":2,"3":2,"4":2,"5":1,"6":1,"7":5,"8":1,"9":1,"10":1,"11":1,"12":2,"13":2,"14":1,"15":1,"16":1,"17":1,"18":1,"19":3,"20":3,"21":1,"22":1,"23":1,"24":2,"25":1,"26":2,"27":2,"28":6,"29":5,"30":1,"31":1,"32":2,"33":2,"34":1,"35":1,"36":2,"37":7,"38":3,"39":1,"40":1,"41":1} |
| roundscore_B | {"1":3,"2":2,"3":2,"4":4,"5":1,"6":1,"7":1,"8":6,"9":2,"10":7,"11":1,"12":2,"13":1,"14":5,"15":3,"16":2,"17":2,"18":1,"19":1,"20":1,"21":1,"22":2,"23":1,"24":1,"25":1,"26":4,"27":2,"28":4,"29":2,"30":1,"31":1,"32":1,"33":1,"34":1,"35":2,"36":1,"37":4} |

The supplied winner/score/shot fields are reproduced above exactly as source strings, including missing values and taxonomy variation. The temporal crosswalk does not establish named player/team equivalence, certified point identity, or exhaustive shot labels. Current rally winners are unknown and hitter identities are anonymous; outcome/score-sequence accuracy and per-shot confusion therefore remain unscorable, rather than being reported as verified model correctness.

### Component-level observed output versus available ground truth

| Coverage diagnostic | Numerator | Denominator | Coverage | Ground-truth accuracy available? |
|---|---|---|---|---|
| Raw shuttle present / source frames | 21018 | 33157 | 63.389% | No reviewed frame/person/contact labels |
| Detector-executed / source frames | 13184 | 33157 | 39.762% | No reviewed frame/person/contact labels |
| Fresh detector-matched person rows / person rows | 26158 | 63796 | 41.003% | No reviewed frame/person/contact labels |
| Current pose rows / person rows | 49379 | 63796 | 77.401% | No reviewed frame/person/contact labels |
| Current racket rows / person rows | 23611 | 63796 | 37.010% | No reviewed frame/person/contact labels |

| All component coverage counts | Value |
|---|---|
| frames | 33157 |
| raw_shuttle_present | 21018 |
| detector_executed_frames | 13184 |
| person_rows | 63796 |
| scene_telemetry_present | 3641 |
| scene_raw_hypotheses | 46 |
| actual_content_epoch_increments | 46 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 26158 |
| person_propagated_or_unmatched | 37638 |
| pose_present_rows | 49379 |
| pose_current_source_rows | 49379 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 23221 |
| racket_present_rows | 23611 |
| racket_current_source_rows | 23611 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 46 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 46 |

#### Frame/component categories

| Field | Observed value |
|---|---|
| view | {"main":32206,"none":951} |
| calibration_state | {"REACQUIRING":24,"VALID":32182,"LOST":951} |
| player_population | {"0":1089,"2":31728,"1":340} |
| association_status | {"missing":11188,"observed":21018,"invalid":951} |
| association_reason | {"no_accepted_raw_observation":11188,"fresh_selection_retained":21018,"image_view_invalid":951} |
| scene_raw_status | {"unknown":140,"measured":3455,"hypothesis":46} |
| person_detector_match | {"True":26158,"False":37638} |
| person_identity_method | {"bytetrack_v1":63796} |
| scene_decision | {"barrier":46} |
| scene_decision_reason | {"raw_change_and_current_layout_discontinuity":46} |

#### Live event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 190 |
| scene | 5 |
| participant_observation | 363 |
| format_decision | 1 |
| rally_start | 84 |
| rally_end | 84 |
| stroke | 885 |
| contact | 885 |
| identity_ambiguity | 62 |
| broadcast_score | 956 |
| match_phase | 1 |
| shuttle_turn | 41 |
| highlight | 3 |

#### Append-only event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 190 |
| scene | 5 |
| participant_observation | 363 |
| format_decision | 1 |
| rally_start | 142 |
| rally_end | 84 |
| contact | 1858 |
| stroke | 905 |
| identity_ambiguity | 62 |
| broadcast_score | 956 |
| match_phase | 1 |
| shuttle_turn | 41 |
| highlight | 3 |

#### All observed event categories

| Field | Observed value |
|---|---|
| event_status | {"confirmed":3011,"provisional":550} |
| rally_end_reason | {"stationary":39,"gap":39,"cut":6} |
| rally_phase | {"unknown":4,"match_play":80} |
| rally_official | {"False":44,"True":40} |
| rally_match_format_known | {"True":84} |
| rally_match_format | {"singles":84} |
| rally_winner | {"None":84} |
| rally_score_transition_status | {"unavailable":57,"candidate":27} |
| rally_admission_reason | {"duration_policy":83,"independent_contact_and_observed_motion_witnesses":1} |
| stroke_actor | {"unknown":885} |
| stroke_physical_event_status | {"insufficient":481,"ambiguous":283,"probable":121} |
| stroke_contact_status | {"estimated":885} |
| stroke_classification_status | {"unknown":670,"estimated":215} |
| stroke_stroke | {"unknown":670,"lift":38,"push":103,"net_shot":25,"drop":24,"smash":5,"clear":9,"drive":11} |
| stroke_attribution_reason | {"nearest_proximity":877,"ambiguous_proximity":8} |
| stroke_classification_abstention_reason | {"missing_required_evidence":668,"unresolved_initial_contact":2} |
| contact_actor | {"unknown":885} |
| contact_physical_event_status | {"insufficient":481,"ambiguous":283,"probable":121} |
| contact_contact_status | {"estimated":885} |
| contact_attribution_reason | {"nearest_proximity":877,"ambiguous_proximity":8} |
| contact_trajectory_reliability | {"probable":480,"insufficient":215,"ambiguous":190} |
| contact_trajectory_reasons | {"supported_turn":380,"coherent_motion_change_unavailable":215,"supported_launch":100,"association_unresolved":190} |
| contact_impact_reliability | {"insufficient":481,"ambiguous":283,"probable":121} |
| contact_impact_reasons | {"fresh_player_observation_unavailable":481,"no_fresh_swing_or_racket_overlap":34,"association_unresolved":190,"coherent_motion_change_unavailable":59,"coherent_motion_and_fresh_contact_cue":121} |
| contact_attribution_reliability | {"insufficient":613,"probable":272} |
| contact_attribution_reasons | {"fresh_player_observation_unavailable":613,"geometric_attribution_not_verified_identity":272} |

#### Track/export counts

| Field | Observed value |
|---|---|
| camera_rows | 33157 |
| player_rows | 63784 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 63046 |
| projected_court_on_propagated_box | 37226 |
| racket_rows | 23601 |
| shuttle_rows | 33157 |

#### Track/export categories

| Field | Observed value |
|---|---|
| player_id | {"None":63784} |
| detector_matched | {"True":26147,"False":37637} |

| Semantic metric | Observed | Baseline comparison / limitation |
|---|---|---|
| Known rally winner output | 0/84 | Supplied coarse winner labels exist; identity/point mapping uncertified |
| Unknown stroke classification | 670/885 | Coarse one-label-per-rally ball_types is not exhaustive per-shot GT |
| Estimated stroke classification | 215/885 | Estimated coverage is not class accuracy |
| OCR saved readouts | 1005 | Observed scoreboard rows, not accepted correct points |
| OCR label counts | {"SHI Y.Q.":1005,"CHRISTIE":1005} | Raw OCR labels may differ from anonymous Player A/B |
| Tracked invalid geometry frames | 975 | Geometric diagnostics, not labelled location error |
| Session degradation | [{"stage":"player_identity","reason":"osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"},{"stage":"player_reid","reason":"baseline player_reid provider is unavailable"}] | Identity/ReID unavailability remains recorded; no new models fetched |

### Runtime, resources and every saved stage latency

| Saved resource/runtime metric | Value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 2349576 |
| parent_failure_inclusive_elapsed_s | — |
| parent_failure_inclusive_source_fps | — |
| neural_only_throughput_fps | — |
| model_loading_time_s | — |
| media_ready_time_s | 2.317508 |
| model_staging_time_s | 1.677650 |
| worker_final_cpu_s | 39141.091468 |
| worker_maxrss_bytes | 2807271424 |
| sampled_worker_tree_peak_rss_bytes | 3005173760 |
| sampled_worker_gpu_peak_mib | 2122 |
| sampled_cpu_seconds_max_observed | 39140.930000 |
| sampled_cpu_seconds_last_observed | 39140.930000 |
| sampled_system_available_ram_min_bytes | 100863033344 |
| sample_count | 1801 |
| resource_rows | 1801 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 3729.349836 |
| parent_completed_source_fps | 8.890826 |
| worker_elapsed_s | 3718.272271 |
| worker_source_fps | 8.917314 |
| component_initialization_including_models_s | 9.012962 |

| Stage | Calls | Total wall s | P50 ms/call | P95 ms/call | Minimum ms | Maximum ms | Frame-population sum |
|---|---|---|---|---|---|---|---|
| court | 553 | 200.924755 | 307.111172 | 405.241007 | 177.654064 | 2150.397495 | 33157 |
| content_continuity_and_players | 553 | 1524.897010 | 3220.903793 | 3522.543325 | 36.763066 | 3769.317017 | 33157 |
| shuttle | 540 | 471.116832 | 851.395763 | 1072.256103 | 510.973479 | 1422.732157 | 32377 |
| players | 553 | 96.140772 | 179.430816 | 359.841947 | 0.590889 | 519.308254 | 33157 |
| ocr | 553 | 419.090960 | 760.678652 | 978.479509 | 0.015757 | 1368.829006 | 33157 |

| Runner timing scope | Seconds |
|---|---|
| component_initialization_including_models_s | 9.012962 |
| decode_perception_cache_s | 2939.406715 |

| Additional completed-worker timing | Seconds |
|---|---|
| Perception completion catalogue publication | 6.474083 |
| Worker media ready | 2.317508 |
| Model staging | 1.677650 |

| Actual worker reproducibility metadata | Value |
|---|---|
| Visible Torch devices | [{"logical_index":0,"name":"NVIDIA GeForce GTX 1080 Ti","uuid":"a618f090-66bf-ad80-b0a5-0c91bee61fab"}] |
| CUDA_VISIBLE_DEVICES GPU UUID | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| Prior cached perceptions used | false |
| Worker model manifest SHA256 | b5590b8ff1437945da036b42b01729f521728259a0dfc4c3299a926216ba8df3 |
| Worker staged model pins SHA256 | 7bd228ead493bba31c1417c46346d35e3cd00e1760ba7d7b35485d3babf5219f |

The historical timing key decode_perception_cache_s wraps the runner’s full _perceive call. Its name does not mean this was an observation-cache replay: the completed-worker receipts explicitly record cached_perception_used=false. It is a broad perception wall-time scope, not isolated cache decoding or pure GPU latency.

| Saved disk-use metric | Bytes / count |
|---|---|
| regular_files | 3322 |
| logical_bytes | 1245506778 |
| allocated_bytes | 1252356096 |
| staged_model_bytes | 361041769 |
| perception_cache_bytes | 125784025 |

Wall-time scopes overlap; they are not summable GPU kernel latency. Pure neural-only FPS and isolated model-loading time remain unavailable. For historical Tests 1/2, final worker-local timing/CPU/RSS fields were lost at catalogue publication and stay unavailable; failure-inclusive parent duration is identified explicitly. For normal runs, worker elapsed includes the runner and final catalogue verification. Current-process GPU samples cannot certify per-node ORT placement or true instantaneous memory peaks.

### Reproducibility, logs and annotation-file review

| Binding | Value |
|---|---|
| Normalized numerical profile SHA256 (passive ranges removed) | 2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb |
| Effective profile canonical SHA256 | 85985c197cf71fd42dcffbdacbfa60ddfc6f87b9be894c7168b71ef02f004fac |
| Model identity sets | 1 |
| Runtime identity sets | 1 |
| Actual model identity SHA256 | e3c96b7c2e522fd6efe6106328bebec30137f29b7303fe5e475f8aedea5d2222 |
| Actual runtime identity SHA256 | 81e41f18d858ed37c34ce9d07ae34a34268f27e57c0e5f878e07253be309066f |
| Executed plan | [plan.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test9/protocol/plan.json) |
| Actual completion receipt | [inference.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test9/run/inference.json) |
| Per-rally saved CSV | [per_rally_comparison.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test9/evaluation/per_rally_comparison.csv) |
| Technical analysis | [technical_analysis.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test9/analysis/technical_analysis.json) |
| Full original predictions | [predicted_rallies.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test9/run/predicted_rallies.csv) |

| Annotation file | Role | Data rows | Blank rows | Bytes | Column/schema inventory | SHA256 |
|---|---|---|---|---|---|---|
| Test9_Full.csv | Secondary coarse outcome/time reference | 88 | 10 | 5942 | ["start_time","end_time","win_point_player","win_reason","ball_types","lose_reason","roundscore_A","roundscore_B"] | f770e681fd033bbfe8061565b58f5d09d2042a1029447e7f22a1d05af8166d3f |
| Test9_Full_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 33157 | 0 | 713118 | ["Frame","X","Y","Visibility","Confidence"] | cdb4d91ddd0869615860c7ac8a677266baae588d752ee403d7129f2f946dac5e |
| Test9_Full_court.json | Auxiliary historical/generated artifact; not certified independent truth | — | — | 537 | ["frame_no","frame_size","corners","net","source"] | 70e660120883230ba303d868a2be1d0bf30303c74022321d1ca3d9788b0afb6d |
| Test9_Full_rally.csv | Primary timing reference | 82 | 0 | 5890 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 39dd99a09db0c9e4a669c504cebed0fbad69927e339884127c48bf63da073435 |
| player_detections.csv | Auxiliary historical/generated artifact; not certified independent truth | 33157 | 0 | 3624988 | ["frame_no","player_1_x","player_1_y","player_1_conf","player_2_x","player_2_y","player_2_conf"] | fd40aa9bcae27b59223123fa8fdf954338fdf4eed48fc8988ce1e5d3e5a4fc52 |
| win_predictions.csv | Auxiliary historical/generated artifact; not certified independent truth | 82 | 0 | 9928 | ["rally_idx","start_frame","end_frame","start_time","end_time","winner","loser","win_reason","reason_src","fault_side","fault_src","cnn_class","cnn_conf","cnn_oob","cnn_hn","cnn_wbl","score_Player A","score_Player B"] | 7696b583d8947841f3aae969d21a826a07bb74af3fb28f87a968e2bd6705e792 |

| Log | Lines | Warning/error-pattern lines | Distinct observed warning/error messages |
|---|---|---|---|
| analysis.log | 1 | 0 | [] |
| download.log | 266 | 0 | [] |
| evaluation.log | 0 | 0 | [] |
| prepare.log | 0 | 0 | [] |
| run.execution.log | 38 | 22 | ["2026-11-06 02:30:30 [warning  ] perception.degraded            reason='osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`' stage=player_identity","2026-11-06 02:30:30 [warning  ] perception.degraded            reason='baseline player_reid provider is unavailable' stage=player_reid","[WARNING] 2026-11-06 02:31:15,978 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:31:29,637 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:31:42,623 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:31:56,459 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:32:07,322 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:32:18,408 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:32:32,183 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:32:41,625 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:32:54,882 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:46:52,496 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:46:58,005 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:46:58,284 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:47:02,450 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:47:07,191 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:47:21,233 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:47:33,389 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 02:47:47,373 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 03:06:54,559 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 03:07:12,332 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 03:21:17,269 [RapidOCR] main.py:164: The text detection result is empty"] |
| run.launch.log | 0 | 0 | [] |
| timestamps.log | 1 | 0 | [] |

Log keyword counts are diagnostic string matches, not failed-inference counts. Tests 1/2 raw original worker logs remain in their source run directories and retain the known final catalogue failure; their independent completion proof is the accepted completion record. All previously completed evaluations remain immutable.

### Duration breakdown for this video

| GT duration bin | GT count | Matched | Missed | Recall | Start MAE f | End MAE f |
|---|---|---|---|---|---|---|
| ≤2 s | 1 | 0 | 1 | 0.000000 | — | — |
| (2,5] s | 19 | 16 | 3 | 0.842105 | 9.875000 | 11.500000 |
| (5,10] s | 32 | 27 | 5 | 0.843750 | 13.629630 | 14.259259 |
| (10,20] s | 25 | 23 | 2 | 0.920000 | 41.956522 | 24.652174 |
| >20 s | 5 | 3 | 2 | 0.600000 | 29.000000 | 55.666667 |

## Test 10: complete evaluation and ground-truth comparison

Reference **93 rallies**, predictions **98**; TP/FP/FN **85/13/8**. Precision **86.735%**, recall **91.398%**, F1 **89.005%**. Matched mean IoU **0.844965**. The ground-truth benchmark for every table in this primary section is [Test10_Full_rally.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test10_Full/Test10_Full_rally.csv).

| Input / execution binding | Value |
|---|---|
| Decoded frames | 37133 |
| FPS | 30.000000 |
| Video duration seconds | 1237.766667 |
| Canonical dimensions | 1280 × 720 |
| Source SHA256 | cf71d8e02086df5e192e3cf834804407ca5d9e0f2f6bdf26512b39b6b264214f |
| Proxy SHA256 | 4a57f6f4e33a80a1d5301ad015b3d6f34091e9d0b07be88c631f00ad743c6cfd |
| Prediction SHA256 | 2f0e14e5e131bc07f74a84d73ce8dbdcda08af74c696e8f4d65066bc1e7fbbc7 |
| Ground-truth SHA256 | 509cabed282eac89217d41a7d1b860991456f5d09cab24bb58b2acaba824d0cf |
| Coarse reference SHA256 | 2fed7c63a5042dbb6ab01ea4baff57cf0a974947218aaeef0c4a07f721648789 |
| Session | UPLOADTEST10 |
| Actual completion mode | normal_completed_worker |
| Original parent receipt status | completed |
| Full source/proxy PTS matches | 37133 |
| Scene probe pixel hashes verified | 54 |
| Verified saved files / logical bytes | 4056 / 1475945145 |
| Read-only record | [saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10_retry1) |

### Primary metric scores versus the ground-truth ideal

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 93 | 93 | 0 |
| Prediction count | 93 | 98 | 5 |
| TP / matched | 93 | 85 | -8 |
| FP | 0 | 13 | 13 |
| FN / missed | 0 | 8 | 8 |
| precision | 1 | 0.867347 | -0.132653 |
| recall | 1 | 0.913978 | -0.086022 |
| f1 | 1 | 0.890052 | -0.109948 |
| Mean matched IoU | 1 | 0.844965 | -0.155035 |
| Median matched IoU | 1 | 0.895425 | -0.104575 |
| Minimum matched IoU | 1 | 0.510067 | -0.489933 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 78.823529 |
| 0.9 | 100 | 48.235294 |
| 0.95 | 100 | 23.529412 |

A GT self-comparison has TP=N, FP=FN=0, precision/recall/F1=1, IoU=1 and every timing/duration error=0. This is the reference ideal, not a separately executed baseline model. The signed count difference alone is insufficient: false positives and misses can cancel.

### Boundary and duration errors versus zero-error ground truth

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 23.988235 | 7.000000 | 50.296415 | 206.000000 | 52.800000 | 15.658824 | 6.000000 |
| end_frame | 18.058824 | 7.000000 | 30.619678 | 136.000000 | 45.600000 | -10.341176 | -4.000000 |
| start_time_sec | 0.799608 | 0.233333 | 1.676547 | 6.866667 | 1.760000 | 0.521961 | 0.200000 |
| end_time_sec | 0.601961 | 0.233333 | 1.020656 | 4.533333 | 1.520000 | -0.344706 | -0.133333 |
| duration_sec | 1.227451 | 0.600000 | 2.052227 | 7.433333 | 3.180000 | -0.866667 | -0.533333 |

| Additional saved statistic | Value | Ground-truth ideal |
|---|---|---|
| Start P95 \|error\| frames | 142.200000 | 0 |
| End P95 \|error\| frames | 65.600000 | 0 |
| Duration mae frames | 36.823529 | 0 |
| Duration rmse frames | 61.566798 | 0 |
| Duration signed_bias frames | -26.000000 | 0 |

All error statistics above condition on eligible matched rallies. A positive start error is a late start; a negative start error is early. A positive end error is a late end; a negative end error is premature. Duration error is prediction minus GT. All 30 FPS frame errors convert by dividing by30; full signed/absolute per-rally values appear below. Misses have no invented zero error.

### Boundary tolerance scores

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 7 | 85 | 8.235% | 93 | 7.527% | 100% |
| start | 3 | 0.100000 | 15 | 85 | 17.647% | 93 | 16.129% | 100% |
| start | 5 | 0.166667 | 32 | 85 | 37.647% | 93 | 34.409% | 100% |
| start | 10 | 0.333333 | 54 | 85 | 63.529% | 93 | 58.065% | 100% |
| start | 15 | 0.500000 | 62 | 85 | 72.941% | 93 | 66.667% | 100% |
| start | 30 | 1.000000 | 69 | 85 | 81.176% | 93 | 74.194% | 100% |
| end | 1 | 0.033333 | 10 | 85 | 11.765% | 93 | 10.753% | 100% |
| end | 3 | 0.100000 | 17 | 85 | 20.000% | 93 | 18.280% | 100% |
| end | 5 | 0.166667 | 32 | 85 | 37.647% | 93 | 34.409% | 100% |
| end | 10 | 0.333333 | 46 | 85 | 54.118% | 93 | 49.462% | 100% |
| end | 15 | 0.500000 | 57 | 85 | 67.059% | 93 | 61.290% | 100% |
| end | 30 | 1.000000 | 70 | 85 | 82.353% | 93 | 75.269% | 100% |

### All saved error distributions

| Distribution / units | N | Mean | Median | Minimum | Maximum | P90 | P95 | Ideal |
|---|---|---|---|---|---|---|---|---|
| matched_iou | 85 | 0.844965 | 0.895425 | 0.510067 | 0.996350 | 0.976718 | 0.983282 | 1 |
| start_signed_frames | 85 | 15.658824 | 6.000000 | -188.000000 | 206.000000 | 45.600000 | 92.600000 | 0 |
| start_absolute_frames | 85 | 23.988235 | 7.000000 | 0.000000 | 206.000000 | 52.800000 | 142.200000 | 0 |
| end_signed_frames | 85 | -10.341176 | -4.000000 | -136.000000 | 39.000000 | 14.600000 | 19.000000 | 0 |
| end_absolute_frames | 85 | 18.058824 | 7.000000 | 0.000000 | 136.000000 | 45.600000 | 65.600000 | 0 |
| duration_signed_frames | 85 | -26.000000 | -16.000000 | -223.000000 | 212.000000 | 4.600000 | 12.000000 | 0 |
| duration_absolute_frames | 85 | 36.823529 | 18.000000 | 0.000000 | 223.000000 | 95.400000 | 145.000000 | 0 |
| duration_signed_seconds | 85 | -0.866667 | -0.533333 | -7.433333 | 7.066667 | 0.153333 | 0.400000 | 0 |

### Misses, extras, overlap topology and failure review

| Diagnostic | Observed | GT ideal / interpretation |
|---|---|---|
| Missed GT IDs | [9,15,30,37,40,43,55,85] | [] |
| Unmatched prediction IDs | [28,32,33,37,40,43,44,45,61,68,85,89,90] | [] |
| No-overlap missed GT IDs | [15,55] | [] |
| Predictions without any GT overlap | [32,33] | [] |
| Possible split GT IDs | [43,60,65,82,85] | Geometric overlap candidates; not adjudicated semantic splits |
| Possible merge prediction IDs | [9] | Geometric overlap candidates; not adjudicated semantic merges |
| Significant failure records | 51 | Unmatched or \|boundary error\|>30frames or IoU<0.75 |
| early_start_gt_ids | [10,18,53] | Direction/weak-overlap inventory, not a physical cause |
| late_start_gt_ids | [1,2,3,4,5,6,7,8,11,12,13,14,16,17,19,20,21,22,23,24,25,26,27,28,29,31,32,33,34,35,36,38,39,41,42,44,45,46,47,48,49,50,51,52,54,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,73,74,75,76,77,78,79,80,81,82,83,84,86,88,89,90,91,92,93] | Direction/weak-overlap inventory, not a physical cause |
| premature_end_gt_ids | [1,3,6,8,12,13,16,17,18,20,21,22,24,25,27,29,34,35,36,39,41,45,46,47,48,50,51,53,54,56,57,58,59,61,62,65,66,68,69,70,71,72,73,74,75,76,79,82,87,88,89,90,93] | Direction/weak-overlap inventory, not a physical cause |
| late_end_gt_ids | [2,5,7,10,11,14,19,23,31,33,38,42,44,52,60,63,64,67,77,78,80,81,83,84,86,91,92] | Direction/weak-overlap inventory, not a physical cause |
| weak_iou_gt_ids | [4,5,6,10,18,20,29,35,51,56,60,65,76,78,80,82,83,93] | Direction/weak-overlap inventory, not a physical cause |

| Inventory validity | Ground truth | Predictions |
|---|---|---|
| count | 93 | 98 |
| duplicate_row_pairs | [] | [] |
| positive_overlap_row_pairs | [] | [] |
| adjacent_row_pairs | [] | [] |
| out_of_range_rows | [] | [] |
| out_of_order_rows | [] | [] |

| False detection P ID | Start frame | End frame | Start seconds | End seconds | Duration seconds | Positive-overlap GT IDs |
|---|---|---|---|---|---|---|
| 28 | 11073 | 11131 | 369.100000 | 371.033333 | 1.933333 | [30] |
| 32 | 12209 | 12280 | 406.966667 | 409.333333 | 2.366667 | [] |
| 33 | 12313 | 12471 | 410.433333 | 415.700000 | 5.266667 | [] |
| 37 | 14065 | 14227 | 468.833333 | 474.233333 | 5.400000 | [37] |
| 40 | 15556 | 15657 | 518.533333 | 521.900000 | 3.366667 | [40] |
| 43 | 16643 | 17055 | 554.766667 | 568.500000 | 13.733333 | [43] |
| 44 | 17174 | 17340 | 572.466667 | 578.000000 | 5.533333 | [43] |
| 45 | 17376 | 17655 | 579.200000 | 588.500000 | 9.300000 | [43] |
| 61 | 24185 | 24347 | 806.166667 | 811.566667 | 5.400000 | [60] |
| 68 | 26206 | 26355 | 873.533333 | 878.500000 | 4.966667 | [65] |
| 85 | 32693 | 32831 | 1089.766667 | 1094.366667 | 4.600000 | [82] |
| 89 | 34122 | 34223 | 1137.400000 | 1140.766667 | 3.366667 | [85] |
| 90 | 34246 | 34335 | 1141.533333 | 1144.500000 | 2.966667 | [85] |

| Largest matched boundary cases | P ID | GT start/end frames | Pred start/end frames | Δstart frames | Δend frames | IoU |
|---|---|---|---|---|---|---|
| 82 | 86 | 32663–33376 | 32869–33370 | 206 | -6 | 0.702665 |
| 10 | 9 | 2726–3170 | 2538–3194 | -188 | 24 | 0.676829 |
| 60 | 62 | 24184–24619 | 24372–24626 | 188 | 7 | 0.558824 |
| 35 | 35 | 12699–13169 | 12880–13127 | 181 | -42 | 0.525532 |
| 18 | 16 | 5622–5834 | 5469–5827 | -153 | -7 | 0.561644 |

Of 8 unmatched reference intervals, 2 have no positive overlap with any prediction; 6 have some overlap but fail the one-to-one IoU eligibility/assignment. This separates absence of overlap from insufficient interval agreement without inventing a causal diagnosis.

### Every GT rally compared directly with its assigned prediction: frames

G IDs are one-based CSV row IDs in the primary rally reference. P IDs are one-based rows in the preserved prediction CSV. C IDs refer to the separate coarse table, linked only by the same IoU-based temporal crosswalk. “—” denotes unavailable/unmatched, not zero.

| G | P | GT start f | GT end f | Pred start f | Pred end f | Δstart f | \|Δstart\| f | Δend f | \|Δend\| f | IoU | Status | Coarse C row |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 131 | 594 | 140 | 579 | 9 | 9 | -15 | 15 | 0.948164 | matched | 1 |
| 2 | 2 | 645 | 704 | 651 | 707 | 6 | 6 | 3 | 3 | 0.854839 | matched | 2 |
| 3 | 3 | 822 | 973 | 832 | 971 | 10 | 10 | -2 | 2 | 0.920530 | matched | 3 |
| 4 | 4 | 1012 | 1199 | 1091 | 1199 | 79 | 79 | 0 | 0 | 0.577540 | matched | — |
| 5 | 5 | 1242 | 1344 | 1273 | 1367 | 31 | 31 | 23 | 23 | 0.568000 | matched | 5 |
| 6 | 6 | 1544 | 1693 | 1551 | 1627 | 7 | 7 | -66 | 66 | 0.510067 | matched | 6 |
| 7 | 7 | 1719 | 2082 | 1723 | 2089 | 4 | 4 | 7 | 7 | 0.970270 | matched | 7 |
| 8 | 8 | 2224 | 2428 | 2229 | 2413 | 5 | 5 | -15 | 15 | 0.901961 | matched | 8 |
| 9 | — | 2533 | 2690 | — | — | — | — | — | — | — | missed | — |
| 10 | 9 | 2726 | 3170 | 2538 | 3194 | -188 | 188 | 24 | 24 | 0.676829 | matched | 9 |
| 11 | 10 | 3376 | 3720 | 3377 | 3728 | 1 | 1 | 8 | 8 | 0.974432 | matched | 10 |
| 12 | 11 | 3744 | 4114 | 3770 | 4110 | 26 | 26 | -4 | 4 | 0.918919 | matched | 11 |
| 13 | 12 | 4147 | 4400 | 4156 | 4395 | 9 | 9 | -5 | 5 | 0.944664 | matched | 12 |
| 14 | 13 | 4458 | 4528 | 4459 | 4530 | 1 | 1 | 2 | 2 | 0.958333 | matched | 13 |
| 15 | — | 4580 | 4640 | — | — | — | — | — | — | — | missed | — |
| 16 | 14 | 4778 | 4928 | 4781 | 4915 | 3 | 3 | -13 | 13 | 0.893333 | matched | 14 |
| 17 | 15 | 5172 | 5446 | 5181 | 5435 | 9 | 9 | -11 | 11 | 0.927007 | matched | 15 |
| 18 | 16 | 5622 | 5834 | 5469 | 5827 | -153 | 153 | -7 | 7 | 0.561644 | matched | 16 |
| 19 | 17 | 5944 | 6055 | 5945 | 6074 | 1 | 1 | 19 | 19 | 0.846154 | matched | 17 |
| 20 | 18 | 6076 | 6184 | 6115 | 6179 | 39 | 39 | -5 | 5 | 0.592593 | matched | 18 |
| 21 | 19 | 6436 | 6573 | 6437 | 6547 | 1 | 1 | -26 | 26 | 0.802920 | matched | 19 |
| 22 | 20 | 6667 | 6971 | 6675 | 6951 | 8 | 8 | -20 | 20 | 0.907895 | matched | 20 |
| 23 | 21 | 7029 | 7329 | 7035 | 7343 | 6 | 6 | 14 | 14 | 0.936306 | matched | 21 |
| 24 | 22 | 7678 | 7984 | 7681 | 7980 | 3 | 3 | -4 | 4 | 0.977124 | matched | 23 |
| 25 | 23 | 8118 | 8568 | 8124 | 8497 | 6 | 6 | -71 | 71 | 0.828889 | matched | 24 |
| 26 | 24 | 8739 | 9287 | 8741 | 9287 | 2 | 2 | 0 | 0 | 0.996350 | matched | — |
| 27 | 25 | 9371 | 10273 | 9377 | 10270 | 6 | 6 | -3 | 3 | 0.990022 | matched | 26 |
| 28 | 26 | 10374 | 10667 | 10381 | 10667 | 7 | 7 | 0 | 0 | 0.976109 | matched | 27 |
| 29 | 27 | 10860 | 11020 | 10871 | 10967 | 11 | 11 | -53 | 53 | 0.600000 | matched | 28 |
| 30 | — | 11070 | 11191 | — | — | — | — | — | — | — | missed | 29 |
| 31 | 29 | 11230 | 11334 | 11237 | 11347 | 7 | 7 | 13 | 13 | 0.829060 | matched | 30 |
| 32 | 30 | 11360 | 11447 | 11377 | 11447 | 17 | 17 | 0 | 0 | 0.804598 | matched | 31 |
| 33 | 31 | 11536 | 12086 | 11541 | 12091 | 5 | 5 | 5 | 5 | 0.981982 | matched | 32 |
| 34 | 34 | 12557 | 12672 | 12567 | 12655 | 10 | 10 | -17 | 17 | 0.765217 | matched | 35 |
| 35 | 35 | 12699 | 13169 | 12880 | 13127 | 181 | 181 | -42 | 42 | 0.525532 | matched | 36 |
| 36 | 36 | 13199 | 13926 | 13201 | 13921 | 2 | 2 | -5 | 5 | 0.990371 | matched | 37 |
| 37 | — | 14160 | 14234 | — | — | — | — | — | — | — | missed | — |
| 38 | 38 | 14287 | 14983 | 14297 | 15022 | 10 | 10 | 39 | 39 | 0.933333 | matched | 39 |
| 39 | 39 | 15142 | 15349 | 15146 | 15343 | 4 | 4 | -6 | 6 | 0.951691 | matched | 40 |
| 40 | — | 15412 | 15675 | — | — | — | — | — | — | — | missed | — |
| 41 | 41 | 15912 | 16154 | 15917 | 16153 | 5 | 5 | -1 | 1 | 0.975207 | matched | 42 |
| 42 | 42 | 16196 | 16478 | 16230 | 16484 | 34 | 34 | 6 | 6 | 0.861111 | matched | 43 |
| 43 | — | 16641 | 17679 | — | — | — | — | — | — | — | missed | — |
| 44 | 46 | 17968 | 18217 | 17981 | 18221 | 13 | 13 | 4 | 4 | 0.932806 | matched | 46 |
| 45 | 47 | 18260 | 18453 | 18266 | 18437 | 6 | 6 | -16 | 16 | 0.886010 | matched | 47 |
| 46 | 48 | 18495 | 18837 | 18500 | 18831 | 5 | 5 | -6 | 6 | 0.967836 | matched | 48 |
| 47 | 49 | 18904 | 19227 | 18909 | 19163 | 5 | 5 | -64 | 64 | 0.786378 | matched | 49 |
| 48 | 50 | 19369 | 19851 | 19423 | 19847 | 54 | 54 | -4 | 4 | 0.879668 | matched | 50 |
| 49 | 51 | 19918 | 20327 | 19927 | 20327 | 9 | 9 | 0 | 0 | 0.977995 | matched | 51 |
| 50 | 52 | 20512 | 20814 | 20517 | 20810 | 5 | 5 | -4 | 4 | 0.970199 | matched | 52 |
| 51 | 53 | 20922 | 21104 | 20923 | 21059 | 1 | 1 | -45 | 45 | 0.747253 | matched | 53 |
| 52 | 54 | 21145 | 21827 | 21161 | 21842 | 16 | 16 | 15 | 15 | 0.955524 | matched | 54 |
| 53 | 55 | 21938 | 22510 | 21925 | 22468 | -13 | 13 | -42 | 42 | 0.905983 | matched | 55 |
| 54 | 56 | 22539 | 22919 | 22550 | 22883 | 11 | 11 | -36 | 36 | 0.876316 | matched | 56 |
| 55 | — | 22960 | 23033 | — | — | — | — | — | — | — | missed | 57 |
| 56 | 57 | 23098 | 23366 | 23103 | 23254 | 5 | 5 | -112 | 112 | 0.563433 | matched | 58 |
| 57 | 58 | 23398 | 23499 | 23409 | 23497 | 11 | 11 | -2 | 2 | 0.871287 | matched | 59 |
| 58 | 59 | 23634 | 23867 | 23641 | 23866 | 7 | 7 | -1 | 1 | 0.965665 | matched | 60 |
| 59 | 60 | 23966 | 24135 | 23989 | 24134 | 23 | 23 | -1 | 1 | 0.857988 | matched | 61 |
| 60 | 62 | 24184 | 24619 | 24372 | 24626 | 188 | 188 | 7 | 7 | 0.558824 | matched | 62 |
| 61 | 63 | 24732 | 25071 | 24736 | 25055 | 4 | 4 | -16 | 16 | 0.941003 | matched | 63 |
| 62 | 64 | 25175 | 25372 | 25193 | 25370 | 18 | 18 | -2 | 2 | 0.898477 | matched | 64 |
| 63 | 65 | 25479 | 25628 | 25484 | 25635 | 5 | 5 | 7 | 7 | 0.923077 | matched | 65 |
| 64 | 66 | 25652 | 25860 | 25685 | 25876 | 33 | 33 | 16 | 16 | 0.781250 | matched | 66 |
| 65 | 67 | 25944 | 26313 | 25949 | 26177 | 5 | 5 | -136 | 136 | 0.617886 | matched | 67 |
| 66 | 69 | 26553 | 26627 | 26558 | 26622 | 5 | 5 | -5 | 5 | 0.864865 | matched | 68 |
| 67 | 70 | 26689 | 26846 | 26695 | 26865 | 6 | 6 | 19 | 19 | 0.857955 | matched | 69 |
| 68 | 71 | 27039 | 27456 | 27042 | 27435 | 3 | 3 | -21 | 21 | 0.942446 | matched | 70 |
| 69 | 72 | 27468 | 28275 | 27489 | 28184 | 21 | 21 | -91 | 91 | 0.861214 | matched | 71 |
| 70 | 73 | 28371 | 28494 | 28373 | 28478 | 2 | 2 | -16 | 16 | 0.853659 | matched | 72 |
| 71 | 74 | 28537 | 28623 | 28543 | 28622 | 6 | 6 | -1 | 1 | 0.918605 | matched | 73 |
| 72 | 75 | 28683 | 29104 | 28683 | 29040 | 0 | 0 | -64 | 64 | 0.847981 | matched | 74 |
| 73 | 76 | 29241 | 29697 | 29247 | 29671 | 6 | 6 | -26 | 26 | 0.929825 | matched | 75 |
| 74 | 77 | 29716 | 30342 | 29721 | 30296 | 5 | 5 | -46 | 46 | 0.918530 | matched | 76 |
| 75 | 78 | 30395 | 30512 | 30401 | 30511 | 6 | 6 | -1 | 1 | 0.940171 | matched | 77 |
| 76 | 79 | 30534 | 30817 | 30630 | 30812 | 96 | 96 | -5 | 5 | 0.643110 | matched | 78 |
| 77 | 80 | 31277 | 31513 | 31281 | 31522 | 4 | 4 | 9 | 9 | 0.946939 | matched | 79 |
| 78 | 81 | 31556 | 31693 | 31584 | 31725 | 28 | 28 | 32 | 32 | 0.644970 | matched | 80 |
| 79 | 82 | 31896 | 32034 | 31911 | 32019 | 15 | 15 | -15 | 15 | 0.782609 | matched | 81 |
| 80 | 83 | 32046 | 32167 | 32097 | 32175 | 51 | 51 | 8 | 8 | 0.542636 | matched | 82 |
| 81 | 84 | 32255 | 32636 | 32258 | 32641 | 3 | 3 | 5 | 5 | 0.979275 | matched | 83 |
| 82 | 86 | 32663 | 33376 | 32869 | 33370 | 206 | 206 | -6 | 6 | 0.702665 | matched | 85 |
| 83 | 87 | 33412 | 33706 | 33511 | 33718 | 99 | 99 | 12 | 12 | 0.637255 | matched | 86 |
| 84 | 88 | 33845 | 34057 | 33895 | 34061 | 50 | 50 | 4 | 4 | 0.750000 | matched | 87 |
| 85 | — | 34101 | 34329 | — | — | — | — | — | — | — | missed | 88 |
| 86 | 91 | 34354 | 34519 | 34366 | 34534 | 12 | 12 | 15 | 15 | 0.850000 | matched | 89 |
| 87 | 92 | 34546 | 34668 | 34546 | 34666 | 0 | 0 | -2 | 2 | 0.983607 | matched | 90 |
| 88 | 93 | 34724 | 35093 | 34738 | 35087 | 14 | 14 | -6 | 6 | 0.945799 | matched | 91 |
| 89 | 94 | 35316 | 35509 | 35320 | 35502 | 4 | 4 | -7 | 7 | 0.943005 | matched | 92 |
| 90 | 95 | 35639 | 36323 | 35642 | 36319 | 3 | 3 | -4 | 4 | 0.989766 | matched | 93 |
| 91 | 96 | 36490 | 36710 | 36494 | 36715 | 4 | 4 | 5 | 5 | 0.960000 | matched | 94 |
| 92 | 97 | 36770 | 36916 | 36779 | 36923 | 9 | 9 | 7 | 7 | 0.895425 | matched | 95 |
| 93 | 98 | 36988 | 37132 | 37026 | 37119 | 38 | 38 | -13 | 13 | 0.645833 | matched | 96 |

### Every GT rally compared directly: timestamps and durations

| G | GT start s | GT end s | Pred start s | Pred end s | GT duration s | Pred duration s | Δstart s | \|Δstart\| s | Δend s | \|Δend\| s | Δduration s | \|Δduration\| s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4.366667 | 19.800000 | 4.666667 | 19.300000 | 15.433333 | 14.633333 | 0.300000 | 0.300000 | -0.500000 | 0.500000 | -0.800000 | 0.800000 |
| 2 | 21.500000 | 23.466667 | 21.700000 | 23.566667 | 1.966667 | 1.866667 | 0.200000 | 0.200000 | 0.100000 | 0.100000 | -0.100000 | 0.100000 |
| 3 | 27.400000 | 32.433333 | 27.733333 | 32.366667 | 5.033333 | 4.633333 | 0.333333 | 0.333333 | -0.066667 | 0.066667 | -0.400000 | 0.400000 |
| 4 | 33.733333 | 39.966667 | 36.366667 | 39.966667 | 6.233333 | 3.600000 | 2.633333 | 2.633333 | 0.000000 | 0.000000 | -2.633333 | 2.633333 |
| 5 | 41.400000 | 44.800000 | 42.433333 | 45.566667 | 3.400000 | 3.133333 | 1.033333 | 1.033333 | 0.766667 | 0.766667 | -0.266667 | 0.266667 |
| 6 | 51.466667 | 56.433333 | 51.700000 | 54.233333 | 4.966667 | 2.533333 | 0.233333 | 0.233333 | -2.200000 | 2.200000 | -2.433333 | 2.433333 |
| 7 | 57.300000 | 69.400000 | 57.433333 | 69.633333 | 12.100000 | 12.200000 | 0.133333 | 0.133333 | 0.233333 | 0.233333 | 0.100000 | 0.100000 |
| 8 | 74.133333 | 80.933333 | 74.300000 | 80.433333 | 6.800000 | 6.133333 | 0.166667 | 0.166667 | -0.500000 | 0.500000 | -0.666667 | 0.666667 |
| 9 | 84.433333 | 89.666667 | — | — | 5.233333 | — | — | — | — | — | — | — |
| 10 | 90.866667 | 105.666667 | 84.600000 | 106.466667 | 14.800000 | 21.866667 | -6.266667 | 6.266667 | 0.800000 | 0.800000 | 7.066667 | 7.066667 |
| 11 | 112.533333 | 124.000000 | 112.566667 | 124.266667 | 11.466667 | 11.700000 | 0.033333 | 0.033333 | 0.266667 | 0.266667 | 0.233333 | 0.233333 |
| 12 | 124.800000 | 137.133333 | 125.666667 | 137.000000 | 12.333333 | 11.333333 | 0.866667 | 0.866667 | -0.133333 | 0.133333 | -1.000000 | 1.000000 |
| 13 | 138.233333 | 146.666667 | 138.533333 | 146.500000 | 8.433333 | 7.966667 | 0.300000 | 0.300000 | -0.166667 | 0.166667 | -0.466667 | 0.466667 |
| 14 | 148.600000 | 150.933333 | 148.633333 | 151.000000 | 2.333333 | 2.366667 | 0.033333 | 0.033333 | 0.066667 | 0.066667 | 0.033333 | 0.033333 |
| 15 | 152.666667 | 154.666667 | — | — | 2.000000 | — | — | — | — | — | — | — |
| 16 | 159.266667 | 164.266667 | 159.366667 | 163.833333 | 5.000000 | 4.466667 | 0.100000 | 0.100000 | -0.433333 | 0.433333 | -0.533333 | 0.533333 |
| 17 | 172.400000 | 181.533333 | 172.700000 | 181.166667 | 9.133333 | 8.466667 | 0.300000 | 0.300000 | -0.366667 | 0.366667 | -0.666667 | 0.666667 |
| 18 | 187.400000 | 194.466667 | 182.300000 | 194.233333 | 7.066667 | 11.933333 | -5.100000 | 5.100000 | -0.233333 | 0.233333 | 4.866667 | 4.866667 |
| 19 | 198.133333 | 201.833333 | 198.166667 | 202.466667 | 3.700000 | 4.300000 | 0.033333 | 0.033333 | 0.633333 | 0.633333 | 0.600000 | 0.600000 |
| 20 | 202.533333 | 206.133333 | 203.833333 | 205.966667 | 3.600000 | 2.133333 | 1.300000 | 1.300000 | -0.166667 | 0.166667 | -1.466667 | 1.466667 |
| 21 | 214.533333 | 219.100000 | 214.566667 | 218.233333 | 4.566667 | 3.666667 | 0.033333 | 0.033333 | -0.866667 | 0.866667 | -0.900000 | 0.900000 |
| 22 | 222.233333 | 232.366667 | 222.500000 | 231.700000 | 10.133333 | 9.200000 | 0.266667 | 0.266667 | -0.666667 | 0.666667 | -0.933333 | 0.933333 |
| 23 | 234.300000 | 244.300000 | 234.500000 | 244.766667 | 10.000000 | 10.266667 | 0.200000 | 0.200000 | 0.466667 | 0.466667 | 0.266667 | 0.266667 |
| 24 | 255.933333 | 266.133333 | 256.033333 | 266.000000 | 10.200000 | 9.966667 | 0.100000 | 0.100000 | -0.133333 | 0.133333 | -0.233333 | 0.233333 |
| 25 | 270.600000 | 285.600000 | 270.800000 | 283.233333 | 15.000000 | 12.433333 | 0.200000 | 0.200000 | -2.366667 | 2.366667 | -2.566667 | 2.566667 |
| 26 | 291.300000 | 309.566667 | 291.366667 | 309.566667 | 18.266667 | 18.200000 | 0.066667 | 0.066667 | 0.000000 | 0.000000 | -0.066667 | 0.066667 |
| 27 | 312.366667 | 342.433333 | 312.566667 | 342.333333 | 30.066667 | 29.766667 | 0.200000 | 0.200000 | -0.100000 | 0.100000 | -0.300000 | 0.300000 |
| 28 | 345.800000 | 355.566667 | 346.033333 | 355.566667 | 9.766667 | 9.533333 | 0.233333 | 0.233333 | 0.000000 | 0.000000 | -0.233333 | 0.233333 |
| 29 | 362.000000 | 367.333333 | 362.366667 | 365.566667 | 5.333333 | 3.200000 | 0.366667 | 0.366667 | -1.766667 | 1.766667 | -2.133333 | 2.133333 |
| 30 | 369.000000 | 373.033333 | — | — | 4.033333 | — | — | — | — | — | — | — |
| 31 | 374.333333 | 377.800000 | 374.566667 | 378.233333 | 3.466667 | 3.666667 | 0.233333 | 0.233333 | 0.433333 | 0.433333 | 0.200000 | 0.200000 |
| 32 | 378.666667 | 381.566667 | 379.233333 | 381.566667 | 2.900000 | 2.333333 | 0.566667 | 0.566667 | 0.000000 | 0.000000 | -0.566667 | 0.566667 |
| 33 | 384.533333 | 402.866667 | 384.700000 | 403.033333 | 18.333333 | 18.333333 | 0.166667 | 0.166667 | 0.166667 | 0.166667 | 0.000000 | 0.000000 |
| 34 | 418.566667 | 422.400000 | 418.900000 | 421.833333 | 3.833333 | 2.933333 | 0.333333 | 0.333333 | -0.566667 | 0.566667 | -0.900000 | 0.900000 |
| 35 | 423.300000 | 438.966667 | 429.333333 | 437.566667 | 15.666667 | 8.233333 | 6.033333 | 6.033333 | -1.400000 | 1.400000 | -7.433333 | 7.433333 |
| 36 | 439.966667 | 464.200000 | 440.033333 | 464.033333 | 24.233333 | 24.000000 | 0.066667 | 0.066667 | -0.166667 | 0.166667 | -0.233333 | 0.233333 |
| 37 | 472.000000 | 474.466667 | — | — | 2.466667 | — | — | — | — | — | — | — |
| 38 | 476.233333 | 499.433333 | 476.566667 | 500.733333 | 23.200000 | 24.166667 | 0.333333 | 0.333333 | 1.300000 | 1.300000 | 0.966667 | 0.966667 |
| 39 | 504.733333 | 511.633333 | 504.866667 | 511.433333 | 6.900000 | 6.566667 | 0.133333 | 0.133333 | -0.200000 | 0.200000 | -0.333333 | 0.333333 |
| 40 | 513.733333 | 522.500000 | — | — | 8.766667 | — | — | — | — | — | — | — |
| 41 | 530.400000 | 538.466667 | 530.566667 | 538.433333 | 8.066667 | 7.866667 | 0.166667 | 0.166667 | -0.033333 | 0.033333 | -0.200000 | 0.200000 |
| 42 | 539.866667 | 549.266667 | 541.000000 | 549.466667 | 9.400000 | 8.466667 | 1.133333 | 1.133333 | 0.200000 | 0.200000 | -0.933333 | 0.933333 |
| 43 | 554.700000 | 589.300000 | — | — | 34.600000 | — | — | — | — | — | — | — |
| 44 | 598.933333 | 607.233333 | 599.366667 | 607.366667 | 8.300000 | 8.000000 | 0.433333 | 0.433333 | 0.133333 | 0.133333 | -0.300000 | 0.300000 |
| 45 | 608.666667 | 615.100000 | 608.866667 | 614.566667 | 6.433333 | 5.700000 | 0.200000 | 0.200000 | -0.533333 | 0.533333 | -0.733333 | 0.733333 |
| 46 | 616.500000 | 627.900000 | 616.666667 | 627.700000 | 11.400000 | 11.033333 | 0.166667 | 0.166667 | -0.200000 | 0.200000 | -0.366667 | 0.366667 |
| 47 | 630.133333 | 640.900000 | 630.300000 | 638.766667 | 10.766667 | 8.466667 | 0.166667 | 0.166667 | -2.133333 | 2.133333 | -2.300000 | 2.300000 |
| 48 | 645.633333 | 661.700000 | 647.433333 | 661.566667 | 16.066667 | 14.133333 | 1.800000 | 1.800000 | -0.133333 | 0.133333 | -1.933333 | 1.933333 |
| 49 | 663.933333 | 677.566667 | 664.233333 | 677.566667 | 13.633333 | 13.333333 | 0.300000 | 0.300000 | 0.000000 | 0.000000 | -0.300000 | 0.300000 |
| 50 | 683.733333 | 693.800000 | 683.900000 | 693.666667 | 10.066667 | 9.766667 | 0.166667 | 0.166667 | -0.133333 | 0.133333 | -0.300000 | 0.300000 |
| 51 | 697.400000 | 703.466667 | 697.433333 | 701.966667 | 6.066667 | 4.533333 | 0.033333 | 0.033333 | -1.500000 | 1.500000 | -1.533333 | 1.533333 |
| 52 | 704.833333 | 727.566667 | 705.366667 | 728.066667 | 22.733333 | 22.700000 | 0.533333 | 0.533333 | 0.500000 | 0.500000 | -0.033333 | 0.033333 |
| 53 | 731.266667 | 750.333333 | 730.833333 | 748.933333 | 19.066667 | 18.100000 | -0.433333 | 0.433333 | -1.400000 | 1.400000 | -0.966667 | 0.966667 |
| 54 | 751.300000 | 763.966667 | 751.666667 | 762.766667 | 12.666667 | 11.100000 | 0.366667 | 0.366667 | -1.200000 | 1.200000 | -1.566667 | 1.566667 |
| 55 | 765.333333 | 767.766667 | — | — | 2.433333 | — | — | — | — | — | — | — |
| 56 | 769.933333 | 778.866667 | 770.100000 | 775.133333 | 8.933333 | 5.033333 | 0.166667 | 0.166667 | -3.733333 | 3.733333 | -3.900000 | 3.900000 |
| 57 | 779.933333 | 783.300000 | 780.300000 | 783.233333 | 3.366667 | 2.933333 | 0.366667 | 0.366667 | -0.066667 | 0.066667 | -0.433333 | 0.433333 |
| 58 | 787.800000 | 795.566667 | 788.033333 | 795.533333 | 7.766667 | 7.500000 | 0.233333 | 0.233333 | -0.033333 | 0.033333 | -0.266667 | 0.266667 |
| 59 | 798.866667 | 804.500000 | 799.633333 | 804.466667 | 5.633333 | 4.833333 | 0.766667 | 0.766667 | -0.033333 | 0.033333 | -0.800000 | 0.800000 |
| 60 | 806.133333 | 820.633333 | 812.400000 | 820.866667 | 14.500000 | 8.466667 | 6.266667 | 6.266667 | 0.233333 | 0.233333 | -6.033333 | 6.033333 |
| 61 | 824.400000 | 835.700000 | 824.533333 | 835.166667 | 11.300000 | 10.633333 | 0.133333 | 0.133333 | -0.533333 | 0.533333 | -0.666667 | 0.666667 |
| 62 | 839.166667 | 845.733333 | 839.766667 | 845.666667 | 6.566667 | 5.900000 | 0.600000 | 0.600000 | -0.066667 | 0.066667 | -0.666667 | 0.666667 |
| 63 | 849.300000 | 854.266667 | 849.466667 | 854.500000 | 4.966667 | 5.033333 | 0.166667 | 0.166667 | 0.233333 | 0.233333 | 0.066667 | 0.066667 |
| 64 | 855.066667 | 862.000000 | 856.166667 | 862.533333 | 6.933333 | 6.366667 | 1.100000 | 1.100000 | 0.533333 | 0.533333 | -0.566667 | 0.566667 |
| 65 | 864.800000 | 877.100000 | 864.966667 | 872.566667 | 12.300000 | 7.600000 | 0.166667 | 0.166667 | -4.533333 | 4.533333 | -4.700000 | 4.700000 |
| 66 | 885.100000 | 887.566667 | 885.266667 | 887.400000 | 2.466667 | 2.133333 | 0.166667 | 0.166667 | -0.166667 | 0.166667 | -0.333333 | 0.333333 |
| 67 | 889.633333 | 894.866667 | 889.833333 | 895.500000 | 5.233333 | 5.666667 | 0.200000 | 0.200000 | 0.633333 | 0.633333 | 0.433333 | 0.433333 |
| 68 | 901.300000 | 915.200000 | 901.400000 | 914.500000 | 13.900000 | 13.100000 | 0.100000 | 0.100000 | -0.700000 | 0.700000 | -0.800000 | 0.800000 |
| 69 | 915.600000 | 942.500000 | 916.300000 | 939.466667 | 26.900000 | 23.166667 | 0.700000 | 0.700000 | -3.033333 | 3.033333 | -3.733333 | 3.733333 |
| 70 | 945.700000 | 949.800000 | 945.766667 | 949.266667 | 4.100000 | 3.500000 | 0.066667 | 0.066667 | -0.533333 | 0.533333 | -0.600000 | 0.600000 |
| 71 | 951.233333 | 954.100000 | 951.433333 | 954.066667 | 2.866667 | 2.633333 | 0.200000 | 0.200000 | -0.033333 | 0.033333 | -0.233333 | 0.233333 |
| 72 | 956.100000 | 970.133333 | 956.100000 | 968.000000 | 14.033333 | 11.900000 | 0.000000 | 0.000000 | -2.133333 | 2.133333 | -2.133333 | 2.133333 |
| 73 | 974.700000 | 989.900000 | 974.900000 | 989.033333 | 15.200000 | 14.133333 | 0.200000 | 0.200000 | -0.866667 | 0.866667 | -1.066667 | 1.066667 |
| 74 | 990.533333 | 1011.400000 | 990.700000 | 1009.866667 | 20.866667 | 19.166667 | 0.166667 | 0.166667 | -1.533333 | 1.533333 | -1.700000 | 1.700000 |
| 75 | 1013.166667 | 1017.066667 | 1013.366667 | 1017.033333 | 3.900000 | 3.666667 | 0.200000 | 0.200000 | -0.033333 | 0.033333 | -0.233333 | 0.233333 |
| 76 | 1017.800000 | 1027.233333 | 1021.000000 | 1027.066667 | 9.433333 | 6.066667 | 3.200000 | 3.200000 | -0.166667 | 0.166667 | -3.366667 | 3.366667 |
| 77 | 1042.566667 | 1050.433333 | 1042.700000 | 1050.733333 | 7.866667 | 8.033333 | 0.133333 | 0.133333 | 0.300000 | 0.300000 | 0.166667 | 0.166667 |
| 78 | 1051.866667 | 1056.433333 | 1052.800000 | 1057.500000 | 4.566667 | 4.700000 | 0.933333 | 0.933333 | 1.066667 | 1.066667 | 0.133333 | 0.133333 |
| 79 | 1063.200000 | 1067.800000 | 1063.700000 | 1067.300000 | 4.600000 | 3.600000 | 0.500000 | 0.500000 | -0.500000 | 0.500000 | -1.000000 | 1.000000 |
| 80 | 1068.200000 | 1072.233333 | 1069.900000 | 1072.500000 | 4.033333 | 2.600000 | 1.700000 | 1.700000 | 0.266667 | 0.266667 | -1.433333 | 1.433333 |
| 81 | 1075.166667 | 1087.866667 | 1075.266667 | 1088.033333 | 12.700000 | 12.766667 | 0.100000 | 0.100000 | 0.166667 | 0.166667 | 0.066667 | 0.066667 |
| 82 | 1088.766667 | 1112.533333 | 1095.633333 | 1112.333333 | 23.766667 | 16.700000 | 6.866667 | 6.866667 | -0.200000 | 0.200000 | -7.066667 | 7.066667 |
| 83 | 1113.733333 | 1123.533333 | 1117.033333 | 1123.933333 | 9.800000 | 6.900000 | 3.300000 | 3.300000 | 0.400000 | 0.400000 | -2.900000 | 2.900000 |
| 84 | 1128.166667 | 1135.233333 | 1129.833333 | 1135.366667 | 7.066667 | 5.533333 | 1.666667 | 1.666667 | 0.133333 | 0.133333 | -1.533333 | 1.533333 |
| 85 | 1136.700000 | 1144.300000 | — | — | 7.600000 | — | — | — | — | — | — | — |
| 86 | 1145.133333 | 1150.633333 | 1145.533333 | 1151.133333 | 5.500000 | 5.600000 | 0.400000 | 0.400000 | 0.500000 | 0.500000 | 0.100000 | 0.100000 |
| 87 | 1151.533333 | 1155.600000 | 1151.533333 | 1155.533333 | 4.066667 | 4.000000 | 0.000000 | 0.000000 | -0.066667 | 0.066667 | -0.066667 | 0.066667 |
| 88 | 1157.466667 | 1169.766667 | 1157.933333 | 1169.566667 | 12.300000 | 11.633333 | 0.466667 | 0.466667 | -0.200000 | 0.200000 | -0.666667 | 0.666667 |
| 89 | 1177.200000 | 1183.633333 | 1177.333333 | 1183.400000 | 6.433333 | 6.066667 | 0.133333 | 0.133333 | -0.233333 | 0.233333 | -0.366667 | 0.366667 |
| 90 | 1187.966667 | 1210.766667 | 1188.066667 | 1210.633333 | 22.800000 | 22.566667 | 0.100000 | 0.100000 | -0.133333 | 0.133333 | -0.233333 | 0.233333 |
| 91 | 1216.333333 | 1223.666667 | 1216.466667 | 1223.833333 | 7.333333 | 7.366667 | 0.133333 | 0.133333 | 0.166667 | 0.166667 | 0.033333 | 0.033333 |
| 92 | 1225.666667 | 1230.533333 | 1225.966667 | 1230.766667 | 4.866667 | 4.800000 | 0.300000 | 0.300000 | 0.233333 | 0.233333 | -0.066667 | 0.066667 |
| 93 | 1232.933333 | 1237.733333 | 1234.200000 | 1237.300000 | 4.800000 | 3.100000 | 1.266667 | 1.266667 | -0.433333 | 0.433333 | -1.700000 | 1.700000 |

### Secondary coarse/outcome annotations: full supplied baseline and comparison

[Test10_Full.csv](/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/dataset/Test10_Full/Test10_Full.csv) contains **101 data rows**, **96 nonblank intervals**, blank row IDs **[97, 98, 99, 100, 101]**. This separate reference differs from the 93-interval primary timing table. The same unchanged predictions and matcher give secondary precision **90.816%**, recall **92.708%**, F1 **91.753%**; this reference-sensitivity analysis does not replace the primary benchmark. No labels, times or predictions were fitted or repaired.

| Metric | Ground-truth / identical-boundary ideal | Observed predictions | Difference from ideal |
|---|---|---|---|
| Ground-truth intervals | 96 | 96 | 0 |
| Prediction count | 96 | 98 | 2 |
| TP / matched | 96 | 89 | -7 |
| FP | 0 | 9 | 9 |
| FN / missed | 0 | 7 | 7 |
| precision | 1 | 0.908163 | -0.091837 |
| recall | 1 | 0.927083 | -0.072917 |
| f1 | 1 | 0.917526 | -0.082474 |
| Mean matched IoU | 1 | 0.822719 | -0.177281 |
| Median matched IoU | 1 | 0.858209 | -0.141791 |
| Minimum matched IoU | 1 | 0.503401 | -0.496599 |

| Matched IoU strictly greater than | Ideal % | Observed % |
|---|---|---|
| 0.5 | 100 | 100.000000 |
| 0.75 | 100 | 76.404494 |
| 0.9 | 100 | 29.213483 |
| 0.95 | 100 | 11.235955 |

| Error / units | MAE (ideal 0) | Median \|error\| | RMSE (ideal 0) | Max \|error\| | P90 \|error\| | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 21.022472 | 16.000000 | 36.147793 | 216.000000 | 31.000000 | 17.719101 | 14.000000 |
| end_frame | 20.887640 | 16.000000 | 29.776131 | 163.000000 | 43.000000 | 6.213483 | 11.000000 |
| start_time_sec | 0.700749 | 0.533333 | 1.204926 | 7.200000 | 1.033333 | 0.590637 | 0.466667 |
| end_time_sec | 0.696255 | 0.533333 | 0.992538 | 5.433333 | 1.433333 | 0.207116 | 0.366667 |
| duration_sec | 0.844944 | 0.500000 | 1.387954 | 6.700000 | 1.673333 | -0.383521 | -0.133333 |

| Boundary | ±frames | ±seconds | Within | Matched denominator | Within / matched | All-GT denominator | Within / all GT | Ideal |
|---|---|---|---|---|---|---|---|---|
| start | 1 | 0.033333 | 6 | 89 | 6.742% | 96 | 6.250% | 100% |
| start | 3 | 0.100000 | 10 | 89 | 11.236% | 96 | 10.417% | 100% |
| start | 5 | 0.166667 | 15 | 89 | 16.854% | 96 | 15.625% | 100% |
| start | 10 | 0.333333 | 28 | 89 | 31.461% | 96 | 29.167% | 100% |
| start | 15 | 0.500000 | 44 | 89 | 49.438% | 96 | 45.833% | 100% |
| start | 30 | 1.000000 | 79 | 89 | 88.764% | 96 | 82.292% | 100% |
| end | 1 | 0.033333 | 8 | 89 | 8.989% | 96 | 8.333% | 100% |
| end | 3 | 0.100000 | 10 | 89 | 11.236% | 96 | 10.417% | 100% |
| end | 5 | 0.166667 | 11 | 89 | 12.360% | 96 | 11.458% | 100% |
| end | 10 | 0.333333 | 24 | 89 | 26.966% | 96 | 25.000% | 100% |
| end | 15 | 0.500000 | 44 | 89 | 49.438% | 96 | 45.833% | 100% |
| end | 30 | 1.000000 | 73 | 89 | 82.022% | 96 | 76.042% | 100% |

| Cross-reference timing diagnostic | Value |
|---|---|
| Primary-to-coarse eligible matched intervals | 86 |
| Primary intervals unmatched to coarse reference | [4,9,15,26,37,40,43] |
| Coarse rows unmatched to primary reference | [4,22,25,33,34,38,41,44,45,84] |
| Primary/coarse matched mean IoU | 0.830157 |

| C source row | Supplied start | Supplied end | Supplied winner | Supplied A:B score | Supplied shot / ball_types | Win reason | Lose reason | Matched P | IoU | Δstart s | Δend s | Δduration s | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0:04 | 0:18 | Player A | 1:0 | Smash | Winner Shot | Opponent Failed to Return | 1 | 0.871460 | 0.666667 | 1.300000 | 0.633333 | matched |
| 2 | 0:21 | 0:23 | Player A | 2:0 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 2 | 0.506494 | 0.700000 | 0.566667 | -0.133333 | matched |
| 3 | 0:27 | 0:32 | Player B | 2:1 | Lift Shot | Winner Shot | Opponent Failed to Return | 3 | 0.795031 | 0.733333 | 0.366667 | -0.366667 | matched |
| 4 | 0:36 | 0:38 | Player B | 2:2 | Drop Shot | Opponent Out of Bounds | Hit Out of Bounds | — | — | — | — | — | missed |
| 5 | 0:42 | 0:45 | Player A | 3:2 | Net Shot | Opponent Out of Bounds | Hit Out of Bounds | 5 | 0.719626 | 0.433333 | 0.566667 | 0.133333 | matched |
| 6 | 0:51 | 0:55 | Player A | 4:2 | Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 6 | 0.633333 | 0.700000 | -0.766667 | -1.466667 | matched |
| 7 | 0:57 | 1:09 | Player B | 4:3 | Smash | Opponent Hit the Net | Hit the Net | 7 | 0.915567 | 0.433333 | 0.633333 | 0.200000 | matched |
| 8 | 1:14 | 1:19 | Player A | 5:3 | Slice Shot | Winner Shot | Opponent Failed to Return | 8 | 0.730570 | 0.300000 | 1.433333 | 1.133333 | matched |
| 9 | 1:24 | 1:45 | Player B | 5:4 | Drop Shot | Opponent Hit the Net | Hit the Net | 9 | 0.908012 | 0.600000 | 1.466667 | 0.866667 | matched |
| 10 | 1:52 | 2:04 | Player A | 6:4 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 10 | 0.932065 | 0.566667 | 0.266667 | -0.300000 | matched |
| 11 | 2:06 | 2:17 | Player A | 7:4 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 11 | 0.970588 | -0.333333 | 0.000000 | 0.333333 | matched |
| 12 | 2:18 | 2:27 | Player B | 7:5 | Net Shot | Opponent Hit the Net | Hit the Net | 12 | 0.885185 | 0.533333 | -0.500000 | -1.033333 | matched |
| 13 | 2:28 | 2:31 | Player A | 8:5 | Block Shot | Opponent Hit the Net | Hit the Net | 13 | 0.788889 | 0.633333 | 0.000000 | -0.633333 | matched |
| 14 | 2:39 | 2:43 | Player A | 9:5 | Smash | Winner Shot | Opponent Failed to Return | 14 | 0.751724 | 0.366667 | 0.833333 | 0.466667 | matched |
| 15 | 2:52 | 3:00 | Player A | 10:5 | Drive Shot | Opponent Hit the Net | Hit the Net | 15 | 0.796364 | 0.700000 | 1.166667 | 0.466667 | matched |
| 16 | 3:03 | 3:14 | Player B | 10:6 | Lift Shot | Winner Shot | Opponent Failed to Return | 16 | 0.921788 | -0.700000 | 0.233333 | 0.933333 | matched |
| 17 | 3:18 | 3:22 | Player A | 11:6 | Push Shot | Winner Shot | Opponent Failed to Return | 17 | 0.858209 | 0.166667 | 0.466667 | 0.300000 | matched |
| 18 | 3:23 | 3:26 | Player B | 11:7 | Net Shot | Opponent Hit the Net | Hit the Net | 18 | 0.711111 | 0.833333 | -0.033333 | -0.866667 | matched |
| 19 | 3:34 | 3:38 | Player A | 12:7 | Slice Shot | Opponent Hit the Net | Hit the Net | 19 | 0.811024 | 0.566667 | 0.233333 | -0.333333 | matched |
| 20 | 3:42 | 3:51 | Player B | 12:8 | Smash | Winner Shot | Opponent Failed to Return | 20 | 0.876289 | 0.500000 | 0.700000 | 0.200000 | matched |
| 21 | 3:54 | 4:04 | Player B | 12:9 | Drop Shot | Opponent Hit the Net | Hit the Net | 21 | 0.882353 | 0.500000 | 0.766667 | 0.266667 | matched |
| 22 | 4:07 | 4:10 | Player B | 12:10 | Drive Shot | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 23 | 4:15 | 4:26 | Player B | 12:11 | Clear Shot | Winner Shot | Opponent Failed to Return | 22 | 0.906061 | 1.033333 | 0.000000 | -1.033333 | matched |
| 24 | 4:30 | 4:44 | Player A | 13:11 | Jump Smash | Winner Shot | Opponent Failed to Return | 23 | 0.888095 | 0.800000 | -0.766667 | -1.566667 | matched |
| 25 | 4:59 | 5:07 | Player A | 14:11 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | — | — | — | — | — | missed |
| 26 | 5:12 | 5:42 | Player A | 15:11 | Slice Shot | Winner Shot | Opponent Failed to Return | 25 | 0.970330 | 0.566667 | 0.333333 | -0.233333 | matched |
| 27 | 5:45 | 5:56 | Player B | 15:12 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 26 | 0.866667 | 1.033333 | -0.433333 | -1.466667 | matched |
| 28 | 6:02 | 6:05 | Player A | 16:12 | Net Shot | Opponent Hit the Net | Hit the Net | 27 | 0.738318 | 0.366667 | 0.566667 | 0.200000 | matched |
| 29 | 6:08 | 6:12 | Player A | 17:12 | Drop Shot | Opponent Out of Bounds | Hit Out of Bounds | — | — | — | — | — | missed |
| 30 | 6:14 | 6:18 | Player A | 18:12 | Smash | Winner Shot | Opponent Failed to Return | 29 | 0.811024 | 0.566667 | 0.233333 | -0.333333 | matched |
| 31 | 6:19 | 6:22 | Player A | 19:12 | Block Shot | Opponent Hit the Net | Hit the Net | 30 | 0.777778 | 0.233333 | -0.433333 | -0.666667 | matched |
| 32 | 6:24 | 6:43 | Player A | 20:12 | Drive Shot | Winner Shot | Opponent Failed to Return | 31 | 0.961471 | 0.700000 | 0.033333 | -0.666667 | matched |
| 33 | 6:47 | 6:49 | Player A | 21:12 | Net Shot | Winner Shot | Opponent Failed to Return | 32 | 0.845070 | -0.033333 | 0.333333 | 0.366667 | matched |
| 34 | 6:50 | 6:56 | Player B | 21:13 | Clear Shot | Winner Shot | Opponent Failed to Return | 33 | 0.877778 | 0.433333 | -0.300000 | -0.733333 | matched |
| 35 | 6:58 | 7:01 | Player B | 21:14 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 34 | 0.547826 | 0.900000 | 0.833333 | -0.066667 | matched |
| 36 | 7:06 | 7:17 | Player A | 22:14 | Slice Shot | Opponent Hit the Net | Hit the Net | 35 | 0.662824 | 3.333333 | 0.566667 | -2.766667 | matched |
| 37 | 7:21 | 7:44 | Player B | 22:15 | Drop Shot | Opponent Hit the Net | Hit the Net | 36 | 0.958333 | -0.966667 | 0.033333 | 1.000000 | matched |
| 38 | 7:48 | 7:55 | Player A | 23:15 | Smash | Opponent Hit the Net | Hit the Net | 37 | 0.771429 | 0.833333 | -0.766667 | -1.600000 | matched |
| 39 | 7:58 | 8:19 | Player A | 24:15 | Drive Shot | Opponent Hit the Net | Hit the Net | 38 | 0.868966 | -1.433333 | 1.733333 | 3.166667 | matched |
| 40 | 8:24 | 8:30 | Player A | 25:15 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 39 | 0.690583 | 0.866667 | 1.433333 | 0.566667 | matched |
| 41 | 8:37 | 8:41 | Player B | 25:16 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 40 | 0.503401 | 1.533333 | 0.900000 | -0.633333 | matched |
| 42 | 8:50 | 8:58 | Player B | 25:17 | Clear Shot | Opponent Out of Bounds | Hit Out of Bounds | 41 | 0.881423 | 0.566667 | 0.433333 | -0.133333 | matched |
| 43 | 9:01 | 9:09 | Player B | 25:18 | Drop Shot | Opponent Out of Bounds | Hit Out of Bounds | 42 | 0.944882 | 0.000000 | 0.466667 | 0.466667 | matched |
| 44 | 9:14 | 9:28 | Player B | 25:19 | Net Shot | Opponent Hit the Net | Hit the Net | 43 | 0.912644 | 0.766667 | 0.500000 | -0.266667 | matched |
| 45 | 9:32 | 9:48 | Player A | 26:19 | Smash | Opponent Out of Bounds | Hit Out of Bounds | 45 | 0.533333 | 7.200000 | 0.500000 | -6.700000 | matched |
| 46 | 9:59 | 10:07 | Player A | 27:19 | Drive Shot | Opponent Out of Bounds | Hit Out of Bounds | 46 | 0.912351 | 0.366667 | 0.366667 | 0.000000 | matched |
| 47 | 10:09 | 10:14 | Player A | 28:19 | Slice Shot | Winner Shot | Opponent Failed to Return | 47 | 0.877193 | -0.133333 | 0.566667 | 0.700000 | matched |
| 48 | 10:16 | 10:27 | Player A | 29:19 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 48 | 0.883191 | 0.666667 | 0.700000 | 0.033333 | matched |
| 49 | 10:30 | 10:41 | Player A | 30:19 | Net Shot | Opponent Hit the Net | Hit the Net | 49 | 0.769697 | 0.300000 | -2.233333 | -2.533333 | matched |
| 50 | 10:47 | 11:01 | Player A | 31:19 | Jump Smash | Winner Shot | Opponent Failed to Return | 50 | 0.931350 | 0.433333 | 0.566667 | 0.133333 | matched |
| 51 | 11:04 | 11:18 | Player A | 32:19 | Drop Shot | Opponent Hit the Net | Hit the Net | 51 | 0.952381 | 0.233333 | -0.433333 | -0.666667 | matched |
| 52 | 11:23 | 11:33 | Player B | 32:20 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 52 | 0.853125 | 0.900000 | 0.666667 | -0.233333 | matched |
| 53 | 11:37 | 11:43 | Player A | 33:20 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 53 | 0.755556 | 0.433333 | -1.033333 | -1.466667 | matched |
| 54 | 11:45 | 12:08 | Player A | 34:20 | Smash | Winner Shot | Opponent Failed to Return | 54 | 0.981214 | 0.366667 | 0.066667 | -0.300000 | matched |
| 55 | 12:11 | 12:28 | Player A | 35:20 | Drive Shot | Winner Shot | Opponent Failed to Return | 55 | 0.939227 | -0.166667 | 0.933333 | 1.100000 | matched |
| 56 | 12:31 | 12:43 | Player B | 35:21 | Net Shot | Winner Shot | Opponent Failed to Return | 56 | 0.925000 | 0.666667 | -0.233333 | -0.900000 | matched |
| 57 | 12:45 | 12:47 | Player B | 35:22 | Block Shot | Opponent Out of Bounds | Hit Out of Bounds | — | — | — | — | — | missed |
| 58 | 12:50 | 12:57 | Player A | 36:22 | Slice Shot | Winner Shot | Opponent Failed to Return | 57 | 0.719048 | 0.100000 | -1.866667 | -1.966667 | matched |
| 59 | 13:00 | 13:03 | Player B | 36:23 | Lift Shot | Winner Shot | Opponent Failed to Return | 58 | 0.835052 | 0.300000 | 0.233333 | -0.066667 | matched |
| 60 | 13:08 | 13:15 | Player B | 36:24 | Smash | Winner Shot | Opponent Failed to Return | 59 | 0.924779 | 0.033333 | 0.533333 | 0.500000 | matched |
| 61 | 13:18 | 13:23 | Player A | 37:24 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 60 | 0.520619 | 1.633333 | 1.466667 | -0.166667 | matched |
| 62 | 13:27 | 13:40 | Player B | 37:25 | Clear Shot | Winner Shot | Opponent Failed to Return | 62 | 0.548077 | 5.400000 | 0.866667 | -4.533333 | matched |
| 63 | 13:44 | 13:55 | Player A | 38:25 | Jump Smash | Winner Shot | Opponent Failed to Return | 63 | 0.937313 | 0.533333 | 0.166667 | -0.366667 | matched |
| 64 | 13:59 | 14:05 | Player B | 38:26 | Drive Shot | Winner Shot | Opponent Failed to Return | 64 | 0.785000 | 0.766667 | 0.666667 | -0.100000 | matched |
| 65 | 14:09 | 14:14 | Player A | 39:26 | Drop Shot | Opponent Out of Bounds | Hit Out of Bounds | 65 | 0.824242 | 0.466667 | 0.500000 | 0.033333 | matched |
| 66 | 14:16 | 14:22 | Player A | 40:26 | Net Shot | Winner Shot | Opponent Failed to Return | 66 | 0.892857 | 0.166667 | 0.533333 | 0.366667 | matched |
| 67 | 14:25 | 14:38 | Player B | 40:27 | Smash | Winner Shot | Opponent Failed to Return | 67 | 0.580563 | -0.033333 | -5.433333 | -5.400000 | matched |
| 68 | 14:45 | 14:47 | Player A | 41:27 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 69 | 0.722222 | 0.266667 | 0.400000 | 0.133333 | matched |
| 69 | 14:50 | 14:55 | Player A | 42:27 | Slice Shot | Opponent Hit the Net | Hit the Net | 70 | 0.882353 | -0.166667 | 0.500000 | 0.666667 | matched |
| 70 | 15:01 | 15:15 | Player A | 43:27 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 71 | 0.935714 | 0.400000 | -0.500000 | -0.900000 | matched |
| 71 | 15:16 | 15:42 | Player B | 43:28 | Clear Shot | Winner Shot | Opponent Failed to Return | 72 | 0.891026 | 0.300000 | -2.533333 | -2.833333 | matched |
| 72 | 15:46 | 15:49 | Player B | 43:29 | Drive Shot | Winner Shot | Opponent Failed to Return | 73 | 0.857143 | -0.233333 | 0.266667 | 0.500000 | matched |
| 73 | 15:51 | 15:54 | Player A | 44:29 | Drop Shot | Winner Shot | Opponent Failed to Return | 74 | 0.836957 | 0.433333 | 0.066667 | -0.366667 | matched |
| 74 | 15:56 | 16:10 | Player A | 45:29 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 75 | 0.850000 | 0.100000 | -2.000000 | -2.100000 | matched |
| 75 | 16:14 | 16:28 | Player A | 46:29 | Smash | Winner Shot | Opponent Failed to Return | 76 | 0.871397 | 0.900000 | 1.033333 | 0.133333 | matched |
| 76 | 16:30 | 16:49 | Player A | 47:29 | Net Shot | Opponent Out of Bounds | Hit Out of Bounds | 77 | 0.921141 | 0.700000 | 0.866667 | 0.166667 | matched |
| 77 | 16:53 | 16:57 | Player A | 48:29 | Block Shot | Opponent Hit the Net | Hit the Net | 78 | 0.900826 | 0.366667 | 0.033333 | -0.333333 | matched |
| 78 | 17:00 | 17:06 | Player B | 48:30 | Drive Shot | Opponent Hit the Net | Hit the Net | 79 | 0.707547 | 1.000000 | 1.066667 | 0.066667 | matched |
| 79 | 17:22 | 17:30 | Player A | 49:30 | Slice Shot | Opponent Out of Bounds | Hit Out of Bounds | 80 | 0.835878 | 0.700000 | 0.733333 | 0.033333 | matched |
| 80 | 17:31 | 17:36 | Player A | 50:30 | Smash | Winner Shot | Opponent Failed to Return | — | — | — | — | — | missed |
| 81 | 17:43 | 17:47 | Player A | 51:30 | Net Shot | Opponent Hit the Net | Hit the Net | 82 | 0.767442 | 0.700000 | 0.300000 | -0.400000 | matched |
| 82 | 17:49 | 17:52 | Player B | 51:31 | Push Shot | Winner Shot | Opponent Failed to Return | 83 | 0.600000 | 0.900000 | 0.500000 | -0.400000 | matched |
| 83 | 17:55 | 18:08 | Player B | 51:32 | Drop Shot | Opponent Hit the Net | Hit the Net | 84 | 0.976982 | 0.266667 | 0.033333 | -0.233333 | matched |
| 84 | 18:10 | 18:14 | Player A | 52:32 | Jump Smash | Winner Shot | Opponent Failed to Return | 85 | 0.869565 | -0.233333 | 0.366667 | 0.600000 | matched |
| 85 | 18:16 | 18:32 | Player A | 53:32 | Clear Shot | Winner Shot | Opponent Failed to Return | 86 | 0.958084 | -0.366667 | 0.333333 | 0.700000 | matched |
| 86 | 18:37 | 18:43 | Player A | 54:32 | Net Shot | Opponent Hit the Net | Hit the Net | 87 | 0.860577 | 0.033333 | 0.933333 | 0.900000 | matched |
| 87 | 18:48 | 18:55 | Player B | 54:33 | Lift Shot | Opponent Out of Bounds | Hit Out of Bounds | 88 | 0.701357 | 1.833333 | 0.366667 | -1.466667 | matched |
| 88 | 18:57 | 19:04 | Player A | 55:33 | Slice Shot | Opponent Hit the Net | Hit the Net | — | — | — | — | — | missed |
| 89 | 19:05 | 19:10 | Player B | 55:34 | Push Shot | Opponent Out of Bounds | Hit Out of Bounds | 91 | 0.728261 | 0.533333 | 1.133333 | 0.600000 | matched |
| 90 | 19:11 | 19:16 | Player A | 56:34 | Smash | Winner Shot | Opponent Failed to Return | 92 | 0.800000 | 0.533333 | -0.466667 | -1.000000 | matched |
| 91 | 19:18 | 19:30 | Player B | 56:35 | Drive Shot | Winner Shot | Opponent Failed to Return | 93 | 0.958564 | -0.066667 | -0.433333 | -0.366667 | matched |
| 92 | 19:37 | 19:44 | Player B | 56:36 | Drop Shot | Winner Shot | Opponent Failed to Return | 94 | 0.866667 | 0.333333 | -0.600000 | -0.933333 | matched |
| 93 | 19:48 | 20:10 | Player A | 57:36 | Jump Smash | Winner Shot | Opponent Failed to Return | 95 | 0.969072 | 0.066667 | 0.633333 | 0.566667 | matched |
| 94 | 20:15 | 20:23 | Player A | 58:36 | Net Shot | Winner Shot | Opponent Failed to Return | 96 | 0.739623 | 1.466667 | 0.833333 | -0.633333 | matched |
| 95 | 20:26 | 20:30 | Player A | 59:36 | Push Shot | Winner Shot | Opponent Failed to Return | 97 | 0.833333 | -0.033333 | 0.766667 | 0.800000 | matched |
| 96 | 20:34 | 20:37 | Player B | 59:37 | Block Shot | Opponent Hit the Net | Hit the Net | 98 | 0.848485 | 0.200000 | 0.300000 | 0.100000 | matched |

| Secondary-reference unmatched P | Start f | End f | Start s | End s |
|---|---|---|---|---|
| 4 | 1091 | 1199 | 36.366667 | 39.966667 |
| 24 | 8741 | 9287 | 291.366667 | 309.566667 |
| 28 | 11073 | 11131 | 369.100000 | 371.033333 |
| 44 | 17174 | 17340 | 572.466667 | 578.000000 |
| 61 | 24185 | 24347 | 806.166667 | 811.566667 |
| 68 | 26206 | 26355 | 873.533333 | 878.500000 |
| 81 | 31584 | 31725 | 1052.800000 | 1057.500000 |
| 89 | 34122 | 34223 | 1137.400000 | 1140.766667 |
| 90 | 34246 | 34335 | 1141.533333 | 1144.500000 |

| Supplied semantic label inventory | Counts |
|---|---|
| win_point_player | {"Player A":59,"Player B":37} |
| ball_types | {"Smash":13,"Push Shot":14,"Lift Shot":8,"Drop Shot":11,"Net Shot":13,"Drive Shot":11,"Slice Shot":9,"Clear Shot":7,"Block Shot":5,"Jump Smash":5} |
| roundscore_A | {"1":1,"2":3,"3":1,"4":2,"5":2,"6":1,"7":2,"8":1,"9":1,"10":2,"11":2,"12":5,"13":1,"14":1,"15":2,"16":1,"17":1,"18":1,"19":1,"20":1,"21":3,"22":2,"23":1,"24":1,"25":5,"26":1,"27":1,"28":1,"29":1,"30":1,"31":1,"32":2,"33":1,"34":1,"35":3,"36":3,"37":2,"38":2,"39":1,"40":2,"41":1,"42":1,"43":3,"44":1,"45":1,"46":1,"47":1,"48":2,"49":1,"50":1,"51":3,"52":1,"53":1,"54":2,"55":2,"56":3,"57":1,"58":1,"59":2} |
| roundscore_B | {"0":2,"1":1,"2":3,"3":2,"4":3,"5":4,"6":2,"7":2,"8":1,"9":1,"10":1,"11":4,"12":7,"13":1,"14":2,"15":4,"16":1,"17":1,"18":1,"19":8,"20":4,"21":1,"22":2,"23":1,"24":2,"25":2,"26":3,"27":4,"28":1,"29":6,"30":4,"31":1,"32":4,"33":2,"34":2,"35":1,"36":4,"37":1} |

The supplied winner/score/shot fields are reproduced above exactly as source strings, including missing values and taxonomy variation. The temporal crosswalk does not establish named player/team equivalence, certified point identity, or exhaustive shot labels. Current rally winners are unknown and hitter identities are anonymous; outcome/score-sequence accuracy and per-shot confusion therefore remain unscorable, rather than being reported as verified model correctness.

### Component-level observed output versus available ground truth

| Coverage diagnostic | Numerator | Denominator | Coverage | Ground-truth accuracy available? |
|---|---|---|---|---|
| Raw shuttle present / source frames | 25049 | 37133 | 67.458% | No reviewed frame/person/contact labels |
| Detector-executed / source frames | 15535 | 37133 | 41.836% | No reviewed frame/person/contact labels |
| Fresh detector-matched person rows / person rows | 30799 | 72858 | 42.273% | No reviewed frame/person/contact labels |
| Current pose rows / person rows | 58682 | 72858 | 80.543% | No reviewed frame/person/contact labels |
| Current racket rows / person rows | 27103 | 72858 | 37.200% | No reviewed frame/person/contact labels |

| All component coverage counts | Value |
|---|---|
| frames | 37133 |
| raw_shuttle_present | 25049 |
| detector_executed_frames | 15535 |
| person_rows | 72858 |
| scene_telemetry_present | 3649 |
| scene_raw_hypotheses | 54 |
| actual_content_epoch_increments | 53 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 30799 |
| person_propagated_or_unmatched | 42059 |
| pose_present_rows | 58682 |
| pose_current_source_rows | 58682 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 27883 |
| racket_present_rows | 27103 |
| racket_current_source_rows | 27103 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 54 |
| scene_positive_correspondence_vetoes | 1 |
| scene_current_detector_probes | 54 |

#### Frame/component categories

| Field | Observed value |
|---|---|
| view | {"main":36787,"none":346} |
| calibration_state | {"REACQUIRING":48,"VALID":36739,"LOST":346} |
| player_population | {"0":511,"2":36236,"1":386} |
| association_status | {"missing":11738,"observed":25028,"invalid":346,"ambiguous":21} |
| association_reason | {"no_accepted_raw_observation":11738,"fresh_selection_retained":25028,"image_view_invalid":346,"coobserved_competing_static_hypothesis":21} |
| scene_raw_status | {"unknown":108,"measured":3487,"hypothesis":54} |
| person_detector_match | {"True":30799,"False":42059} |
| person_identity_method | {"bytetrack_v1":72858} |
| scene_decision | {"barrier":53,"no_barrier":1} |
| scene_decision_reason | {"raw_change_and_current_layout_discontinuity":53,"complete_current_layout_correspondence":1} |

#### Live event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 262 |
| scene | 7 |
| participant_observation | 391 |
| format_decision | 1 |
| rally_start | 98 |
| stroke | 1090 |
| contact | 1090 |
| rally_end | 98 |
| identity_ambiguity | 84 |
| shuttle_turn | 38 |
| broadcast_score | 1117 |
| match_phase | 1 |
| highlight | 5 |

#### Append-only event counts

| Field | Observed value |
|---|---|
| calibration | 1 |
| activity_interval | 262 |
| scene | 7 |
| participant_observation | 391 |
| format_decision | 1 |
| rally_start | 188 |
| contact | 2304 |
| stroke | 1114 |
| rally_end | 98 |
| identity_ambiguity | 84 |
| shuttle_turn | 38 |
| broadcast_score | 1117 |
| match_phase | 1 |
| highlight | 5 |

#### All observed event categories

| Field | Observed value |
|---|---|
| event_status | {"confirmed":3672,"provisional":611} |
| stroke_actor | {"unknown":1090} |
| stroke_physical_event_status | {"insufficient":553,"probable":146,"ambiguous":391} |
| stroke_contact_status | {"estimated":1090} |
| stroke_classification_status | {"unknown":804,"estimated":286} |
| stroke_stroke | {"unknown":804,"lift":48,"push":136,"net_shot":44,"drop":39,"drive":8,"clear":10,"rush":1} |
| stroke_attribution_reason | {"nearest_proximity":1086,"ambiguous_proximity":4} |
| stroke_classification_abstention_reason | {"missing_required_evidence":801,"unresolved_initial_contact":3} |
| contact_actor | {"unknown":1090} |
| contact_physical_event_status | {"insufficient":553,"probable":146,"ambiguous":391} |
| contact_contact_status | {"estimated":1090} |
| contact_attribution_reason | {"nearest_proximity":1086,"ambiguous_proximity":4} |
| contact_trajectory_reliability | {"insufficient":268,"probable":559,"ambiguous":263} |
| contact_trajectory_reasons | {"coherent_motion_change_unavailable":268,"supported_launch":137,"supported_turn":422,"association_unresolved":263} |
| contact_impact_reliability | {"insufficient":553,"probable":146,"ambiguous":391} |
| contact_impact_reasons | {"fresh_player_observation_unavailable":553,"coherent_motion_and_fresh_contact_cue":146,"association_unresolved":263,"coherent_motion_change_unavailable":73,"no_fresh_swing_or_racket_overlap":55} |
| contact_attribution_reliability | {"insufficient":739,"probable":351} |
| contact_attribution_reasons | {"fresh_player_observation_unavailable":739,"geometric_attribution_not_verified_identity":351} |
| rally_end_reason | {"cut":19,"gap":36,"stationary":42,"flush":1} |
| rally_phase | {"unknown":5,"match_play":93} |
| rally_official | {"False":56,"True":42} |
| rally_match_format_known | {"True":98} |
| rally_match_format | {"singles":98} |
| rally_winner | {"None":98} |
| rally_score_transition_status | {"unavailable":66,"candidate":32} |
| rally_admission_reason | {"duration_policy":96,"independent_contact_and_observed_motion_witnesses":2} |

#### Track/export counts

| Field | Observed value |
|---|---|
| camera_rows | 37133 |
| player_rows | 72838 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 71891 |
| projected_court_on_propagated_box | 41577 |
| racket_rows | 27085 |
| shuttle_rows | 37133 |

#### Track/export categories

| Field | Observed value |
|---|---|
| player_id | {"None":72838} |
| detector_matched | {"True":30781,"False":42057} |

| Semantic metric | Observed | Baseline comparison / limitation |
|---|---|---|
| Known rally winner output | 0/98 | Supplied coarse winner labels exist; identity/point mapping uncertified |
| Unknown stroke classification | 804/1090 | Coarse one-label-per-rally ball_types is not exhaustive per-shot GT |
| Estimated stroke classification | 286/1090 | Estimated coverage is not class accuracy |
| OCR saved readouts | 1166 | Observed scoreboard rows, not accepted correct points |
| OCR label counts | {"SHI Y.Q.":1166,"AXELSEN":1166} | Raw OCR labels may differ from anonymous Player A/B |
| Tracked invalid geometry frames | 394 | Geometric diagnostics, not labelled location error |
| Session degradation | [{"stage":"player_identity","reason":"osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`"},{"stage":"player_reid","reason":"baseline player_reid provider is unavailable"}] | Identity/ReID unavailability remains recorded; no new models fetched |

### Runtime, resources and every saved stage latency

| Saved resource/runtime metric | Value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 2434314 |
| parent_failure_inclusive_elapsed_s | — |
| parent_failure_inclusive_source_fps | — |
| neural_only_throughput_fps | — |
| model_loading_time_s | — |
| media_ready_time_s | 2.797784 |
| model_staging_time_s | 1.758922 |
| worker_final_cpu_s | 45227.636703 |
| worker_maxrss_bytes | 2881126400 |
| sampled_worker_tree_peak_rss_bytes | 3048800256 |
| sampled_worker_gpu_peak_mib | 2124 |
| sampled_cpu_seconds_max_observed | 45227.040000 |
| sampled_cpu_seconds_last_observed | 45227.040000 |
| sampled_system_available_ram_min_bytes | 101641170944 |
| sample_count | 2140 |
| resource_rows | 2140 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 4433.866512 |
| parent_completed_source_fps | 8.374857 |
| worker_elapsed_s | 4421.865935 |
| worker_source_fps | 8.397586 |
| component_initialization_including_models_s | 8.983048 |

| Stage | Calls | Total wall s | P50 ms/call | P95 ms/call | Minimum ms | Maximum ms | Frame-population sum |
|---|---|---|---|---|---|---|---|
| court | 619 | 207.146754 | 313.787855 | 404.511849 | 265.983936 | 2083.618245 | 37133 |
| content_continuity_and_players | 619 | 1833.586975 | 3316.546564 | 3673.695002 | 50.187807 | 4438.859883 | 37133 |
| shuttle | 616 | 527.034390 | 833.738472 | 1035.624624 | 714.927282 | 1490.508199 | 36953 |
| players | 619 | 117.152488 | 209.445342 | 361.153280 | 0.638503 | 513.304261 | 37133 |
| ocr | 619 | 474.490933 | 720.949175 | 997.316719 | 0.016525 | 1421.220531 | 37133 |

| Runner timing scope | Seconds |
|---|---|
| component_initialization_including_models_s | 8.983048 |
| decode_perception_cache_s | 3421.460045 |

| Additional completed-worker timing | Seconds |
|---|---|
| Perception completion catalogue publication | 7.501287 |
| Worker media ready | 2.797784 |
| Model staging | 1.758922 |

| Actual worker reproducibility metadata | Value |
|---|---|
| Visible Torch devices | [{"logical_index":0,"name":"NVIDIA GeForce GTX 1080 Ti","uuid":"a618f090-66bf-ad80-b0a5-0c91bee61fab"}] |
| CUDA_VISIBLE_DEVICES GPU UUID | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| Prior cached perceptions used | false |
| Worker model manifest SHA256 | b5590b8ff1437945da036b42b01729f521728259a0dfc4c3299a926216ba8df3 |
| Worker staged model pins SHA256 | 7bd228ead493bba31c1417c46346d35e3cd00e1760ba7d7b35485d3babf5219f |

The historical timing key decode_perception_cache_s wraps the runner’s full _perceive call. Its name does not mean this was an observation-cache replay: the completed-worker receipts explicitly record cached_perception_used=false. It is a broad perception wall-time scope, not isolated cache decoding or pure GPU latency.

| Saved disk-use metric | Bytes / count |
|---|---|
| regular_files | 3738 |
| logical_bytes | 1466368526 |
| allocated_bytes | 1474048000 |
| staged_model_bytes | 361041769 |
| perception_cache_bytes | 143061880 |

Wall-time scopes overlap; they are not summable GPU kernel latency. Pure neural-only FPS and isolated model-loading time remain unavailable. For historical Tests 1/2, final worker-local timing/CPU/RSS fields were lost at catalogue publication and stay unavailable; failure-inclusive parent duration is identified explicitly. For normal runs, worker elapsed includes the runner and final catalogue verification. Current-process GPU samples cannot certify per-node ORT placement or true instantaneous memory peaks.

### Reproducibility, logs and annotation-file review

| Binding | Value |
|---|---|
| Normalized numerical profile SHA256 (passive ranges removed) | 2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb |
| Effective profile canonical SHA256 | 2cfc39048692297ed7c6403eb114dc368dfca3cc0db94bcabddd0aa2b54b165b |
| Model identity sets | 1 |
| Runtime identity sets | 1 |
| Actual model identity SHA256 | e3c96b7c2e522fd6efe6106328bebec30137f29b7303fe5e475f8aedea5d2222 |
| Actual runtime identity SHA256 | 81e41f18d858ed37c34ce9d07ae34a34268f27e57c0e5f878e07253be309066f |
| Executed plan | [plan.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10_retry1/protocol/plan.json) |
| Actual completion receipt | [inference.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10_retry1/run/inference.json) |
| Per-rally saved CSV | [per_rally_comparison.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10_retry1/evaluation/per_rally_comparison.csv) |
| Technical analysis | [technical_analysis.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10_retry1/analysis/technical_analysis.json) |
| Full original predictions | [predicted_rallies.csv](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10_retry1/run/predicted_rallies.csv) |

| Annotation file | Role | Data rows | Blank rows | Bytes | Column/schema inventory | SHA256 |
|---|---|---|---|---|---|---|
| Test10_Full.csv | Secondary coarse outcome/time reference | 101 | 5 | 7247 | ["start_time","end_time","win_point_player","win_reason","ball_types","lose_reason","roundscore_A","roundscore_B"] | 2fed7c63a5042dbb6ab01ea4baff57cf0a974947218aaeef0c4a07f721648789 |
| Test10_Full_ball_filled.csv | Auxiliary historical/generated artifact; not certified independent truth | 37133 | 0 | 805209 | ["Frame","X","Y","Visibility","Confidence"] | 8214e4d2922f2f688bd94818c2f145be294b1533c9e3ad615a04b46e07bdddfa |
| Test10_Full_court.json | Auxiliary historical/generated artifact; not certified independent truth | — | — | 537 | ["frame_no","frame_size","corners","net","source"] | b21a927a132a17814093a150eadeece4dcdbece2bedd92525a258c488a56f8f3 |
| Test10_Full_rally.csv | Primary timing reference | 93 | 0 | 6488 | ["Start_Frame","End_Frame","Start_Time_sec","End_Time_sec","Duration_sec","Start_Time","End_Time"] | 509cabed282eac89217d41a7d1b860991456f5d09cab24bb58b2acaba824d0cf |
| player_detections.csv | Auxiliary historical/generated artifact; not certified independent truth | 37133 | 0 | 4112337 | ["frame_no","player_1_x","player_1_y","player_1_conf","player_2_x","player_2_y","player_2_conf"] | 60fa4fbdc65e0ccba41f58e29c95043579fcd3f0d9c8780bcaba57a90b445243 |
| win_predictions.csv | Auxiliary historical/generated artifact; not certified independent truth | 93 | 0 | 11334 | ["rally_idx","start_frame","end_frame","start_time","end_time","winner","loser","win_reason","reason_src","fault_side","fault_src","cnn_class","cnn_conf","cnn_oob","cnn_hn","cnn_wbl","score_Player A","score_Player B"] | 40570229545ce1cf508ee6bb92fb79359e79926d4daa792962364aee7ba83e0c |

| Log | Lines | Warning/error-pattern lines | Distinct observed warning/error messages |
|---|---|---|---|
| analysis.log | 1 | 0 | [] |
| evaluation.log | 0 | 0 | [] |
| prepare.log | 1 | 0 | [] |
| run.execution.log | 34 | 18 | ["2026-11-06 08:55:16 [warning  ] perception.degraded            reason='osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`' stage=player_identity","2026-11-06 08:55:16 [warning  ] perception.degraded            reason='baseline player_reid provider is unavailable' stage=player_reid","[WARNING] 2026-11-06 08:56:10,754 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 08:56:25,422 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 08:56:39,745 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 08:56:54,586 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 08:57:19,019 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 08:57:45,472 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 08:58:12,198 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 09:16:14,526 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 09:16:14,823 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 09:16:18,624 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 09:16:18,892 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 09:52:45,643 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 09:52:52,382 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 09:52:52,666 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 09:52:57,391 [RapidOCR] main.py:164: The text detection result is empty","[WARNING] 2026-11-06 09:53:05,049 [RapidOCR] main.py:164: The text detection result is empty"] |
| run.launch.log | 0 | 0 | [] |
| timestamps.log | 1 | 0 | [] |

Log keyword counts are diagnostic string matches, not failed-inference counts. Tests 1/2 raw original worker logs remain in their source run directories and retain the known final catalogue failure; their independent completion proof is the accepted completion record. All previously completed evaluations remain immutable.

### Duration breakdown for this video

| GT duration bin | GT count | Matched | Missed | Recall | Start MAE f | End MAE f |
|---|---|---|---|---|---|---|
| ≤2 s | 2 | 1 | 1 | 0.500000 | 6.000000 | 3.000000 |
| (2,5] s | 25 | 22 | 3 | 0.880000 | 13.318182 | 13.318182 |
| (5,10] s | 31 | 28 | 3 | 0.903226 | 25.464286 | 14.035714 |
| (10,20] s | 26 | 26 | 0 | 1.000000 | 29.153846 | 24.500000 |
| >20 s | 9 | 8 | 1 | 0.888889 | 33.625000 | 26.125000 |

## Recurring failures, generalisation and priorities

| Video | Primary F1 rank (low first) | Misses | False detections | Significant cases | Raw shuttle presence / frames |
|---|---|---|---|---|---|
| 6 | 1 | 7 | 12 | 34 | 82.116% |
| 9 | 2 | 13 | 15 | 47 | 63.389% |
| 3 | 3 | 1 | 6 | 11 | 73.984% |
| 4 | 4 | 3 | 8 | 30 | 64.495% |
| 10 | 5 | 8 | 13 | 51 | 67.458% |
| 7 | 6 | 2 | 4 | 15 | 60.503% |
| 2 | 7 | 5 | 7 | 39 | 69.143% |
| 1 | 8 | 0 | 0 | 14 | 69.701% |

Test6 has the lowest primary F1 (78.652%); Test9 contributes the most missed rallies (13) and false detections (15). Test10 has51 significant review records. Test6 also has the highest raw-shuttle presence coverage among these runs, illustrating that raw observation availability alone does not rank rally accuracy. This is a cross-video descriptive association; deciding whether an error arises from tracking, contact admission, scene changes, reference boundaries or temporal policy requires the saved source-bound case evidence.

| Recurring temporal category | Count | GT ideal |
|---|---|---|
| GT misses | 39 | 0 |
| False detected rallies | 65 | 0 |
| Significant review records | 241 | 0 |
| early_start_gt_ids | 36 | 0 |
| late_start_gt_ids | 333 | 0 |
| premature_end_gt_ids | 224 | 0 |
| late_end_gt_ids | 138 | 0 |
| weak_iou_gt_ids | 72 | 0 |

| All pooled observed event categories | Counts |
|---|---|
| event_status | {"confirmed":16216,"provisional":2851} |
| stroke_actor | {"unknown":4874} |
| stroke_physical_event_status | {"ambiguous":1640,"insufficient":2526,"probable":708} |
| stroke_contact_status | {"estimated":4874} |
| stroke_classification_status | {"unknown":3539,"estimated":1335} |
| stroke_stroke | {"unknown":3539,"push":605,"lift":202,"drive":60,"net_shot":186,"drop":203,"clear":64,"smash":13,"rush":2} |
| stroke_attribution_reason | {"nearest_proximity":4846,"ambiguous_proximity":28} |
| stroke_classification_abstention_reason | {"unresolved_initial_contact":31,"missing_required_evidence":3508} |
| contact_actor | {"unknown":4874} |
| contact_physical_event_status | {"ambiguous":1640,"insufficient":2526,"probable":708} |
| contact_contact_status | {"estimated":4874} |
| contact_attribution_reason | {"nearest_proximity":4846,"ambiguous_proximity":28} |
| contact_trajectory_reliability | {"probable":2629,"ambiguous":1040,"insufficient":1205} |
| contact_trajectory_reasons | {"supported_turn":2009,"association_unresolved":1040,"coherent_motion_change_unavailable":1205,"supported_launch":620} |
| contact_impact_reliability | {"ambiguous":1640,"insufficient":2526,"probable":708} |
| contact_impact_reasons | {"no_fresh_swing_or_racket_overlap":238,"association_unresolved":1040,"fresh_player_observation_unavailable":2526,"coherent_motion_change_unavailable":362,"coherent_motion_and_fresh_contact_cue":708} |
| contact_attribution_reliability | {"probable":1640,"insufficient":3234} |
| contact_attribution_reasons | {"geometric_attribution_not_verified_identity":1640,"fresh_player_observation_unavailable":3234} |
| rally_end_reason | {"gap":159,"stationary":213,"cut":69,"flush":1} |
| rally_phase | {"unknown":26,"match_play":416} |
| rally_official | {"False":196,"True":246} |
| rally_match_format_known | {"True":441,"False":1} |
| rally_match_format | {"singles":441,"unknown":1} |
| rally_winner | {"None":442} |
| rally_score_transition_status | {"unavailable":303,"candidate":138,"match_format_unknown":1} |
| rally_admission_reason | {"duration_policy":434,"independent_contact_and_observed_motion_witnesses":8} |

| All pooled frame/person component counts | Count |
|---|---|
| frames | 173942 |
| raw_shuttle_present | 118705 |
| detector_executed_frames | 71752 |
| person_rows | 338036 |
| scene_telemetry_present | 28977 |
| scene_raw_hypotheses | 217 |
| actual_content_epoch_increments | 214 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 28800 |
| person_current_detector_matches | 142526 |
| person_propagated_or_unmatched | 195510 |
| pose_present_rows | 271369 |
| pose_current_source_rows | 271369 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 128845 |
| racket_present_rows | 120698 |
| racket_current_source_rows | 120698 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 217 |
| scene_positive_correspondence_vetoes | 3 |
| scene_current_detector_probes | 217 |

All 442 predicted rally winners are unknown. All 4,874 contact/stroke actors are anonymous;3,539 stroke classifications are unknown and1,335 estimated. Impact evidence is708 probable,1,640 ambiguous and2,526 insufficient;2,526 cases cite unavailable fresh player observation. These are output/evidence coverage counts, not independently validated impact accuracy. Identity/ReID unavailability is recorded in the sessions. OCR score observations and138 candidate score transitions do not establish accepted official point correctness; no winner/score accuracy is invented from candidate counts.

| Reporting group | GT | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| Exposed historical development Tests 1/2 | 109 | 104 | 7 | 5 | 0.936937 | 0.954128 | 0.945455 |
| Current sequential Tests3/4/6/7/9/10 | 307 | 273 | 58 | 34 | 0.824773 | 0.889251 | 0.855799 |

These groups show descriptive transfer differences but are not certified train/test splits. Tests 1/2 informed prior development; other historical footage/annotations have also been exposed. No prospective recording-disjoint blind generalisation is established. The supplied dataset also does not certify comprehensive four-player doubles performance; format observations and actual player-population categories are retained without treating contract tests or singles outputs as doubles accuracy.

Priority1 — Reference adjudication: preserve both supplied families, independently review disagreements (especially Test3’s reference sensitivity), certify source alignment and collect exhaustive frame/contact/hitter/shot/score labels. Define a genuinely match-disjoint prospective validation split before tuning.

Priority2 — Boundary and short/missed-rally review: inspect the full39-miss/65-extra inventories and the largest per-video matched errors. Use the duration breakdown, overlap graphs and exact frame/PTS artifacts to separate no observation, fragment/merge geometry, contact-admission and reference-definition hypotheses. The positive mean start error and negative mean duration error support examining late admission/early termination, but do not establish the responsible component alone.

Priority3 — Identity and contact evidence: study the documented missing identity/ReID capability, fresh-detector requirement, propagated boxes and insufficient/ambiguous impact categories. Anonymous tracking, current pose on a propagated box and physical hitter identification are different claims. Do not fetch or swap models based on this report alone.

Priority4 — Semantic scoring: validate OCR row/score ownership, symbolic Player A/B mapping, rally-to-point transitions and shot taxonomy separately. Current unknown winner/actor coverage prevents verified official score-sequence or hitter accuracy; a high rally F1 must not be presented as a complete match-analysis score.

Priority5 — Runtime: profile the dominant measured content/player stage, CPU preparation/OCR and final catalogue decoding/verification on the same frozen workload. Test10’s runner decode/perception scope is3421.460045s within a4421.865935s worker duration; scopes overlap and this is not isolated neural latency. Its frame-count timeout required340.145571s rather than the original300s allowance. Keep operational verification costs separate from GPU model execution and compare performance under controlled shared-host load.

No pipeline fix, model replacement, threshold tuning, label edit or new inference was performed during this report. These are priorities for subsequently authorized improvement work, preserving this complete benchmark as the comparison reference.

## Model, configuration and audit appendix

| Actually declared component | Model / implementation version |
|---|---|
| shuttle | tracknetv3@3.0 |
| shuttle_association | coobserved-static-hypotheses-v1@1 |
| content_continuity | foreground-content-continuity-v2@2 |
| player_detector | rfdetr_small@1.4.2 |
| pose | rtmpose_m_body7@1.0 |
| ocr | rapidocr@3.10.0+bbb248356812+nearest-name-current-column-v2 |
| racket | racket_geometry_v1@1 |
| tracking | court-player-episodes-v1@1 |

| Registry/package artifact | Verified status or SHA256 |
|---|---|
| osnet_ain_x0_25 | unavailable_not_claimed_loaded |
| racketvision_balltrack | unavailable_not_claimed_loaded |
| rfdetr_small | fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e |
| rtmpose_m_body7 | f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741 |
| tracknetv3 | df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a |
| det | 090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f |
| cls | e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c |
| rec | 6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884 |

| Historical runtime inventory field | Recorded value |
|---|---|
| python | 3.12.12 |
| packages | {"torch":"2.14.1+cu126","onnxruntime-gpu":"1.29.0","av":"19.0.1","opencv-python":"5.0.0.93","opencv-python-headless":"5.0.0.93","numpy":"2.5.3","pydantic":"2.14.0","rapidocr":"3.10.0","trackers":"2.6.1","supervision":"0.30.9"} |
| cpu_logical | 36 |
| ram_total | 131912644 kB |
| gpus | [{"physical_visible_index":0,"name":"NVIDIA GeForce GTX 1080 Ti","capability":[6,1],"memory_bytes":11704532992},{"physical_visible_index":1,"name":"NVIDIA GeForce GTX 1080 Ti","capability":[6,1],"memory_bytes":11707809792}] |
| torch_cuda | 12.6 |
| cudnn | 91002 |

This package/hardware inventory was saved before the improved historical runs; it is not a new per-run package-version capture for every video. Actual per-run visible GPU declarations, model/runtime identities and backend receipts remain the authoritative execution evidence. Historical Tests 1/2 lost final CUDA enumeration at publication failure. Source model-lock hashes are distinct from per-worker staged pin-file hashes.

| Frozen source binding | SHA256 |
|---|---|
| Profile source | 280cbf717568fa2a7a1c3b476921bac1b48e9958bf65be0469fae7b5b2dae756 |
| Canonical model manifest | b5590b8ff1437945da036b42b01729f521728259a0dfc4c3299a926216ba8df3 |
| Canonical model lock | fb3b69b8ff3224d6f7b647c68acb08ec4ed4ffec6c67e3acf6f08da485ff9966 |
| Common normalized profile | 2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb |
| Common actual model identity | e3c96b7c2e522fd6efe6106328bebec30137f29b7303fe5e475f8aedea5d2222 |
| Common actual runtime identity | 81e41f18d858ed37c34ce9d07ae34a34268f27e57c0e5f878e07253be309066f |

### Actual backend declarations common to the saved runtime identity

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
  "shuttle_association": {
    "backend": "numpy-cpu",
    "weights": null
  },
  "content_continuity": {
    "backend": "opencv-cpu",
    "weights": null,
    "input_dtype": "uint8",
    "mode": "barrier_detector_layout_v2",
    "barrier_enabled": true,
    "evidence_schema": "foreground-scene-hypothesis:v2",
    "score_semantics": "uncalibrated_pixel_and_ratio_evidence"
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
  },
  "ocr": {
    "package_version": "3.10.0",
    "requested_backend": "onnx-cpu",
    "parser_policy": "nearest-name-current-column-v2",
    "requested_num_threads": null,
    "stages": {
      "det": {
        "model_file": "PP-OCRv6_det_small.onnx",
        "sha256": "090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f",
        "configured_ocr_version": "PP-OCRv6",
        "providers": [
          "CPUExecutionProvider"
        ],
        "provider_options": {
          "CPUExecutionProvider": {}
        },
        "session_options": {
          "intra_op_num_threads": 0,
          "inter_op_num_threads": 0
        }
      },
      "cls": {
        "model_file": "ch_ppocr_mobile_v2.0_cls_mobile.onnx",
        "sha256": "e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c",
        "configured_ocr_version": "PP-OCRv4",
        "providers": [
          "CPUExecutionProvider"
        ],
        "provider_options": {
          "CPUExecutionProvider": {}
        },
        "session_options": {
          "intra_op_num_threads": 0,
          "inter_op_num_threads": 0
        }
      },
      "rec": {
        "model_file": "PP-OCRv6_rec_small.onnx",
        "sha256": "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884",
        "configured_ocr_version": "PP-OCRv6",
        "providers": [
          "CPUExecutionProvider"
        ],
        "provider_options": {
          "CPUExecutionProvider": {}
        },
        "session_options": {
          "intra_op_num_threads": 0,
          "inter_op_num_threads": 0
        }
      }
    },
    "backend_fallback": false
  },
  "racket": {
    "requested_backend": "opencv-cpu",
    "actual_backend": "opencv-cpu",
    "backend_fallback": false,
    "method": "opencv_ellipse_shaft_v1"
  }
}
```

TrackNet ran CUDA FP16. Detector/pose ONNX use CUDA-provider declarations and actual FP32 graphs as documented in the source validation; provider lists do not prove every individual node executes on GPU. The selected profile explicitly runs RapidOCR on CPU. Scene/association/racket geometry are CPU components. Unavailable OSNet and racketvision artifacts are not claimed loaded. The full source profile is experimental, not automatically promoted to production.

### Identical numerical profile, with passive ranges removed

```yaml
name: experiment
description: 'EXPERIMENTAL repair validation on Pascal GTX1080Ti: CUDA FP16 TrackNet,
  actual FP32 detector/pose, explicit CPU OCR; no production promotion'
device: cuda
analysis_height: 720
chunk_frames: 64
lead_buffer_s: 5.0
components:
  stroke:
    model: none
    implementation: stroke-rules-v0
    backend: none
    precision: fp32
    batch: 1
    input_size: null
    params: {}
  rally:
    model: none
    implementation: rally-evidence-tracklets-v1
    backend: none
    precision: fp32
    batch: 1
    input_size: null
    params:
      use_reconstruction: false
      motion_guard: false
      use_exit_recovery: true
      use_curve_exit: false
      use_short_exchange_evidence: true
      use_terminal_contact_evidence: false
  shuttle_association:
    model: none
    implementation: coobserved-static-hypotheses-v1
    backend: none
    precision: fp32
    batch: 1
    input_size: null
    params: {}
  contact:
    model: none
    implementation: contact-evidence-v1
    backend: none
    precision: fp32
    batch: 1
    input_size: null
    params:
      spatial_sigma_px: 0.7216878364870323
  content_continuity:
    model: none
    implementation: foreground-content-continuity-v2
    backend: none
    precision: fp32
    batch: 1
    input_size: null
    params:
      mode: barrier_detector_layout_v2
shuttle:
  model: tracknetv3
  implementation: null
  backend: torch-cuda
  precision: fp16
  batch: 4
  input_size:
  - 512
  - 288
  params:
    seq_len: 8
    bg_mode: concat
    threshold: 0.5
    step: 8
    flight_region: vertical_columns_to_image_top_v1
    diagnostics:
      ranges: []
      top_k: 5
      candidate_floor: 0.1
shuttle_live:
  model: racketvision_balltrack
  implementation: null
  backend: torch-cuda
  precision: fp16
  batch: 1
  input_size: null
  params: {}
shuttle_second_opinion:
  model: wasb_badminton
  implementation: null
  backend: torch-cuda
  precision: fp16
  batch: 1
  input_size: null
  params: {}
player_detector:
  model: rfdetr_small
  implementation: null
  backend: onnx-cuda
  precision: fp32
  batch: 1
  input_size:
  - 512
  - 512
  params:
    score_threshold: 0.35
    court_roi: true
player_reid:
  model: osnet_ain_x0_25
  implementation: null
  backend: torch-cuda
  precision: fp32
  batch: 1
  input_size: null
  params:
    retention_seconds: 8
pose:
  model: rtmpose_m_body7
  implementation: null
  backend: onnx-cuda
  precision: fp32
  batch: 2
  input_size:
  - 192
  - 256
  params: {}
racket:
  model: racket_geometry_v1
  implementation: null
  backend: opencv-cpu
  precision: fp32
  batch: 1
  input_size: null
  params: {}
stroke:
  model: none
  implementation: null
  backend: none
  precision: fp32
  batch: 1
  input_size: null
  params: {}
contact:
  model: contact_fusion_v2
  implementation: null
  backend: none
  precision: fp32
  batch: 1
  input_size: null
  params: {}
ocr:
  model: rapidocr_v4
  implementation: null
  backend: onnx-cpu
  precision: fp32
  batch: 1
  input_size: null
  params: {}
detector_rates:
  in_play: 2
  idle: 6
  replay: 0
pose_rates:
  in_play: 1
  idle: 6
  replay: 0
shuttle_rates:
  in_play: 1
  idle: 1
  replay: 0
ocr_every_s: 1.0
court_verify_every_s: 2.0
escalation_budget: 0.15
racket_window: 6
```

The normalized canonical SHA256 is `2802624c8cd6087de0c9f0c1a7c37fb3dce79fb777bc74848c4cc9586a8bb5fb` for all eight records. Only passive diagnostic frame ranges vary with video length. Each effective unmodified per-video profile and executed source snapshot is linked in its section. Each source/model/checkpoint hash is preserved; current code or a commit label is not substituted for executed historical source.

### Document and artifact verification

| Test | Saved metric recomputation | Every per-rally cell | Event ledger | All component CSV frames | Preserved PTS proof | Source snapshot hashes | Saved files hash-checked | Saved logical bytes |
|---|---|---|---|---|---|---|---|---|
| 1 | pass | pass | pass | pass | pass | pass | 18 | 3191331 |
| 2 | pass | pass | pass | pass | pass | pass | 18 | 5329494 |
| 3 | pass | pass | pass | pass | pass | pass | 1188 | 563026290 |
| 4 | pass | pass | pass | pass | pass | pass | 2340 | 796531230 |
| 6 | pass | pass | pass | pass | pass | pass | 2137 | 789618749 |
| 7 | pass | pass | pass | pass | pass | pass | 1412 | 596070042 |
| 9 | pass | pass | pass | pass | pass | pass | 3636 | 1254208433 |
| 10 | pass | pass | pass | pass | pass | pass | 4056 | 1475945145 |

This review hash-checked 14,805 saved artifact files (5,483,920,714 logical bytes, including repeated staged assets), parsed every primary/predicted interval and every coarse reference row, re-evaluated all 416 GT rows, checked all saved comparison cells, rebuilt event summaries from the original JSONL ledgers, and recounted all 173,942 exported component-frame rows. The56 supplied annotation files are inventoried above with schemas, row counts and hashes. Original source videos had already been deleted only after successful completion verification; their preserved full PTS/pixel/source-hash proofs were checked rather than claiming a new decode of deleted media. The report does not pretend to visually re-adjudicate every sporting error or independently label every physical component.

Original Test10 timeout evidence: [failure.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10/failure.json); separate successful deadline-only retry: [frame_count_retry_receipt.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10_retry1/frame_count_retry_receipt.json). The original failed attempt and all earlier complete records remain untouched. Historic prior aggregate: [REPORT.md](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/consolidated_v1/REPORT.md); this new comprehensive document adds full row-level comparisons and a separately labelled coarse-reference sensitivity analysis without replacing earlier results.

End of comprehensive report.
