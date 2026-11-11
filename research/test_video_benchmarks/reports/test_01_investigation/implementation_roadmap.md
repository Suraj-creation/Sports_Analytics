# Implementation roadmap and ownership

## Completed investigation controls

- Orchestrator owns integration, shared schemas, evidence registry and acceptance.
- A/B/C/D/E/F/G own separate named audit reports/helpers only; no concurrent
  production-file editing is permitted.
- All original media, annotations and baseline artifacts remain immutable.
- Full baseline evaluator and86source-module/active-checkpoint hashes verified.
- Exact production semantic replay and55source-bound diagnostic packages built.
- Existing full baseline suite:1725passed,19deprecation warnings.

## Completed gate before the first production edit

All seven specialist reviews and the ranked diagnosis/alternative explanations
were consolidated and committed at `3859f83` before production edits. The initial
experiment plan and acceptance criteria were frozen with that investigation.

## Incremental work after the diagnosis gate

1. Add focused failing tests for proven stationarity-buffer, contact-history and
   motion-confirmation defects. Fix only their owner module; default-independent
   provider, checkpoint/reset, singles/doubles and existing scoring behavior stay
   covered. Measure each intervention independently on recorded real inputs.
2. Add a typed sport-owned optional evidence interface/provider; retain the
   original rally port unchanged for independent implementations. Build inputs
   from the frame-aligned processed window and target-court participant episodes.
   Never read the future/current activity state as if aligned to finalized frame.
3. Test reconstructed-continuation and stationary-conflict handling independently
   before combination. Preserve observation/interpolation provenance and allow
   unknown/missing evidence. Add synthetic regressions for disappearance, false
   stationary peaks, contact transitions, player dropouts, moving players during
   breaks, fast shuttle, real short intervals, long loss, cuts and close breaks.
4. Run fixed-input production-FSM and full semantic-engine ablations, then fresh
   full-video production inference for the selected candidate(s). Keep detector,
   checkpoint, media timebase and evaluator fixed unless the named experiment
   changes exactly one of them. No baseline output path may be reused.
5. Separate the existing TrackNet overlap experiment from segmentation changes;
   record window-vote coverage, runtime, GPU/CPU memory and all boundary metrics.
6. Run the complete regression suite after integration; distinguish controlled
   mocks, synthetic temporal probes, real-media contracts, semantic replay and
   fresh model inference. Publish remaining failures and unavailable evidence.

## Final deliverables and acceptance

`final_benchmark_report.md` lists baseline, every experiment, every fix, full
metrics and outlier changes; `component_test_report.md` records actual commands,
configurations and result classes; `regression_report.md` identifies resolved,
worsened and remaining cases. Models/code/licenses/data provenance remain
separate. Improvements on Test1 do not establish performance on other matches,
amateur views or unannotated doubles footage.

Main is not modified. Final branch commits contain only scoped implementation,
tests and small evidence/reports; large runtime/caches/media stay ignored under
`artifacts/benchmarking/` and source data management.

## Completed implementation and validation

| Commit | Scoped implementation and verification |
| --- | --- |
| `6aa79ac` | Parameter-shaped stationary history, contact rebasing and recovery-onset clocks; focused failing/green controls and independent ablations |
| `b60f114` | Injected registry model root used for derived caches; unknown/singles/doubles constructor regression controls |
| `af70da7` | Optional typed sport-owned evidence port/provider, frame-aligned helpers and isolated production experiment observer |
| `7c83b00` | Bounded observed image-exit/return support with missing-anchor, cut, break and no-fabrication controls |
| `3653b0d` | Frozen extended factorial and explicit exploratory GPU profile; full source used by the fresh production run |

Phases 1–6 completed with distinct evidence classes. The final full software
suite passed 1,895 tests, no skips. One fresh full original-video inference
completed with 39 predictions, 35 TP, 4 FP, 1 FN, F1 0.933333; source/proxy
timeline and complete perception coverage were verified. Fresh observations
replay exactly to all 39 intervals/end reasons and 447 live contact timestamps.
The 40 new diagnostic packages supplement the 55 frozen-baseline packages.

The final reports and machine-readable `experiment_results.json` preserve all
rejected pilots/ablations, row regressions, runtime scopes and remaining errors.
The new provider remains opt-in. Held-out validation, repeated full GPU inference,
reviewed contact/pixel labels, browser-seek validation, real doubles model quality
and residual source-edit/start-convention decisions remain future work, not
completed acceptance claims. No main branch or frozen artifact was changed.
