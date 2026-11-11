# Consolidated sequential benchmark: eight requested videos

Evaluated Tests1,2,3,4,6,7,9,10. Tests5 and8 were explicitly skipped by the user and are excluded from every denominator. This report consolidates the completed requested subset; it does not claim a ten-video result.

The improved profile, inference components, checkpoints and unchanged IoU0.5 matcher were frozen throughout new-video evaluation. Historical Tests1/2 retain their actual source and original catalogue-publication failures plus independent completion proofs; the later existing catalogue harness fix did not change their component code/profile. Test10 required a separate retry with only the original FFprobe frame-count timeout extended300→1800seconds. Its failed attempt remains preserved.

| Test | Reference rallies | Predictions | TP / FP / FN | Precision | Recall | F1 | Matched mean IoU | Start MAE frames | End MAE frames | Duration MAE seconds |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 36 | 36 | 36 / 0 / 0 | 1.000000 | 1.000000 | 1.000000 | 0.871026 | 28.250000 | 10.472222 | 1.111111 |
| 2 | 73 | 75 | 68 / 7 / 5 | 0.906667 | 0.931507 | 0.918919 | 0.848135 | 23.882353 | 21.161765 | 1.302451 |
| 3 | 19 | 24 | 18 / 6 / 1 | 0.750000 | 0.947368 | 0.837209 | 0.895795 | 28.611111 | 8.500000 | 0.992593 |
| 4 | 41 | 46 | 38 / 8 / 3 | 0.826087 | 0.926829 | 0.873563 | 0.821815 | 31.289474 | 26.842105 | 1.532456 |
| 6 | 42 | 47 | 35 / 12 / 7 | 0.744681 | 0.833333 | 0.786517 | 0.884584 | 23.485714 | 20.571429 | 1.350476 |
| 7 | 30 | 32 | 28 / 4 / 2 | 0.875000 | 0.933333 | 0.903226 | 0.833985 | 23.464286 | 14.964286 | 1.178571 |
| 9 | 82 | 84 | 69 / 15 / 13 | 0.821429 | 0.841463 | 0.831325 | 0.862791 | 22.869565 | 18.884058 | 1.250725 |
| 10 | 93 | 98 | 85 / 13 / 8 | 0.867347 | 0.913978 | 0.890052 | 0.844965 | 23.988235 | 18.058824 | 1.227451 |

| Aggregate detection | Value |
|---|---|
| Pooled ground_truth_count | 416 |
| Pooled predicted_count | 442 |
| Pooled true_positives | 377 |
| Pooled false_positives | 65 |
| Pooled false_negatives | 39 |
| Pooled precision | 0.852941 |
| Pooled recall | 0.906250 |
| Pooled f1 | 0.878788 |
| Macro per-video precision | 0.848901 |
| Macro per-video recall | 0.915977 |
| Macro per-video f1 | 0.880101 |
| Pooled matched mean IoU | 0.854244 |

Micro detection pools TP/FP/FN. Macro gives each recording equal weight. Pooled boundary errors/IoU condition on matched intervals; missed rallies remain misses and receive no invented boundary error. Exact pooled signed/absolute error arrays, quantiles, per-video metrics and both boundary-tolerance denominators are retained in consolidated_metrics.json.

| Matched error | MAE | RMSE | Signed bias |
|---|---|---|---|
| start_frame | 25.042440 | 48.408765 | 17.222812 |
| end_frame | 18.477454 | 38.668077 | -8.408488 |
| start_time_sec | 0.834748 | 1.613625 | 0.574094 |
| end_time_sec | 0.615915 | 1.288936 | -0.280283 |
| duration_sec | 1.261450 | 2.150160 | -0.854377 |

| Test | Missed rally IDs | False detection IDs | Significant cases requiring source review |
|---|---|---|---|
| 1 | [] | [] | 14 |
| 2 | [31, 39, 56, 58, 63] | [11, 32, 40, 41, 47, 58, 71] | 39 |
| 3 | [7] | [7, 8, 9, 10, 19, 22] | 11 |
| 4 | [1, 14, 25] | [1, 5, 7, 10, 17, 28, 31, 45] | 30 |
| 6 | [9, 19, 22, 26, 30, 40, 41] | [2, 10, 11, 12, 15, 16, 24, 25, 31, 32, 36, 46] | 34 |
| 7 | [3, 22] | [3, 4, 5, 22] | 15 |
| 9 | [5, 7, 16, 24, 32, 33, 41, 42, 46, 50, 52, 55, 71] | [5, 6, 8, 9, 14, 33, 34, 35, 36, 41, 48, 49, 54, 62, 83] | 47 |
| 10 | [9, 15, 30, 37, 40, 43, 55, 85] | [28, 32, 33, 37, 40, 43, 44, 45, 61, 68, 85, 89, 90] | 51 |

Recurring failure patterns and weak components:

- Missed intervals, unmatched detections and late starts/early ends recur across the evaluated recordings. Per-video miss/extra IDs, overlap topology and significant-case indexes identify where review should begin. These are measured reference disagreements; their physical causes are not established by interval matching alone.
- Contact, hitter and stroke semantics remain limited by evidence/abstention. Observed unknown actors, insufficient/ambiguous impact evidence and unknown shot labels are counted below. These coverage deficits are measured system behavior, not independently labelled contact or classification error rates.
- Scene barriers, player detector cadence, propagated boxes, shuttle observations and court/pose/racket coverage are preserved per frame. Correlation with rally errors needs source review; scene counts or geometric coverage do not certify physical model accuracy.
- OCR observations, candidate score transitions and unknown rally winners remain distinct from accepted official point decisions. Rally-level CSVs do not supply exhaustive source-bound contact, stroke, identity, shuttle-coordinate or score-sequence labels, so those component precision/recall/confusion metrics remain unavailable.

Pooled observed categories (counts, not physical accuracy):

```json
{
  "rally_end_reason": {
    "gap": 159,
    "stationary": 213,
    "cut": 69,
    "flush": 1
  },
  "rally_winner": {
    "None": 442
  },
  "rally_score_transition_status": {
    "unavailable": 303,
    "candidate": 138,
    "match_format_unknown": 1
  },
  "stroke_actor": {
    "unknown": 4874
  },
  "stroke_classification_status": {
    "unknown": 3539,
    "estimated": 1335
  },
  "contact_physical_event_status": {
    "ambiguous": 1640,
    "insufficient": 2526,
    "probable": 708
  },
  "contact_impact_reasons": {
    "no_fresh_swing_or_racket_overlap": 238,
    "association_unresolved": 1040,
    "fresh_player_observation_unavailable": 2526,
    "coherent_motion_change_unavailable": 362,
    "coherent_motion_and_fresh_contact_cue": 708
  }
}
```

| Test | Worker seconds | Worker FPS | Parent seconds (original failure-inclusive for historical1/2) | Sampled worker GPU MiB | Sampled tree RSS bytes |
|---|---|---|---|---|---|
| 1 | unavailable | unavailable | 2037.223530 | 2126 | 3068030976 |
| 2 | unavailable | unavailable | 3643.506591 | 2122 | 3052724224 |
| 3 | 858.445222 | 9.801441 | 864.429404 | 2130 | 2827141120 |
| 4 | 2004.809194 | 9.992971 | 2012.031731 | 2126 | 2992701440 |
| 6 | 1984.001834 | 9.029730 | 1992.107158 | 2128 | 2848849920 |
| 7 | 1034.103667 | 10.371301 | 1039.893208 | 2122 | 2906685440 |
| 9 | 3718.272271 | 8.917314 | 3729.349836 | 2122 | 3005173760 |
| 10 | 4421.865935 | 8.397586 | 4433.866512 | 2124 | 3048800256 |

Runtime limits: GPU1 was used for neural inference; CPU decoding, scene/association work, configured CPU OCR and verification contribute to elapsed time. Stage scopes overlap and cannot be summed as model latency. GPU peaks are sampled per worker PID/UUID; process-tree RSS can double-count shared pages. Historical1/2 missing final worker timings remain unavailable, and failure-inclusive parent elapsed is not substituted for successful worker runtime.

Generalisation: this is descriptive agreement with supplied legacy rally tables across eight videos. Tests1/2 informed prior development, historical exposure of other recordings is documented, and no prospective recording-disjoint blind evaluation is certified. Per-video variability demonstrates sensitivity to recording conditions; it does not by itself identify a causal weak component or establish production readiness.

Improvement priorities for later work, with no fixes performed:

1. Establish independently reviewed, source-bound rally/contact/shot/hitter/score labels and recording-disjoint validation splits. Resolve reference disagreements without rewriting the preserved original CSVs.
2. Review the saved missed/extra intervals and the worst matched boundary errors. Trace them through actual shuttle observations, contact evidence, detector cadence and scene/coordinate epochs before selecting any change.
3. Prioritize contact/hitter evidence and classification coverage where the saved categories show insufficient/ambiguous evidence or abstention; distinguish missing observations from temporal admission policy.
4. Audit score observations, row ownership, player/team binding and accepted point decisions separately from rally detection. Preserve unknown outcomes until supporting evidence exists.
5. Profile dominant stage scopes and CPU/GPU scheduling on the same frozen workload. The Test10 preparation timeout is an operational limitation; the documented deadline-only retry changes no inference result by design. Confirm performance improvements separately from accuracy.

All individual reports, prediction/event/cache outputs, effective profiles, source/model/runtime bindings, command/resource logs and PTS/scene-pixel verification are retained in their immutable records. Required proxies remain; only successfully processed originals were removed from the working video directory. Test10 initial failure is retained separately. No pipeline fixes were begun.

- [Test1 saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test1_historical)
- [Test2 saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test2_historical)
- [Test3 saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test3)
- [Test4 saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test4)
- [Test6 saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test6)
- [Test7 saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test7)
- [Test9 saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test9)
- [Test10 saved record](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10_retry1)
