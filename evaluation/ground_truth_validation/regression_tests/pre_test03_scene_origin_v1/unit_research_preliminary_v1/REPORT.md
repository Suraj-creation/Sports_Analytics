# Preliminary candidate research regression

Full existing `research/tests` scope is green after four narrowly scoped test-fixture updates: **736passed,10explicit integration-fixture skips,0failures/errors (746collected),13.09s**. The final retry source hashes remained unchanged during execution. This is preliminary research coverage, not the final root-owned commit/source freeze or neural acceptance.

Candidate imports were explicitly bound to `test03-scene-overlap-20261112`, including its pyproject/rootdir and package PYTHONPATH. CPU-only environment used the existing server runtime; no neural inference was invoked. [Full retry](full_retry_v1/completion.json), [test log](full_retry_v1/pytest.log), [JUnit](full_retry_v1/junit.xml), [frozen owned test hashes](owned_test_freeze.json).

The initial broad run retained689passes,10skips,4failures and39setup errors. It exposed outdated catalogue codec expectations and newly explicit source/structural provenance in the AST equivalence checks. Both focused red retries remain preserved. No failed test was marked skipped as part of these corrections; the10completed-native fixtures already require a separate exact completed-NN producer fixture, as root documented.

Changes were confined to four existing candidate research test files:

- Codec21synthetic historical fixture now permits a latest24writer as its source, then still constructs the explicit historical21wire fixture. Normal writer allowlist assertions include24; genuinely unsupported future codec is25. Published historical catalogue preservation tests remain intact.
- Codec22compatibility tests include a valid24normal/completed roundtrip, reject24population claiming old23acceptance metadata, and prove valid24cannot enter strict21historical recovery. No production recovery or catalogue function was changed.
- The historical recovery test's separate normal-writer future-version control uses25; strict21recovery assertions remain unchanged.
- Exact numeric AST equivalence normalizes only the precisely declared structural dispatch/import, source-snapshot call and `executed_analysis_source.py`copy. A changed numeric argument (`n+1`) is rejected, and an unrelated numeric-output file operation remains in the AST comparison. No report arithmetic, threshold, coordinate or matching expression is normalized away.

Five added guard cases account for746collected versus the root's741expected after removing its unrelated new epoch-sequence restriction. The patch file captures the current Git diff for the four owned paths; it may also show the root's pre-existing integration-fixture gating on the same existing audit test file. The initial manifest records those pre-existing file hashes and dirty state.

Ruff passes all four edited test files. Production code, original producer2418, MAIN tools, annotations, model files and evaluation arithmetic were not edited by this task. The root owns final authoritative frozen-source testing and subsequent fresh neural validation.
