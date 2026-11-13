# Test 2 V5: independent known-case source review

All **108 predeclared frames** were inspected as original source, preserved baseline overlay and actual current overlay: **324 panels on 18 aspect-preserving sheets**. The current run is the genuinely completed fresh Test 2 run from frozen commit `5ae614826e6f909defb02445386962ac13b4641a`; baseline is the original completed `dacc05e` Test 2 `improved_v1` neural run. This review covers selected known cases, not every new reset or every frame of the video.

Rendering waited for the actual worker and parent to complete, the catalogue to contain all **29,296 frames**, and timestamp auditing to finish with exit0, exact source/proxy PTS equality and a matching source-frame CSV hash. The readiness transition is retained in [observations](readiness_observations.jsonl). The frozen producer's original renderer then passed its genuine full-run/source guards; no guard was bypassed, ROOT rebased, header changed or receipt fabricated. The exact owned Test 2 source SHA256 is `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`.

The completed package verifies **1,284 artifact hashes**, **1,015 recorded input bindings**, and **324 decoded image pixel/shape receipts**. Every source time equals the rational canonical time for both actual proxy arms. Original and frozen cache segments agree, and model/config/producer provenance is retained. The executed renderer bytes equal the frozen candidate's renderer. See [verification](verification.json), [frame register](frame_register.json), [sheet index](sheet_index.json) and [closed rendered bundle](../visual_test02_v5_known_cases_v1/index.md). This CPU-only work decoded source/proxy images and performed no neural inference or numerical benchmark recalculation.

## Scene reset and continuity controls

All four previously lost candidate resets—**2928, 11082, 22416 and 23279**—coincide with real same-camera source edits. The athletes abruptly change position while the court/broadcast view persists. Current records a strong scene hypothesis, a layout-confirmed barrier and two fresh detector-matched athletes at each. The original baseline also resets at these four locations, but emits no admitted people at the cut frame; current immediately acquires the visible pair. The older2418 candidate's loss of these resets was diagnosed separately; this package compares actual5ae with originaldacc, not with2418.

At2928 the near athlete jumps from a bent central posture into a leftward playing position while the far athlete relocates. At11082 both athletes move abruptly from the left side into central play. At22416 a near-net/bent state jumps into a separated near/far service-like layout, with a scoreboard transition. At23279 the overlapping near-net pair abruptly separates into a central near/far layout; current has no carried far-athlete box over the previous empty region. See [2928](sheet_04.jpg), [11082](sheet_10.jpg), [22416](sheet_15.jpg) and [23279](sheet_16.jpg).

The nine earlier weak-reset contexts remain source-supported edits:355,699,1095,3394,4581,5958,11691,11985 and25521. Current preserves the raw strong-hypothesis value **false** and uses the explicit relative-change/complete-current-court replacement proof. These are not strong hypotheses relabelled after the fact. Walking/off-court athletes jump to current central positions; several transitions also show scoreboard changes. At5958 the actual source edit is visible and current acquires the two athletes; the baseline retains the earlier background-region/official context before later acquisition. This evidence does not solve unrestricted identity handover during otherwise continuous footage.

Other source-supported strong controls6151,6307 and11346 also produce current barriers and two fresh athletes. Full-run11346 has enough genuine preceding foreground history to recover this edit; it must not be equated with the old cold-start prefix's unknown scene status. This package preserves the actual complete-run history.

At **7703** the near athlete continues a lunge and the far athlete maintains a coherent response. At **23639** the near athlete bends/walks toward the camera while the far athlete remains consistent. Both source sequences are continuous. Current records a raw strong hypothesis but **no_barrier** because the current layout positively corresponds to the preceding regions. Both controls keep two fresh athlete boxes at the centre frame. They remain useful controls against converting every foreground innovation into a cut. See [7703](sheet_09.jpg) and [23639](sheet_16.jpg).

| Frame | Predeclared role | Source diagnostic | Current evidence | Current decision | Baseline → current people |
|---|---|---|---|---|---|
| 355 | earlier weak edit cases | edit | relative/court | barrier | 2 → 2 fresh |
| 699 | earlier weak edit cases | edit | relative/court | barrier | 2 → 2 fresh |
| 1095 | earlier weak edit cases | edit | relative/court | barrier | 2 → 2 fresh |
| 2928 | recovered prior candidate edits | edit | strong | barrier | 0 → 2 fresh |
| 3394 | earlier weak edit cases | edit | relative/court | barrier | 1 → 2 fresh |
| 4581 | earlier weak edit cases | edit | relative/court | barrier | 2 → 2 fresh |
| 5958 | earlier weak edit cases | edit | relative/court | barrier | 1 → 2 fresh |
| 6151 | other edit controls | edit | strong | barrier | 3 → 2 fresh |
| 6307 | other edit controls | edit | strong | barrier | 3 → 2 fresh |
| 7703 | continuous negative controls | continuous | strong | no_barrier | 2 → 2 fresh |
| 11082 | recovered prior candidate edits | edit | strong | barrier | 0 → 2 fresh |
| 11346 | other edit controls | edit | strong | barrier | 0 → 2 fresh |
| 11691 | earlier weak edit cases | edit | relative/court | barrier | 2 → 2 fresh |
| 11985 | earlier weak edit cases | edit | relative/court | barrier | 2 → 2 fresh |
| 22416 | recovered prior candidate edits | edit | strong | barrier | 0 → 2 fresh |
| 23279 | recovered prior candidate edits | edit | strong | barrier | 0 → 2 fresh |
| 23639 | continuous negative controls | continuous | strong | no_barrier | 2 → 2 fresh |
| 25521 | earlier weak edit cases | edit | relative/court | barrier | 2 → 2 fresh |

The table contains **16 selected edit contexts and two selected continuity controls**. These are deliberately selected diagnostic examples, not a sampled physical scene precision/recall denominator. Source expectations are agent observations; original CSV annotations are untouched and no new physical GT labels were created. Exact source/overlay links and typed decision reasons are in [case register](case_register.json).

## Preparation, short exchange and cadence limitations

The early809/850 source frames still show preparation/held positioning. Frames900/904/907 show the later near-athlete service-like movement and departure. Current's raw shuttle association is unknown at809/850, with reacquisition at900 and tracked observations904/907. Neither an old high contact score nor a new tracked point establishes exact physical impact, class, named hitter or a legal point.

The sampled short-event sequence11700/11710/11715/11716/11731/11740/11751/11774 retains two source-aligned people with current-source pose in both arms. Source preparation progresses to near-athlete action/departure, far-athlete return-like action and forward movement/aftermath. No obvious athlete-hypothesis break is visible in these selected frames. Exact impacts and rally boundaries remain unlabelled. This source package does not decide whether the formal short-event admission is correct, recover11715 as a physically probable impact, or replace the independent numerical event/IoU comparison. See [short exchange](sheet_13.jpg). The previously sealed continuous197-frame source review remains a separate historical source study; it is not being represented as a fresh5ae full-timeline semantic result.

The **cadence limitation persists** in the actual current run. At sampled25680,25681,25710 and25739, current uses perception stride6 while original baseline uses stride1, despite visible active play. Current has fresh detection/pose at25680 and25710 but carried boxes and no current pose at25681/25739. At25740 both return to stride1 and fresh detection/pose. The selected carried boxes still cover the moving athletes with ordinary lag; this does not remove the lost temporal pose coverage. These five samples confirm the scheduling difference; they do not independently reproduce the complete FSM feedback cause or certify physical player accuracy. See [cadence samples](sheet_18.jpg).

## Scope and preservation

The initial predeclared source controls pass their specific visual expectations, while sparse scheduling and physical contact/classification uncertainty remain. Whole-video component metrics, all newly changed regions, additional reset contexts, raw shuttle quality and final Test 2 acceptance belong to the separate completed-run numerical and source reviews. This package makes no blanket claim of unchanged shuttle output, aggregate physical accuracy or pipeline acceptance.

Every original source video, annotation, prediction, historical evaluation and active downstream output remains intact. Candidate source files were not modified. The parent orchestrator retains control of acceptance, merge/push and eventual cleanup.
