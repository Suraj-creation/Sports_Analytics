# Pluggable analytics and badminton quality design

This design implements the user's architecture and quality requirements dated
3 November 2026. All work remains uncommitted. It builds on the current
`SportPlugin`/`SportSession` entry-point boundary and preserves earlier repairs.

## Requirements and observed failures

The generic host must accommodate whole pipeline plugins and replaceable stages,
including future domains beyond badminton. Detection/perception, identity,
contacts, classification, segmentation, scoring and analytics have explicit
contracts. Singles and four-player doubles are required configurations, not a
later fork. Unspecified format needs an evidence-bearing unknown/inferred state;
explicit configuration remains authoritative.

The completed Hylo source session `01M6GC737FR6Z4PDA74BPEZX4H` has 20,524 canonical
frames. Its current output has 676 contact/stroke candidates, all with null named
contact actors; 473 strokes are unknown and 203 are heuristic estimates. There
are 70 rally ends, only six official, and no accepted point. Its 65 corroborated
broadcast observations include KJAERSFELDT/PUSARLA12–21, but configured scoring
labels are1/2 and the row mapping remains unknown. These are observed software
outputs, not labelled contact/shot accuracy.

The baseline is preserved outside the repository at
`../pluggable-pipeline-research-20261103/hylo-before-new-pipeline/`. Existing source,
models, trusted artifact pins, calibration, user reviews and main-port8010 service
must be preserved. Tests and inference run only in the configured GPU environment.

## Architecture choices

Three approaches were considered: copying the reference pipeline wholesale,
replacing the current engine with a new generic graph framework, or extending
the existing plugin interfaces with explicit component composition. The third
approach is selected by the user's reusable-platform requirement: it preserves
event/store/runtime contracts, permits controlled replacement and avoids a second
authority for scoring. Reference code is evidence and a source of compatible
methods, not a reason to copy its forced outcomes or lose provenance.

### Whole-pipeline boundary

`engine/sport.py` already discovers whole implementations through `bai.sports`.
Keep that supported entry point and `SportSession` lifecycle. Add only the
generic composition metadata/factory contracts needed by actual providers.
Badminton does not become an import of the generic host. An independent test
pipeline must run with no badminton-specific model configuration and demonstrate
that changing a component changes its output without changing the host.

### Component boundary

A provider declares a stable component kind, implementation ID/version, typed
input/output contract, required evidence, supported format/device capabilities,
state lifecycle, cache identity and failure behavior. Each session obtains fresh
stateful instances from a registry/factory; registrations cannot silently replace
one another. Factories receive explicit dependencies rather than module globals.
The sport plugin composes the order and owns domain meanings. The generic host
does not assume that every pipeline has a shuttle, a rally or two competitors.

Retain existing model ports and `ModelChoice` compatibility. Introduce a generic
component configuration route without forcing a non-badminton plugin to fill
badminton model fields. Move hard-coded badminton implementation selection into
sport-owned provider registration. A missing model/provider reports unavailable;
an unsupported format cannot silently select a singles model for doubles.

The first actual replaceable ports are the current shuttle/person/pose/racket
estimators, contact inference and the existing `StrokeClassifier.predict` port.
Baseline providers preserve current behavior. Research alternatives remain
explicitly selectable and versioned; they do not become defaults on event counts.

### Format and identity

Format understanding is a replaceable sport component consuming fresh,
target-court detector evidence with view/calibration/epoch context and an optional
user override. It returns `singles`, `doubles` or `unknown`, the observation
interval, evidence basis and an uncalibrated support description. Missing
participants and stale tracker predictions do not count as evidence for singles.
The acquisition layer must not truncate raw detections to two before format is
understood. Format changes form explicit temporal/cache boundaries.

Scoring slots, named competitors/teams, physical participants and track episodes
remain distinct. A provisional track can support an estimated contact and
classifier geometry without becoming a permanent named person. Four-player
hitter ambiguity is preserved; neither alternating sides nor the first same-side
partner is a valid forced identity. Required extra roster/side/service bindings
must be exposed as configuration or review, not hidden defaults.

## Quality repairs and evidence contracts

1. **Acquisition independence:** collect an observed racket when image, current
   matched person and pose evidence support it, even if shuttle detection misses.
   Do not relax the later physical-contact evidence requirements by implication.
   OCR cadence must not depend on a heuristic rally currently being in play.
2. **Contact proposals:** retain the current observed trajectory estimator as a
   baseline provider. A gap/onset alternative must identify timing uncertainty,
   observed support frames and reconstructed/unknown positions. A midpoint is not
   a newly observed shuttle or confirmed racket touch. Compare it on labels
   before changing defaults.
3. **Classification:** separate acquisition/context failures from label errors.
   The current rule provider is heuristic; the existing CG-AP pretrained adapter
   remains a separately measured singles option. BST-0 is a different model and
   cannot consume CG-AP weights. Missing reference stack artifacts must not be
   replaced with a trained-on-test model or a renamed rule output.
4. **Score evidence:** match supplied names conservatively using tokens/initials
   with ambiguity rejection and complete team-pair matching. A single stable
   score transition cannot award multiple rallies. Association must be explicit
   and idempotent, with transactional rollback; a rejected/nonofficial candidate
   must not steal evidence from a later supported association.
5. **Delayed scoring:** independent OCR observations may arrive after a candidate
   is finalized. Keep a bounded unresolved association ledger by score-layout/
   competitor episode. Reconsider only affected unresolved decisions and require
   a unique supported association. Do not merely enlarge a fixed waiting window,
   pad missing points or manufacture a final score.
6. **Visual understanding:** expose observed named scoreboard values and source
   changes separately from accepted point/state. The current ScoreBug already
   supports unbound broadcast values at the presented frame; investigate missing
   or late evidence before adding another score authority. Contact candidates,
   actor hypotheses, classifications and point decisions must be inspectable at
   canonical frames with unknown/rejection reasons.

## Evaluation and adoption gate

Use the matrix in the pinned reference study, expanded for our evidence types:

| Boundary | Required measurements | Essential controls |
|---|---|---|
| Shuttle | visibility precision/recall; observed pixel error; coverage/gaps | source/proxy hash, view/format, observed versus repaired |
| Contacts | full-window precision/recall/F1; timing error; gap/onset subsets | fixed one-to-one tolerance, unmatched detections counted |
| Hitter | conditional accuracy and end-to-end coverage/error; partner confusion | named versus episode/team hypotheses; unknown retained |
| Shots | per-class confusion, macro F1/balanced accuracy and end-to-end recovery | matched-contact and whole-chain denominators; no labels at inference |
| Rallies | onset/offset errors, interval matching and false detections | no annotation windows supplied to production detector |
| Score | transition/point precision, association coverage, sequence error and latency | one transition per point, resets/mid-match starts/row changes |
| Formats | singles/doubles/unknown confusion, time to stable decision | occlusion, adjacent courts, overrides, epoch reset |
| Runtime | measured latency/throughput/memory and failure rate | same videos, model hashes, configuration and hardware |

Keep development and evaluation matches separate. Freeze metric definitions,
tolerances and parameters before evaluating the held-out window. Public
ShuttleSet annotations may supply hit/shot/player/score labels, but do not imply
dense shuttle truth, authoritative line calls or independently labelled racket
contact. Agent visual inspection remains draft diagnostic evidence.

Compare the unchanged baseline and candidate on identical inputs. Software
regressions, replay counts, geometric exclusion and exact final score are not
substitutes for these metrics. Report unavailable labels/models/licenses and
unsupported doubles paths explicitly. A provider is adopted by default only
when comparable evidence supports the change without a material regression.

## Reference provenance and limits

BadmintonAI is pinned at `5c356f05cde0ed90c75316c133e0aba495e5232b`, cloned outside
this repository. Its own code is MIT; model, dependency, data and video terms are
separate. Preserve notices if code is reused. Its legal-score completion,
label-window contact evaluation, synthetic endpoints and model-selection history
must be audited rather than imported as accepted truth. The three specialized
studies record exact source paths and those limitations.

## Verification and rollout

Author focused RED regressions locally, transfer through a temporary-index Git
patch and run them on the GPU server before production edits. Verify each bounded
change, then the combined backend/frontend and plugin contract suites. Back up
sessions before fresh analysis. Keep comparison outputs separate and restore a
public preview only after localhost verification; never publish private prior
validation data implicitly. All changes stay uncommitted.
