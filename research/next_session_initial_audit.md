# Next-session initial audit — 2026-11-05

The frozen evidence is intact and the existing v1 evaluator result reproduces
exactly. This audit changes no prediction, annotation, model, historical report
or application deployment. It is evaluation and provenance work, not fresh
perception inference.

## Repository and environment

At audit start the working tree was clean on `Benchmarking`, HEAD
`64d098b72e592998222f81bf858163b45496d799`. The required checkpoints are ancestors;
local `main` is `301baf08be5e989dd0ed93cb885733c3cf6f356a`. The current branch is
not reset to the historical inference source. Existing ignored artifacts,
application sessions and unrelated processes remain in place.

`AGENTS.md`, `CODEX.md`, `CLAUDE.md`, the complete handoff and structured failure
inventory were read before changes. The user's explicit `Benchmarking` instruction
supersedes the older main-branch wording in the local instruction files.
The orchestrator and specialist audits read the mandatory reports and source-bound
evidence; this provenance audit additionally inspected benchmark, temporal and
architecture audit pairs, benchmark tool documentation, evaluator and ablation
sources, and all sections of the three JSON evidence registers below.

The environment-runtime skill was read. Its managed-environment status tool is
not exposed in this session; local runtime checks supply the environment evidence.
No network credentials were read and no remote connection was needed. Commands
source `../gpu-env.sh` and use the existing `.venv/bin/python`:

| Check | Observed |
| --- | --- |
| Python | 3.12.12 |
| Torch / CUDA build | 2.14.1+cu126 / 12.6 |
| Torch CUDA available | true |
| GPUs / driver | two GTX 1080 Ti, 580.178.04 |
| ONNX Runtime | 1.29.0 |
| ORT available providers | TensorRT, CUDA, CPU |
| OpenCV | 5.0.0 |
| FFmpeg | existing `.local/opt/ffmpeg-static/bin/ffmpeg` |

Initial GPU checks found both GPUs idle. Later snapshots observed the
orchestrator's Python/FFmpeg control worker; this audit avoided resource-heavy
tests during that run. Available ORT providers are environment capability,
not proof of individual-node execution. Historical `inference.json` contains
the actual model-session backend/fallback records. No environment was installed
or replaced and no unrelated process was stopped.

## Complete integrity verification

`artifacts/benchmarking/experiments/next_20261105_audit_integrity/integrity.json`
contains every expected/actual digest and the audit source identity.

The safe repeat helper checks all pinned baseline/model/input files and all 28
experiment metric objects, and refuses an existing output directory:

```bash
python research/next_evidence_validate.py \
  --output artifacts/benchmarking/experiments/NEW_EVIDENCE_AUDIT
```

Its executed repeat is `next_20261105_audit_reproducible/validation.json`.

| Evidence | Result |
| --- | --- |
| All registry baseline files | 1,766 / 1,766 SHA256 matches |
| All historical production source entries | 86 / 86 match Git blobs at recorded `301baf08` |
| Original video | `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6` |
| Ground truth | `30651cf7238924d6a5072b1dd71d34ca5839cd5b842f696e745229033ae4f887` |
| TrackNet checkpoint | `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a` |
| RF-DETR ONNX | `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e` |
| RTMPose package | `f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741` |

All input/model digests match their registry entries. Historical source hashes
are compared against the recorded Git revision; current source is expected to
contain later fixes and is not falsely required to match that older revision.
Fresh `ffprobe` verifies 1920 × 1080, nominal/average 30/1 FPS, 17,268 declared
video frames and 575.600000 seconds. This probe is not a new full decode count.
Ground truth has 36 validated seven-column intervals. Existing exact packet and
decoded alignment audits remain available as historical evidence.

Both baseline and fresh semantic traces are present. There are 288 fresh v1
perception caches. All 40 fresh failure-case manifests match their recorded
hashes; their six required files, frame ranges and trace provenance are present
and consistent. The 55-case original index and 40-case fresh index remain intact.
Per-case execution logs remain whole-session logs; they do not establish invented
frame-level log timestamps.

## Numerical reproduction and structured-register inspection

Reproduction command:

```bash
source ../gpu-env.sh
python scripts/benchmarking/evaluate_rallies.py \
  --ground-truth Part2/dataset/Test1_Full/Test1_Full_rally.csv \
  --predictions artifacts/benchmarking/experiments/fresh_image_exit_v1/predicted_rallies.csv \
  --fps 30 \
  --output artifacts/benchmarking/experiments/next_20261105_v1_evaluation_check
```

The complete metrics JSON is value-identical and the 36-row comparison CSV is
byte-identical to fresh v1. Predictions remain 39; TP/FP/FN are 35/4/1;
precision/recall/F1 are 0.8974358974 / 0.9722222222 / 0.9333333333.
Start/end MAE remain 45.7714285714 / 16.3142857143 frames. No matcher, tolerance,
denominator, endpoint or frame-index convention changed.

`structured_evidence_audit.json` in the integrity directory records recursive
inspection of every section of `experiment_results.json`, `evidence_registry.json`
and `benchmark_audit.json`; no JSON section was skipped. This is not limited to
headline F1: all 28 experiment prediction CSVs were read through the unchanged
validator and all metrics were recomputed. Every metric object is equal both to
its saved run metrics and to the experiment-results register. Rejected pilots
remain rejected; an arithmetically valid metric does not establish experiment
acceptance. All 17 benchmark-audit evidence digests match; all 36 match IDs and
boundary errors agree with reevaluation. Its findings and limitations are retained
in the new audit artifact.

The results register's entire `fresh_runtime` object equals fresh v1's own
`inference.json`; the entire post-run validation object equals its own saved
validation. The summary-generator hash matches the current historical finalizer
file. That finalizer was inspected, not run. Model fallbacks explicitly record
unavailable OSNet/player ReID; this does not license invented identities. The
historical repeat count is one full GPU run; semantic parity is not a second run.

## Reproduced tooling issues and remaining evidence limits

H24 is reproduced in `next_20261105_audit_integrity/empty_export_reproduction/`:
`save_evaluation([], [])` writes a zero-byte comparison CSV. Current source puts
header creation under `if rows`. This affects empty-input export, not Test 1
matching or metrics. A header-only correction and negative controls will be
made separately after the orchestrator releases the source freeze.

H25 is confirmed against current tooling: `run_evidence_ablations.py` inherits
trace-generator Git/source metadata into executor output, asserts the inherited
`source_unchanged`, and uses a Test 1 frame-119 flush reset. `run_fsm_ablations.py`
also fixes that epoch and output path. New tooling should record executor and
trace-source identities separately, snapshot exact harness/source bytes, derive
recorded reset epochs from trace events, and refuse existing outputs. Historical
manifests will not be rewritten to imply better provenance.

H19 remains a generic source-mapping limitation, absent from exact CFR30 Test 1.
H20 remains an untested browser/MSE seek hypothesis and cannot explain offline
hundred-frame errors. H21 performance attribution requires an isolated profile;
historical overlapping stages cannot be summed. H22 requires actual repeat
inference. H23 lacks match-disjoint reviewed footage and component labels; no
generalization, real doubles or contact/localization accuracy is established.
H26 is controlled here by explicit new paths and read-only historical evidence.
H27/H28 remain observed non-causal warning/maintenance issues, not segmentation
defects. The final investigation will attach new source-specific statuses and
results while preserving these initial observations.
