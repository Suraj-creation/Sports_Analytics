# Test 2 cross-test regression: candidate 2418ab8

Status: complete fresh inference, postprocessing and independent numeric review. **Rejected for advancing to Test 3 pending missed-edit repair.** Broader source review confirmed real temporal edits that the candidate fails to reset. Main remains dacc05e; the actual candidate production code remains isolated and unchanged between Test 1 and Test 2.

| Reference | Baseline TP/FP/FN | Candidate TP/FP/FN | Baseline P/R/F1 | Candidate P/R/F1 | Mean IoU before → after |
|---|---|---|---|---|---|
| Coarse Test2_Full.csv |69/6/6|68/6/7|0.9200/0.9200/0.9200|0.918919/0.906667/0.912752|0.8306646002 → 0.8380953372|
| Generated Test2_Full_rally.csv |68/7/5|68/6/5|0.906667/0.931507/0.918919|0.918919/0.931507/0.925170|0.8493108146 → 0.8307896604|
| win_predictions.csv timing |68/7/5|68/6/5|0.906667/0.931507/0.918919|0.918919/0.931507/0.925170|0.8493108146 → 0.8307896604|

The third timing reference duplicates the generated reference; it is not another independent sample population. All seven original annotation/supporting files are accounted for. Numeric matching, IoU eligibility, boundary tolerances, annotation bytes and original predictions were not edited to improve scores. Physical AP, tracking identity, pose, shuttle/contact/stroke/outcome/score/highlight accuracy families remain null where independently reviewed truth is absent.

All start/end signed and absolute errors, duration errors, tolerances, matched rows, missed/extra IDs, point comparisons, court diagnostics, class/unknown coverage, model fingerprints, runtime/resource values and downstream products are in the [complete comparison](../test_02/pre_test03_2418ab8_v1/comparison.md) and [component matrices](../test_02/pre_test03_2418ab8_v1/metrics/). The [workspace index](../test_02/pre_test03_2418ab8_v1/README.md) preserves original inference and separate postprocessing locations.

## Newly observed regressions requiring investigation

Coarse reference33 [11700,11760), 06:30–06:32, is newly missed. Its original prediction [11715,11751) disappears. The current trace starts activity at11716 and cancels it at11774: the finalized short exchange lacks qualified witness frames and participant proof under the existing duration/evidence policy. The preceding reset11691 corresponds to a real source edit with athlete relocation and skipped broadcast points. Neither fact alone proves whether the lost short event is a code defect or the baseline relied on invalid prior-epoch evidence. The complete [86-frame source comparison](../regression_tests/pre_test03_contract_v1/visual_test02_lost_short_event_v1/index.md) and full semantic trace are retained.

Generated reference3 has the largest individual overlap loss: prediction start809→904 with end1039 unchanged, IoU0.9871244635→0.5793991416. Reference13 start4633→4681 gives0.7727272727→0.5000000000. Other boundary changes remain in the complete row matrices, including improvements. All regressions must be explained before cross-test acceptance; a higher F1 on one supplied reference is insufficient.

Both actual canonical proxy SHAs equal2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd. Some cached raw shuttle coordinates differ by subpixels between fresh runs. Subsequent implementation tracing found a material input difference: the pipeline passes combined camera-shot/content-epoch IDs to TrackNet; TrackNet uses that same ID for both temporal-window isolation and its median-background reservoir. New valid content edits therefore also reset the median history. At809 the recorded peak changes from0.51318 to0.13770 under the unchanged0.5 threshold, while a later4672–4679 diagnostic retains equal window-vote counts but different background hashes. Equal source/weights do not imply equal model tensors. This is a confirmed input/lifecycle difference and a likely regression cause; whether/how static background memory can safely be preserved independently of dynamic trajectory state remains under investigation. No cross-cut temporal window or threshold bypass is proposed. New anonymous tracks, contacts or classes do not establish better physical accuracy.

## Execution and preservation

The actual fresh GPU1 worker processed29,296 frames in3504.397877 seconds, versus3381.987166 seconds in the preserved fresh baseline. Shared host workload and overlapping stage timers prevent a controlled speedup claim. No neural inference was repeated for postprocessing. Full native semantic replay agrees with the original current run. Original failed outer analysis, successful worker/parent/cache receipts, all3,620 original artifact files and protected source/model/annotation inputs were verified unchanged. Separate postprocessing retained2,111 output hashes and completed in472.57 seconds.

Canonical heatmap export contains zero admitted grids; this is missing named/official evidence coverage, not verified zero movement or spatial accuracy. Unknown winners and unsupported score sequences remain unknown. The source video remains available for diagnosis; no media cleanup or Test 3 access has taken place.

## Missed real edits discovered in expanded source review

The candidate adds12 reset frames but loses original barriers2928,11082,22416 and23279. Source pairs2927→2928 and11081→11082 independently confirm real athlete relocations under the same camera, despite unchanged score displays. Current epochs6/19 do not increment. Remaining two source windows are being rendered/reviewed; no harmless-removal claim is made. This blocks cross-test acceptance independently of rally F1.

At11082, two source correspondence ratios20.2866/26.8157 and mean23.5511 pass unchanged3×/15 evidence gates, but both are discarded because their prior full rectangles overlap. The same geometric exclusion also blocks a single-witness acquisition request. An isolated experiment will measure exclusive feature origins while preserving full boxes for layout/background exclusion; it is not yet a validated pipeline fix. Lucas–Kanade patch support can extend outside origin masks, so fully independent photometric evidence is not claimed.

**Interpretation correction:** raw2928 has2 admitted fresh persons and3 scene-only foreground regions; the blue old empty rectangle is scene-only image context. It is not an admitted stale athlete. The [correction receipt](../regression_tests/pre_test03_contract_v1/test02_scene_context_interpretation_correction_v1.json) preserves the initial root misreading and correction without altering source or outputs.
