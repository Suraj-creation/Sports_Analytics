# Validation coverage and limits — 2026-11-05

Release validation passed **1,966 application/engine/sport tests, 19 warnings,
299.58 seconds**, plus **77 benchmark tests, 1.00 second** (2,043 combined).
The default pytest paths exclude the benchmark directory; both were executed.
Logs are `next_20261105_full_regression_release.log` and
`next_20261105_benchmark_release.log` under the experiment root. The earlier
explicit combined suite passed 2,029 tests before 14 new packager tests were
added (`next_20261105_full_regression_after_mask.log`). The 14 packager red/green
controls and 15 additional research diagnostic controls also pass. No deployment
or default profile was changed. Lint passes for every changed/new Python file; the pre-existing
unrelated split `review_action` string in `plugin.py` remains a format warning.

Passing software contracts does not establish reviewed sporting accuracy.
Source-frame review is diagnostic evidence, not newly approved component labels.

| Requirement | Relevant executed software coverage | Real evidence / remaining limit |
| --- | --- | --- |
| Temporary and consecutive shuttle loss | `test_rally_evidence_v2.py`, `test_rally_temporal_correctness.py`, `test_rally_tracklet_support.py` | Own all-frame semantic traces; GT23/31 focused review |
| Moving shuttle with stationary players; moving players in breaks | `test_rally_motion_evidence.py`, `test_activity_false_evidence.py`, `test_engine_temporal_evidence.py` | Player activity never establishes shuttle landing; false prep/contact remains open |
| Court lines, spare shuttles, fast flight, weak launches/apexes | `test_shuttle_diagnostics.py`, `test_shuttle_flight_region.py`, `test_contact_motion_reliability.py`, `test_rally_image_exit_evidence.py` | Actual paired background inference and unmarked original crops; no complete localization labels |
| True/false estimated contacts; near-zero incoming velocity | `test_contact_motion_reliability.py`, `test_contact_scene_boundaries.py`, singles/doubles fusion tests | Numerical defect reproduced; alternative rejected on old perception; physical contact error rate unknown |
| Detector/pose dropouts and fresh/carried evidence | `test_pose_schedule_provenance.py`, `test_player_roi_continuity.py`, `test_perception_diagnostic_provenance.py` | Bounded new raw-query/rejection/carry telemetry; no reviewed association labels |
| Scene/view changes and same-camera edits | `test_scene_segments.py`, `test_camera_recovery_state.py`, `test_shuttle_scene_boundaries.py` | Two missed same-camera edits reproduced from original pixels; foreground probe only, no cut rule promoted |
| Short events, long loss, close separate rallies, fragment recovery | `test_rally_evidence_segments.py`, `test_rally_tracklet_provider.py`, `test_rally_port_independence.py` | New association requires qualification before loss; all36 rows and overlap topology retained |
| Repeated supersession/retraction, EOF, reset and rollback | `test_rally_temporal_correctness.py`, `test_streaming_contact_integrity.py`, `test_semantic_transaction_state.py`, engine `test_event_transactions.py`, `test_pipeline_component_lifecycle.py` | Exact own trace/event/export parity required for final run; growing rollback history cost remains unprofiled |
| Cache version/config/calibration invalidation | `test_stateful_perception_cache.py`, `test_tracknet_cache_lifecycle.py`, `test_perception_diagnostic_provenance.py` | Codec18; legacy17 diagnostic reads only; live sequential cache reuse remains prohibited |
| Singles and four-player doubles | `test_four_player_retention.py`, `test_doubles_tracking_capacity.py`, `test_doubles_contact_fusion.py`, `test_plugin_format_adaptation.py` | No reviewed four-player footage or doubles-accuracy claim |
| Invalid/offscreen geometry and neighboring courts | `test_shuttle_flight_region.py`, `test_invalid_court_projection.py`, `test_court_isolation.py` | Image columns are a spatial prior, not 3D ownership; held-out multi-court flight remains unvalidated |
| Non30-FPS arithmetic and VFR source mapping | engine `test_timeline.py`, `test_media.py`; benchmark `test_prediction_schema.py` | Actual Test1 is CFR30. Generic VFR/unsupported-rate source mapping remains H19; no end-to-end VFR accuracy claim |
| Browser seeking and live causality | engine timeline/frontier tests; badminton `test_engine_temporal_evidence.py` | Firefox static-replay smoke is not HLS/MSE seek validation. H20 remains open. Bounded VOD lookahead is not live inference |
| Independent host and injectable providers | engine `test_independent_pipeline_plugin.py`, `test_component_registry.py`; `test_local_adapter_contracts.py`, `test_rally_port_independence.py` | No badminton assumptions added to generic host |
| Score, winner, stroke, team and identity preservation | Existing analytics, scoring, service-order, identity and plugin suites | Functional contracts preserved; changed contact/rally evidence can change derived outputs. No accuracy inferred from rally F1 |

An independent validation set must be authorized, match-disjoint and separately
reviewed before promotion. Its manifest should cover amateur singles and four-player
doubles, camera positions, lighting/surfaces, similar clothing, multiple courts,
spectators, occlusions, camera motion/edits, VFR and poor shuttle visibility.
Keep localization/visibility, contact timing and hitter/team, shots, rally boundaries,
point/score sequences and runtime labels separate. Split by match before selecting
parameters, retain unknown/ambiguous labels, double-review onset/end conventions,
and use unchanged primary matching rules. No unrelated footage was accessed.
