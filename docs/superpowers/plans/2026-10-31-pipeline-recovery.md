# Badminton pipeline recovery implementation plan

**Goal:** Recover useful unmerged reliability fixes on `main`, repair demonstrated defects, and validate locally without downloading models, installing packages, or using the GPU server.

**Architecture:** Keep the existing `SessionRunner -> BadmintonSession -> BadmintonPerception -> BadmintonMatchEngine` architecture. CFR proxy frames are canonical; perception supplies pixel observations, court homographies supply ground coordinates, contact fusion and stroke rules create estimated events, and BWF state plus the canonical event/track fold supply scores and analytics.

**Tech stack:** Existing Python 3.12, NumPy/SciPy/OpenCV, Pydantic, SQLite/Parquet, pytest, React/TypeScript/Vitest. Use existing local package caches through process-only `sys.path` additions when compatible; no environment installation.

**Spec:** User attachment `99c6aa38-f56e-4f65-9ac0-aeda7a9c1f1f/Pasted text.txt` (31 October 2026). Its local-only instruction overrides the repository's normal remote-validation workflow. Execute inline in this checkout as requested.

## Constraints and protected state

- Do not SSH, run inference, fetch weights, install packages, mutate real session stores, or publish remote history.
- Preserve initial Design deletions, `apps/web/package.json`, `apps/web/pnpm-lock.yaml`, and untracked `Design/`, `client-website/`, `Part2/`, and `SportsVideoAnalysis/` content.
- Original active branch: `main`, `510b703`; local `origin/main` is the same commit. No fetch is needed for the historical recovery.
- Recovery candidate: `review/pipeline-reliability`, four commits after the common ancestor `5d76ad6`. Never merge its older UI and persistence implementation wholesale over newer main.
- Tests of controlled adapters establish contracts, not real model accuracy. Geometric coverage is not labelled event accuracy.

## Execution checklist

- [x] Inspect Git, user changes, entry points, dependencies, and relevant unmerged history.
- [x] Save binary diffs, branch inventory, original revision, and copies of modified dependency files under ignored `.kilo/recovery-20261031/`.
- [x] Run historical regression tests against current main before integrating the corresponding fixes.
- [x] Recover detection colour, elapsed-time tracking, bounded ROI continuity, shot-isolated shuttle windows, and cache chronology. Preserve selected-court and current evidence gates. Test adapters without model downloads.
- [x] Recover contact suppression, anonymous-body fusion, qualified serve context, rally boundaries, and evidence semantics. Test chunk partition invariance, incomplete evidence, timestamps, and singles/doubles attribution.
- [x] Inspect scoring/OCR, corrections, reanalysis generation, persistence, live/API folds, highlights, exports, and frontend transport. Recover compatible fixes and add tests for newly demonstrated defects.
- [x] Audit CUDA/provider selection and disabled models. Test requested versus actual backend status with controlled sessions; never claim CUDA execution locally.
- [x] Run available existing unit/regression/synthetic integration tests, static parsing, focused lint, frontend tests/typecheck/build. Record unavailable dependencies and actual pass/fail/skip counts.
- [ ] Review all changed paths and file sizes; verify protected user state byte-for-byte. Commit only reviewed recovery files, leave protected changes untouched, and delete only obsolete fully merged local branches without active worktrees.
- [ ] Complete `docs/testing/pipeline-recovery-20261031.md` with architecture, contracts, defect register, commands/results, limitations, completion checklist, and ordered GPU/real-video validation plan.

## Primary boundaries to inspect

1. `engine/src/bai_engine/media/{probe,proxy}.py`, `decode.py`, and `runtime/runner.py`: oriented dimensions, canonical frame index, strict segment bounds, chronological perception, analysis revision.
2. `sports/badminton/src/bai_badminton/perception/{players,tracknet,pipeline,scoreboard}.py`, `plugin.py`: BGR decoder boundary, RGB model boundary, box/confidence validation, absolute timestamps, observed versus carried rows, cut isolation, loaded capabilities.
3. `identity.py`, `engine.py`, `events/{contact,stroke,rally_fsm,rally_outcome}.py`: track/participant separation, unique spatial rebind, contact local maxima, heuristic evidence, unknown winners, event ordering.
4. `rules/bwf.py`, `score_ocr.py`, `analytics/{rebuild,match,spatial}.py`, `store/{events,sessions,tracks}.py`: replay/corrections, idempotency, authoritative score, movement validity, cache revisions.
5. `apps/api/src/bai_api/{analytics,ws}.py`, routes and `apps/web/src/{lib,stores,features/player}`: snapshot generation, anonymous observations, bounded overlays, stale data replacement, score priority and export consistency.

Each repair cycle records a failing regression, a targeted integration or fix, and a passing focused rerun before proceeding. Missing optional model packages block their real inference tests and are not replaced with fake production outputs.
