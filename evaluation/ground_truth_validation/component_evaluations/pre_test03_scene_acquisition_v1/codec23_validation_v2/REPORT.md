# Synthetic historical-codec fixture correction proposal

The frozen research run has **705 tests:665 passed,39 fixture setup errors and1 failed expectation**. The39 errors share an obsolete assertion that the current writer version must be21/22; the writer is now23. The remaining test calls23 an unsupported future codec, although normal completed-cache validation now supports it. The original JUnit, pytest log, source manifest, completion receipt and executed runner are copied unchanged under [red_full_research_run/](red_full_research_run/).

**No candidate, existing MAIN test, production helper, evaluation matrix or real cache was changed.** Proposed copies live under [proposed_tests/](proposed_tests/). The root orchestrator must wait for the running frozen checks to finish before applying the [formatted test-only patch](proposed_test_only_formatted.patch).

The proposal makes only these compatibility corrections:

- Permit the native synthetic writer guard to recognize23, then still explicitly build and assert historical21 wire data. Remove newer optional empty fields from that controlled21 fixture as well as `fg`, so the fixture actually tests the historical field shape.
- Update the current catalogue acceptance-list expectations to20/21/22/23. Published legacy20 catalogue verification still requires unchanged recorded bytes and the exact historical policy.
- Move the unsupported normal future-codec example23 to24, both in the parametrized catalogue rejection test and the recovery-related normal-catalogue rejection example.
- Preserve the explicit historical recovery rejection of22 and the strict21-only recovery wrapper. Failure/source/receipt checks, bad geometry/model/timestamps, missing fields, historical catalogue limits and population guards are unchanged.

The two proposed files pass **69 focused tests** using the frozen candidate’s native plugin and research helpers. [Pass log](proposed_tests_first.log), [lint log](lint.log). Independent module-path verification resolved the plugin and both helpers inside `test03-scene-acquisition-20261112`. Formatting then preserved the entire proposed Python AST; no repeated execution was needed for formatting alone. The original705-test run remains red historical evidence, and the69 passing proposal tests do not claim that the full suite has been rerun or passed.

The proposal uses synthetic temporary sessions/cache packets only. It does not relabel any real worker output, rewrite a historical completed cache, run neural inference, change an annotation or matching threshold, or access Test3 data.
