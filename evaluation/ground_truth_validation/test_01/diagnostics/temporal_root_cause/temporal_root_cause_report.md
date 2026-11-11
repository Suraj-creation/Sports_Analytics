# Test1 temporal root-cause and bounded correction review

Baseline: fresh current improved pipeline at `../ground-truth-validation-artifacts-20261110/test_01/baseline_v1`. This audit reads all17,268 step traces,485 contact-evidence callbacks,403 discontinuity callbacks, the14 significant boundary cases, and preserved reference variants. No original annotations, frozen baseline outputs or original production-checkout files were changed. The only candidate production change is in the root-assigned isolated worktree.

## Confirmed code defect: stale active frontier after recovery

`RallyFSM.step()` updated `_last_in_play_frame` only when its entry state was IN_PLAY. CLOSED→IN_PLAY observed-motion recovery and ENDING→IN_PLAY observed resume consumed a current frame but left the prior active frontier unchanged. A following discontinuity used that stale value to end the rally, losing accepted recovery observations. This is a deterministic timeline/state defect independent of reference labels.

Reproduction uses unchanged default `RallyParams(fps=30)`: observed frames0–100; missing101–115 closes a mergeable gap with end100; observed116–118 reopens; cut119 incorrectly emits end110 instead118. ENDING resume at111 followed by cut112 similarly incorrectly emits110 instead111. A delayed cut without newly processed frames must still end at the last actually processed frame100, not invent199.

## Minimal candidate correction and regression proof

Assigned worktree: `/home/administrator/Desktop/sport-analytics/test01-pipeline-fixes-20261110`. After every normal FSM step, if its final state is IN_PLAY, record the consumed current frame as `_last_in_play_frame`. Replay/discontinuity returns precede that update. Tentative end and closed segment policies remain unchanged. No numeric thresholds, matching rules, contact coordinates or GT-conditioned frame exceptions were changed.

See [five-line patch relative to actual improved baseline](recovery_cut_frontier_only.patch), [source/hash receipt](recovery_cut_fix_receipt.json), [worktree import proof](worktree_import_path.log), [RED log](worktree_recovery_cut_red.log), and [GREEN log](worktree_recovery_cut_green.log).

New dedicated regression file: `sports/badminton/tests/test_rally_recovery_cut_frontier.py`; tests both base and evidence FSMs. RED:6 failures and8 control passes. GREEN focused group:156 passed in1.50s. Controls preserve missing-evidence closure, earlier tentative ends, delayed-cut no-future behavior, replay exclusion and flush semantics. The new14-test set verifies externally visible segment ends, not merely an implementation-mirroring private variable.

Focused command (original GPU environment and original venv, with worktree PYTHONPATH first):

```bash
source /home/administrator/Desktop/sport-analytics/gpu-env.sh
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src:$PWD"
/home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/bin/python -m pytest sports/badminton/tests/test_rally_recovery_cut_frontier.py sports/badminton/tests/test_rally_temporal_correctness.py sports/badminton/tests/test_rally_evidence_v2.py sports/badminton/tests/test_rally_evidence_segments.py sports/badminton/tests/test_rally_image_exit_evidence.py sports/badminton/tests/test_rally_terminal_admission.py sports/badminton/tests/test_rally_observed_continuity.py sports/badminton/tests/test_rally_short_exchange_evidence.py sports/badminton/tests/test_rally_terminal_admission.py -q
```

The logged focused command includes terminal-admission twice; it is reproduced verbatim rather than inflating its pass count into independent scenario coverage.

## Baseline relevance is explicitly bounded

The baseline contains6 motion-driven CLOSED reopenings at frames4407,5101,11392,11635,13153,13174. None of those or the ENDING resumes is followed by an immediate next-frame discontinuity. Therefore this correction is **not established as a cause of the14 Test1 errors**, and no Test1 detection/IoU/boundary improvement is claimed. Fresh before/after inference and unchanged-label evaluation remain the orchestrator’s next verification.

## All14 significant cases: actual gates

| G ID | GT frames | Prediction frames | Δstart / Δend frames | Start evidence kinds over disagreement span | Contact frames in start span | Content epochs | End evidence kinds | Diagnosis status |
|---|---|---|---|---|---|---|---|
| 4 | 1874–2161 | 1803–2167 | -71 / 6 | {'observed': 31, 'missing': 41} | [1803, 1816, 1828] | [0] | {'observed': 7} | Earlier candidate contact opens before reference start; early start may include preparation. No physical impact label certifies either boundary. |
| 5 | 2210–2500 | 2308–2496 | 98 / -4 | {'missing': 60, 'observed': 39} | [2221, 2237, 2249] | [1] | {'observed': 5} | Earlier contact candidate cancelled by duration/witness policy; later evidence opens retained interval. Physical completeness requires temporal video review. |
| 8 | 3451–3695 | 3519–3699 | 68 / 4 | {'invalid': 16, 'observed': 7, 'missing': 46} | [] | [1] | {'observed': 5} | No start-span contacts; invalid/missing evidence delays motion launch. Missing evidence is not proof of missing physical rally. |
| 9 | 3751–4073 | 3857–4059 | 106 / -14 | {'invalid': 17, 'missing': 49, 'observed': 41} | [3771, 3790, 3798] | [1] | {'observed': 9, 'missing': 6} | Earlier contact candidate cancelled by duration/witness policy; later evidence opens retained interval. Physical completeness requires temporal video review. |
| 10 | 4247–4839 | 4272–4804 | 25 / -35 | {'missing': 13, 'observed': 13} | [4272] | [1] | {'observed': 33, 'missing': 3} | Stationary end4804; reference extends across observed edit4837. Do not extend temporal threshold merely to fit reference. |
| 11 | 4872–5045 | 4901–5027 | 29 / -18 | {'missing': 12, 'observed': 18} | [4901] | [2] | {'observed': 19} | Observed/missing motion and stationary terminal; physical end not certified by reference alone. |
| 14 | 6382–6656 | 6450–6639 | 68 / -17 | {'invalid': 12, 'missing': 51, 'observed': 6} | [] | [2] | {'observed': 1, 'missing': 17} | No start-span contacts; invalid/missing evidence delays motion launch. Missing evidence is not proof of missing physical rally. |
| 15 | 6716–6913 | 6802–6908 | 86 / -5 | {'invalid': 2, 'missing': 50, 'observed': 35} | [6732, 6744] | [2] | {'observed': 6} | Earlier contact candidate cancelled by duration/witness policy; later evidence opens retained interval. Physical completeness requires temporal video review. |
| 16 | 6976–7458 | 7006–7502 | 30 / 44 | {'invalid': 17, 'missing': 12, 'observed': 2} | [] | [2] | {'observed': 42, 'missing': 3} | No start-span contacts; invalid/missing evidence delays motion launch. Missing evidence is not proof of missing physical rally. |
| 20 | 8683–9967 | 8715–9947 | 32 / -20 | {'invalid': 16, 'missing': 11, 'observed': 6} | [] | [5] | {'observed': 1, 'missing': 20} | No start-span contacts; invalid/missing evidence delays motion launch. Missing evidence is not proof of missing physical rally. |
| 23 | 10733–11078 | 10775–11085 | 42 / 7 | {'missing': 19, 'observed': 24} | [10738, 10775] | [7, 8] | {'observed': 8} | GT-start disagreement spans content epochs7→8 and prior retained exchange; reference/camera continuity requires source review. |
| 25 | 11568–11865 | 11613–11867 | 45 / 2 | {'observed': 22, 'missing': 24} | [11570, 11583, 11613] | [8] | {'observed': 3} | Earlier contact candidate cancelled by duration/witness policy; later evidence opens retained interval. Physical completeness requires temporal video review. |
| 28 | 13054–13442 | 13115–13439 | 61 / -3 | {'invalid': 2, 'missing': 56, 'observed': 4} | [] | [9] | {'observed': 1, 'missing': 3} | No start-span contacts; invalid/missing evidence delays motion launch. Missing evidence is not proof of missing physical rally. |
| 33 | 15596–15946 | 15664–15951 | 68 / 5 | {'missing': 51, 'observed': 18} | [15601, 15611] | [10] | {'observed': 6} | Earlier contact candidate cancelled by duration/witness policy; later evidence opens retained interval. Physical completeness requires temporal video review. |

Full per-frame transition/callback inventories and evidence-kind counts are in [significant_case_gate_audit.json](significant_case_gate_audit.json). They separate causal software gates from unverified physical explanations. “Observed” here means accepted pipeline observation, not independently labelled correctness.

## Representative cancellation mechanisms

- G5: contacts2221/2237/2249 exist. Candidate2221 closes and is cancelled at2277; a new observed-motion run confirms at2310 with start2308. Calling this “no contacts detected” would be wrong.
- G9: candidate3771 receives further contacts3790/3798, but closes and is cancelled at3827; later start3857 confirms at3859.
- G15: candidate6732 with contact6744 is cancelled at6773; later motion confirms start6802 at6804.
- G25: candidate11570 with contact11583 is cancelled at11610; next accepted contact11613 opens retained rally.
- G33: candidate15601 with contact15611 is cancelled at15638; later motion confirms start15664 at15666.

These observations isolate maturity/continuity gates and insufficient independent short-exchange witnesses. They do not authorize lowering minimum duration or extending gaps to match labels: earlier activity may be preparation/pickup or a genuine partly missed exchange. The existing witness rules require opposite simultaneous observed episodes and independent motion; inspect that evidence before a change.

## Visual checks against reference-fitting shortcuts

The baseline visual package was inspected for frames1803,2210,2308,4804,4837. At1803 and2210 the near athlete is raising racket/arms while the far athlete is waiting; isolated stills cannot establish serve/contact timing. At2308 the far athlete is in an overhead posture, which confirms a visible action but not the first physical rally frame.

At4804, a small white object is visible near the near court floor while athletes are repositioning; the scoreboard reads7:11. At4837 the scoreboard reads9:12 and the athletes are in a new preparation view. Thus the source includes an edit before the supplied G10 reference end4839; extending current4804 ending through4839 would risk including a different context. This is concrete visual/reference disagreement, not proof of a current scene-reset bug.

The earlier source-alignment review independently found G20 reference start8683 in an athlete closeup after courtwide8640. Its first32 reference-start frames include invalid/missing evidence before motion-based start8715. That supports contextual qualification of the reference rather than inventing play during a closeup.

## Boundary variants for each case (best temporal overlap, diagnostic only)

This cross-reference is a nearest-overlap diagnostic, not a one-to-one scored evaluation or a permission to transfer labels by row order. Full2 has only20 numeric rows; its literal ellipsis record remains documented in the dataset audit. Zero-overlap rows are shown as unavailable.

| G ID | Primary supplied _rally frames | Coarse Full.csv nearest interval | rev_T nearest interval | rev_T4 nearest interval | Partial Full2 nearest interval |
|---|---|---|---|---|---|
| 4 | 1874–2161 | row4: 1800–2160 (IoU0.792) | row4: 1874–2161 (IoU1.000) | row5: 1874–2161 (IoU1.000) | row4: 1874–2161 (IoU1.000) |
| 5 | 2210–2500 | row5: 2250–2490 (IoU0.828) | row5: 2410–2500 (IoU0.310) | row6: 2210–2500 (IoU1.000) | row5: 2410–2500 (IoU0.310) |
| 8 | 3451–3695 | row8: 3450–3690 (IoU0.976) | row8: 3451–3685 (IoU0.959) | row10: 3451–3695 (IoU1.000) | row8: 3451–3685 (IoU0.959) |
| 9 | 3751–4073 | row9: 3780–4050 (IoU0.839) | row9: 3751–4033 (IoU0.876) | row11: 3751–4073 (IoU1.000) | row9: 3751–4033 (IoU0.876) |
| 10 | 4247–4839 | row10: 4260–4800 (IoU0.912) | row10: 4247–4812 (IoU0.954) | row12: 4247–4839 (IoU1.000) | row10: 4247–4812 (IoU0.954) |
| 11 | 4872–5045 | row11: 4890–5010 (IoU0.694) | row11: 4872–5018 (IoU0.844) | row13: 4872–5045 (IoU1.000) | row11: 4872–5018 (IoU0.844) |
| 14 | 6382–6656 | row14: 6390–6660 (IoU0.957) | row14: 6382–6628 (IoU0.898) | row16: 6382–6656 (IoU1.000) | row14: 6382–6628 (IoU0.898) |
| 15 | 6716–6913 | row15: 6750–6900 (IoU0.761) | row15: 6716–6903 (IoU0.949) | row17: 6716–6913 (IoU1.000) | row15: 6716–6903 (IoU0.949) |
| 16 | 6976–7458 | row16: 6990–7470 (IoU0.947) | row16: 6976–7458 (IoU1.000) | row18: 6976–7458 (IoU1.000) | row16: 6976–7458 (IoU1.000) |
| 20 | 8683–9967 | row20: 8670–9960 (IoU0.985) | row20: 8683–9967 (IoU1.000) | row22: 8683–9967 (IoU1.000) | row20: 8683–9967 (IoU1.000) |
| 23 | 10733–11078 | row23: 10770–11070 (IoU0.870) | row23: 10733–11078 (IoU1.000) | row25: 10733–11078 (IoU1.000) | No overlap |
| 25 | 11568–11865 | row25: 11550–11880 (IoU0.900) | row25: 11568–11865 (IoU1.000) | row27: 11568–11865 (IoU1.000) | No overlap |
| 28 | 13054–13442 | row28: 13110–13440 (IoU0.851) | row28: 13054–13442 (IoU1.000) | row30: 13054–13442 (IoU1.000) | No overlap |
| 33 | 15596–15946 | row33: 15600–15960 (IoU0.951) | row33: 15596–15946 (IoU1.000) | row35: 15596–15946 (IoU1.000) | No overlap |

## Priorities after the bounded frontier correction

1. Review continuous opening/cancellation intervals against source video and all references; classify preparation, floor pickup, airborne exchange or unresolvable evidence without using supplied boundaries as physical proof.
2. Trace actual invalid-camera/calibration gates at delayed starts before changing rally thresholds.
3. Separate terminal stationary observations, physical landing/contact uncertainty and label spans that cross edits.
4. Retain the frontier fix as a correctness regression; evaluate fresh before/after output without claiming metric gains from synthetic controls.
5. Keep contact evidence and anonymously tracked episode support source-bound; do not invent hitter identity or point outcomes to explain score annotations.

