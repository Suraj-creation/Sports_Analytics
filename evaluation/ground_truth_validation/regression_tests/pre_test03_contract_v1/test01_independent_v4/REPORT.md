# Independent completed Test1 review — 2418ab8

**The full fresh run and its guards pass. All182 previously withheld image regions are restored, no original participant-count loss or scene-boundary regression is found, and all six interval detection matrices are preserved.** Source review supports the intended athlete restoration. This is a Test1 regression result, not final root acceptance, an all-video aggregate or independently measured physical accuracy.

The executed native checkout is `/home/administrator/Desktop/sport-analytics/test03-scene-evidence-contract-20261112`, commit `2418ab8cbe4cca74dd16b722b9727ffdc950294a`. The complete17,268-frame source uses1280×720 canonical images at30FPS. No pipeline, model, configuration, annotation, baseline or evaluation policy was modified during this independent review. No neural inference was run by the reviewer. The earlier incomplete a146953run remains a separate preserved failure.

## Completion and reproducibility

The actual native strict completion loader passed without rebasing an imported ROOT; its worker and parent completed fresh inference with own-run semantic parity. We rehashed3709 preserved completed artifacts and289 worker-plan source files. All94 protected inputs—including all62 original Part2 files by opaque hash only—are unchanged. The nine applicable Test1 annotation hashes match the preserved baseline, and the original six-reference baseline JSON is byte-identical. Seven evaluator/guard implementations retain their original hashes; matching and numeric thresholds were not changed.

The frozen source also has2,773 main tests and705 research tests passing:3,478 total, with702 source files unchanged in each suite. The actual model/configuration comparison passes; seven assets were additionally fingerprinted, including the pose ZIP container and its actual staged ONNX graph. RFDETR, RTMPose, TrackNet and all three package OCR weights retain the recorded hashes. OSNet and the optional racket neural model remain unavailable/not claimed loaded; no new model was adopted.

Evidence: [native guard](native_guard_receipt.json), [protected inputs](protected_inputs_review.json), [runtime/model/config/source records](runtime_provenance_review.json), [additional source/unit/model verification](additional_reproducibility_review.json).

## Six interval-reference matrices

Every row below has unchanged TP/FP/FN and precision/recall/F1 versus the stored original full-neural baseline. IoU changes are limited to one predicted start boundary. These are the existing coarse/generated/partial reference agreements; the filenames do not confer physical ground-truth status. Full2 contains partial positives, so false positives, precision and F1 remain unavailable rather than zero.

| Reference | Role | TP/FP/FN | Precision | Recall | F1 | Mean IoU before → fresh |
|---|---|---|---:|---:|---:|---|
| Test1_Full.csv | coarse_legacy_label_agreement | 36/0/0 | 1.000000 | 1.000000 | 1.000000 | 0.842130 → 0.842284 |
| Test1_Full2.csv | partial_mixed_label_candidate | 19/N/A/1 | N/A | 0.950000 | N/A | 0.846835 → 0.847138 |
| Test1_Full_rally.csv | legacy_generated_reference_agreement | 36/0/0 | 1.000000 | 1.000000 | 1.000000 | 0.871026 → 0.871185 |
| Test1_Full_rev_T.csv | legacy_generated_reference_agreement | 34/2/1 | 0.944444 | 0.971429 | 0.957746 | 0.867878 → 0.868047 |
| Test1_Full_rev_T4.csv | legacy_generated_reference_agreement | 36/0/2 | 1.000000 | 0.947368 | 0.972973 | 0.871026 → 0.871185 |
| win_predictions.csv | legacy_generated_reference_agreement | 36/0/0 | 1.000000 | 1.000000 | 1.000000 | 0.871026 → 0.871185 |

| Reference | Start MAE seconds before → fresh | End MAE seconds before → fresh | Duration MAE seconds before → fresh |
|---|---|---|---|
| Test1_Full.csv | 1.029630 → 1.026852 | 0.466667 → 0.466667 | 1.159259 → 1.156481 |
| Test1_Full2.csv | 1.098246 → 1.092982 | 0.433333 → 0.433333 | 1.064912 → 1.059649 |
| Test1_Full_rally.csv | 0.941667 → 0.938889 | 0.349074 → 0.349074 | 1.111111 → 1.108333 |
| Test1_Full_rev_T.csv | 0.893137 → 0.890196 | 0.388235 → 0.388235 | 0.910784 → 0.907843 |
| Test1_Full_rev_T4.csv | 0.941667 → 0.938889 | 0.349074 → 0.349074 | 1.111111 → 1.108333 |
| win_predictions.csv | 0.941667 → 0.938889 | 0.349074 → 0.349074 | 1.111111 → 1.108333 |

Only primary reference row19 changes: reference8106–8628; original prediction8111–8627; fresh8108–8627. Start error5→2frames, end error remains−1frame, duration error−.2→−.1s and rowIoU.988506→.994253. Every other predicted start and every predicted end remain unchanged. Primary meanIoU.871185 does not imply tight boundaries: start MAE remains.938889s, end MAE.349074s and duration MAE1.108333s; maximum start error remains3.533333s.

Full2 still misses its reference row5. The rev_T reference still has one miss(row5) and two unmatched predictions(rallies5and36); rev_T4 still misses rows2and8. The coarse, primary and win-interval references retain no misses/extras under the original matching rule. These refer to reference matching, not human-verified sporting false detections.

All per-row matches, misses/extras, boundary signed/absolute/median/RMSE/max/p90 values and six boundary tolerances are preserved in [interval_reference_differences.json](interval_reference_differences.json) and the [full all-component comparison](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v4/test01_candidate_v4/comparison.md). No raw frame arrays are embedded here.

## Coverage, scene boundaries and camera proofs

All13 original recorded content barriers remain, with zero new and zero lost barriers. The full catalogue has no content-epoch decrease. Source review supports edited athlete layouts at all13 selected adjacent pairs, including immediate reacquisition at7857/8106 and no stale near-right person box at7857–7859. This remains agent source diagnosis, not a new human scene-GT benchmark.

| Historical withheld group | Rows restored with exact saved bbox | Fresh matched / carried or unmatched | Minimum bbox IoU |
|---|---:|---:|---:|
| 753–800 | 48/48 | 24/24 | 1.0 |
| 3413–3449 | 37/37 | 18/19 | 1.0 |
| 6365–6381 | 17/17 | 8/9 | 1.0 |
| 7801–7805 | 5/5 | 0/5 | 1.0 |
| 7812–7856 | 45/45 | 8/37 | 1.0 |
| 8087–8105 | 19/19 | 9/10 | 1.0 |
| 14103–14113 | 11/11 | 5/6 | 1.0 |

All182 rows are restored exactly:72 fresh detections and110 carried estimates. None is hidden by the new240-person-row gain. Across **every** frame, current participant count is never lower than the original baseline; there are zero gross lower-count frames. These are historical image-region and population comparisons, not independently labelled detection recall or identity performance.

All155 relative camera claims pass against actual adjacent cached source cameras, including cross-chunk claims at1200,11040and13920. No weak-only barrier occurs in this Test1 run. The relative acquisition path therefore incurs additional probes here without adding a reset; its full-video positive generalisation still needs Test2 evaluation.

The one raw format-context comparison flag at chunk120 is explained, not a defect. Caches are written before `sport.ingest`; the sustained-format decision is established at frame96 during ingest60–119, so that stored chunk remains unknown/unconfirmed and the next chunk120 correctly begins confirmed singles. It is neither annotation input nor current-count guessing. [Ordering/source proof](format_context_transition_review.json), [complete cross-chunk audit](crosschunk_camera_format_audit.json).

## Point agreement and freshness tradeoffs

The original player/shuttle tables are generated references and lack independent physical identities/localization labels. Lower distances indicate agreement with those references, not detection or tracking accuracy.

| Population | Before → fresh count | Mean pixel disagreement before → fresh | Maximum before → fresh |
|---|---|---|---|
| All returned-player pairs | 33466 → 33706 | 3.069777 → 3.050997 | 70.435594 → 70.435594 |
| Current fresh-detector pairs | 13966 → 14237 | 1.456916 → 1.456150 | 68.937185 → 68.937185 |

All33,466 original all-row pairs remain, plus240 new pairs; no old-only pair is removed. All13,966 original fresh-detector pairs have **exactly unchanged** errors;271 fresh pairs are added. The all-row common-pair mean changes3.069777→3.038788 because carried-source comparisons are refreshed:33,171 errors are identical,234 decrease and61 increase. All295 changed pairs were carried/unmatched in the original;183 are fresh in the new frame and the others use refreshed carried geometry. This is not a claim that every new estimate is physically better.

| Largest common-pair increase | Original error px | Fresh error px | Increase px |
|---|---:|---:|---:|
| 16552, legacy slot2 | 4.586953 | 8.574640 | 3.987687 |
| 16553, legacy slot2 | 6.353238 | 10.295458 | 3.942220 |
| 14561, legacy slot2 | 0.902000 | 2.611910 | 1.709911 |

The independent visual review finds the intended athletes in those increased-distance examples, without a new gross wrong-person/empty-court regression. Source ambiguity and generated-reference timing prevent classifying these few-pixel changes as physical errors. The inherited overall player maximum70.435594px at13467 occurs during overlap/occlusion. The newly scored maximum57.284493px at11333 still shows a lagging carried box. These limitations remain visible and unresolved.

Raw shuttle coordinates and confidence are **exactly identical on all17,268 frames**. Presence remains12,036 frames, and11,853 paired generated-reference observations retain mean7.459980px/max561.768698px. The13153shoe-adjacent localization remains an inherited suspicious model observation; filled/generated reference values do not establish its true shuttle position. Manual-court disagreement is unchanged at the one reviewed8634frame: mean1.797572px/max3.529582px for four declared singles-floor corners, not all-frame calibration accuracy.

Evidence: [population decomposition](point_population_decomposition.json), [all changed common pairs](changed_common_player_pairs.json), [freshness/detail](point_freshness_detail.json), [all182 rows](all_182_coverage_review.json), [all current count-loss rows](all_current_gross_population_losses.json).

## Contacts, classes and identity uncertainty

The semantic comparator is the latest preserved dacc05e445-contact cached-perception control. The older raw full-neural baseline has446contacts and is used for raw source overlays/timing; those two scopes are kept separate. Fresh has451contacts/strokes: no original exact anchor is removed and there are no candidate temporal shifts.

| Additional anchor | Stroke output | Recorded physical-event status |
|---:|---|---|
| 1438 | unknown | ambiguous |
| 3015 | unknown | insufficient |
| 3558 | lift | ambiguous |
| 6471 | unknown | ambiguous |
| 8108 | unknown | ambiguous |
| 10676 | unknown | insufficient |

The six extra candidates have four ambiguous and two insufficient physical statuses. Source actions are plausible, but no verified impacts are established. Pipeline `event_status=confirmed` is a lifecycle state; it is not ground-truth contact confirmation.

| Same-anchor class change | Before → fresh | Flight-time context seconds before → fresh |
|---:|---|---|
| 3540 | lift → push | 1.733333 → 0.600000 |
| 6456 | clear → drop | 2.000000 → 0.500000 |
| 16600 | unknown → net_shot | 0.833333 → 0.833333 |

The3540/6456flight contexts shorten with the additional next candidates3558/6471. At16600, source review confirms fresher athlete boxes; it does not verify `net_shot`. Unknown strokes remain305/451(67.6275%), versus301/445(67.6404%). Class-wise correctness/confusion remains unavailable.

Five anonymous attribution changes are retained:1522/1534/1654select exactly the same image box despite episode3→2;5459/16600change unresolved attribution to a provisional episode1 using fresh boxes. No named player is assigned. All named contact actors and known rally winners remain zero outputs, and accepted point decisions remain absent; observed broadcast-score records remain473 and highlights4. This does not establish score accuracy or a verified0–0 score.

Raw output coverage increases: detector-executed frames7091→7183(+92, no original executed frame lost), person rows33,716→33,956, fresh matches14,091→14,362, current-source poses26,752→26,855, and raw racket observations11,385→11,525. Head-alias ambiguity events2047→2077retain rejection diagnostics. Successful execution/greater coverage is not model precision. [Detailed semantic changes](event_differences.json).

## Runtime and remaining limits

| Recorded scope | Original | Fresh |
|---|---:|---:|
| Worker wall seconds | 1750.791 | 1784.006 |
| Worker source FPS | 9.862970 | 9.679337 |
| Parent completed wall seconds | 1757.935 | 1792.249 |
| Final worker CPU thread-seconds | 20979.959 | 21275.076 |
| Worker maxRSS MiB | 2709.656 | 2762.406 |
| Sampled worker GPU MiB | 2124 | 2130 |

Both runs use physicalGPU1, exposed as logicalCUDA0, with the same allocated GPU UUID. Fresh worker time is about29.73minutes for575.6seconds of source. These wall scopes include mixed pipeline work; neural-only throughput and isolated model-loading latency remain unavailable. The modest runtime/resource increase is not an isolated causal performance measurement. Full sampled arrays and stage scopes stay in the linked runtime JSON, not this summary.

All ten unsupported physical metric families remain null: playerAP/mAP/IoU, trackingIDF1/HOTA/switches/fragmentation, posePCK/OKS, shuttle localization/PR, racket/contactPR/F1/timing, stroke confusion/PR/F1, outcome accuracy, score sequence accuracy, highlight quality and player-analytics accuracy. Do not convert unavailable values into zeros or promote generated predictions to ground truth.

Remaining evidence-ranked limitations are carried-box lag during fast motion, inherited shuttle localization/association ambiguity, weak racket/contact evidence, high unknown stroke rate, and absent verified roster/winner/score binding. Test1 now passes the stated population/timing/source regression controls, but these limitations are not declared fixed. Generalisation and positive weak scene acquisition require the separately authorized Test2 workflow before any Test3 claim.

The [independent88-frame visual review](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_contract_v1/visual_test01_v4_review/REPORT.md) inspected all requested source/current/baseline cases and verified1,094 render-output hashes,613 input hashes and264 pixel bindings. Its agent interpretation is diagnostic, not physical GT. Full evidence: [source-frame plan](source_frame_plan.json), [scene records](scene_boundary_review_inputs.json), [visual completion](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_contract_v1/visual_test01_v4_review/completion.json). Root retains the acceptance decision.
