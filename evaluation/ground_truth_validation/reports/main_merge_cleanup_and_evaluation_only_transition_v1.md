# Main integration and sequential evaluation transition

Existing production fixes were fast-forwarded and pushed to `main` at `88aa0ad47d6be8dc1f073d0297efdb430b6ceaa0`. All six temporary branches/worktrees were removed after remote reachability, clean status and shared-symlink checks. Only main remains. The 102 focused post-integration checks passed.

The user explicitly replaced the prior Test1/2 acceptance gate with immediate publication and evaluation-only processing. This is not an assertion of complete nonregression: the preserved Test2 full run had mixed reference metrics and one additional missed short coarse-reference event. Test1 V7 completed fresh inference and evaluation; visual acceptance remains distinct. No new Test2 V7 inference was started.

The downloaded Test2 video was removed after verifying all 5,740 retained V5 artifact hashes, source identity and reports. Original annotations, predictions, logs, metrics and source archives remain intact.

Test3 was restored from Drive with its exact historical SHA256 and byte count, then started through the actual native pipeline in main on physical GPU1. No pipeline changes, evaluator matching changes or threshold tuning are authorized during this sequence.

Sequence: Test3 → Test4 → Test6 → Test7 → Test9 → Test10. Tests5/8 remain excluded. Each video requires its actual annotation inventory, all applicable component comparisons, native completion, runtime/resources, visual evidence and preservation checks before its owned raw/proxy media is removed and the next video is downloaded. Unsupported metrics remain unavailable, with requirements explained.

[Permanent integration snapshot and cleanup receipts](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/main_integration_v1)

[Live sequential evaluation status](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/evaluation_only_v1/status.json)

[Diagnosis and proposed fixes](evaluation_only_diagnosis_spec.md)
