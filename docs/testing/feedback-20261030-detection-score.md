# Match feedback: detection and broadcast score — 30 October 2026

The source repository is the GPU server checkout. The observations below are from stored results before the feedback fixes; counts are detections and geometric coverage, not labelled shuttle, contact, or stroke accuracy.

## Recorded evidence

| Session | Stored analysed frames | Initial audit stroke rows | Unknown strokes | Point events |
| --- | ---: | ---: | ---: | ---: |
| 01M616D5NP6VVEGD5RT5VDM497, low-angle doubles | 16,080 / 38,417 | 51 | 31 | 0 |
| 01M55NQMRAS0ATB73XE3XA6S74, Antonsen–Farhan | 12,075 / 12,075 | 243 | 232 | 0 |

Every unknown Antonsen–Farhan stroke lacked supported hitter court coordinates; 183 retained measured speed and flight time. Current main already supports conservative classification from current detector observations without claiming a named player. Historical perception version 7 lacks newer pose schedule and person-association metadata; it must not be promoted into current evidence by guessing those fields. The trained BST-CG-AP classifier named in the profile is not implemented; current stroke classifications use the existing rule classifier.

The timeline previously dropped strokes without P1/P2 identities, so an empty plot did not mean that no contacts had been found. The separate frontend fix now displays unassigned shots and distinguishes missing classifications from unanalysed footage.

## Low-angle court failure

The cache tagged 9,434 frames as another camera and 544 as no court; only 6,102 frames were admitted as main camera. Shuttle observations existed in 2,868 admitted frames. Sampled images at 4,200, 6,000, 8,000, 9,600, and 11,300 show the same active court camera despite alternate-head labels.

The initial auto calibration matched long white roof rafters and wall beams. An overlay of its projected model covers the roof and spectators instead of the green floor. Its supposed net centre is above the frame. This corrupted the court ROI and caused unstable camera identities. Accepting more camera heads or reducing shuttle thresholds would retain the wrong geometry.

The line extractor now limits white-line evidence to large mat-coloured regions when they are present, using all existing colour families, with a small paint-edge allowance. Small coloured objects do not define a floor. Neutral scenes without a large coloured mat retain the previous evidence. Candidate quality thresholds, camera residual limits, player admission, and shuttle thresholds remain unchanged. The filter activates only when that coloured region also contains a retained long white-line component; an unmarked coloured wall must not hide neutral floor lines elsewhere. The cache policy includes the surface-filter revision.

A diagnostic 24-sample proxy calibration selected frame 5,010 with a floor-aligned 5×5-line fit and 0.795 precision. Three independent 64-frame CPU court-tracking clips admitted 64 frames at 1,000, 56 at 4,200, and 22 at 9,600. The corresponding old cache admitted 64, 0, and 0. Remaining weak or ambiguous fits are still withheld. These are geometric coverage measurements, not tracking accuracy.

The exact production sampler was also repeated against the AV1 source: 24 seeks, identical to `SessionRunner._sample_keyframes`. It selected source frame 780 with 0.8802 precision, 5×6 supported lines, 0.973 px RMS, and a camera centre of (−3.703, −8.074, 1.447) m. The annotated reference was visually inspected against the painted floor markings. Thirteen samples yielded accepted fits; eight matched the main head. The summary is retained in `feedback-20261030-calibration-canary.json`. This is an automatic estimate, not a human-verified calibration.

## Score recovery

The Antonsen–Farhan cache contains 85 high-confidence OCR readings, beginning 3–2 and ending 21–17. The configured aliases Sam/TAM do not match the broadcast names, and uncertain player identity prevented learning a row-to-player map. No point events were generated. Shot labels are not a prerequisite for reading the broadcast score.

Two distinct matching name-and-score observations now produce a confirmed broadcast_score event, independently of P1/P2 attribution. The video overlay uses the original broadcast names, shows the last-observation age, and never reveals a future reading. Newer explicit human score corrections take precedence. No server, winner, completed-game count, or named-player mapping is invented.

The original event database was backed up using SQLite's online backup API to:

`/home/administrator/Desktop/sport-analytics/session-backups/20261030-feedback-score-recovery/01M55NQMRAS0ATB73XE3XA6S74.sqlite`

Seventy corroborated broadcast observations were appended from the original cache. The first is frame 249, ANTONSEN 3 / FARHAN 2; the last is frame 11,279, 21 / 17. Point events remain zero. This operation did not re-run models or replace prior analysis.

## Validation

All tests and media checks source `../gpu-env.sh` and use the existing `.venv`.

- New court-surface regressions: four colour cases failed on roof-line leakage before the change, then passed.
- Final court-surface, court lines, court isolation, and plugin camera suite: 42 passed.
- Final full badminton suite, including the cache fingerprint and neutral-floor regression: 578 passed in 244.92 seconds.
- Score reconciler and new persisted-score tests: 7 passed.
- ScoreBug and existing session-component tests, including future-score, stale-score, human-correction priority, and malformed-row cases: 10 passed. Final complete frontend suite: 78 passed; TypeScript typecheck and production build passed. The build retains the existing Settings static/dynamic import warning.
- Changed Python files passed Ruff; changed score UI files passed Biome; git diff --check passed.
- Root browser check confirmed the recovered 3–2 board at frame 250.

Full GPU reanalysis is separately required to replace the low-angle recording's old geometry and inference. It must back up results and discard the bad automatic calibration, while retaining existing source media and explicit human inputs. At inspection both GPUs were idle; historical throughput was approximately 21 frames/s, suggesting roughly 30 minutes for 38,417 frames plus startup overhead. The surface filter improves an evidenced failure; it does not establish complete shot classification or perfect low-angle shuttle recall.

Validation commands:

```sh
source ../gpu-env.sh
.venv/bin/python -m pytest sports/badminton/tests -q
.venv/bin/ruff check sports/badminton/src/bai_badminton/engine.py sports/badminton/src/bai_badminton/perception/court_lines.py sports/badminton/src/bai_badminton/plugin.py sports/badminton/src/bai_badminton/score_ocr.py sports/badminton/tests/test_broadcast_score.py sports/badminton/tests/test_court_surface_evidence.py
cd apps/web
npx biome check src/features/player/ScoreBug.tsx src/features/player/ScoreBug.test.tsx
npm test
npm run typecheck
npm run build
```


## Completed reanalysis
The backed-up reanalysis finished 38,417 / 38,417 frames on 30 October. The final
folded live-event count is 133 shots (42 typed, 91 unknown), versus 40 live shots in
the prior partial backup. Initial audit counts above included superseded records;
they should not be compared as labelled performance metrics. The original run had
processed only 16,080 frames.

Full results and restart/reopen verification are in feedback-20261030-reanalysis.json.
The final backend and frontend are deployed; public health is HTTP 200. Reopening
after a backend restart preserved the exact result timestamp and event sequence
without loading inference models.
