# Pluggable pipeline quality work — 2026-11-04

This work continues on the GPU server, branch `codex/pluggable-pipeline-quality`,
checkout `/home/administrator/Desktop/sport-analytics/event-score-integrity-20261103`.
The user authorized a checkpoint push: commit `5c9b0f5257c252f8bbb8a206ed956c6917477f1a`.
Subsequent changes remain uncommitted. The user's separate Windows UI branch is
not an authoring surface for this task. The three instruction files reflect this.

## Evaluation definition and evidence limits

Public human labels are bound to original source bytes and one continuous CFR
proxy per recording. All clip frames, inter-rally gaps and live contact hypotheses
are evaluated, rather than running the detector only inside ground-truth rallies.
Chronological one-to-one matching maximizes matches, then minimizes timing error.
Report both ±3 and ±6 canonical frames, known-class coverage/abstention, native
class confusion and joint contact/class metrics. A correct event count is not
accuracy. Agent visual alignment remains draft, not independent human verification.

- India Open 2022 singles: development, four rallies, 85 anchors, 4,800 frames.
- Denmark Open 2022 singles: reserved project comparison, four rallies including
  one single-contact serve, 39 anchors, 3,300 frames. It was used in later upstream
  deployment selection and is not a pristine upstream holdout.
- Indonesia Masters 2022 men's doubles: DShuttleNet version 7, match 5, set 1,
  rallies 144–147, all four hitters and two teams, 45 anchors, 3,600 frames.

ShuttleSet22 label source is CoachAI commit
`45517f7d4cb936b03f3eabf939cc7959d39226fe`, whose root MIT notice is retained.
DShuttleNet DOI `10.34740/kaggle/dsv/16097938` resolves to publisher version 7,
licensed CC BY-NC-SA 4.0; attribution and license evidence are retained privately.
The project is currently noncommercial. Broadcast rights remain separate; neither
videos nor generated annotation files are committed or redistributed here.
Dense shuttle visibility, physical racket contacts, true 3D speed and line-call
truth are not supplied by these sparse shot annotations. Test7 highlight labels
contain contradictory winner/score rows and are excluded as trusted score truth.

## Preserved baseline and first result

The baseline uses the previous task's code patch on `cc736886`, with only the
shared harness repair that preserves source-to-proxy crop metadata. Model weights,
FP32 shuttle precision and processing settings are recorded per run. The original
application sessions and existing models are read-only inputs. A pinned external
corner candidate is an explicit shared singles input, not independently reviewed
calibration truth; production warm-start can also propose calibration.

India baseline, all 85 anchors and 84 predictions:

| Tolerance | Matched | Precision | Recall | F1 | Correct matched shot labels |
|---|---:|---:|---:|---:|---:|
| ±3 frames | 60 | 71.4% | 70.6% | 71.0% | 3/60 (5.0%) |
| ±6 frames | 61 | 72.6% | 71.8% | 72.2% | 3/61 (4.9%) |

At ±6, known-label coverage on matched contacts is 15/61 (24.6%), supported-class
macro F1 is 5.7%, and full-clip joint contact/class precision/recall are 3.6%/3.5%.
There are zero observed broadcast-score events and zero accepted points in this
baseline. Runtime consistency passes, which does not establish score accuracy.
End-to-end wall throughput is 13.09 FPS on the shared GTX 1080 Ti server.

Source SHA-256: `47bb759f8f6864c2c1c6952b743c1a4735137fe86835a6b240f3ceffd05603ca`.
Proxy SHA-256: `018df5d81dbb60c692805acf558992554e4a24b29fc8e64ea28fd0857bd1ac49`.
Canonical crop: original decode frames [12000,16800), 30 FPS. Label offset is −1
in full-source frames and remains an agent-reviewed draft.

## Diagnosed repairs under integration

- Score OCR had usable names/digits but merged court-side mini-scores and sponsor
  logos into a false third board row. Spatial pairing now requires a unique
  aligned two-row name/score board and rejects ambiguous extra boards/columns.
  The same 20 real-frame/corner probes improved from zero to two legitimate
  readings; actual reader discovery and locked-ROI reads follow LOH 2 / SEN 0→1→2.
  These are source observations, not accepted point decisions.
- OCR acquisition no longer stops during a rally; racket acquisition no longer
  requires a simultaneous shuttle detection. Their own view and cadence gates remain.
- Accepted source increments have durable references and unique claims. Delayed
  readings reconcile only after current frame processing, with bounded temporal
  evidence, ambiguity abstention, historical format gates and transactional retries.
  Regressed/replayed score runs and gaps require sequence consistency; no missed
  points or final scores are fabricated. Canonical OCR frames support visual review.
- Optional detector-bracket geometry is explicitly estimated and revalidated at
  classification time. It requires all two/four participants and same-episode fresh
  bracketing observations. It never promotes a carried box, invented pose or named
  actor. Default remains off pending comparative evidence.
- Perception and semantic providers use actual configured factories and typed
  ports. Independent non-badminton host execution and component replacement are
  tested. Format understanding preserves unknown/configured/inferred states and
  chronological boundaries; singles-only components have explicit capability gates.

The default stroke implementation is the rule classifier. A legacy profile name
must not advertise execution of an absent pretrained BST model. The CG-AP checkpoint
is not installed in the primary registry, and its separate exact-weight license
was not verified from the author's source/Drive metadata. No new weights are
adopted. Source-code MIT licensing is not treated as a blanket weight grant.

## Pending measured candidate results

Two explicit profile proposals are preserved privately: an FP32 control with prior
sampling, and a quality candidate with overlapping shuttle windows, denser detector/
pose sampling and optional bracket geometry. Select on India development only;
freeze before inspecting the reserved Denmark/doubles prediction results. Fresh
inference and accuracy results for the repaired pipeline are pending. No quality
improvement or production readiness is claimed from the regression counts alone.

Private reproducibility/evaluation artifacts are under
`/home/administrator/Desktop/sport-analytics/pluggable-pipeline-research-20261103`.
The original Hylo session was backed up before this phase and has not been replaced.


## Development comparison and further defects

The repaired control preserves baseline contact/class predictions and emits 66
corroborated scoreboard events instead of zero. No point events are accepted yet;
source/rally association remains ambiguous under the fragmented rally candidates.
The denser candidate has 76 predictions, 58/85 matches at ±6 frames, precision
76.3%, recall 68.2%, F1 72.0%; correct matched classes increase to 9/58 (15.5%),
with known-class coverage 77.6% and supported-class macro F1 12.2%. Joint
contact/class precision/recall are 11.8%/10.6%, and wall throughput is 8.83 FPS.
These are development results, not a finished classifier or a reserved-test claim.

Real-video review found seven of eight initially named matched actors contradicted
the name-checked annotations: default near/far score-slot ends had been treated as
physical identities. Named identity now requires separate accepted binding/review;
format and competitor names alone do not bind a track. Anonymous current detector
or explicitly bracket-estimated geometry remains available for classification.
The former named attribution is retained only in the preserved baseline.

The SS22 `hit_x`/`hit_y` columns are not treated as airborne shuttle-location truth.
Their semantics are not authoritatively documented in the reviewed source; visual
checks place several near the floor/feet. Diagnostic strips retain the raw values,
but any earlier description of those markers as shuttle pixels is superseded.
Timing, class, hitter and score metrics do not use these coordinate columns.

Further source-score tests cover a new value visible before a later rally starts,
which must not become that later rally's point, and a before-state first visible
before rally start but corroborated later, which can be used retrospectively only
once the corroborating observation is available. Missing score evidence and gaps
remain explicit; no winners or tail points are generated to reach a final total.
