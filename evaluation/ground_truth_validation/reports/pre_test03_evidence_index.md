# Evidence index for Test1–2 engineering before Test3

The active production candidate is `5ae6148`, isolated from main (`dacc05e`).
The earlier `2418ab8` Test 1 was accepted with disclosed limitations; its Test 2 was rejected for four source-confirmed missed edits. The repaired `5ae6148` fresh Test 1 workflow is complete, and independently accepted for Test2 validation with disclosed variations.
Test 2 fresh NN and separate postprocessing are complete, but mixed reference
regressions remain under diagnosis; Test 2 is not accepted. No Test 3 annotation
contents, source video download or inference have been started in this phase.
Existing historical matrices and failed attempts remain immutable.

| Evidence | Result and scope | Record |
|---|---|---|
| Original Test1/Test2 review |16original files,6/3interval reference families,422validrows,53packagedcases; partial/duplicate/generated-reference limits disclosed |[Annotation and failure review](test_01_02_annotation_and_failure_review.md) |
| Engineering specification |Actual modules, confirmed defects, rejected diagnoses and unresolved priorities |[Living specification](test_01_02_root_cause_and_improvement_spec.md) |
| c585 full Test1 |Completed but rejected:182visible-athlete rows withheld despite unchanged interval detection matrices |[Independent v2 review](../regression_tests/pre_test03_scene_v1/test01_independent_v2/REPORT.md) |
| 9992 chronological source controls |15windows,3054exactframes,25decisions;182conditional boxes restored, three additional Test2 edits recovered; not physicalrecall or fullpipeline acceptance |[Independent source review](../component_evaluations/pre_test03_scene_acquisition_v1/independent_prefix_review_v1/REPORT.md) |
| a146 fresh Test1 v3 |Failed during chunk1500–1559,1500cachedframes retained; exactfatalframe unavailable |[Runtime contract review](../component_evaluations/pre_test03_scene_contract_v1/REPORT.md) |
| 2418 contract fix |Unsupported residual staysraw, ratio staysunknown; unsupported numeric evidence rejected; sevennew focused regressions |[Separate failure case](../component_evaluations/pre_test03_scene_contract_v1/case_runtime_contract_v1.json) |
| Earlier2418 regression suites |2773main+705research=3478tests pass;702source/config/test hashes unchanged,19existingwarnings |[Contract regression index](../regression_tests/pre_test03_contract_v1/README.md) |
| Accepted full Test 1 |17,268 fresh frames; all six detection matrices retained, all 13 cuts preserved, all 182 previously lost boxes restored; independent 88-frame review complete |[Root acceptance](../regression_tests/pre_test03_contract_v1/test01_acceptance_v4.json) |
| Completed full Test 2 and postprocessing |29,296 fresh frames, original outer audit failure retained; separate postprocessing passes full own-run semantic parity and unchanged-input guards; mixed metrics are not accepted nonregression |[Test 2 workspace index](../test_02/pre_test03_2418ab8_v1/README.md) |
| Postprocessing compatibility |28 focused tests; original Test 1 report fields and CSV exact; numerical analysis/component/frame/heatmap calculations independently verified unchanged |[Independent compatibility review](../component_evaluations/pre_test03_audit_compat_v1/independent_review_v1/REPORT.md) |
| Manifest evaluator compatibility |61 focused guards; original numeric rules unchanged and native MAIN Test 1 control exact; not installed into frozen producer |[Validation v2](../regression_tests/manifest_component_evaluator_v2/REPORT.md) |
| Test 2 scene/source evidence |75 synchronized frames cover nine weak resets and source controls; independent review complete. Two Test 1 frame-number controls are explicitly excluded from Test 1 validation here |[Source bundle](../regression_tests/pre_test03_contract_v1/visual_test02_weak_barriers_v1/index.md), [scope correction](../regression_tests/pre_test03_contract_v1/test02_weak_barrier_frame_plan_v1_scope_correction.json) |
| Newly missed short Test 2 event |86 contiguous source frames11690–11775; engine starts11716 then cancels at11774 under short-exchange duration/evidence policy; root cause still under investigation |[Synchronized evidence](../regression_tests/pre_test03_contract_v1/visual_test02_lost_short_event_v1/index.md) |
| Structured engineering failures |25immutable source/contract/limitation records; allphysicalGTnull; countisnotfailurefrequency |[Engineering register v3](../failure_cases/pre_test03_engineering_v3/README.md) |
| G69 shuttle/rally diagnosis |64sourceframes,134retainedcandidate records; partialupper-edge visibility, offimageuncertainty and racketdistractor; not22visible-shuttleFNs |[Source diagnosis](../component_evaluations/pre_test03_shuttle_gap_v1/REPORT.md) |
| OCR acquisition |Generic stale-success crop hazard confirmed; full-corner replacement rejected, actual105callgap unlocks; fusedtokens remainunknown |[Contract and counterexamples](../component_evaluations/pre_test03_ocr_acquisition_v1/contract_review_v1/REPORT.md) |
| Motion/appearance alternatives |No adoption: fixed motion variants, HSV and isolated pinnedOSNet probes do not support safe athlete recovery |[Continuity investigation](../component_evaluations/pre_test03_participant_continuity_v1/REPORT.md) |

Focused and research-control counts overlap or have different scopes; never add
them into a synthetic accuracy score. Unit/runtime success, generated-reference
agreement, model-box agreement and agent visual review remain distinct from
independently labelled physical accuracy. The fresh Test1/Test2 regression gates
precede Test3 annotation preparation, paired-source download and evaluation.

## Active5ae Test1 V5 evidence

- [Final source/test gate](../regression_tests/pre_test03_scene_origin_v1/final_validation_gate_v1/REPORT.md): application2823passes plus one corrected synthetic fixture and46focusedretry; research736passes/10explicitintegrationfixtureskips. Overlapping scopes are not added.
- Fresh Test1 full workflow completed17,268frames and3,724artifactbindings; all six interval metrics exactly equal accepted2418. [Independent numerical review](../regression_tests/pre_test03_scene_origin_v1/test01_independent_v5/REPORT.md) passed with explicit point, cadence, shuttle, class and runtime variations.
- [Independent new-reset source and native structural review](../regression_tests/pre_test03_scene_origin_v1/visual_test01_v5_new_reset_review_v1/REPORT.md):14114 is a real same-camera edit; all288codec24packets and164relativeproofs pass.
- Test2V5 full workflow completed all29,296frames with same frozen5ae; independent review confirms mixed metrics and coarseFN33, so main promotion is on hold. Main promotion/push and source-preserving removal of all five auxiliary worktrees/branches are explicitly authorized after both videos pass.

- [Completed Test2V5 workspace and mixed metrics](../test_02/pre_test03_5ae6148_v1/README.md). All four lost edits are recovered; short-rally/cadence limitations remain under diagnosis before any merge.
