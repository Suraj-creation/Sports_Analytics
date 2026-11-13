# Independent review of scene feature-origin implementation V5

The reviewed V5 implementation separates **LK feature origins** across prior ROI masks and preserves the full boxes for detector-layout correspondence. It does not establish statistically independent LK patches, distinct physical actors, named identity, or physical scene accuracy. Two material contract risks identified during this review were corrected by the production owners: self-consistent omission/substitution of an actual prior ROI, and raw strong fallback on a newly overlap-dependent ambiguous layout. A further reproducible one-actor-fragmentation counterexample was also corrected conservatively. Original positive and corrected probes are preserved separately.

The final bounded review passes **174 focused tests**, four recomputed-mask forgery refusals, and the exact synthetic counterexample. Six independently hash-checked source/model/crop-bound component controls produce four barrier decisions and two no-barrier controls. These are component checks, not proof that a complete new neural pipeline run preserves rally metrics or recovers every edit. Full chronological pipeline/cache validation and fresh Test 1–2 regressions remain required before adoption.

## Executed source and scope

The review imports the actual isolated producer at `/home/administrator/Desktop/sport-analytics/test03-scene-overlap-20261112`, based on commit `2418ab8cbe4cca74dd16b722b9727ffdc950294a`. The reviewed changes were evolving working-tree changes; that base commit alone does not identify the new implementation. Exact four-file source snapshots and SHA256 bindings are retained under each probe attempt. [Final focused verification](bounded_controls_verification.json) additionally binds all six test files before/after execution. Imported module paths point to this producer; no `ROOT` reassignment or historical cache-header rewriting was used.

| Final reviewed source | SHA256 |
|---|---|
| `perception/scene_change.py` | `f54fa65da75c4e2fced124130c8058266a83f31512a3beae388a44e3642745d7` |
| `perception/content.py` | `96a8c54e5145fdaf4d61f7290e6053736dfe4826616adbc9c879fefcbaf8823f` |
| `perception/components.py` | `739e0468e9f9353fe19224616ab9019fe2eed691ca2ebf708a180833cd698034` |
| `plugin.py` | `acf452c857b64a9d5006544e38439592cc1750ba99044c9a3375a96077f30b41` |

Only new review scripts, synthetic fixtures, snapshots, and reports were written in this review directory. No production, model, configuration, annotations, historical evaluator, or closed video output was modified by this reviewer. The synthetic flow probe replaces `_flow` only in its own Python process to isolate contract logic; its reported innovations are deliberately controlled values, not video measurements. Existing tests likewise exercise contract fixtures without neural inference. No Test 3 data was accessed.

## Feature-origin and coordinate contract

Every measured prior full ROI participates in occupancy, including static, ineligible, or non-supporting regions. A region receives only pixels covered by exactly one ROI as potential feature origins. Exact duplicates and nested inner boxes therefore cannot each contribute an independent origin pool. Background flow continues to exclude the union of the **full** prior boxes rather than just exclusive slivers. Full-box coordinates remain available for the existing 0.3 IoU detector-layout logic; the new masks do not shrink player boxes or change court geometry.

V5 records its named origin policy, input and analysis raster sizes, and a key/count/SHA256 record for every measured prior ROI. The parser rederives all masks from all declared prior boxes, rejects wrong count/digest/key/order/shape/policy, and rejects impossible feature counts or current innovation from empty masks. Same-channel witness flags and relative/acquisition cohorts are recomputed from measurements and recorded parameters. The existing adaptive ratio 3, strong mean floor 15, at least six features, background support gate 0.5, and layout IoU 0.3 remain unchanged defaults; they are not newly fitted to these cuts. Custom recorded parameters remain bound to the producer profile.

The observer's `source_frame_size` means **the pixels passed into the observer**. In these runs that is the canonical 1280×720 analysis proxy; the original video is 1920×1080. The default measurement raster is 480×270. Source evidence for frame 2928 independently records original `[1080,1920,3]` and proxy `[720,1280,3]` shapes in [the coordinate-basis verification](bounded_controls_verification.json). The codec compares the observer size against the actual cached canonical frame size, and the measurement raster against the configured width/aspect calculation. It must not compare the 1280 proxy box coordinates to the 1920 original canvas without the recorded transform.

Disjoint starting centres are not disjoint photometric observations: LK windows and pyramids can overlap spatially, and two partial boxes can originate from one physical person. Mask hashes prove the declared origin domain, not that the scene contains multiple independently moving actors or that the recorded feature values were independently human-validated. A changing mask/history distribution can also affect adaptive measurements. Source-bound controls and false-reset studies remain necessary.

## Review findings and corrections

| Finding | Preserved evidence | Current disposition |
|---|---|---|
| Raw masks could be internally consistent after omitting or relabelling a prior static region. Recomputing mask hashes alone did not prove the list was the actual complete previous foreground. | Independent static omission/relabel/box-shift/reorder probes in [attempt 01](probe_attempt_01/result.json), repeated in [attempt 03](probe_attempt_03/result.json); owners implemented binding before the first executable probe. | Native codec now compares nonempty measured raw-region sequences with the actual previous-frame `fg`, all fields and order, when that adjacent frame is present in the packet. Exact positive payload passes; all four consistent rewrites fail. |
| Two partially overlapping fragments could support V5 raw change, while one current full actor box matched both. Existing strong unknown fallback could reset on that ambiguity. | Same actor represented by two partial fragments plus a static second actor; source snapshots and typed decision retained in each attempt. | New `feature_origin_overlap_dependent` provenance is recomputed from the raw whole-box legacy rule. An unknown decision in this newly expanded authority abstains from resetting. Old nonoverlap raw fallback retains its historical meaning. |
| Complete current two-person layout alone still did not exclude a single moving actor represented by two prior fragments. The other actor positively matched a non-innovating prior region. | [Attempt 02](probe_attempt_02/result.json), `layout_variants.partial_duplicate_one_actor_displaced_other_static`: `barrier=true`. This counterexample remains immutable. | [Attempt 03](probe_attempt_03/result.json), exact same case: `unknown`, no reset, reason `nonwitness_court_region_preserves_overlap_continuity`. Current strict-court positive correspondence with any prior nonwitness now vetoes new overlap-dependent reset, using raw OR camera-aligned boxes. |

The fragmented-actor fixture has prior boxes `(200,100,500,500)`, `(400,200,700,550)`, and static `(800,100,1000,500)`. Controlled innovations occur only in the first two; current boxes are `(20,100,180,550)` and the unchanged static box. A confirmed two-person complete court layout and identity camera previously permitted a false-positive **synthetic** reset despite the unchanged actor. The corrected policy preserves uncertainty. This is a design counterexample, not a measured video false positive or an invented annotation.

The new veto uses only current **strict-court** boxes: a seated outside-court official that remains visible cannot by itself block acquisition. `nonwitness` means absent qualifying innovation, not verified static identity. For doubles, one unchanged current court actor can conservatively block a reset even when other actors truly changed across an edit. That reduces authority rather than asserting that the frame is continuous; sensitivity on real doubles remains unmeasured. Fragments with no remaining positive nonwitness correspondence can still be indistinguishable from an edit using these measurements alone. There is no proof of physical multi-actor independence.

## Source, format, camera, and version binding

The current live producer sources its previous regions from the exact preceding `_content_previous` foreground in canonical order. Codec24 additionally binds nonempty V5 raw regions to actual previous `fg` within a packet. A first record that refers into the previous packet cannot establish that source population by standalone decoding alone. The full native audit must compare across packet boundaries using the actual previous packet and source receipts; this review does not fabricate that proof or claim it is already a complete new-run validation.

New raw V5 maps to decision V4; older raw V4 remains decision V3 with its old whole-ROI witness interpretation. Legacy wire serialization omits the new origin fields and overlap-authority flag. V5 cannot be downgraded into codec17–23, and codec24 selected layout policy cannot silently accept a V4 measurement basis. Historical V4 diagnostic decode remains available without acquiring new authority.

New overlap-dependent nonunknown decisions require confirmed singles/two or doubles/four current strict-court coverage, valid source geometry, and both adjacent camera observations. Unknown format, missing camera, invalid geometry, incomplete doubles, and ambiguous current layout abstain in the independent probe. The decoder binds expected population to the pre-acquisition format context, detector model to producer models, image dimensions to canonical media, court polygon to the recorded calibrated reference and current camera, and the relative camera transform to actual adjacent cached observations where available. Camera-aligned positive correspondence also prevents new overlap authority from treating explained camera motion as scene replacement. These safeguards preserve anonymous hypotheses; no roster identity or scoring authority is created.

Cache invalidation is explicit: codec **24**, badminton pipeline version **9**, content component version **5**, raw schema V5 and decision schema V4. The component contract still supports singles, doubles, and unknown. The approved research compatibility changes add codec24 to normal completed-run acceptance; the strict recovery wrapper is not relabelled. No interval matching, scoring threshold, or numerical benchmark methodology was changed by this review.

## Bounded real-source controls and tests

The component owner's [closed layout result](../pre_test03_test02_regression_diagnosis_v1/isolated_scene_prefix_v1/layout_results_v3.json) and [receipt](../pre_test03_test02_regression_diagnosis_v1/isolated_scene_prefix_v1/layout_receipt_v3.json) were independently checked against all **18 recorded input hashes**, including actual source cache segments, model bytes, source/crop/model-bound query banks, source implementations, and previous-stage receipts. The new final policy reuses six retained actual query sets and performs zero additional neural forwards.

| Source frame | Component layout result | Tracking action | Correspondence |
|---|---|---|---|
| 2928 | barrier | reset requested | 1 of 2 innovating regions positively matches |
| 11082 | barrier | reset requested | 0 of 2 |
| 22416 | barrier | reset requested | 1 of 2 |
| 23279 | barrier | reset requested | 1 of 2 |
| 7703 | no barrier | no reset | complete 2 of 2 |
| 23639 | no barrier | no reset | complete 2 of 2; legacy-qualified case |

The observer study records 145 retained V4 comparisons with no reported value mismatch: per-window counts are 0,23,31,30,30,31 in the table's order. In particular, the 2928 prefix has no previously retained raw row for an exact recorded-row parity claim; its source-driven reconstruction must not be described as a cached-row match. Source/model/detector controls do not simulate the entire tracker lease, event engine, or downstream pipeline, and do not prove actual full-run scene epochs yet.

The final independent source-bound [focused test log](focused_tests_source_bound.log) reports **174 passed in 5.08 s**, with all four production source files and all six test files unchanged before/after execution. The earlier 171-pass interim log is retained as an earlier check, not substituted for the final bound receipt. Tests cover mask overlap/duplicates/nesting/static exclusions, source-mask forgeries and downgrade refusals, old schema controls, singles/doubles layout, camera/format/court binding, and the new conservative ambiguity policies. The pure [contract probe](probe_contract.py) also retains exact positive native decoding and the four source-population negative cases.

## Required next validation

Run the actual chronological candidate pipeline on both complete videos, preserving original model/profile/annotation pins and the failed prior candidate. Verify every prior scene barrier and new barrier with source evidence, along with whole-timeline detector cadence, player/foreground coverage, shuttle raw values/association, contacts, classes, and all unchanged interval references. Bind cross-packet foreground and camera provenance through the actual native audit. Check that the lost short coarse event around 11700–11760 and all existing mixed-IoU changes are measured again rather than inferred resolved from four cuts.

No candidate acceptance or physical accuracy claim follows from this report. The bounded implementation risks found here have focused corrections and reproducible controls; general scene recall/false-reset rate, doubles generalisation, and end-to-end nonregression remain open until the required runs and labels support them.
