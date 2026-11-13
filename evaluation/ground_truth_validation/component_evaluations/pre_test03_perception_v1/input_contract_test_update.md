# Final input-contract regression correction

The initial broad candidate run passed2489cases and failed three FPS variants of
one pre-existing unit test. Its assertions required a new detection to disappear
at birth and again after an expired identity. That encoded the confirmed backend
integration behavior being corrected, contrary to the selected one-observation
activation contract. The [original broad failure log](../../regression_tests/pre_test03_v1/candidate_main_regressions_v2.log)
is preserved unchanged. No evaluator, metric, threshold or original annotation
was changed to accommodate a candidate result.

At25/30/60fps, the updated unit test now requires a current episode immediately
at frame0, the same ID at2 and6, a different ID immediately at6+fps+1, and that
new ID again at6+fps+3. It therefore retains the original video-time expiry
invariant and additionally verifies stability of both the first and replacement
identities. It does not weaken expiry to call-count behavior or reuse the old ID.

[Focused input-contract/birth/lease tests](final_input_contracts_green.log):
**38passed**. [Lint](final_input_contracts_lint.log): passed. These overlap the
121related tests in the main tracking report and must not be summed as distinct
coverage. The parent orchestrator is rerunning the authoritative broad suites.

The production tracking files are byte-identical to the completed v3 prefix
intervention. Only this existing unit test was added to the final source/test
handoff. [Final six-file source receipt](candidate_source_receipt_final.json),
[final owned patch](tracking_candidate_final.patch). All candidate production and
test files are frozen for parent broad/fresh regression. Full fresh Test1/Test2
pipeline regression remains required and is not claimed completed here.
