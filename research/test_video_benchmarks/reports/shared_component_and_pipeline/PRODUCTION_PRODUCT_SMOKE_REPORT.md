# Isolated product workflow validation — 2026-11-05

The actual built frontend, FastAPI application factory, `EngineService`,
`LocalBus`, upload storage, media transcode, segment analysis, event store,
WebSocket gateway and export routes ran together in a new loopback-only process.
Firefox uploaded the retained 67-frame MP4 through the real recording form and
reached completed results. This validates product and transport behavior with
every neural provider explicitly disabled. The input contains generated frame
barcodes, not badminton; no sporting or model accuracy follows from this test.

## Execution and isolation

Harness: `research/production_product_smoke.py`; four focused harness controls in
`research/tests/test_production_product_smoke.py` passed. The two unchanged-source
browser controls are preserved separately:

- `artifacts/benchmarking/experiments/prod_20261105_product_smoke_v1/`
- `artifacts/benchmarking/experiments/prod_20261105_product_smoke_v2/`

Each contains exact executed harness bytes, configuration and source/build/input
hashes, command lines, server and geckodriver logs, real HTTP/WebSocket traffic,
screenshots and DOM text, downloaded exports, session state and process cleanup.
The source is the then-frozen `85993259a3a2838881ed2b18658a07967058d191`
checkpoint. `main` remains `301baf08be5e989dd0ed93cb885733c3cf6f356a`.

The existing isolated `prod_20261105_frontend_release_v2/build` was served by a
separate instance of the application factory. The harness configures that
instance's frontend location in its own process; it never replaces deployment
files. Each run owns a fresh empty data tree, empty model manifest, diagnostic
profile, ephemeral application/WebDriver ports and Firefox profile/download
directory. No existing server, Redis deployment, port 8010 service or deployed
`dist` directory was changed or addressed.

The profile explicitly sets shuttle, detector, pose and stroke neural models to
`none` with backend `none`; optional neural stages are absent. Existing rule
components remain available. `CUDA_VISIBLE_DEVICES` is empty in the owned server.
An explicit FFmpeg adapter excludes NVENC from encoder enumeration and rejects
GPU encoder commands, then executes the installed FFmpeg unchanged for actual
media work. Recorded commands show `libx264`, no neural model weights and no GPU
encoder invocation. This is CPU product validation, not an inference performance
benchmark or evidence of GPU fallback quality.

## Observed behavior before fixes

| Actual check | Result | Evidence |
| --- | --- | --- |
| Browser upload, preparation and analysis | `ingesting → ready_to_play → analysing → analysed`; 67 frames, 30 FPS, frontier 66, duration 2,233,333 µs | v2 `status_timeline.json`, `completed_session.json` |
| Live binary WebSocket | Actual msgpack `hello`, ingest/status, tracks, events and state; final status `analysed`, frontier 66 | v2 `requests.jsonl` |
| Browser HLS seeking | All six targets 66, 0, 30, 59, 60, 1 show the matching independently decoded pixel barcode; no missing presented-frame callbacks | v2 `evidence/browser_seeks.json` |
| Completed empty analytics | Zero counted rallies and shots, score unavailable, player names null; participant/identity guidance remains visible | v2 `evidence/04_completed_empty_analytics.*`, `analytics.json`, `individual.json`, `estimated_individual.json` |
| Real export links | Browser downloaded rallies CSV, classic CSV, event JSONL and summary JSON; separate HTTP downloads returned 200 | v2 `downloads/`, `evidence/`, `results.json` |
| Source ownership | Public source URI is empty; unknown session and its export return 404; content-addressed reupload returns 200 and the same own session ID | v2 `results.json`, `requests.jsonl` |
| Invalid and empty media | A malformed container uploaded through the browser reaches real `failed`; an empty HTTP upload is accepted asynchronously then reaches `failed` | v2 `failed_session.json`, `empty_failed_session.json` |
| Preservation/cleanup | Core/build/input guards unchanged; owned server, WebDriver and Firefox PIDs gone; both owned ports closed | v1/v2 `results.json`, `cleanup_verification.json` |

The empty completed run still contains two generic rule events (`scene` and
`activity_interval`). It contains no contact, stroke, rally or point event. The
events export default is the live folded event log; this test does not establish
complete correction-history export behavior. PDF and clip exports were not
invoked. The anonymous P1/P2 scoring slots displayed as 1 and 2 are not reviewed
athlete identities. The known/unknown accounting endpoints report no individual
measurements or reviewed evidence for this fixture.

## Reproduced defects and staged corrections

The browser check found actual product defects rather than only testing a proposed
implementation. Screenshots/DOM text and HTTP/binary WebSocket payloads independently
confirm them:

1. An empty or failed `rallies.csv` contains only `match_id\r\n`. A populated
   application CSV has 17 public columns. The candidate declares that existing
   populated schema explicitly, preserving columns for all empty states and
   leaving nonempty rows, times, null scores and private-field exclusion intact.
   This application CSV is separate from the seven-column benchmark contract.
2. A failed unprobeable recording with `media=null`, `frontier_frame=0` and zero
   processed frames displays “100% of analysis proxy frames processed.” The
   candidate shows coverage unavailable without media and uses actual processed
   frame counts when a denominator exists, keeping a foreign active session from
   supplying progress. Completion status alone no longer manufactures coverage.
3. The same failed recording's export panel says “Analysis is still running.”
   The candidate labels failed exports as partial; running and completed states
   retain distinct behavior.
4. The public failed session and the live binary WebSocket status expose FFmpeg's
   absolute server-side source path. The candidate projects one generic actionable
   failure detail at the API boundary for HTTP/summary/hello and live statuses.
   The full private session detail, raw bus message and server logs remain intact.

Staged evidence: `prod_20261105_product_candidate_v1/` contains original and
candidate copies, a proposed patch, all test sources and separate red/green logs.
No guarded production file was edited during the external inference freeze.

| Staged control | Existing source | Copied candidate |
| --- | --- | --- |
| API/export/public/WebSocket contracts | 7 failed, 3 passed | 10 passed, 2.52 s |
| Timeline/export UI contracts | 4 failed, 4 passed | 8 passed, 2.86 s |
| Candidate frontend TypeScript | Not a defect discriminator | Exit 0 |

The API controls separately test a failed WebSocket hello and a live failure
following a healthy hello, so sanitizing HTTP alone cannot pass them. Negative
controls preserve nonempty CSV frame/time/null-score values, healthy details,
live status frames, in-progress export wording, completed coverage and partial
failed coverage. The production application of this staged patch and the fresh
post-fix browser run must be recorded separately after source-freeze release.

After all four external workers completed and their source guards passed, the
orchestrator released the source freeze and approved application of the five
reviewed production files. All original digests matched before application, and
`git apply --check` passed. The actual source then passed 15 focused API/export/
WebSocket tests (one existing FastAPI 422 deprecation warning, 2.60 s), 10 frontend
tests across the new failure contract and existing timeline cases (2.49 s),
TypeScript checking and `git diff --check`. Logs are the separate
`api_actual_green.log`, `web_actual_green.log` and `web_actual_typecheck.log` in
the candidate directory. These tests do not replace the pending new-build,
post-fix real-server/browser run. The current harness has five controls, including
rejection of a deliberately incorrect measured barcode identity and rejection of
the observed pre-fix export schema when fixed-output checks are requested.

## Completed post-fix product replay

`prod_20261105_product_smoke_v3/` is a new actual-server/browser run using the
settled API/service/agent source and the isolated frontend release-v3 build.
`--expect-fixes` completed successfully; all 307 source files, 45 build files and
the original fixture passed exact before/after hash guards. The build's own
`prod_20261105_frontend_release_v3/build_receipt.json` binds its changed TypeScript
sources through exact sourcemap bytes and file hashes; the integrated frontend
passed 210 tests across 44 files before this replay.

The browser repeated real upload, live progress and completion at frame 66 of 67.
All six independently decoded barcode identities matched, with no missing
presented-frame callbacks. All four browser-downloaded file hashes match the
corresponding HTTP exports. The same-source reupload returns 200 and the same
session ID; unknown session and export requests remain 404. Completed zero-rally
and failed exports both retain the full 17-column application CSV schema.

The failed source now displays “Analysis coverage unavailable” and “Analysis
stopped before completion — exports contain partial results.” Both HTTP failure
detail and the real binary WebSocket `status` message contain the shared generic
detail without an internal media path. A separate read of the owned repository
after shutdown confirms that the original private source URI and full raw error
detail remain retained. Screenshots were inspected, including
`evidence/07_failed_exports.png` and `evidence/08_failed_coverage.png`.

The server, WebDriver and Firefox PIDs are independently confirmed gone and their
owned ports closed in `cleanup_verification.json`; the exact invocation and
runtime log are preserved in `commands.json` and `execution.log`. No GPU work,
deployment change or historical-output rewrite occurred. The failed video pane
still displays a loading placeholder without a decodable source; the page's
failure notice and coverage are correct, and no image/measurement is invented.
This residual presentation behavior is bounded evidence, not a claim that all
failure-state UX has been exhaustively validated.

## Superseding failed-pane fix and final browser replay

The remaining loading placeholder above was subsequently reproduced by five
failing frontend checks and fixed in `VideoStage.tsx`. A failed recording without
media now displays “Video unavailable” and an explicit retry/add-recording
instruction. Loading/recovery for recordings with existing media and ready
playback after a later analysis failure remain available. The stage reads live
status only for its own session. Thirteen new regressions include valid initial
preparation, stream recovery, same-recording retry, ready partial playback and
foreign-session status controls; the focused set including existing native-HLS
and playback tests passes 25 cases.

`prod_20261105_frontend_release_v4/` contains the new isolated build and receipt;
its three changed/relevant source files match exact sourcemap content and all 45
asset hashes are recorded. TypeScript passed; the build completed in 7.32 s. The
first full frontend run passed 222 and failed one existing calibration save-point
test. That failure is preserved in `tests.log`, not removed from reporting. The
unchanged isolated calibration tests pass 3/3 and the unchanged full repeat passes
223/223 across 45 files (5.65 s). No calibration source or test was edited by this
workstream; the timing-sensitive failure is under separate causal review.

The new actual-server Firefox `prod_20261105_product_smoke_v4/` then passes all
earlier upload/progress/ownership/export/private-detail checks, six exact pixel
seeks and explicit absence of a loading claim in the failed video pane. Its
`failed_video_pane` evidence contains the new unavailable/retry wording. Source,
build and input guards pass; all owned processes and ports close. Earlier v1–v3
artifacts and their exact executed harness snapshots remain intact.

## Actual nonempty neural-results-to-product replay

The same harness also supports a separate `--completed-run` mode with the actual
application factory's `start_engine=False`. It imports read-only byte copies of
completed Test7-v2 results into an isolated new catalogue: original session JSON,
closed event database, 710 track chunks and finalized playback assets. There is
no connection to the original SQLite database, no WAL/SHM processing, no hardlink
or writable original route, and no new inference. The original files are read
only as bytes for hashing/copying; all 898 consumed-file hashes remain unchanged.
Only the new catalogue's save timestamp changes; session/event IDs, source SHA,
event values, intervals, track bytes and media bytes remain unchanged.

Selected evidence is `prod_20261105_neural_results_product_v3/`. All 896 physical
copies use independent inodes. The browser loads actual HLS footage with the
copied tracks and event evidence, opens nonempty results and four export links,
and displays the completed event backlog before screenshots. Public event export
IDs/counts exactly match the copied durable live fold and original producer:
32 `rally_end`, 32 `rally_start`, 248 contacts and 248 linked strokes. The UI shows
32 rally candidates, 65 of 248 shot events classified, anonymous tracked/pose
estimates and explicit unknown/estimated evidence; these are system outputs,
not reviewed physical accuracy.

The application CSV contains **21 intervals marked official by existing event
phase logic**, with every exported boundary exactly matching its durable row.
The other 11 raw rally candidates remain in the event log. No count was forced
to 32 and phase/analytics logic was unchanged. The classic CSV remains header-only
when no winner is available, preserving its existing contract rather than
inventing score/identity. The original Test7 source hash is retained and its
private URI is empty in public session/summary responses. All four browser file
hashes match their HTTP exports; source/build/original-result guards and process
cleanup pass.

The preliminary neural-product v1 receipt's “original database opened” wording
meant no SQLite connection; the v2/v3 field explicitly says
`original_sqlite_connection_opened=false`. V3 additionally waits for the full
WebSocket event backlog before the shot view. All three are product replays of
the **same** completed neural run, not independent inference repetitions. Eight
research harness controls pass, including a guard that rejects any SQLite
connection to the original path, refusal of original WAL sidecars, independent
copy/hash preservation and rejection of incomplete frame coverage. No annotation
file, new model, ground-truth court/identity input or label-based offset enters
this product workflow.

## Final calibration ordering repair and v5 product gate

The v4 calibration observation received an independent causal investigation in
`PRODUCTION_CALIBRATION_SAVE_REPORT.md`. The original failed run did not capture
its complete payload or scheduling order, so its exact cause cannot be recovered
retrospectively. A controlled native first-enabled DOM click reproduced the same
missing-coordinate signature on the unchanged old component: TanStack's mutation
observer still held an earlier empty-points closure after the rendered Save
button became enabled. Three valid contracts failed on the actual old source and
passed on the copied candidate and repaired actual source. This establishes the
software ordering defect, not its human/browser recurrence frequency or the
original run's precise schedule. The backend rejects insufficient geometry; no
claim is made that invalid geometry was persisted.

The narrow repair passes `{sessionId, points, frame}` as explicit click-time
mutation variables. Existing geometry seeding, fitting, point values and success
behavior are preserved. Actual calibration focused tests pass 6/6; the first full
frontend run on the repaired source passes **226/226 across 46 files**, with
TypeScript and isolated release-v5 Vite build successful. Its receipt binds exact
sourcemap content for CalibratePage, VideoStage, Timeline and ExportTab and all
45 generated assets. Earlier v4 failure/repeat logs remain intact.

The final actual upload-to-results browser check is now
`prod_20261105_product_smoke_v5/`, using that bundle and final API/service source.
All **309 source files, 45 build files and the fixture** pass before/after guards.
All six presented pixel identities and four hash-matching real browser downloads
pass. The completed and failed application CSVs retain 17 columns, failed media
shows unavailable instead of loading, partial exports/coverage are truthful,
public HTTP/binary WebSocket details are sanitized and full private diagnostics
remain stored. Content-addressed reuse and unknown-session404 controls pass. The
owned server, WebDriver and Firefox PIDs are gone and both owned ports closed.
`results.json` SHA256 is
`3c2bb9d86cc4165d1f0c7669bfedaa63afd38141b8fc9b24fc51dc6823751e78`.

The nonempty completed-Test7 product-v3 evidence remains explicitly the prior
release-v4 rendering stage; its exact raw/official event and source-integrity
checks are not another neural run or a claim that the final browser uploaded and
inferred the full match. No inference, label value, default model/profile,
deployment or historical result changed to complete the v5 product gate.

## Compatibility and remaining scope

No session fields, event schema, frame indexing or interval semantics change. No
persisted diagnostics or historical exports are rewritten. Existing populated
application CSV consumers retain the same 17 columns; previously schema-truncated
empty CSVs gain those columns on a new download. Clients should treat public
failure details as user-facing text, not parse FFmpeg internals; full diagnostic
investigation uses the unchanged private server log/session. No stored-data or HLS
migration is needed for these four product corrections.

This automated local browser run does not prove authenticated/shared-host isolation,
Redis command transport, remote LLM behavior, production deployment readiness,
network resilience, accessibility, human usability or badminton analytics accuracy.
It does establish that the tested actual upload, progress, result, source and
export paths work together and exposes the recorded failure-state defects.
