# Full-system integrity audit — 3 November 2026

The existing pipeline has been inventoried and its confirmed score, persistence,
media-lifecycle, cache, export and frontend failure defects corrected in the local
`full_pipeline` checkout. The candidate has passed 1,398 backend tests and 162
frontend tests in the configured GPU-server environment, plus the TypeScript/Vite
build and all eight browser acceptance tests. This is **prepared for further
validation**, not a declaration
of production readiness or independently measured badminton accuracy.

The later [real-video/runtime continuation](real-video-runtime-validation-20261103.md)
adds1,418 passing backend tests, successful fresh ONNX CPU/CUDA parity,13 passing
real Redis/API-worker stages and fresh continuous SampleRally/Test7/A02 inference.
The missing exporter/service blockers are resolved after explicit user approval
of additive runtime packages and a private Redis build. This report's original
counts and no-dependency statements describe the preceding audit phase. Test7's
33 rally outcomes remain unknown and no points were accepted; the continuation
does not establish target accuracy or deployment readiness.

The continuation adds nine scoped files to the original86-path manifest:
`config/runtime/onnx-export-pascal.txt`,
`research/validate_real_video_runtime.py`,
`research/tests/test_validate_real_video_runtime.py`,
`research/validate_redis_runtime.py`,
`engine/tests/test_redis_runtime_harness.py`,
`research/validate_tracknet_onnx_runtime.py`,
`docs/architecture/audits/part2-label-readiness-20261103.md`,
`docs/architecture/real-video-runtime-validation-20261103.md` and
`docs/superpowers/plans/2026-11-03-real-video-onnx-redis-validation.md`.
The complete95-path transfer remains uncommitted and excludes unrelated user
files, dependency edits and prototype deletions.

## Inspected implementation and actual ownership

Read the project instructions, architecture/engineering/operations/research/model
evaluation records, current Git state and the actual implementation. The
[component ledger](full-pipeline-phase-2-ledger.md) incorporates three detailed
inventories covering media/timeline, court/camera, all current perception stages,
temporal contacts/strokes/rallies/outcomes, singles/doubles identity, rules/score,
SQLite/Parquet persistence, workers/cache/model registry, API/WebSocket/auth,
analytics/highlights/agents/exports and the production React route/state tree.

The [event contracts](full-pipeline-contracts-20261103.md) record all durable event
families, identifiers, status/evidence distinctions, producers/consumers, retries,
corrections, replay, timing and missing guarantees. `engine/` retains generic
media/execution/storage; `sports/badminton/` retains sport geometry/perception/rules.
No new framework, broker, model, dependency or competing score authority was added.

## What was broken and what changed

The earlier [score investigation](event-score-integrity-20261103.md) is part of
this candidate. A stable but initially unchanged broadcast reading hid a later
legal score change. Separate database commits exposed incomplete rally/point/state
updates; retry/restore and generic verification could produce contradictory score
history. Stale/provisional/retracted frontend projections added independent
failures. The correction inspects the complete bounded OCR window, commits one
logical scoring mutation atomically, rolls back in-memory bookkeeping on failure,
notifies after commit, restores only accepted decisions and renders accepted
effective event history. Unknown outcomes remain unresolved.

The expanded audit reproduced and repaired these additional boundaries:

| Boundary | Root cause → correction |
|---|---|
| Model archives | Unbound extracted files could outlive verified archive changes or publish incompletely → verified private archive snapshot, digest/member manifest, complete bundle publication and safe member paths. |
| Media stream selection | Probe excluded artwork but encoding/calibration selected the first video → carry the selected global stream index through preparation and sampling. Existing complete user proxies are preserved, not silently regenerated. |
| Stop/failure cleanup | Semantic runner exited while media still wrote; callback/worker failures leaked processes or left ingest waiting → own, cancel and join all media jobs, fence future jobs, reap encoder on exceptions and publish terminal state. |
| Background memory | Completed camera-shot reservoirs accumulated → retain only shot backgrounds required by the current sequential call, preserving active/seeded histories. |
| Generation reads | Independent repository retained an old unlinked event database; repeated refresh could close an active read → generation-aware reopening and explicit refusal of detected generation crossings during a pinned snapshot. General distributed reset atomicity remains unsupported. |
| Transport/lifecycle configuration | Fractional Redis timeout became infinite; external mode without shared transport lost commands; external delete raced writer shutdown → preserve timeout, reject disconnected settings and reject external deletion until acknowledgement exists. |
| Bind/auth configuration | CLI host override bypassed the app's loopback/passphrase guard → one effective Settings object for app and listener. |
| Analytics/report coherence | Separate reads mixed old fold/new evidence; tactics accepted unsupported winners → whole-response snapshots and accepted-point criteria. |
| Clip downloads | Failed/in-progress output became reusable; proxy/FPS changes reused old clips → private staging, atomic publication, explicit timeout, input fingerprint and replacement check. |
| Frontend lifecycle/errors | Upload continuations survived unmount; HLS401/403 looked like waiting; failed reviewed analytics looked empty; movement support ignored same-generation correction → cleanup, explicit errors and scoped invalidation. |
| Evidence copy | Source-frame and semantic-grounding wording exceeded implementation → canonical analysis-frame labels and scoped citation language. |
| Background probe | Interactive FFmpeg capability probe suspended the disposable SSH server → `-nostdin`, plus detached test-server stdin. |

The final browser investigation also found a **test timing error**: a half-second
repeat replay completed between remote polling calls. Three recorded media-event
traces showed correct play/playing/pause behavior. The E2E assertion now observes
the transition in the browser and verifies its final frame; playback production
code was not changed to satisfy the test.

## Validation and its limits

The [validation record](full-pipeline-phase-2-validation.md) contains exact commands,
logs, RED/GREEN history, environment, interpretation and blocked gates.

- GPU backend: **1,398 passed**, 19 existing Starlette deprecation warnings,
  221.93 seconds. Includes 42 new audit cases, all prior score coverage and real
  FFmpeg/PyAV/HLS/clip/PDF API integration.
- Frontend: **162 passed in 40 files**, 5.28 seconds; 13 new audit cases. Final
  TypeScript + Vite build passed (Vite 6.39 seconds).
- Final focused Python check: **20 passed** after style-only changes. Scoped
  Ruff passed. Scoped Biome has no errors; test assertion warnings are recorded.
- Browser: **8 passed in 2.6 minutes**, against a fresh model-free server. Real
  upload/playback/range delivery, navigation, review, exports, score correction
  and reload passed. The authentication failure UI deliberately uses mocked
  rejection; controlled point/player observations are not ML labels.
- Real existing TrackNet on idle GPU1: finite FP32 CUDA outputs exactly equal to
  the HEAD baseline (maximum/mean difference0); eight existing proxy frames
  decoded and one detector call completed. No weights or thresholds changed.
  These are bounded runtime/parity checks, not accuracy or throughput evidence.
- Fresh ONNX attempt: **partial/exit2**, missing `onnxscript`; `onnx` also absent.
  No graph was published or dependency installed. Native TensorRT remains untested.

Independent review caught the active-snapshot closure and encoder callback cleanup
gaps before final validation; their regressions failed before correction and pass
in the full suite. The final Git diff was reviewed by component owners and the
integration owner. Initial failed builds and interrupted/failed browser attempts
are preserved and explicitly separated from successful results.

## Remaining blockers, missing features and debt

The detailed lists in the ledger are authoritative. The material limits are:

- No independently reviewed, exhaustive, source-bound target labels or held-out
  match evaluation for shuttle/contact/hitter/stroke/rally/point/score/doubles/line
  accuracy. Geometric court exclusion and synthetic controls are not substitutes.
- No per-frame source-to-CFR observation/duplicate map or independent same-camera
  replay-content recognition. Floor homography is not airborne3D measurement.
- External Redis API/worker/crash recovery has not been run. Command delivery has
  no durable processing acknowledgement; a generic correction's HTTP202 is only
  queued. Multiple temporal writers and distributed reset fences are unsupported.
  Detected generation crossing fails explicitly rather than serving mixed data;
  it is not a distributed snapshot protocol.
- Raw Q&A handle lifetime across asynchronous reanalysis, real provider grounding,
  semantic answer correctness and the broader shutdown/dispatch race remain
  unverified. Numeric/citation validation alone is narrower than semantic proof.
- InpaintNet, second-opinion/live shuttle, learned racket detection, live BST shot
  classification, native TensorRT cache lifecycle, 3D speed/trajectory and automatic
  line judging are not established production capabilities. Some are explicitly
  unsupported or shadow-only; registry/profile entries do not prove execution.
- Inactive profile controls, misleading model alias/prose, incomplete metric
  instrumentation and standard21/30 OCR assumptions remain configuration debt.
  Existing media cache has no automatic pipeline-version migration; preserve and
  explicitly regenerate a proven-bad old proxy and dependent results.
- Authentication is single-user cookie/CSRF protection, not tenant/RBAC isolation.
  No public deployment or production data reanalysis was performed.

## Git preservation and handoff

Branch remains `full_pipeline`, HEAD remains
`cc73688630e40d534d94b7ef32bd0cbfed7e0571`; the real index remains empty. No commits,
push, reset, clean, force checkout or deployment was performed. Task changes were
transported through temporary-index Git patches to an isolated server checkout.

Unrelated `apps/web/package.json` and `pnpm-lock.yaml` SHA256 values exactly match
the start-of-audit receipt. All17 pre-existing Design prototype deletions remain.
`Part2/`, `SportsVideoAnalysis/`, `client-website/`, `Design/references/` and other
unrelated untracked work were not edited. The primary server checkout and
`apps/web/dist.old/` remain preserved. No SSH password or application secret was
written into this repository.

Changed production files are limited to the existing API, generic engine, badminton
domain/perception and React boundaries described above and in the earlier score
ledger. Regression files, the model-free browser fixture/shared CDP harness and
audit documents accompany them. The complete scoped path manifest is appended
below; unrelated user changes are intentionally excluded.

Validation artifacts remain under
`/home/administrator/Desktop/sport-analytics/full-pipeline-audit-validation-20261103`.
The server uses the existing `../gpu-env.sh` and `Sports_Analytics/.venv`; the normal
port8010 application has not been replaced by this candidate. Test fixture routes
exist only in the disposable E2E server. Stop/cleanup and final patch fingerprints
are recorded with the final acceptance result.

Final source/test-only patch SHA256 is
`637b4202ecfece965391024ca089fbe42d55994b6df56a23a1ee1613acb846f2`
(74 source/test/harness paths; documents excluded from the fingerprint).
All 86 task paths are listed below. The disposable server has been stopped; the
primary port8010 application still returns healthy at its original HEAD, and
Cloudflare remains disabled.

## Complete scoped file manifest

```text
apps/api/src/bai_api/cli.py
apps/api/src/bai_api/product_analytics.py
apps/api/src/bai_api/routes/exports.py
apps/api/src/bai_api/routes/identity_reviews.py
apps/api/src/bai_api/routes/sessions.py
apps/api/tests/test_cli_bind_contract.py
apps/api/tests/test_export_publication_integrity.py
apps/api/tests/test_external_lifecycle_contract.py
apps/api/tests/test_product_projection_integrity.py
apps/api/tests/test_score_read_snapshot.py
apps/api/tests/test_score_synchronization.py
apps/web/e2e/fixtures.ts
apps/web/e2e/production.spec.ts
apps/web/e2e/review.spec.ts
apps/web/e2e/score_fixture.py
apps/web/e2e/score-integrity.spec.ts
apps/web/e2e/server.py
apps/web/e2e/smoke.spec.ts
apps/web/src/features/analytics/useInsights.refresh.test.tsx
apps/web/src/features/analytics/useInsights.ts
apps/web/src/features/library/LibraryPage.lifecycle.test.tsx
apps/web/src/features/library/LibraryPage.tsx
apps/web/src/features/player/EvidenceDetails.test.tsx
apps/web/src/features/player/EvidenceDetails.tsx
apps/web/src/features/player/ScoreBug.test.tsx
apps/web/src/features/player/ScoreBug.tsx
apps/web/src/features/player/useHls.failure.test.tsx
apps/web/src/features/player/useHls.ts
apps/web/src/features/product/Help.tsx
apps/web/src/features/product/Moments.tsx
apps/web/src/features/session/derive.test.ts
apps/web/src/features/session/derive.ts
apps/web/src/features/session/IndividualAnalytics.tsx
apps/web/src/features/session/PairAnalytics.tsx
apps/web/src/features/session/ReviewedAnalytics.failure.test.tsx
apps/web/src/features/session/SessionPage.test.tsx
apps/web/src/features/session/SessionPage.tsx
apps/web/src/features/session/tabs/AskTab.tsx
apps/web/src/features/session/tabs/RalliesTab.test.tsx
apps/web/src/features/session/tabs/RalliesTab.tsx
apps/web/src/features/timeline/Timeline.tsx
apps/web/src/stores/session.score.test.ts
apps/web/src/stores/session.test.ts
apps/web/src/stores/session.ts
docs/architecture/audits/backend-runtime-20261103.md
docs/architecture/audits/frontend-analytics-20261103.md
docs/architecture/audits/perception-timeline-20261103.md
docs/architecture/event-score-integrity-20261103.md
docs/architecture/event-score-integrity-ledger-20261103.md
docs/architecture/full-pipeline-audit-20261103.md
docs/architecture/full-pipeline-contracts-20261103.md
docs/architecture/full-pipeline-operations.md
docs/architecture/full-pipeline-phase-2-ledger.md
docs/architecture/full-pipeline-phase-2-validation.md
docs/superpowers/plans/2026-11-03-event-score-integrity.md
docs/superpowers/plans/2026-11-03-full-pipeline-audit.md
engine/src/bai_engine/bus.py
engine/src/bai_engine/config.py
engine/src/bai_engine/media/ffmpeg.py
engine/src/bai_engine/media/probe.py
engine/src/bai_engine/media/proxy.py
engine/src/bai_engine/runtime/registry.py
engine/src/bai_engine/runtime/runner.py
engine/src/bai_engine/store/events.py
engine/src/bai_engine/store/sessions.py
engine/tests/test_event_transactions.py
engine/tests/test_external_generation_refresh.py
engine/tests/test_ffmpeg_probe_isolation.py
engine/tests/test_media_stream_selection.py
engine/tests/test_model_archive_integrity.py
engine/tests/test_model_fetch_publication.py
engine/tests/test_redis_timeout_contract.py
engine/tests/test_runtime_stop_integrity.py
sports/badminton/src/bai_badminton/analytics/match.py
sports/badminton/src/bai_badminton/analytics/rebuild.py
sports/badminton/src/bai_badminton/engine.py
sports/badminton/src/bai_badminton/perception/tracknet.py
sports/badminton/src/bai_badminton/plugin.py
sports/badminton/src/bai_badminton/rules/__init__.py
sports/badminton/src/bai_badminton/score_ocr.py
sports/badminton/tests/test_analytics_integrity.py
sports/badminton/tests/test_analytics_point_acceptance.py
sports/badminton/tests/test_score_event_integrity.py
sports/badminton/tests/test_score_ocr_delay.py
sports/badminton/tests/test_score_reading_integrity.py
sports/badminton/tests/test_tracknet_background_retention.py
```
