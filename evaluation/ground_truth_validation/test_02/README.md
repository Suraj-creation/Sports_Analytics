# Test 2 ground-truth-driven validation

Evaluation and diagnosis are complete with documented limitations. Both the
preserved baseline and the post-fix comparison processed all 29,296 frames by
fresh neural inference. The [consolidated report](../reports/test_02_consolidated_v1.md)
contains every supplied interval row, component matrix, before/after difference,
visual diagnosis, configuration, model identity and runtime measurement.

This run carries forward the completed Test 1 repairs and the inherited improved
scene, format, short-exchange and OCR implementations. Original Part2 files,
Test 1 evidence and the earlier eight-video timing benchmark remain separate.

- [Annotation inventory and component mapping](annotations/annotation_mapping.md)
- [Test 1 readiness and Test 2 diagnostic plan](diagnostics/prior_findings_and_plan.md)
- [Live execution state](orchestration/status.json)
- [Download identity verification](inputs/download_verification.json)
- [Fresh baseline artifacts](baseline_v1/)
- [Fresh post-fix artifacts](improved_v1/)
- [Baseline matrix](../reports/test_02_baseline_v1/matrix.md)
- [Post-fix matrix](../reports/test_02_improved_v1/matrix.md)
- [Independent fresh component review](fixes/fresh_component_review_v1/REVIEW.md)
- [Test 1 and Test 2 controlled semantic effects](fixes/semantic_effect_review.md)
- [Annotation/source visual review](diagnostics/annotation_visual_review/)
- [Inherited OCR fix verification](diagnostics/ocr_pairing/)

The baseline is a new full production upload with no annotation, old calibration,
roster or prior session supplied to inference. It uses the same numerical profile
as the completed Test 1 run. The executor records current source snapshots,
configuration, model hashes, backend choices, resource samples and event/cache
receipts. Its physical GPU allocation is 1; OCR remains explicitly on CPU.

The executor requires its writable run directory outside the source repository.
The workspace link points into the existing
`../ground-truth-validation-artifacts-20261110/test_02/` artifact root. Do not
replace that link with a partial copy or treat a Git push as a raw-artifact backup.

Reference comparisons distinguish coarse human-origin candidates, historical
generated predictions and single-frame manual geometry. Player slots are
anonymous observations; filled shuttle coordinates are not physical GT. Missing
box, keypoint, contact, identity and exhaustive stroke labels yield unavailable
accuracy metrics, with observed output coverage recorded separately.

The implemented code repair withholds a selected geometric racket cue when
current facial landmarks establish anatomical ambiguity; raw candidates remain
preserved. Main and research suites passed 3,204 tests. Test 1's six reference
metric sets remain identical in a full fixed-perception semantic regression;
that check is explicitly distinct from fresh Test 1 neural inference.

All three Test 2 reference F1 scores are unchanged. Coarse annotation mean IoU
changes 0.833215 to 0.830665; generated rally-reference IoU changes 0.848135 to
0.849311. These mixed results do not establish improved physical contact or
racket accuracy. Anonymous player tracking, shuttle gaps, an unrecognized edit,
raw racket distractors, identities and scoring remain documented limitations.
Missing reviewed boxes, joints, contacts and identity/outcome bindings leave the
corresponding accuracy metrics unavailable, rather than zero.

Final artifact manifests and exact owned-download cleanup receipts belong in
[retention](retention/). Only the newly downloaded Test 2 source is eligible for
deletion after successful verification; annotations, proxies, predictions,
logs, models, visual evidence and all previous benchmark records are retained.
The receipt records whether deletion actually occurred. No Test 3 was started.
