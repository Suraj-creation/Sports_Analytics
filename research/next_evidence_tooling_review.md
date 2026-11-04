# Evidence tooling reproduction and corrections — 2026-11-05

This review concerns H24–H26 and evidence preservation. No rally score improvement
is attributed to tooling changes. Production contact, perception and rally logic
are owned by the orchestrator and the other specialist investigations.

## H25: executor and trace-source provenance

The pre-change four-way ablation in
`artifacts/benchmarking/experiments/next_20261105_audit_provenance_red/` reproduces
the defect: a later executor inherits generator commit `af70da7` and
`source_unchanged` from the input trace, with no separately captured executor or
epoch record. The generator's record is valid for that earlier trace; it is not
proof of the later executing source. The fixed frame-119 reset also embeds a
particular format epoch into a replay tool.

The correction adds `fixed-input-executor:v1` records with actual executor SHA,
branch, relevant dirty status, exact source/harness hashes, dirty diff and source
byte snapshots, including untracked helper bytes. Generator metadata and its
hash remain separately nested under `trace_generator`. Every replay verifies
input-trace content against its generator record and checks the executing source
remains unchanged. It rejects an unsupported trace call. Epoch resets come from
the source run's folded `format_decision` events aligned to the trace's prior
flush; the event input hash is recorded. This establishes an epoch even when
both visible snapshots are idle and private histories cannot be inspected.
The snapshot-only diagnostic helper treats equal snapshots as insufficient and
rejects missing/unexplained transitions. No annotation determines an epoch.

`run_fsm_ablations.py` now accepts an explicit new output path and records actual
FSM-loop timing separately from loading, export and evaluation. Both tools take
FPS from their source metadata. Their baseline and label selection remain
explicitly Test 1 specific; these are not generic new-dataset inference tools.

Eleven focused provenance tests pass, including arbitrary frame-41/frame-480 epoch changes,
continued state at frame 119, ambiguous or decreasing trace identity, equal idle
snapshots, unexplained transitions, exact dirty/untracked-byte snapshots,
source mutation detection, overwrite refusal, explicit equal-idle format resets,
missing matching flushes and retracted decisions. Tests use controlled temporal
records and a small temporary Git repository, not sporting labels. Six additional
run-comparison integrity tests cover contiguous frame identities and folded events.

Executed real fixed-input checks after the final source change:

```bash
source ../gpu-env.sh
pytest -q tests/benchmarking/test_executor_provenance.py
python research/run_evidence_ablations.py \
  --source artifacts/benchmarking/experiments/evidence_feature_replay_v1 \
  --output artifacts/benchmarking/experiments/next_20261105_audit_provenance_event_epochs
python research/run_fsm_ablations.py \
  --output artifacts/benchmarking/experiments/next_20261105_audit_fsm_event_epochs
```

All eight variant prediction CSVs are byte-identical and all complete metrics
objects equal their corresponding historical runs. All source snapshot bytes
match their recorded hashes. Generator commits remain `af70da7` or `b773e20`,
while the executor is correctly recorded as HEAD `64d098b` plus its exact dirty
source snapshots. The observed reset frame is still 119 for these actual traces,
but the implementation no longer assumes that number.

Detailed comparison and timings are in
`next_20261105_audit_integrity/h25_event_epochs_comparison.json`; red/green/final logs and
earlier iterations are preserved. These repeated temporal loops ran alongside
the orchestrator's control worker and are not isolated runtime comparisons,
fresh GPU runs or new datasets.

## H24: empty comparison schema

The original source writes a zero-byte comparison CSV for empty ground truth.
The reproduced artifact is
`next_20261105_audit_integrity/empty_export_reproduction/`. Two new regression
cases, with empty predictions and with one unmatched prediction, both fail at
the missing CSV header. The red test log is `h24_red.log` in the integrity
directory. After the fresh control completed and its source hashes passed,
the correction defined the existing 20-column comparison schema independently
of rows and always wrote its header. Matching, numerical rules and the primary
seven-column prediction CSV remain untouched.

All 63 benchmark tests pass. Full metrics JSON and every 36-row comparison CSV
are byte-identical for the frozen original, v1 and the new control, using each
recorded FPS representation (`30.0` in original metrics, `30` in v1/control).
The empty comparison now has its 20-column header. Exact checks are in
`next_20261105_audit_h24_bytes/parity.json`; test/lint/format results are in
`next_20261105_audit_integrity/h24_h25_tests_green.log`. A preceding check passed
integer `30` to all runs and therefore reserialized only the original JSON FPS
as `30`; its numeric metrics and comparison bytes were equal. That preliminary
artifact remains preserved in `next_20261105_audit_h24_green/`.

## H26: safe repeats and limits

`research/next_evidence_validate.py --output NEW_DIRECTORY` refuses an existing
output and verifies all pinned baseline files, historical Git source, inputs,
weights, all 28 historical experiment metric objects and fresh case artifacts.
The actual repeat `next_20261105_audit_reproducible/validation.json` contains 2,174
passing checks. The historical hardcoded finalizer and report-generating audit
scripts were inspected and were not run. The new helper writes only its new
directory; it never regenerates historical reports.

`next_evidence_compare_runs.py` compares each completed run's own frame records,
model/backend/fallback bindings and folded contact/stroke timestamps and rally
end reasons. It rejects missing/duplicated frame identities and ambiguous cache
selection. No ground-truth values are read. Its self-comparison sanity check
verifies 17,268 exact frame records, 11,767 raw shuttle observations, 447 live
contacts/strokes and all 39 interval/end-reason pairs. This self-check is not
independent inference. The later comparison against the orchestrator's completed
`next_20261105_fresh_control` verifies a second actual model run: all 17,268 frame
records, 447 live contact timestamps, 447 stroke timestamps, all 39 interval/end
reason pairs and prediction CSV bytes are exact. Actual backend/model/fallback
records, source/proxy hashes and FPS are equal. The artifact is
`next_20261105_audit_repeat_control/comparison.json`. This closes the one-repeat
gap for this source/configuration; it does not establish determinism on every
device or generalization. The comparator itself remains artifact analysis,
even when both input artifacts were produced by real neural inference.

H19 remains an untriggered non-CFR source-mapping risk. H20 remains a real-browser
HLS seek/callback evidence gap: the existing Playwright package is present, but
its browser cache and a Chromium executable are absent, and the existing review
script's default browser path is Windows-specific. System Firefox alone does
not establish a compatible Playwright runtime. No browser installation or
deployment change was made. H21 requires isolated runtime profiling; H23 requires
independently reviewed footage and labels.
H27/H28 remain non-causal warnings/maintenance evidence. None is marked fixed
by an artifact hash or a software-test pass.
