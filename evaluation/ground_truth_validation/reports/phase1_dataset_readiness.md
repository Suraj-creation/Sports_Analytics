# Phase 1: dataset understanding and Test 1 baseline readiness

Phase 1 is complete for the available files. The new full Test 1 baseline has started; diagnosis, controlled fixes and regressions are subsequent gates, not completed claims.

## Inventory and source pairing

- 62 original files inspected: 48 CSVs, 8 court JSONs, 4 reference DOCX documents and 2 supporting repository files. Every file is hashed and every CSV has column-level coverage/distribution profiles.
- The supplied Drive folder was listed live. It contains videos for Tests 1–7, 9 and 10. No Test 8 video was found. Local annotation directories exist for Tests 1–4, 6–7, 9–10; Tests 5 and 8 remain missing, not skipped or reported as evaluated.
- Test 1's retained original matches the supplied object ID and historical source SHA256. Reuse avoids a duplicate large download; original bytes are untouched.
- All 56 CSV/JSON files are explicitly mapped in the [evaluation manifest](../dataset_inventory/evaluation_manifest.json).

## Annotation contracts and exact problems

- Coarse Full.csv references have documented human origin, but no complete per-row review/correction ledger. All 425 nonblank time spans are preserved separately from 15 blank rows and 416 generated rally intervals.
- Win-prediction files are legacy ML/rule outputs; their accumulated scores come from predicted winners. All 416 interval pairs equal their generated rally source. These are disagreement baselines, not independent winner/score ground truth.
- Test 1 Full2 contains 20 valid mixed records and a literal ellipsis at source row 21; it covers only part of the video and conflicts with primary semantics/scores. No full-match false-positive denominator is justified.
- Test 3 source row 6 contains 7 cells under an 8-column header; row 9 has a leading-space winner value. Do not guess the missing field or silently normalize source strings.
- Test 7's opening winner disagrees with its supplied score under the declared opening-score diagnostic. Tests 2 and 4 have 26 and 20 non-unit adjacent score transitions. Edited points, resets and annotation problems must be distinguished by source review.
- Player tables export detector-ordered bottom-center points and confidences, not boxes, joints or persistent physical identities. AP/mAP, IDF1/HOTA and PCK/OKS require labels the files do not contain.
- Shuttle tables are generated/filled estimates with missing interpolation provenance; visible low-confidence and out-of-bounds points are retained as cases, not clipped or promoted to reviewed coordinates.
- Six courts explicitly declare manual provenance; Tests 6 and 7 omit it. All are frame-specific 1280×720 geometry. Test 1 court frame 8634 requires visual verification of singles/doubles line correspondence before measuring geometric error. No reference court is injected into automatic baseline calibration.

## Current execution and preservation

The current improved working-tree files match the former recorded 289 source/config/model-binding hashes. This establishes current source identity, not permission to substitute old inference. A fresh full-video SessionRunner baseline is running on GPU1, preserving actual optional-model degradation. The commit alone is insufficient to reproduce inherited uncommitted improvements: dirty patch, 71 authored-file backups, exact executed-source snapshot, config/model bindings, package versions and logs are retained.

[Actual execution state](../orchestration/status.json) and [Test 1 baseline artifact link](../test_01/baseline_v1/) are the progress entry points. Complete output resides outside the repository under the executor's existing safety contract and is linked into this workspace.

After strict original worker completion: full PTS/pixel verification, every-frame component analysis, legacy reference agreement, full diagnostic traces, synchronized failure packages, all-reference component evaluation, and actual analytics/highlight export. Diagnostic observation replay is identified separately from fresh neural inference. Raw original videos/annotations and all historical benchmarks remain untouched.

The central orchestrator will review these before making isolated fixes and running a new before/after regression. Test 2 must not start simply because Test 1 inference completed. Independent visual inspection remains diagnostic evidence, not a newly manufactured ground-truth label set.

## Detailed evidence

- [Full inventory](../dataset_inventory/README.md)
- [Component schemas and coordinates](../dataset_inventory/component_schema_analysis.md)
- [Outcome provenance and conflicts](../dataset_inventory/outcome_provenance_analysis.md)
- [Current pipeline and execution mapping](../dataset_inventory/current_pipeline_mapping.md)
- [Initial data-understanding gate](../dataset_inventory/phase1_review.json)

## Early source-image evidence

At source frame **8634 / 287.8 s**, the [synchronized court/player overlay](../test_01/diagnostics/annotation_visual_review/frame_08634_legacy_overlay.png) visibly shows scoreboard rows **AN S.Y. 20 / INTANON 20**. The nearby coarse row19 ends **10:9**, while Full2 row19 ends **9:10**. These tables cannot be assumed to carry synchronized absolute broadcast scores; edited/selected-rally accumulation and annotation conflicts must be resolved before an accuracy claim. This is a specific observed disagreement, not a reason to silently change any supplied score.

The marked court corners align with **singles sidelines**, not automatically outer doubles boundaries. A homography comparison must use matching physical court coordinates; comparing this reference to a doubles-width template would invent a calibration error. The original JSON remains untouched. The player overlays are spatially plausible at the declared image size, but detector slot numbers change near/far ownership and are not permanent named identities. These visual observations are diagnostic context, not newly certified ground truth.
