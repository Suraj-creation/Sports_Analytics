# Single-video frontend validation — 13 November 2026

Branch: `engineering/deep-pipeline-overhaul-20261113`; starting commit `e558fd9`.
The integration owner records final commits and backend acceptance in the main
validation report. This workstream owns `apps/web/` and this report. No historical
evaluation video was uploaded, opened or processed by this workstream. Unit
fixtures are synthetic; they are never substituted for application results.

## Status

The actual built application completed the selected-video workflow in three
iterations. Real upload, live updates, playback, all seven session tabs, evidence
navigation, layer toggles and unsaved calibration edits were exercised. Run04
adds conservative quality/evidence reporting and recording-selection protection;
its production build and 253 synthetic unit tests pass, with final browser
validation pending the integration owner's run04 startup. This document will be
updated with that run's evidence rather than treating its build as empirical proof.

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
| FE05 | Actual uncounted intervals showed `Rally0`; headline called ambiguous intervals observed rallies; candidate event counts appeared as shots | Preserve positive official numbers; use original-list ordinal Candidate1/2/etc for unofficial entries. Summary says recorded rally candidates and shot events. | Candidate labels exercised run02/03; final summary/event wording is covered by unit regressions and awaiting run04 capture. |
| FE06 | Actual Recording & quality section claimed two court-side identities and hid `meta.degraded`/`meta.capabilities` | Render recorded limitations and provider status/reasons; availability is distinguished from accuracy. Track episodes, reviewed athletes and scoring slots are explicitly separate. Missing legacy metadata remains unknown. | Three synthetic metadata tests pass; actual run03 old wording is retained as before evidence. Awaiting run04 real panel. |
| FE07 | Distance-weighted heatmap totals were rounded and labelled samples; presence described time without dwell-time weighting | Movement totals retain decimal metres and are estimates. Presence is sampled feet positions. Loading state is explicit. | Two synthetic response tests pass. Positive calibrated named-player heatmap is not exercised by the selected workflow. |
| FE08 | Session highlights omitted evidence status and ranking-score semantics; play action dropped source event ID | Preserve optional evidence fields in types; show source count/status and estimated-ranking qualification; pass canonical rally event ID to evidence navigation. Filter says scoring sides. | New/legacy synthetic highlight tests pass. Real selected runs returned no eligible highlights; positive ranking content is not empirically validated. |
| FE09 | Explicit unavailable highlight session silently fell back to first loaded recording | Explicit session selects exactly that record or shows unavailable; only empty selection defaults first. Disabled placeholder keeps browser select from displaying another record. | Two synthetic metadata records verify missing/empty/exact selection, and no wrong insights request. Actual missing-ID browser check planned run04. |
| FE10 | Negative canonical IDs could be named or joined to another unresolved observation's prior pose/motion | Negative-ID labels say Unresolved observation; prevent reviewed-name binding, pose holds and court trails for unresolved canonical identities. Preserve current raw observation displays. | Synthetic distinct -1 wire groups, pose/motion rejection, review rejection and label tests pass. Backend independently fixes wire grouping by raw/context; final integrated behavior awaiting run04. |
| FE11 | Upload helper claimed unspecified format always means singles | Explain sustained court-observation inference and identity/scoring review. | Real library screenshot inspected. |

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
| Explicit highlight session → overview collection | Exact identifier must exist in loaded collection; unavailable/truncated data cannot authorize substitution. |

## Models and backend boundary

The frontend does not initialize ML models. The actual WebSocket/REST path
consumes backend media, tracks, calibration, events and analytics. Run03 metadata
reports TrackNet, RF-DETR, RTMPose and OCR loaded, racket geometric, stroke and
identity heuristic, named identity review required, optional OSNet unavailable.
These are backend-reported states, not frontend assertions that inference is
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
candidate labels:239/47. Run04 candidate: **253 tests/51 files pass**, TypeScript
passes, production build passes6.85seconds. Build time is not an inference or UI
rendering improvement claim. No unit/build command ran during a selected-video
inference. Biome changed-file checks pass; existing `BaiEvent.payload:any` remains
a warning. Existing unrelated React act warnings remain in suite output; newly
added heatmap teardown uses act.

Final run04 build index SHA256:
`ee1d35e021239b3f184a563e0cff149d090edc460721223f2fe4d28059136a78`.
Generated dist assets are ignored, not committed. Exact outputs are retained in
`unit-run04-final.log` and `build-run04-final.log`. An initial SAR regression used
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
| run04 | pending | Built and frozen; normal UI/live watcher prepared. |

Completed captures run01/02/03 have no page/console/request/WebSocket errors; five
saved final API responses per run are200 (analytics, individual, estimated
individual, highlights, events). No named physical identity or eligible highlight
was manufactured to fill empty states. Rallies/events can be viewed despite
unsupported official counts. Player labels can crowd behind the score overlay;
this remains a minor readability limitation.

Representative run03 interaction: first candidate Watch navigates event frame472
and source15.75seconds (30fps). The maximum floor-frame offset is less than one
canonical frame; clip navigation intentionally uses its existing small seek
margin. Calibration SVG raw viewbox762×720 covers820×773.671875 presented pixels,
inside822×776.6875 outer container. Click/drag/Undo produced the exact expected
raw coordinates, with **zero POST/PUT/DELETE** and no saved calibration.

Single API latency samples (ms; no percentile or equivalence claim):

| Run | Analytics | Individual | Estimated individual | Highlights | Events |
|---|---:|---:|---:|---:|---:|
| run01 |17.2|40.3|154.1|12.7|75.7|
| run02 |16.2|36.0|145.3|10.9|71.6|
| run03 |1742.0|116.0|213.1|10.7|75.5|

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

## Artifacts and reproduction

External root:
`/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/frontend/`.

- `run01/`: failed pre-upload selector; `run01-upload2/`: actual upload and initial
  watcher failure/live snapshot; `run01-final/`: completed tabs/APIs/HAR/trace.
- `run02-upload/`, `run02-live/`, `run02-final/`, `run02-interactions/`: actual
  upload, coordinate/frame/layer checks, completed outputs and unsaved editor.
- `run03-upload/`, `run03-final/`, `run03-interactions/`: actual upload,
  all-tab/timestamp payloads and exact unsaved geometry checks.
- `validate-real-workflow.mjs`: locked-source upload or read-only completed
  inspection; `check-live-coordinate-ui.mjs`: canvas/layer/frame checks;
  `check-interactions.mjs`: evidence/editor/quality checks without Save.
- `watch-live-workflow.mjs`: locked-source **single** normal upload, full Chromium
  alive through completion; compact decoded WebSocket summaries, periodic real
  screenshots, API progress and first playable/track/event observations measured
  from browser upload click. Tensor/image payloads are not logged.

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

Production: `lib/tracks.ts`, new`lib/videoCoordinates.ts`,
`lib/reviewedIdentity.ts`, `lib/types.ts`, `features/player/overlay.ts`,
`features/player/VideoStage.tsx`, `features/calibrate/CalibratePage.tsx`,
`features/court/CourtMinimap.tsx`, `features/library/LibraryPage.tsx`,
`features/session/SessionPage.tsx`, new`features/session/RecordingQuality.tsx`,
`features/session/tabs/{RalliesTab,HeatmapsTab,HighlightsTab}.tsx`,
`features/highlights/{useCollection.ts,HighlightsPage.tsx}`.

Regression files: `lib/{buffers,poseProvenance,reviewedIdentity,videoCoordinates}.test.ts`,
`features/player/overlay.test.ts`,
`features/calibrate/CalibratePage.mutation-ordering.test.tsx`,
`features/session/RecordingQuality.test.tsx`,
`features/session/tabs/{RalliesTab,HeatmapsTab,HighlightsTab}.test.tsx`,
`features/highlights/useCollection.test.tsx`.
No frontend file is concurrently owned by another agent. No commits were created
by this workstream; integration/commit receipts belong to the orchestrator.

## Acceptance boundaries

Validated: synthetic frontend contracts/build; real uploads, playback, live
updates, completed session tabs, SAR coordinate transforms, frame controls,
evidence navigation, layer toggles and unsaved calibration pointer/Undo.
Partially validated: player/pose/shuttle rendering (visual samples, not full
adjudication); unknown/empty analytics states. Pending run04: new actual quality
panel, unresolved-group integration, updated candidate summary and stale-session
browser guard. Not exercised: positive named physical-player movement heatmaps,
positive eligible highlights, reviewed scoring or exports of a validated point.
Those gaps must not be reported as passed or inferred from synthetic tests.
