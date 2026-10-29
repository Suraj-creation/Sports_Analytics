# Development contact diagnostics and same-observation replay

The anonymous-player integration repair corrects which evidence reaches the
contact detector. It does **not** establish improved event accuracy: the final
same-observation development comparison has lower published-anchor precision/F1.
All 41 published anchors and their original ±0.2-second matching tolerance remain
in every comparison. Nothing was relabelled, retimed or removed to improve scores.
Recording 0046 and its labels were not used in this investigation.

## Concrete defect and repair

In `BadmintonMatchEngine._advance`, doubles already constructed a temporal
`participant_window` from anonymous track episodes. Singles instead scored the
named P1/P2 arrays. After cuts, unreviewed singles identity correctly remains
unknown, leaving those arrays empty even when actual boxes/poses are present.
The detector therefore used only shuttle redirect and impulse; anonymous
proximity and wrist motion were computed later for attribution, after event
selection. Real physical observations were accidentally coupled to name review.

Both disciplines now use qualified anonymous episode evidence during selection.
Singles requires exactly two distinct visible episode tracks and rejects extra or
unresolved visual people. Each current candidate maps to a named actor only if
that frame already has one unique reviewed/established track assignment. Anonymous
episode IDs never become P1/P2 and never trigger the named-player alternation
heuristic. Existing synthetic/legacy named observations remain supported.

A separate eligibility check reuses the existing `ATTRIBUTION_MIN_PROXIMITY=0.05`;
it does not tune a new cutoff. Redirect plus impulse can exceed `P_MIN` with no
player evidence at all. Such peaks now create inspectable `shuttle_turn`
diagnostics with component scores and a rejection reason, rather than opening
rallies and producing strokes. Ambiguous attribution with sufficient body support
remains eligible with an unknown actor. All resulting contacts remain estimates;
this does not prove racket contact or eliminate nearby background false peaks.

## Visual investigation

Twelve development anchors across all four published windows were inspected at
anchor−8, −4, 0, +4 and +8 frames, with raw shuttle trajectories, tracked boxes and
observed wrists overlaid. The local raw 17-frame series and montages are under
`data/audit-20261029/events/dev0044-visual/`. These are AI visual diagnostics, not
new independent contact labels.

| Published frame/family | Raw shuttle observations in ±8 frames | Diagnostic finding |
| --- | ---: | --- |
| 2197 long serve | 0/17 | Camera cuts from close-up into full court; reacquisition and no shuttle. |
| 2227 smash | 5/17 | Calibrated two-player view, no shuttle at the anchor; observations arrive later. |
| 2250 push | 16/17 | Mostly observed flight and player motion; trajectory-only detector ignores available body cues. |
| 2291 block | 17/17 | Flight observed; player count briefly falls to one. Matching event occurs at 2296 without a detector run. |
| 2345 drop | 7/17 | No shuttle at the anchor; later observations accompany an overhead swing. |
| 2396 drive | 17/17 | Observed shuttle initially high/far from the near player's racket, then descends; turn is later than anchor. |
| 3921 long serve | 0/17 | Court/player evidence valid, but shuttle unavailable throughout the interval. |
| 3949 clear | 17/17 | Shuttle and near-player overhead motion observed; detected turn appears later than the published start. |
| 4016 net shot | 17/17 | Continuous observations and two boxes; proximity/swing was absent from original selection. |
| 4342 short serve | 0/17 | Side-camera replay transitions to close-up; calibration lost, no admitted players. |
| 4386 lift | 15/17 | Main-court flight followed by loss; available near-net body/pose evidence. |
| 4916 smash | 0/17 | Valid main-court geometry, but no shuttle observations across this interval. |

Six of twelve anchors have no observed shuttle at the exact anchor. Four have no
raw shuttle in the entire inspected 17-frame interval. Most other windows retain
valid court geometry, so calibration is not their primary failure. This limited
sample is diagnostic and was not selected as an unbiased accuracy sample.

Four baseline unmatched events were also inspected: 2256, 2357, 3960 and 4996.
The first three occur around visible player swing/flight transitions after their
nearest published start anchors (2250, 2345 and 3949). This raises timestamp-
semantics uncertainty; it is not a basis for retiming labels or declaring those
predictions physically correct. Event 4996 occurs in a short observed burst
followed by loss; its exact physical contact remains unverified. Separately,
matched wrong-side events 2462 and 4036 have raw peaks on advertising boards,
while their chosen players' court-coordinate signs agree with visible feet.
These are shuttle/local-association failures, not a reversed court axis.

## Fixed-data comparisons

The isolated replay harness reconstructs engine events and tracks from every
original cache frame, preserving raw camera transforms, observation provenance,
OCR, one bound initial calibration, media bytes and published labels. It refuses
incomplete/noncontiguous media or a changing source tree. It never runs models or
writes to the source session. Code/cache/label hashes are written to each output.

The first comparison uses frozen baseline perception with the repaired lifecycle
code held constant. Adding anonymous cues without the existing two-person safety
increased matches 9→11 but also false positives 19→27 (F1 .2609→.2785). That version
was rejected because it could enable four-person cues in a singles session.

The final ablation uses the completed candidate-v1 perception, with all 41 anchors:

| Event selection | Predictions | Matches | FP | Misses | Precision | Recall | F1 | Family macro F1 | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prior singles selection | 28 | 9 | 19 | 32 | .3214 | .2195 | .2609 | .0593 | 20/28 |
| Anonymous cues, two-person safety | 37 | 10 | 27 | 31 | .2703 | .2439 | .2564 | .0485 | 20/37 |
| Above + existing proximity eligibility | 34 | 9 | 25 | 32 | .2647 | .2195 | .2400 | .0536 | 17/34 |

The eligibility check retains eleven raw-turn diagnostics across the full video.
Three lie inside labelled windows: 2256 and 4998 were unmatched; 4085 matched a
published smash anchor but already had unknown classification and insufficient
player proximity. It is retained diagnostically, not silently deleted. No known
correct matched family is removed by this check; subsequent temporal context can
still change family guesses. Correct matched families remain three in the final
comparison. Court-side agreement remains weak (0 correct, 3 wrong, 6 unresolved
among nine matches), so this work does not justify a person-attribution claim.

The reason to retain the final change is evidence semantics and restoring omitted
input modalities, not a claimed accuracy gain. The low measured agreement,
remaining false peaks, missing shuttle, sparse detector observations and uncertain
provider start-frame precision remain explicit. Thresholds were not optimized.
A final fresh-perception run with the independent ROI/tracker repair is separate.

Local results:

- Baseline-input control: `events/dev0044-before-complete/`
- Baseline-input anonymous-cue ablation: `events/dev0044-after-complete/`
- Candidate-v1 neural result: `evaluation/candidate-0044/`
- Candidate-input unrestricted ablation: `events/dev0044-fresh-after/`
- Candidate-input two-person variant: `events/dev0044-fresh-two/`
- Candidate-input final eligibility variant: `events/dev0044-fresh-guard/`

All paths above are relative to ignored `data/audit-20261029/`. Early failed replay
outputs without `benchmark.json` are incomplete attempts, not reported results.

```bash
.venv/bin/python research/evaluation/replay_reference_events.py \
  --code-root data/audit-20261029/events/participant-guard-source \
  --input data/audit-20261029/evaluation/candidate-0044 \
  --output data/audit-20261029/events/new-replay
```

Regression tests cover actual cue-dependent selection without names, missing/extra
people, unique named mapping, anonymous versus named alternation, raw-turn retention,
unchanged ambiguous actors, and whole/chunk partition invariance. The existing test
called `test_real_engine_ingest_retains_episode_evidence_in_doubles` was corrected
to configure an actual doubles session; its previous default was singles with four
people, which is deliberately ineligible under the singles ambiguity policy.

Final verification: the focused engine, streaming integrity, contact attribution,
doubles fusion, anonymous singles, participant evidence and new singles fusion
selection passed **92 tests in 41.42 seconds**. Ruff and formatting checks pass for
the modified engine, new tests and replay harness. Frozen engine SHA-256:
`f233548e8f69d4f65045e4947b3121e9a9b6277f3cc49a8ed6f9412ba84734ac`.
