# Test1 component/reference diagnosis

Strict completed-run/source/cache guards passed before annotations were loaded. No new inference or prediction/annotation edits. Generated references are diagnostic agreement, not independently adjudicated physical truth.

## Annotation applicability

| File | Role | Evaluation status |
|---|---|---|
| Test1_Full.csv | coarse_legacy_label_agreement | evaluated_with_disclosed_reference_role |
| Test1_Full2.csv | partial_mixed_label_candidate | evaluated_with_disclosed_reference_role |
| Test1_Full_ball_filled.csv | filtered/filled model estimate; no observed-vs-filled marker | generated_trajectory_diagnostic |
| Test1_Full_court.json | manual asserted at frame8634; source and corner interpretation require review | court_single_frame_candidate |
| Test1_Full_rally.csv | legacy_generated_reference_agreement | evaluated_with_disclosed_reference_role |
| Test1_Full_rev_T.csv | legacy_generated_reference_agreement | evaluated_with_disclosed_reference_role |
| Test1_Full_rev_T4.csv | legacy_generated_reference_agreement | evaluated_with_disclosed_reference_role |
| player_detections.csv | points only; no boxes or stable identities | generated_two_point_slot_diagnostic |
| win_predictions.csv | legacy_generated_reference_agreement | evaluated_with_disclosed_reference_role |

## Interval reference agreement

| Reference | Valid positives | Matched | Unmatched positive rows | Unmatched current proposals | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| Test1_Full.csv | 36 | 36 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| Test1_Full2.csv | 20 | 19 | 1 | None | None | 0.95 | None |
| Test1_Full_rally.csv | 36 | 36 | 0 | 0 | 1.0 | 1.0 | 1.0 |
| Test1_Full_rev_T.csv | 35 | 34 | 1 | 2 | 0.9444444444444444 | 0.9714285714285714 | 0.9577464788732394 |
| Test1_Full_rev_T4.csv | 38 | 36 | 2 | 0 | 1.0 | 0.9473684210526315 | 0.972972972972973 |
| win_predictions.csv | 36 | 36 | 0 | 0 | 1.0 | 1.0 | 1.0 |

Full2 malformed row21 and all raw rows remain in the JSON. Full2 precision/F1/unmatched-proposal false-positive meaning are unavailable because its valid20 records do not establish exhaustive coverage; no arbitrary negative interval is inferred.

## Coordinates and court

Coordinate contract: diagnostic_coordinate_binding_declared. Unverified coordinate semantics produce candidates only, with metric=null. The optional review certificate cannot turn legacy generated points into independent labels. `frame_point_candidates.jsonl` preserves every frame’s legacy/current values, visibility, confidence and source diagnostics for synchronized overlays. Current shuttle distance uses raw analysis-image output, never registered-reference selected coordinates without a transformation contract.

Court reference frame8634: candidate singles/doubles outer corners and exact calibration event/H are retained when recoverable; a corner error is reported only with the explicit reviewed singles/doubles corner semantics. No original SQLite database was opened.

## Unavailable requested metrics

- player_AP_mAP_IoU: unavailable; requires Reviewed bounding boxes and exhaustive positive/negative coverage; existing CSV has only two generated point slots.
- tracking_IDF1_HOTA_ID_switches_fragmentation: unavailable; requires Reviewed persistent athlete identities and complete box/visibility labels; generated slots are not persistent IDs.
- pose_PCK_OKS: unavailable; requires Reviewed keypoint positions/joint visibility plus scale/skeleton convention.
- shuttle_physical_localization_PR: unavailable; requires Independent reviewed coordinates/visibility and explicit observed-vs-filled flags; generated filled trajectory is diagnostic only.
- racket_contact_PR_F1_temporal_error: unavailable; requires Reviewed racket/contact times and negative windows, not rally-level labels.
- stroke_per_class_PR_F1_confusion: unavailable; requires Exhaustive per-contact stroke labels and declared taxonomy; one ball_types label per rally is insufficient.
- winner_outcome_accuracy_PR_F1_confusion: unavailable; requires Verified Player A/B mapping and source-bound adjudicated rally outcomes; win_predictions is generated and Full2 is partial/conflicting.
- score_sequence_accuracy: unavailable; requires Verified identity, point-to-rally mapping, edited-video completeness and reviewed score sequence.
- highlight_quality: unavailable; requires Reviewed highlight boundaries/relevance; rally overlap alone is only a proxy.
- player_analytics_accuracy: unavailable; requires Reviewed named-player identity and metric-specific movement/event labels.

See `component_reference_metrics.json` for full row-by-row matches, malformed rows, boundary/duration/IoU metrics, coverage denominators, diagnostic point distributions (when bound), court candidates and every consumed input hash.
