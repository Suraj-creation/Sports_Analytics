# Actual Test 1 class/context change diagnosis

The two common-anchor class changes are caused by new intermediate **estimated contact candidates**, which shorten the classifier's next-candidate flight interval. All seven added candidates receive restored player-body context after the birth fix. Their actual incoming/outgoing shuttle velocities are exactly unchanged. No use of interpolated shuttle samples as observed contact/speed evidence was found in these nine focused cases. Neither new class is established as physically correct; ground truth is unavailable.

This is a read-only diagnosis of completed fresh candidate `c585e35` versus the latest dacc05e semantic control. No pipeline, helper, profile, model, threshold, annotation or evaluation rule was changed. The known raw shoe/equipment alias at13153 is outside these nine cases and was not heuristically suppressed.

## Reproduction and scope

The original serialized stroke/contact payloads already identify the changed flight intervals. We then ran the **unchanged existing** `production_external_semantic_replay.py` with its built-in `--focus` score/readout hook in two new output directories. The hook executes the actual provider's original `detect()` first and returns its output untouched. It only records `score_frame`, velocities, bodies and neighboring selected peaks. This is a CPU cached-perception replay, not new NN inference or a parallel engine implementation.

Both native input/source/model/profile/complete-catalogue guards pass. The new [focus replay manifest](new_focus_replay/replay_manifest.json) has strict fresh own-parity true. The old replay's [comparison to original NN](old_focus_replay/parity_vs_fresh.json) is false because that earlier pre-racket-intervention NN arm has446 contacts. It is **not** the latest semantic baseline. Against the intended latest445-contact dacc semantic control, the existing unmodified `compare_live()` yields **zero differences across every live event**: [exact control comparison](old_focus_vs_latest_semantic_control.json). No guard was relaxed or metadata rebased.

Detailed source-bound values and input SHA256s are in [causal readout](causal_readout.json); the actual provider readouts are [before](old_focus_replay/contact_readouts.json) and [after](new_focus_replay/contact_readouts.json). Both replays preserve executed core/helper bytes and source/cache receipts. Original fresh/model outputs and historical records remain untouched.

## Why3540 and6456 change labels

| Anchor | Before → after | Next estimated anchor | Flight interval | Unchanged speed | Unchanged hitter court position |
|---|---|---|---|---:|---|
|3540 /118.000s|lift → push|3592 →3558|1.733333 →0.600000s|1097.669469px/s|−0.503174,−4.237730m|
|6456 /215.200s|clear → drop|6516 →6471|2.000000 →0.500000s|994.214987px/s|1.780978,5.659977m|

`_on_contact()` classifies the previous candidate when the next candidate is emitted. `_classify()` computes `flight_time_s=(next_frame-current_frame)/fps`; it does not claim this is a reviewed physical flight. The rule classifier source is unchanged between arms.

At3540 the hitter is geometrically midcourt, with speed1.524541 frame-heights/s, below the existing1.6 fast screen. The old interval exceeds1s and selects lift; the new interval does not and selects push. At6456 the hitter is rear-court, with speed1.380854 frame-heights/s. The old long interval selects clear; the shorter interval selects drop. Head/vertical/side features do not affect these particular branches.

Four model-free calls to the **actual unchanged RuleStrokeClassifier**, using the serialized court/speed/flight values, reproduce all four labels **and exact heuristic supports**: [branch-isolation probe](rule_branch_probe.json). Lift0.463093 becomes push0.337851; clear0.674170 becomes drop0.587128. These are uncalibrated supports, not class accuracy. Both common-anchor payloads remain `classification_status=estimated`, `physical_event_status=ambiguous`; named actors and receiver identities stay null.

## Why seven additional contacts appear

Every old focused contact window has **zero usable current body series** at these anchors; every new window has two. This does not imply the old raw detector saw zero people. The singles engine intentionally withholds episode cues unless exactly two mature, distinct current participant snapshots exist. An already emitted raw track may still await the independent participant-entry streak. Earlier correct first births let that streak mature earlier, making the pair available to the unchanged contact provider.

| Added anchor | Old → new support | Old selection/admission | Restored body cue | New stroke | Physical status |
|---|---:|---|---:|---|---|
|1438 /47.933s|0.598688 →0.766899|Provider-selected turn; proximity0 prevented contact|proximity0.2326|unknown: missing evidence|ambiguous|
|1488 /49.600s|0.268941 →0.583597|Below0.35; neighboring1489 selected in old NMS|proximity0.3934|lift estimate|ambiguous|
|3015 /100.500s|0.463448 →0.690944|Provider-selected turn; proximity0 prevented contact|proximity0.2797|unknown: missing evidence|insufficient|
|3558 /118.600s|0.382396 →0.487983|Provider-selected turn; proximity0 prevented contact|proximity0.1269|lift estimate|ambiguous|
|6471 /215.700s|0.423370 →0.512229|Provider-selected turn; proximity0 prevented contact|proximity0.1053|unknown: missing evidence|ambiguous|
|8108 /270.267s|0.343243 →0.838674|Below0.35|proximity0.5396; swing0.4205|unknown: unresolved initial contact|ambiguous|
|10676 /355.867s|0.598688 →0.898714|Provider-selected turn; proximity0 prevented contact|proximity0.5244|unknown: missing evidence|insufficient|

The legacy contact score uses unchanged redirect, impulse, body proximity, swing and optional observed racket overlap. In five cases the old provider already selects the motion peak; the engine exports it as `shuttle_turn`, because proximity is below the unchanged0.05 body-support screen. Restored context moves it into the contact-producing group. At1488 the score crosses0.35 and changes the bounded peak competition around1489; at8108 it also crosses0.35. No threshold changed. Racket overlap is zero in all seven new cases; the observed-racket availability flag at3558 is not proof of overlap or impact.

Actual participant-event lineage demonstrates earlier pair maturity: the relevant near episode1436 versus1442, far episode1484 versus1490, near3014 versus3020, near3554 versus3560, far6470 versus6476, and the post-cut pair8108 versus8110. At10676 the new far episode enters then; its original equivalent enters10682. Opaque episode IDs are lineage identifiers, not verified athlete names. Some newly available body boxes are carried rather than fresh at the exact anchor. The physical-evidence payload correctly records that limitation instead of labeling them fresh.

Total contact/stroke records445→452; unknown strokes301→306. The five added unknowns explain the entire unknown-count increase. The two additional nonunknown labels are1488/3558 lift estimates. No old contact is removed and only the two listed common-anchor classes change. These are output/coverage counts, not improved contact or classification precision/recall.

## D01 and the reconstruction flag

`use_reconstruction=False` belongs to the **rally provider's optional continuation policy**. It is not a global disable switch for `shuttle_post.process()` or every consumer of a processed track. Engine `_window()` already runs bounded postprocessing; D01 preserves independent marked context for ordinary raw absence and prevents reconstruction across contradictory evidence.

The actual contact scorer uses `ok=track.vis & ~track.interp`. Contact physical-motion evidence and post-contact stroke speed use the same observed-only distinction. In these seven added cases, every serialized incoming/outgoing sample was checked against its completed replay step: raw coordinate exists, raw status is observed, observation kind is observed and `interpolated=false`. Old/new raw coordinates and **full precision incoming/outgoing velocity vectors are exactly equal** for all seven. The two common-anchor speeds and hitter geometry also match exactly.

Thus the new candidates in this scope do not arise from D01 promoting estimates to observed impacts or from a global flag leak. The demonstrated cause is availability of participant context after correct births, followed by existing scoring/admission/NMS behavior. This is a bounded causal finding for these cases, not a universal guarantee about every future consumer.

## Synchronized source and perception evidence

Closed source packages independently preserve exact original PTS/pixel and cache bindings. Their visual baseline is the original fullNN perception arm, **not** the later445-contact semantic-control event set used by the class tables. This distinction matters at3558: both original/current images already contain two fresh raw boxes/poses, while the older semantic contact window has zero usable body series because the second participant episode has not matured. The source geometry was not moved to change the class.

Agent source-sequence review finds near overhead preparation1438/3015, near lateral lunge1488/6471, far raised-racket posture3558, near forehand8108 and near net approach/close image overlap10676. Such movement is compatible with activity but does not certify an exact impact, TP, named hitter or class.3540/6456 single frames do not adjudicate lift/push or clear/drop. The overlay at3558 also shows the selected shuttle well above the athlete region; this is a reason to retain raw-localization/contact uncertainty, not to manufacture an alternative label or suppress the case.

| Anchor | Exact source | Current cached perception |
|---|---|---|
| 1438 | [source](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0001438/source_original.png) | [overlay](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0001438/current_source_overlay.png) |
| 1488 | [source](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0001488/source_original.png) | [overlay](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0001488/current_source_overlay.png) |
| 3015 | [source](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0003015/source_original.png) | [overlay](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0003015/current_source_overlay.png) |
| 3540 | [source](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0003540/source_original.png) | [overlay](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0003540/current_source_overlay.png) |
| 3558 | [source](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0003558/source_original.png) | [overlay](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0003558/current_source_overlay.png) |
| 6456 | [source](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0006456/source_original.png) | [overlay](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0006456/current_source_overlay.png) |
| 6471 | [source](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0006471/source_original.png) | [overlay](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0006471/current_source_overlay.png) |
| 8108 | [source](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_v1/frame_0008108/source_original.png) | [overlay](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_v1/frame_0008108/current_source_overlay.png) |
| 10676 | [source](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0010676/source_original.png) | [overlay](/home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_supplement_v1/frame_0010676/current_source_overlay.png) |

[Selected visual receipts](visual_evidence_refs.json) bind all27 linked source/current/baseline PNGs and both completed package receipts. These diagnostics support geometry/lineage inspection; no contact or class accuracy is added to the benchmark.

## Interpretation and next work

No new software-contract defect requiring a production patch was established here. The intended dataflow changed because previously discarded body evidence now reaches an existing heuristic. Existing uncertainty remains material: an ambiguous or insufficient kinematic candidate can still become the next interval endpoint used by the heuristic classifier. More candidate coverage can increase false contacts as well as recover true ones. It can change a preceding label without establishing that either label is right.

Keep this limitation separate from software provenance correctness. A future alternative that uses only reviewed physical next-hit anchors, models endpoint uncertainty, or replaces the classifier needs independent contact/hitter/stroke labels and held-out controls before adoption. Do not suppress all new contacts, increase/decrease thresholds, force classes to unknown, or preserve old labels merely to improve these videos. No named winner or point is manufactured.

The full Test1 evaluation and visual acceptance remain the parent's separate gate; Test2 cross-video regression is still required. This report contributes an explanation and evidence, not a claim that the entire pipeline or physical class accuracy has improved.
