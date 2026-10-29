# Event and analytics integrity repair — 29 October 2026

These results establish deterministic event integrity on frozen observations. They do not establish shot/contact accuracy or improve the supplied perception outputs.

## Repaired causes

- Contact suppression previously saw only the current output chunk. A turn spanning a boundary could emit twice and contaminate the next shot's flight duration. Selection now uses bounded local score maxima with contextual observations, deterministic earliest-frame tie handling, and a causal singles alternation guard maintained across calls. Synthetic contact frames, actors, families, service status and flight durations agree for chunk sizes 1, 16, 32, 64 and whole-clip ingestion. Local maxima replace greedy NMS: distant suppression chains no longer change a decision. The singles guard retains the earlier emitted hypothesis instead of replacing it after publication.
- The first detected contact of every segmented exchange was unconditionally classified as a serve. An observed incoming flight now identifies a nonserve. A stationary diagonal service formation over the preceding 0.6 seconds can support an **estimated** serve. Missing history/geometry/formation produces unresolved initial-shot context, not an invented serve; later shots still receive available family estimates. Doubles and anonymous initial service roles remain unresolved. This is a documented heuristic, not a learned service detector.
- A stationary shuttle window could backdate a rally end before an already accepted contact, leaving a stroke outside every rally and contaminating the next exchange's flight interval. Rally ends now include their latest accepted contact. A contact after the merge deadline opens another exchange. When one FSM update finalizes an old rally and starts another, the engine now preserves both start-event references in the correct order. Cancelled-rally contacts are retracted even if a start reference was absent.
- Contact events disclose `contact_status=estimated`, `racket_contact_observed=false` and uncalibrated heuristic support. Their confidence band never claims confirmed physical contact. `CONFIRMED` remains the finalized event-lifecycle status. The unsupported source comment asserting trained/calibrated fusion weights was removed.
- The live plugin snapshot now uses the same canonical event/track fold as HTTP analytics. Its former engine-only view omitted the timestamp, track and camera evidence required by movement and returned empty spatial analytics. The persisted fold is cached by ledger identity/revision, player/camera directory revisions and FPS; unchanged status reads reuse it. Tests exercise track-only revision, stroke correction and equal-sequence database replacement.
- Highlights expose their supporting rally/shot IDs, estimated-event basis, and ranking-score semantics. Unknown family labels no longer earn a variety bonus. Ranking score is no longer presented as a confidence probability. Receiver-position proxies remain separate from actual shuttle landing evidence.

## Frozen real-video semantic replay

Source: the existing local session `01M62Y12THWAV746H1H8PXWGVX`, first **13,140 frames at 30 fps**, through the original audit-snapshot frontier. Exactly 219 perception chunks were copied and SHA-256 bound before replay. Both engines use the same observations and calibration in isolated event databases. No GPU inference or source-session mutation occurs in this replay.

| Diagnostic | Frozen baseline | Repaired engine |
|---|---:|---:|
| Retained contact/stroke hypotheses | 305 / 305 | 313 / 313 |
| Segmented exchanges | 45 | 46 |
| Adjacent contact pairs within 0.20 s | 7 | 0 |
| Strokes referenced by no completed exchange | 1 | 0 |
| Short/long serve family labels | 27 | 0 |
| Unknown family hypotheses | 180 | 210 |
| Known family hypotheses | 125 | 103 |
| CPU semantic replay wall time, single run | 24.85 s | 25.64 s |

All 46 repaired exchanges have an explicit initial-contact service decision: 31 show incoming flight; 14 lack enough service evidence; one has estimated service formation but insufficient flight evidence for family classification. Nonserve known families remain available. Requiring an accepted contact to lie inside its exchange retains some hypotheses previously lost to short-rally cancellation, so total event count rises. These are accounting changes, **not a claim that the added events are true hits**. The frame-window occupancy and absence of close duplicate candidates are not precision/recall.

The supplied observations were produced by the old perception pipeline, including its subsequently discovered image-colour defect. Repaired perception needs separate fresh-video evaluation.

Artifacts in the ignored local evaluation directory:

- `data/audit-20261029/events/cache-manifest.json` — frozen input hashes; manifest SHA-256 `1ffbdfcddec02e43978b989ff121425cffd249e3887b2f8d167448da7266929e`.
- `data/audit-20261029/events/replay_semantics.py` — executed read-only input replay harness, with explicit code-root/output arguments and overwrite refusal.
- `data/audit-20261029/events/before/summary.json` and `data/audit-20261029/events/frozen-final/summary.json` — event counts, per-frame family predictions, implementation hashes and timing; corresponding isolated `events.sqlite` ledgers remain alongside them.

Reproduce from the repository root, using fresh output paths:

```sh
.venv/bin/python data/audit-20261029/events/replay_semantics.py \
  --code-root data/audit-20261029/baseline-source --output /tmp/badminton-events-before
.venv/bin/python data/audit-20261029/events/replay_semantics.py \
  --code-root . --output /tmp/badminton-events-after
.venv/bin/python -m pytest \
  sports/badminton/tests/test_streaming_contact_integrity.py \
  sports/badminton/tests/test_plugin_analytics.py \
  sports/badminton/tests/test_engine.py \
  sports/badminton/tests/test_temporal.py \
  sports/badminton/tests/test_match_phase.py \
  sports/badminton/tests/test_analytics_integrity.py -q
```

The final focused engine/phase/spatial/live-cache/integrity run passed 71 tests; an additional temporal/integrity run passed 41, and the contact/doubles/anonymous-context integration run passed 75. These overlapping counts are individual runs, not a summed unique-test total. Ruff check and format check pass for the changed files.

## Remaining measurement limits

The installed default remains `stroke_rules_v0`; changing profile text to BST does not install or evaluate a trained classifier. Exact racket contact is unavailable. Pixel-speed/depth rules remain perspective dependent; final shots lack next-contact flight duration. Service formation is an estimate, and doubles partner service rotation is not inferred. Published FineBadminton 0044 development and 0046 reserved-holdout evaluations must report actual new inference independently. Published anchor/family/court-side agreement does not establish durable four-person identity or independently verified racket-contact accuracy.

## Baseline 0044 court-side attribution inspection

The fresh frozen baseline's nine anchor-matched events contain two resolved sides,
both wrong, and seven unresolved sides. Inspection of raw perception, source frames
and stored classification context does **not** show reversed court coordinates:

- Predicted frame 2462 matches the published top-side anchor 2463 but selects near
  track 0, whose stored court y is −4.35 m. Its visible box is on the near half.
  The predicted shuttle is at approximately (506, 175), on a rear advertising board.
- Predicted frame 4036 matches the bottom-side anchor 4040 but selects far track 4,
  whose stored court y is +1.67 m. Its visible box is on the far half. The predicted
  shuttle is at approximately (825, 180), on another rear advertising board.

The nearest-body heuristic assigns the wrong participant from false shuttle peaks;
changing the sign of court y would conceal that upstream failure and corrupt valid
coordinates. Screenshots are in the local ignored
`data/audit-20261029/events/side-inspection/` directory. These are visual diagnostics,
not new physical-contact ground truth.

Six unresolved matches (frames 2296, 3998, 4444, 4943, 5029, 5083) have
`detector_observed=false` and every stored person `detector_matched=false`; their
reason is `player_not_detector_matched`. Frame 4085 also has no detector run and
abstains for `insufficient_proximity`. Exact rows and event IDs are saved in
`data/audit-20261029/events/baseline0044-side-matches.json`. These coverage gaps must
remain explicit; loosening attribution thresholds is not an evidence-based repair.
Fresh candidate perception and its separately frozen evaluation are needed to
measure the effect of the RGB/input repairs. No coordinate or attribution-threshold
patch was made from this inspection.
