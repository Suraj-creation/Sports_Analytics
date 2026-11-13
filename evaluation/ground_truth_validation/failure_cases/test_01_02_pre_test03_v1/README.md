# Test1–2 preserved evidence review, before Test3

The main report is [annotation and failure review](../../reports/test_01_02_annotation_and_failure_review.md).

- `failure_database.jsonl`:53 unique packaged rally cases, each with both fresh-run arm observations, source hashes, exact frame windows, original case evidence, signal/state coverage, overlapping predictions and prior baseline gate/source diagnostics.
- `reference_rows.jsonl`:422 valid rows across six Test1 and three Test2 reference families, including raw CSV values, data rows/CSV lines and complete before/after row metrics.
- `component_cases.json`:17 separate component/annotation/reporting findings, with root-cause status, proposed investigation/fix prerequisites, validation and exact evidence links. These do not inflate the53 rally-case count.
- `reference_metrics.json`, `mixed_iou_exact.json`:complete reference matrices and exact rational explanation for six changed intervals with stable one-to-one assignments.
- `annotation_inventory.json`:all16 original Test1/2 file hashes/schemas. Partial Full2 and all seven Test2 originals are preserved, including duplicate shuttle aliases.
- `visual_review/`:14 newly inspected source contact sheets, exact input image hashes and agent review limits. Static source sampling is not exhaustive physical adjudication.
- `source_snapshots/`:preserved current source bytes used for module inspection; exact historical execution hashes remain in original run receipts.
- `input_provenance.json`, `review_completion.json`, `validation.json`:consumed evidence bindings, scope and validation results.

Reproduce only in a new review version if the preserved source inspection has changed. This folder's builders write only here and the named report; original inputs are read-only. Use the existing server runtime:

```bash
source ../gpu-env.sh
.venv/bin/python evaluation/ground_truth_validation/failure_cases/test_01_02_pre_test03_v1/build_failure_database.py
.venv/bin/python evaluation/ground_truth_validation/failure_cases/test_01_02_pre_test03_v1/write_review.py
.venv/bin/python evaluation/ground_truth_validation/failure_cases/test_01_02_pre_test03_v1/validate_review.py
```

No inference, pipeline changes, original annotation edits or Test3 input access is performed. Generated reference disagreement and agent visual findings do not become physical GT or AP/IDF1/HOTA/PCK/contact/stroke/winner accuracy.
