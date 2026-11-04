# Contact/event causal experiments and regression plan

The completed audit uses unchanged production code and frozen recorded evidence.
All findings are development diagnostics on Test 1. No independent generalization
claim or new contact accuracy label is introduced.

## Reproduction

```bash
source ../gpu-env.sh
python research/audit_e_contacts.py \
  --output artifacts/benchmarking/investigation/audit_e-repeat
pytest -q \
  sports/badminton/tests/test_contact_attribution.py \
  sports/badminton/tests/test_contact_pose_sampling.py \
  sports/badminton/tests/test_contact_scene_boundaries.py \
  sports/badminton/tests/test_contact_event_evidence.py \
  sports/badminton/tests/test_streaming_contact_integrity.py \
  sports/badminton/tests/test_singles_contact_fusion.py \
  sports/badminton/tests/test_doubles_contact_fusion.py \
  sports/badminton/tests/test_racket_evidence.py
```

Executed outputs: `artifacts/benchmarking/investigation/audit_e_final/summary.json`,
`boundary_contact_evidence.json`, and `tests.log`. The focused suite completed
97 tests, none skipped. The helper's controlled probes use the actual production
`RallyFSM` and `score_frame`; their assertions reproduce existing behavior and
are not a substitute for a new production regression test after a fix.

## Completed probes

| ID | Intervention/control | Measured result | Meaning and limit |
| --- | --- | --- | --- |
| E-history | Same production FSM and accepted contact; research-only clearing of old stationarity history in counterfactual | Baseline enters ENDING on same frame despite current speed10; counterfactual remains IN_PLAY | Establishes history/state inconsistency; no video performance claim |
| E-jitter | Construct a 2.4px-span turn near 100px body, no pose/racket | Speeds0.02→0.6, redirect1, impulse1, support0.977989 | Exposes relative-ratio sensitivity; does not invent a physical false-contact label |
| E-ledger | Fold all superseding/retracted raw contacts independently | 489 accepted calls,57 withdrawals,432 live events | Prevents counting append-only versions as distinct detections |
| E-real-state | Read exact-parity engine traces | 38 same-frame stationary re-entries after contacts | Shows the history mechanism occurs in real production decisions |
| E-streaming | Existing contextual-NMS and scene-boundary tests | Focused suite97passed | Validates existing partition/coordinate/evidence contracts with controlled inputs |

## Exact GT27 event chain

1. Accepted estimated contact12748, weak proximity0.0656 and no observed racket
   overlap. Motion/trajectory support is high despite speeds0.0228→1.1602.
2. Old low-motion shuttle samples yield stationary candidate12753, clamped to
   contact12748. The segment closes12763.
3. Estimated contact12771 arrives23frames after the tentative endpoint; the
   configured merge allowance is22frames. It finalizes12455–12748 and opens a
   new segment at12771. This is not a timebase error.
4. That same frame immediately re-enters ENDING from retained stationary history;
   observed speed376.023 at12772 resumes play, and old history causes another
   ending/resume oscillation before it ages out.

This chain contains two independent mechanisms: a configured merge boundary and
history reuse. Fixing history alone does not prove the previous segment will
merge; increasing all merge gaps would risk joining distinct nearby rallies.

## Proposed controlled experiments after consolidated diagnosis

| Experiment | Change one variable | Acceptance evidence | Main risk |
| --- | --- | --- | --- |
| E1 contact-history boundary | Invalidate/rebase stationarity evidence when contact is accepted; preserve original thresholds | Focused state-machine counterexamples pass; fewer contradictory same-frame re-entries; unchanged matcher full-video detection/boundary metrics and every outlier reviewed | False estimated hits postpone valid endings |
| E2 contact validity exposure | Retain independently inspectable pre/post velocity quality, observed availability, proximity and swing/racket availability | No numerical score is silently called calibrated; annotation-free parity where behavior unchanged | Broader interface change or accidental fabricated observations |
| E3 relative versus absolute impulse | Replace only the unstable relative impulse feature in an opt-in contact implementation; explicit serve controls | Reviewed physical contact labels plus interval metrics; no claims from contact counts alone | Missed low-speed serve launches and weak hits |
| E4 cue ablation | Trajectory; +body; +pose; +geometric racket on exactly same recorded perception | Publish signal coverage and reviewed conditional accuracy separately, then Test1 intervals | Test1 overfitting and changed singles/doubles coverage |
| E5 association/cadence | One player/pose cadence or association intervention at a time | Compare physical episode cue availability; keep named identity uncertain | Cadence changes affect runtime and perception feedback, requiring fresh full-video inference |

Rally-level success requires unchanged maximum-cardinality IoU>=0.5 matching,
better start/end error distributions, fewer misses/extras and less fragmentation,
without joining legitimate adjacent rallies. Record all weights/parameters,
checkpoints, code/input hashes, actual providers, fresh-inference versus replay
status and execution logs in a new experiment directory. No post-hoc manual
contact or boundary corrections may enter predictions.

## Required regression cases for an accepted fix

- Contact during ENDING followed by observed fast motion must not immediately
  re-end solely because precontact samples were stationary.
- Contact during a genuinely terminal phase still requires bounded confirmation;
  a false candidate cannot extend an exchange indefinitely.
- Contact on the final frame, inside/outside merge budget, or across a camera/cut
  boundary retains correct ordering and endpoint conventions.
- No contact may be created solely from interpolated shuttle points; a physical
  uncertainty/occlusion continuation signal must remain distinct from impact.
- Missing pose/racket, held detector boxes, two ambiguous players, or four-player
  doubles preserve explicit availability and attribution uncertainty.
- Contextual NMS remains invariant to processing partitions and does not suppress
  a body-supported hit behind an unsupported trajectory turn.
- Low-speed launch, shuttle apex and small static jitter are separate controls;
  neither an incoming-speed floor nor a relative impulse ratio alone establishes
  a physical hit.

The 38 occurrences, complete frame list, and contact event payloads remain
reviewable in the artifact package. Model-generated contact events are diagnostic
evidence, never ground-truth contact annotations.
