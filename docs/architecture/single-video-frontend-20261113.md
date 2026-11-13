# Single-video frontend validation — 13 November 2026

Branch: `engineering/deep-pipeline-overhaul-20261113`; starting commit `e558fd9`.
The integration owner records final commits and backend acceptance in the main
validation report. This workstream owns `apps/web/` and this report. No historical
evaluation video was uploaded, opened or processed by this workstream. Unit
fixtures are synthetic; they are never substituted for application results.

## Status

The actual built application completed five iterations of the **same selected
video** (run01/02/03/04/06). Run05 was interrupted when the user's turn abort
stopped its attached service; its partial artifacts remain separate. The final
run06 used source commit `8110422` and a detached backend/browser observer. It
processed all 4,462 frames, exercised all ten session tabs and eleven source
timestamps, and passed the focused presentation, uncertainty, selection,
navigation and unsaved-editor checks described below.

Source fixes are integrated in the working branch. The final frontend checks
pass: **264 tests / 52 files**, TypeScript, changed-file formatting and production
build. Run06 reduced page-issued analytics requests from 1,368 to 153 and heatmap
requests from 2,189 to 302 compared with run04. Combined frontend/backend repairs
reduced browser-observed upload-click-to-completion from 773.924 to 648.574 s;
this does not isolate a frontend-only speedup.
Physical detection accuracy, correct contacts, sporting outcomes and reviewed
athlete identity are separate from rendering correctness. Empty highlights,
unknown strokes and unavailable named-player analytics remain explicit. The
frontend does not establish their sporting validity.

## Diagnosis and implemented changes

| ID | Evidence / root cause | Implementation | Validation and limits |
|---|---|---|---|
| FE01 | `TrackBuffer.displayPose` promoted every non-null pose array to source=current/age0, ignoring `pf` | Exact source-frame equality is required for a fresh pose. Legacy unstamped coordinates display unknown source and cannot become a forward hold. | Synthetic current/stale/unknown-source tests pass; source stamps are never synthesized. |
| FE02 | Optional backend `ctx` columns were ignored; same physical-camera resets could preserve old pose/shuttle/court continuity | Preserve player/camera contexts; stop holds/trails at changed contexts or invalid intermediate camera views. Validate columns before mutation. | Synthetic malformed-column atomicity, same-camera epoch and invalid-view regressions pass. |
| FE03 | Real video: proxy analysis762×720, browser presentation763×720 due non-square sample aspect ratio. Overlay scaled both axes with the intrinsic video width. | New pure video-coordinate mapping uses presentation dimensions for contained display geometry and analysis dimensions for independent raw x/y scales. VideoStage passes analysis dimensions; calibration SVG and inverse pointer mapping use the same raw-pixel contract. | Run02 live canvas transform equals expected scales; run03 unsaved click/drag exactly match raw coordinates. No inference pixels or SAR metadata changed. |
| FE04 | Calibration container border was included in pointer inverse, although SVG image rectangle was smaller | Inverse mapping reads the actual SVG rectangle. Bars remain outside valid image coordinates. | Run03 click190.5,288 and drag228.6,324 each have zero raw-pixel error; Undo works. No calibration was saved. |
| FE05 | Actual uncounted intervals showed `Rally0`; headline called ambiguous intervals observed rallies; candidate event counts appeared as shots | Preserve positive official numbers; use original-list ordinal Candidate1/2/etc for unofficial entries. Summary says recorded rally candidates and shot events. | Run04 rows/summary pass; run06 evidence details, clip labels and exact-event keyboard navigation also pass. No interval is selected by a shared rally_no=0. |
| FE06 | Actual Recording & quality section claimed two court-side identities and hid `meta.degraded`/`meta.capabilities` | Render recorded limitations and provider status/reasons; availability is distinguished from accuracy. Track episodes, reviewed athletes and scoring slots are explicitly separate. Missing legacy metadata remains unknown. | Three synthetic metadata tests and actual run04/run06 panels pass. Run03 old wording remains as before evidence; named identity still requires review. |
| FE07 | Distance-weighted heatmap totals were rounded and labelled samples; presence described time without dwell-time weighting | Movement totals retain decimal metres and are estimates. Presence is sampled feet positions. Loading state is explicit. | Two synthetic response tests pass. Positive calibrated named-player heatmap is not exercised by the selected workflow. |
| FE08 | Session highlights omitted evidence status and ranking-score semantics; play action dropped source event ID | Preserve optional evidence fields in types; show source count/status and estimated-ranking qualification; pass canonical rally event ID to evidence navigation. Filter says scoring sides. | New/legacy synthetic highlight tests pass. Real selected runs returned no eligible highlights; positive ranking content is not empirically validated. |
| FE09 | Explicit unavailable highlight session silently fell back to first loaded recording | Explicit session selects exactly that record or shows unavailable; only empty selection defaults first. Disabled placeholder keeps browser select from displaying another record. | Two synthetic metadata records verify missing/empty/exact selection, and no wrong insights request. Actual run04/run06 browser checks preserve the missing selection and make no other-recording insights request. |
| FE10 | Negative canonical IDs could be named or joined to another unresolved observation's prior pose/motion | Negative-ID labels say Unresolved observation; prevent reviewed-name binding, pose holds and court trails for unresolved canonical identities. Preserve current raw observation displays. | Synthetic distinct -1 wire groups, pose/motion rejection, review rejection and label tests pass. Backend wire grouping and run06 source-frame rendering are integrated: frame421 preserves and draws both raw8/canonical-10 and raw3/canonical-5 independently. No named identity is inferred. |
| FE11 | Upload helper claimed unspecified format always means singles | Explain sustained court-observation inference and identity/scoring review. | Real library screenshot inspected. |
| FE12 | Run04 live browser issued 1,368 analytics and 2,189 heatmap responses. Each analyticsVersion event independently invalidated the same query in SessionAnalytics, nested StatsTab and movement observers, repeatedly cancelling/restarting work. | One QueryClient/session refresh coordinator deduplicates observers; coalesces live derived snapshots to a 2 s cadence; preserves in-flight dirty work; supersedes initial/live requests at completion; isolates revision resets; disposes timers/listeners. Queries consume AbortSignal and reuse recently fetched snapshots. Raw WebSocket observations remain immediate. | Eight fake-timer regressions pass; run06 counts fall to 153/302 and terminal WebSocket status is followed by fresh successful analytics/P1/P2 requests. |
| FE13 | Run04 editor accepted pointer edits while its real proposal was loading; late initialization replaced those points and cleared Undo history. | Ignore edits until video/proposal/seed initialization is ready. Explain that automatic court geometry can be wrong. | Deferred-response regression passes. Run06 actual response with CDP transport delay ignores the pending click, then permits an initialized edit and Undo; zero mutations. |

No display-only pose transformation overwrites stored model coordinates. Optional
context and highlight evidence fields preserve old v1/v2 data compatibility.
Missing physical identity is never repaired by calling a tracker ID a name.

## Frontend data contracts

| Input / consumer | Contract |
|---|---|
| `session.media` → video overlay/editor | Width/height are analysis pixels; `fps_num/fps_den` define canonical frame timeline. Browser intrinsic width/height describe presentation geometry and may differ with SAR. |
| Columnar track window → TrackBuffer | Parallel f/t/b/k/court columns; optional source `pf`, episode `obs`, context `ctx` remain evidence, not fabricated defaults. Optional columns are validated before mutation. |
| TrackBuffer → canvas | Current detections/poses and display-only holds remain distinguishable. Held poses require stamped source and compatible episode/context. Unresolved IDs do not connect into identity motion. |
| Events → rally/evidence controls | Event identity is passed through navigation; candidate ordinal is a list label, not an official rally number. Event frame is divided by canonical FPS for playback. |
| Session meta → quality panel | Saved capability status/reason and degradation entries are shown conservatively. Loaded means reported availability, not measured accuracy or proof of GPU node placement. |
| Heatmap response → court grid | Movement total is metres; other totals are sample counts. Normalized cell intensity is distinct from total quantity. |
| Highlights → ranking | Optional evidence IDs/status/score semantics are preserved. Legacy absence is unknown; no calibrated probability is invented. |
| Derived analysis queries → server | Shared live refresh is bounded to 2 s; terminal updates/corrections are prompt; queued dirty work is retained and old revisions remain isolated. Raw events/overlays keep their immediate path. |
| Explicit highlight session → overview collection | Exact identifier must exist in loaded collection; unavailable/truncated data cannot authorize substitution. |

## Models and backend boundary

The frontend does not initialize ML models. The actual WebSocket/REST path
consumes backend media, tracks, calibration, events and analytics. Run03 metadata
reports TrackNet, RF-DETR, RTMPose and OCR loaded, racket geometric, stroke and
identity heuristic, named identity review required, optional OSNet unavailable.
Run04/run06 subsequently report appearance matching loaded after the integration
owner supplied the existing pinned OSNet asset. Named identity remains review
required. These are backend-reported states, not frontend assertions that inference is
correct or every graph node executes on a particular provider. The integration
owner audits actual model invocation and device execution separately.

## Tests and builds

Commands run in `Sports_Analytics/apps/web`, after `source ../../../gpu-env.sh`:

```sh
pnpm typecheck
pnpm test
pnpm exec biome check --write <changed-source-and-test-files>
pnpm build
```

Baseline: 226 tests/46 files. Provenance fixes:230/46. SAR, calibration border and
candidate labels:239/47. Run04:253/51. Final source: **264 tests/52 files pass**,
TypeScript passes, production build passes in 6.57 s. Build time is not an inference or UI
rendering improvement claim. No unit/build command ran during a selected-video
inference. Biome changed-file checks pass; existing `BaiEvent.payload:any` remains
a warning. Existing unrelated React act warnings remain in suite output; newly
added heatmap teardown uses act.

Final run05/run06 build index SHA256:
`ac1d861c1b13d18727c2339e2b11ee696d6db8dac5956a331c12f6b387e0f946`.
Run04 index SHA256: `ee1d35e021239b3f184a563e0cff149d090edc460721223f2fe4d28059136a78`.
Generated dist assets are ignored, not committed. Exact outputs are retained in
`unit-run05-final.log` and `build-run05-final.log`; earlier run04 logs remain.
Eight new scheduler cases cover duplicate/late observers, bursts, inherited and
ordinary in-flight dirty work, completion with/without cached data, revision
reset, corrections and cleanup. Existing EvidenceDetails tests were restored
alongside the new candidate-identity case before final checks; no prior coverage
was discarded. Preparation failures remain in focused/candidate logs (obsolete
cancellation expectation, a test selecting the icon SVG, and a test typing error). An initial SAR regression used
overstrict floating equality and was corrected to10-decimal tolerance; the
original failed output remains in `unit-sar-candidate.log`.

## Selected source and actual browser runs

Only source:
`data/media/06a5cb888e58c64421114fecc582f60b85466900efec6db0bbf99420f4f6c010/source.mp4`.
The integration owner locked this148.736-second amateur doubles recording,
approximately15 visible exchanges including partial ends. Independent complete
human sporting annotations are unavailable. Canonical timeline:4462 frames at
30fps. Browser duration148.733333seconds agrees with that timeline.

Real base: `http://127.0.0.1:8011`; each iteration uses isolated backend data and
the real production SPA. Upload path: `/library` → actual file input → Doubles →
blank name inputs → Analyse video. No API-only substitute, mocked backend,
hardcoded success result or fixture e2e server was used.

| Iteration | Real session | Frontend evidence |
|---|---|---|
| run01 | `01M7A8NAGTXH3J7HXEAW17WH96` | Upload response1281.8ms; live12sec view shows four boxes/poses, frame360, unassigned identity/unknown score. All seven completed tabs and five timestamps captured. Found SAR mismatch and Rally0. |
| run02 | `01M7A9S1B8M5GFKJPCQV6Z0TJG` | Raw762/presentation763 mapping inspected. Canvas scales match computed x=.779527545 and y=.778505921 within Float32 precision. Next-frame control12.000→12.050sec / frame361; pose layer toggles. All seven tabs/APIs inspected. |
| run03 | `01M7AB2DGRBX8JAKNNZ0QS3Q36` | All seven tabs, times12/32/62/92/122sec, canonical event cue and exact unsaved pointer mapping. Three ambiguous rally candidates and14 unknown stroke events reported by backend; no official rally/score correctness implied. |
| run04 | `01M7ACDPXGXM4YNQ866CF2FEGJ` | Source `ac0084f`; full live browser completed in773.924 s; ten tabs/nine timestamps; actual quality, negative observations, selector guard and editor inspected. Revealed request storm and initialization race. |
| run05 | `01M7AE8EGHF561F9WWWXC1NKFW` | Source `8110422`; interrupted at observed frontier4019/4020 processed. ECONNREFUSED at595 s; no completion claim or inferred final metrics. |
| run06 | `01M7AEZC82KAE6B152D6TWYJTB` | Source `8110422`; detached full browser completed in648.574 s; ten tabs/eleven timestamps, terminal refresh, exact-event navigation, real quality/selection and initialized editor checks pass. |

Completed captures run01/02/03 have no page/console/request/WebSocket errors; five
saved final API responses per run are200 (analytics, individual, estimated
individual, highlights, events). No named physical identity or eligible highlight
was manufactured to fill empty states. Rallies/events can be viewed despite
unsupported official counts. Player labels can crowd behind the score overlay;
this remains a minor readability limitation.

Representative run03 interaction: first candidate Watch navigates event frame472
and source15.75seconds (30fps), the centre of canonical frame472. Next-frame
control similarly seeks frame361 at12.050 s; the displayed canonical frame clock
is based on frame361/30. Navigation deliberately seeks the frame centre. Calibration SVG raw viewbox762×720 covers820×773.671875 presented pixels,
inside822×776.6875 outer container. Click/drag/Undo produced the exact expected
raw coordinates, with **zero POST/PUT/DELETE** and no saved calibration.

Single API latency samples (ms; no percentile or equivalence claim):

| Run | Analytics | Individual | Estimated individual | Highlights | Events |
|---|---:|---:|---:|---:|---:|
| run01 |17.2|40.3|154.1|12.7|75.7|
| run02 |16.2|36.0|145.3|10.9|71.6|
| run03 |1742.0|116.0|213.1|10.7|75.5|
| run04 |17.4|41.5|157.2|10.6|69.1|
| run06 |33.2|41.2|157.6|11.4|72.6|

The run03 analytics outlier was reported to the integration owner; its capture
near completion does not establish a frontend regression or explain server
contention. Backend trace/resource comparisons are owned by the main report.

## Harness limitations, preserved transparently

Pinned Playwright initially lacked a browser; runtime package instructions were
read before `pnpm exec playwright install chromium`. Bundled Chromium156.0.8078.4
was installed outside the repository; no manifest/lock dependency changed.

The first selector attempt failed **before** upload, so created no session. The
first long headless-shell watcher lost its browser after about32seconds; backend
processing continued and no second upload was issued. No OOM cause was confirmed.
Two sprite-metadata404s during generation later became200. Full bundled Chromium
via `executablePath:chromium.executablePath()` subsequently completed captures.

The first run02 interaction reader inspected the first SVG point rather than
the selected near-left point. That harness limitation is preserved in its report;
run03 records all SVG groups and verifies the nearest target, rather than
silently overwriting evidence. Scripts archive/hash themselves in later run
folders. HAR omits response body content; selected API payloads are separately
saved for source comparison.

## Measured live request repair and final freshness

The sustained run04 browser observed 3,666 page-issued API responses, including
1,368 analytics and 2,189 heatmap calls. The source-confirmed cause was repeated
per-observer invalidation for the same version/key. Run06, with the same video,
profile/models and browser workflow, observed **551** page-issued responses:
**153 analytics** (88.8% fewer) and **302 heatmaps** (86.2% fewer). These counts
exclude the diagnostic observer's separate status polling. They include normal
page media/API traffic. Raw reports and the archived harnesses remain available.

Browser upload-click-to-terminal duration was 773.924 s in run04 and 648.574 s
in run06, a 125.350 s / 16.2% aggregate reduction. The backend owner separately
measured engine analysis 771.019 → 645.284 s. Frontend refresh and backend
fold/read optimizations changed together, so this is not a frontend-only causal
speedup. All cached inference-frame fields match run04 according to the
integration audit; preserving eight early image rows is a separate intentional
output repair, not reduced sampling or skipped inference.

Run06 page HTTP durations, request start to body finish, nearest-rank quantiles:

| Endpoint | n | p50 ms | p95 ms | max ms |
|---|---:|---:|---:|---:|
| analytics |153|33.5|205.0|400.4|
| heatmap |302|34.9|195.7|451.5|
| individual analytics |43|33.3|419.1|848.7|
| estimated individual analytics |22|107.4|382.0|461.5|

These are local observations during one processing run, not a service guarantee;
small-n distributions are especially preliminary. Run04 did not record comparable
per-request body-finish duration rows, so no before/after HTTP percentile claim
is made. Source/model inference timing is measured separately by the backend.

Actual terminal freshness is demonstrated: WebSocket analysed status arrived at
648158.946 ms from upload click; new analytics/P1-presence/P2-presence requests
started at648163 ms and completed200 in20.9/24.4/26.3 ms. The final-refresh path
therefore did not leave an earlier in-flight snapshot as the final result.
First observed playable media was4.952 s, nonbacklog events30.217 s and nonempty
track window38.224 s; these names describe observed messages, not correct sports
facts. No faster cold-start claim is made.

## Final visual, identity and loading checks

Final run06 captures all ten actual tabs: overview, rallies, shots, tactics,
court, movement, head-to-head, pair, moments and Ask. Source samples are0,
0.05 (canonical frame1),12,14,17.37,18,19.97,32,62,92 and122 s. The browser
shows real backend results and unknown/empty states. No named shots, winners,
physical identities or eligible highlights were supplied to make them look full.

Frame0 now renders all four image boxes/current poses while the court remains
unusable; court-coordinate analytics remain unavailable. Frame420 displays the
actual unresolved raw8/canonical-10 observation. At frame421, two separate raw
observations (raw8/-10 and raw3/-5) both render independently as Unresolved
observation. The exported run contains at most four unresolved observations in a
frame; their labels are not four reviewed athletes. Pose holds/movement for
unresolved canonical identities are rejected. Screenshots with the Score layer
hidden retain the same actual labels for unobstructed inspection.

Candidate1 Watch seeks source frame472 at15.750 s. Keyboard L dispatches exact
Candidate2 event `01M7AFB5G37J4K8YQBSAREG3AQ`, frame1858/end1944. After waiting
for the **presented** frame, controls/video61.950 s and Now showing both agree on
Candidate2. The first400 ms screenshot still showed the old presented frame
while the target seek was loading; that capture remains preserved rather than
being mistaken for a final synchronized frame. No lookup by rally_no=0 occurs.
At17.37 s the selected event context says Candidate1/Not counted/Winner unresolved.

The real quality panel shows recorded provider availability, heuristic/unsupported
stages and review-required named identity. Missing recording selection stays
`unavailable-validation-id`, displays its error and fetches no other recording's
insights; selecting the actual session loads its real collection.

Normal calibration click190.5,288 and drag228.6,324 have zero raw-pixel error;
Undo restores the click. A focused real-browser check uses CDP to add750 ms
network latency until the actual proposal response arrives, without substituting
payloads. The pending click changes no points. Once initialized, an edit is
accepted and Undo remains enabled. Both checks make **zero mutations** and never
save a calibration. This delayed-transport check is excluded from latency metrics.

## Interruption and retained browser diagnostics

Run05 was interrupted after the last REST observation592.862 s /4020 processed
frames. At595.235 s its reconnect was refused; the user turn abort had stopped
the attached backend. The report finalized at12:41:23.910 UTC with ECONNREFUSED,
502 page responses and no final session/completion timestamp. Those artifacts
remain partial. Run06 starts fresh on the same frozen source, with detached
service/browser PID/log receipts, and is the complete comparison.

Run06's sustained live browser has no page/request/socket/decode failure; two
sprite-metadata404 console entries recovered to200. Post-run repeated document
navigation captures retain **56 net::ERR_ABORTED** fetch records:22 analytics,
31 heatmaps,2 insights,1 highlights. There is no HTTP error response or page
exception. HAR timing places53 within1 s of document initialization; three end
2.6–3.6 s later. AbortSignal unmount and coordinator snapshot-supersession paths
are source-confirmed; the exact individual trigger of those latter three was
not traced. They are consistent with cancelled derived queries, not evidence of
an application crash, and remain visible in
`run06-final/cancellation-classification.json` rather than being filtered out.
All five final explicit API payload fetches returned200.

Run04's original qualification attempt used an overly exact Recording-label
selector and failed after correctly showing the missing-ID error; its retry
uses the actual combobox and passes. Its original editor attempt clicked during
the real proposal spinner, exposing the initialization/history defect fixed
before run06; its post-ready retry passes. All original failed artifacts are
retained alongside subsequent successful checks.

## Artifacts and reproduction

External root:
`/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/frontend/`.

- `run01/`: failed pre-upload selector; `run01-upload2/`: actual upload and initial
  watcher failure/live snapshot; `run01-final/`: completed tabs/APIs/HAR/trace.
- `run02-upload/`, `run02-live/`, `run02-final/`, `run02-interactions/`: actual
  upload, coordinate/frame/layer checks, completed outputs and unsaved editor.
- `run03-upload/`, `run03-final/`, `run03-interactions/`: actual upload,
  all-tab/timestamp payloads and exact unsaved geometry checks.
- `run04-live/`, `run04-final/`, `run04-coordinate/`, `run04-interactions-retry/`,
  `run04-qualifications-retry/`: complete baseline, actual source metadata and
  known loading-race/selector failures preserved in the original folders.
- `run05-live/`: interrupted prefix, error/PID/log/source-harness receipts; no final session.
- `run06-live/`, `run06-final/`, `run06-coordinate/`,
  `run06-interactions-presented/`, `run06-qualifications/`,
  `run06-qualifications-groups/`, `run06-calibration-loading/`: final complete
  browser and focused evidence. `request-comparison-run04-run06.json` records
  measured counts, durations and terminal-request timing.
- `check-output-qualifications.mjs` checks actual metadata/negative identities and
  explicit missing-recording selection. `check-calibration-loading.mjs` delays
  actual transport through CDP; it replaces no response content and never saves.
- `validate-real-workflow.mjs`: locked-source upload or read-only completed
  inspection; `check-live-coordinate-ui.mjs`: canvas/layer/frame checks;
  `check-interactions.mjs`: evidence/editor/quality checks without Save.
- `watch-live-workflow.mjs`: locked-source **single** normal upload, full Chromium
  alive through completion; compact decoded WebSocket summaries, periodic real
  screenshots, API progress and first playable/track/event observations measured
  from browser upload click. Compact request start/status/body-finish/failure rows
  support HTTP distributions; tensors and full image payloads are not logged.
  Run06 uses a detached process with explicit watcher PID/log receipts.

For an already-running isolated backend containing the selected session:

```sh
source ../gpu-env.sh
node /home/administrator/Desktop/sport-analytics/single-video-validation-20261113/frontend/validate-real-workflow.mjs \
  http://127.0.0.1:8011 NEW_EXTERNAL_OUTPUT_DIRECTORY inspect SESSION_ID
node /home/administrator/Desktop/sport-analytics/single-video-validation-20261113/frontend/check-interactions.mjs \
  http://127.0.0.1:8011 SESSION_ID NEW_EXTERNAL_INTERACTION_DIRECTORY
```

A new upload is a new controlled processing iteration and must be coordinated
with the integration owner, using only the locked source. Scripts neither start
backend services nor choose another video.

## Changed-file ownership

Production: `lib/tracks.ts`, new `lib/videoCoordinates.ts`, new `lib/analysisRefresh.ts`,
`lib/api.ts`, `lib/format.ts`, `features/analytics/useInsights.ts`,
`lib/reviewedIdentity.ts`, `lib/types.ts`, `features/player/overlay.ts`,
`features/player/VideoStage.tsx`, `features/calibrate/CalibratePage.tsx`,
`features/court/CourtMinimap.tsx`, `features/library/LibraryPage.tsx`,
`features/session/SessionPage.tsx`, new`features/session/RecordingQuality.tsx`,
`features/session/tabs/{RalliesTab,HeatmapsTab,HighlightsTab,StatsTab}.tsx`,
`features/session/LiveFeed.tsx`, `features/player/{clip.ts,EvidenceDetails.tsx}`,
`features/highlights/{useCollection.ts,HighlightsPage.tsx}`.

Regression files: `lib/{buffers,poseProvenance,reviewedIdentity,videoCoordinates}.test.ts`,
`lib/{analysisQuery,analysisRefresh}.test.tsx`,
`features/player/{clip.test.ts,EvidenceDetails.test.tsx}`,
`features/player/overlay.test.ts`,
`features/calibrate/CalibratePage.mutation-ordering.test.tsx`,
`features/session/RecordingQuality.test.tsx`,
`features/session/tabs/{RalliesTab,HeatmapsTab,HighlightsTab}.test.tsx`,
`features/highlights/useCollection.test.tsx`.
No frontend file is concurrently owned by another agent. No commits were created
by this workstream; integration/commit receipts belong to the orchestrator.

## Acceptance boundaries

Validated: synthetic frontend contracts/build; real uploads, complete live
WebSocket workflow, all ten final session tabs, playback/timeline/frame controls,
SAR mapping, named-identity uncertainty, real capability/degradation metadata,
explicit stale-selection protection, negative-observation rendering, exact-event
candidate navigation, layer toggles, unsaved pointer/drag/Undo and initialization
guards. Derived-request cadence and actual terminal freshness are measured.

Partially validated: player/pose/shuttle rendering (selected visual samples and
source contracts, not exhaustive physical adjudication). The selected run retains
false/ambiguous perceptions and only two uncounted rally candidates/ten unknown
shot events; rendering them accurately does not establish sporting recall.

Not exercised: positive named physical-player movement heatmaps, positive eligible
highlights, reviewed scoring, OCR scoreboard recognition, generated Ask answers,
or frontend exports of a verified point. Ask's actual interface/provider state
was loaded only. API/persistence/export validation owned by the integration report
must be consulted separately. These gaps are not passed by synthetic tests.
