# Bounded source validation of scene-only foreground continuity

The candidate at `5b6d429b277e60837146ee02361a9961076079b6` restores the two source-confirmed Test1 cuts7857 and8106 without restoring offcourt participant authority. Ten chronological component windows pass their specified controls. This supports proceeding to complete fresh Test1–2 regression; it does **not** establish full-video benchmark acceptance or physical detection, contact, stroke, identity, winner, or scoring accuracy.

## Trial design and provenance

All three arms use the same exact decoded source pixels, original recorded geometry and detector-rate schedule, and source/crop-bound RFDETR proposals:

- `original`: exact MAIN dacc05e source, original tracker birth behavior, rolling observed offcourt membership, original two-to-four/all-region content screen.
- `c7`: exact frozen c7cf871 source with immediate birth and last-in-court authority lease, original content input from admitted persons.
- `foreground`: immediate birth and the unchanged strict participant lease, plus separate court-origin image context and V3 explicit independent witness evidence.

[First trial7ed2f73](prefix_v1/summary.json) completed normally but failed the7857 acceptance control. The [second trial5b6d429](prefix_v2/summary.json) includes bounded ambiguous-match retention and passes that control. Both unchanged control arms are **exactly equal on every row** across all ten trials: [control parity receipt](prefix_v2/control_parity_receipt.json). This is a component intervention using controlled scheduling, not a semantic replay or complete pipeline run. Pose, shuttle, contacts, strokes, rallies/FSM feedback and scores are not executed by this helper. No CSV, winner label or other annotation is passed into it.

Both trials preserve the actual helper bytes, all per-frame evidence and panels, exact original control source copies, clean candidate commit and source hashes. All164 candidate source/config files were independently recovered from each executed Git commit and checked against the run's captured hashes: [v1 receipt](prefix_v1/source_commit_receipt.json), [v2 receipt](prefix_v2/source_commit_receipt.json). No production input changed during either trial. Original worker/parent/catalogue completion, source/proxy identity, cached segment hashes, checkpoint SHA, current detector preprocessing/decoder AST, exact source/crop hashes, and seed output hashes were checked. The checkpoint is `rfdetr_s_v142_512x512.onnx`, SHA `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e`; input512×512 and support threshold0.35 are unchanged.

The first trial executed282 previously unavailable detector crops; all other observations were already retained. The second trial executed **zero fresh neural detector calls**, reusing911 distinct exact model observations through2728 retained lookups. It still executes current tracking/content logic on2399 chronological source frames, three independent arms each. This distinction prevents reused NN predictions from being described as fresh model inference. Both use physical GPU1 visibility; ORT reports CUDAExecutionProvider plus CPUExecutionProvider. These prefixes provide no end-to-end runtime/resource comparison. Full worker runtime, GPU/CPU resources, labels and all annotation metrics must come from the separate native full regressions.

## All window results

Entries are local content-barrier source frames, not ground-truth scene precision/recall. No scene labels were manufactured and numeric track IDs were not scored as physical identity. Capacity overflow is zero in every new-arm window; the maximum observed foreground population is four. Singles/doubles and eight-region/overflow behavior also have focused synthetic contracts; these two real videos alone are not doubles-generalisation evidence.

| Source window | Original | c7 | Initial scene trial | Final scene trial | Max image regions |
|---|---|---|---|---|---|
| Test1, 0–80 | none | none | none | none | 2 |
| Test1, 235–310 | none | none | none | none | 2 |
| Test1, 7650–8150 | 7857, 8106 | none | 8106 | 7857, 8106 | 3 |
| Test1, 9000–9060 | none | none | none | none | 2 |
| Test2, 300–365 | none | none | none | none | 4 |
| Test2, 5505–6510 | none | 6307 | 6151, 6307 | 6151, 6307 | 4 |
| Test2, 7640–7740 | none | none | none | none | 2 |
| Test2, 11300–11360 | none | none | none | none | 3 |
| Test2, 23570–23680 | none | none | none | none | 2 |
| Test2, 25206–25540 | none | none | none | none | 4 |

## Exact failure chain and repair

At source7801, the far athlete's participant authority expires correctly: latest fresh in-court anchor7770, outside observation7800, unchanged30-frame authority limit. The separate image context initially keeps the athlete visible to the scene observer.

At7806, two raw detector boxes overlap the previous far-athlete image box at the existing0.3 gate: actual athlete IoU0.636083 and nearby official IoU0.360303. The initial7ed2f73 image memory deletes the original key on this ambiguity. Because the athlete remains offcourt, it cannot create a new court-origin key. A transient ambiguous observation therefore becomes permanent context loss. At7812, the athlete is again the unique spatial match (IoU0.558191, official0.216148), but the deleted key cannot recover. At7857, only one prior region reaches content; the observer safely abstains and the old near-player box survives on visibly empty right court through7859.

The final change treats ambiguous raw correspondence as bounded **missing image evidence**, the same contract as an empty fresh detector result. It retains the previous box and its original fresh timestamp, with `detector_matched=False`; ambiguous boxes never renew freshness, participant membership or identity. A later unique observation can recover the visual episode before the existing freshness bound expires. Overlapping proposals cannot seed duplicates of existing image context. Expired, reset or never-court-origin outside episodes cannot resurrect themselves.

In the final trial, key`court-origin:0` is explicitly unmatched at7806 and fresh again at7812. At7857, both independent prior witnesses support the existing image-change thresholds, the current detector-layout decision corroborates the reset, and current athletes are freshly detected. The stale right-court box is absent. At7858–7859 the new current-frame detections are carried as **unobserved**, rather than the pre-edit box. At8106 the second missed cut is also recovered. The same logic never turns these visual episode keys into physical player names or point winners.

[7857 three-arm source comparison](prefix_v2/test1_07650_08150_frame_07857.png), [7858](prefix_v2/test1_07650_08150_frame_07858.png), [7859](prefix_v2/test1_07650_08150_frame_07859.png), [8106](prefix_v2/test1_07650_08150_frame_08106.png). Green/orange outlines are participant observations/carries; cyan is detached image context. Visual review is diagnostic evidence, not an exhaustive labelled metric.

## Preserved controls and independently reviewed new recovery

Test2 at5958 and6492 keeps both current athletes while excluding the official from participant output. Detached image context may include an official-like image episode but grants it no participant authority. The true edit6307 remains acquired. At source23639, complete positive current-layout correspondence explicitly vetoes a raw two-witness hypothesis. At7703, the final bounded window finds insufficient independent witnesses and produces neither hypothesis nor decision. Both remain free of resets;7703 is not a positive-layout-veto example in this bounded startup.

The additional6151 barrier is independently source-reviewed as a genuine edited jump: displayed10:13 becomes10:14 and walking positions change to central active exchange. Both athletes support the V3 image innovation; a static official no longer vetoes their evidence. The unchanged original full inference had no reset there. This is documented in [independent6151 review](independent_review_6151_v1/REPORT.md) with seven source-bound PNGs/PTS/pixel hashes and exact current-layout matrix. It is not a new human rally/winner label or measured scene recall claim.

The11300–11360 window does not acquire11346 in any arm. It begins without pre11300 court-origin memory and may start with an already-offcourt athlete. Treat this as a **bounded startup limitation**; it does not establish the full new pipeline's11346 behavior. A longer anchored prefix or complete fresh regression is required. The same startup limitation applies to any window beginning without prior tracker/history state; the critical7650–8150 window explicitly includes the7770/8056 anchors.

## Tests, residual risks and next gate

[Original cause/proposal](PROPOSAL.md), [genuine static-extra/over-capacity RED tests](joint_contract_RED.log), [raw-layout dependence RED](raw_layout_continuity_RED.log), [ambiguity-recovery RED](ambiguity_recovery_RED.log), and [exact final focused test sources](final_focused_tests/source_receipt.json) are retained. The root orchestrator separately ran [177 focused tests](ambiguity_recovery_GREEN.log) after the final code change; that result is distinct from these source trials and the earlier30-test receipt. No missing-feature, one-region, overlapping-witness or cross-channel single-witness case is promoted to a verified change. No threshold, court geometry, model, annotation, matching rule or scoring identity was tuned to obtain the recovered cuts.

The final design has an explicit false-reset surface: multiple occlusions may resemble a source edit, and a visual episode may follow a nearby person while staying unbound. Bounded freshness, nonoverlapping independently qualified witnesses, positive current-layout vetoes and preserved unknown provenance limit this surface; they do not prove exhaustive scene or physical-identity accuracy. Overflow deliberately abstains until reset and must be monitored on real doubles/multi-court footage. Zero overflow here cannot substitute for those format controls.

The next acceptance gate is complete **fresh** source-native Test1 and Test2 inference at the recorded final commit, through the unchanged original evaluators and all applicable annotations, compared with preserved baselines. Include all reference matrices, resource scopes, contact/class timing shifts, short/walking controls, supported versus unsupported metrics, and source-bound failure evidence. No Test3 data was accessed, no original reference/evaluation output was overwritten, and no full-pipeline improvement is claimed by this bounded report.
