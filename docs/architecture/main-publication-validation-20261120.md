# Main publication validation — 20 November 2026

This release integrates the completed pipeline engineering branch into
`origin/main` at the user's explicit request. It publishes the checked source
and preserved evaluation progress. The previously documented sporting-accuracy
limitations remain; passing regression checks does not establish that every
physical rally, shuttle, contact or identity error is fixed.

## Source and branch audit

- Validated starting branch: `engineering/deep-pipeline-overhaul-20261113`,
  commit `1182972b7b967a868fa5c198222bb0f1db120ee0`.
- Remote `origin/main` before publication: `88aa0ad`.
- Local `main` before integration: `1313370`, already an ancestor of the branch.
- Retained engineering commits include `e558fd9`, `ac0084f`, `8110422` and
  `1182972`, together with the evaluation checkpoint `1313370`.
- All seven retained `codex/live-*` fix/test/delivery refs are ancestors of the
  validated branch. `origin/fix/pipeline-tracking-reliability`,
  `origin/review/pipeline-reliability` and `sva/v2/pipeline` are also ancestors.
  Their fixes require no duplicate merge or cherry-pick.
- `origin/client-website-immersive` contains one unrelated marketing-site commit
  and is excluded from this pipeline publication. `sva/main` belongs to a
  separate upstream repository/history and is excluded.

Integration uses a fast-forward and a normal push. No force push, historical
reset, branch deletion or unrelated change is part of this release.

## Validation performed

| Check | Result |
|---|---|
| Backend/engine/domain/API/agent regression | **1,367 passed**, 119 explicit modules, 108.51s; eight existing deprecation warnings |
| Frontend unit suite | **264 passed**, 52 files, 6.36s |
| TypeScript | Passed |
| External production build | Passed, 7.21s; served build was not overwritten |
| Python source/test syntax and Ruff | 69 changed Python files passed; changed test rechecked after repair |
| Existing application smoke | Health, Library, completed selected-video session, analytics and track window all200 |
| Served frontend preservation | All45 existing served-file hashes unchanged |
| Publication preflight | Authenticated Git push dry run passed; no new blob over100MiB; high-precision secret/path scan found no hits |

The first backend run reported1,354 passes and seven failures. Those failures
asserted that unavailable court geometry must discard all player image boxes.
The engineering branch deliberately preserves eligible image observations while
withholding court coordinates, participant binding and named attribution. The
tests now verify those exact restrictions, input immutability and absent named
court histories. Six additional replay cases require image observations to remain
excluded on replay frames. No production code was changed to silence the failures.

The final regression selection combines the previous audited synthetic suite,
all newly added pipeline/API test modules, and targeted wire/ReID/codec checks.
An `av.open` guard prevents accidental media processing. This is an explicitly
selected suite, not a claim that every repository/evaluation test was executed.
An initial selection preflight safely stopped before pytest when it encountered
the non-test helper `endpoint_support.py`; the corrected selection admits only
explicit test modules and checks its module count before execution.

No new video inference or benchmark was run for publication. Existing completed
single-video empirical evidence is preserved in
[the end-to-end report](single-video-end-to-end-validation-20261113-v1.md).
Its five completed runs, one interrupted attempt, unchanged final perception
outputs, measured latency improvements and remaining accuracy failures retain
their original meaning.

## Reproducibility and publication receipt

Commands, module selection, per-node outcomes, initial/final logs, branch audit,
static checks, smoke responses and frontend build manifests are retained under:

`/home/administrator/Desktop/sport-analytics/main-release-validation-20261120/`

The frontend build targets this external directory, preserving the existing
application on127.0.0.1:8011. Original sessions, models, accepted evidence and
unrelated processes are retained. The final publication receipt records the
committed candidate and remote-main hash after the normal push.

Known limits remain in
[the residual register](single-video-residual-issues-20261113.json), particularly
physical shuttle/contact evidence, stable player identity, unknown stroke labels
and incomplete whole-rally coverage. This release is an engineering integration
and regression check, not a new production-accuracy certification.
