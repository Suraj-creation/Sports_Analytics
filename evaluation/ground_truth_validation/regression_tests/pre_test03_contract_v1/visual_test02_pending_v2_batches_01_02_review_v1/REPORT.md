# Independent Test 2 visual review: pending batches 01–02

The two closed render batches pass the independent artifact and selected-pixel checks. All **256 selected frames** were visually inspected in 64 source/current/baseline contact sheets. The source edits at **2927→2928** and **11081→11082** are independently visible but do not reset the current content epoch. These are scene-acquisition regressions relative to the baseline and prevent a blanket preservation claim. Correct current athlete acquisition at these frames does not prove that temporal scene state was reset.

This is a diagnostic review of selected source frames, not physical ground truth or full-video accuracy validation. No pipeline, model, annotation, metric, matching method, or historical report was changed. No inference was run. Acceptance remains with the orchestrator.

## Provenance and verification

The executed current producer is `2418ab8cbe4cca74dd16b722b9727ffdc950294a`; its original completed fresh Test 2 worker is preserved. Its original outer analysis failure remains preserved. The separate completed continuation performs postprocessing of that original worker and does not represent another neural run. The sealed [numeric review](../test02_postprocessing_independent_v1/REPORT.md) records those guards and the mixed metric results. This visual review is a new sibling and does not amend that sealed history.

The original source video SHA256 is `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`. Source frames are decoded with original PTS; overlays use the bound canonical proxy. The review checked 3,102 output file hashes, 2,030 declared input bindings across both receipts, and 768 source/current-proxy/baseline-proxy pixel bindings. Shared input paths are hash-memoized using path, byte count, and modification time. These are receipt-binding counts, not necessarily unique files.

See [verification](verification.json), [per-frame typed data](per_frame_diagnostic_index.json), [viewing record](reviewed_pages.json), and [finding records](visual_findings.json). Each selected frame retains its exact original pixels, PTS, raw model row, and source/current/baseline overlay in the immutable render directories. Contact sheets resize the 1280×720 image area to 480×270 and exclude overlay footers; high-resolution originals were additionally inspected for the principal cuts and carried-box failures. Fine shuttle/contact localization is not established from these sheets.

## Confirmed source edit regressions

| Transition | Source observation | Current typed output | Diagnostic conclusion |
|---|---|---|---|
| 2927→2928, 97.567→97.600 s | Near red changes from bent central posture to a displaced left/ready position; far blue also jumps toward a different central position. The visible score remains 5:5. | Epoch 6 unchanged; `p=2`, both fresh current athlete boxes; `fg=3`, including an old region as blue image context. | Abrupt source edit missed by the current scene reset. This is not a score-only judgment and not a third admitted person. |
| 11081→11082, 369.367→369.400 s | Near blue changes from bent/left to central ready posture; far red relocates from the left to the centre. The visible score graphic does not supply the edit judgment. | Epoch 19 unchanged; `p=2`, both fresh athlete boxes; `fg=4`, including prior-position image context. Raw scene evidence records insufficient independent witnesses. | Abrupt source edit missed by the current reset, despite fresh current athlete boxes. Full causal gate analysis is owned by the component review. |

Evidence: [2927 original](../visual_test02_pending_v2_batch_01/frame_0002927/source_original.png), [2928 original](../visual_test02_pending_v2_batch_01/frame_0002928/source_original.png), [2928 current overlay](../visual_test02_pending_v2_batch_01/frame_0002928/current_proxy_overlay.png), [11081 original](../visual_test02_pending_v2_batch_02/frame_0011081/source_original.png), [11082 original](../visual_test02_pending_v2_batch_02/frame_0011082/source_original.png), [11082 current overlay](../visual_test02_pending_v2_batch_02/frame_0011082/current_proxy_overlay.png).

`p` is admitted participant output. `fg` is detached image context; blue boxes do not grant participant, identity, contact, or scoring authority. The old empty blue region at 2928 must not be described as an admitted stale player. The analogous distinction applies at 11082 and to the other context boxes in this review.

## Lower-count intervals: background population removal

All **40 selected controls** lying within the five lower-count intervals below show the current two intended athletes retained and the baseline's extra seated background official removed. The baseline official is above/behind the far court, not a third match participant. This is qualitative source interpretation, not annotated detection precision or recall. Only the selected controls were visually reviewed; it is not a claim that every one of the 754 interval frames has been physically labelled.

| Lower-count interval | Selected controls reviewed | Typed counts current / baseline |
|---|---:|---|
| 5960–6023 | 6 | 2 / 3 throughout these controls |
| 6030–6151 | 1 | 2 / 3 |
| 6154–6307 | 6 | 2 / 3 throughout these controls |
| 6310–6491 | 8 | 2 / 3 throughout these controls |
| 6498–6729 | 19 | 2 / 3 throughout these controls |

The current boxes coarsely cover both source athletes in these controls, including ordinary play, lunges, and the bent far athlete at 6729. Fresh/carried provenance is preserved in the per-frame JSON. Examples: [5960 current](../visual_test02_pending_v2_batch_01/frame_0005960/current_proxy_overlay.png), [5960 baseline](../visual_test02_pending_v2_batch_01/frame_0005960/baseline_proxy_overlay.png), [6729 triptych](sheets/batch_02_page_08.png). Removing an official is compatible with separate temporal/rally failures elsewhere; count reduction alone is not evidence of athlete recall loss or gain.

## Inherited carried-box lag and acquisition differences

At **8567**, both arms have the same single carried admitted box over empty court, while the two source athletes occupy different visible locations. This is actual stale `p` output, unlike the context-only old regions above. At **8568**, current output reacquires both athletes fresh while baseline output is empty. At **9513**, both arms carry identical displaced boxes: the far box is on empty court to the right of the far athlete, and the near box is offset. At **9514**, the current run acquires both athletes fresh while baseline retains only the near athlete. These source-bound examples expose unresolved acquisition/cadence lag; they are not newly introduced candidate-only stale boxes.

Evidence: [8567 current](../visual_test02_pending_v2_batch_02/frame_0008567/current_proxy_overlay.png), [8568 current](../visual_test02_pending_v2_batch_02/frame_0008568/current_proxy_overlay.png), [9513 current](../visual_test02_pending_v2_batch_02/frame_0009513/current_proxy_overlay.png), [9514 current](../visual_test02_pending_v2_batch_02/frame_0009514/current_proxy_overlay.png). Raw frame data records `detector_executed=false` and `dm=false` on 8567/9513, and fresh detections on their next selected frames. This does not establish the exact first frame of either source edit because the immediately preceding source frame is not in this pair's review scope.

Several other selected edit/acquisition controls show current two-athlete output while baseline temporarily clears or suppresses an athlete, including 357, 701, 1097, 1829, 2451, 2679, 3866, 3942, 3994, 4257, 4810, 5174, 5505, 6747, 7012, 7184, 7632, 10230, 10366, 12102, 12298, 12602 and 12798. These are observations of output coverage at selected source frames, not physical AP/IDF1. Carried estimates remain visibly less current than fresh boxes at some ordinary-motion frames. Track episode numbers are anonymous and cannot establish named identities or scoreboard ownership.

## Boundary/reference convention caution

The sealed coarse row 14 loss remains: reference 4650–4770, old prediction 4633–4769, current 4681–4769, IoU 0.86861314→0.73333333. Selected source frames 4633, 4647 and 4675 show near red preparing a serve with far blue ready; the later 4681/4683 frames show action beginning. This supports a preparation-versus-active-event convention ambiguity, not an independently labelled physical contact or a reason to rewrite the supplied reference. The numerical loss must stay reported. [Preparation/action triptychs](sheets/batch_01_page_24.png), [later selected frames](sheets/batch_01_page_25.png).

The larger generated row 3 shift and the missed short coarse row 33 event belong to already rendered separate contiguous bundles. Their preserved numeric and initial source findings are in the sealed numeric review. This report does not claim to have visually reviewed their full 111/86-frame bundles. The other lost cuts 22416/23279 and batches 03/04 are assigned to a separate reviewer. All 664 requested frames being rendered does not mean this reviewer inspected all 664.

## Remaining uncertainty and disposition

Raw classical racket ellipses still often sit near heads, body edges, or banners; they remain model estimates and are not verified contacts. Some cyan shuttle marks remain at suspicious banner/background positions in both arms, while the full Test 2 shuttle arrays also differ between arms. Selected panels cannot resolve all shuttle presence/localization or assign every event difference to scene code. Pose overlays at coarse scale do not supply joint ground truth. No named player, shot class, physical contact, winner, point, or score sequence is validated here.

The review confirms useful acquisition/background improvements alongside unresolved source resets and inherited carried-box lag. It therefore supports continued diagnosis before acceptance, with the unchanged reference matrices and uncertainty preserved. No cleanup, Test 3 processing, publication, or code change was performed by this review.
