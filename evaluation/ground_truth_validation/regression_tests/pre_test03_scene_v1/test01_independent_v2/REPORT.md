# Independent fresh Test1 review — c585e35 candidate v2

**The candidate repairs both failed c7 edit controls and removes the7857–7859 stale box, while preserving all six interval detection matrices. There is a material participant-coverage tradeoff:182 original participant rows are withheld across seven offcourt intervals, even though their image regions remain available for scene continuity.** Conditional point agreement and net coverage gains must not hide those losses or be called physical recall nonregression.

This is an independent read-only review of a completed genuine fresh-NN run. It does not approve the whole phase, claim every Test1 issue is fixed, certify physical component accuracy, or complete Test3. Root owns acceptance and the next sequential video.

## Evidence gates and comparison arms

- Actual candidate:`c585e3507a2fef9ff393a8cfbba575a979345f53`;17,268canonical1280×720frames at30/1fps. Worker and original parent completed with fresh perception; own-cache semantic parity is recorded true.
- The unchanged strict guard was executed from the actual recorded candidate ROOT, without rebasing imports. All3,709 completed artifact hashes and289 source-plan hashes were independently checked. Numerical profile, actual model identities, nine Test1 annotation hashes and unchanged evaluation-method bindings pass.
- Before perception/resources/intervals: original preserved Test1improved_v1 full-NN output. Additional failed-control comparison:c7freshTest1. Baselines were read as saved, not re-evaluated using current code.
- Before contacts/classes: latest dacc05e semantic replay over preserved perception (445contacts,301unknown). This is cached-semantic versus fresh-NN, not a single-variable fresh-NN experiment.
- SourceSHA256:`877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`. Complete native/source/model/method bindings:[native guard](native_guard_receipt.json), [computational summary](summary.json), [original completion](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2/completion.json).

## Six reference matrices

Detection dictionaries and matching policies are unchanged. Existing IoU≥0.5assignment, half-open timestamps, tolerance denominators, exclusions and zero/unavailable conventions remain intact. Coarse labels, generated timing references and partial Full2 retain their original disclosed roles; generated agreement is not independent physical ground truth.

| Reference | TP/FP/FN before = fresh | Precision / Recall / F1 before = fresh | Mean IoU before → fresh | Fresh start/end/duration MAE(s) |
|---|---|---|---|---|
| `Test1_Full.csv` | 36/0/0 | 1.000000 / 1.000000 / 1.000000 | 0.842130 → 0.842284 | 1.026852 / 0.466667 / 1.156481 |
| `Test1_Full2.csv` | 19/unavailable/1 | unavailable / 0.950000 / unavailable | 0.846835 → 0.847138 | 1.092982 / 0.433333 / 1.059649 |
| `Test1_Full_rally.csv` | 36/0/0 | 1.000000 / 1.000000 / 1.000000 | 0.871026 → 0.871185 | 0.938889 / 0.349074 / 1.108333 |
| `Test1_Full_rev_T.csv` | 34/2/1 | 0.944444 / 0.971429 / 0.957746 | 0.867878 → 0.868047 | 0.890196 / 0.388235 / 0.907843 |
| `Test1_Full_rev_T4.csv` | 36/0/2 | 1.000000 / 0.947368 / 0.972973 | 0.871026 → 0.871185 | 0.938889 / 0.349074 / 1.108333 |
| `win_predictions.csv` | 36/0/0 | 1.000000 / 1.000000 / 1.000000 | 0.871026 → 0.871185 | 0.938889 / 0.349074 / 1.108333 |

Only predicted rally19start changes8111→8108; all other starts and every end are unchanged. Primary generated reference19starts8106and ends8628: start error5→2frames, prediction end8627unchanged, duration error−0.2→−0.1s and rowIoU0.988505747→0.994252874. The tiny six-reference IoU improvement comes from this single boundary. Full2FP/precision/F1 remainnull; unlabelled predictions are not silently counted as false detections.

All changed per-reference rows, complete metrics/tolerances/signed-error distributions and raw source rows remain accessible:[independent interval differences](interval_reference_differences.json), [fresh component matrix](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2/bound_reference_diagnostics/component_reference_metrics.json), [saved baseline](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2/before_components.json).

## Scene continuity: confirmed repairs

Fresh content barriers exactly match the original13:2195,4837,7503,7857,8106,10023,10604,10770,11903,15579,15985,16446,17069. Relative to c7,7857and8106are recovered and none are lost. Relative to the original there are no new or lost content barriers. Matching a count alone is not scene precision/recall or proof that every inherited barrier is a true edit.

At7857two current athlete boxes are detector-observed immediately;7858–7859carry those current boxes. Every box has0IoUto the known old7854/7856 near-player stale region, which is visibly empty after the edit. The failed c7maximum170.104874px disappears; the all-returned generated-player maximum returns to the inherited70.435594px at13467. At8106the barrier and immediate current athlete acquisition also hold.

Independent source views:[7857](source_evidence/frame_07857.png), [7859](source_evidence/frame_07859.png), [8106](source_evidence/frame_08106.png). Exact cache/scene evidence:[scene boundary review inputs](scene_boundary_review_inputs.json). These are source-bound agent diagnostics, not newly created physical labels.

## Point agreement and population changes

| Original full-NN → fresh | Pairs | Mean disagreement(px) | Maximum(px) |
|---|---|---|---|
| All returned players: full population | 33466 → 33649 | 3.069777 → 3.082777 | 70.435594 → 70.435594 |
| All returned players: identical frame/legacy-slot subset | 33409 → 33409 | 3.070216 → 3.070216 | 70.435594 → 70.435594 |
| All returned players: new-only | 240 | 4.831308 | 57.284493 |
| All returned players: old-only | 57 | 2.812589 | 7.040684 |
| Fresh detector-matched players: full population | 13966 → 14042 | 1.456916 → 1.456219 | 68.937185 → 68.937185 |
| Fresh detector-matched players: identical frame/legacy-slot subset | 13955 → 13955 | 1.457184 → 1.457184 | 68.937185 → 68.937185 |
| Fresh detector-matched players: new-only | 87 | 1.301383 | 7.686194 |
| Fresh detector-matched players: old-only | 11 | 1.116936 | 2.521750 |

Every33,409common all-player error and every13,955common detector-matched error is numerically identical to the original. The all-row mean increase is therefore a population effect, not a common-subset degradation. This conditional equality does **not** demonstrate all-frame physical recall preservation. Comparing c7→fresh, the common all-row mean decreases3.101034→3.082969px and the170px stale-box outlier is removed; all14,000common detector-matched errors are unchanged.

Raw shuttle XYand confidence are exactly identical to the original on all17,268frames. Presence12,036and generated-reference both-present11,853 remain unchanged; mean7.459980px, median1.478514px and maximum561.768698px are unchanged. Source13153still exposes an inherited shoe-alias diagnostic. Filled-reference disagreement cannot be converted into physical shuttleAP/PR or a reviewed localization error.

Complete common/new-only/old-only keys and original/c7 decompositions:[point population decomposition](point_population_decomposition.json). Original source rows are preserved in the producer’s [frame-point JSONL](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2/bound_reference_diagnostics/frame_point_candidates.jsonl).

## Explicit coverage costs: all57scored losses and all182withheld rows

The57old-only generated-point pairs are alllegacy slot2:6375–6381(7),7801–7805(5),7812–7856(45). Their former matched distances average2.812589px, maximum7.040684px; they are not dropped from this report. All57corresponding image regions remain in foreground context withIoU>0.99to the original box;46are unobserved carries and11are fresh matched image observations. Current detector support is retained in8of these rows’ detailed diagnostics. Foreground has no confidence field; missing current support is explicitly unavailable and is never copied from historical person confidence.

The broader raw participant tradeoff is182withheld rows over182frames, compared with240additional rows over173frames: net+58rows. The net gain must not conceal the gross losses. The182missing participant regions are all retained as scene-only context (minimum same-regionIoU>0.999998).

| Fewer-participant interval | Rows withheld | Reconstructed last padded-court anchor | Representative source assessment |
|---|---:|---:|---|
| 753–800 | 48 | 722 | [Near dark-top athlete beyond near baseline, lower-left](source_evidence/frame_00753.png) |
| 3413–3449 | 37 | 3382 | [Near dark-top athlete beyond near baseline, lower-right](source_evidence/frame_03413.png) |
| 6365–6381 | 17 | 6334 | [White-top athlete outside right sideline near umpire](source_evidence/frame_06365.png) |
| 7801–7805 | 5 | 7770 | [White-top athlete beyond far baseline](source_evidence/frame_07801.png) |
| 7812–7856 | 45 | 7770 | [Far white-top athlete remains visible near boards](source_evidence/frame_07812.png) |
| 8087–8105 | 19 | 8056 | [Near dark-top athlete beyond near baseline, lower-right](source_evidence/frame_08087.png) |
| 14103–14113 | 11 | 14072 | [Far dark-top athlete outside right sideline near umpire](source_evidence/frame_14103.png) |

These reconstructed leases expire31frames after the last observed padded-court anchor; later raw image matches renew scene context, not participant authority. Source checks in every interval show visible courtside athletes at representative frames, not obvious officials. This is a real semantic-coverage tradeoff. It does not become182independently labelled false negatives, because complete role/visibility identities are unavailable and not every frame was manually adjudicated. Scene context also supplies no pose/contact/named-player authority for those withheld people.

Only57of those182losses appear as old-only matched legacy pairs. Other frames, including8087–8105, lack the same legacy assignment population; a generated reference’s missing pair is not proof the visible athlete is irrelevant. All182rows, flags, exact boxes, reconstructed ages and available current support are retained:[gross coverage ledger](gross_coverage_all_182_rows.json), [57pair ledger](coverage_tradeoffs.json). Timestamps are reconstructed from recorded observations/native court predicates, not invented private-state traces.

## Contacts, classes and identity scope

Latest dacc semantic445→fresh452contacts/strokes. All445exact anchors are retained with no candidate shifts or removals. Seven new anchors are1438,1488,3015,3558,6471,8108,10676: fiveunknown and twolift(1488/3558). Their recorded physical statuses are ambiguous or insufficient; added counts are not validated contact recall.

Only same-anchor class changes are3540lift→push and6456clear→drop. Their recorded flight-time features change1.733333→0.6s and2.0→0.5s respectively. These are temporal/context feature changes with unchanged raw neural shuttle observations; class accuracy is unavailable without per-contact GT. The failed c7candidate’s three shifted anchors and8380lift→drive change are absent here.

| Predicted class | Latest cached-semantic before | Fresh c585 |
|---|---:|---:|
| clear | 8 | 7 |
| drive | 4 | 4 |
| drop | 22 | 23 |
| lift | 28 | 29 |
| net_shot | 32 | 32 |
| push | 48 | 49 |
| smash | 2 | 2 |
| unknown | 301 | 306 |

Unknown301/445=67.640449%→306/452=67.699115%. No same-anchor anonymous actor episode/status change is detected; no physicalIDF1/HOTA inference follows. Named contact actors remain0and known rally winners remain0. Broadcast-score observations473and highlights4are unchanged; no accepted point event is recorded. Observed scoreboard values are not an accepted verified match score.

Detailed compact event differences, physical-evidence statuses and class counts:[event differences](event_differences.json). The [45-frame source plan](source_frame_plan.json), [all-coverage plan](all_coverage_frame_plan.json) and source-bound [agent observations](agent_source_observations.json) preserve controls for separate rendering/review.

## Remaining perception limitations

- At11333a newly available box is carried from11328while the near athlete lunges. It visibly lags; its generated-reference distance57.284493px is a newly exposed estimate/cadence limitation, not physical GT localization error. The old arm had no matched pair there. [Source11333](source_evidence/frame_11333.png).
- At13153the inherited raw shuttle point is near the athlete’s shoe. The filled reference is also not independently trustworthy; this remains an unresolved model/candidate diagnostic. [Source13153](source_evidence/frame_13153.png).
- At13467athletes overlap near the left/net region; the inherited70.435594px player disagreement remains. No box-ground-truth adjudication establishes a physical IoU/AP score. [Source13467](source_evidence/frame_13467.png).
- Other independent rendered review retains inherited false raw racket ellipses, including near-body15808. Semantic ambiguity admission is not a repair of every raw racket detection. [Separate rendered review](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_v1_review.md).

## Component coverage, resources and unavailable metrics

| Count / resource | Original full-NN | Fresh c585 full-NN |
|---|---:|---:|
| `detector_executed_frames` | 7091 | 7091 |
| `person_rows` | 33716 | 33774 |
| `person_current_detector_matches` | 14091 | 14106 |
| `person_propagated_or_unmatched` | 19625 | 19668 |
| `pose_present_rows` | 26752 | 26715 |
| `racket_present_rows` | 11385 | 11393 |
| `worker_elapsed_s` | 1750.791 | 1748.479 |
| `worker_source_fps` | 9.863 | 9.876 |
| `parent_completed_elapsed_s` | 1757.935 | 1756.291 |
| `worker_final_cpu_s` | 20979.959 | 21052.071 |
| `worker_maxrss_bytes` | 2841280512.000 | 3213459456.000 |
| `sampled_worker_tree_peak_rss_bytes` | 2847993856.000 | 3144826880.000 |
| `sampled_worker_gpu_peak_mib` | 2124.000 | 2124.000 |

Both runs use physicalGPU1with the same recorded device UUID. These are resource observations on a shared host; overlapping stage timers and sampled peaks do not support a causal throughput claim. Peak processRSS increases2.841→3.213GB while sampled GPU peak remains2124MiB. Full actual backend/checkpoint provenance, including OCR package assets and extracted pose graph, is preserved in the [runtime asset audit](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/runtime_assets_v1/REPORT.md).

Single-frame court reference8634 remains mean1.797572px/max3.529582px outer-singles-corner disagreement under its source/coordinate certificate; it does not certify all-frame geometry. All10unsupported physical metric families remainnull: playerAP/mAP/boxIoU; trackingIDF1/HOTA/switches/fragmentation; posePCK/OKS; physical shuttlePR/localization; racket/contactPR/F1/timing; per-stroke classPR/F1/confusion; physical outcome accuracy/confusion; score accuracy; highlight quality; named-player analytics accuracy. Null means unavailable evidence, not zero performance.

**Disposition:** the confirmed c7same-camera edit regression is repaired in this genuine fresh run and reference detection agreement is preserved. Acceptance must retain the explicit182-row participant-coverage cost,57old-onlypairs, newly exposed carried-box lag and inherited raw perception errors. This review provides no new code fix, no full-phase/Test3 completion claim and no physical generalisation guarantee. Complete fresh Test2 and the planned component-specific diagnostics remain separate work.
