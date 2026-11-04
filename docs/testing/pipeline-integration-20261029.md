# Pipeline transport and UI validation — 29 October 2026

This document records integration evidence from the local Linux / RTX 4000 Ada
runtime. It does not turn observation counts, working endpoints or test passes
into labelled tracking, pose or shot accuracy.

## Reproduced missing-pose failure

The original session `01M62Y12THWAV746H1H8PXWGVX` contained 120 player rows in
frames 10200–10259, with valid 17-joint poses and temporary track IDs 32 and 34.
Their `player_id` was null because durable identity had not been established.
The old wire encoder required a truthy `player_id`, so the same range was
returned as `players: {}`. The frontend only considered P1 and P2. Pose inference
was present on disk but could not reach the overlay.

The additive v1 wire field `anonymous` now carries those observations, keyed by
observation episode and temporary track. It carries confidence, detector evidence,
identity method, bounding box and pose alongside the existing named-player path.
Four anonymous doubles tracks can be transported simultaneously. Neither the API
nor the display turns those temporary IDs into durable participant identities.
Malformed poses are padded as a missing frame rather than shifting all subsequent
flat-array keypoints.

After rebuilding and restarting the app, the same real window returned:

| Item | Persisted data / repaired response |
| --- | --- |
| Named player rows | 0 |
| Anonymous player rows | 120 |
| Anonymous tracks | 2 |
| Pose values | 6,120 = 120 × 17 × 3 |
| Shuttle observations | 36 |
| Analysis revision header | 0 |

The browser also displayed the recorded anonymous boxes and skeletons at frame
10200. This proves that recorded observations survive transport and rendering;
it does not prove the keypoints are anatomically accurate. A four-row real-data
fixture from frames 10200–10201 is retained in
`engine/tests/fixtures/anonymous_real_tracks.json` for regression coverage.

## Data flow and uncertainty

Canonical video frames, stored player boxes, pose coordinates and shuttle
coordinates use the same proxy image dimensions. The video overlay uses the
video's intrinsic dimensions and its contained display rectangle. The minimap
uses court coordinates associated with that frame's calibration. Camera changes
break shuttle trails and movement histories.

Anonymous overlays say identity is unassigned. Tracker-only boxes are visually
qualified as estimates. All visible player observations can reach the overlay and
minimap, including four-player views. Pose visibility is independent of the box
toggle. Hiding overlays also hides contact flashes. Shuttle confidence is retained,
and low-confidence observations have a distinct style; this pipeline does not
invent an occluded or out-of-frame state that the model did not produce.

Between scheduled pose samples, the display may hold a pose for at most five
frames and map it onto the current box. A dashed pose and estimate label distinguish
this from a current inference result. This requires a current body box, the same
track and observation episode on every intervening frame, camera/view continuity
and bounded box changes. Missing bodies, cuts and new episodes break the hold.
Stored keypoints and downstream movement/event calculations are not filled in.

Estimated hits and heuristic shot labels are described as estimates. Human review
is represented separately. Unscored exchanges are described as having unconfirmed
match status rather than being asserted to be warm-ups.

## Reanalysis, paging and evidence lineage

An analysis revision is persisted and transmitted with state, events, tracks and
progress. A reset clears frontend event/track buffers, cursors, calibration and
derived analytics. Late responses from an old socket, session or revision are
ignored. Reconnection includes the known revision and receives fresh state when
that revision has changed.

The WebSocket reads durable events in pages until caught up rather than truncating
the full backlog at a page limit. It reacquires the repository's current event store
after reset, uses a repository snapshot for synchronous reads, and checks revisions
between awaited pages. The repository lock is not held across network awaits.
Bus notifications trigger durable catch-up, so a dropped notification does not by
itself discard the event.

Status now carries the analysed frame frontier, degradation and actual model
capabilities. The UI invalidates derived analytics as relevant data changes and
shows unavailable or unsupported stages. HTTP media hydration cannot overwrite
newer live metadata.

All derived REST query keys also include the analysis revision, with existing
invalidation prefixes preserved. Old cached counts and old in-flight responses
remain associated with their original generation. The analytics view does not
carry placeholder data across revision changes. Player-review selections, watched
shot state, pending preview/seek callbacks and preview boxes reset with the
generation; even a server response that ignores cancellation cannot restore an
old preview. AI answer/history state resets too, so previous counts and citations
cannot be reused with replacement evidence.

Corrections and retractions resolve through canonical event lineage. An embedded
historical shot reference cannot resurrect a retracted event or inflate a rally's
shot count. Evidence details resolve the currently effective record.

## Reproducible checks

From the repository root in the existing local environment:

```bash
.venv/bin/python -m pytest engine/tests/test_wire_anonymous.py apps/api/tests/test_websocket_revisions.py
cd apps/web
npm test -- --run
npm run build
```

The initial integration-focused Python run passed 7 tests. The final frontend
suite passed 80 tests across 24 files, including the display pose hold and
reanalysis HTTP/review/AI races. The production TypeScript/Vite build passed.
The full backend suite is recorded in the main audit report.

The tests cover real anonymous transport, four-player transport, malformed pose
alignment, paginated catch-up, reset while a socket is connected, stale reconnect
cursors, reverse track-window rejection, stale callbacks and corrected/retracted
evidence, late REST responses, stale AI history and cancelled review previews.
The original user session was not reset for these checks; inference
evaluations use isolated session repositories under `data/audit-20261029/`.
