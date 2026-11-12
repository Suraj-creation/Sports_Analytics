# Candidate-native fresh Test 1–2 regression

This orchestration runs one exact original video through the actual isolated production checkout on GPU1. It freezes source/config/model inputs, preserves original annotations and historical results, runs the original numerical comparison, and writes a new immutable output. It never automatically downloads/deletes media or advances to Test3.

## Explicit roots

The driver can live in the candidate while using the primary checkout's original annotations, historical reports and status workspace. `SPORTS_ANALYTICS_PRIMARY_WORKSPACE` configures **only those workflow locations**. Native production imports, recorded worker source paths, decoder ROOT and runtime PYTHONPATH remain bound to `--pipeline-root`; no native module is rebased or monkeypatched.

```bash
source /home/administrator/Desktop/sport-analytics/gpu-env.sh
SPORTS_ANALYTICS_PRIMARY_WORKSPACE=/home/administrator/Desktop/sport-analytics/Sports_Analytics \
  .venv/bin/python evaluation/ground_truth_validation/orchestration/run_pre_test03_regression.py \
  --test 1 --pipeline-root /absolute/isolated-candidate \
  --video /absolute/exact-original-video.mp4 \
  --output /absolute/new-external-output --check-only
```

Remove `--check-only` only after the candidate is frozen and its regressions pass. Existing output directories are rejected. Test2 requires the exact separately restored video, with its original source hash. Only one full fresh video run is permitted by the orchestration lock/GPU lease.

## Numerical and structural compatibility

The original interval matching, eligibility, tolerances, partial-reference rules, point calculations, boundary/duration errors and annotation bytes remain unchanged. Whole-file AST equality permits only the exact codec24 catalogue/completion metadata extensions and one explicit structural-audit dispatch in each canonical component evaluator. Seven adverse mutations of matching/coordinate/NULL/FPS/dispatch/future-codec rules are independently rejected. All other common helper files must be byte-identical to the primary workspace.

Codec24 uses native decoding of V5 feature-origin/V4 layout evidence. The structural audit checks actual previous-frame foreground across packets, source camera/calibration, confirmed format, overlap-dependent abstentions and real content epochs. Raw measurements and unknowns are preserved; matching and metric arithmetic are not relaxed. Historical codec21 recovery remains strictly codec21.

Execution records exact primary workspace, producer/tool roots, commit/dirty patch, original SHA, all62 original annotation hashes, model/checkpoint/environment/configuration, source snapshots, runtime/resource samples and full own-run semantic replay parity. Exact executable tool dependencies are archived so accepted evidence can survive removal of temporary worktrees.

Full-run completion means execution/evaluation artifacts exist; it does not establish physical accuracy or root acceptance. Independent metrics/source comparison and regression investigation are required before promotion. Main integration and cleanup occur only after verification; reports, predictions, logs, annotations and source evidence remain preserved.
