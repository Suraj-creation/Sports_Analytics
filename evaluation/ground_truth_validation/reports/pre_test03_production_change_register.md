> Current status (2026-11-12): superseded historical investigation below. Existing fixes through `88aa0ad` are now merged and pushed to main at the user’s direction. All six auxiliary worktrees and branches were removed. Mixed Test2 metrics and the short-rally limitation remain disclosed; full all-component nonregression is not claimed. Evaluation-only Tests 3, 4, 6, 7, 9, 10 now use frozen main; further fixes are deferred to the specification.

# Production changes before Test 3

The active candidate is `5ae614826e6f909defb02445386962ac13b4641a` in
`test03-scene-overlap-20261112`. Its fresh Test 1 workflow completed all 17,268 frames and is source-frozen;
independent numerical acceptance passed with disclosed variations; fresh Test2 validation completed with mixed metrics and a promotion hold. Main is still `dacc05e`; no new fixes
from this phase have been merged or pushed. The earlier `2418ab8` candidate's
Test 1 passed, but its Test 2 failed acceptance after four missed real edits were
found. Every earlier source, annotation, metric and failure remains preserved.

## Actual reusable pipeline changes

| Module | Final behavior and reason |
|---|---|
| `engine.py` — observation window | Preserve explicitly marked bounded reconstruction for ordinary missing observations; ambiguous, invalid and rejected evidence remains a barrier. Observed-only contact anchors stay observed-only. This does not enable reconstruction for rally admission or solve the G69 gap. |
| `plugin.py` — capability reporting | Retain the actual selected ReID loader/checkpoint/runtime failure in singles and unknown format instead of replacing it with an inaccurate format explanation. Reporting is distinct from identity accuracy. |
| `perception/_bytetrack.py`, `players.py` | Honor the existing minimum of one observed detection at track birth while preserving the backend association, timing and ID allocator. No detector confidence threshold is lowered. |
| `perception/players.py` — continuity | Preserve continuously fresh court-origin image hypotheses beyond a runoff; retain the actual geometric anchor separately. Missing/carry observations cannot renew freshness. An outside person cannot bootstrap a new court origin, and cuts clear temporal state before current probes are consumed. |
| `perception/foreground.py` | Maintain bounded scene-only image context independently of participant admission. Ambiguous matches preserve an unmatched old box/time within the existing lease; they cannot renew freshness or seed duplicates. The opaque keys do not identify physical or named players. |
| `perception/scene_change.py` | Preserve all bounded region measurements and require independent same-channel witnesses. A static third region cannot veto two qualified innovations. Strong image thresholds remain unchanged. |
| `perception/content.py`, `pipeline.py` | Separate a request for a fresh detector observation from authorization to reset tracking. Relative-only acquisition may request a source-bound probe; a weak reset needs two same-channel witnesses, a previously confirmed singles/doubles format, a complete strict-court current layout and raw plus camera-aligned displacement from every prior region. Unknown evidence does not acquire weak fallback authority. |
| `perception/pipeline.py` — lifecycle | Reuse a probe exactly once in normal tracking and reset before consumption when justified. Capture format context before chunk observation, independently of a format inferred later during ingestion. A standalone default format is not confirmed evidence. |
| `perception/content.py` — support validation | A raw patch residual with fewer than six usable features remains available while its adaptive ratio stays unknown. Reject unsupported finite ratios. This repairs the source-backed crash without changing feature, image or evaluation thresholds. |
| `plugin.py`, `perception_types.py`, component registry | Preserve bounded typed foreground and scene decisions in codec23, bind court geometry and relative camera claims to their source, prevent downgrade of new authority into legacy headers, retain legacy diagnostic reads and invalidate changed component/pipeline identities. |

The earlier `2418ab8` declarations were pipeline version8, tracking contract/model version5,
content contract/model version4, raw scene evidenceV4, scene decisionV3 and
perception codec23. These versions identify implementation/evidence contracts;
all actual neural checkpoint hashes and numeric profile settings are unchanged.

The first court-anchor-only timeout was rejected after withholding 182 visible
athlete rows. The final implementation above replaces that policy. Its failed
full run, source and tests remain in history; it is not an accepted accuracy gain.

## Commit lineage

| Commit | Scope |
|---|---|
| `0c3c2b6` | Initial birth, composition, capability and court-continuity engineering work. The strict court-only portion was subsequently rejected and replaced. |
| `c7cf871` | Earlier strict-expiry regression controls, retained as rejected-policy history. |
| `7ed2f73`, `5b6d429` | Separate scene context, independent witnesses and bounded ambiguity recovery. |
| `0af9f40`, `c585e35` | Schema-only completed-run compatibility and contract assertions. |
| `9992f87` | Relative scene acquisition, court/camera/format corroboration and restored continuous athlete hypotheses. |
| `a146953` | Test-only updates for synthetic historical codecs and partial constructor fixtures. Its full inference attempt exposed the low-feature validation error. |
| `2418ab8` | Correct current feature support when validating adaptive scene ratios; seven focused regressions. |

## Earlier 2418ab8 validation (retained history)

- Earlier 2418ab8 full candidate suites: **2,773 main tests + 705 research tests = 3,478 passed**.
  All 702 recorded source/config/test hashes stayed unchanged; 19 existing
  Starlette warnings remain. Focused and research-control counts overlap or
  have separate scopes and are not added to this total.
- Fresh Test 1: all 17,268 frames completed with no cached perception. All six
  interval detection matrices are unchanged. Coarse mean IoU moves from
  0.8421299051 to 0.8422842260; generated-rally mean IoU moves from
  0.8710256650 to 0.8711853074. All 13 original content boundaries remain.
- Independent coverage audit: all 182 rows lost by the rejected court timeout
  are restored with exact historical boxes. No current frame has a lower
  participant count than the original baseline. These are conditional source/
  model comparisons, not physical AP, identity accuracy or recall.
- Legacy point agreement has both improvements and worsenings. All 13,966
  common fresh-detector point errors are unchanged; some carried-frame
  comparisons change. The worst common legacy-distance increase is about
  3.99 pixels. These generated references do not establish physical foot accuracy.
- Contacts change from 445 in the latest semantic control to 451 estimates.
  Unknown classes change from 301 to 305. No independent contact or stroke
  accuracy gain is claimed; named winners and accepted points remain unavailable.
- Test 1 independent metric and 88-frame visual review are complete. Root accepted
  it for sequential cross-test validation with disclosed limitations; the receipt
  is `regression_tests/pre_test03_contract_v1/test01_acceptance_v4.json`.
- Fresh Test 2 neural inference completed all 29,296 frames with its original
  worker and parent successful and the candidate frozen. The outer workflow
  failed in the legacy report audit, which requires the old strong-image flag
  even for a validated weak court/camera/format reset. This is a postprocessing
  compatibility failure, not a failed neural run. The original failure is retained.
- Separate postprocessing and independent numeric review subsequently completed.
  Expanded source evidence exposed four real missed edits and rejected this arm.
  The new5ae6148 run is a distinct fresh experiment, not repeated postprocessing
  presented as new inference. Test3 remains gated.

The earlier 2418ab8 full Test 1 worker took 1,784.01 seconds versus 1,750.79 seconds in
the preserved full-neural baseline. Peak sampled worker GPU memory is 2,130 MiB
versus 2,124 MiB, on physical GPU1. Shared host work, cache state and workload
differences prevent a controlled performance claim.

## Evaluation tooling and rejected alternatives

Research helper changes extend schema support and preserve strict historical
codec21 recovery. Seven numerical evaluator/guard modules remain byte- and
AST-identical to the preserved review. No original annotations, matching policy,
metric threshold or prediction endpoints are changed to improve reported scores.
The reusable orchestration, manifest evaluator and renderer add provenance and
review artifacts; they do not create a parallel Test3 pipeline.

Fixed motion gates, HSV and the isolated pinned OSNet probe were not adopted
without safe recovery evidence. Full-corner OCR was rejected after zero benefit
and loss of a valid reading. The G69 audit found that the configured provider
already supports one qualified isolated alternative; six contiguous lower
observations exceed its conservative contract. No global gap, merge or
confidence threshold is tuned to fit that example. Unsupported physical metrics
stay unavailable rather than zero.

## Changed production files

- `sports/badminton/src/bai_badminton/engine.py`
- `sports/badminton/src/bai_badminton/perception/_bytetrack.py`
- `sports/badminton/src/bai_badminton/perception/components.py`
- `sports/badminton/src/bai_badminton/perception/content.py`
- `sports/badminton/src/bai_badminton/perception/foreground.py`
- `sports/badminton/src/bai_badminton/perception/pipeline.py`
- `sports/badminton/src/bai_badminton/perception/players.py`
- `sports/badminton/src/bai_badminton/perception/scene_change.py`
- `sports/badminton/src/bai_badminton/perception_types.py`
- `sports/badminton/src/bai_badminton/plugin.py`

## Active overlap repair (not yet full-video accepted)

Commit5ae6148 changes the actual reusable `perception/scene_change.py` and
`perception/content.py`, with integration in `perception/components.py` and
`plugin.py`. It measures exclusive feature origins from all previous full ROIs,
preserves full layout boxes and full-union background exclusion, and binds mask
areas/digests/source dimensions to the actual previous foreground. LK tracking
patches can overlap; statistical independence or distinct physical actors is not
claimed. Overlap-dependent unknown layouts abstain. Positive current continuity
of a non-innovating court actor or a camera-explainable layout prevents the new
ambiguous fragmentation authority.

Actual source-prefix controls recover2928/11082/22416/23279 and retain complete
continuity vetoes7703/23639 at unchanged image/model/IoU gates. Native raw schemaV5,
decisionV4, codec24, pipeline9 and content contract/model5 identify the new code.
Legacy schemas retain their old interpretation. Current full-video execution is
required because changed resets affect TrackNet background and temporal inputs.

Broad application validation recorded2823 passes and one outdated historical
codec fixture; correcting only that fixture's wire-version declaration yielded
46 focused passes. All379 application/test files were checked against that run;
only the fixture changed. Research validation recorded736 passes and10 explicit
completed-NN integration-fixture skips. The174 focused component controls overlap
these scopes and are not added. Four numerical helper changes are restricted by
whole-file AST guards to explicit schema/structural dispatch; interval matching,
thresholds, point math, annotation values and partial-reference rules are unchanged.

The user explicitly requires accepted fixes merged into main and all five
created auxiliary worktrees/temporary branches removed after verification and
source/artifact preservation. This instruction is recorded; no extra approval
is required. Worktrees remain temporarily necessary for the active frozen run.

## Test 1 V5 completed workflow; acceptance pending

The fresh `5ae6148` run completed inference and every evaluation/export/parity
stage with exit0. Its completion binds 3,724 artifact hashes, unchanged source,
annotations, original baselines and actual model identities. The outer inference
command took 1,944.84 seconds; the executor recorded 1,922.49 seconds. These scopes
include different overhead and are not directly controlled speed measurements.

All six interval results exactly reproduce the accepted `2418ab8` Test 1 results,
including mean IoUs. Independent source/structural review verified all 288 native
codec24 packets, 17,268 frames and 164 relative camera/layout proofs. The extra
reset at14114 is a real same-camera edit: both athletes abruptly relocate from
the right sideline to central positions. Current acquisition returns two fresh
boxes at14114 and two carried boxes at14115, versus zero in the original arm.
See `regression_tests/pre_test03_scene_origin_v1/visual_test01_v5_new_reset_review_v1/REPORT.md`.
Full numerical/population acceptance remains separate. No new production fixes
have been merged, pushed or cleaned up at this stage.

## Test1 V5 acceptance and fresh Test2 launch

Root accepted Test1 for sequential cross-test validation, not complete physical
accuracy. The [independent report](../regression_tests/pre_test03_scene_origin_v1/test01_independent_v5/REPORT.md) records all six unchanged interval matrices, exact182region restoration, zero lower-countframes, and source-supported14114reset. It also discloses109rawshuttleXY and107supportdifferences,36generatedpointchanges(17worse/19better),six detector-frame swaps each direction, one unknown-to-estimated-lift change, and slower observed worker runtime. No blanket unchanged-shuttle or all-components-improved claim is made.

Fresh Test2 uses the identical frozen5ae code and exact restored original source.
Frame-count preparation completed281.59seconds within its existing300second
timeout; no timeout or numerical policy changed. The actual worker is554893 on
GPU1. Merge, push and five-tree cleanup remain gated on its completed evaluation.

## Test2 V5 full workflow completed; main promotion hold

Fresh5ae Test2 completed29,296frames/489nativepackets and5,740artifactbindings,
with full semantic parity and unchanged source/model/profile/annotation guards.
Worker took3,645.819seconds; parent3,656.234seconds. Source review confirms all
four previously missed edits are recovered with two fresh athletes, removing the
stale far box at23279; both continuous controls retain no reset.

Coarse F1 moves0.9200→0.918918919(TP68/FP5/FN7), meanIoU0.830664600→0.847804618.
Generated-rally F1 moves0.918918919→0.945205479(TP69/FP4/FN4), while meanIoU
moves0.849310815→0.833925082. These mixed values do not establish all-reference
nonregression. Coarse short rally33remains missed, and active-play sparse cadence
still omits some pose observations. Independent numeric review and focused
short-event diagnosis are active; new13452source review is pending. Actual
production promotion/push and worktree removal remain on hold.
