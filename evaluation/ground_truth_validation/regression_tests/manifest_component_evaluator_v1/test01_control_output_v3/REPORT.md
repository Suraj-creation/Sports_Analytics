# Manifest-driven component evaluation

Native complete fresh worker and original cache guards passed. Generated references measure agreement, not physical accuracy. All original inputs are unchanged.

| Reference | TP | FP | FN | Precision | Recall | F1 | Mean IoU | Start MAE s | End MAE s | Duration MAE s |
|---|---|---|---|---|---|---|---|---|---|---|
| Test1_Full.csv | 36 | 0 | 0 | 1.0 | 1.0 | 1.0 | 0.8421299050542989 | 1.0296296296296341 | 0.46666666666666856 | 1.159259259259263 |
| Test1_Full2.csv | 19 | unavailable | 1 | unavailable | 0.95 | unavailable | 0.8468352271418205 | 1.0982456140350922 | 0.4333333333333414 | 1.0649122807017646 |
| Test1_Full_rally.csv | 36 | 0 | 0 | 1.0 | 1.0 | 1.0 | 0.8710256650394885 | 0.9416666666666749 | 0.3490740740740812 | 1.111111111111119 |
| Test1_Full_rev_T.csv | 34 | 2 | 1 | 0.9444444444444444 | 0.9714285714285714 | 0.9577464788732394 | 0.8678779703223529 | 0.89313725490197 | 0.38823529411765584 | 0.9107843137254996 |
| Test1_Full_rev_T4.csv | 36 | 0 | 2 | 1.0 | 0.9473684210526315 | 0.972972972972973 | 0.8710256650394885 | 0.9416666666666749 | 0.3490740740740812 | 1.111111111111119 |
| win_predictions.csv | 36 | 0 | 0 | 1.0 | 1.0 | 1.0 | 0.8710256650394885 | 0.9416666666666749 | 0.3490740740740812 | 1.111111111111119 |

Full tolerance/error distributions, missed IDs and extra/unscored predictions are in component_reference_metrics.json; every original row and field eligibility is in reference_raw_details.json. Per-frame points are separate JSONL files. No arrays are printed in this summary.

| Annotation | Declared role | Purpose / ambiguity |
|---|---|---|
| Test1_Full.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged; Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full2.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged; Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_ball_filled.csv | dense_generated_shuttle | Previously reviewed Test1 reference control; original annotations unchanged; Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_court.json | manual_court | Previously reviewed Test1 reference control; original annotations unchanged; Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_rally.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged; Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_rev_T.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged; Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_rev_T4.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged; Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| player_detections.csv | dense_generated_players | Previously reviewed Test1 reference control; original annotations unchanged; Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| win_predictions.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged; Generated/legacy candidate, no independent contact/identity/outcome ground truth |

## Unavailable physical metrics

- player_AP_mAP_IoU: unavailable. Independently reviewed boxes and complete positive/negative coverage; supplied generated points are not boxes.
- tracking_IDF1_HOTA_ID_switches_fragmentation: unavailable. Reviewed persistent athlete identities, boxes and visibility; two generated detection slots are not persistent IDs.
- pose_PCK_OKS: unavailable. Reviewed keypoints and joint visibility, skeleton convention and scale.
- shuttle_physical_localization_PR: unavailable. Independent reviewed coordinates/visibility; filled model estimates do not identify interpolated frames.
- racket_contact_PR_F1_temporal_error: unavailable. Reviewed contact/racket times and negative windows, not rally-level labels.
- stroke_per_class_PR_F1_confusion: unavailable. Complete per-contact stroke taxonomy and labels; a single ball_types field per coarse rally is insufficient.
- winner_outcome_accuracy_PR_F1_confusion: unavailable. Verified symbolic Player A/B identity and source-bound adjudicated outcomes; win_predictions is generated.
- score_sequence_accuracy: unavailable. Reviewed broadcast identity, point alignment and score sequence, accounting for edited-video omissions.
- highlight_quality: unavailable. Reviewed highlight relevance/boundaries; rally overlap and execution are not relevance accuracy.
- player_analytics_accuracy: unavailable. Reviewed participant identities and metric-specific physical movement/event labels.

Actual models/checkpoint hashes, native source root, original profile, backend declarations, runtime/resource measurements and event/class/outcome counts are retained in component_reference_metrics.json. Successful execution does not validate accuracy.
