# Test 2 V5: source-confirmed shuttle branch regression

**The current5ae run selects a static floor mark while a separate airborne object is visibly present.** Frame23542 gives the clearest direct evidence: source shows a small bright moving object above the far background signage, consistent with the airborne shuttle, near the2418 upper trajectory. Current instead selects approximately `[572.53,439.64]` canonical pixels, corresponding to the fixed white HSBC floor-logo triangle at approximately `[859,659]` original pixels. No transient shuttle is visible at that floor mark. This is a source-supported perception/association regression; it is not inferred solely from disagreement with a generated CSV.

All ten contiguous frames **23534–23543** were reviewed as original source, actual secondary2418 overlay and actual current5ae overlay:30panels on four aspect-preserving sheets. Selected full1080p source frames23534/23538/23542 were also inspected. Both exact producers and completed runs remain distinct; this comparator is2418, not originaldacc. Source is continuous within this window, following the earlier recovered real edit at23279. No additional source edit is visible here.

The [fixed-region source sequence](fixed_source_regions.jpg) shows two different physical structures. In the upper crop a small bright object becomes clearly separate from the advertising print at23537 and progresses upward through23543. In the lower crop the same printed floor-logo triangle persists throughout, with no corresponding moving object. The upper branch at23534–23536 overlaps high-contrast advertising text, so those early exact object centres cannot be independently localized confidently. This qualification does not make the current floor-logo branch valid, and the direct23542 distinction remains clear. Crops have fixed source-coordinate bounds, rather than following a prediction and artificially cancelling motion. Twenty native-resolution crop PNGs, their pixel hashes and display policy are retained in [crop bindings](source_crop_bindings.json). Nearest-neighbor display enlargement adds no source information and creates no GT points.

## Actual raw and association behavior

The current model supplies **both peaks above the unchanged0.5 inference threshold in all ten frames**. Its raw maximum selects the floor-logo mode at23534,23535,23536 and23542; it selects the upper branch on the other six. The upper candidate was therefore available even on the bad selection frames. For23542, floor support0.662598 narrowly exceeds upper support0.656738. The accepted raw coordinate jumps398.713px relative to2418's `[767.938237,92.101965]`, rather than representing a subtle subpixel localization change.

Crucially, association does not reject the bad floor observation in these four frames. It records `status=observed`, `association_status=tracked`, the same selected lower coordinate and reason `fresh_selection_retained`. Thus the wrong raw branch reaches the accepted perception stream. This is not an example of a safe raw false peak already withheld by postprocessing. The stationary mode also remains a strong second candidate when the visible upper branch wins, giving explicit competing-mode evidence across the sequence.

| Frame | Upper support / rank | Floor support / rank | Current selected branch | XY delta vs2418, px |
|---|---:|---:|---|---:|
| 23534 | 0.619141 / 2 | 0.662598 / 1 | floor logo | 344.216738 |
| 23535 | 0.598145 / 2 | 0.638184 / 1 | floor logo | 358.083192 |
| 23536 | 0.641602 / 2 | 0.646973 / 1 | floor logo | 358.127673 |
| 23537 | 0.690430 / 1 | 0.659180 / 2 | upper branch | 0.003196 |
| 23538 | 0.679199 / 1 | 0.657715 / 2 | upper branch | 0.000839 |
| 23539 | 0.706055 / 1 | 0.658203 / 2 | upper branch | 0.001486 |
| 23540 | 0.658691 / 1 | 0.647461 / 2 | upper branch | 0.000946 |
| 23541 | 0.683105 / 1 | 0.644043 / 2 | upper branch | 0.001123 |
| 23542 | 0.656738 / 2 | 0.662598 / 1 | floor logo | 398.708553 |
| 23543 | 0.699219 / 1 | 0.637695 / 2 | upper branch | 0.477624 |

These are uncalibrated model support values and recorded candidate ranks, not probabilities of physical truth. The four floor selections are measured examples in this deliberately selected window, not a video-level error-rate denominator. The source diagnosis does not manufacture localization labels, contact labels, per-frame TP/FN counts or AP. Exact values, selected coordinates and association reasons remain in [branch comparison](branch_comparison.json) and [raw frame register](frame_register.json).

## Engineering implication and limits

A confirmed reusable failure is present at the candidate-selection/association boundary: a persistent static background mode can beat the available moving-object mode and be published as tracked. The changed heatmap modes are measured; their precise neural input/state cause has not been isolated by this review. The recovered scene epoch can alter TrackNet temporal/background state, but no background-only or temporal-only neural ablation was performed here. It would be premature to attribute the failure exclusively to one bank update or to prescribe background carry across arbitrary cuts.

Further design must preserve the actual competing candidate/support history and uncertainty, and test generic stationary-background versus moving-object controls. A future fix must also preserve genuine held/slow shuttle, low-motion/net cases, occlusion/reacquisition, same-camera edits and actual camera/light changes. Hard-coded logo coordinates, branding masks, video-specific thresholds or treating the old generated reference as physical GT would not establish such a fix. No correction, threshold adjustment or model run is adopted in this source review.

## Evidence verification and preservation

The frozen renderer passed genuine full worker/parent/catalogue, source/model and timestamp guards. **153 artifact hashes,1,014 input bindings and30 source/proxy pixel/shape receipts** verify, including rational PTS equality and original/frozen cache identities. All20native crop PNGs were checked against their exact source pixel subarrays. Source SHA256 is `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`. See [verification](verification.json), [closed source bundle](../visual_test02_v5_shuttle23534_23543_v1/index.md), [23534–23536](sheet_01.jpg), [23537–23539](sheet_02.jpg), [23540–23542](sheet_03.jpg) and [23543](sheet_04.jpg).

Physical ground truth remains null. Original videos, annotations, benchmark scores, completed caches and previous reports remain untouched. No NN inference, production/source/profile edit, metric recomputation or final acceptance/merge occurred. This newly confirmed source failure remains a blocker for the parent orchestrator's acceptance decision until explicitly addressed or scoped.
