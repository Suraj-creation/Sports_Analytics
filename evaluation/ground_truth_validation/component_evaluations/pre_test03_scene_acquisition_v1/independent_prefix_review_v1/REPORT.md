# Independent review of the relative-acquisition prefix

The closed native prefix at **9992f87fc24c51da28ada77c07d15e9e18338232** restores all **182 saved missing-region boxes across seven intervals**, preserves the two sampled Test 1 edit barriers lost by the failed c7 control, and acquires three additional Test 2 edits at **355, 5958 and 25521**. This supports proceeding to full fresh regression; it does **not** establish full-pipeline preservation, physical player recall, identity accuracy, contact quality or acceptance of the candidate.

This is a read-only independent review of [the sealed prefix](../prefix_v2/artifact_receipt.json). No production, annotation, model, profile or historical evaluation was changed. No neural inference was run by this review. New panels at 6150/6151 were rendered from the preserved proxy and closed rows only. Earlier failed-prefix and c7 evidence remain untouched.

## Provenance and execution scope

[Verification](verification.json) checks all **92 sealed artifact hashes** and **274 recorded input hashes**, all 15 complete chronological case timelines, and the executed commit. The later observed HEAD `a14695372f0d66d0c80a0bbad8d2c63864001d95` changes five test files only; it is not the executed commit. Recorded production/model/config bytes still matched when reviewed.

[The independent source audit](source_pixels_audit.json) re-decodes **all 3,054 selected proxy frames** and checks exact CFR frame, rational PTS/timebase and BGR pixel SHA against every arm. These are the existing original-source-bound analysis proxies: Test 1 source SHA `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`, Test 2 source SHA `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`. It does not claim to have re-downloaded or re-decoded the absent original Test 2 video. [Decision binding](decision_binding_audit.json) independently verifies all **25 current layout decisions** against exact retained raw proposals translated by the recorded crop origin, their scores and full-image pixel identity.

The bounded worker recorded **289 fresh neural detector forwards**, with a CUDA-first ONNX session listing `CUDAExecutionProvider` and `CPUExecutionProvider`. A provider list does not prove every operation ran on GPU. The common bank contains 1,200 exact frame/crop observations, from retained seeds and actual forwards; all were consumed by at least one arm. Original, c7 and native current implementations query this common bank. Equal proposal identity at a given query does not imply equal query cadence.

These runs cover RFDETR/ROI/ByteTrack/content with the original recorded rate, geometry and format schedule. They omit pose, shuttle, semantic engine/FSM feedback, highlights and a complete fresh pipeline. Each prefix starts with cold component state. The footage is singles with confirmed/uncertain format context preserved; this is not a real doubles validation.

## All seven saved coverage losses

[Every saved row](coverage_all182.json) is compared to the unchanged c585 gross-loss ledger at the same source frame. Diagnostic matching uses bbox IoU ≥0.5. Every current match actually has **IoU 1.0**. These targets are prior model boxes, not independent physical bounding-box annotations; the table is conditional restoration, not AP or physical recall. Source panels were visually inspected for each group.

| Test 1 interval | Rows | Original matches | Failed c7 matches | Current matches | Fresh / carried current matches | Source example |
|---|---:|---:|---:|---:|---:|---|
| 753–800 | 48 | 48 | 0 | 48 | 24 / 24 | [753](../prefix_v2/test1_00700_00820_frame_00753.png) |
| 3413–3449 | 37 | 37 | 0 | 37 | 18 / 19 | [3413](../prefix_v2/test1_03330_03470_frame_03413.png) |
| 6365–6381 | 17 | 17 | 0 | 17 | 8 / 9 | [6381](../prefix_v2/test1_06280_06400_frame_06381.png) |
| 7801–7805 | 5 | 5 | 0 | 5 | 0 / 5 | [7801](../prefix_v2/test1_07650_08150_frame_07801.png) |
| 7812–7856 | 45 | 45 | 0 | 45 | 8 / 37 | [7856](../prefix_v2/test1_07650_08150_frame_07856.png) |
| 8087–8105 | 19 | 19 | 0 | 19 | 9 / 10 | [8087](../prefix_v2/test1_07650_08150_frame_08087.png) |
| 14103–14113 | 11 | 11 | 0 | 11 | 5 / 6 | [14103](../prefix_v2/test1_14000_14150_frame_14103.png) |
| **Total** | **182** | **182** | **0** | **182** | **72 / 110** | |

The restored boxes follow the visible near athlete in the first two groups, the white-clad athlete outside the right/net area at 6381, the far athlete at 7801/7856, the near athlete at 8087, and the departing dark-clad athlete at 14103. Cyan outlines can obscure a coincident person outline; row-level matches and fresh/carried flags resolve that display ambiguity. Cyan means detached image context, not participant, named identity, score or ground-truth authority. Carried boxes remain tracker estimates. Private anchor-age state is not included in the prefix person rows; its renewal policy is a source/unit-test claim, not a directly measured age series here.

## Edit acquisition and controls

All seven native barriers are listed below. The observed source relocations are agent visual diagnostic expectations; physical scene ground truth remains null. Score changes alone were not used to infer edits.

| Test / frame | Original barrier | c7 barrier | Current barrier and route | Independent source observation |
|---|---|---|---|---|
| 1 / 7857 | yes | no | yes, strong | [Current athletes](../prefix_v2/test1_07650_08150_frame_07857.png) replace the prior layout; c7 retains a box on empty near-right court. |
| 1 / 8106 | yes | no | yes, strong | [Current layout](../prefix_v2/test1_07650_08150_frame_08106.png) is freshly reacquired; no barrier was emitted by c7. |
| 2 / 355 | no | no | yes, relative replacement | [354](../prefix_v2/test2_00300_00365_frame_00354.png) to [355](../prefix_v2/test2_00300_00365_frame_00355.png): athletes reposition in one frame; current returns two fresh boxes instead of stale offcourt/empty boxes. |
| 2 / 5958 | no | no | yes, relative replacement | [5957](../prefix_v2/test2_05505_06510_frame_05957.png) to [5958](../prefix_v2/test2_05505_06510_frame_05958.png): both athletes relocate from left areas to central court in 1/30 s. The original arm instead returns the seated official. |
| 2 / 6151 | no | no | yes, strong | [6150](test2_frame_06150.png) to [6151](test2_frame_06151.png): both athletes relocate; current reacquires both while the controls keep empty-position boxes. |
| 2 / 6307 | no | yes | yes, strong | [Current frame](../prefix_v2/test2_05505_06510_frame_06307.png) returns both athletes; original retains incorrect old positions and an official. |
| 2 / 25521 | no | no | yes, relative replacement | [25520](../prefix_v2/test2_25206_25540_frame_25520.png) to [25521](../prefix_v2/test2_25206_25540_frame_25521.png): left-courtside athletes relocate centrally; current returns fresh boxes instead of empty left-position boxes. |

At 5958 the raw strong hypothesis is false. The current decision separately binds two relative witnesses, known participant count 2, exactly two strict-current-court boxes, all five raw proposals, camera alignment and no complete old-layout correspondence. Inherited admission includes the official before reset; it is not used as strict court membership. After the reset, only the two current athlete boxes are returned. Thus one static outside official matching one prior region no longer suppresses acquisition; a complete positive raw-layout match still vetoes reset. This preserves the absolute strong floor rather than lowering it to fit this edit.

At [6492](../prefix_v2/test2_05505_06510_frame_06492.png) the original arm has two fresh boxes but one belongs to the official and the near red athlete is absent. c7 and current show the two athletes. Counting boxes alone would conceal that failure. The historical handover started across the missed 5958 edit; these panels do not prove a continuous physical athlete-to-official identity handover in an unedited scene.

No other native barriers appear in the 15 selected windows. There are 17 relative acquisition decisions without a complete replacement and one complete-current-layout correspondence veto. The visible lunge at [7703](../prefix_v2/test2_07640_07740_frame_07703.png) and the [23639](../prefix_v2/test2_23570_23680_frame_23639.png) control produce no current barrier. These are selected controls, not an exhaustive false-reset rate. Only the two sampled Test 1 original barriers were executed here; preservation of all 13 historical full-video cuts still needs the full fresh run.

## Remaining limitations and cadence audit

At [Test 1 frame 11333](../prefix_v2/test1_11240_11360_frame_11333.png), the near athlete lunges beyond the carried box. Both c7 and current return the same lagging near estimate, with `detector_executed=false`, `detector_matched=false` and no barrier. The original prefix returns only the far athlete then. Restoring the missing person population does not solve detector scheduling/carry localization.

At [Test 2 frame 11346](../prefix_v2/test2_11300_11360_frame_11346.png), current returns two fresh athletes but scene evidence remains `unknown` with `two_to_four_prior_regions_required`, and no barrier. This cold-prefix result has insufficient prior context for the scene policy; it must not be reported as a proven full-timeline fix or an annotation error.

[Cadence audit](cadence_audit.json) uses current-frame `tracking_diagnostic.frame_idx` plus `detector_executed`, giving **1,187 original**, **1,187 c7**, and **1,199 current** execution rows. Current adds 13 frames and omits original frame 7703, net +12. Acquisition-triggered calls can shift subsequent cadence. These execution rows include shared/seed replay consumption, not 1,199 new neural forwards.

The initially recorded `verification.json.per_arm_detector_observed_frames` counts 1,200/1,200/1,212. Those are sticky-property sums and are **not actual execution counts**: frames 801–813 in an off-main span carry stale `detector_observed=true` while processing was skipped, persons are empty and tracking diagnostics are absent. All 39 records are preserved in the audit. This is a prefix reporting caveat; the sealed worker artifacts were not rewritten and no production behavior was changed to repair the counter.

Full fresh Test 1 and Test 2 runs, native completion/cache/PTS guards, unchanged evaluation methods, interval/component matrices, semantic effects and source visual comparisons remain required before candidate acceptance. Contacts/classes/outcomes, player identity, exhaustive false positives and doubles accuracy remain unsupported by this bounded prefix. **Physical ground truth and physical accuracy metrics: unavailable, not zero.**
