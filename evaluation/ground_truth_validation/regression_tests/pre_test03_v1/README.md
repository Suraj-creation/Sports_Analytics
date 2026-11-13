# Test 1–2 engineering regression before Test 3

The production baseline is `dacc05e`. The isolated candidate is
`test03-pipeline-improvements-20261111`, commit `c7cf871`, which includes
production commit `0c3c2b6`. Main is not promoted until the measured comparisons
and visual evidence have been reviewed. Numerical profiles, model/checkpoint
pins, original annotations and matching methodology remain unchanged.

## Authoritative source-frozen unit gates

- [Main suite log](candidate_final_main_regressions.log):2,570 passed,19 existing
  Starlette warnings,325.22seconds. It includes the77 benchmark tests once.
- [Main before/after source receipt](candidate_final_main_completion.json):
  exit0 and all recorded production/test bytes unchanged.
- [Research suite log](candidate_final_research_regressions.log):689 passed,
 10.07seconds, using explicit candidate source imports.
- [Lint log](candidate_final_lint.log):all checks passed.
- New regression controls cover17 temporal-integration cases,9 identity
  availability cases, track birth/confirmation/expiry/order/multiple-person
  cases and independent court-anchor/carry expiry cases. They preserve four-
  person doubles and unknown-identity semantics.

The separate runner's48 synthetic guards and renderer's32 synthetic guards
validate reproducibility/visual tooling. They are not additional physical
accuracy samples or evidence that a match has been processed.

## Preserved intermediate failures

The first broad command used a nonexistent `scripts/benchmarking/tests` path and
ran no tests. The correct directory is `tests/benchmarking`; the authoritative
combined run includes it. An intermediate broad run retained three assertions
that expected the known delayed-birth defect. The replacement tests strengthen
the original one-video-second lost-ID invariant while asserting the intended
first-observation activation contract. No evaluator or score tolerance changed.

The first research run lacked the isolated checkout's archived metric helper,
deployment-build and browser-control fixtures. Existing primary-checkout
fixtures were linked without changes. One subsequent intermediate research
invocation omitted explicit package paths and is not counted as candidate
validation. The final run uses explicit candidate `PYTHONPATH`; import proof and
all intermediate logs remain accessible. No failed attempt is overwritten.

## Fresh integrated runs

[Candidate-native runner and usage](../../orchestration/run_pre_test03_regression.md)
freeze exact source/configuration/helper/checkpoint bytes, use one physical GPU1
worker and require actual complete worker/parent/cache receipts. Inference sees
the video/profile only; evaluators read original labels after completion.

The fresh Test1 run completed all17,268 frames in1,769.01 worker seconds;
[live status](test_01/status.json) and [launch log](test01_fresh.launch.log)
retain its stages. **This candidate is not accepted:** source review confirms
lost real scene boundaries at7857 and8106 and a stale carried player box
across7857–7859. The court lease can remove a genuine off-court foreground
region; the scene observer then lacks its required two-region context.
All six interval detection counts/F1 remain unchanged, and the small mean-IoU
gains do not override this actual integration regression. Its output is
`../ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01/`.
The saved before state separates Test1's older full neural component baseline
from its latest `dacc05e` cached semantic contact/class control. All six interval
metrics must agree between those saved controls before comparison. The partial
Full2 precision/F1/FP remain unavailable.

Test2 requires a separate invocation after Test1 review. Its before state is
the latest complete fresh `test_02/improved_v1`, with all three supplied interval
references. It must use the same candidate source/profile/model pins. The older
pre-racket baseline is historical context, not substituted for this control.

Fresh completion is not automatic acceptance: root must inspect every metric
change and source-bound overlays. No Test3 download, original-data modification,
automatic next-video execution or cleanup occurs in this runner.
