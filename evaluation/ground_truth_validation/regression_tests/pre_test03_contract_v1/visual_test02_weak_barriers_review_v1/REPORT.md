# Independent Test2 source review: nine weak scene resets

All nine selected weak-reset contexts show an abrupt same-camera edited jump in the source sequence. The native current run returns two fresh visible-athlete boxes at each reset, instead of retaining the old scene positions. These are agent-reviewed diagnostic findings; physical ground truth remains **null**. Nine selected supported cases are not a precision/recall estimate.

## Bound evidence and scope

The current producer is `2418ab8cbe4cca74dd16b722b9727ffdc950294a`; baseline is the preserved Test2 `improved_v1` full run. The source SHA is `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`. The [original sealed package](../visual_test02_weak_barriers_v1/completion.json) binds actual worker, model, source, proxy, configuration and per-frame provenance. The worker processed all29296frames; the historical outer analysis failure is separate from this review and is not relabelled completed here.

Rehashed905 rendered outputs and1015 recorded input bindings (1010unique paths), plus225 source/proxy pixel receipts. Visually reviewed75 source-frame contexts across20 aspect-preserving sheets:225 source/baseline/current panels. The original package contains600PNGs; this review does not claim all600 were separately visually inspected. Source1920×1080 and overlay1280×890 images are scale-fit with letterboxing and never stretched to a common aspect ratio. No video re-decoding or inference was performed. [Verification](verification.json); [machine readouts](machine_readout.json); [structured review](review.json).

## Selected weak resets

Every listed current packet has raw `hypothesis=False`, validated `barrier`, an epoch increment of one from its previous frame, and two fresh persons. The raw false flag remains false; the typed weak acquisition proof supplies reset authority. Source relocation supports an edit rather than ordinary motion in these examples.

Broadcast numbers below are manually observed top-row:bottom-row rightmost/current columns, used only as corroborating source context. Historical game columns, named player identity, point attribution and winner correctness are not inferred.

| Frame / source time | Source change | Display before → after | Evidence |
|---|---|---|---|
| 355 / 11.833s | Near red athlete moves from bottom-left walk to near centre; far blue athlete relocates right. | 0:0 → 0:1 | [sheet](weak_00355.png) |
| 699 / 23.300s | Near red athlete relocates from right to centre and far blue athlete from centre to left. | 0:1 → 0:2 | [sheet](weak_00699.png) |
| 1095 / 36.500s | Near red athlete relocates right-to-left while far blue athlete relocates left-to-right. | 0:2 → 1:3 | [sheet](weak_01095.png) |
| 3394 / 113.133s | Red athlete outside right runoff and blue athlete near far/net middle abruptly become near-centre red and far-right blue. | 6:6 → 7:7 | [sheet](weak_03394.png) |
| 4581 / 152.700s | Both athletes relocate from left-side walking positions to central active positions. | 9:9 → 9:10 | [sheet](weak_04581.png) |
| 5958 / 198.600s | Blue athlete outside far-left and red athlete near-left abruptly relocate into central active positions. | 9:13 → 10:13 | [sheet](weak_05958.png) |
| 11691 / 389.700s | Near blue athlete relocates from left-side walk to centre; far red athlete relocates centre-to-right. | 5:1 → 7:1 | [sheet](weak_11691.png) |
| 11985 / 399.500s | Near blue athlete relocates from left-side bend to centre; far red athlete relocates centre-to-right. | 8:1 → 9:1 | [sheet](weak_11985.png) |
| 25521 / 850.700s | Near blue athlete changes from left-side bend/pickup to right-central position; far red athlete returns from far-left runoff to centre. | 14:15 → 14:16 | [sheet](weak_25521.png) |

## Controls and limitations

- **6151 (source_supported_edit):** Abrupt athlete relocation and displayed10:13 → 10:14; strong current barrier returns two fresh athletes; baseline retains three stale/official-position boxes. [Source/baseline/current sheet](control_06151.png).
- **6307 (source_supported_edit):** Abrupt relocation and displayed10:14 → 12:14; strong current barrier returns two fresh athletes; baseline carries prior three positions. [Source/baseline/current sheet](control_06307.png).
- **6492 (official_alias_countercontrol):** Source sequence is continuous play. Both arms have two fresh boxes, but baseline includes seated official and misses near red athlete; current boxes cover the two visible athletes. Counts alone hide the error. [Source/baseline/current sheet](control_06492.png).
- **7703 (ordinary_motion_no_reset):** Red athlete lunges during continuous play, display14:17 unchanged. Baseline raw hypothesis is vetoed by positive layout; current has no raw hypothesis/decision and carries two boxes without detector execution. No reset does not imply equal freshness or localisation. [Source/baseline/current sheet](control_07703.png).
- **11333 (additional_test2_context_only):** Test2 athletes walk outside on right; both arms admit one far red person, current also retains near blue scene context. This is not Test1 frame11333 and cannot validate its carried-lunge error. [Source/baseline/current sheet](control_11333.png).
- **11346 (source_supported_edit_full_history):** Abrupt relocation and current-game display4:0 → 5:1. Full-native current produces strong barrier and two fresh athletes; baseline has zero persons at11346 and11347. Earlier bounded cold-prefix unknown is a different history scope. [Source/baseline/current sheet](control_11346.png).
- **13153 (additional_test2_context_only):** Ordinary Test2 context with two persons and no reset. This is not Test1 frame13153 and cannot validate its raw shoe alias. [Source/baseline/current sheet](control_13153.png).
- **23639 (ordinary_motion_positive_veto):** Continuous bend/posture change, display9:15 unchanged. Both arms have raw hypothesis true and no_barrier positive layout; epochs remain stable. No shuttle/contact correctness follows. [Source/baseline/current sheet](control_23639.png).

**Plan scope correction:** the sealed frame plan combined previous carry/shoe rationale with Test2 frames11333/13153. Those numbers belong to different Test1 diagnostics. The rendered Test2 images are valid additional source context, but cannot validate the Test1 carried-lunge or shoe-alias findings. The original plan and artifacts remain unchanged.

The5958 source edit explains the historical official-context carryover in this selected sequence. It does not prove that a generic uninterrupted athlete-to-official handover is solved. Likewise, before3394 the source includes an off-court visible athlete while only one person is admitted; successful scene context is not universal player coverage.

## G69 remains unresolved

[Exit sheet](g69_exit.png), [lower return sheet](g69_reacquisition_01.png), [upper return sheet](g69_reacquisition_02.png) show the partial outgoing upper-edge object at27326–28, unobservable flight outside the image, the lower accepted racket-like branch at27348–53, and the bright upper return from27354. Both arms retain two persons and no scene reset in the15 selected frames. Their raw shuttle coordinates and support values are exactly equal on those15frames, including absence. This equality is scoped: only51/75 selected frame raw readouts are exactly equal overall.

The selected images do not establish22 physical false negatives, a continuous physical trajectory, a class/contact label, or current full FSM parity. No G69 repair is claimed. The earlier [source-bound gap diagnosis](../../../component_evaluations/pre_test03_shuttle_gap_v1/REPORT.md) and [exit-recovery contract audit](../../../component_evaluations/pre_test03_shuttle_gap_v1/exit_contract_audit_v1/REPORT.md) retain their distinct old-run scope.

## Acceptance boundary

These source controls support the selected scene-reset behavior and expose meaningful distinctions: official box versus athlete box, positive layout veto versus absent observer evidence, full-history versus cold-prefix behavior, and visible alias versus outside-image uncertainty. They do not establish physical tracking AP, named identity, winner accuracy, contact precision or stroke correctness. Full numeric evaluation, immutable-artifact verification and any final pipeline acceptance remain separate.
