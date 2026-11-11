# Test 2 player-point outliers: source-bound diagnosis

This is an agent qualitative review of **six selected source/proxy frames**, not independently adjudicated player boxes/IDs, AP/mAP or physical localization accuracy. No pipeline fix, inference, matching cutoff or annotation edit was performed. The fresh baseline remains unchanged.

## What the aggregate hides

The preserved bound component matrix reports anonymous bottom-center disagreement over57,305pairs: **mean3.461802px, median1.572611px, max429.411529px**, p95=11.764085px. On24,129fresh-detector matched pairs, mean1.678630px, median1.117645px, the same maximum429.411529px. These compare current predictions against legacy generated bottom-center points, not reviewed physical truth. A fresh match means the current box has a current detector observation, not that it belongs to a target athlete.

[ranked_outliers.json](ranked_outliers.json) ranks the maximum all-current assignment distance per **distinct frame**, retaining the top30 and the source candidate-file SHA. The absolute top3 frames6492,6493,6494 are one contiguous failure; they must not be counted as three independent failure types. We inspected those plus ordinary control300 and distinct high-disagreement episodes355/25521.

| Frame | Seconds | Current detector match | Pair disagreements, px | Inspected classification |
|---|---:|---|---|---|
| 6492 | 216.400000 | Both true | **429.411529**,0.215038 | Background official admitted as player; near athlete missing |
| 6493 | 216.433333 | Both false | **425.195259**,1.588730 | Same wrong population propagated |
| 6494 | 216.466667 | Both false | **420.349693**,1.271826 | Same wrong population propagated |
| 355 | 11.833333 | Both false | **403.540233**,55.969865 | Propagated boxes drift away from both visible athletes |
| 25521 | 850.700000 | Both false | **364.873591**,308.521084 | Two propagated boxes over empty left courtside/background |
| 300 | 10.000000 | Both true | **2.388207**,1.509091 | Both current boxes and legacy points plausibly align athletes |

## Exact media and cache evidence

The original source SHA256 is `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`; actual analysis proxy SHA256 is `2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd`. Both entire files were rehashed against the completed inference receipt. Every requested frame was decoded with PyAV by backward keyframe seek, then accepted **only if decoded PTS×timebase equalled frame/30 exactly**. Source frames are1920×1080, resized by `INTER_AREA` to1280×720; actual proxy frames are natively1280×720. Source/proxy pixel hashes and individual PTS are retained separately; compression differences are not falsely described as identical pixels.

Each selected closed msgpack segment was verified against the original completion catalogue and copied by SHA256 into `cache_snapshots/`. Each frame folder contains source and proxy PNGs/overlays, the exact comparison row, complete current perception frame and an evidence receipt binding cache/model/source/panel hashes. [extraction_manifest.json](extraction_manifest.json) binds all selected evidence and the completed catalogue/candidate files. No live database was opened.

The exact executed extraction source is [extract_player_outliers.executed.source](extract_player_outliers.executed.source), whose SHA matches the extraction manifest. The maintained `.py` helper was subsequently formatted/linted without rerunning inference or changing saved images. Keep the executed snapshot when reproducing this immutable extraction.

## Confirmed observations

### 1. Frame6492: detector-fresh background person, not a target athlete

Both [source overlay](frame_06492/source_overlay.png) and [actual proxy overlay](frame_06492/proxy_overlay.png) show the far blue athlete and near red athlete in the normal main court view. Current index0/track8 box **(545.809,233.310)–(636.687,370.534)** follows the far blue athlete; its bottom-center **(591.248,370.534)** agrees with legacy slot2 **(591.192,370.327)** within0.215px.

Current index1/track0 box **(447.318,153.195)–(484.898,206.195)** surrounds the seated dark-clothed **background official above the far baseline**, not either court athlete. It is explicitly `detector_matched=true` and `detector_observed=true`. The real near red athlete is visible around legacy slot1 **(627.424,604.154)** and has no corresponding current person row. This is a confirmed **current target-person population/admission failure** on the inspected source. A generic person detector may correctly detect the official as a person; the analytic error is treating that person as a target player while omitting the visible near athlete.

The minimum-cost anonymous assignment preserves the excellent far match, then necessarily pairs the remaining near-player legacy point with the official's bottom-center **(466.108,206.195)**. That forced pair produces429.411529px. It does not mean one physical athlete's foot was measured429px incorrectly. The final supplied-current population has the wrong semantic member, and the comparator has no independently labelled target-person validity/negative set.

This cache does not preserve every original raw detector proposal at this exact frame. It therefore cannot establish whether the near athlete was missed by the neural detector, lost during tracker association, or excluded by a later selection/filter stage. Trace detector proposals, court admission and tracker links before naming a precise code cause. Do not fix this by fitting a distance cutoff to these rows.

![Background official replaces near athlete](frame_06492/proxy_overlay.png)

### 2. Frames6493–6494: propagation retains the bad population

[Frame6493](frame_06493/proxy_overlay.png) and [frame6494](frame_06494/source_overlay.png) keep the same two current boxes bit-for-bit, now with `detector_matched=false`, while athletes move slightly. The background official remains included and the near red athlete remains absent. Legacy points continue to lie plausibly near both athletes. This is the same failure sustained on non-detection frames, not a new identity-switch count or three separate model false positives.

All three frames are `view=main`, `calibration=VALID`, content epoch8 and an identity camera transform. Correct scene/calibration labels alone do not establish correct person selection. Source/proxy exact-time review and the simultaneous0.215px far match rule out a global coordinate rescale/time shift as a useful explanation for the429px near pair.

### 3. Frame355: propagated motion is visibly inconsistent with the image

In [source](frame_00355/source_overlay.png) and [proxy](frame_00355/proxy_overlay.png), both real athletes remain visible around legacy points **(620.629,543.237)** and **(733.580,374.761)**. Current track0's propagated box lies around the empty left courtside at **(235.176,484.886)–(274.946,714.130)**, and track1's box is shifted left/up relative to the far blue athlete. Both are unmatched/propagated, despite main-view/VALID state and identity camera transform. The near paired distance is403.540px and far55.970px.

This is a confirmed current propagated-box alignment failure in the inspected image, not merely a legacy player-slot swap. A single frame cannot establish the first wrong tracker update, detector cadence cause, camera-cut history or recovery duration. Current `pose_frame=355` on those boxes indicates same-frame pose execution on propagated boxes; it does not prove pose-to-athlete association accuracy.

### 4. Frame25521: propagated boxes cover empty background

[Source](frame_25521/source_overlay.png) and [proxy](frame_25521/proxy_overlay.png) show the near blue and far red athletes near legacy points **(718.253,570.710)** and **(632.640,387.353)**. Both current boxes sit well to their left over empty courtside/background, with `detector_matched=false`, distances364.874px and308.521px. This is another confirmed current alignment failure. Its main-view/VALID flags and identity camera transform do not explain it away as a different coordinate basis.

### 5. Control300 supports the general source/coordinate pairing

[Control source/proxy overlay](frame_00300/proxy_overlay.png) shows current boxes around both athletes and legacy bottom-centers near their lower box boundaries. Distances2.388px and1.509px are plausible agreement between two detectors. This control and exact PTS binding support the general video/annotation pairing; they do not certify every legacy value or turn the whole dataset into physical GT.

## Population and matching interpretation

The inspected6492–6494/355/25521 rows have two current and two legacy points, so the issue is **wrong semantic population despite equal counts**. Hungarian assignment pairs the smaller population exhaustively without a physical validity gate. Supplementary top-ranked **row-only, not visually inspected here** examples5958,6152,6308 have only one current person, the same track0 near(466,206), versus two legacy points. Their203–230px forced matches and unmatched legacy point counts describe a partial/mismatched population, not reviewed FP/FN or point error for a known athlete. Frame6024 additionally pairs the same official while correctly matching one real near athlete. Preserve these candidates for continuous review; do not silently delete their difficult cases.

No selected source review established that a legacy point is the cause of these largest errors; those legacy points are qualitatively plausible at these instants. That bounded observation does not validate all29,296legacy frames. Pose/keypoint GT, exhaustive target boxes, persistent identities and independent negative labels remain absent. The current matrix must retain its **generated-output disagreement** classification, all unmatched counts and freshness distinctions.

## Next bounded investigation, without blind fixes

1. Trace current detector proposals, matched/unmatched assignments and target-court admission around5958–6497, especially the recurrent small background-official box and the first lost near-athlete observation. Preserve current component thresholds; distinguish person detection from target-player membership.
2. Inspect preceding fresh detections and propagation updates around355 and25521. Determine whether extrapolation, association, cadence/recovery or scene-transition history first diverged; look at complete windows, not only the peak pair distance.
3. Build independently reviewed target-person boxes/visibility and negative examples for these windows plus ordinary controls and doubles/occlusion/adjacent-court cases before AP, recall or tracking-ID accuracy claims. Keep new reviews separate from originals and generated predictions.
4. Evaluate any verified fix as another controlled intervention with before/after Test1/Test2 regressions and fresh perception when person selection changes. The existing engine-only racket-admission experiment does not claim to repair these player tracking/admission failures.
