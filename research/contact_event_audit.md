# Contact and event evidence audit

Audit E inspected the production code and immutable Test 1 evidence at benchmark
commit `b773e20`, production `301baf08`. No production file, annotation, source
video, or frozen output was modified. The helper is
`research/audit_e_contacts.py`; machine-readable results, exact boundary-event
extracts, and test output are in
`artifacts/benchmarking/investigation/audit_e_final/`.

## Observed contact evidence

The raw append-only ledger contains **1,002 contact entries**, not 1,002 distinct
physical contacts: 489 provisional entries, 456 confirmations, and 57
retractions. Folding superseding/retracted entries yields **432 current live
contacts**. Exact production-engine replay recorded 489 accepted contact calls;
57 were subsequently withdrawn with cancelled exchanges. The orchestrator
verified identical live contact timestamps between replay and frozen production.

| Property | Recorded count |
| --- | ---: |
| Accepted FSM contact calls | 489 |
| Current live contact events | 432 |
| Named player actor unavailable | 432 |
| Nearest-proximity attribution reason | 428 |
| Ambiguous-proximity attribution reason | 4 |
| Provisional participant hypothesis | 156 |
| Unresolved participant hypothesis | 276 |
| Unresolved because current person is not detector-matched | 272 |
| Available geometric racket evidence | 83 |
| Geometric racket overlap observed | 6 |
| Physical racket contact claimed observed | 0 |
| Positive wrist-swing component | 330 |
| Same-frame stationary re-entry after accepted contact | 38 / 489 calls |

All physical contact events remain **estimated**, including confirmed event-log
versions. Confirmation means the event was associated with a subsequent stroke;
it does not verify an observed racket–shuttle impact. Six ellipse overlaps are
not six verified contacts. There are no independent per-contact timestamps,
hitter identities, or physical racket-contact labels, so this audit does **not**
report contact precision, recall, or causal contact accuracy.

## Actual dependency and timing path

1. `perception/pipeline.py::BadmintonPerception.process` runs the configured
   player/pose cadence and optional `RacketDetector.detect`. Its geometric racket
   detector requires a current uniquely detector-matched player, confident
   observed wrist, plausible ellipse and connected shaft. A carried player or
   missing/blurred racket remains missing. No trained racket-contact adapter is
   active.
2. `engine.py::_window` stabilizes compatible image observations into reference
   coordinates and constructs the processed shuttle track. `events/contact.py`
   `score_frame` at lines 158–175 uses only `vis & ~interp` shuttle samples and
   rejects replay; contextual velocities require at least two independently
   observed points on each side within a bounded temporal segment. Interpolation
   is not silently promoted to an observed hit.
3. `participant_contact.py::participant_window` builds provisional track-episode
   series. `engine.py::_advance` restricts normal contact discovery to target-court
   provenance, excludes unsupported singles participant configurations, and
   preserves anonymous actors separately from physical episode evidence.
4. `score_frame` ranks each person's observed racket, wrist, or upper-body box
   fallback. Proximity is `exp(-distance/body_height/0.45)`. The minimum support
   gate is 0.05, equivalent to roughly 1.35 body heights, not a calibrated contact
   radius. Ambiguous player proximity abstains from identity.
5. Hand-set logistic fusion uses bias −4.2, redirect weight 3.2, relative impulse
   1.4, proximity 3.4, swing 1.1 and optional racket overlap 1.4. Minimum support
   is 0.35. These values are heuristic scores, not learned/calibrated probabilities.
6. `detect_contacts` uses bounded local maxima, six-frame NMS at 30 FPS, earliest
   tie preference, and separate body-supported versus unsupported trajectory-turn
   groups. Scene/replay boundaries limit comparisons. It scores context outside
   the emitted range, so ordinary processing partitions do not shift timestamps.
7. The engine rejects proximity below 0.05 as `shuttle_turn`, then calls
   `fsm.on_contact(frame)` **before** `fsm.step` for that same canonical frame.
   Contacts may start IDLE play, cancel ENDING, reopen CLOSED within its merge
   budget, or start a new segment after that budget. The last accepted contact
   clamps a candidate rally end. Named-player alternation requires a non-null
   named actor; all Test 1 machine contacts are anonymous under the existing
   review policy, so that particular alternation rejection cannot explain their
   timestamps.

Contact velocities use ±3 frame support and local maxima use a six-frame radius.
The engine's 40-frame lookahead and 45-frame retained backward context exceed
these bounded contextual requirements. Runtime publication is delayed, but the
contact event is assigned the candidate's original canonical frame; this is not
a 40-frame timestamp shift. The temporal/video audit provides independent
source/proxy alignment verification.

## E1 — Precontact stationarity immediately contradicts accepted contact

**Symptom and evidence.** In 38 of 489 actual accepted calls, the subsequent
same-frame `step` transitions from IN_PLAY to ENDING using stationary evidence.
Examples include frame 264 at the first annotated rally and frame 12771 in GT27.
The complete frame list is retained in `summary.json`.

**Implementation.** `events/rally_fsm.py::on_contact`, lines 93–110, switches
ENDING to IN_PLAY or opens/reopens a segment but retains `_recent` motion
history. `step`, lines 142–147, immediately tests the old stationary window.
`_begin_end` clamps the timestamp to the new contact; it does not require any
new postcontact stationary evidence. The engine's contact-before-step ordering
at `engine.py::_advance` makes this happen in the same frame.

**Causal probe.** The actual production FSM consumes ten slow observed frames,
accepts a contact at frame 10, and receives a **moving observed sample at speed
10 px/frame**. It nevertheless enters ENDING because nine retained slow samples
outvote the new sample. An isolated research-only counterfactual clears `_recent`
after the accepted contact; the identical current observation leaves IN_PLAY.
The original implementation is not edited for this probe.

**Diagnosis/confidence.** High confidence in the state-history inconsistency and
its occurrence in actual Test 1 traces. The baseline expressly treats accepted
contact as continuation evidence, yet old negative evidence can reverse that
decision without a new stationary period. The experiment does not prove that all
38 contacts are real or that clearing history improves complete-video metrics.

**Alternative explanations.** A physical last contact can coincide with a rally
end, and a false estimated contact should not keep arbitrary noise alive.
Window smoothing itself is legitimate; the unresolved policy is which precontact
observations may still terminate the newly accepted exchange.

**Next causal experiment.** Ablate contact-history invalidation alone on exact
recorded perception, then rerun full production video if results are acceptable.
Compare cancelled provisional starts, fragmentation, duration bias, FP/FN and
every newly extended interval. Test both singles and doubles and contacts near
genuine terminal boundaries.

**Proposed correction/effect/risk.** Give accepted contact an explicit temporal
evidence boundary for stationarity, or require fresh postcontact terminal support.
This should reduce contradictory ending/continuation oscillation and may avoid
some cancelled initial fragments. It can also postpone a valid end or extend play
after a false contact, so it is a candidate correctness fix requiring ablation,
not permission to increase a generic merge threshold.

## E2 — Near-zero velocity can create saturated relative impulse support

**Symptom/evidence.** At GT27 frame 12748, the estimated contact has support
0.72973384, redirect=1, impulse=1, proximity=0.0656 and swing=0.3366. Its contextual
speed changes from **0.0228 to 1.1602 px/frame**. Available geometric racket
evidence has overlap=0. At frame 12771, redirect and impulse again saturate;
speeds are 0.05 and 103.8168, proximity=0.2633, swing=0, support=0.78503353.
Both recorded shuttle positions are near the static court-intersection cluster
identified in the shuttle/video audits; they are not independent impact labels.

**Implementation.** `contact.py::score_frame`, lines 168–175, rejects only when
both velocity norms are below 0.5, then divides post-speed by pre-speed with a
1e−6 floor. Small jitter around a near-zero pre-speed can therefore saturate
relative impulse and redirect; a trajectory-only signature can obtain strong
support with weak body proximity and no racket overlap.

**Controlled evidence.** A constructed nine-frame observed trajectory spans only
2.4 pixels next to a 100-pixel body. Contextual speeds 0.02→0.6 produce redirect=1,
impulse=1 and final support 0.977989 with no pose or racket observation. This
proves score sensitivity, **not** that such a constructed turn is a labeled false
contact or that every high Test 1 score is wrong.

**Diagnosis/confidence.** High confidence in numerical/heuristic sensitivity;
moderate confidence that it contributes to GT27's suspicious contact support.
Alternative explanations include a valid contact near an apex, detector
quantization, or a delayed trajectory turn. No independent contact labels
distinguish those possibilities here.

**Experiment/correction.** Compare absolute motion/acceleration and uncertainty
features against relative impulse, retaining low-speed serve-launch cases.
Expose velocity reliability independently of the fused score. A blunt minimum
incoming speed would suppress legitimate serves and should not be adopted.
Expected effect is fewer static-point/trajectory-switch contacts; risks are lost
weak/occluded physical hits, later starts and poorer short-rally recall. Such
score changes need reviewed contact labels as well as the unchanged rally test.

## E3 — Sparse direct racket evidence limits physical-contact certainty

**Evidence.** Only 83/432 live events retain geometric racket evidence and only
6/432 overlap a geometric racket; 330 have positive swing support. The baseline
therefore mostly segments from trajectory/body/pose cues, not direct equipment
impact. Image-based racket requirements deliberately reject carried detector
tracks and weak/absent wrists, so cadence and geometry quality affect availability.

**Diagnosis/confidence.** Availability is proven; a causal accuracy loss is not.
Missing overlap is not evidence of no physical contact. Weak real rackets can be
blurred, edge-on or occluded. Conversely, an ellipse/shaft near a wrist can still
be an image distractor, so geometric overlap must not be promoted to physical
contact ground truth.

**Experiment/proposal.** Annotate a bounded, source-bound contact review set
before fitting fusion weights or adopting an alternative racket model. Compare
trajectory-only, trajectory+body, +pose, +geometric-racket ablations with the same
input evidence and publish coverage separately from conditional accuracy. Keep
missing evidence explicitly unavailable and preserve replaceable contact ports.
Risks include overfitting the reviewed Test 1 cases and lower doubles coverage.

## E4 — Unresolved named identity is not equivalent to missing contact evidence

All 432 current contacts have anonymous named actors, while 156 retain provisional
physical participant hypotheses. The other 276 are unresolved: 272 are explicitly
`player_not_detector_matched` and four have ambiguous proximity. The engine still
uses independently constructed track/body evidence before named attribution.
Restoring OSNet does not automatically establish named player identity or convert
these estimates to verified contacts. This audit finds no basis to blame missing
OSNet for all fragmentation. Association changes could affect body/pose quality,
but require an isolated player/association experiment; they are not established
by this count alone.

## Validation and limitations

**97 existing contact/racket/streaming/singles/doubles tests passed in 7.65s** in
the required sourced GPU-server environment. They are component/integration
contract tests with controlled or synthetic inputs, not measured real-contact
accuracy. Two additional production-code diagnostic probes passed. No new model,
checkpoint, inference backend, dataset label or production default was installed.

The physical-input ambiguity is material: shuttle pixel tracks and racket/contact
timestamps have no independent labels. Canonical interval matching must remain
unchanged; contact-count changes alone are not an improvement. Decisions about
production fixes belong to the orchestrator after all audits are consolidated.
