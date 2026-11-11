# Test2 component validation — 5 November 2026

The complete production chain was technically exercised, but physical component accuracy is **unvalidated** without reviewed source-bound annotations. Rally-level legacy proposals do not supply shuttle/contact/pose/racket/identity/shot truth. Passing transport tests is distinct from useful automatic match analytics: this run has no accepted official rallies, identity-bound heatmaps or highlights.

| Component | Observed evidence / output | Validation boundary |
|---|---|---|
| Decode / timestamp mapping | 29,296 source and proxy frames; exact rational PTS identity; complete tail | Technically verified for this CFR30 source; generic VFR mapping not tested |
| Court / calibration | {'REACQUIRING': 22, 'VALID': 29205, 'LOST': 69}; court_lines_v1 fresh calibration | State coverage, not labelled geometric accuracy |
| Shuttle decoder | 20211 selected model coordinates | Includes dead time; presence rate is not detection recall |
| Association | {'missing': 9016, 'observed': 20194, 'invalid': 69, 'ambiguous': 17} | All-frame candidates/reasons retained; no independent visibility/location truth |
| Players / tracking | 58338 person rows; 12273 detector frames | Model coverage only; physical identity/IDF1/HOTA unvalidated |
| Pose | 46629 current-frame pose rows; no future stamps | Current source stamp is not pose correctness |
| Racket geometry | 20498 current geometry rows | Pose-derived heuristic geometry, not independently validated racket/contact detection |
| Contacts | 812 candidates; {'insufficient': 429, 'ambiguous': 278, 'probable': 105} | Zero confirmed physical impacts; no contact P/R from rally labels |
| Shots | {'unknown': 581, 'estimated': 231}; labels {'unknown': 581, 'push': 105, 'clear': 16, 'drop': 51, 'lift': 22, 'net_shot': 25, 'smash': 1, 'drive': 11} | 231 estimated labels /812; no per-shot reviewed denominator or confusion accuracy |
| Rallies | 73 candidates; legacy-reference TP67/FP6/FN6 | Reference agreement only; all 40 significant cases preserved |
| Format | Singles inferred at 96 from unknown; source shows two-player target court | Technical/visual singles check; no doubles accuracy validation |
| Physical identity | All 58,338 track rows and812 contact/stroke actors remain anonymous | Intentional abstention, not continuous physical/named identity proof |
| Positions / movement | 56,485 finite floor coordinates preserved in Parquet | Anonymous floor estimates, not calibrated athlete distances/speeds |
| Heatmaps | P1/P2 public grids have0eligible samples; raw position chart retained | Identity/official-ownership gates unmet; positive athlete heatmaps unexercised |
| Official play / points | All 73 rally candidates official=false, phase=unknown | No human/scoreboard corroboration; no points or score padded |
| OCR | One stabilized, unmapped SXFI21/LIVE12 board at 22924 | Branding/readout failure; no validated score sequence |
| Highlights | Empty | Positive highlight grounding/selection unexercised |
| Summary | Deterministic analytics/highlights export matches API | No LLM synthesis/paid provider call; sporting narrative accuracy unvalidated |
| API / frontend | 11 GET endpoints200,7 Firefoxpanels,4 downloadedexports; allsource/event bindings match | Transport/consistency passed; does not turn empty/unknown content into accuracy |


## Full evidence and technical checks

All 489 cache segments cover exactly0–29,295 and are byte-identical across independent fresh workers. Detailed heatmap/player diagnostics cover3,600 frames; all-frame raw decoder coordinates (already court-masked), association candidates/reasons, persons, geometry states, scene/format and source stamps remain cached. No full heatmap tensor retention or all-frame detailed diagnostic claim is made. Raw provider support and association/contact scores are uncalibrated, not physical probabilities.

The source-frame replay has6,551 exact-PTS frames over all 40 significant cases. Browser validation exercises all 40 cases and170 actual rendered frame/PTS checks; source/hash links are retained. Agent visual reviews are diagnostic drafts, not independent ground truth. Presence of `cc` content evidence includes negative hypotheses; actual barriers require the hypothesis flag/epoch transition. Neither content-hypothesis counts nor a model's VALID calibration state are scene/court accuracy scores.

## Why product-derived outputs are empty

The [empty-output causal audit](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/product_empty_outputs_causal_audit.json) verifies all 58,338 raw person rows survived into Parquet, including56,485 finite floor estimates,46,629 fresh poses and57,968observation references. Every row has player_id=None, and all 812 contacts and812 strokes have no accepted actor. Engine initialization deliberately withholds ambiguous physical identity; this is not a proved P1/P2 key-mapping or empty-session-player-list defect.

Independently, every rally has phase=unknown and official=false because match activity needs human or corroborated scoreboard confirmation. Analytics admit official-owned strokes/presence with accepted player IDs. The public P1/P2 queries therefore correctly return empty grids, and official-only CSV/highlights are empty. Source OCR's sole stabilized board is unmapped SXFI21/LIVE12 branding, not a verified athlete score transition. Forcing identities, official flags, points or highlights would manufacture evidence and was not done. The73unfiltered benchmark candidates remain available in their separate seven-column CSV.

## Runtime / product limits

Actual hardware is GTX 1080 Ti; TrackNet usesTorch CUDA FP16, while staged detector/pose ONNX inputs/weights areFP32. Optional OSNet is unavailable and explicitly degraded; OCR emits CUDA-provider warnings. Available/provider metadata is retained, but no per-node ORT placement profile was captured. Singles format and anonymous tracks do not validate named-athlete continuity across end changes, four-player doubles or amateur/multi-court recording conditions.

The isolated product test byte-copied a closed actual run; it did not connect to original SQLite, rerun models, change source events or deploy the application. It verified11 APIreads,7browser panels and4 downloadedexports against source IDs/bytes; original2,456consumed assets remained unchanged. Empty highlights/official rows make positive highlight/boundary checks vacuous, explicitly documented rather than counted as successful sporting validation. Q&A/provider generation was not exercised (zero POST /ask calls). The owned server required forced cleanup and was reaped; driver and loopback ports closed. Source-frame viewer v1 had a test-sandbox assumption failure; v2 uses actual DOM/rendered state and passes without changing the viewer/package.

Artifacts: [component counters](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/components/component_diagnostics.json), [per-frame coverage](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/components/frame_component_coverage.csv), [model graph types](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/model_graph_diagnostics.json), [product results](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/product_validation_v1/results.json), [product review](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/product_validation_v1/product_review.json), [source replay](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/failure_package/index.html). See [main evaluation](TEST2_EVALUATION_REPORT.md) and [reproduction](TEST2_REPRODUCTION.md).

## Standalone OCR execution-placement diagnostic

The full-video workers did not collect node profiles. A separate post-run diagnostic used the actual Test2 proxy frame 22,924 (exact source PTS), its cold top-left production search crop and the same verified OCR models/settings on physical GPU 1. Only process-local ORT profiling was enabled; original inference outputs and provider/model configuration remained unchanged.

| OCR stage | Executed unique CUDA nodes | Executed unique CPU nodes |
|---|---|---|
| det | 190 | 0 |
| cls | 179 | 0 |
| rec | 181 | 2 |

The two recognition CPU nodes are structural Concat/Slice operations. All profiled kernel events identify their provider; observed tensor types include float and structural int64. This sample demonstrates actual CUDA execution, despite the logged plugin-device warnings; it does not establish full-run placement or accumulator/hardware precision.

Profiled calls took 10122.24 ms cold and 8029.15 ms for one warm call; loading took 0.888 s. These two instrumented calls are not a steady-state benchmark or a controlled comparison with full-video runtime. Raw recognized text includes athlete names, but the unchanged row parser selects SXFI/LIVE branding as score labels: a retained layout/parser ambiguity, not valid sporting-score evidence. No logo blacklist, provider adjustment or parser tuning was introduced. [Raw profiles and report](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/ort_ocr_node_probe_v1/report.json), [source/model verification](../artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/ort_ocr_node_probe_v1/verification.json).
