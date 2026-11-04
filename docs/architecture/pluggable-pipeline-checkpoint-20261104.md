# GPU pipeline checkpoint — 2026-11-04

This is an in-progress checkpoint, published at the user's explicit request.
Development is isolated from the user's local UI branch. The original application
runtime and sessions remain separate. Generated media, benchmark labels, models,
private runtime files and credentials are excluded from Git.

## Verified in the GPU runtime

- Generic component contracts and six configured perception providers, including
  actual selected-provider execution, lifecycle adapters and artifact identity:
  60 targeted tests passed (21 generic, 13 domain, 26 acquisition regressions).
- Detector-bracket participant geometry helper: 79 tests passed; production
  integration remains opt-in and is not yet wired.
- Source-bound ShuttleSet22 importer: 55 tests passed. Singles-only CG-AP shadow
  capability guard: 15 tests passed.
- Canonical cropped-media provenance: 12 harness tests passed. Score UI: 32 tests
  passed and TypeScript compilation passed before this checkpoint.
- Conservative score-name aliases and immutable unique transition references
  pass their helper cases. The reset-only winner guess has been removed.

## Work still open

Accepted transition ownership, refold/restart and delayed scoring integration are
unfinished: 4 failures, 52 passes in the last scoring subset. Contact geometry
integration has 10 failing and 2 passing contract cases. Format understanding and
whole-host independent-pipeline proof are next. Full regression and real-video
accuracy checks for this checkpoint have not completed.

Public India/Denmark source videos and published labels are downloaded privately,
with hashes and license receipts. The first continuous clip is prepared; label
alignment remains draft. Runtime/test passes above do not establish contact,
shot or score accuracy. No new benchmark metric or model-adoption claim is made.
