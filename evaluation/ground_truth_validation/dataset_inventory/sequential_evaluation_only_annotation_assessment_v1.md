# Sequential evaluation-only annotation assessment: Tests 3, 4, 6, 7, 9 and 10

Every immediate original file in these six Part2 folders was independently read, hashed and checked against the preserved global manifest. The new manifests use existing `component-evaluation-manifest:v1`; every original field has explicit eligibility, purpose and ambiguity. Existing generic evaluator schema/inventory/dense-timeline loaders accepted every manifest. **Tests5 and8 remain excluded by user instruction. No pipeline or Python source was changed, no labels repaired, and no video downloaded or inference run by this inventory review.**

Original dense tables and all semantic fields remain intact. This is an annotation/readiness assessment, not fresh model performance, independent physical accuracy certification, or an aggregate benchmark.

## Dataset coverage and distinct reference families

| Test | Original files | Canonical frames / FPS | Coarse raw / valid timing | Generated timing rows | Main caveats |
|---|---:|---|---|---|---|
| 3 | 7 | 8,414 /30 | 22 /22 | Test3_Full_Rev_T4.csv: 19, Test3_Full_rally.csv: 19, win_predictions.csv: 19 | Coarse row6 has7/8cells; row9 leading-space winner; rally/RevT4 exact duplicate; coordinate certificate added separately |
| 4 | 7 | 20,034 /30 | 45 /45 | Test4_Full_rally.csv: 41, win_predictions.csv: 41 | Normal/Rev shuttle exports exact duplicate;34 out-of-canvas shuttle rows retained; many nonunit score transitions |
| 6 | 7 | 17,915 /30 | 42 /42 | Test6_Full_T4.csv: 43, Test6_Full_rally.csv: 42, win_predictions.csv: 42 | No shuttle Confidence column; court source absent; T4 has43 versus rally42; visible(0,0) sentinel contradictions |
| 7 | 7 | 10,725 /30 | 31 /31 | Test7_Full_T4.csv: 33, Test7_Full_rally.csv: 30, win_predictions.csv: 30 | No shuttle Confidence column; court source absent; T4 has33 versus rally30; opening symbolic winner/score conflict |
| 9 | 6 | 33,157 /30 | 88 /78 | Test9_Full_rally.csv: 82, win_predictions.csv: 82 | Ten blank coarse rows79–88 retained; generated82 versus78 valid coarse spans; one visible(0,0) contradiction |
| 10 | 6 | 37,133 /30 | 101 /96 | Test10_Full_rally.csv: 93, win_predictions.csv: 93 | Five blank coarse rows97–101 retained; completed historical retry1 source metadata used, original timeout attempt preserved |

All canonical media are1280×720,30/1fps. Every dense frame column is unique, ordered, zero-origin and complete for the corresponding historical source. The seven-column generated timing families agree internally with frame/30 and duration at1e-6second tolerance; their physical onset/end conventions remain uncertified. Win-prediction frame boundaries equal each video’s main rally table, but outcomes/CNN confidence/rule sources/scores are **earlier model outputs**, not ground truth. Duplicates and alternative tables remain separate manifest entries, with no inflated independent-GT denominator.

All coarse blank rows are preserved and visible in inventory. Existing unchanged interval parsing excludes blank spans from positive-reference counts; no nonblank parseable interval is silently discarded. A reference’s count or boundary change can change metrics even for identical predictions. Keep coarse, main generated, T4 variants and win-derived timing results separate. Original half-open end values are retained without inclusive-end adjustment or fitted offset.

## Historical source identity; fresh verification still required

Pairing, completed-worker media, deletion receipt and full rational PTS audit were cross-checked. Every historical PTS CSV was rehashed and every timestamp checked against frame/30. The source byte/hash targets below are historical verified evidence; the new download and actual completed run must still match. No remote object or new video bytes were inspected by this inventory task.

| Test | Original video / Drive ID | Expected bytes | Source SHA256 |
|---|---|---:|---|
| 3 | Test3_Full_Rev.mp4 / `1BOqrabc6KqyvjsC0llTUm6g6BM7fD6fd` | 696,523,353 | `d587569affa3b4fcabab0ea6b97ecd278af15675ce5cba36c79298bb6d0db5fa` |
| 4 | Test4_Full_Rev.mp4 / `1W8gjgQz8QX2MkvqmtsQFb3-3y9wfRuy7` | 1,296,890,124 | `adff61dad4741ea6e8220c5d3292ddb0578b3c91b9e724f49b6f6608203558ed` |
| 6 | Test6_Full.mp4 / `1LxlJnH5bJo_tLVfgDH73UQ35XCtRg1tC` | 1,330,306,904 | `45f873540649ec9d2b20e2d14edbf35ba2b2e41b150bfe07f3c995a0310fdab8` |
| 7 | Test7_Full.mp4 / `1WS9suAtgbuwB2qc4IteGgFL6xf5hs0Gq` | 664,899,136 | `1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c` |
| 9 | test_9.mp4 / `1iwjp0Aph_00mznu-PNxsLKb_Y3B0-e1u` | 2,778,705,525 | `f2aabeb9610c437b38b840ae45885b4b71854702a6b30dd4aee4c54d1417dd4a` |
| 10 | Test_10.mp4 / `1Zr3JVT1ICpJlFqGE9r7sUaxmrfwWQ72l` | 3,112,811,045 | `cf71d8e02086df5e192e3cf834804407ca5d9e0f2f6bdf26512b39b6b264214f` |

Test10 source identity explicitly uses `sequential-benchmark-20261106/test10_retry1` completed-worker/timestamp/deletion receipts. Its original `test10` directory contains the earlier frame-count timeout failure and lacks completed-worker metadata; it was not treated as a completed run. Retry configuration and retry receipt hashes are retained in Test10 source_pairing.json.

## Component eligibility and limits

- **Rally timing:** supplied-reference precision/recall/F1, TP/FP/FN, IoU, boundary/duration errors, missed/extra comparisons and tolerances are supported using the existing comparator unchanged. These are distinct reference-agreement families; generated timing is not independent physical frame-exact truth.
- **Players:** legacy first-two filtered YOLO detection slots export bottom centers and confidence. Slots can swap spatial order and are not named athletes, stable track IDs or teams. Preserve absent points. Anonymous point disagreement requires a source-bound diagnostic coordinate certificate; box AP/mAP/IoU, HOTA/IDF1 and physical identity accuracy are unsupported.
- **Shuttle:** generated/filled trajectories have no per-row observed-versus-interpolated flag. Visibility and support are exporter/model fields, not physical visibility labels or calibrated probabilities. Tests6/7 lack Confidence entirely; no confidence was invented. Invisible(0,0), visible(0,0) contradictions and out-of-image coordinates remain explicit. No clipping, fill, threshold fitting or sample removal was applied.
- **Court:** Tests3/4/9/10 explicitly assert source=manual, without named reviewer or physical corner semantics in the originals. Tests6/7 omit source provenance and are declared `supporting` rather than promoted to manual GT. All unbound manifests leave geometry/distances unavailable. A reviewed source frame/corner certificate may support diagnostic image agreement, not all-frame court accuracy or airborne3D measurements.
- **Outcomes, scores, shot classes:** coarse tables have documented legacy human-origin references but unresolved source-bound A/B/team binding and per-field quality issues. Legacy predictor defaults PlayerA=far/PlayerB=near, which is not a verified physical identity mapping. Edited-video cumulative reference scores need not equal broadcast official scores. One ball_types label per rally does not label all contact/stroke timestamps. CNN supports, generated win_predictions and rule fields are preserved as competing predictions, never physical GT.
- **Other physical metrics:** pose PCK/OKS, physical contact/racket F1, exhaustive stroke confusion, accepted winner/score sequence, highlight quality and player analytics accuracy remain unavailable without corresponding independently reviewed labels. Successful inference is not those metrics. Actual model/config/commit/resource/runtime/event coverage can still be recorded from the genuine finished run.

## Concrete per-dataset annotation issues

Test3’s malformed row6 retains usable1:13–1:18 timing, but missing column position is not guessed; affected stroke/reason/score fields stay unresolved. Row9’s raw ` Player A` string is preserved. Its generated7th interval spans82.8–101.833seconds and overlaps multiple coarse rows, illustrating a reference-convention difference rather than a fixed-offset problem. A separate agent source review now binds diagnostic coordinates and identifies singles lines at frame4207; its NEW bound manifest preserves the unbound original. Source4204→4207 is an edit, not evidence for shifting CSV timestamps.

Test4’s two shuttle files are exact byte duplicates. The normal table is ordered before its Rev alias in the manifest so later reference binding has an explicit primary. No duplicate trajectory should be counted as independent data. All34 out-of-image shuttle rows remain in raw evidence.

Tests6/7 have genuinely four-column shuttle exports (`Frame,X,Y,Visibility`). Their court JSONs have no source assertion. Alternative T4 timing families contain different rally counts and must not replace main timing silently. Test7 opening winner-versus-symbolic0:1 score discrepancy is conditional on an assumed0:0 beginning; it is an annotation-convention conflict requiring review, not a corrected physical winner.

Test9’s88 coarse records include ten fully blank rows, leaving78 positive timing spans; the82 generated intervals describe a different family. Test10’s101 coarse records include five blanks, leaving96 positive timing spans versus93 generated intervals. Blanks and raw model/label disagreements remain preserved.

The companion [machine-readable assessment](sequential_evaluation_only_annotation_assessment_v1.json) retains manifest/source hashes, inventory paths, score-delta assumptions, interval-family counts and dense coverage; the underlying per-test inventories contain exact original schemas/hashes, every numeric/missing/category field profile and all flagged frame IDs.

## Deliverables and source evidence

| Test | Inventory/readiness | Unbound generic manifest |
|---|---|---|
| 3 | [README](../test_03/annotations/evaluation_only_v1/README.md), [exact inventory](../test_03/annotations/evaluation_only_v1/annotation_inventory.json), [source pairing](../test_03/annotations/evaluation_only_v1/source_pairing.json) | [manifest](../test_03/annotations/evaluation_only_v1/evaluation_manifest.json), [static validation](../test_03/annotations/evaluation_only_v1/manifest_static_validation.json) |
| 4 | [README](../test_04/annotations/evaluation_only_v1/README.md), [exact inventory](../test_04/annotations/evaluation_only_v1/annotation_inventory.json), [source pairing](../test_04/annotations/evaluation_only_v1/source_pairing.json) | [manifest](../test_04/annotations/evaluation_only_v1/evaluation_manifest.json), [static validation](../test_04/annotations/evaluation_only_v1/manifest_static_validation.json) |
| 6 | [README](../test_06/annotations/evaluation_only_v1/README.md), [exact inventory](../test_06/annotations/evaluation_only_v1/annotation_inventory.json), [source pairing](../test_06/annotations/evaluation_only_v1/source_pairing.json) | [manifest](../test_06/annotations/evaluation_only_v1/evaluation_manifest.json), [static validation](../test_06/annotations/evaluation_only_v1/manifest_static_validation.json) |
| 7 | [README](../test_07/annotations/evaluation_only_v1/README.md), [exact inventory](../test_07/annotations/evaluation_only_v1/annotation_inventory.json), [source pairing](../test_07/annotations/evaluation_only_v1/source_pairing.json) | [manifest](../test_07/annotations/evaluation_only_v1/evaluation_manifest.json), [static validation](../test_07/annotations/evaluation_only_v1/manifest_static_validation.json) |
| 9 | [README](../test_09/annotations/evaluation_only_v1/README.md), [exact inventory](../test_09/annotations/evaluation_only_v1/annotation_inventory.json), [source pairing](../test_09/annotations/evaluation_only_v1/source_pairing.json) | [manifest](../test_09/annotations/evaluation_only_v1/evaluation_manifest.json), [static validation](../test_09/annotations/evaluation_only_v1/manifest_static_validation.json) |
| 10 | [README](../test_10/annotations/evaluation_only_v1/README.md), [exact inventory](../test_10/annotations/evaluation_only_v1/annotation_inventory.json), [source pairing](../test_10/annotations/evaluation_only_v1/source_pairing.json) | [manifest](../test_10/annotations/evaluation_only_v1/evaluation_manifest.json), [static validation](../test_10/annotations/evaluation_only_v1/manifest_static_validation.json) |

Existing preserved [global schema analysis](component_schema_analysis.md) and [outcome provenance analysis](outcome_provenance_analysis.md) contain direct legacy producer references for bottom-center export, filled trajectories, generated intervals and ML/rule score output. This review independently verified current file bytes and all schemas/rows rather than assigning meaning by filename.

Use at most one large video at a time. Genuine source/native-worker/parent/catalogue/model/config/timestamp completion guards must pass before numerical evaluation; missing coordinate certificates yield explicit null distances. Preserve prior per-video results and failures, keep metrics per reference family, and perform evaluation only. Do not make pipeline fixes between these sequential videos.
