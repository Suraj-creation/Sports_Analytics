# Minimal scene-feature-origin correction proposal

The four source-reviewed lost edits have overlapping *previous full boxes*. Current V4 discards every eligible region that intersects any other eligible box. At11082, both correspondence regions independently exceed the existing3× adaptive test and their mean discontinuity23.551 exceeds15; neither can reach strong, relative or even one-region acquisition because the box-intersection check removes both. Full-box overlap does not prove that the actual image feature origins were reused.

The detached actual-pixel prefix experiment replaces the region sampling masks with each original raster ROI minus the union of **all other prior ROIs**. The background still excludes the full original ROI union. It retains the existing optical-flow algorithm, feature minimum6, history length2, ratio3, strong mean-intensity15 and two-region same-channel requirement. It produces a strong raw hypothesis at2928,11082,22416 and23279. No production file or cached evidence has changed.

Call this **exclusive feature-origin masks**. LK21×21/pyramid tracking windows can extend outside their seed masks; these measurements are not calibrated or statistically independent photometric observations. They remain uncalibrated image hypotheses requiring the existing current-source detector/layout/camera corroboration. A new raw hypothesis at continuous control7703 must be vetoed by an actual positive current layout, or the proposal fails acceptance. Raw hypothesis recovery alone is not reset accuracy.

## Proposed production change, exclusively in the new isolated checkout

1. Add `SceneContinuityDetectorV5`, preserving old V2/V3/V4 measurement paths exactly. V5 computes all full-box masks first; each measurement mask retains only pixels covered by exactly one full ROI. Fully nested, identical or fully occluded boxes have empty exclusive masks and cannot supply feature witnesses. Do not erode masks or lower gates. Full boxes remain unchanged for player memory, court geometry and layout matching.
2. Add an explicit new raw measurement contract, `foreground-scene-hypothesis:v5`. Proposed new fields are `feature_origin_policy="exclusive_previous_roi_origins:v1"`, `source_frame_size`, `analysis_frame_size`, and ordered `origin_masks` records `{key,pixels,sha256}` for every measured prior region. Records include zero-area masks. Deterministic rasterization derives every mask from ALL previous full ROIs and those dimensions. The parser recomputes mask areas/digests and validates ordering, keys, dimensions and feature counts. Metadata cannot turn overlapping legacy V4 measurements into exclusive observations.
3. Strong and relative cohort functions may accept overlapping *full boxes* only after this V5 origin-mask binding has passed. Each channel still needs its own qualifying cohort; one appearance and one correspondence witness cannot be pooled. Legacy V4 and earlier keep their original strict box-overlap rule. Acquisition remains distinct from reset authority.
4. Use a new `detector-layout-scene-decision:v4` binding to rawV5. Keep all existing full-box IoU0.3, positive correspondence veto, camera alignment, strict court and confirmed-format gates. New decisions cannot pair with legacy raw measurements and new raw measurements cannot masquerade under old decisions. Unknown and partial doubles stay unknown.
5. Root integrates codec24/pipeline/content implementation versions and source-policy hashes after review. No original cache is retagged or rewritten. Existing historical raw/decision families remain readable and retain their exact old interpretation. The new source is distinct from frozen2418.

The new source/analysis dimensions must be bound by the native cache decoder to actual `ci.frame_size` and the producer's configured analysis width, not accepted as a free coordinate system. Mask digest correctness alone is not source-pixel truth; run/source hashes and actual current-source layout evidence remain mandatory.

## Required validation before adoption

- Exact native observer reproduction of retained source measurements after chronological warmup, with tuple/list wire containers normalized and no numeric tolerance relaxation.
- Four actual lost-edit prefixes, preserving current detector source and proving an actual barrier rather than only raw hypotheses.
- Continuous7703/23639 controls, source camera/pan/zoom controls, partial matching and one-region changes; every new raw request must receive fresh independent layout or abstain.
- Identical/nested/partially overlapping/full-overlap ROIs, static third/fourth regions, insufficient exclusive features, one-channel-only witnesses, changing ROI geometry/history, low-feature history and missing/future source flags.
- Singles and four-player doubles, confirmed and unknown format, forged mask area/hash/dimensions, source geometry and version downgrades. Old V4 caches must not acquire new authority.
- Broad tests plus Test1/Test2 comparable full regression. Changed epochs affect TrackNet's background/temporal inputs, so cached semantic replay alone cannot certify whole-pipeline equivalence.

No contact/launch, model threshold, interval matching, annotation or scoring changes are part of this correction. Contact11715 noise sensitivity and the conservative short-exchange issue remain separate, documented investigations.
