# Regression of independent scene acquisition

Production candidate `9992f87` is frozen separately from main in
`test03-scene-acquisition-20261112`. The earlier `c585e35` candidate is rejected
for182 visible-athlete row losses. All prior outputs remain immutable.

The current focused gates pass170cases (overlapping the eventual full suites).
Independent codec proof validation passes119cases with unchanged source hashes.
The initial complete research run contains705tests:665passed,39setup errors
from a stale native-writer version guard and one stale unsupported-version
expectation. Its log/JUnit/completion are retained in unit_research_v1/. A sealed
test-only proposal preserves explicit synthetic historical codec21 evidence and
updates current/future version expectations; it awaits the current source freeze
before application. No numerical evaluation method changed.

A fifteen-window chronological perception replay and the full main regression
suite are active. These are component/runtime controls, not a full fresh-video
accuracy result. Test1 full fresh rerun remains gated on source review; Test2
video restoration/fresh inference and Test3 inventory/download/inference remain
pending the required sequential acceptance gates.


The complete first main run retained2,763passes and3failures: all three
partial-constructor test fixtures omitted the new explicit format context.
No production fallback was loosened; fixtures now declare unknown/unconfirmed
format. The five fixture/version test changes are isolated in `a146953`; all
production bytes remain exactly those executed by the15-window `9992f87`
source replay. Its92 closed artifact hashes and actual CUDA provider identity
are preserved. New full main/research suites run under `unit_main_v2/` and
`unit_research_v2/`; focused repair validation passed90cases.


The final full suites now pass:2,766 main tests and705 research tests, with
701 tracked source/config/test hashes unchanged. They total3,471 tests; focused
counts overlap and are not added. There are19 existing Starlette warnings.
The full fresh Test1 arm has started at the frozen `a146953` candidate, separate
from every previous run, in `pre_test03_v3/test01_candidate_v3`. No benchmark
acceptance or Test3 completion is implied by the passing suites.
