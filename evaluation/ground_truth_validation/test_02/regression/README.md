# Controlled semantic regressions for the Test 2 racket admission fix

The root orchestrator must finish the genuine fresh Test2 baseline, strict original semantic parity proof, diagnosis and tested production fix receipt **before** invoking these helpers. Preparing this orchestration did not apply a fix, execute semantic replay or run neural inference.

```bash
source ../gpu-env.sh
.venv/bin/python evaluation/ground_truth_validation/orchestration/run_controlled_semantic_regression.py --test 1
.venv/bin/python evaluation/ground_truth_validation/orchestration/run_controlled_semantic_regression.py --test 2
```

An explicit test selection is required. Test1 binds the original full `test_01/improved_v1` run, exact source SHA and17,268frames; Test2 binds `test_02/baseline_v1`, its different exact SHA and29,296frames. CLI overrides for baseline, metrics or proof still undergo those same source/session/media/hash guards. The default metrics prefer the bound component matrix if present, otherwise the original all-reference matrix. Prior Test1/Test2 matrices remain unchanged.

The helper refuses anything except the applied receipt schema `test2-applied-correctness-fix:v1`, fix `racket_anatomical_alias_abstention_v1`, passed/protected/unchanged flags, retained test logs and exactly two actual source changes:

- `sports/badminton/src/bai_badminton/engine.py`, with baseline-before and current-after hashes.
- Newly added `sports/badminton/src/bai_badminton/racket_admission.py`, with null before and current-after hash.

Perception code, other core source, frozen model manifest/lock, profile and original input edits reject the experiment. New tests, diagnostic helpers and reports are separate noncore work. Receipt source fields may be absolute or repository relative; test logs may be paths or `{path,sha256}` records.

Only completed original worker/executor/catalogue evidence is accepted. The baseline proof must have strict parity, no intervention, the same original report/cache/session/run, every frame and full ordered FSM trace. Its outputs, archived helpers and core source snapshots are verified. A complete `controlled-semantic-source-intervention:v1` manifest binds current core source hashes, exact two-file delta and original report/proof SHA. The existing semantic replay then reuses immutable own-cache observations over the complete timeline; **it performs no fresh neural inference** and receives no annotations as input.

New outputs default to `ground-truth-validation-artifacts-20261110/test_02/test1_semantic_regression_v1/` or `test2_semantic_regression_v1/` outside the repo. A matching link appears here only on actual execution after successful preflight. Outputs preserve commands/logs, applied receipt/test evidence, source snapshots, replay events/full trace/parity, protected hashes and full interval-reference comparisons. New directories must not already exist; failed output/logs are retained for diagnosis.

After replay completion and unchanged-source/cache/profile guards, the shared existing comparator evaluates **all six Test1** or **all three Test2** reference files separately. Partial Test1 Full2 has no FP/precision/F1 claims outside known coverage. Complete distributions and mismatches are saved with before/after event types, contacts, named actors, known winners, official rallies and identity ambiguity counts. A Markdown comparison and hashed completion inventory accompany the machine-readable matrix.

`perception_schedule_feedback.json` additionally compares the final FSM state after **all traced operations in order** at every actual nonterminal cache chunk frontier. This includes contact/discontinuity operations after a step; step-only comparisons cannot establish the cadence driver. The binary driver is the actual plugin's `fsm.state != IDLE`; `ending` and `closed` also count as in-play for this purpose. Full before/after step-state differences are recorded separately. The terminal chunk/flush has no next neural chunk and is retained separately, excluded from next-chunk feedback.

If any nonterminal binary driver differs, the report explicitly marks the semantic regression **conditional** and requires fresh inference for that test before claiming full-pipeline preservation. If all drivers match while perception/profile/model inputs are unchanged, the report establishes equal recorded chunk-cadence inputs, while retaining its semantic-only provenance. Test1 and Test2 results are never silently described as fresh neural runs.

This is an engine-only fixed-perception development regression, not a new fresh-model benchmark, label adjudication or independent AP/HOTA/contact/racket accuracy test. Candidate acceptance remains the root orchestrator's decision. A successful semantic comparison does not authorize silently replacing historical results or claiming neural-model improvements.

Initial guard validation is preserved in `../diagnostics/semantic_regression_guard_validation.log`; extended scheduling validation is in `../diagnostics/semantic_regression_guard_validation_v2.log` (29passed). Tests cover additional core changes, receipt hashes/flags, incomplete/foreign parity proofs, changed profile/assets, incomplete/duplicate/future-frontier traces, missing/modified regression evidence, contact changes after a step, nonidle state differences, terminal flush and missing chunk-frontier evidence.
