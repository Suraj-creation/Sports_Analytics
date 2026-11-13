# Cross-test regression for the scene-context corrections

The production baseline is `dacc05e`. The frozen candidate is `c585e35` in
`test03-scene-continuity-20261112`; no Test3 video has been downloaded or run.
Original annotations, model/checkpoint values and numerical evaluation methods
are unchanged. Main has not received the candidate production changes.

## Completed source-frozen gates

| Gate | Result | Evidence |
|---|---|---|
| Main engine/sport/agent/API/benchmark suite |2,656 passed;19 existing Starlette warnings |[Log](unit_main_v2/pytest.log), [source receipt](unit_main_v2/completion.json) |
| Research suite |704 passed |[Log](unit_research_v1/pytest.log), [source receipt](unit_research_v1/completion.json) |
| Changed-file lint |26 Python files pass |[Receipt](candidate_final_lint.json) |
| Source-prefix controls |10 windows, no overflow; two lost Test1 edits recovered |[Source report](../../component_evaluations/pre_test03_scene_foreground_v1/REPORT.md) |
| Scoring/matching/annotation/model integrity |Independent verification passed |[Schema review](../../component_evaluations/pre_test03_scene_foreground_v1/schema_compat_independent_review_v1/REPORT.md) |
| External OCR/pose asset provenance |Model hashes match five historical arms |[Runtime model audit](runtime_assets_v1/REPORT.md) |

The two full suites total3,360 tests. Focused tests, tooling guards and repeated
controls overlap these suites and are not added to that count. Both full runs
verify unchanged hashes for697 tracked source/configuration/test files.

The original [failed main run](unit_main_v1/pytest.log) is preserved:2,655 passes
and one stale contract-version assertion. Its corrected
[19-case tracking test](tracking_metadata_contract_GREEN.log) independently checks
birth activation, court authority and the new scene-context cache policy. The
complete main suite was then rerun successfully. No production algorithm or
numerical evaluator changed to resolve that assertion.

## Preserved experimental failures

The older `c7cf871` full Test1 candidate is a failed integration control: it
misses real edits7857/8106 and carries an empty-court box across7857–7859. Its
[immutable independent review](../pre_test03_v1/test01_independent_review/REPORT.md)
and [108-frame visual record](../pre_test03_v1/visual_test01_v2/index.md) remain.

The first scene-only candidate `7ed2f73` still lost7857 after deleting ambiguous
image context. Its failed prefix output/source snapshot remains separate from
`5b6d429`, whose bounded ambiguity recovery passes all ten source windows. The
latter uses911 retained detector observations and zero new neural calls in that
repeat. These component experiments are not fresh end-to-end benchmarks or
independent physical-accuracy scores.

## Fresh end-to-end acceptance

The new full Test1 run completed, but acceptance was rejected for182 visible-athlete coverage losses. [Status](../pre_test03_v1/test01_candidate_v2/status.json)
and [launch log](test01_fresh_v2.launch.log) describe the genuine chronological
inference. Outputs are stored separately at:

`/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2/`

All six supplied interval-reference families, generated-reference point
agreement, contacts/classes, downstream outputs, runtime/resources and source
visual evidence must be reviewed after genuine completion. The latest Test1
semantic control is distinguished from the older full-neural perception arm.
Partial Full2 precision/F1/FP remain unavailable.

Test2 requires a separate exact-byte owned download and fresh run with the same
candidate after Test1 acceptance. Its three supplied interval references and
all component limitations remain separate. Only after this engineering and
cross-test regression gate may independent Test3 annotation preparation and
video inference begin. Existing records are never overwritten or pooled as a
final ten-video score.


The next isolated candidate is `test03-scene-acquisition-20261112`. It corrects
the missed-edit root cause and restores continuous athlete observations; it is
not yet benchmark-accepted. See the living root-cause specification and the
new `component_evaluations/pre_test03_scene_acquisition_v1/` controls. Frozen
prior candidate results and visual evidence remain immutable.
