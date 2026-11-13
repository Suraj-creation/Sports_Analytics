# Test 3 annotation inventory and evaluation mapping

Evaluation-only review of every original file in `Part2/dataset/Test3_Full`. No annotation, pipeline, model, threshold or historical evaluation was changed. No video was downloaded or inference run by this reviewer. The complete machine-readable inventory preserves exact hashes, column order, numeric/missing/category profiles, malformed rows, all interval consistency checks and an annotation-only overlap graph.

## Source pairing

Historical independently retained pairing, completed-worker metadata, deletion receipt and full rational PTS audit agree on the following source. These are verified existing records; the newly downloaded source and fresh run must independently match before evaluation.

- Video: `Test3_Full_Rev.mp4`; Drive ID `1BOqrabc6KqyvjsC0llTUm6g6BM7fD6fd`.
- SHA256: `d587569affa3b4fcabab0ea6b97ecd278af15675ce5cba36c79298bb6d0db5fa`; exact bytes: **696,523,353**.
- Original source: 1920×1080 H.264, 30fps, no recorded VFR. Canonical analysis: **1280×720, 30/1fps, 8,414 frames**, zero-origin frames0–8413.
- Historical PTS CSV was rehashed and every one of its8,414 rational timestamps verified equal to frame/30. This does not replace the new run’s source/PTS guards.
- Automatic inference must not ingest the court JSON or any evaluation labels. Original image coordinates and canonical analysis coordinates must remain distinct.

[Exact source receipts and hashes](source_pairing.json).

## Every original file

| File | Content verified | Evaluation role and limitation |
|---|---|---|
| Test3_Full.csv | 22 coarse start/end MM:SS spans; winner/reasons; one ball_types field; two symbolic running-score columns | Separate supplied coarse timing benchmark; human-origin legacy documentation does not certify every semantic field |
| Test3_Full_Rev_T4.csv | 19 rows, byte-identical to Test3_Full_rally.csv | Declared duplicate timing reference, not an independent accuracy observation |
| Test3_Full_ball_filled.csv | 8,414 complete timeline rows; generated/filled X/Y, binary Visibility and confidence | Generated trajectory agreement after coordinate binding; physical detection/visibility accuracy unavailable |
| Test3_Full_court.json | frame4207;1280×720; TL/TR/BR/BL and net coordinates; source explicitly manual | Single-frame court comparison only after source/corner-semantics binding; no automatic singles/doubles-line assumption |
| Test3_Full_rally.csv | 19 exact frame/seconds/duration intervals plus lossy MM:SS displays | Historical generated timing agreement; preserve existing benchmark separately |
| player_detections.csv | 8,414 complete timeline rows; two anonymous generated bottom-center slots and confidences | Anonymous point disagreement only after source-bound coordinate certificate; no boxes or persistent physical IDs |
| win_predictions.csv | 19 generated winner/loser/reason/CNN/source/score rows; frames equal rally reference | Generated timing and model-to-model semantic context; never winner/score GT |

Four interval-reference entries preserve the coarse table, both duplicate timing files and win-prediction timing. Their results must remain separate; duplicates are not extra independent GT. No pooled count or score is an all-video aggregate.

## Data quality and annotation conventions

- **Coarse row6 / CSV line7** has seven cells under an eight-column header: `1:13,1:18,Player B,Opponent Out of Bounds,Opponent Failed to Return,2,4`. Timing remains usable. Parsed `ball_types` is reason-like, `lose_reason=2`, `roundscore_A=4`, and `roundscore_B` is missing. Do not guess which field was omitted or shift later cells. Preserve field-specific ineligibility for stroke/reason/score interpretation.
- **Coarse row9 / CSV line10** retains raw winner ` Player A`. Any later whitespace normalization requires explicit raw/normalized provenance; it is not physical winner adjudication.
- All22 coarse timing spans are nonblank. All19 generated frame/seconds/duration rows are consistent at historical30fps and inside source extent. Different coarse/generated counts include merged/differently bounded spans; [the overlap graph](annotation_inventory.json) preserves each relationship without fitted offsets or row-number pairing.
- Existing numerical evaluation uses zero-origin **half-open** intervals and IoU0.5 maximum-cardinality/IoU matching. Original end values, including last generated end8413, remain unchanged; do not add1 or reinterpret an inclusive endpoint to improve a score. The author’s physical start/end event convention is not certified.
- Player slots are the first two current filtered detections in the legacy exporter, not track identities or named athletes. Both slots are populated on8,323frames; slot1 is lower than slot2 on8,071frames and slot2 is lower on252. These swaps rule out permanent near/far assignment by column. Missing cells remain missing.
- Shuttle Visibility=1 on7,061frames and0 on1,353. Invisible rows use(0,0); none are nonzero. Visible rows have no(0,0) sentinel, and all supplied coordinates fit1280×720. **383 visible rows have confidence<0.5**, reported descriptively with no exclusion/filter. Visibility and confidence are generated states; no observed-versus-interpolated row flag exists.
- Court JSON declares `source: manual`, but has no named reviewer, exact source hash, physical line-width semantics or per-frame camera validation. TL/TR/BR/BL are ordered image points; singles versus doubles line meaning awaits synchronized frame4207 review. Net coordinates do not establish an airborne3D measurement.
- Legacy winner producer defaults PlayerA=far andPlayerB=near. That is a historical software naming convention, not a reviewed roster/side/team binding for this edited video. Coarse score columns and generated scores may disagree and need no forced reconciliation. One ball_types value per rally is not an exhaustive stroke/contact sequence.

## Metrics and unavailable ground truth

The manifest enables unchanged interval P/R/F1/TP/FP/FN, temporalIoU, boundary/duration errors and all missed/extra comparisons independently for each supplied reference. Dense timing/schema coverage and actual prediction/event/model/config/runtime metadata can be retained without a coordinate certificate.

No coordinate certificate is currently declared. Dense player/shuttle distances and court corner accuracy therefore remain **unavailable/null**, not zero, until a separate source-bound diagnostic review is supplied. A subsequent certificate must be referenced in a NEW manifest, preserving this unbound manifest. Even a valid agent certificate supports generated-reference agreement, not physical player AP/mAP, IDF1/HOTA, pose OKS/PCK, physical shuttle visibility/localization accuracy, racket/contact F1, exhaustive stroke confusion, winner/official-score/highlight/analytics accuracy. No corresponding exhaustive reviewed GT was found in these seven files.

## Reusable manifest and preservation

[evaluation_manifest.json](evaluation_manifest.json) follows existing `component-evaluation-manifest:v1`; every original immediate file and field has an explicit role, purpose, ambiguity and eligibility declaration. [Static validation](manifest_static_validation.json) passed existing generic evaluator `validate_manifest`, exact inventory hashes and each annotation loader for all7files, without a completed run or prediction access.

Provenance and conventions reuse the established global [schema review](../../../dataset_inventory/component_schema_analysis.md) and [outcome-origin review](../../../dataset_inventory/outcome_provenance_analysis.md). Direct producer evidence: legacy `analysis/player_detection.py` exports detector bottom centers/first-two slots; `TrackNetV3/fill_gaps.py` generates interpolated estimates; `analysis/detect_rallies.py` writes frame/time intervals; `win_predictor/predict.py` writes ML/rule outcome/score fields. Full original-data and supporting receipt hashes are in [annotation_inventory.json](annotation_inventory.json) and [source_pairing.json](source_pairing.json).

Initial video processing remains automatic and evaluation-only. Record any failures for later diagnosis; do not modify pipeline code, thresholds or models for this individual video.
