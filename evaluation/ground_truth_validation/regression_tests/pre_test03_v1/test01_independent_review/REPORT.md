# Independent fresh Test1 regression review — c7cf871c failed acceptance control

The fresh candidate preserves all six interval detection matrices and improves their mean IoU slightly, but it fails the source-level acceptance review: two real same-camera edits lose their content barriers, and frames 7857–7859 carry a pre-edit athlete box over empty court. The larger generated-player disagreement maximum is partly a changed population and also exposes this confirmed stale-output regression. This arm must remain a failed acceptance control; its completed execution receipt does not certify accuracy or acceptance.

This review reads completed evidence only. It changes no production source, model, profile, evaluator, annotation, original report or frozen failure database; performs no neural inference; and accesses no Test3 data.

## Comparison arms and reproducibility

- Fresh candidate: `c7cf871c81ccfd0b2bec888284bf9eb2f2f62e8a`, actual full-NN Test1 run at `/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01`; 17,268 canonical 1280×720 frames at 30/1 fps. `cached_perception_used=false`; worker and original parent completed.
- Before perception, resource and interval reference arm: preserved original Test1 `improved_v1` full-NN artifacts. These artifacts were read as saved and were never re-evaluated using new code.
- Before contact/classification arm: latest dacc05e fixed-perception Test1 semantic control (445 contacts/strokes). It executes updated semantics on preserved perception, so this contact comparison is **cached-semantic versus fresh candidate NN**, not two fresh-NN arms with only one code variable.
- Source SHA256: `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`; fresh proxy SHA256: `d352d684fb5399d804b8f50c785a3605346e7f03987ecb1d9a73ef3482535a97`. Same numerical profile, verified loaded model hashes/statuses, and all nine annotation-file hashes match the saved full-NN arm.
- Independently verified all 3,705 completed orchestration artifact hashes, all 288 source-plan production-file hashes, and every consumed input hash. The unchanged strict completion guard was imported and executed from the actual candidate checkout with candidate packages first on `PYTHONPATH`; its ROOT was not rebased to MAIN.
- Full orchestration own-cache semantic parity is recorded as passed. That proves replay reproduction for this arm, not source accuracy. After the completed run, root briefly prepared a new scene-witness candidate at its checkout path, then moved that unbenchmarked experiment to a separate checkout and restored all recorded c7 bytes. The final strict native guard and every production-plan source hash pass again at the original ROOT. The completed c7 outputs and this failed-control diagnosis remain unchanged.

Evidence: [final restored native guard receipt](native_guard_restored_receipt.json), [earlier native guard receipt](native_guard_receipt.json), [review summary](summary.json), [source/lease reconstruction](scene_lease_diagnostics.json), [structured failure cases](structured_failure_cases.json), [original orchestration completion](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01/completion.json).

## Interval reference matrices

Matching policies and complete detection dictionaries are exactly unchanged. Intervals retain the original IoU≥0.5 maximum-cardinality assignment and half-open timestamp duration convention. Partial `Full2` positives retain unavailable FP/precision/F1; unmatched predictions are not asserted false positives. Generated references remain reference-agreement measurements, not independently adjudicated physical truth.

| Reference | TP / FP / FN (both arms) | Precision / Recall / F1 (both) | Mean IoU before → fresh | Fresh start / end / duration MAE (s) |
|---|---:|---|---|---|
| `Test1_Full.csv` | 36 / 0 / 0 | 1.000000 / 1.000000 / 1.000000 | 0.842130 → 0.842284 | 1.026852 / 0.466667 / 1.156481 |
| `Test1_Full2.csv` | 19 / unavailable / 1 | unavailable / 0.950000 / unavailable | 0.846835 → 0.847138 | 1.092982 / 0.433333 / 1.059649 |
| `Test1_Full_rally.csv` | 36 / 0 / 0 | 1.000000 / 1.000000 / 1.000000 | 0.871026 → 0.871185 | 0.938889 / 0.349074 / 1.108333 |
| `Test1_Full_rev_T.csv` | 34 / 2 / 1 | 0.944444 / 0.971429 / 0.957746 | 0.867878 → 0.868047 | 0.890196 / 0.388235 / 0.907843 |
| `Test1_Full_rev_T4.csv` | 36 / 0 / 2 | 1.000000 / 0.947368 / 0.972973 | 0.871026 → 0.871185 | 0.938889 / 0.349074 / 1.108333 |
| `win_predictions.csv` | 36 / 0 / 0 | 1.000000 / 1.000000 / 1.000000 | 0.871026 → 0.871185 | 0.938889 / 0.349074 / 1.108333 |

Only predicted rally 19 changes: start 8111→8108 (270.366667→270.266667 s); all other starts and every end remain unchanged. The primary generated reference starts at 8106 and ends at 8628. Its row19 start error falls 5→2 frames; prediction end stays8627; duration error −0.2→−0.1s; row IoU rises0.988505747→0.994252874. This improvement coexists with the missed8106 temporal barrier and does not validate temporal safety.

Full per-row matches/misses/extras, tolerance tables, signed errors, RMSE, percentiles and duration aggregates remain in the unchanged [fresh component matrix](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01/bound_reference_diagnostics/component_reference_metrics.json), [before component matrix](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01/before_components.json), and [root comparison](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01/comparison.json). No rows or difficult references were removed.

## Generated-point population decomposition

The following diagnostics retain the original assignment scores. Common populations use identical source-frame and legacy point-slot keys, not named or persistent physical athlete IDs. The common/new-only/old-only decompositions explain population effects and do not replace the official all-row metrics.

| Player comparison population | Pairs before → fresh | Mean distance before → fresh (px) | Maximum before → fresh (px) |
|---|---:|---|---|
| All returned rows | 33,466 → 33,646 | 3.069777 → 3.101034 | 70.435594 → 170.104874 |
| All returned rows: same frame/slot | 33,409 → 33,409 | 3.070216 → 3.073217 | 70.435594 → 70.435594 |
| All returned rows: newly scored | 237 | 7.022239 (one arm) | 170.104874 (one arm) |
| All returned rows: no longer scored | 57 | 2.812589 (one arm) | 7.040684 (one arm) |
| Fresh detector-matched rows | 13,966 → 14,000 | 1.456916 → 1.457385 | 68.937185 → 68.937185 |
| Fresh detector-matched rows: same frame/slot | 13,915 → 13,915 | 1.458283 → 1.458283 | 68.937185 → 68.937185 |
| Fresh detector-matched rows: newly scored | 85 | 1.310395 (one arm) | 7.686194 (one arm) |
| Fresh detector-matched rows: no longer scored | 51 | 1.084080 (one arm) | 2.521750 (one arm) |

All-row common-pair mean rises0.003001102px; common-pair maximum stays70.435594px. All13,915 common fresh-detector assignments have **exactly identical** distances. Therefore the detector mean change is a population effect. The all-row maximum170.104874px occurs among newly scored pairs7857–7859; source inspection confirms a real stale carried box there, so population conditioning cannot dismiss the regression.

The unchanged maximum fresh-detector disagreement68.937185px is at13466; unchanged all-returned maximum70.435594px is at13467. The source panels show the two athletes overlapping near the net/left side, consistent with an occlusion or box-bottom ambiguity. They do not adjudicate a correct physical bounding box or athlete identity.

Raw-shuttle/reference both-present pairs11,853→11,861; mean7.459980→7.456164px; median1.478514→1.479515px; maximum561.768698px unchanged. On the11,852 common source-frame pairs, mean7.460392→7.460159px. Raw shuttle presence decreases12,036→12,013 (32old-only,9new-only); common raw positions differ on some frames but P95 displacement remains0 and maximum displacement is3.746525px. Filled/generated visibility is not independent shuttle truth.

At13153 the unchanged raw/legacy discrepancy compares raw(472.38,615.64) to generated-filled(508,55). The source still contains plausible bright shuttle-like pixels elsewhere; a single image does not adjudicate the trajectory. Both coordinates and the unmodified source image are preserved for temporal review. No shuttle PR or physical localization accuracy is claimed.

Complete subsets, new-only/old-only keys and exact raw candidates: [point subset diagnostics](point_subset_diagnostics.json), [raw perception differences](raw_perception_changes.json), [all raw point rows](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01/bound_reference_diagnostics/frame_point_candidates.jsonl).

## Confirmed source-level failure controls

| Source edit | Prior source witness inventory | Existing bounded lease exclusion | Old completed arm | Fresh c7 arm |
|---|---|---|---|---|
| 7856→7857 (261.866667→261.9s) | Old2 actors; fresh1 near actor | Far raw1 last fresh padded-court anchor7770; returned outside through7800; excluded7801 | Raw hypothesis + layout barrier, epoch3→4, no people7857–7859 | No hypothesis/layout; epoch3; detector idle stride6 skips7857; carries pre-edit near bbox until fresh7860 |
| 8105→8106 (270.166667→270.2s) | Old2 actors; fresh1 far actor | Near raw4 last fresh padded-court anchor8056; returned outside through8086; excluded8087 | Raw hypothesis + layout barrier, epoch4→5, no people8106–8107 | No hypothesis/layout; epoch3; scheduled fresh detector executes at8106 and immediately returns current athlete episodes5/6 |

Independent source inspection confirms actual same-camera edits: the displayed score changes18:16→20:18 at7857 and20:18→20:20 at8106, with discontinuous athlete layouts. These are visible broadcast text observations and do not reconstruct points, bind names to tracks or certify the annotation outcome conventions.

The unchanged pipeline constructs scene witnesses exclusively from the immediately preceding returned participant list. Its source continuity detector requires2–4 distinct prior regions before pixel-change analysis or a current layout probe. The new bounded court lease correctly stops indefinite outside-court self-renewal, but it also removes real off-court athletes from this shared scene-witness list. That coupling explains the two missing barriers: old13 actual content barriers become11; only7857 and8106 disappear. Unselected unknown evidence is not serialized at those frames; its two-region failure reason is a deterministic source-branch deduction, separately distinguished from recorded evidence.

At7857–7859 the carried box is `[835.57,439.29,909.24,623.35]`, last detector-matched at7854. Its bottom centre(872.41,623.35) lies over empty rightcourt after the edit; the newly matched generated reference point lies near(713.08,563.76). The cache truthfully marks detector_matched=false. Emitting this stale spatial participant evidence across a missed edit is still a practical pipeline regression. At8106 normal cadence and immediate birth activation acquire the two current athlete regions, so that frame lacks the temporal barrier without the same stale-box effect.

Lease timestamps are private and unpersisted. The quoted anchors are reconstructed from completed returned fresh matches using the exact candidate-native `CourtROI.contains_feet` and `Homography` on recorded per-frameG × calibrationH. They are not fabricated internal traces or physical ground-foot labels. The reconstruction preserves the existing numerical lease and spatial policies.

The failure is not a reason to restore indefinite outside-court authority, alter reference matching, or lower scene thresholds to this video. Root owns the separate generic scene-witness correction proposal and any new isolated candidate arm. This review applies no fix. The remaining11 shared barriers have not all been independently adjudicated as true edits, so retaining them is not a precision claim.

Evidence: [structured failure cases](structured_failure_cases.json), [exact old/new cache and native ROI ledger](scene_lease_diagnostics.json), [7856 image](source_evidence/frame_07856_new_proxy.png), [7857 image](source_evidence/frame_07857_new_proxy.png), [8105 image](source_evidence/frame_08105_new_proxy.png), [8106 image](source_evidence/frame_08106_new_proxy.png), [source frame extraction receipt](source_evidence/receipt.json).

## Contact anchors, classes and anonymous attribution

Latest cached-semantic control445→fresh452 contacts/strokes. With diagnostic maximum15-frame, same-chronological-rally matching, three candidate anchor shifts are7975→7976(+1),8049→8048(−1),8132→8136(+4). The first two stayunknown; the third changeslift→net_shot. These are nearby-anchor associations, not adjudicated physical event identities. There are seven unpaired new anchors and zero unpaired removed anchors under that diagnostic association.

| Unpaired new anchor | Seconds | Predicted class | Recorded physical-event status |
|---:|---:|---|---|
| 1438 | 47.933333 | unknown | ambiguous |
| 1488 | 49.600000 | lift | ambiguous |
| 3015 | 100.500000 | unknown | insufficient |
| 3558 | 118.600000 | lift | ambiguous |
| 6471 | 215.700000 | unknown | ambiguous |
| 8108 | 270.266667 | unknown | ambiguous |
| 10676 | 355.866667 | unknown | insufficient |

Same-anchor class changes are3540lift→push,6456clear→drop,8380lift→drive. Every changed stroke remains an inferred or unknown label. Contact/class metrics cannot be scored from one rally-level `ball_types` label. Added candidates may be true or false; removing/adding counts is not evidence of improved contact accuracy.

| Predicted stroke class | Latest cached-semantic before | Fresh c7 |
|---|---:|---:|
| clear | 8 | 7 |
| drive | 4 | 5 |
| drop | 22 | 23 |
| lift | 28 | 27 |
| net_shot | 32 | 33 |
| push | 48 | 49 |
| smash | 2 | 2 |
| unknown | 301 | 306 |

Unknown rate301/445=67.640449%→306/452=67.699115%. Nine same-anchor anonymous actor records change; all nine select the identical source-image region (raw bboxIoU1.0). Numeric episode namespaces change across resets/births and must not be scored as physical identity switches. Named contact actors remain0 and known rally winners remain0 in both arms; these are missing identity/outcome evidence, not zero accuracy.

Other latest-semantic→fresh event counts: racket ambiguity2047→2022, participant observation123→131, activity interval122→112, shuttle turn41→37, identity ambiguity50→48, broadcast score473→473, highlights4→4 and rallies36→36. No accepted point event is emitted in either arm. Observed scoreboard values must not be reported as an accepted match score or a verified0–0.

Every compact before/after event, contact evidence field, candidate shift, added anchor and class change is in [event differences](event_differences.json). The source-bound [expanded visual frame plan](visual_frame_plan_v3.json) contains31 diagnostic frames; root’s separate renderer combines it with77 preserved cases into a new108-case panel run. That renderer is outside this immutable review and is not assumed successful here.

## Component coverage and unavailable accuracy

| Raw cache coverage | Original full-NN | Fresh c7 full-NN |
|---|---:|---:|
| `raw_shuttle_present` | 12036 | 12013 |
| `detector_executed_frames` | 7091 | 7070 |
| `person_rows` | 33716 | 33771 |
| `person_current_detector_matches` | 14091 | 14064 |
| `person_propagated_or_unmatched` | 19625 | 19707 |
| `pose_present_rows` | 26752 | 26615 |
| `pose_current_on_propagated_box` | 12661 | 12561 |
| `racket_present_rows` | 11385 | 11353 |
| `actual_content_epoch_increments` | 13 | 11 |

New calibration coverage:16,941VALID,42REACQUIRING,285LOST frames; target view16,983main/285none. Player populations2:16,788,1:195,0:285. All recorded stale pose/racket source-marker counts remainzero; this does not make carried boxes current detections. Single-frame manual court reference8634 yields mean1.797572px/max3.529582px outer-singles-corner disagreement under the existing source/semantic certificate. It is a single reviewed diagnostic, not all-frame calibration accuracy.

All ten unsupported metric families remain explicitlynull/unavailable: playerAP/mAP/boxIoU; trackingIDF1/HOTA/ID switches/fragmentation; posePCK/OKS; physical shuttle localization/PR; racket/contactPR/F1/temporal error; stroke per-classPR/F1/confusion; physical winner/outcome accuracy/confusion; score-sequence accuracy; highlight quality; named player analytics accuracy. The annotations lack the reviewed exhaustive boxes, persistent identities, joints, contact negatives/times, per-contact classes or legal score binding needed for those metrics. They must not becomezero performance or model-generated ground truth.

## Runtime, actual models and scope limits

| Full-NN resource measure | Original full-NN | Fresh c7 full-NN |
|---|---:|---:|
| `worker_elapsed_s` | 1750.791 | 1769.007 |
| `worker_source_fps` | 9.863 | 9.761 |
| `parent_completed_elapsed_s` | 1757.935 | 1777.014 |
| `worker_final_cpu_s` | 20979.959 | 21172.256 |
| `worker_maxrss_bytes` | 2841280512.000 | 2887081984.000 |
| `sampled_worker_tree_peak_rss_bytes` | 2847993856.000 | 2890985472.000 |
| `sampled_worker_gpu_peak_mib` | 2124.000 | 2132.000 |

Both arms use physicalGPU1 (GTX1080Ti), UUID`GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab`. Loaded TrackNetv3 uses CUDAFP16; RF-DETRsmall and RTMPose use ONNXCUDAFP32; OCR uses CPU; racket geometry uses OpenCVCPU. Declared runtime backends show no neural fallback. Sampled GPU/RSS peaks are sampled observations, stage timers overlap, and CPU time sums threads. Shared-host loads were not controlled, so this is no throughput improvement/regression attribution.

Verified weights are exactly unchanged: TrackNetv3`df867641a027…`; RF-DETR`fcd3c3c4e0d3…`; RTMPose`f7fbb6c5c11a…`; all three package OCR hashes also agree. Complete hashes and actual cache runtime declarations are preserved in [technical analysis](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01/analysis/technical_analysis.json) under`models_verified_during_analysis`,`model_sets_from_actual_caches`,`runtime_declarations_from_actual_caches`, and in [worker model staging/runtime](/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01/run/inference.json). Configured optional OSNet and BallTrack remain unavailable; WASB remains an unknown registry entry. Their presence in the profile is not a claim they executed. Named-player and reidentification accuracy remain unavailable.

The review isolates population and semantic changes; it does not establish a causal physical accuracy delta for each candidate change. The candidate includes birth activation, bounded court leases, engine evidence lifecycle and capability changes; the contact before arm is a cached-perception semantic control. Test1 is singles and provides no empirical four-player doubles accuracy claim. Generic doubles contract tests are separate engineering evidence. No conclusions about Test2’s fresh candidate performance or Test3 generalisation follow from this run.

Evidence is kept separately: [additional source extraction receipt](source_evidence/receipt_additional.json), [13153 source](source_evidence/frame_13153_new_proxy.png), [13466 source](source_evidence/frame_13466_new_proxy.png), [13467 source](source_evidence/frame_13467_new_proxy.png), [executed primary diagnostic](executed_independent_review.py), [executed native scene ledger helper](extend_scene_review.py).

**Disposition:** completed reproducible review; candidate c7cf871c **failed acceptance** on confirmed temporal continuity controls. Keep this arm, all baselines and original annotations immutable. Root must review a generic correction and any separately named follow-up regression arm before accepting the candidate or continuing to the next large video.
