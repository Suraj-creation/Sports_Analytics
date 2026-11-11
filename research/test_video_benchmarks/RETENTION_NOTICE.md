# Historical evidence retirement — 11 November 2026

The user explicitly requested deletion of these external directories after the disk review:

- `pipeline-repair-runs-20261105`
- `test2-runs-20261105`
- `production-readiness-runs-20261105`
- `backups`

Their large historical caches, databases, staged model copies, frame collections and auxiliary experiment evidence have been removed. This is not a complete archive: old absolute paths recorded in historical reports/receipts no longer resolve, and the deleted runs cannot be presented as currently replayable complete artifacts.

Before removal, compact primary-run predictions/events/logs/metadata, original Test1/Test2 protocols and executed sources, completion/evaluation records, publication receipts and exact old timestamp-helper source were preserved under `../sequential-benchmark-20261106/retired-artifact-records-20261111/`. The local collection's historical evidence links now lead to those explicitly labelled partial records. Original Test1/Test2 analysis proxies were copied and hash-verified under ignored `data/benchmarking/test1/retained_historical_proxy.mp4` and `data/benchmarking/test2/retained_historical_proxy.mp4`; all eight collection analysis-video links remain accessible.

Six otherwise-unreferenced historical Git states were retained in local `refs/archive/retired-backups-20261111/` before deleting the recovery bundles. These are archival refs, not active branches or extra worktrees.

The current `ground-truth-validation-artifacts-20261110` Test1 baseline/post-fix runs, the sequential benchmark folder, original Part2 annotations, retained source videos, canonical models and runtime environment remain intact. No current model, threshold, annotation or measured score was changed.

The active timestamp verifier is now tracked at `research/normal_timestamp_audit.py`; current Test1 orchestration uses this maintained location. The tracker comparison's Test2 media path points at the exact retained historical proxy.

See local `preservation_manifest.json`, `deletion_receipt.json` and per-retired-root inventories in the retained compact-record directory for file hashes, explicit data loss and reclaimed-space accounting. Human-readable reports remain published; local raw evidence was never a GitHub backup.
