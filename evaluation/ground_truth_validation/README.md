# Ground-truth validation and sequential diagnosis

This is the new annotation-driven investigation, separate from the historical eight-video benchmark in `research/test_video_benchmarks/`.

Sequence: inventory and annotation understanding → current-source Test1 fresh baseline → all-reference comparisons and synchronized visual diagnosis → isolated measured fixes where supported → before/after regression → Test2, continuing in order. No later video starts automatically before the previous test passes these gates. Original data, videos and historical baselines remain untouched.

- `dataset_inventory/`: whole-file hashes, every CSV schema/column profile, provenance, reference documents, component eligibility and live Drive listing.
- `test_01/` … `test_10/`: original annotation references, predictions/metrics, visual evidence, diagnostics, metadata and logs. Missing data is recorded explicitly, never as zero accuracy.
- `component_evaluations/`, `failure_cases/`, `regression_tests/`, `reports/`: centrally reviewed findings and subsequent evidence.
- `orchestration/status.json`: actual execution state and next-video gate.

Existing protected executors require generated runs outside the source repository. Fresh execution artifacts live in `../ground-truth-validation-artifacts-20261110/` and are linked from the corresponding test directory. This preserves executor safeguards and provides one workspace entry point.

The current improved working-tree source, not merely the old HEAD commit, is authoritative for the new baseline. Each run snapshots source/configuration/model bindings and records dirty state. No model or production component is changed before that baseline. Agent visual reviews remain diagnostic, not newly certified ground truth.
