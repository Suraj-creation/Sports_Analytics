# Test-video benchmark collection

**Retention update:** four historical artifact roots were deleted by request. Current runs and all eight analysis-video links are retained; some older run links now expose compact records only. Read the [retention notice](RETENTION_NOTICE.md) before attempting historical replay.

Tests **1, 2, 3, 4, 6, 7, 9, 10**. Tests **5 and 8** are excluded from the evaluated-video collection.

Start with [the comprehensive ground-truth evaluation](reports/consolidated/COMPREHENSIVE_EIGHT_VIDEO_GROUND_TRUTH_EVALUATION.md), then [the consolidated summary](reports/consolidated/CONSOLIDATED_SEQUENTIAL_BENCHMARK_REPORT.md).

## Layout

- `reports/consolidated/`: full benchmark, comparison and cumulative reports.
- `reports/test_XX/`: per-video evaluation, diagnosis, failure analysis and reproduction reports.
- `reports/test_01_investigation/`: earlier benchmark audits, temporal/contact/shuttle/player investigations and development results.
- `reports/shared_component_and_pipeline/`: shared validation, performance, generalisation, provenance and readiness reports. Mixed-video reports keep their original scope statements.
- `research_data/`: existing evaluation tables, failure inventories and research JSON/CSV/HTML files.
- `videos/test_XX/`: each video’s annotations, evaluation values, predictions, diagnosis, complete run and retained media through links to preserved artifacts.
- `historical_evidence/`: prior baselines, failed attempts, experiment history and final audit artifacts. These historical roots can also contain incidental unrelated validation footage; they are not additional benchmark results.
- `reproduction_tools/`: links to existing research/evaluation scripts.
- `provenance/`: frozen configuration identities, input/source inventories and original protocol.

Reports and research data are copies; existing source files and immutable evaluation records remain in place. Markdown file links in copied reports are rebased so they continue to resolve. Large datasets, complete runs and videos are directory/file symlinks to their existing local locations; this folder is a local collection, not a standalone export.

## Evaluated videos

| Test | GT rallies | Predictions | TP / FP / FN | Precision | Recall | F1 | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | 36 | 36 | 36 / 0 / 0 | 1.000000 | 1.000000 | 1.000000 | [Test 1](videos/test_01/) |
| 2 | 73 | 75 | 68 / 7 / 5 | 0.906667 | 0.931507 | 0.918919 | [Test 2](videos/test_02/) |
| 3 | 19 | 24 | 18 / 6 / 1 | 0.750000 | 0.947368 | 0.837209 | [Test 3](videos/test_03/) |
| 4 | 41 | 46 | 38 / 8 / 3 | 0.826087 | 0.926829 | 0.873563 | [Test 4](videos/test_04/) |
| 6 | 42 | 47 | 35 / 12 / 7 | 0.744681 | 0.833333 | 0.786517 | [Test 6](videos/test_06/) |
| 7 | 30 | 32 | 28 / 4 / 2 | 0.875000 | 0.933333 | 0.903226 | [Test 7](videos/test_07/) |
| 9 | 82 | 84 | 69 / 15 / 13 | 0.821429 | 0.841463 | 0.831325 | [Test 9](videos/test_09/) |
| 10 | 93 | 98 | 85 / 13 / 8 | 0.867347 | 0.913978 | 0.890052 | [Test 10](videos/test_10/) |

## Video retention

All eight canonical analysis proxies remain accessible under each `videos/test_XX/media/` folder. Retained full original videos for Tests 1 and 7 are linked there too. Working originals for Tests 2, 3, 4, 6, 9 and 10 were previously deleted after artifact verification, as requested for storage conservation. They were not restored or re-downloaded. [Media inventory](media_inventory.json) records this distinction and the original Drive folder.

## Report catalogue

### consolidated

- [COMPREHENSIVE_EIGHT_VIDEO_GROUND_TRUTH_EVALUATION.md](reports/consolidated/COMPREHENSIVE_EIGHT_VIDEO_GROUND_TRUTH_EVALUATION.md)
- [CONSOLIDATED_SEQUENTIAL_BENCHMARK_REPORT.md](reports/consolidated/CONSOLIDATED_SEQUENTIAL_BENCHMARK_REPORT.md)
- [SEQUENTIAL_BENCHMARK_INDEX.md](reports/consolidated/SEQUENTIAL_BENCHMARK_INDEX.md)
- [TEST1_TEST2_COMPARISON.md](reports/consolidated/TEST1_TEST2_COMPARISON.md)

### shared_component_and_pipeline

- [AGENT_ORCHESTRATION_AUDIT.md](reports/shared_component_and_pipeline/AGENT_ORCHESTRATION_AUDIT.md)
- [ANALYTICS_CHECKPOINT_REPORT.md](reports/shared_component_and_pipeline/ANALYTICS_CHECKPOINT_REPORT.md)
- [CODEBASE_CLEANUP_REVIEW.md](reports/shared_component_and_pipeline/CODEBASE_CLEANUP_REVIEW.md)
- [CURRENT_BADMINTON_PIPELINE_TECHNICAL_REPORT.md](reports/shared_component_and_pipeline/CURRENT_BADMINTON_PIPELINE_TECHNICAL_REPORT.md)
- [DOUBLES_VALIDATION_REPORT.md](reports/shared_component_and_pipeline/DOUBLES_VALIDATION_REPORT.md)
- [GENERALIZATION_EVALUATION_REPORT.md](reports/shared_component_and_pipeline/GENERALIZATION_EVALUATION_REPORT.md)
- [GPU_PERFORMANCE_REPORT.md](reports/shared_component_and_pipeline/GPU_PERFORMANCE_REPORT.md)
- [PIPELINE_COMPONENT_VALIDATION.md](reports/shared_component_and_pipeline/PIPELINE_COMPONENT_VALIDATION.md)
- [PIPELINE_GENERALIZATION_REPORT.md](reports/shared_component_and_pipeline/PIPELINE_GENERALIZATION_REPORT.md)
- [PIPELINE_PERFORMANCE_REPORT.md](reports/shared_component_and_pipeline/PIPELINE_PERFORMANCE_REPORT.md)
- [PIPELINE_REMAINING_ISSUES.md](reports/shared_component_and_pipeline/PIPELINE_REMAINING_ISSUES.md)
- [PIPELINE_REPAIR_IMPLEMENTATION_REPORT.md](reports/shared_component_and_pipeline/PIPELINE_REPAIR_IMPLEMENTATION_REPORT.md)
- [PIPELINE_REPAIR_PLAN.md](reports/shared_component_and_pipeline/PIPELINE_REPAIR_PLAN.md)
- [PRODUCTION_ADDITIONAL_DATA_PROVENANCE.md](reports/shared_component_and_pipeline/PRODUCTION_ADDITIONAL_DATA_PROVENANCE.md)
- [PRODUCTION_BOUNDARY_REVIEW.md](reports/shared_component_and_pipeline/PRODUCTION_BOUNDARY_REVIEW.md)
- [PRODUCTION_CACHE_COMPLETION_PROVENANCE_REPORT.md](reports/shared_component_and_pipeline/PRODUCTION_CACHE_COMPLETION_PROVENANCE_REPORT.md)
- [PRODUCTION_CALIBRATION_SAVE_REPORT.md](reports/shared_component_and_pipeline/PRODUCTION_CALIBRATION_SAVE_REPORT.md)
- [PRODUCTION_COMPONENT_INVENTORY.md](reports/shared_component_and_pipeline/PRODUCTION_COMPONENT_INVENTORY.md)
- [PRODUCTION_CONTACT_ASSOCIATION_REVIEW.md](reports/shared_component_and_pipeline/PRODUCTION_CONTACT_ASSOCIATION_REVIEW.md)
- [PRODUCTION_CONTACT_SHOT_REPORT.md](reports/shared_component_and_pipeline/PRODUCTION_CONTACT_SHOT_REPORT.md)
- [PRODUCTION_MEDIA_COMPATIBILITY_REPORT.md](reports/shared_component_and_pipeline/PRODUCTION_MEDIA_COMPATIBILITY_REPORT.md)
- [PRODUCTION_PRODUCT_SMOKE_REPORT.md](reports/shared_component_and_pipeline/PRODUCTION_PRODUCT_SMOKE_REPORT.md)
- [PRODUCTION_READINESS_ANNOTATION_PROTOCOL.md](reports/shared_component_and_pipeline/PRODUCTION_READINESS_ANNOTATION_PROTOCOL.md)
- [PRODUCTION_READINESS_AUDIT.md](reports/shared_component_and_pipeline/PRODUCTION_READINESS_AUDIT.md)
- [PRODUCTION_READINESS_EXPERIMENT_RESULTS.md](reports/shared_component_and_pipeline/PRODUCTION_READINESS_EXPERIMENT_RESULTS.md)
- [PRODUCTION_READINESS_FINAL_REPORT.md](reports/shared_component_and_pipeline/PRODUCTION_READINESS_FINAL_REPORT.md)
- [PRODUCTION_READINESS_ROADMAP.md](reports/shared_component_and_pipeline/PRODUCTION_READINESS_ROADMAP.md)
- [PRODUCTION_READINESS_VALIDATION_MATRIX.md](reports/shared_component_and_pipeline/PRODUCTION_READINESS_VALIDATION_MATRIX.md)
- [PRODUCTION_RELEASE_INDEPENDENT_REVIEW.md](reports/shared_component_and_pipeline/PRODUCTION_RELEASE_INDEPENDENT_REVIEW.md)
- [PRODUCTION_SCENE_REPORT.md](reports/shared_component_and_pipeline/PRODUCTION_SCENE_REPORT.md)
- [PRODUCTION_TEMPORAL_ISSUE_RECOMMENDATIONS.md](reports/shared_component_and_pipeline/PRODUCTION_TEMPORAL_ISSUE_RECOMMENDATIONS.md)
- [participant-annotation-protocol.md](reports/shared_component_and_pipeline/participant-annotation-protocol.md)
- [shot-annotation-protocol.md](reports/shared_component_and_pipeline/shot-annotation-protocol.md)
- [tracking-annotation-protocol.md](reports/shared_component_and_pipeline/tracking-annotation-protocol.md)

### test_01_investigation

- [NEXT_SESSION_HANDOFF.md](reports/test_01_investigation/NEXT_SESSION_HANDOFF.md)
- [benchmark_audit.md](reports/test_01_investigation/benchmark_audit.md)
- [component_test_report.md](reports/test_01_investigation/component_test_report.md)
- [contact_event_audit.md](reports/test_01_investigation/contact_event_audit.md)
- [contact_event_experiments.md](reports/test_01_investigation/contact_event_experiments.md)
- [experiment_matrix.md](reports/test_01_investigation/experiment_matrix.md)
- [final_benchmark_report.md](reports/test_01_investigation/final_benchmark_report.md)
- [implementation_roadmap.md](reports/test_01_investigation/implementation_roadmap.md)
- [improvement_strategy.md](reports/test_01_investigation/improvement_strategy.md)
- [modularity_and_reliability_plan.md](reports/test_01_investigation/modularity_and_reliability_plan.md)
- [next_contact_scene_perception_findings.md](reports/test_01_investigation/next_contact_scene_perception_findings.md)
- [next_contact_scene_report.md](reports/test_01_investigation/next_contact_scene_report.md)
- [next_evidence_tooling_review.md](reports/test_01_investigation/next_evidence_tooling_review.md)
- [next_session_experiment_plan.md](reports/test_01_investigation/next_session_experiment_plan.md)
- [next_session_final_report.md](reports/test_01_investigation/next_session_final_report.md)
- [next_session_initial_audit.md](reports/test_01_investigation/next_session_initial_audit.md)
- [next_session_root_cause_report.md](reports/test_01_investigation/next_session_root_cause_report.md)
- [next_session_validation_matrix.md](reports/test_01_investigation/next_session_validation_matrix.md)
- [next_temporal_root_findings.md](reports/test_01_investigation/next_temporal_root_findings.md)
- [player_court_pose_audit.md](reports/test_01_investigation/player_court_pose_audit.md)
- [player_tracking_experiments.md](reports/test_01_investigation/player_tracking_experiments.md)
- [production_architecture_audit.md](reports/test_01_investigation/production_architecture_audit.md)
- [rally_failure_taxonomy.md](reports/test_01_investigation/rally_failure_taxonomy.md)
- [rally_segmentation_audit.md](reports/test_01_investigation/rally_segmentation_audit.md)
- [regression_report.md](reports/test_01_investigation/regression_report.md)
- [remaining_failure_review.md](reports/test_01_investigation/remaining_failure_review.md)
- [root_cause_analysis.md](reports/test_01_investigation/root_cause_analysis.md)
- [shuttle_model_comparison.md](reports/test_01_investigation/shuttle_model_comparison.md)
- [shuttle_perception_audit.md](reports/test_01_investigation/shuttle_perception_audit.md)
- [temporal_alignment_audit.md](reports/test_01_investigation/temporal_alignment_audit.md)
- [temporal_alignment_tests.md](reports/test_01_investigation/temporal_alignment_tests.md)

### test_02

- [TEST2_COMPONENT_VALIDATION.md](reports/test_02/TEST2_COMPONENT_VALIDATION.md)
- [TEST2_EVALUATION_REPORT.md](reports/test_02/TEST2_EVALUATION_REPORT.md)
- [TEST2_FAILURE_ANALYSIS.md](reports/test_02/TEST2_FAILURE_ANALYSIS.md)
- [TEST2_REPRODUCTION.md](reports/test_02/TEST2_REPRODUCTION.md)

### test_03

- [TEST3_SEQUENTIAL_EVALUATION_REPORT.md](reports/test_03/TEST3_SEQUENTIAL_EVALUATION_REPORT.md)

### test_04

- [TEST4_SEQUENTIAL_EVALUATION_REPORT.md](reports/test_04/TEST4_SEQUENTIAL_EVALUATION_REPORT.md)

### test_06

- [TEST6_SEQUENTIAL_EVALUATION_REPORT.md](reports/test_06/TEST6_SEQUENTIAL_EVALUATION_REPORT.md)

### test_07

- [TEST7_SEQUENTIAL_EVALUATION_REPORT.md](reports/test_07/TEST7_SEQUENTIAL_EVALUATION_REPORT.md)

### test_09

- [TEST9_SEQUENTIAL_EVALUATION_REPORT.md](reports/test_09/TEST9_SEQUENTIAL_EVALUATION_REPORT.md)

### test_10

- [TEST10_SEQUENTIAL_EVALUATION_REPORT.md](reports/test_10/TEST10_SEQUENTIAL_EVALUATION_REPORT.md)

## Integrity and coverage

[Collection manifest](collection_manifest.json) records every original/copy SHA256, rebased report, deliberately excluded general research document and any pre-existing missing link. Existing historical artifacts and source annotations are unchanged. No evaluation or pipeline modification was performed.
