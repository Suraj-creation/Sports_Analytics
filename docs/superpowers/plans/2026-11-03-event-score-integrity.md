# Event and score integrity implementation plan

> Execute in this session with isolated file ownership. The mission prohibits commits; use Git patches against the recorded HEAD for server validation.

**Goal:** Make accepted point decisions durable, retry-safe, recoverable and visible without stale or provisional score state.

**Architecture:** Retain the existing badminton engine, SQLite event ledger, snapshots and WebSocket replay. Add one nested transaction boundary around a scoring decision or correction; retain unknown outcomes. Reuse existing frontend event folding and revision guards.

**Baseline:** `full_pipeline`, `cc73688630e40d534d94b7ef32bd0cbfed7e0571`; earlier architecture baseline `32a8295d9645d81bd1586a777541bb2f72c08bed`.

**Constraints:** Edit this Windows checkout. Run all tests/media work on the GPU server after `source ../gpu-env.sh`, using the existing virtual environment. Do not install dependencies, download weights, replace models, commit, reset unrelated work or reanalyse saved sessions. Keep Cloudflare disabled.

- [x] Inspect current code and historical reports; assign frontend, score-domain and cache investigations with exclusive file ownership.
- [x] Reproduce persistence, duplicate delivery, OCR waiting-window and frontend projection defects using focused server regressions before implementation.
- [x] `engine/store/events.py`: introduce `transaction()` with nested savepoints and `after_commit(callback)`; identical event-ID delivery is idempotent, conflicting content is rejected. Return the latest snapshot at each frame while retaining audit rows. Bind multi-query projections to a read snapshot.
- [x] `bai_badminton/engine.py`: group rally, point, transitions and snapshots atomically; restore in-memory scoring bookkeeping on failure, preserve retryable pending rallies, order decisions by frame and withhold orphan outcomes on restoration. Corrections refold atomically. Preserve singles/doubles and configured rule boundaries.
- [x] `score_ocr.py`: tolerate stable unchanged readings before one supported change; abstain on conflicting changes in the waiting window. Add public seed state without altering the existing raw restore field.
- [x] Web score projection: choose accepted effective points, honor seed timing, prevent provisional or retracted packets from overwriting score state, and reject stale metadata responses. Keep analytics on the same accepted-decision contract.
- [x] Registry `_fetch`: reproduce and isolate concurrent download staging; validate complete bytes before atomic publication. Use mocked downloads only.
- [x] Add real API/WebSocket/reload coverage and a disposable browser fixture/spec exercising controlled observations → decisions → persistence → rendered score and correction.
- [x] Run focused regressions, then the existing engine/sport/API/research/frontend suites and builds. Inspect the browser through SSH forwarding; report browser-runner availability honestly.
- [x] Record the source-grounded lineage, ranked defect ledger, root causes, executed and skipped checks, unresolved risks, and preserved Git state in the architecture/operations report.

Focused backend command (isolated server worktree):

```bash
source ../gpu-env.sh
export GPU_PY=/home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/bin/python
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src:$PWD"
"$GPU_PY" -m pytest -q engine/tests/test_event_transactions.py engine/tests/test_model_fetch_publication.py sports/badminton/tests/test_score_event_integrity.py sports/badminton/tests/test_score_ocr_delay.py
```

Frontend checks use the existing server `node_modules`: `pnpm exec vitest run`, `pnpm typecheck`, and `pnpm build` from `apps/web`. No local test execution is permitted.

Executed: 1,356 backend tests, 149 frontend tests, typecheck/build and one real browser
score synchronization test passed. The browser is an installed Windows Chrome
accessed over CDP/SSH; the Playwright runner and assertions executed on the GPU
server. See the [validation report](../../architecture/event-score-integrity-20261103.md)
for logs, the root-cause boundaries and the remaining real-video/export limitations.
