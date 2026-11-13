# Test 2 regression diagnosis and isolated scene correction

The isolated observer/parser candidate restores positive scene decisions at the four source-confirmed edits **2928, 11082, 22416, and 23279** in bounded chronological source-pixel tests. Continuous-play controls **7703 and 23639** retain complete-layout vetoes. Full pipeline regression and acceptance remain the orchestrator’s next gates; these probes establish component behavior, not physical detection accuracy.

## Confirmed cause and correction

The previous observer discarded regional innovations whenever their full foreground rectangles overlapped. At frame 11082, both regions already met the unchanged correspondence innovation gates; rectangle intersection removed both witnesses. Other missed edits never acquired a serialized scene decision. These are real same-camera edits, verified separately against adjacent source images.

The new V5 measurement basis gives each prior region feature origins inside its rectangle **minus every other prior rectangle**. Full rectangles remain intact for layout, scene memory, and background exclusion. Feature count, history, adaptive ratio, strong intensity floor, channel quorum, and layout IoU policies remain unchanged. Source size, exact analysis raster dimensions, mask area, ordered region keys, and mask hashes are recomputed by the parser. Old V2–V4 measurement semantics remain unchanged: 145 retained source-prefix measurements compare exactly.

Disjoint feature origins do not establish distinct physical actors or independent photometric samples. LK windows and pyramids extend beyond their origins. Consequently, newly overlap-dependent authority requires a positively complete current court layout and camera/format evidence. Unknown or partial layouts cannot use the legacy strong-unknown fallback. Positive correspondence between a current strict-court proposal and a non-innovating prior region conservatively withholds this new authority; outside officials do not supply that veto. Camera-aligned correspondence also prevents motion explained by camera change from becoming a reset.

## Source controls

| Frame | Final bounded decision | Interpretation |
|---:|---|---|
| 2928 | Barrier | Source-confirmed edit; one partial full-box correspondence does not erase two qualified innovations. |
| 11082 | Barrier | Both previously overlap-excluded correspondence innovations are retained. |
| 22416 | Barrier | Source-confirmed edited jump and score change. |
| 23279 | Barrier | Source-confirmed edit; old pipeline carried prior boxes through the transition. |
| 7703 | No barrier | Complete current layout corresponds to prior layout. |
| 23639 | No barrier | Complete current layout corresponds to prior layout. |

Frame 2928 has two fresh admitted participants in the preserved run. Its additional scene-only foreground record is a separate typed object, not a third admitted player. Frame 22416 also has fresh correct participant boxes. Frame 23279 instead has carried participant boxes at the missed edit. These distinctions prevent scene-context counts from being presented as player-detection errors.

The source-pixel prefixes reproduce chronological observer history. Final layout controls use four successful detached RFDETR forwards at the four missed edits and two previously retained, source/crop/model-bound proposal sets for the continuous controls. One earlier detached forward completed inference but failed metadata assembly; its failure remains preserved. There was no TrackNet inference or full pipeline rerun in this task. Actual CUDA execution is bound in the hardware receipt.

## Validation and preserved evidence

- [Implementation receipt](observer_parser_implementation_receipt_v1.json): final source/test hashes, original producer preservation, scope, and test receipt.
- [Final six layout decisions](isolated_scene_prefix_v1/layout_results_v3.json) and [source-policy receipt](isolated_scene_prefix_v1/layout_receipt_v3.json).
- [Chronological prefix summary](isolated_scene_prefix_v1/summary.json) and [source rows](isolated_scene_prefix_v1/source_bound_rows.json).
- [Focused test log](lost_scene_prefix_v2/isolated_focused_tests_v3.log): **174 passed** in one selected combined run; this is not a full-suite count. Lint passed.
- [Actual GPU execution](isolated_scene_prefix_v1/actual_hardware_v2.json).
- [Frozen observer/parser/test snapshot](observer_parser_source_snapshot_v1/) and [owned-file patch](observer_parser_patch_v1.diff).

The original executed 2418 producer’s 289 recorded source files were rehashed unchanged. Original annotations, checkpoints, complete neural runs, failed outer analysis, historical matrices, and old diagnostic attempts remain preserved. Root owns codec24/source-history integration, versioning, broad tests, and any fresh end-to-end regression. No commit or aggregate accuracy claim is made here.

## Separate contact and rally findings

The newly missed short interval 11700–11760 remains an unresolved end-to-end result. Current activity starts at 11716 and has later contacts at 11731 and 11740, but the exchange fails the unchanged short-duration admission policy because qualifying opposite-player evidence is absent. The former contact at 11715 changes from score 0.9054 to 0.2824, below the unchanged 0.35 cutoff. Factorial score probes isolate the large change to an unstable low-speed incoming heading; incoming directional support is zero in both arms. Physical impact remains ambiguous, so restoring that candidate solely to improve interval F1 is unjustified.

Existing motion-reliability scoring suppresses some unsupported headings but also removes other source-reviewed contacts in the bounded controls. It has not been adopted as the default. An activity-departure witness and targeted fresh perception are proposals requiring their own evidence and negative controls, not implemented fixes in this candidate.

The generated reference’s early start near frame 809 is also not independent in-play truth. Source review shows pre-serve motion there, while frame 904 aligns with visible service and the coarse 900–1080 interval. Changes to static background inputs can affect TrackNet outputs after true content edits, but no safe background-carry correction or physical recall gain has been established. The new scene correction must therefore be judged using full preserved metric populations and source review, not by selectively restoring old generated-reference timing.

Physical AP, player identity accuracy, contact accuracy, stroke accuracy, and shuttle accuracy remain unavailable where independent ground truth is absent. Raw predictions and diagnostic agreement are not substituted for such truth.
