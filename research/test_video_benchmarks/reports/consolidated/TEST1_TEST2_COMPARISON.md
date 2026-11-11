# Test1 / Test2 comparison — 5 November 2026

The same current badminton implementation transfers operationally, but exact reference agreement degrades on Test2. This is a descriptive initial cross-match validation, not independent physical accuracy or broad generalization. All results below use the unchanged one-to-one IoU≥0.5 evaluator and half-open intervals.

| Metric | Frozen Test1 historical selection | Frozen Test1 latest scene profile | Test2 fixed primary |
|---|---|---|---|
| GT rally count | 36 | 36 | 73 |
| Predicted rally count | 36 | 36 | 73 |
| TP | 36 | 36 | 67 |
| FP | 0 | 0 | 6 |
| FN | 0 | 0 | 6 |
| Precision | 1.000000 | 1.000000 | 0.917808 |
| Recall | 1.000000 | 1.000000 | 0.917808 |
| F1 | 1.000000 | 1.000000 | 0.917808 |
| Mean IoU | 0.867622 | 0.871026 | 0.849962 |
| Start MAE frames | 29.1389 | 28.2500 | 24.8657 |
| End MAE frames | 10.3333 | 10.4722 | 21.6269 |
| Duration MAE seconds | 1.1324 | 1.1111 | 1.3199 |
| Start ±5 all-reference accuracy | 10/36 (27.78%) | 12/36 (33.33%) | 23/73 (31.51%) |
| Start ±30 all-reference accuracy | 25/36 (69.44%) | 25/36 (69.44%) | 49/73 (67.12%) |
| End ±5 all-reference accuracy | 17/36 (47.22%) | 17/36 (47.22%) | 24/73 (32.88%) |
| End ±30 all-reference accuracy | 34/36 (94.44%) | 34/36 (94.44%) | 54/73 (73.97%) |
| Worker throughput FPS | 11.38677 | 9.62346 | 4.4763 |
| Peak worker RSS bytes | 2871062528 | 2904952832 | 3105214464 |
| Sampled worker GPU peak MiB | 2880 | 2894 | 3400 |

Boundary metrics condition on qualified matches. Tolerance cells above use all-reference denominators; both matched and all-reference denominators for every tolerance are preserved in each supplemental JSON and in the aggregate JSON. Lower conditional start MAE on Test2 does not erase its six missed intervals or prove improved serve timing.

## Predeclared two-video aggregates

### Matched-profile pair (latest Test1 scene + Test2)

| Measure | Macro (unweighted videos) | Micro (pooled) |
|---|---|---|
| Precision | 0.958904 | 0.944954 |
| Recall | 0.958904 | 0.944954 |
| F1 | 0.958904 | 0.944954 |
| Mean matched IoU | 0.860494 | 0.857324 |
| Start MAE frames | 26.5578 | 26.0485 |
| End MAE frames | 16.0495 | 17.7282 |
| Duration MAE seconds | 1.2155 | 1.2469 |

Pooled counts: 109 references, 109 predictions, 103 TP, 6 FP, 6 FN. Median/P90/P95 are not invented from averaged quantiles; per-video distributions remain separate. Full aggregate tolerances and pooled sufficient-statistic RMSE/bias are in the [comparison JSON](/home/administrator/Desktop/sport-analytics/Sports_Analytics/artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/cross_video_comparison.json).

### Historical control pair (older selected Test1 + Test2)

| Measure | Macro (unweighted videos) | Micro (pooled) |
|---|---|---|
| Precision | 0.958904 | 0.944954 |
| Recall | 0.958904 | 0.944954 |
| F1 | 0.958904 | 0.944954 |
| Mean matched IoU | 0.858792 | 0.856135 |
| Start MAE frames | 27.0023 | 26.3592 |
| End MAE frames | 15.9801 | 17.6796 |
| Duration MAE seconds | 1.2262 | 1.2544 |

Pooled counts: 109 references, 109 predictions, 103 TP, 6 FP, 6 FN. Median/P90/P95 are not invented from averaged quantiles; per-video distributions remain separate. Full aggregate tolerances and pooled sufficient-statistic RMSE/bias are in the [comparison JSON](/home/administrator/Desktop/sport-analytics/Sports_Analytics/artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/cross_video_comparison.json).

## Transfer, failure patterns and limits

Both videos are edited broadcast singles, not amateur/doubles or a match-disjoint prospective blind corpus. Test2 has29,296 frames versus 17,268 and a different recording/scoreboard, source activity and edit pattern. All 65 badminton source hashes match the latest frozen Test1; the numerical profile matches, with passive telemetry differences. The two new Test2 runs share host resources, so the observed throughput gap is not attributed to a software regression. Actual stage measurements show OCR dominating Test2 runtime; no controlled RTX 4000 Ada or real-time performance claim follows.

Historical Test1 worst onset examples include GT9(+106f),GT5(+98f),GT15(+86f),GT4(−71f),GT28(+61f); the newer scene arm changes several boundaries while retaining36matches. Test2's largest matched onset is G11(+167f), whose source shows distinct edited points inside one legacy interval; its largest end error is G69(−343f), a real long-flight continuity split. Misses31/32/56/63 include genuinely short exchanges;58 instead has walking/handling reference ambiguity. These cases require the source-specific distinctions recorded in the failure analysis.

Shared weaknesses: sparse early shuttle evidence, immature candidates, temporary raw loss, static/pickup activity, and imperfect same-camera edit handling. Test1-specific documented controls include the painted-T GT27 distractor and GT28 upper-frame/geometry reacquisition. Test2 exposes omitted real P45 activity, reference spans crossing edits, short-point rejection, startup format-confirmation reset, long-clear fragmentation and late pickup continuation. These are diagnostic observations, not independently adjudicated per-component accuracy labels.

The original Test1 result alone overstated the evidence for generalization: complete36/36 reference detection coexists with substantial boundary errors and unvalidated contacts/identity/shots. Test2 refutes extrapolating that perfect reference F1 to another recording. It does not by itself prove threshold overfitting: reference quality, recording conditions and limited component evidence remain confounds. No Test2-specific correction or label-based parameter search was accepted. Both sources remain exposed development/validation evidence; a new reviewed match and independent component annotations are needed for prospective validation.

See [evaluation](../test_02/TEST2_EVALUATION_REPORT.md), [all-case source analysis](../test_02/TEST2_FAILURE_ANALYSIS.md), [component validation](../test_02/TEST2_COMPONENT_VALIDATION.md) and [reproduction](../test_02/TEST2_REPRODUCTION.md).
