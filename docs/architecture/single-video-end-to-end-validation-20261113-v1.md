# Single-video pipeline engineering and empirical validation — 13 November 2026

## 1. Executive status

This work follows the static overhaul, preserves its evidence, and executes the
actual built web application, API, embedded engine and configured perception on
one locked amateur doubles recording. Source improvements are committed on
`engineering/deep-pipeline-overhaul-20261113` as `ac0084f` and `8110422`.

**Application execution and sports accuracy are separate acceptance decisions.**
Five complete runs (01–04 and06) process all 4,462 canonical frames and persist
real results; run05 is preserved as interrupted. The final live workflow takes
648.574s versus773.924s before its last repairs, with identical cached frame
outputs and all eight previously dropped uncalibrated image observations retained.
It still produces only two unofficial rally candidates and ten unknown stroke
events against approximately15 visually drafted exchanges, with no accepted
official points. These counts are not precision/recall or independent ground
truth. **The branch contains tested engineering improvements; automatic sports
accuracy does not meet production acceptance. No production-readiness sign-off,
push or main-branch merge is claimed.**

Run04 exercised the committed source, the repaired browser contracts, structured
cancellation evidence, and the previously configured but unavailable OSNet
appearance model. It also exposed live-query amplification. `8110422` repairs
that measured mechanism and preserves early image observations. Run05 was
interrupted; the fresh run06 comparison and final acceptance decisions are recorded
in the closing supplement below. No experimental model is promoted into a
new default production profile by this work.

## 2. Git, preservation and ownership

The starting tree was clean at `e558fd9`; `1313370` and the preceding evaluation
history are ancestors. The existing branch was retained. No reset, clean,
worktree replacement, historical-artifact deletion, push or merge was performed.
The existing service on8010 and unrelated processes/tunnel were preserved. Our
isolated application uses127.0.0.1:8011 without a tunnel.

| Owner | Production ownership | Other responsibility |
|---|---|---|
| Root/integration | Generic tracing, runner/config/metrics, API bundle startup, wire, shared engine, content decisions/validation, component versions, appearance runtime metadata | Dataset lock, all neural runs, API/resource capture, integration and this report |
| Perception agent | Player/TrackNet contract fixes and spans; scene-change geometry cache/grouped LK | Synthetic perception checks, selected saved-output visual diagnosis, read-only final review |
| Contracts agent | Rally parameter validation, cancellation interval and short-exchange diagnostic fields | Synthetic evidence fixture repair, guarded curated regression and issue register |
| Frontend agent | `apps/web/` source/tests | Built UI, real Chromium upload/playback/interaction/WS evidence |

Edits were coordinated by file. Source/build freezes separated measured runs;
tests/builds did not execute during the measured neural iterations. Reports may
be updated while a run executes; imported production code remains frozen.
Runs01–03 identify dirty `e558fd9` source through exact file hashes, patches and
byte archives. Run04 identifies committed `ac0084f` and archives the built SPA.
The final documentation commit records the completed experiment separately.

## 3. Evidence and specifications inspected

The expected `research/evaluation/benchmark/` and `evaluation/evaluation/` paths
remain absent. Actual discovery covered the following retained evidence:

- `research/SEQUENTIAL_BENCHMARK_INDEX.md`,
  `CONSOLIDATED_SEQUENTIAL_BENCHMARK_REPORT.md`,
  `CURRENT_BADMINTON_PIPELINE_TECHNICAL_REPORT.md`,
  `PRODUCTION_COMPONENT_INVENTORY.md`, and `research/test_video_benchmarks/`.
- `evaluation/ground_truth_validation/reports/`, component evaluations,
  per-test diagnostics/failure cases, orchestration specifications and retained
  artifact indexes. Historical Tests1,2,3,4,6,7,9,10 supply diagnosis only.
- The class-context diagnosis under
  `component_evaluations/pre_test03_class_context_v1/`, event/score integrity,
  continuity/identity specifications and source-bound failure examples.
- [Deep overhaul](deep-pipeline-overhaul-20261113.md) and its linked
  [perception](overhaul-perception-20261113.md),
  [tracking](overhaul-tracking-20261113.md),
  [events](overhaul-events-20261113.md) reports; actual modified implementations.
- Root `AGENTS.md`, `CLAUDE.md`, `CODEX.md`; `config/profiles/`,
  `models/manifest.yaml`, model cache pins, component declarations, APIs/wire,
  event/track persistence, frontend playback/buffers and existing tests.

Historical interval tables are generated/legacy references, not physical contact,
stroke, person or winner truth. Historical agreement metrics are not recomputed
or transferred to this experiment. Source-confirmed defects, observed selected
video behavior, synthetic contract checks and hypotheses are labelled separately.

## 4. Residual-issues register and diagnosis-to-fix map

The machine-readable register is
[single-video-residual-issues-20261113.json](single-video-residual-issues-20261113.json).
It records severity, evidence kind/path, dependencies, confirmed/hypothesized cause,
required improvement, actual change, validation method and remaining limitation.

| Issue / evidence | Confirmed mechanism | Actual change | Demonstration / limit |
|---|---|---|---|
| SV-024: unexecuted temporal overhaul | Carry rows, missing source stamps and weak endpoints must not become fresh observations | Focused positive/negative contracts and truthful synthetic fixtures; retained strict production gates | Curated tests pass; real physical accuracy remains separate |
| SV-019: missing stage attribution | Aggregate perception timing obscured detector/pose/CPU work | Opt-in bounded per-session JSONL spans, exact frame scopes, model/runtime summaries and parent IDs | Real trace files for every run; host-wall timing, no all-node GPU claim |
| SV-018: CPU pool contention | OpenCV default pool was36 threads; nested native work consumed many CPU cores | Validated `BAI_OPENCV_THREADS`, default1, set before workers/recovery | Run01→02 identical frame payloads; aligned CPU samples944.84→347.98%; analysis629.07→624.07s is not a meaningful latency claim |
| SV-002: false reset at369/12.30s | Duplicate/current detector proposals made witness matching ambiguous; unknown decision fell through to a positive raw barrier despite every old witness retaining overlap | Abstain from reset for source-bound ambiguous layouts with supported witnesses; retain unknown identity, empty match claims and validation against raw geometry | Exact saved369 fixture plus synthetic disjoint/forged controls; run03 epoch0 all 4,462 frames, player continuity preserved across369 |
| SV-018: repeated scene CPU work | Same geometry rebuilt raster proof records; repeated independent LK calls; validation repeated encoder/decoder gates | Geometry-only immutable bounded cache; independent feature sampling with batched forward/backward LK; one complete boundary validation |51 dedicated and230 curated scene checks; unchanged frame payloads0–359; source-prefix content validation5.765→1.433s |
| SV-006: ndarray pose input | Boolean test of a multi-person NumPy array raises ambiguous-truth-value | Length-based empty check, per-person crop/order/missing-output controls | Synthetic regression; default observed caller supplied lists |
| SV-020: SAR/display mismatch | Raw762×720 analysis coordinates were scaled against browser763×720 natural display dimensions | Shared raw-analysis/display containment transform and inverse court pointer mapping using actual SVG rectangle | Real click190.5,288; drag228.6,324; Undo restores original; no calibration saved |
| SV-020: stale frontend evidence | Context/source columns were ignored; old pose could appear current or cross an epoch | Preserve `ctx`/`pf`; atomic optional-column validation; restrict pose holds/trails and unresolved ownership | Frontend regression and actual frame/playback/layer checks |
| SV-014: canceled rally evidence lost | Retraction preserved only original start and generic note, discarding rejected interval/end reason/admission proof | Optional `cancelled_segment`; interval-matched copied admission on retraction, track-window and original-event references | Synthetic gap/cut/flush/legacy/old-cancel+new-start/store cases; runs04/06 preserve all 50 rejected intervals and proof |
| SV-004: configured ReID skipped | Correct existing adapter could not find its pinned local checkpoint | Fetch the existing1,001,683-byte registered checkpoint; report actual parameter placement/dtype and appearance execution shapes/counts | SHA verified before load; runs04/06 demonstrate actual invocation/consumption; no identity accuracy inferred from loading |
| SV-005: unresolved player loss | A generic/preview producer returning multiple IDs−1 shares anonymous key `track:-1`; browser Maps overwrite duplicate frame rows | Separate display series by context/raw observation and occurrence; per-frame fallback without raw ID; no new identity | Wire tests preserve four unresolved bodies; the active badminton path already used distinct negative display IDs, so no recovered-box count is claimed |
| SV-026: incomplete web build crashes API | Existing dist root without assets directory made StaticFiles construction fail | Mount only complete index+assets bundle; explicit API-only warning; launcher checks assets directory | Five synthetic layout cases and complete built app startup |
| SV-021: misleading output/UI claims | Two scoring slots called two identities; capabilities hidden; presence samples/distance metres conflated; unknown recording selected first available | Actual quality/capability panel; candidate/event wording, units/evidence qualification, explicit unavailable selection |253 frontend checks; final real-browser display |
| SV-013: fragmented shuttle/rally coverage | Long raw observation gaps terminate short candidates; conservative witness policy cannot establish a physical opposing exchange from same-episode cues | Preserve missing/unknown, diagnose exact rejected intervals; do not lower duration/contact thresholds to fit draft count | Runs01–03 demonstrate unresolved coverage; specialized perception and independent labels remain necessary |
| SV-003: spectator/athlete handover | Court-origin image overlap can continue outside court and raw tracker ownership can change | Existing appearance-assisted path now exercised; unresolved observations cannot acquire named/held movement facts | Run04/06 audit splits the particular handover; physical identity still fragments |
| SV-027: live request amplification | Multiple widgets invalidate the same derived query on each event/frontier update; repeated snapshot reads block the writer | Shared per-client/session refresh owner, bounded live cadence, preserved completion/revision/correction freshness and request cancellation | Run04 records3,666 API requests; focused timer/ownership controls and complete live run04→06 comparison |
| SV-028: unused spatial reads | Canonical analytics scans camera Parquet even when all rally intervals are unofficial and no spatial statistic consumes it | Skip geometry reads in empty/candidate-only folds; preserve official geometry path |34 relevant tests; six alternating saved-run04 folds have identical output and median135.08→1.32ms |
| SV-029: early image detections discarded | Anonymous track persistence depended on valid court geometry | Preserve eligible image boxes with null court positions/participant binding while calibration reacquires | Run04 lacks eight image observations at0/1;20 focused checks; run06 preserves all eight without spatial facts |
| SV-030: late court proposal erases edits | Pointer interaction accepted during initialization before a late proposal resets draft/history | Disable editing until initialization resolves; retain explicit proposal lifecycle | Real run04 loading race retained; focused regression and run06 delayed-network editor check pass |
| SV-031: residual Rally0 labels | Some evidence/clip/feed labels format a zero official number despite an unofficial candidate identity | Shared conservative candidate label with event/frame navigation retained | Source-linked run04 screenshot and synthetic identity regression; run06 actual browser reinspection passes |

## 5. Exactly one selected video

Source path:
`data/media/06a5cb888e58c64421114fecc582f60b85466900efec6db0bbf99420f4f6c010/source.mp4`.

| Property | Recorded value |
|---|---|
| SHA256 | `06a5cb888e58c64421114fecc582f60b85466900efec6db0bbf99420f4f6c010` |
| Size |102,264,648 bytes |
| Container duration |148.736s; video stream duration148.733333s |
| Selected original video stream |1; audio is stream0 |
| Original coded dimensions / FPS |1142×1078;30/1;4,462 frames |
| Analysis proxy |762×720;30/1; SAR68520:68453; DAR571:539 |
| Browser natural dimensions |763×720, reflecting display aspect |
| Camera/content | Fixed oblique amateur doubles, four active players, seated far-baseline spectators, adjacent court, near baseline cropped, no readable scoreboard |
| Approximate exchanges |15, including partial first/last; complete1Hz contact-sheet visual draft, coarse boundaries±1s |
| Ground truth | No independent exhaustive person/contact/shuttle/shot/winner labels; draft is agent visual review, not human ground truth |

Selection exposed realistic clutter, partial geometry, spectator association,
shuttle absence and four-player attribution in a short iteration. It is outside
the eight prohibited historical evaluation recordings. Selection/hash/probe and
draft intervals are preserved in the external `selection/selection.json`.

Compressed-packet timeline audit found4,462 distinct presentation timestamps in
both source and run03 proxy,0 through148.7s, every adjacent presentation step
exactly1/30s. Each executed run also preserves contiguous canonical frames0–4461.
This validates this CFR case, not arbitrary VFR or camera-edit correspondence.

## 6. Actual execution and dependency map

```text
Built Library UI → POST /api/sessions → content-addressed source + session repository
 → local bus command → EngineService → per-session SessionRunner
 → probe/validate stream → proxy/HLS/sprite preparation
 → sport plugin + component registry + pinned model adapters
 → selected-source warm-start background/court proposal
 → HLS segment decode (canonical CFR frames, BGR arrays)
 → court/camera/calibration states
 → content continuity + current detector probes + ByteTrack/player cadence
 → optional appearance/canonical association → current crop pose → racket geometry
 → TrackNet temporal windows/heatmaps/candidates → causal shuttle association
 → immutable perception cache → BadmintonMatchEngine chronological ingest
 → participant episodes / format / provisional identity
 → observed temporal shuttle/participant windows → contact candidates/evidence
 → rally FSM/admission → supported-endpoint stroke classifier
 → guarded terminal outcome/OCR/legal score transitions
 → event ledger + Arrow tracks + transactional analytics/highlights
 → REST / exports / WebSocket → browser buffers/overlays/timeline/analytics
```

`SessionRunner` stages media preparation and updates ready-to-play independently
of later analysis. Measured runs use a fresh application data directory and fresh
source staging; perception spans report `cache_reused=False`. The stateful
badminton provider processes chronologically rather than allowing seek-ahead
perception to mutate matcher state. Browser seeking reads persisted windows.
Human corrections/calibration commands are serialized between chunks; browser
editor checks deliberately left drafts unsaved, preserving comparison inputs.

## 7. Component contracts and missing evidence

| Boundary | Input → output / temporal and coordinate convention | Missing/error/provenance contract |
|---|---|---|
| Acquisition/probe | Selected original stream → validated finite metadata and source hash | Invalid dimensions/duration/FPS fail explicitly; source stream index retained |
| Decoder | Proxy segment → ordered uint8 H×W×3 BGR arrays, absolute canonical indices | Actual4,462 contiguous outputs; source↔proxy transform recorded; no dropped/duplicate canonical index |
| Court/camera | Current image/retained reference → ordered court geometry,3×3 reference→image camera transform and calibration state | VALID/REACQUIRING/invalid remain distinct; homography existence is not physical calibration truth |
| Detector/tracker | Current cropped image → xyxy analysis-pixel boxes/confidence → raw track IDs/current unique matches | Detector ran differs from person matched; carries retain renderability but cannot vote as fresh evidence |
| Appearance | Current matched in-frame boxes → ephemeral normalized N×512 float32 descriptors → canonical identity hypotheses | Pinned local checkpoint; bounded crops; no stored embeddings; unknown ownership stays−1; no raw-ID fallback after failure |
| Pose | Current person crops → per-person17×3 COCO joints + exact pose frame | Invalid crop/output preserves person position as missing; current pose on carried box has uncertain person geometry |
| Shuttle | Eight RGB frames plus background at512×288 → host float32 `[B,27,288,512]` in[0,1] → CUDA FP16 adapter → `[B,8,288,512]` heatmaps, CPU float32 reduction → raw peaks/candidates/association | Coordinates rescale to raw analysis pixels; support is uncalibrated; missing remains missing; inferred positions never become detector observations |
| Racket | Current image+pose/wrist/person → ellipse/shaft candidate with source stamp | Geometric alias remains possible; physical contact is not established by proximity |
| Contact | Same-context observed motion + fresh participant/equipment → candidate and separate impact/trajectory/actor reliability | Nonfinite/interpolated/stale/context-incompatible cues excluded; ambiguous/insufficient preserved |
| Stroke | Candidate anchor + supported next physical endpoint + calibrated fresh player context | Weak numerical next candidate is only a motion cutoff; unknown class and unknown actor remain valid outputs |
| Rally | Ordered typed observed/missing/estimated samples and admitted contacts → provisional/final/retracted intervals | Minimum/gap/lookahead/merge policy retained; cancellation now preserves rejected interval/proof |
| Score/outcome | Supported terminal observation, format, legal transition and row/identity evidence | Unknown winner/score stays unknown; cut/EOF does not establish physical end; no `None==None` winner fact |
| Movement/analytics | Fresh matched feet, same camera context/episode, ground homography → metres/sample distributions | Unsupported named identities/geometry/cadence suppress paths; four participants differ from two scoring slots |
| Storage/API/UI | Append-only event supersession + Arrow/wire windows → canonical fold/REST/WS/export/browser | Source frame/context retained; optional legacy fields remain unknown; unresolved bodies separated for display, not named |

## 8. Models: loading, invocation and consumption

| Component | Loaded / invoked / consumed evidence | Actual runtime / remaining limit |
|---|---|---|
| RF-DETR small1.4.2 | Loader/component metadata; detector spans including probes; boxes consumed by tracker/layout | ONNX CUDA priority, FP32,512×512. Provider initialization is not all-node GPU profiling; spectators/far boxes can be wrong |
| Other cached detector/pose checkpoints | RF-DETR nano/medium, YOLOX HumanArt and the larger RTMPose profile are present in the inventory but not selected/loaded/invoked in this experiment | Weight presence is not execution. The `rtmpose_x_halpe26` legacy registry alias currently points to a body7 export, not verified26-joint foot anatomy; no such anatomy is claimed |
| RTMPose-M body7 | Adapter/session + pose spans/current stamps; joints consumed by racket/contact/display | ONNX CUDA priority, FP32,192×256 crops, COCO17 decode; per-crop loop despite configured batch2 |
| TrackNetV3 | Torch checkpoint; temporal forwards and shape checks;1399/1416 observed raw outputs consumed in runs01/03 | CUDA FP16, seq8, background concat, batch4, step8; registration/candidate association remains heuristic |
| OSNet-AIN x0.25 | Runs01–03 unavailable, explicit degradation. Run04 uses existing pinned adapter, appearance spans and associator | FP32 explicit CUDA; actual parameter device/dtype recorded;512D ephemeral features; no claim of verified physical identity |
| Court/calibration | Actual OpenCV line/camera path and per-frame matrices consumed | No neural court detector; partial court and offscreen corners limit physical validation |
| ByteTrack/canonical association | Actual tracker calls; raw and optional appearance-assisted IDs consumed by participant episodes | Tracker ID, episode, physical athlete, reviewed identity and scoring slot remain separate |
| Racket geometry | Current-image ellipse/shaft/wrist outputs consumed by contact cues | CPU OpenCV, not trained racket vision; head/shoe/banner aliases observed |
| RapidOCR | Actual package-selected detection/classification/recognition stages execute; zero score readouts in earlier runs | Explicit ONNX CPU. Package reports actual PP-OCR files/hashes; profile alias is not an independently pinned PP-OCRv4 version |
| Contact/stroke/rally/outcome | Builtin configured adapters invoked; events/admission/folds consumed | Heuristic scores, conservative endpoint/terminal gates, unknown output preserved |
| InpaintNet | Cached weight presence only; not loaded/invoked/consumed in selected profile | Estimated interpolation is separate from observations |
| RacketVision ball/racket, WASB second opinion | Profile/manifest references do not establish adapter execution; capabilities explicitly unsupported | Not exercised; no silent replacement or duplicate engine added |
| BST-CG-AP | Optional singles shadow adapter exists; not loaded/invoked/consumed for this doubles run | Two-person checkpoint and separate weight-grant uncertainty; not a doubles classifier |

Official reference checks were limited and source-directed. The
[TrackNetV3 repository](https://github.com/qaz812345/TrackNetV3) and
[prediction implementation](https://github.com/qaz812345/TrackNetV3/blob/master/predict.py)
support the sequence/background and distinct rectification contract, not accuracy
on this camera. The existing
[OSNet publisher card](https://huggingface.co/LibreYOLO/LibreReID-osnet) supplies
the pinned checksum and weight provenance; the
[original code license](https://github.com/KaiyangZhou/deep-person-reid/blob/master/LICENSE)
is MIT. Research-dataset provenance and uncalibrated identity behavior remain
limitations. No newer-model claim substitutes for integration or measurement.

## 9. Runtime traces and representative failures

`BAI_TRACE_DIR` enables `execution-span:v1` JSONL. Each span has session/source
hash, span/parent IDs, canonical frame bounds, Unix start/end and monotonic host
duration, bounded attribute summaries and error details. No images, tensors or
appearance vectors are logged. Open/write/close failure warns without masking
the original provider failure. Nested sessions/disabled scopes restore context.
All timings are labelled `host_wall_time_no_device_sync`.

Concrete source examples:

- Frame369/12.30s was a false content barrier. Two current proposals overlap a
  crouched far player/witness; retaining unknown layout does not imply positive
  identity correspondence. Run03 preserves epoch0 and the prior tracker IDs.
- Frames441/14.70s and521/17.37s show an extra seated-spectator box. Raw track4
  later follows a moving athlete. Fresh detector matching alone cannot certify
  ownership; the source image and saved boxes expose the handover risk.
- At868/28.93s and876/29.20s, probable contact cues belong to the same far episode.
  Raw shuttle gap889–915 follows; the short candidate lacks independent opposing
  witnesses. Lowering duration thresholds would not establish an actual rally.
- Frame599/19.97s contains a raw shuttle marker on the adjacent court in the
  saved review. Candidate support/model score is not physical shuttle truth.
- Current poses are often inferred from carried boxes: run03 has4,252 such
  person/frame rows. They retain current image stamps without becoming fresh
  player identity evidence.

## 10. Latency and resource measurements

| Measured scope | Run01 baseline | Run02 native pool1 | Run03 scene repair/CPU changes |
|---|---:|---:|---:|
| Analysis wall seconds |629.071 |624.072 |600.023 |
| Component initialization seconds |7.440 |7.020 |7.005 |
| Warm start seconds |19.149 |20.205 |19.394 |
| Decode total seconds /75 chunks |10.957 |11.314 |11.067 |
| Perception total seconds /75 chunks |565.019 |558.222 |530.914 |
| Perception chunk p50 milliseconds |7250.57 |7124.67 |6771.06 |
| Perception chunk p95 milliseconds |14161.15 |13229.64 |12270.39 |
| Perception chunk maximum milliseconds |14888.10 |14492.07 |13034.29 |
| Content observation total seconds |Not separately traced |85.763 |77.050 |
| Content validation total seconds |Not separately traced |24.275 |7.274 |
| Temporal ingest total seconds |17.090 |17.197 |21.635 |
| Perception persistence total seconds |5.540 |5.957 |1.949 |
| Track persistence/transport total seconds |1.495 |1.785 |3.306 |

Nested scopes overlap; totals must not be added as independent inference time.
Single totals do not support p95 claims; percentile entries above use75 chunk
samples. Trace summaries also contain detector/pose/batch/racket/OCR counts and
latencies. GPU telemetry samples actual process PID/UUID/memory/utilization every
approximately2s; RSS is server-process resident memory, not full process-tree or
initialization-peak accounting.

Run01 and02 frame payloads are exactly equal, including diagnostics and missing
NaN joint semantics. The aligned middle-video resource sample window (published
frontier239–4199, analyzing state) gives mean server CPU944.84% versus347.98%
(254/251 samples); over100% denotes multiple cores. This supports lower CPU
consumption, not a statistically established total-latency gain. RSS peaks vary
and no memory improvement is claimed from those runs.

Run03 changes scene/identity/background state after the repaired boundary and
therefore changes workload. Compare the unchanged first360 frames separately:
content observation19.672→17.116s, content validation5.765→1.433s, same167
detector calls/160 pose calls/12 shuttle batches and identical frame payloads.
Whole-run600 versus624s is an observed combined result, not isolated LK speedup.
Shuttle changes can begin at361 because a temporal window includes the old369
barrier. No neural sampling threshold was tuned to produce these timings.

Remaining measured CPU costs include geometric racket extraction (~94s in
run02), court/camera, scene work, pose crops and CPU OCR (~41s with no readable
scoreboard). A full-video bulk track API request is ~11.5MB and took3.31s in
run02; normal viewport windows are smaller. Run03 one-shot analytics GET was
1.742s while earlier single samples were~16–17ms. Cold folds, cache state and
concurrent reads differ; this is not a proven regression or a comparable p95.

## 11. Iteration history and before/after comparisons

| Run | Source/config and cache | Session | Result |
|---|---|---|---|
|01 | Dirty `e558fd9`, original native pool36, passive trace, fresh data | `01M7A8NAGTXH3J7HXEAW17WH96` | Complete4,462frames; false epoch reset369;2 unofficial candidates,7 unknown stroke events |
|02 | Same profile/models/cadence; pool1; finer spans; browser SAR fixes; fresh data | `01M7A9S1B8M5GFKJPCQV6Z0TJG` | Same exact frame outputs; CPU reduction; same2/7 sports outputs |
|03 | Scene ambiguity abstention + validation/cache/grouped-LK fixes; pool1; fresh data | `01M7AB2DGRBX8JAKNNZ0QS3Q36` | Complete; epoch0 allframes;3 unofficial candidates,14 unknown stroke events;600.023s |
|04 | Committed `ac0084f`, same profile/pool/cadence, configured pinned OSNet now available, final UI/cancellation diagnostics; fresh data | `01M7ACDPXGXM4YNQ866CF2FEGJ` | See closing measured supplement |
|05 | `8110422`; same video/profile/models/cadence; request/unused-read fixes, early image observations and presentation repairs | `01M7AE8EGHF561F9WWWXC1NKFW` | Interrupted at4,020 analyzed frames/frontier4,019; no full-run latency claim |
|06 | Same source/config as05, fresh data and normal upload, detached service/browser/observer | `01M7AEZC82KAE6B152D6TWYJTB` | Final integrated comparison in closing supplement |

No iteration overwrites an earlier source archive, cache, ledger or browser
capture. ReID intentionally changes canonical ID namespaces; compare raw IDs,
boxes and exact frames rather than treating canonical integers as physical truth.

## 12. Rally/timestamp findings and reference limits

Run01/02 retain only472–539 and1869–1943. Run03 retains472–555
(15.73–18.50s),1747–1812(58.23–60.40s),1858–1944(61.93–64.80s), all
unofficial with unknown winner. These are numerical intervals, not a claim of
three correctly recovered whole physical exchanges.

The coarse full-video visual draft contains activity intervals0–4,6–10,11–19,
21–28,32–45,48–50,54–65,67–78,81–89,93–100,104–111,113–130,131–139,
140–145,147–148.736s. It guides inspection/coverage diagnosis. It is not an
exhaustive contact/rally-boundary annotation and is not used for precision,
recall, F1, boundary MAE, class confusion or identity accuracy.

## 13. Actual frontend visual validation

Chromium156 opens the built SPA, selects the locked local video in Library,
chooses Doubles, leaves names blank and clicks Analyse video. No fixture or API
upload substitute is used. Source playback, processing progress, overlays,
timeline, rally/shot/court/movement/pair/moments tabs and unknown/empty individual
analytics are captured. Screenshots inspect12/32/62/92/122s and evidence seeking.
Watching frame472 seeks to15.75s, within the intended frame display convention;
next-frame12.00→12.05 updates visible frame360→361.

Analysis coordinates remain raw762×720 while video containment uses display
763×720. The court editor click/drag/Undo test measures exact raw positions using
the actual SVG rectangle and ignores letterbox areas. It creates no persisted
calibration or other mutation. Layer toggling changes actual canvas content.

Final UI changes show actual recorded capability/degradation values, distinguish
anonymous episodes from reviewed athletes/two scoring slots, call uncertain
results candidates/events, show correct presence/distance units, preserve
highlight evidence/status, and withhold unresolved pose/travel/name continuity.
An explicitly missing recording no longer silently selects another recording.
Positive named four-player heatmaps, verified winners and nonempty highlights
are not manufactured to exercise otherwise unavailable states.

## 14. APIs, persistence and exports

Per-run `api/` captures include session, system, canonical analytics, individual
and estimated analytics, highlights, events JSONL, rallies CSV, summary JSON,
report PDF, full track msgpack and metrics. All completed-run captures returned
200. Read-only SQLite folding agrees with live API counts; retracted/superseded
events are not counted as current sports facts. All stored pose/racket rows
inspected in summary audits have their correct current frame source; finite
supported joint/bbox contracts report no invalid rows.

The four participant cards have unavailable reviewed movement/shot facts without
reviewed identities. Zero accepted points and unknown winners/scores agree across
ledger, API, exports and UI. PDF generation succeeds; this verifies export
execution/content consistency, not the quality of unsupported sports estimates.
The rally CSV intentionally exports **official** intervals only: it has zero data
rows for run04, while live events retain two unofficial candidates. Summary
analytics likewise has zero counted rallies. This is a scope difference, not
missing official CSV rows; candidate evidence remains in the event export.
Run04 explicitly checks cancellation payloads, appearance runtime and real binary
WebSocket delivery in addition to these snapshots.

## 15. Tests and validation discipline

Final curated Python regression: **1,216 passed**,8 deprecation warnings,
108.33s, exactly105 audited synthetic modules, AV media guard and bounded native
thread environment. Exact module list/per-node results/source hashes are in
`contract-tests/final_synthetic_selection_v2.json` and
`final_synthetic_receipt_v2.json`. This is not the unrestricted repository suite.

Additional focused checks:97 temporal/store/profile tests,34 final
wire/domain/identity integration checks,22 unresolved-wire/ReID checks,26
bundle/codec checks,230 curated scene checks and51 dedicated scene optimization
checks. These sets overlap; their counts must not be summed as unique coverage.
Changed51 Python files pass final Ruff and AST parsing, and Git whitespace checks pass.
Frontend after the final repairs: **264 tests/52 files**, typecheck, formatting
and production build pass (253/51 was the preceding run04 candidate).
Detailed commands/results/ownership are in the three linked workstream reports.

Earlier failing tests/logs remain preserved. Substantive fixture failures came
from missing per-person matches/context, missing endpoint proof or unstamped
synthetic pose/shuttle data; positives now declare the generator's actual
evidence and negatives explicitly remove it. Production provenance gates and
positive class/movement assertions were not weakened to make tests green.
Adding optional cancellation metadata required one exact asdict expectation to
include `cancelled_segment=None`; admission/terminal assertions remain.

### Scope deviation and defensive harness failures

One broad scene-test glob mistakenly executed retained historical grayscale
fixtures:15 images from Test1 frames10766–10770/15575–15579 and Test2
7699–7703 through three classical scene observers, plus51 retained geometry JSON
cases. **This violated the intended synthetic-only test selection.** No historical
source video was decoded and no historical neural inference occurred. The
execution/log is retained, excluded from this selected-video empirical evidence,
and later commands use explicit lists/name exclusions. This cannot be undone or
described as full compliance with the single-video processing restriction.

Two broader-test harness errors are also preserved: a per-node recorder collided
with a global Path.open failure-injection mock; a later wrapper had an empty
module array after a missing `python` command and attempted default collection.
The AV guard blocked generated-media fixtures before opening/creating media.
The final wrapper uses `set -euo pipefail`, explicit `.venv/bin/python`, an exact
105-module count assertion and the AV guard. Those rejected invocations are not
application failures or passing regression evidence.

An initial browser selector failed before upload. A headless-shell watcher exited
after~32s while the backend continued. Full Chromium completed subsequent
captures. Initial sprite metadata404s recover after generation; no successful
media/result payload was fabricated to hide them. These harness/transient states
and eventual successful requests are retained in browser receipts.

## 16. Component acceptance and unresolved work

| Component | Status supported by this controlled case | Practical limit |
|---|---|---|
| Ingestion/CFR decode | Validated for selected recording | VFR, rotation, other codecs and long videos not exercised |
| Court/camera | Partially validated | Finite/consistent matrices and visible overlay do not independently certify geometry on a partial court |
| Player detection | Partially validated | Active boxes inspected; spectator/occlusion errors remain |
| Tracking/episodes/physical identity | Partially validated; physical ownership failure observed before run04 | Run04/06 split the inspected ownership handover, with remaining fragmentation and no dense identity truth |
| Pose | Partially validated | Actual loading/shapes/stamps/overlay exercised; joint accuracy and carried-crop association not fully labelled |
| Shuttle association | Partially validated; physical coverage inadequate | Missing raw evidence and adjacent-court aliases remain |
| Racket/contact | Partially validated | Exact cues traceable, physical impact remains ambiguous/insufficient; geometric aliases observed |
| Stroke classification | Failed coverage / blocked for accuracy certification | All retained run03 labels unknown; no suitable labelled doubles classifier integrated |
| Rally segmentation | Failed whole-exchange coverage | Fragmented raw evidence and insufficient independent opposing contact cues; no threshold-based manufactured recovery |
| OCR/outcomes/scoring | Acquisition/gates partially validated; positive score path not exercised | No readable scoreboard or reviewed winning terminal/row identity in clip |
| Individual analytics | Contracts validated synthetically; actual unavailable states inspected | Four physical athletes are not automatically four reviewed identities |
| Highlights | Empty/gated execution validated; positive selection not exercised | No supported qualifying match facts in selected output |
| Persistence/API/export/WS | Exercised and consistency inspected | Historical migrations/multiple-user concurrency not exhaustively validated |
| Browser playback/overlays/editor | Exercised with real results; targeted contract checks pass | Other devices/layouts/content and positive reviewed analytics not exercised |
| Resource/performance | Measured and bounded improvements demonstrated | No all-node GPU profile, multi-job throughput or long-video stress certification |

Remaining external dependencies are independently reviewed physical shuttle,
contact/negative, stroke and identity labels; suitable verified doubles/small
object/equipment checkpoints or training evidence; and review of visible court
geometry/score ownership. These requirements must not be replaced by generated
references, easy threshold tuning, interpolation-as-observation or fake names.
The single selected clip cannot exercise all scene, format and score transitions.

## 17. Remaining bottlenecks and engineering decisions

The largest useful measured CPU targets are geometric racket work, scene/court
processing, CPU OCR and per-crop pose overhead. Scene optimization was implemented
only after attribution and compared on unchanged input. No GPU parallelism,
unmeasured TensorRT/FP16 detector conversion or duplicate neural engine was added.
Appearance activation is a controlled extra workload, not a free speed improvement.

Potential future work includes avoiding redundant default RTMPose session
construction, measured pose batching, justified OCR acquisition policy, bulk
serialization and resource admission/model reuse across concurrent sessions.
These are not claimed implemented or validated by a sequential one-video test.
Physical accuracy work must first resolve source-bound labels and the raw
perception failure windows rather than adjust the final rally count.

## 18. Changed-file inventory and workstream detail

`ac0084f` changes79 files; `8110422` changes22 files, with overlap. Important groups:

- `engine/src/bai_engine/{trace,config,obs,wire}.py`, `runtime/runner.py`:
  optional diagnostics, native thread lifecycle and lossless unresolved display
  observations; dedicated trace/thread/wire/ingestion tests.
- `apps/api/src/bai_api/app.py`, `start-app.sh`: complete-bundle startup contract;
  API layout regression; reviewed four-player synthetic proof fixture repair.
- `sports/badminton/src/bai_badminton/{engine,components,plugin}.py`:
  cancellation persistence, contact/stroke/outcome spans, provider version
  identity and ReID capability runtime alias.
- `events/{rally_fsm,rally_evidence}.py`: validated parameters, optional exact
  cancellation segment and retained short-exchange decision inputs.
- `perception/{content,scene_change,pipeline,players,tracknet,offline_reid,components}.py`:
  source-bound false-reset abstention, cached proof records/grouped LK, single
  boundary validation, crop-array fix, model/stage runtime evidence.
- `apps/web/src/lib/{tracks,videoCoordinates,reviewedIdentity,types}.ts`, player
  overlay/VideoStage, court editor/minimap, session quality/heatmaps/highlights/
  rallies and collection selection: temporal/display/uncertainty contracts and
  matching regressions.
- `apps/web/src/lib/analysisRefresh.ts` and analytical query hooks: one shared
  per-session refresh owner, bounded derived snapshots, AbortSignal propagation,
  terminal/revision/correction freshness and dirty in-flight follow-up. Raw
  event/overlay updates remain immediate.
- `analytics/rebuild.py`: candidate-only/empty folds skip unused geometry I/O;
  official geometry consumption remains unchanged. `engine.py` separately
  preserves valid uncalibrated image boxes with null spatial/participant facts.
- Synthetic tests explicitly cover missing proof, identity/epoch ownership,
  cancellation lineage, invalid geometry, output compatibility and legacy unknowns.

Full source inventory: `git show --stat ac0084f`, `git show --stat 8110422` and
`git diff --name-status e558fd9 8110422`.
Detailed owned reports:
[perception](single-video-perception-20261113.md),
[contracts](single-video-contracts-20261113.md),
[frontend](single-video-frontend-20261113.md).

## 19. Artifacts and reproduction

Artifact root:
`/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/`.
Historical artifacts remain untouched. New per-run subdirectories contain
`source_receipt.json`, `executed-source.tar.gz`, `working-tree.patch`,
`backend.log`, `data/` (source/proxy/HLS/session cache/SQLite/Arrow), `traces/`,
`resource-status.jsonl`, component/trace summaries and `api/`. Browser HAR,
screenshots, trace archives, live WS summaries and exact harness source are under
`frontend/`. Selection/packet timeline and model-fetch/hash receipts are separate.
Artifact hashes/index are recorded after the final capture.

Reproduce on the existing compatible Pascal environment without replacing its
custom Torch/CUDA installation. Start with the committed source and built web:

```bash
cd /home/administrator/Desktop/sport-analytics/Sports_Analytics
source ../gpu-env.sh
pnpm --dir apps/web build
.venv/bin/bai models fetch osnet_ain_x0_25
# Verify SHA ce171fe160b3608f5e4c19489774991419be965b1d6f4bdccc4b4cfd2ef95347.
# Choose a new, empty run directory. Never reuse a recorded run directory.
validation_run=/absolute/path/to/new-single-video-run
BAI_DATA_DIR="$validation_run/data" \
BAI_TRACE_DIR="$validation_run/traces" \
BAI_PROFILE=experimental-pipeline-repair-v1 \
BAI_ENGINE_MODE=embedded BAI_REDIS_URL= BAI_PASSPHRASE= \
BAI_OPENCV_THREADS=1 CUDA_VISIBLE_DEVICES=1 \
./start-app.sh --host 127.0.0.1 --port 8011
```

Open `/library`, upload only the locked source/hash, select Doubles, leave names
blank, and click Analyse video once. The current full Chromium live harness used
for run06 is retained under `frontend/watch-live-workflow.mjs`; its locked source
guard refuses any other media path. Example command (output must be new):

```bash
node /home/administrator/Desktop/sport-analytics/single-video-validation-20261113/frontend/watch-live-workflow.mjs \
  http://127.0.0.1:8011 /absolute/path/to/new-browser-capture \
  /home/administrator/Desktop/sport-analytics/Sports_Analytics/data/media/06a5cb888e58c64421114fecc582f60b85466900efec6db0bbf99420f4f6c010/source.mp4
```

The retained harness requires the **absolute** locked source path shown above. `observe.py --out RUN --pid PID`
samples resources/status; `summarize.py RUN` reads saved outputs;
`capture_api.py http://127.0.0.1:8011 RUN` captures APIs/exports;
`compare.py LEFT RIGHT` compares cached frame fields. Their retained sources and
hashes make orchestration inspectable; they do not replace the real app workflow.

Synthetic reproduction uses explicit module selections and media guard; see
`contract-tests/final_synthetic_selection_v2.json` and the workstream report.
Do not run a broad historical scene fixture glob or an empty/default pytest list.

## 20. Closing measurements and final disposition

### Completed live baseline: run04

Run04 completed all 4,462 frames on `ac0084f`. Analysis took771.019s; the browser
observed773.924s from upload click to completion. Appearance ran1,776 times,
55.707s total, median30.649ms/p9536.568ms; its exact CUDA FP32 parameter/checkpoint
metadata is present in session capabilities and its output feeds canonical
association. No descriptor vectors are persisted.

The run retained two unofficial intervals472–555/1858–1944,10 unknown stroke
events, seven ambiguous/three insufficient impact assessments, unknown winners
and zero accepted points. Raw shuttle outputs are identical to run03:1,416
observations and3,046 missing samples, not an estimated recall measure. Pose
rows10,857 include4,009 on carried boxes; all source stamps remain explicit.

All50 canceled starts now retain their interval/admission proof:38 gap endings,
11 stationary endings and one EOF close. Forty-one lack a qualified observed
motion span; nine lack an independent contact pair. For example, candidate9–22
has14 frames against the60-frame duration policy, observed motion span9–11 and
only one retained contact witness14. It is rejected without asserting that the
physical exchange ended there. Its original event, retraction and track-window
references remain inspectable in `run04/cancellation-audit.json`.

The inspected spectator-to-athlete handover changes from a single canonical
owner to old7249→unknown/transient8385→new8449, with an uncertainty link. Another
near player fragments2→6817. This is a scoped uncertainty improvement, not
stable four-player identity or an identity-switch accuracy metric. In the first
1,980 frames there are554 unresolved rows/105 frames with two unresolved bodies;
the active badminton engine already had unique negative display IDs, so the
generic wire repair is not claimed to recover105 missing overlays.

Live-page telemetry records3,666 API responses, including1,368 analytics and
2,189 heatmap responses. These exclude the separate harness/observer status
polls. Duplicate per-widget invalidation drives redundant consistent-snapshot
reads; those locks exclude the writer. Temporal ingest rises to91.246s and track
persistence/transport27.808s, versus21.635/3.306s in run03's different browser
workload. Appearance alone does not explain the whole slowdown.

The resulting fixes are source-committed, not just recommendations: shared
derived-query scheduling, correct terminal/revision/in-flight refresh semantics,
and omission of unused camera scans in candidate-only folds. Six alternating
same-store CPU-fold pairs produce identical JSON with median135.082ms reference
versus1.321ms optimized. This is a local fold measurement, not a100-fold
end-to-end performance claim. Frontend checks increase to264 tests/52 files;
backend follow-up suites pass34 analytics/transaction checks and20 image/camera/
epoch checks. These overlap prior coverage and are not summed as unique tests.

### Interrupted attempt: run05

Run05 never completed. At the conversation/tool interruption the service became
unavailable; persisted state remains analyzing at4,020 frames/frontier4,019.
The browser retained502 page responses and failed on connection refusal after
approximately593s. Its resource observer retained only151.30s, so it cannot
support a full resource or wall-clock comparison. No processing traceback was
found; the exact termination signal was not captured. `run05/interruption.json`
preserves this distinction. Nothing was reset or overwritten to make this attempt
look successful.

The fresh run06 uses the same locked source, `8110422`, profile, checkpoints,
sampling and browser workflow. The backend, observer and browser are detached
with explicit PID receipts so conversation lifetime does not control their
survival. Its completed comparison and final disposition follow below.

### Completed final comparison: run06

Run06 finishes at frame4,461/all 4,462 frames with no processing exception or
trace-write failure. **Every cached frame field equals run04 exactly**, including
diagnostics, detector/pose cadence, association, coordinates, uncertainty and
missing-joint semantics. Canonical event counts/intervals also agree; session/event
ULIDs differ by design. The track API now retains all 18,522 player observations,
including eight image-only rows at frames0/1 with null court positions and no
participant/name binding. The real browser displays those four initial boxes and
current poses while still showing unavailable court geometry/movement.

| Comparable measured scope | Run04 | Run06 |
|---|---:|---:|
| Browser upload-click→terminal seconds |773.924 |648.574 |
| Engine analysis seconds |771.019 |645.284 |
| Decode total seconds |21.389 |11.202 |
| Perception total seconds |591.741 |578.454 |
| Temporal ingest seconds |91.246 |23.390 |
| Track persistence/transport seconds |27.808 |2.246 |
| Appearance seconds |55.707 |54.126 |
| Page API responses |3,666 |551 |
| Analytics responses |1,368 |153 |
| Heatmap responses |2,189 |302 |
| Sampled GPU memory for server PID, MiB |2,142 |2,142 |

Observed engine analysis time falls16.31%; browser wall time falls16.20%.
Analytics requests fall88.8% and heatmap requests86.2%. These are combined fixes
in one complete controlled run per source state, not isolated optimization effects
or statistical confidence intervals. Browser/observer status polls are separate
from the page-response counts and use the same cadence in both runs. No neural
coverage reduction or physical accuracy gain is inferred from the timing result.

Run06 live network/body-finish measurements use nearest-rank quantiles:
analytics n153/p5033.5ms/p95205.0ms/max400.4ms; heatmaps n302/p5034.9ms/
p95195.7ms/max451.5ms. Run04 did not retain comparable per-request durations, so
there is no claimed before/after API p95. The actual terminal WebSocket status
is followed by fresh analytics and both presence requests, all200/21–26ms;
final derived values are not left at a stale pre-completion revision.

Selected run06 component host-wall measurements (nested scopes are not additive):

| Scope | Samples | Total s | p50 ms | p95 ms | Maximum ms |
|---|---:|---:|---:|---:|---:|
| Perception chunk |75 |578.454 |7732.792 |13408.668 |14314.061 |
| Player detector, including probes |1776 |43.257 |23.985 |25.663 |330.778 |
| Appearance |1776 |54.126 |29.771 |33.656 |197.228 |
| Pose |2612 |62.294 |22.991 |28.465 |136.662 |
| Shuttle forward batch |149 |14.663 |97.645 |105.305 |142.584 |
| Racket frame scope |4462 |85.330 |0.038 |70.520 |193.926 |
| OCR chunk scope |75 |41.956 |536.502 |808.004 |946.593 |
| Contact candidate window |76 |0.733 |8.301 |23.180 |29.118 |
| Stroke-classifier invocation |41 |0.002 |0.030 |0.174 |0.274 |

Run06 samples319 resource points; server RSS maximum2,762,399,744 bytes. There
is no memory-saving claim. API folding/derived refresh was a genuine exercised
bottleneck; remaining racket/court/scene/OCR costs are measured priorities.
Analysis is approximately260.3 processing seconds per source-video minute,
or4.34× source duration on this machine. It is not a real-time inference result.

### Final browser, persistence and artifact checks

Full Chromium stays connected through the entire upload/process workflow.
Playable media is observed at4.952s, first nonbacklog event batch30.217s and
first nonempty track window38.224s. All ten tabs and eleven selected timestamps
are inspected, including frames0/1 and420/521/540/599. Two simultaneous unresolved
bodies at frame421 remain independently rendered; no named identity is implied.
Keyboard navigation chooses the exact second-candidate event
`01M7AFB5G37J4K8YQBSAREG3AQ`/frame1858, and after presented-frame readiness video
time61.950s/control/evidence labels agree on Candidate2. No residual Rally0 is
shown in this checked path.

The quality panel shows actual model/runtime limitations. Unknown recording
selection remains unavailable and does not fetch another recording's insights.
Court editor click/drag/Undo matches raw coordinates. A real delayed-proposal
network check confirms that edits are ignored before initialization and Undo
works after readiness; no payload fixture or saved calibration is substituted.
All checks are read-only at the application level, with zero persisted mutations.

The complete live run has no page, request, WebSocket or decode failure beyond
two sprite-metadata404s that recover to200 during generation. Later repeated tab
navigation retains56 `net::ERR_ABORTED` analytical requests:53 finish within one
second of document initialization and match the new observer/navigation
cancellation path. Three later requests are consistent with snapshot supersession,
but their individual triggers were not independently proven. No page exception
or corrupted result accompanied them. The raw records and classification are
preserved rather than reported as zero request errors. One
premature400ms keyboard screenshot was retained and recaptured after actual
presented-frame readiness; no source change or inference retry was needed.

Saved API/SQLite/wire checks pass:864 append-only events,501 live events, all 50
retraction proofs and original-event/track-window references,18,522 player rows,
1,416 observed shuttle rows and4,462 camera rows. Live event export IDs equal the
ledger fold; `live=false` export preserves the full history. Official CSV has
zero data rows and canonical analytics zero counted rallies, while event exports
retain two unofficial candidates. PDF is a real generated PDF; every captured
API/export returns200. See `run06/saved-output-contracts.json`.

Exact results are linked by the preserved artifact index, source/built-SPA
archives, configuration, model hashes, traces, request comparison, portable SQLite
backups and browser captures. Run05 is explicitly excluded from completed-run
performance/resource conclusions.

### Acceptance and remaining blockers

| Component | Final scoped status | Reason |
|---|---|---|
| Acquisition/CFR timeline | **Validated** | Selected stream, source/proxy timestamps and all decoded indices agree |
| Model loading/input-output integration | **Validated for exercised contracts** | Real primary detector/pose/shuttle/appearance/OCR paths execute and their outputs are consumed; operation-level GPU placement remains unprofiled |
| Court and pose physical geometry | **Partially validated** | Numerical/freshness/visual checks pass; partial court/joints lack independent physical labels |
| Tracking/participant episodes | **Partially validated** | Specific ownership handover is split/withheld, but stable physical identity fragments and is not certified |
| Shuttle physical trajectory | **Partially validated** | Observations/estimates/missing provenance is preserved; sparsity and adjacent-court aliases remain |
| Racket/contact evidence | **Partially validated** | Real cues/abstentions traceable; no independently established impact accuracy |
| Stroke classification | **Failed coverage; accuracy certification blocked** | Ten final stroke events remain unknown; supported endpoints/contact evidence and a suitable labelled doubles classifier are absent |
| Whole-rally segmentation | **Failed coverage** | Two candidates do not account for the approximately15 visible draft exchanges; raw perception and opposing-contact support remain inadequate |
| Positive OCR/score/outcome transitions | **Not exercised** | No usable scoreboard/reviewed terminal winner; conservative unknown handling does execute |
| Positive named four-player analytics/highlights | **Not exercised** | No reviewed physical identities or qualifying accepted points/events; explicit empty/uncertain paths pass |
| Persistence/API/export/live browser | **Validated for exercised workflow** | Real workflow completes; schema, frames, evidence, uncertainty and folds agree |
| Performance/reliability | **Partially validated** | Same-workload latency/request reduction measured; multi-job, long-video and all-node GPU profiling are outside exercised scope |

Further physical accuracy improvement needs independently reviewed source-bound
shuttle/contact/negative/identity/stroke labels and camera-appropriate pretrained
assets or training evidence. The single allowed recording cannot establish
held-out generalization or exercise VFR, different cameras and positive scoring
scenarios. Training/tuning to this clip's draft count would manufacture success;
no such tuning was performed. Missing raw evidence is not repaired by relabelling
interpolation as an observation or forcing a stroke, winner or player identity.

**Final execution status:** source improvements implemented and integrated;
every active pipeline area investigated; five complete real selected-video runs
plus one preserved interrupted attempt; real backend/frontend/browser/tests and
performance measurements executed. Software consistency and exercised integration
repairs are demonstrated. Sporting accuracy/generalization, stable four-player
identity, the unexercised scenarios and production deployment readiness remain
unverified or failed as classified above. No push or merge was performed.

### Final evidence and Git receipt

The [artifact index](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/artifact-index.json) records3,336 files /2,208,099,611 retained bytes; SHA256 `eefd4461bde17fe2cac013748ad6baaca754490055f77cef5882d5360d74fda1`. Portable SQLite copies and the frozen final backend log are under each run's `frozen/` directory. The working final backend remains available on127.0.0.1:8011 (PID1159298), serving source `8110422`; it is not a public deployment.

Inspect [final output checks](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/run06/saved-output-contracts.json), [timing/output comparison](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/run06/final-comparison.json), [live request comparison](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/frontend/request-comparison-run04-run06.json), [final browser screenshots](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/frontend/run06-final/) and [initial image observations](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/frontend/run06-live/03-first-analysis-progress.png). The index includes exact orchestration helpers/harness copies and source/built-asset hashes; source/model/video hashes are not substituted for physical labels.

The final documentation commit follows source commits `ac0084f` and `8110422` on the existing engineering branch. Generated videos, model weights and large diagnostic artifacts stay out of Git and are preserved at the indexed paths. The working tree is checked after the documentation commit; no main merge or push is performed.
