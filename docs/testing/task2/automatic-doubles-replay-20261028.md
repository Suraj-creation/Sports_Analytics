# Automatic doubles: matched cached-video replay

On 28 October 2026, baseline `83a668f` and the four-episode implementation were run against the same backed-up cached perception and initial calibration from five existing videos. The replay is isolated, does not modify application sessions, and does not run new inference. The He/Ren–Rankireddy/Shetty recording was explicitly configured for doubles court bounds in both runs; the other recordings used their previous singles configuration. Doubles service and scoring remain incomplete. The paired source and cache hashes, engine hashes, event counts, classification distributions, and metadata coverage are in `five-video-replay-20261028.json`.

| Recording | Frames | Baseline → new strokes | Baseline → new rallies |
| --- | ---: | ---: | ---: |
| SampleRally | 480 | 2 → 2 | 1 → 1 |
| Antonsen–Farhan singles | 12,075 | 235 → 235 | 25 → 25 |
| He/Ren–Rankireddy/Shetty doubles | 12,148 | 202 → 305 | 27 → 28 |
| A02 amateur, singles configuration | 22,802 | 272 → 272 | 65 → 65 |
| Real Video, singles configuration | 4,462 | 0 → 0 | 0 → 0 |

For the four recordings replayed in singles mode, the multisets of current stroke, rally-end and point signatures (event type, frame range, actor, shot label and winner) matched between runs.

In the doubles replay, baseline strokes had 186 `unknown` labels and 16 heuristic serve labels. The new replay had 76 `unknown` and 229 non-unknown heuristic labels; 296 strokes carried a provisional track hypothesis and nine were unresolved. These are **not accuracy scores**: extra candidates may be false positives, and the labels and track associations were not independently reviewed. Historical caches lack the newer per-frame calibration/detector-validity fields; missing values were not fabricated. The replay uses the first recorded calibration and excludes historical human corrections, so it is not a full production reanalysis.

A separate Test7 comparison pairs the supplied filled shuttle CSV with the previously saved 270-frame GPU probe. Both reported a visible point in 253 frames, with median point separation 1.43 px at 1280×720. This is **agreement with an unverified filled reference**, not shuttle accuracy and not shot-classification or player-attribution accuracy. The CSV may be interpolated and may share model or algorithm outputs with the probe, so the near agreement cannot establish correctness. See `test7-shuttle-reference-agreement.json` for source hashes, counts and methodology.

Named automatic estimates still require a reviewed track seed; temporary anonymous track episodes are not durable player identities. Meaningful precision, recall, shot-family accuracy and individual-player attribution accuracy require independent exhaustive held-out per-shot and identity labels for the same video windows; the supplied rally-level CSV does not provide them. The evaluator in `research/participant_benchmark.py` requires such labels and binds the identity map to the exact event log.

## Fresh isolated GPU application run

A separate copy of the app and data processed a 10-second, 250-frame clip (60–70 seconds) from the same doubles proxy on GPU 1. It completed in 28.33 seconds including media preparation, model loading, polling and API reads; sampled peak process GPU memory was 2,122 MiB. The clip produced 17 candidate contacts, 16 stroke events, one rally, and three anonymous track episodes with candidate shots. The bounded movement endpoint returned five track episodes with valid partial movement segments. No result is a correctness measurement, and three candidate episodes do not demonstrate four-player coverage. Full source and clip hashes, output counts and caveats are in `fresh-doubles-gpu-canary-20261028.json`.

The actual isolated dashboard was opened against this video. It showed all four roster slots, three anonymous shot-track episodes, and the partial court-movement view. A selected track box was displayed on the corresponding video frame without creating a human identity review. A duplicate panel rendering bug found during this inspection was corrected and rechecked.
