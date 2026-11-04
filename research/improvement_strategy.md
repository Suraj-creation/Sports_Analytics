# Improvement strategy and rejected shortcuts

Status: all seven audits incorporated; diagnosis gate closed before production
changes. The root-cause registry defines the evidence and uncertainty.

## Sequence

1. Lock the reproduced baseline and failure packages. The evaluator stays frozen.
2. Test small proven defects independently: configured history size, motion-onset
   versus confirmation clock, and contact-stationarity history rebasing.
3. Introduce a sport-owned optional typed evidence port that separates observed
   shuttle motion, estimated trajectory continuity, missing/invalid evidence and
   independently observed participant motion. Existing providers remain usable.
4. Test bounded reconstructed continuity separately from a stationary-conflict
   guard, then use a factorial/ablation comparison for interacting changes.
5. Hold the existing detector fixed for those tests. Separately compare its
   existing overlap strategy with unchanged checkpoints, segmentation and rates.
6. Run selected candidates through fresh full-video production inference, because
   altered rally state changes player/pose scheduling; cached-perception replay
   cannot capture that feedback. Record per-stage timings/resources and actual
   backends. Keep all inferred contacts, outcomes and analytics available.

## Challenge the hypotheses

**Weighted fusion:** uncalibrated hand weights cannot become probabilities by
renaming them confidence. Prefer explicit inspectable gates/uncertainty for this
small development set. There is no independent shuttle/contact visibility set
to fit calibration. Preserve weak candidates diagnostically, not as fabricated
observations. A probabilistic/learned alternative needs separate training labels.

**Adaptive windows:** contact scoring needs short local motion; a reconstructed
occlusion requires bracketing observations; rally confirmation is a different
clock. Do not increase all windows together. Test each intervention separately,
including latency and bounded memory. No interpolation may cross a cut or become
an observed contact, landing or new start.

**Recovery/merging:** GT-dependent fragment unions are diagnostics only. The
segmentation algorithm must decide using source evidence, independently of label
locations/counts. Activity alone is unsafe:1625 baseline active-play frames fall
outside labels. Retain real close breaks, replay/cut barriers and valid unknowns.

**Independent boundaries:** preserve provisional starts and their rejection
reasons. Many large apparent late starts are earlier fragments/cancellations,
not a fixed inference delay. End state must distinguish temporary missing data
from independent terminal evidence; point/winner confidence cannot validate rally
boundaries. Evaluate start and end separately rather than maximizing one IoU.

**Alternative perception:** TrackNetV3 step8 already emits every frame. Overlap
may help model context but cannot observe an out-of-image shuttle. Audit C's
primary-source model comparison screens TrackNetV4, WASB, RacketVision and
InpaintNet without claiming unmeasured superiority or unverified weight licenses.
Keep the compatible existing checkpoint unless measured gains justify change.

**Learned temporal models:**36 intervals from one exposed source do not justify
training, calibrating and claiming generalization on that same source. A TCN/HMM
or pretrained event backbone is an experiment only after verifying label/domain
compatibility, licensing, latency and a match-disjoint evaluation plan. Preserve
typed ports so a justified model can replace the rule segmenter later.

## Promotion policy

Proven lifecycle/configuration defects may be repaired with focused tests and
full regression checks. An evidence-aware segmentation candidate remains
explicitly versioned and opt-in until independent annotated footage establishes
generalization. Report Test1 improvements as exploratory and include every
outlier/regression. Do not remove broad pipeline capabilities or restore an
unrelated optional checkpoint merely to conceal missing evidence.

## Executed outcome

The bounded observed image-exit/return cue was the successful intervention:
35 TP, 4 FP, 1 FN and F1 0.933333 in a fresh complete Test1 run, compared with
30/19/6 and 0.705882. Full numerical and per-row results are in
`final_benchmark_report.md` and `regression_report.md`. This cue retains unknown
shuttle coordinates and cannot create an idle start or observed contact.

Generic reconstruction did not improve the selected exit-only output; the
motion guard reduced recall. TrackNet step4 cost 1.46 times the paired component
runtime and did not recover the tested physical visibility gap, so step8 stays.
These negative controls reject the assumption that more signals, a larger
temporal window or a more complicated detector necessarily improve this task.

Remaining priorities follow observed failures: independently review preparation
versus physical rally-start conventions and same-camera edits; label source
shuttle visibility/location around early misses and static attractors; then test
background/context and candidate association under fixed segmentation. Use
match-disjoint annotated singles, amateur and doubles footage before promoting
the optional mode. Do not fit residual coordinates, merge budgets or offsets to
these exposed intervals. Severe residual and worsened boundaries remain open.
