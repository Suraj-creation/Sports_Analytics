# Independent Test 2 review — original fresh inference, separate postprocessing

**The results are mixed; cross-video nonregression and candidate acceptance are not established.** The coarse reference gains an additional missed interval, while the generated timing references gain precision but lose mean IoU. One short exchange needs pipeline diagnosis, and several boundary changes need annotation-convention/source review. Physical component accuracy remains unavailable.

## Exact execution provenance

The actual fresh neural run is `pre_test03_v4/test02_candidate_v4/run`, produced by **2418ab8cbe4cca74dd16b722b9727ffdc950294a** in the unchanged native producer checkout. Its original neural worker and executor genuinely completed all29,296frames. The original outer orchestration failed later during legacy analysis; its failure files remain unchanged and it has **no fabricated outer completion**.

The distinct `pre_test03_v4/test02_postprocessing_v1` contains new postprocessing only. Its completion declares `new_neural_inference=false`, `original_neural_inference_was_fresh=true`, preserved original failure, unchanged protected inputs and complete own-run semantic parity. New navigation links point to the actual original NN receipts; this review uses explicit original NN and postprocessing paths rather than treating those links as new inference.

[native_guard_receipt.json](native_guard_receipt.json) verifies the actual native worker/parent, exact Test2source/proxy identity and byte extent, all **3,620 original artifact hashes**,289recorded source files and **489native cache packets**, before consuming new metrics. It imports the actual producer helper/plugin with their actual ROOT, reuses the final adapter's `require_recorded_producer` to bind executor command/source-file population, and independently repeats native decoding/structural audit. Both new analysis/component compatibility receipts bind the unchanged numerical native functions and the same structural proof. No ROOT assignment, module monkeypatch, model inference or source/annotation modification occurs here.

Two initial review guard attempts stopped before metrics because this review incorrectly interpreted `plan.root` as a code-producer path; it is a protocol staging directory. Both logs/helper/config snapshots are preserved in `failed_guard_attempt_01/` and `failed_guard_attempt_02/`. The successful third attempt uses the adapter's exact explicit producer binding. These are review-tool corrections, not pipeline fixes. The previously prepared `test02_independent_v4` files remain untouched. **33review guard tests and6partition tests pass; final core review lint passes.**

Seven annotation hashes, profile and actual model identities match the preserved full-neural baseline. Three interval references use unchanged numerical matching, thresholds and tolerances. Ten unsupported physical-metric families remain null, including unsupported AP/tracking/pose/contact accuracy; null is not zero. All precision/recall/IoU below are agreement with the specific supplied reference, not manufactured physical labels.

## Complete reference results

Full matrices, matching policies, every changed row, missed IDs, extra predictions, overlap, boundary tolerances and start/end/duration distributions are preserved in [interval_reference_differences.json](interval_reference_differences.json). [reference_change_diagnosis.json](reference_change_diagnosis.json) separates ordinal-only changes from substantive changes without rematching predictions.

| Reference | TP / FP / FN before→current | Precision before→current | Recall before→current | F1 before→current | Mean IoU before→current |
|---|---|---|---|---|---|
| `Test2_Full.csv` coarse,75rows | 69/6/6 →68/6/7 | .920000→.918919 | .920000→.906667 | .920000→.912752 | .830665→.838095 |
| `Test2_Full_rally.csv`,73rows | 68/7/5 →68/6/5 | .906667→.918919 | .931507→.931507 | .918919→.925170 | .849311→.830790 |
| `win_predictions.csv`,73rows | 68/7/5 →68/6/5 | .906667→.918919 | .931507→.931507 | .918919→.925170 | .849311→.830790 |

The latter two references share generated timing; they are not independent corroborating physical ground truth. Predictions decrease75→74. Each reference reports47changed comparison rows, but coarse34are prediction-ordinal-only and13substantive; each generated reference has35ordinal-only and12substantive changes. Losing one prediction renumbers later predictions; do not describe every renumbered row as a new boundary defect.

| Matched-population MAE in seconds | Coarse before→current | Each generated reference before→current |
|---|---|---|
| Start | .820290→.785784 | .805392→.937745 |
| End | .584541→.595588 | .695588→.697549 |
| Duration | 1.126570→1.122549 | 1.300980→1.433333 |

Coarse matched population falls69→68. Its higher overall mean IoU partly excludes the newly missed row33, whose old IoU was.6. For the same68surviving matched rows, mean IoU changes.834057→.838095. This conditional improvement does not cancel the additional miss. Generated references retain the same68matched source rows; their mean-IoU decline therefore remains a real benchmark boundary-agreement regression.

### Highest-priority failure: coarse row33

The unchanged coarse reference interval is **11700–11760** (06:30–06:32). The old prediction **11715–11751** matched atIoU.6, start error+15frames, end error−9frames and duration error−.8s. Current has no match: row33is the sole newly lost matched coarse reference. No other coarse row becomes newly matched. The loss follows the new weak reset11691, but temporal ordering alone does not prove the reset's causal mechanism.

Independent spot inspection of preserved source frames [11715](../visual_test02_lost_short_event_v1/frame_0011715/source_resized.png), [11733](../visual_test02_lost_short_event_v1/frame_0011733/source_resized.png) and [11751](../visual_test02_lost_short_event_v1/frame_0011751/source_resized.png) shows a short active exchange: near blue-clad athlete's racket action, far red-clad athlete's return and subsequent movement. This supports treating the missing short exchange as a genuine concern rather than dismissing it as preparation. Exact contacts, winners and frame-accurate physical boundaries are still unreviewed. Trace contact admission/FSM/association through the complete retained semantic trace before selecting a fix.

### Largest generated-reference IoU loss: row3

Generated reference **807–1040**: old prediction809–1039→current904–1039. IoU.987124→.579399; signed start error+2→+97frames. The end is unchanged. Coarse row3starts900, a different boundary convention. Independent source spot inspection at [809](../visual_test02_delayed_start_row03_v1/frame_0000809/source_resized.png) shows walking/preparation, [850](../visual_test02_delayed_start_row03_v1/frame_0000850/source_resized.png) shows serve setup, and [904](../visual_test02_delayed_start_row03_v1/frame_0000904/source_resized.png) shows the near red-clad athlete's outgoing serve-like action. Thus the generated benchmark loss may remove preparation rather than demonstrate a3.17sphysical rally-start delay. Preserve both reference deltas and this uncertainty; do not silently change annotations or erase the regression. Exact serve-impact adjudication is not established by these three selected frames.

The worst surviving coarse IoU loss is row14: GT4650–4770, old4633–4769→current4681–4769, IoU.868613→.733333. It remains in the mandatory expanded source plan. Every changed row, not just these examples, is retained in the diagnosis JSON.

## Component population, source proofs and raw differences

[full_population_summary.json](full_population_summary.json), [population_change_intervals.json](population_change_intervals.json) and the full region ledgers preserve all count/region changes:58,452→58,101person rows,754lower-count frames across5960–6023,6030–6151,6154–6307,6310–6491and6498–6729;829historical regions lackIoU≥.5current overlap and478new regions lack historical overlap. These are model-image populations, not physical false negatives/positives. The historical official admission in this region means fewer boxes may remove an official, but each interval needs source classification rather than an automatic improvement label. Detector execution gains192frames and loses82; equal cadence is not claimed.

Generated player-point agreement, all-row assignments:57,305→57,708pairs, mean3.461802→3.277068px, maximum429.411529→256.206844px. Common57,305pairs have current mean3.270431;403new pairs have mean4.220835 and no old-only pairs exist. Fresh-detector assignments:24,129→24,509pairs, mean1.678630→1.618420px;23,967common pairs,542new and162old-only. Full distributions, common deltas, extremes and raw source bboxes are in [point_population_decomposition.json](point_population_decomposition.json). These compare generated legacy points, not AP or physical anatomical localization. Changing population and removing historical wrong-person matches must stay visible.

The native scene audit covers29,296frames,251relative camera claims and4cross-chunk claims. The nine weak barriers are355,699,1095,3394,4581,5958,11691,11985,25521. Total recorded content barriers change36→44:12new and4lost. All new/lost resets require source review; the plan includes them. At chunk120–179the serialized before-chunk format context differs from the previous post-chunk summary; [crosschunk_camera_format_audit.json](crosschunk_camera_format_audit.json) retains that runtime-order review flag rather than silently dropping it or calling it an established format bug. Native decoding/positive proof checks pass; this is not independent physical camera accuracy.

Unlike Test1, raw shuttle arrays are **not identical**. [raw_shuttle_difference_summary.json](raw_shuttle_difference_summary.json) records4,655XY differences,4,450support differences,419presence/status differences and460association-status differences. Association payloads differ on28,949frames, which can include episode/hypothesis provenance rather than a changed coordinate. [The full row ledger](raw_shuttle_value_status_association_differences.json) preserves before/current `s`, `c` and complete`sa` objects. Subpixel differences around11715–11750 and other changed evidence prevent attributing all semantic changes to scene logic alone. A held shuttle during preparation is not automatically a missing in-play detection. No physical shuttle-error metric or causal ablation is claimed.

## Events, models and resources

The actual full-neural baseline has816contacts/strokes and75rallies; current has823contacts/strokes and74rallies. Unknown stroke labels586→593, identity-ambiguity events48→56, shuttle-turn events58→43. Named contact actors remain0and known rally winners remain0; these are output coverage/abstention, not0%measured accuracy. All exact-anchor event/anonymous actor/class differences are retained in [event_differences.json](event_differences.json). Changed rally context can make nearby-event association unavailable; the existing fallback explicitly retains exact-anchor set differences rather than inventing shifted-event identity.

The selected profile/model checkpoint identities are unchanged. Actual raw cache codec23and producer identity remain recorded. Fresh worker cumulative CPU time is38,399.944s versus37,556.787s baseline; maximum RSS2,976,436,224bytes versus3,194,896,384; sampled peak GPU memory2,122MiB in both. These are original worker measurements, not this postprocessing's compute. Neural-only throughput and failure-inclusive original outer elapsed fields are unavailable/null. New continuation elapsed time is separate in its completion receipt. Full environment/models/stage latency/resource series are preserved in [runtime_provenance_review.json](runtime_provenance_review.json); no new inference runtime is fabricated.

## Review coverage and next gate

The complete diagnostic source plan contains **664frames**. Three existing completed bundles contain75+86+111=272rendered frame entries; after overlap and intersection with this plan, **214requested frames are reused and450remain**, split into128/128/128/66frames. [visual_evidence_partition_v2.json](visual_evidence_partition_v2.json) verifies all three bundles' input/output hashes, binds their completion receipts and lists the exact four new pending batch files under `pending_source_frame_plans_v2/`. No requested case is dropped; already rendered800–910and11690–11775are excluded from new batches. Earlier two-bundle partition files remain preserved and are superseded for launching additional renders.

**This reviewer independently spot-viewed six source frames at this stage, not all664.** Additional visual review, short-exchange diagnosis, source classification of changed boundaries/population and any proposed fix/regression remain pending. This report seals the numeric/provenance review and honest mixed result; it does not accept Test2, authorize Test3, overwrite historical benchmarks or turn model outputs into ground truth.
