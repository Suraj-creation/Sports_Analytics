# Test 1 rally boundary baseline

This benchmark uses **one** original `Test1_Full_rev.mp4` and the existing
`Part2/dataset/Test1_Full/Test1_Full_rally.csv`. The latter remains byte-for-byte
unchanged in its original tracked location. Related Part2 results are diagnostic
context only; they are never input to the production inference worker.

Run on branch `Benchmarking`, on the GPU server with its existing environment:

```bash
source ../gpu-env.sh
pytest -q tests/benchmarking
python scripts/benchmarking/run_test1_benchmark.py
```

For a repeat, use a **new** output directory:

```bash
python scripts/benchmarking/run_test1_benchmark.py --output outputs/benchmarking/test1-repeat
```

The baseline refuses to overwrite an existing run. Source media must already be
at `data/benchmarking/test1/Test1_Full_rev.mp4`. It is ignored by Git. The public
Drive folder contains a `video_raw` subfolder; the exact Test 1 file ID is
`1vR71QTkUYEGWy4PjXa5vfMdJEXt_OwLn`. No folder-wide download is used.
The original is never modified; the normal production CFR proxy is generated
inside the isolated output runtime. This preserves the production decoding path.

## Scope and leakage control

The default `gpu-rtx4000` profile matches the deployed `BAI_PROFILE` at baseline
creation. It uses the unmodified VOD TrackNetV3 implementation and the selected
production plugin components. The worker receives just the source path, frozen
profile name/directory and output path. No annotation path or target count is
provided. No thresholds are tuned, no manual boundaries are injected, and no
Part2 shuttle/player/rally predictions or court calibration are imported.

All current final `rally_end` events are exported, regardless of point acceptance,
official status, shot count, or winner. Provisional/cancelled starts are excluded;
the event store folds corrections/retractions. Prediction rows are sorted by
start/end frame. The primary CSV has exactly the required seven fields.
Other pipeline events are retained only as raw execution evidence; no unrelated
analytics are evaluated.

## Timebase and endpoints

Every annotation column is validated: integer boundary frames, seconds matching
frame/FPS, duration=end-start, and MM:SS truncation to whole seconds. The actual
source is independently probed and decoded to count frames. Packet presentation
timestamps are checked against a zero-origin CFR grid. Evaluation stops on a
source/proxy FPS or frame-count mismatch instead of fitting an offset.

Production event frame endpoints identify inclusive observations, but the supplied
CSV defines duration as the span **between** the boundary timestamps. Thus the
benchmark uses `[start_time, end_time)` for continuous temporal IoU and duration,
without adding a frame. It does not reuse the production payload's rounded,
inclusive duration. Predicted frame indices are integers; seconds are written
with Python's round-trip float precision. No timing-dependent frame rounding
or empirical alignment correction is used.

The related Part2 shuttle table enumerates 0..17267, and the original video has
17268 frames. CSV timestamps use frame/30 with no subtracted one-frame offset.
This establishes arithmetic compatibility with zero-based original indices;
the unavailable original annotation tool/review history leaves a potential
one-frame human labeling ambiguity. The raw labels are not changed.

## Matching and metrics

Policy `rally-boundaries-v1`, frozen before real inference:

1. A candidate pair must have continuous temporal IoU >= **0.5**.
2. Rectangular bipartite assignment with dummy unmatched slots maximizes eligible
   pair count first, then total IoU plus `1e-9/(1+boundary distance in seconds)`.
   The small proximity preference resolves near-ties; exact numerical ties follow
   the deterministic SciPy solver for fixed input order. Each interval matches at
   most once. The cardinality bonus exceeds every possible secondary-score gain.
3. TP=matched pairs, FP=unmatched predictions, FN=unmatched labels. Empty precision,
   recall and F1 denominators return zero. Unavailable conditional metrics are null.
4. Signed error is prediction minus ground truth. Start and end frame/time errors
   are separate, with MAE, median absolute error, RMSE, maximum and p90 (NumPy's
   linear percentile). Duration has signed and absolute errors. IoU coverage uses
   strict `>` for the reported thresholds. Eligibility uses `>=`.
5. Boundary tolerances include equality (±1, 3, 5, 10, 15, 30 frames). Both matched
   and all-GT denominators are reported; misses cannot disappear from the latter.
   Timing equivalents use the actual source FPS. Boundary/IoU metrics are
   conditional on matched pairs and must be read with detection recall.

Re-evaluate frozen predictions without rerunning inference:

```bash
python scripts/benchmarking/evaluate_rallies.py \
  --ground-truth Part2/dataset/Test1_Full/Test1_Full_rally.csv \
  --predictions outputs/benchmarking/test1/predicted_rallies.csv \
  --fps 30 --output outputs/benchmarking/test1-reevaluation
```

Use the audited FPS recorded in metadata for any future source. Explicit
`--gt-frame-base` and `--pred-frame-base` options support known one-based tables;
they are not searched for or optimized. The API also supports an explicit
timestamp origin. Mixed-rate CSVs must be transformed with an independently
established mapping before frame errors can be compared.

## Evidence and reproducibility

Metadata records source/label/profile/model hashes, Git SHA and branch, source
file hashes (including dirty-state provenance), evaluator hashes, effective
profile, actual providers and CUDA precision, selected component fingerprints,
timeline checks and execution date. `inference.json` records degradation and
perception runtime details. `execution.log`, raw SQLite events, tracks and
perception caches are preserved locally under the isolated output directory.
Large artifacts and raw events/logs are not added to Git. Small CSVs and audit
reports remain reviewable. Existing application sessions and models are reused
without reanalysis or replacement.

`executed_scripts/` preserves the scripts used to launch the initial baseline.
The final evaluator adds median signed errors and explicit row-level absolute
time errors; its assignments and all original numeric metrics are checked against
the initial evaluation before publishing the extended artifacts. Metadata records
both script versions and this postprocessing verification. These additions do
not change predictions, matching, or detection thresholds. The original evaluation
is retained in `initial_evaluation/`. Future runs snapshot their current scripts
and produce the full report automatically. The report alone can be regenerated:

```bash
python scripts/benchmarking/report_test1_benchmark.py --output outputs/benchmarking/test1
```

Synthetic evaluator tests cover exact/shuffled/global assignment, isolated start
and end errors, missing/extra/duplicate/overlapping intervals, counts, no matches,
invalid and missing timestamps, alternate rates, explicit frame bases, inclusive
end differences, and exact prediction schema. They allocate no model or GPU
inference tensors and install no packages.
