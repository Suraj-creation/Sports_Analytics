# Generic manifest evaluator: structural compatibility validation

The generic evaluator now uses the same-root native decoder and the separately versioned scene-epoch auditor. It explicitly rejects a foreign analysis module identity or producer/tool root, even when a substitute exposes similar attributes. Native decoder failure propagates; weak positive decisions require actual epoch application and adjacent camera/confirmed format proofs. Raw hypothesis flags and all metric policies remain unchanged.

All61 focused cases pass: the existing44 guards are unchanged, with17 new cases for structural admission, native-module/root binding, decode failure, raw flags, legacy strong/unknown fallback and exact AST invariance. Every original non-orchestrator function AST is unchanged. The original evaluate() AST is also unchanged after removing only the declared structural call/provenance additions.

The actual full17,268-frame MAIN-native Test1 control completed without inference. Every original report value is exact, except the explicit provenance/input-hash expansion; all previous provenance fields are equal and the sole new provenance field is structural_compatibility. All current consumed inputs rehash unchanged. No weak resets occur in this MAIN-native control. It does not claim that the generic evaluator has run from candidate2418 or on Test3.

The original44-guard validation receipts and original outputs are preserved. The old-to-new input hash comparison has two expected code changes: this newly updated generic evaluator, and a pre-existing MAIN pipeline_repair_completion.py schema-compatibility change authorized outside this task. The latter file was not edited here; actual model/resource/metric outputs remain exact. New adapter/auditor/benchmark helper bindings are retained explicitly. This is not described as all historical source hashes being identical.

The frozen postprocessing adapter/auditor/test sources still match their final implementation receipt. No helper was installed into frozen2418. No production/checkpoint/profile/annotation changes or Test3 file access occurred.

Evidence: [test log](tests_v2.log), [preserved pre-change source](before_evaluator.py), [before source receipt](before_source_receipt.json), [new structural tests](test_structural_compatibility.py), [validation receipt](verification_receipt.json). The new actual control is external at /home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/manifest_component_evaluator_v2/test01_control.
