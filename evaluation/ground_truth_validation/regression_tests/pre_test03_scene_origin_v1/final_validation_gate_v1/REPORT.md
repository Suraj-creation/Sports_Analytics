# Frozen candidate validation handoff

Commit `5ae614826e6f909defb02445386962ac13b4641a` in `test03-scene-overlap-20261112` has a clean tracked working tree. This read-only handoff verifies the actual committed bytes against the retained test and review receipts. The fresh Test 1 execution is still running; this is an engineering source/test gate, not final video acceptance or measured physical accuracy.

| Scope | Recorded result | Boundaries |
|---|---|---|
| Broad application/core | 2,823 passed; one historical synthetic codec fixture failed, among 2,824 tests | Original failure retained; this whole suite was not subsequently rerun |
| Fixture correction | 46 targeted tests passed | Only the historical fixture wire version changed; existing assertions and core source remained unchanged |
| Broad application source check | 379 application/test files compared | The fixture is the sole change in this scope |
| Research suite | 736 passed; 10 skipped, 746 collected | The ten explicit completed-native integration fixtures require appropriate completed runs; they are not passes |
| Independent focused review | 174 tests passed; six source controls | Overlaps the broader suites; no additive total is claimed |
| Orchestration review | 15 helpers checked; seven mutation controls rejected | Four narrow metadata/dispatch AST normalizations; other helper snapshots byte-identical |
| Parent codec source binding | 19 tests passed | Positive proof and forged/downgraded synthetic metadata controls; no video accuracy claim |

All 712 files in the final research source snapshot are tracked in this commit and match their recorded hashes. All four owned research fixture tests and all ten files in the independent focused review also match their sealed hashes. The source controls use retained source pixels and actual detector proposals at four known edit contexts (2928, 11082, 22416, 23279) and two continuity controls (7703, 23639); they verify the bounded observer/layout behavior, without establishing aggregate scene precision or recall.

The orchestration check verifies every final helper hash. The only byte change since the orchestration review's source map is the regression driver's module docstring, which now describes codec-24 native structural auditing explicitly. Removing only that initial docstring gives identical full ASTs. This descriptive change is separate from the earlier, explicitly reviewed structural import/dispatch and executable source-archive provenance changes. Numerical matching, tolerances, reference arithmetic and model thresholds were not changed by those metadata adaptations. The seven numerical-helper AST comparisons are a distinct narrower claim in the original review, rather than a claim that all fifteen helpers have identical ASTs without normalization.

The initial failed verifier attempt is preserved: it mistakenly applied `len()` to an integer receipt count. No candidate code or historical receipt changed. The corrected verifier compares that field with 18, and all source checks passed. The verifier imports no candidate modules and writes only this new handoff directory.

Fresh full Test 1 and subsequently Test 2 still require their own completed worker/parent/catalogue receipts, numerical comparisons, independent source review and acceptance decision. Earlier raw F1/IoU regressions remain reportable results. Unit passes and bounded controls do not replace these gates or establish contact, class, winner, scoring or identity accuracy.

The user has already authorized merging accepted work to main, pushing main, then removing our five auxiliary worktrees and temporary branches. Cleanup must wait for validation and preservation of external runs, accepted evidence, original annotations/model assets and any untracked or dirty source snapshots. All four earlier auxiliary heads are verified ancestors of this candidate, so merging and pushing the actual history retains those commits; a separate large recovery bundle is not needed solely for those already committed ancestors. No merge, push or removal was performed by this handoff.

Reproduction and detailed source/test bindings are in [verify_gate.py](verify_gate.py) and [source_and_test_binding.json](source_and_test_binding.json). Original receipt paths and hashes, plus the read-only worktree inventory, are retained in the latter.
