# Consolidated Test2 report builder: validation and publication gate

The new standalone helper is
[build_test02_consolidated_report.py](../../orchestration/build_test02_consolidated_report.py).
It is outside the running fresh post-fix runner's frozen helper set. No production
pipeline, inference, model, annotation, baseline or existing report was changed
by this work.

Publication is deliberately gated on the genuine worker and parent full-run
completion receipts, final improved all-reference diagnostic completion, full
matrix comparisons, final artifact preservation receipt, model/profile equality,
current/executed repair source hashes and preserved Test1 semantic regression.
The separate fresh component review must also finish its own artifact/link/
unsupported-metric receipt and bind the actual final fresh inputs. Baseline
player-outlier diagnosis and that independent fresh review are mandatory
embedded sections with separate evidence scopes.
`improved_completion.json` alone is insufficient because it precedes the final
matrix and preservation receipts. Existing report paths and paths inside the
immutable run/regression directories are rejected. The helper does not perform
another expensive full media/cache guard or re-evaluate an old run.

Validation on 2026-11-11:

- Compilation passed.
- 42 focused publication, source/timebase identity, original-row alignment,
  complete tolerance flattening, configuration preservation and immutable-output
  and independent component-review guard tests passed in 0.23 seconds.
- A temporary rendering fixture used the completed baseline as both comparison
  arms solely to exercise every rendering path, all three schemas and embedded
  diagnostics. It rendered all 221 original reference rows and a roughly423 KiB
  Markdown file; longest line1120 characters. This fixture was automatically
  removed. It was never published or represented as a post-fix result.
- The actual consolidated report has **not** been published while the fresh
  post-fix run is active. The root orchestrator must invoke it only after the
  final receipts exist.

After genuine fresh completion, from the main checkout:

```bash
source ../gpu-env.sh
.venv/bin/python evaluation/ground_truth_validation/orchestration/build_test02_consolidated_report.py
```

Defaults create NEW
`reports/test_02_consolidated_v1.md` and sibling `.json`. `--artifact-root` selects
the parent holding `baseline_v1`, `improved_v1` and
`test1_semantic_regression_v1`; `--output` selects a NEW Markdown path. The report
distinguishes two fresh Test2 neural runs from the fixed-perception Test1
semantic regression, generated-reference agreement from physical accuracy, and
baseline failure mechanisms from actual fresh post-fix measurements.

The report includes all saved aggregate/tolerance metrics and deltas, every
original interval and supplied outcome label, missed/extra predictions, seven
annotation roles and quality limitations, supported component diagnostics,
unsupported accuracy prerequisites, actual stage/product coverage and abstention,
racket admission reasons, Test1 semantic/contact-NMS effects, all39 baseline
cases, fresh case links, model/config/source/resource identities and ranked
confirmed failures versus annotation ambiguities and rejected alternatives.
Embedded local links are converted to absolute paths. No video cleanup or Test3
advance is performed.
