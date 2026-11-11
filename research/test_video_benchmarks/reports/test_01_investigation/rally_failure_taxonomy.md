# Test1 rally failure taxonomy

Auditor F. Classification uses frozen predictions and raw event provenance, not manually corrected model outputs. Matching and the seven-column schema remain unchanged. See `rally_segmentation_audit.md` and `artifacts/benchmarking/investigation/audit_f/fsm_probe_results.json` for source and controlled evidence.

## Levels of evidence

- **Observed:** a recorded interval, event, observation or metric.
- **Proven mechanics:** source plus an executed controlled production-FSM probe establishes the software behavior.
- **Real causal attribution:** the exact real processed input triggers that software behavior, with alternate visual/perception explanations reviewed. This last level still requires orchestrator replay for most missing/stationary decisions.

## Ranked classes

| Class | Observed support | What it explains | What it does not establish | Next discriminating experiment |
| --- | --- | --- | --- | --- |
| F1 Fragmentation plus assignment displacement |11 GT intervals overlap multiple predictions; GT2/19 first fragments start+4 but selected fragments start+179/+202 | Large apparent start delays and end truncations can come from selecting one of several pieces | It does not prove fragments should be joined or that the first/last envelope is ground truth | Exact state replay and conditional continuity ablation with separate-rally controls |
| F2 Cancelled initial fragments |34 provisional starts retracted; GT5 onset2210 is detected then cancelled | Lost exported onset despite earlier motion/contact evidence | Cancellation may correctly reject noise; the first provisional point is not automatically valid | Recover candidate duration/end gate and evidence on both sides of reacquisition |
| F3 Observation-gap termination |26 final gap reasons; gap-fill interpolation is excluded from FSM observation mask | Temporary loss can still terminate an interval | Does not tell whether each loss is occlusion, confidence, rejection, view loss or actual point end | Observe exact boolean/speed/context trajectory and inspect original frames |
| F4 False/ambiguous shuttle stationarity |23 final stationary reasons; low-speed count has no quality/landing gate | Potential early stops and repeated fragments | Player inactivity is not the direct trigger; stationary detections may be a correctly landed shuttle | Inspect peak/trajectory evidence; separate rest, slow flight and stuck/background detections |
| F5 Boundary-gap and confirmation-clock mismatch |18-frame loss probe recovers,19-frame loss splits; candidate onset inside22 but confirmation outside | Near-window recovery can fail even at unchanged nominal gap | Not established as dominant baseline cause; cannot explain43-frame gaps alone | Candidate-time accounting ablation with exact replay |
| F6 Explicit contact outside current merge bound |GT27 end/contact12748 and next start/contact12771, difference23 vs limit22 | That real neighboring fragment is excluded by current merge policy despite accepted contact | A one-frame wider merge is not automatically safe or generalizable | Compare contact/context-compatible continuation and close real-break controls |
| F7 Stationary-window configuration defect |Deque maxlen10; windows5/15 fail stationarity after warmup | Invalid parameter experiments and replaceability failure | No baseline effect at default10 | Parameter/reset/checkpoint regression tests; preserve default behavior |
| F8 View/context interruption |Some source frames are excluded/replay-flagged; GT31 has21 camera-lost/replay-flagged frames | Can clear history/cancel a provisional interval and prevent merges | Zero final cut reasons does not prove view transitions had no effect; short cut segments may be cancelled | Capture all discontinuity calls and short cancellations, not only final end reasons |
| F9 True initial signal/onset weakness |Some first surviving fragments remain late even after accounting for assignment | Additional onset loss beyond fragmentation | Cannot be blamed on TrackNet stride or missing OSNet from source alone | Align original frames, raw detections, processed adjacent motion, contacts and cancelled starts |

## Named severe cases

| GT row | Label frames | Exported pieces overlapping the label | Selected-match consequence | Proven minimum explanation |
| --- | --- | --- | --- | --- |
|2|887–1262|891–1023 gap;1066–1255 stationary|Selected second piece starts179 frames late|Initial first exported onset is only4 frames late;43-frame inter-fragment gap exists|
|19|8106–8628|8110–8266 gap;8308–8627 gap|Selected second piece starts202 frames late|Initial first exported onset is only4 frames late;42-frame inter-fragment gap exists|
|20|8683–9967|8715–9525 gap;9548–9646 gap;9685–9947 gap|Selected first piece ends442 frames early|Last piece reaches20 frames before label end;gaps23/39 remain|
|27|12451–12966|12455–12748 stationary;12771–12954 stationary|Selected first piece ends218 frames early|Last piece reaches12 frames before label end;accepted-contact gap23 exceeds22|

These envelopes are supplementary diagnostics only. They must never replace prediction rows or be used to modify the benchmark matcher.

## All six policy-missed labels

| GT row | Label frames | Recorded pieces | Initial cancelled starts within the label | Evidence distinction |
| --- | --- | --- | --- | --- |
|5|2210–2500|2309–2423 gap|2210,2460|The initial label-aligned onset is recorded then retracted;one curtailed surviving piece fails IoU eligibility|
|23|10733–11078|10601–10737 stationary;10769–10908 gap;10949–11085 stationary|none|First overlap is tail of preceding interval;two later fragments also fail IoU eligibility|
|25|11568–11865|11634–11745 gap;11801–11867 gap|11570,11613|Early candidate cancellation plus later fragmentation|
|28|13054–13442|13176–13252 gap;13273–13439 gap|13115,13151|Large initial onset loss plus fragmented return;root perception cause still unproven|
|29|13679–13994|13686–13843 gap;13883–13982 stationary|none|First157-frame span is just below half of the315-frame label span;do not change the0.5 rule to rescue it|
|31|14404–15151|14491–14646 gap;14701–14969 gap;14994–15171 stationary|14430|Candidate cancellation and three fragments;21 lost/replay-flagged camera frames are an additional observed confound|

## Fragmentation set and unmatched predictions

The11 overlap-multiple labels are `[2,3,19,20,23,25,27,28,29,31,33]`. These are overlap diagnostics; a marginal tail crossing a label boundary also counts, as in GT23. Distinguish this from a claim of11 causally proven mid-rally splits.

The19 unmatched predictions must remain false positives under the fixed matching policy, even when a prediction is a valid-looking fragment of a labeled rally. An unmatched prediction is not necessarily a fabricated interval during a break. The orchestrator's failure-case package should identify both (a) overlapping fragments that lost assignment and (b) intervals overlapping no ground-truth rally. Do not suppress either class.

## Correct controls and falsification

GT7,17,18,24,30,32 and34 have relatively high IoU and small boundary errors and are useful observed control intervals; selecting them is diagnostic, not independent validation. Their actual CSV values remain in the fixed comparison. Also retain the34 short-candidate cancellations outside and inside labels as controls: a continuity change that converts floor pickups or false shuttle motion into full rallies can improve some missed labels while damaging production behavior.

Reject explanations when evidence contradicts them: (1) player stationarity is not the FSM's speed input; (2) a missing ReID checkpoint does not change the direct shuttle-motion start path; (3) a source/proxy clock shift cannot explain correctly aligned early fragments followed by large selected-fragment shifts; (4) a three-frame confirmation delay alone cannot explain a179-frame matched delay; (5) the proven configurable-window defect cannot explain a baseline that uses10; (6) no final cut reasons does not rule out cancelled cut candidates.

## Recommended experiment order

1. Reproduce exact baseline semantics from real cached perception and freeze the processed per-frame observation/contact/discontinuity stream.
2. Repair independently proven configuration/clock-accounting defects in isolated branches/configurations, with default-preserving tests; measure real affected counts before claiming benchmark benefit.
3. Ablate continuation evidence independently from start evidence and stationary-end localization. Use same observations to identify causal segmentation effects, then fresh inference to test upstream feedback through scheduling/identity/calibration.
4. Investigate perception failures at the actual split frames. Do not choose wider merge/minimum-duration settings from label gaps alone.
5. Require the original metrics, severe-case metrics, fragmentation, false positives during breaks and capability regressions before adoption. Test1 remains exploratory development data.
