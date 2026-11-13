# Independent scene-overlap regression review

Two retained source pairs independently show abrupt same-camera edited jumps: Test2 frames2927→2928 and11081→11082. The current native run keeps its content epoch unchanged at both transitions. This is a real lost scene-boundary control; successful recovery of the nine other selected edits does not erase it. Physical labels remain null and no exhaustive cut precision/recall is inferred.

The current packets contain **two admitted persons** at2928 and11082. Their additional old rectangles are image-only foreground context: three foreground regions at2928 and four at11082. They must not be described as three/four admitted athletes or as an admitted stale person at2928.

[Original source pairs](source_pairs.png), [retained packet readout](actual_contract_readout.json), [input bindings](input_binding.json). Producer2418ab8cbe4cca74dd16b722b9727ffdc950294a remains unchanged. This review verifies selected closed renderer artifacts and deterministic mask geometry; it performs no flow replay or inference.

## Exact observed behavior

| Transition | Source diagnostic | Preserved baseline epoch | Current epoch | Current persons / foreground |
|---|---|---|---|---|
|2927→2928|Near red athlete relocates from central bent posture to left/back running posture; far blue athlete also changes position and stance abruptly. Display5:5 stays unchanged.|3→4 barrier|6→6, no retained scene evidence/decision|2 /3 at2928|
|11081→11082|Near blue and far red athletes both relocate from left-side walking/pickup to central active positions. Current-game display4:0 stays unchanged.|12→13 barrier|19→19, measured raw false and no decision|2 /4 at11082|

Unchanged broadcast digits do not disprove an edit. These source checks do not assert that the edit starts a new point, identify an actor, or provide a class/contact label.

## Confirmed11082 software gate

Both current prior regions have ample flow features, existing correspondence ratios above3, and joint mean discontinuity above the existing15intensity floor:

| Prior region | Features | Previous mean | Current discontinuity / ratio |
|---|---:|---:|---:|
|court-origin:55|28|0|20.2865653|
|court-origin:58|44|0|26.8156799|

Mean23.5511226passes the strong intensity gate; background80features/consistency1passes. The explicit previous means of0are valid history, with the existing denominator floor1. **The zero previous mean is not why these witnesses fail.**

`independent_scene_witnesses` removes every eligible rectangle intersecting any other eligible rectangle. These two prior boxes intersect over approximately30.946×60.102original analysis-image pixels. Both are removed. The same whole-box veto is reused for the one-region acquisition and two-region relative cohorts, leaving all witness-key lists empty. `acquire_layout` is therefore false and the current detector-layout corroboration is not requested through this route.

At the existing480×270observer raster, full masks contain1044and2074pixels, with299shared origin pixels. Subtracting the other region would leave745and1775exclusive origin pixels. This is geometry only: no claim is made about feature sufficiency, innovation magnitude, history or recovery under those proposed masks until the component agent's chronological actual-pixel prefix probe completes.

For2928, `cc=None` means raw observer output was not retained at this nondiagnostic frame, not that the observer did not execute. The pipeline calls the observer each frame and serializes only acquisition/hypothesis or selected diagnostic frames. Its missing acquisition cause requires the separate chronological prefix recovery; it must not be invented from the absent serialized field. Additional lost cuts22416/23279 remain in the other agent's proof/source review scope.

## Smallest reusable remedy worth controlled testing

Instead of declaring every pair of intersecting boxes unusable, measure each previous region only from **exclusive feature-origin pixels**: its rasterized ROI minus the union of all other prior ROIs. Preserve the original full rectangles for layout, foreground memory and raw provenance. Keep background sampling outside the union of the full original rectangles. Keep at least two independently qualifying same-channel region witnesses, existing feature/history/ratio/intensity limits and detector-layout corroboration.

This removes shared origin pixels without selecting the best overlapping person or choosing a favourable sub-pair. Exact duplicate boxes then have no exclusive support; an entirely nested ROI has no exclusive support; one surviving outer ring cannot supply a two-region quorum. Fully occluded or featureless exclusive masks remain unknown. Four-player doubles can use all bounded regions rather than truncating to two. Bounded overflow still abstains.

This is a new measurement policy, not a numeric reinterpretation of the old whole-rectangle measurements. Every actual-pixel/history prefix must be recomputed under it; it is invalid to retain old flow numbers and merely permit their intersecting boxes to count twice.

## Important contract and measurement caveats

- Exclusive seed masks do not guarantee disjoint Lucas–Kanade photometric patches. The existing21×21pyramidal windows extend beyond the seed mask. Describe distinct feature-origin support precisely; do not claim statistical independence or calibrated scene probability. A cross-boundary repeated-corner control should be measured.
- Rasterization must be deterministic and shared by observation and structural verification: actual analysis width/shape, scale, integer lower/ceiling upper bounds, clipping and all prior regions. Per-region exclusive mask areas/digests can bind this basis without persisting large bitmap arrays. A forged area/digest or omitted competing ROI must fail.
- The background mask must exclude full original regions, not only exclusive remnants; otherwise shared athlete pixels contaminate the supposedly reliable background.
- History represents the new mask policy from its first pair. Changing overlap geometry can change the sampled appearance distribution. Preserve unknown on missing support and quantify dynamic-occlusion controls rather than weakening history requirements.
- Keep full ROI geometry in layout matching. A current positive complete injective correspondence remains a veto; many-to-one and incomplete geometry remain unknown. Do not equate raw IDs with physical continuity.
- Weak complete-replacement policy deliberately rejects a retained old/current correspondence. If a new masked strong witness still fails its unchanged floors, do not silently weaken weak-reset policy merely to recover one remaining cut. That is a separate evidence problem.

## Required source, schema and regression gates

A new scene measurement-basis/version must identify the changed mask policy and actual observer geometry. OldV4packets retain strict historical overlap exclusion; an omitted, unknown or downgraded basis must not acquire new authority. Native raw parser must recompute quorum membership under the declared basis; typed detector decision and native completed-cache decoder must bind the same source/frame/region keys/geometry/format. Update relevant provider/model/stage/pipeline/cache identities and preserve old artifact decoding diagnostically. Do not relabel old raw values as new measurements.

Focused controls should cover identical/nested/partially overlapping ROIs; shared-pixel/feature manipulation; absent/invalid shape; forged mask basis/areas; duplicate keys; overflow; unknown background/features; zero valid history; missing/cold history; channels with one witness each; full injective normal correspondence and many-to-one ambiguity. Singles and doubles must both retain their explicit format/capacity contracts.

Actual-pixel controls must include all four lost edits2928/11082/22416/23279, preserved6151/6307and nine weak resets, foreground lease/ambiguity cases, ordinary lunge7703and bend23639, body overlap/occlusion, frozen/duplicate source frames, exposure changes and live featureless/unknown contexts. Compare full before/after source-bound prefix traces, not only cut counts or new person IDs. A full frozen-cache/fresh Test1/Test2 regression with unchanged original evaluators is required before acceptance.

No production change is recommended as accepted yet. This report establishes the source regression and11082whole-box veto, and defines the proof needed for a minimal reusable mask-policy experiment.
