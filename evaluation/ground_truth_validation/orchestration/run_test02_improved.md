# Fresh Test2 improved run — prepared, not executed

`run_test02_improved.py` must be invoked by root only after completing the
baseline, its additional diagnostics, main integration and regressions.
This preparation did not execute the runner or launch inference.

Required receipt:
`test_02/fixes/applied_fix_receipt.json`, with:

```json
{
  "regressions_passed": true,
  "baseline_protected": true,
  "production_files": {
    "/absolute/repository/production/source.py": {
      "before_sha256": "original baseline source digest, or null for a new file",
      "after_sha256": "reviewed integrated source digest"
    }
  }
}
```

The script refuses incomplete baseline or annotation-diagnostic gates; existing
improved outputs/reports; undeclared frozen source changes; perception changes;
unlisted new core files; an isolated/old package import; changed numerical
profile/model manifest/lock; a wrong video; or any changed original annotation.
It does not reuse the Test1 pre-fix source-hash guard for a changed Test2 engine.

After preflight it creates only new external `test_02/improved_v1` artifacts and
the corresponding workspace symlink. Physical GPU1 performs fresh full inference.
All standard timestamp, model/coverage, unbound/bound annotation, rally-reference,
downstream, strict same-run parity, visual, causal, heatmap and matrix helpers
execute with exclusive logs/command/result records. Helper bytes, Git/source
metadata and configuration/model identities are retained.

The fresh replay must establish full own-run parity with no source intervention.
That replay is diagnostic; it is not mislabeled as neural inference. The actual
before/after comparison uses the fresh pipeline runs and preserved baseline
JSON. It does not re-evaluate the baseline with current source or substitute
Test1's reference families.

The baseline artifact directory, baseline report directory, original annotations,
video, coordinate contract and helper files are checked for preservation. The
runner emits an improved matrix, all-three-reference comparison, complete saved
component-matrix comparison and final artifact-verification receipts.

Failures retain the input and partial evidence. A failed preflight cannot write
into a previously existing improved artifact directory. There is no automatic
retry, Test3 advancement or media deletion. Test1 regression and final root
review remain explicit completion requirements.

Validation performed during preparation: syntax compilation, lint, and **9
guard/comparison unit tests passed**. The runner's `main` was not invoked.
