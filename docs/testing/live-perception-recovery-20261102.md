# Live perception and score recovery — 2 November 2026

## Result and scope

The GPU deployment now runs the existing recovery implementation plus the renderer/score fixes in `4371cb0`, with a newly built frontend. The affected He/Ren versus Rankireddy/Shetty recording was freshly analysed through all **12,148 canonical frames** on the existing GPU runtime. Its validated results were promoted to the original session only after backing up its catalogue, event log, generated results and complete original session directory.

This establishes execution, persistence, transport and rendering on this recording. It does **not** establish labelled detection, identity, contact, shot-family or automatic point-winner accuracy. Missing evidence remains missing; the system does not award points merely because a player falls or a shuttle disappears.

Public application: `https://fellow-solution-identified-parliamentary.trycloudflare.com`.
Affected session: `01M56T2EED5Z7W9VTGG19FHNTF`.
Frame **2927** contains a corroborated source-board reading **HE REN 10 / RANKI SHETTY 16**, matching the kind of discrepancy shown in the supplied screenshot. Source-board readings are labelled **Broadcast score**; they are not fabricated P1/P2 assignments.

## Root causes and defect register

| Component | Evidence and root cause | Repair / outcome | Validation |
|---|---|---|---|
| Deployed revision | Server checkout was `510b703`, while local `fd11525` already contained the recovery commits `74a200a` and `9e105e9`. Restarting the old launcher kept serving old code and assets. | Tested the newer source in a separate server Git worktree; pinned the launcher to that release and built its frontend. Original server checkout was not switched or cleaned. | Source revision, built assets, real REST/WebSocket/browser inspection and public health/auth responses. |
| Player boxes and pose transport | Original Parquet contained **27,296 player rows**, all unnamed, including **19,560 pose rows**. The deployed encoder required a named P1/P2 identity and discarded every one. Sampled live windows therefore had shuttle/camera data but no player data. | Deploy the already-recovered `encode_tracks` anonymous series, `TrackBuffer` support and renderer iteration. Detection identity is distinct from a score-side or real person name. | Existing real-track transport fixture, new server HTTP response with anonymous observations, actual four-player boxes and skeletons in browser. |
| Detector / pose adapters | The old deployment lacked the recovered BGR→RGB, output validation, elapsed-time tracking and conservative admission contracts. This was separate from the transport failure. | Deploy the existing repaired RF-DETR, RTMPose and tracker adapters without replacing models or the CUDA environment. | Installed adapters exercised by backend suite; actual cached RF-DETR, RTMPose and TrackNet checkpoints executed on GTX 1080 Ti; full pipeline subsequently completed the clip. |
| Independent name-label toggle | `drawOverlay` entered the player loop only when boxes or pose were enabled. Labels alone drew nothing. | Include `layers.labels` in the loop condition; box/pose controls remain independent. | New failing regression reproduced on server, then passed. No real names inferred for unassigned tracks. |
| Frame-tied state selection | `EventLog.latestBefore` retained the first event at a tied frame rather than the highest append sequence. | Compare frame first and sequence for ties, including delayed older arrivals. | Three failing regressions for point, broadcast-score and calibration events, followed by passing checks. |
| Accepted point hidden by stale OCR | `ScoreBug` allowed only human decisions to supersede an older broadcast reading. An ordinary accepted point could remain invisible or make a human-corrected score jump backward. | Prefer a confirmed/corrected/human-verified point newer by video time than the latest broadcast observation. | Two failing renderer regressions, then passing live-store/UI tests; genuinely newer broadcast readings remain usable. |
| Carried human correction freezes later scores | Reanalysis appends carried decisions at the end. The old human-score sequence override made an early-frame human correction appear newer than every later-frame OCR reading. This affected the real session's frame-849 manual 1–0 correction. | Order display evidence by **video frame**, using append sequence only for equal-frame ties. Keep the human decision and canonical analytics intact. | New failure with frame-300 human point seq101 versus frame-500 broadcast seq20; passing after repair. Public frame-2927 inspection checks later 10–16 source score. |
| Court geometry | Saved calibration and per-frame camera transforms existed; this was not evidence of an absent court detector. White overlay lines can coincide with source paint. Alternate/close-up views intentionally withhold invalid geometry. | Retain calibrated `G @ H` projection and existing calibration workflow. Do not draw arbitrary fallback lines. | Known synthetic court points, translated camera, lost-pose suppression, landscape/portrait letterboxing, and actual court alignment in browser. |
| Contact / rally / authoritative score | The original 1–0 point was a **human decision**, not a broadcast-board reading or proof of automatic winner detection. User aliases `ind`/`chin` and the unassigned doubles roster do not establish the OCR-row→score-side or person mapping. | Deploy the recovered evidence gates, BWF fold, idempotency, correction/refold and generation-aware transport; preserve unresolved winners. Corroborated source readings can display independently of identity mapping. | Backend terminal-loss, supported-terminal repeated-flush, OCR row/name/reset, correction, generation and WebSocket tests; full video emits 283 contacts/strokes, 26 rally candidates and 86 corroborated board observations. Only the retained human point is accepted as a point in this run. |
| Persistent names / identity | Four roster participants have no supplied names/team associations or reviewed track intervals. P1/P2 aliases are not four identities. The pinned OSNet artifact is absent. | Keep real tracks explicitly unidentified; existing reviewed-interval assignment remains available. Capability metadata reports neural identity **unavailable**. No weights downloaded and no names inferred from appearance. | Existing identity/review/cut/epoch tests, four anonymous real tracks, unavailable-stage metadata, preserved roster. |
| Shuttle and missing optional output | Shuttle already worked and must not depend on named players, pose or equipment output. | Preserve the existing observed/missing shuttle path and frame-indexed renderer. | Backend temporal/cache/contact tests, frontend trail tests, real TrackNet inference, full persisted shuttle series and visible browser trail. |

## New source changes

- `apps/web/src/features/player/overlay.ts`, `drawOverlay`: independent label rendering.
- `apps/web/src/lib/events.ts`, `EventLog.latestBefore`: frame/sequence precedence.
- `apps/web/src/features/player/ScoreBug.tsx`, `ScoreBug`: accepted point precedence and video-time ordering of carried corrections.
- `apps/web/src/features/player/overlay.test.ts`: independent labels, actual keypoint coordinates and confidence gates, camera/court projection and lost-court suppression.
- `apps/web/src/lib/buffers.test.ts`: tied-frame ordering under delayed arrivals.
- `apps/web/src/features/player/ScoreBug.test.tsx`: automatic accepted point, human→automatic continuation, later broadcast observation and retroactive correction timing.
- `docs/superpowers/plans/2026-11-02-live-perception-recovery.md`: investigation and execution record.

The much larger backend recovery is existing source from the earlier commits, newly deployed and actually validated on the server here. This report supplements the earlier local-only reports rather than reclassifying their evidence as GPU validation.

## Validation executed on the GPU server

Isolated checkout: `/home/administrator/Desktop/sport-analytics/live-perception-recovery-20261102`.
All execution sourced `../gpu-env.sh`, reused the original `.venv` and installed frontend dependencies, and selected the isolated source through `PYTHONPATH`. The owned Cloudflare process was stopped during the test run; browser inspection used SSH forwarding. No dependency/model installation, CUDA/FFmpeg replacement or unrelated process termination occurred.

| Check | Actual result | Evidence under `.validation/` in the isolated checkout |
|---|---|---|
| Initial renderer/event red tests | **4 failed, 23 passed**, expected failures | `frontend-red.log` |
| Accepted-score red tests | **2 failed, 13 passed**, expected failures | `score-red.log` |
| Carried-correction red test | **1 failed, 7 passed**, expected failure | `carry-red.log` |
| Broad backend/research | **1,113 passed**, 12 existing HTTP-status deprecation warnings | `backend-final.log`, exit0 |
| Final frontend | **34 files, 129 passed** | `frontend-delivery.log`, exit0 |
| TypeScript | Passed | `typecheck-delivery.log`, exit0 |
| Focused frontend lint/format | **6 files**, no fixes/errors | `frontend-lint-delivery.log`, exit0 |
| Production build | Passed | `build-delivery.log`, exit0 |
| Real component inference | Actual TrackNet, RF-DETR and RTMPose execution over frames800–919; 70 shuttle hits; full-frame people0–6 including off-court candidates | `real-doubles-components.json` and `.log`, exit0 |
| Full actual pipeline | **12,148/12,148 frames**, statusanalysed, frontier12147 | `real-full-pipeline-summary.json` and `live-server.log` |
| Safe promotion | Unchanged source catalogue/session and event digest; complete original preserved; new digest checked after staging | `promotion-dry-run.json`, `promotion-result.json` |
| Browser / public access | Four real boxes, skeletons, calibrated court, trail and changing source score; healthok and `auth_required:false` | Browser inspection and direct public responses |

Commands: `python -m pytest -q engine/tests sports/badminton/tests agents/tests apps/api/tests research/tests -m 'not gpu and not slow and not network' --tb=short`; from `apps/web`, `pnpm exec vitest run`, `pnpm exec tsc -b --noEmit`, focused `pnpm exec biome check` over the six changed TS/TSX files, and `pnpm exec vite build`. GPU component and full-application runs are separate from these unit/controlled-integration counts.

The standalone Playwright E2E scripts were not executed: the server did not have the configured Chromium browser installed, and no new browser package was installed. Real browser inspection over SSH and after public deployment is recorded separately, not reported as passing those automated scripts.

The first broad backend run overlapped the frontend build. Vite briefly removed `dist/assets`, causing one `StaticFiles` construction failure: **1 failed, 1,112 passed**. The failed test passed alone after the build. The subsequent full run completed **1,113 passed** after asset generation was finished. This was a validation scheduling error, not a discarded unexplained failure.

The component probe is uncalibrated and intentionally admits off-court candidates. Its source still labels a model string “fp16”, but the actual TrackNet load log reports **FP32** for that standalone probe; the production profile's separate execution uses its configured precision. ONNX CUDA was first in the installed provider list, with CPU fallback also listed; that list alone does not prove every operator ran on GPU. Neither component counts nor full-pipeline counts measure accuracy.

### Fresh persisted evidence

- 12,148 shuttle **rows**, of which **4,928 are visible observations**; the rest explicitly represent missing/invisible observations. This is not 12,148 successful detections or a recall measurement.
- 12,148 camera rows.
- **27,601 player rows**, including tracked estimates, and **19,940 pose rows**.
- 6,204 optional geometric racket rows, not trained racket/contact ground truth.
- 283 estimated contact and stroke events; 26 rally candidates; 86 corroborated broadcast-score observations.
- One canonical point, sourcehuman, at frame849, P1=1/P2=0. Other winners remain unresolved rather than being guessed.

## Deployment, backups and preservation

The existing `../start-server.sh` now selects the tested isolated release, its model manifest and profiles, while retaining the original `.venv`, `.env` and production data directory. It explicitly exports an **empty** `BAI_PASSPHRASE` after reading configuration. No password, key or application secret is written into Git. The previous launcher is backed up outside the repository at `/home/administrator/.local/state/sport-analytics/start-server-before-4371cb0.sh`.

Original affected-session backup:

`/home/administrator/Desktop/sport-analytics/Sports_Analytics/data/backups/01M56T2EED5Z7W9VTGG19FHNTF/20261102T140051.060293Z-01M6E905KMM42MDEN5VQJD0WJC/`

It contains SQLite backups, catalogue, original metadata and `complete-original-session/`, including the complete original cache and any other original files. Promotion staged the full original directory, replaced only generated analysis products, verified the fresh ledger digest, then swapped while both application writers were stopped. A directory/catalogue rollback path was prepared. The operation also received an independent review; a staging symlink write-through risk was fixed before use.

Original event digest: `b4db93a257f34948d5142c3c4dd1abca989fce5b0a1cc9b1b74dd2e3b10d9f659`.
Promoted event digest: `4d315d3de23f5800a5d8938e67ae061cb598990cff80163bcaa86b3966f1846be`.

All **six unrelated sessions are byte-identical in the catalogue**. Original videos/media remain in place. Server `apps/web/dist.old/` and `client-website/` are unchanged. The original server checkout remains on its old commit; deployment uses the isolated release rather than overwriting its files.

The local protected diff (Design deletions and the user's web dependency edits) remains byte-identical, SHA256 `01F68BF08339C85CDA7669097AAE175EC359849E8BC0809DC87E3FC36493D052`. Untracked `Design/`, `SportsVideoAnalysis/`, `client-website/`, the external-repository research note, ignored `Part2/` and other unrelated files were not staged, cleaned or moved. Work is on `codex/live-perception-recovery`; nothing was pushed to GitHub.

## Remaining limits and next validation

1. Explicit participant/team names and bounded reviewed track intervals are required for named doubles overlays. Restoring neural re-identification additionally requires the pinned OSNet artifact; it was not fetched in this task. Appearance similarity never establishes a real name.
2. OCR source names/scores do not by themselves identify P1/P2 or four people. Supply an explicit correct score-side association when authoritative team scoring is required. Unresolved rally winners remain unscored; the independent source board stays visibly labelled.
3. Evaluate player/shuttle recall, identity switches, court projection error, contact timing, shot family and point-winner accuracy against independently labelled representative footage. The operational checks here do not supply those labels.
4. This is recorded-video processing with frame-aligned live updates, not a measured guarantee of full-source-rate live ingestion. “Wait for analysis” retains the existing frontier gate. Dedicated general live-source, alternate shuttle models and the doubles-trained BST path remain unsupported research stages.
5. Validate additional recordings/camera types separately, including crossings, occlusion, close-ups, scoreboard swaps, completed-game resets and genuinely unavailable court geometry. No generic court or fabricated player/score output was introduced to cover gaps.
