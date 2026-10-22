# Pipeline and independent validation notes

Inspection: 23 October 2026, branch `front-end`, remote authoritative checkout
`/home/administrator/Desktop/sport-analytics/Sports_Analytics`.

## Authoritative processing path

| Stage | Implementation and evidence |
| --- | --- |
| Ingestion | `routes/sessions.py` accepts uploads and rights-acknowledged YouTube imports. Other live-source enum values do not establish a live ingestion service. |
| Media | `runtime/runner.py` probes the source, makes a constant-rate H.264 proxy and progressive fMP4 HLS segments, then makes scrubber sprites. The proxy timeline is canonical for event frames. |
| Court | Warm-start keyframes seed selected court geometry. Codec-6 perception caches bind geometry and fixed-camera policy; see `multi-court-isolation.md`. |
| Perception | Selected-court admission and flight masks constrain player/shuttle candidates before semantic inference. TrackNet, player detection and pose are optional profile stages. |
| Identity | `identity.py` selects at most one person per court half and assigns P1/P2. Four individual doubles identities and pair responsibilities are not established by these records. |
| Semantics | Contacts fuse motion/proximity/pose evidence. The rule stroke fallback caps confidence at 0.7. Rally/phase/outcome and BWF state feed the event log. |
| Persistence | Content-addressed media, SQLite session catalogue, per-session SQLite events/state snapshots, Parquet track chunks, and cached perception segments. |
| Analytics | `analytics/rebuild.py` folds the live event view, including corrections and official-play exclusions. Court movement reads persisted player coordinates. |
| Playback | Authenticated HLS/proxy/sprite endpoints. Playlists have `no-cache`; immutable media segments have long cache headers. MP4 partial delivery is provided by `FileResponse`. |
| Status | Runner progress is published through the session WebSocket; polling refreshes session records. Analysis can finish later than video preparation. |

The runner's final frontier can exceed the last decoded frame because its segment
frontier is padded. Clamp UI progress to 100%; use media `n_frames` and fps for
video boundaries. A stopped runner has no dedicated paused status in the existing
session enum. Do not claim that persisted `analysing` alone proves a worker is
currently running.

Reanalysis resets event/track stores and keeps compatible perception. Human
corrections/manual calibration are carried forward. Back up real session results
before any reanalysis. Independent checks below did not reanalyse real sessions.

## Recorded evidence available for repeatable read-only checks

| Session | Source and canonical media | Persisted analytics checked |
| --- | --- | --- |
| `01M55MFY9GQF6ZXP2SQPQ8X1KG` | SampleRally, 16 s, 30 fps, 1280×720 | 0 official rallies, 1 excluded rally, mean shots unavailable, no highlights |
| `01M55NQMRAS0ATB73XE3XA6S74` | Antonsen vs Farhan, 483 s, 25 fps, 1280×720 | 24 official + 1 excluded rally; 262.3 s active play; mean 10.88 shots; 10 highlights returned |
| `01M56T2EED5Z7W9VTGG19FHNTF` | He/Ren vs Rankireddy/Shetty, 486 s, 25 fps, 1280×720 | Recorded doubles footage exists; separate four-player identity validation is missing |
| `01M5EXGZNEVGYAJ3AR6CJS5ZG9` | A02 CCTV, 760 s, 30 fps proxy, 1270×720; VFR 15 fps source | 50 official + 14 excluded rallies; 205.3 s active play; mean 4.32 shots; 10 highlights returned |

For SampleRally, Antonsen–Farhan, and A02, authenticated live requests for
`Range: bytes=0-1023` returned HTTP 206, a correct `Content-Range`, and exactly
1,024 bytes. Credentials were read into process memory and were not saved to test
sources, reports, or logs.

These are consistency and media-delivery checks against stored outputs, not
labelled shuttle/contact/stroke/scoring accuracy measurements. The court-isolation
report's geometric exclusion counts are not event accuracy.

## Independent coverage matrix

| Workflow | Test/evidence |
| --- | --- |
| Empty home/matches/moments/people/progress/settings/help | `e2e/production.spec.ts`, real empty throwaway server, desktop + mobile |
| Upload → FFmpeg/HLS → scheduler → persisted completion | `e2e/smoke.spec.ts` and `e2e/production.spec.ts`, synthetic input video, model-free profile |
| MP4 ranges, playlist freshness, segment path allowlist | `e2e/production.spec.ts`; live read-only checks above |
| Playback clock, play/pause, exact next frame, speed, overlays | `e2e/production.spec.ts` |
| Auth failure and unknown-match recovery | `e2e/production.spec.ts` UI contract; API authentication/CSRF tests |
| Official/excluded rallies, player filters, correction lineage | API analytics tests and frontend evidence unit tests |
| Cache refresh after equal-count event reset and track updates | `apps/api/tests/test_product_analytics.py` |
| Court selection/camera/admission regression | `sports/badminton/tests/test_court_isolation.py` and related existing suites |

The model-free end-to-end server validates transport and product behavior. It
does not create meaningful sporting events, and its empty analytics are expected.
Real persisted-video review is a separate read-only integration check.

## Executed product checks

The final integrated browser suite passed **6 tests in 19.6 seconds**. It covers seven
empty product routes at desktop/mobile widths, upload and real media playback,
range delivery, presented-frame stepping, speed/overlays, all match tabs, selected
player URL/refresh persistence, unavailable pair attribution, auth failure,
missing-record recovery, display/reduced-motion refresh, match search, exports,
and the system view. The independent frontend unit suite passed 43 tests.
The final complete CPU backend regression passed 228 tests in 129.20 seconds,
including the stubborn-worker deletion guard. Independent checks also ran the
preceding complete 227-test suite and a subsequent 23-test safety/API suite.
Two existing Starlette deprecation warnings remained. GPU, slow, and
network-marked tests were excluded from the complete CPU regression.

Frame-step assertions first establish a known paused media frame. A presented
frame callback still in flight immediately after pausing can legitimately update
React's throttled frame label; reading that transitional label as the expected
next-frame baseline made the previous smoke assertion intermittent.

An authenticated read-only app (engine disabled, existing real session stores)
reconciled Antonsen–Farhan's 25 visible rally records, 24 counted rallies, and 11
counted P1 wins with the insights API. Rally 1's Watch control paused the actual
video at 29.3 seconds, exactly `(frame_end + 0.5) / 25`; Again and Loop replayed
within the same bounded clip. The final 390 px court page had no horizontal
overflow. The first check exposed 63 px overflow from an intrinsic 420 px heatmap
canvas; the responsive canvas correction was verified against the same route.
No uncaught JavaScript errors or failed HTTP requests occurred during that live
recorded-data review. No live session records were modified.

Review screenshots are held outside the source tree at
`/tmp/bai-front-end-qa-screens/`, with `production-*` and `reference-*` pairs.
Prototype captures dismiss the initial identity dialog so the actual tab layout
can be compared. The snapshots compare structure, typography and interaction
placement; numeric pixel differences include the deliberate replacement of
generated charts/footage with actual measured evidence.

## Commands and environment

Always source the existing Pascal-compatible runtime before tests/media work:

```sh
cd /home/administrator/Desktop/sport-analytics/Sports_Analytics
source ../gpu-env.sh
.venv/bin/python -m pytest apps/api/tests -q
.venv/bin/python -m pytest engine/tests sports/badminton/tests agents/tests -q
cd apps/web
pnpm test
pnpm typecheck
pnpm build
BAI_E2E_PORT=8767 pnpm exec playwright test
```

The sourced environment selects Node 22, FFmpeg, and `.venv`, and sets
`UV_NO_SYNC=1`. Do not run dependency synchronization that replaces the configured
CUDA environment. The normal bare SSH PATH selected obsolete Node 12 during
inspection. Browser tests require the Playwright version's matching Chromium
headless shell; use `pnpm exec playwright install chromium --only-shell` if absent.

`e2e/server.py` uses a separate temporary data directory and model-free profile.
It serves the built `apps/web/dist`, not a Vite source tree. Build after frontend
changes before running browser tests. Never point its mutating upload workflow
at production sessions or reuse the production API port.
