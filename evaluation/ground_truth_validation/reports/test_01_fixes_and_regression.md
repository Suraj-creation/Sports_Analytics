# Test1 code fixes and fresh before/after regression

Three code defects were fixed in the actual current pipeline after preservation and isolated regression tests: reopened-rally cut frontier, duplicated source-score-transition mapping votes, and transformed detector-foot projection. No threshold/model/profile or original annotation changes.

## Actual video evidence

Primary baseline detection: `{"ground_truth_count": 36, "predicted_count": 36, "matched_count": 36, "true_positives": 36, "false_positives": 0, "false_negatives": 0, "precision": 1.0, "recall": 1.0, "f1": 1.0}`

Post-fix detection: `{"ground_truth_count": 36, "predicted_count": 36, "matched_count": 36, "true_positives": 36, "false_positives": 0, "false_negatives": 0, "precision": 1.0, "recall": 1.0, "f1": 1.0}`

Prediction CSV byte-identical: **True**. Primary metrics equal: **True**.

These baseline Test1 observations did not trigger the three reproduced edge contracts. Identical video metrics demonstrate a regression-preservation result, not a new physical accuracy gain. Do not report all semantic/annotation limitations fixed: independent box/keypoint/contact/identity labels, conflicting/partial scores and model-generated reference provenance remain explicit.

Full comparison: [before_after_comparison.json](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_01/improved_v1/before_after_comparison.json).

Matrix: [all-data evaluation matrix](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/reports/test_01_evaluation_matrix.md).

Test2 has not started. Remaining observed failure hypotheses require adjudicated source evidence rather than fitting the generated timing labels.
