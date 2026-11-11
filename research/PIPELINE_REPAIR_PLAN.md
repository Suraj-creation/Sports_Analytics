# Pipeline repair plan

**Final scope clarification:** the user requested Video2 only. Completed additional local-video checks are preserved as incidental historical context. The extra amateur run was interrupted and is not a completed benchmark. No further video inference is running. The additional Video2 repeat was not performed: preparation timed out during its300second FFprobe count before a new plan or NN run was created. The original full fresh Video2 run, independent completion proof, unchanged evaluation and failure analysis are complete. Nothing was deleted.

Implementation branch: `repair/pipeline-generalization-20261105`, baseline HEAD `caa91761948d09f2cfe4937b0db743fff8643a12`. The inherited 26 dirty/untracked files are preserved in `../pipeline-repair-runs-20261105/baseline/` (patch, original files archive, per-file hashes). Historical Test1/Test2 artifacts, datasets and weights remain immutable.

The five full Test2 reports and the 792-line architecture blueprint were read. The blueprint describes an older implementation and estimated RTX4000 performance; active source and actual GTX1080Ti measurements take precedence. Test2 is exposed development/validation material. Reference agreement is not certified physical accuracy.

| Issue | Evidence / root cause to test | Correction strategy | Owner / validation | Status |
|---|---|---|---|---|
| FORMAT-01 | GT1 candidate canceled at unknown→same placeholder format confirmation | Preserve compatible format-agnostic temporal observations; bind rule eligibility to observation origin | Root; causal candidate, epoch and no retroactive point tests | Implemented; format/epoch/no-retroactive-point and rollback regressions pass |
| RALLY-01 | Brief exchanges fail duration maturity; G58 walking is a negative control | Opt-in disjoint motion and fresh opposite-episode witnesses; duration threshold unchanged | Typed participant/source-window regressions | Implemented for sufficient evidence; G56/G63 abstain; fresh Test2 complete68TP/7FP/5FN; precision/meanIoU regressions visible |
| RALLY-02 | GT39/55/69 provider gaps fragment continuing play | Separate missing/conflicting association from physical flight; no invented trajectories or global timeout extension | Full callback parity, gap probes and source review | Mechanisms reproduced; unresolved model/evidence limits documented; broad merge controls rejected |
| CONTACT-01 | Insufficient/ambiguous floor/pickup candidates reopen terminal rallies | Pass typed contact evidence into optional rally port, retain rejected candidates with reason | Temporal agent + root integration; low-serve, genuine hit and pickup controls | Implemented typed port and consistent stationary recovery; broad terminal veto rejected after recall regressions |
| SCENE-01 | False appearance resets; missed one-person edit | Raw hypothesis plus current detector-layout decision and explicit unknown fallback | 51 actual detector probes, full observer ablations, codec tamper/source tests | Experimental policy implemented; two false resets suppressed in source probes; missed11346 remains unresolved |
| OCR-01 | Branding borrows another label's score fields | Unique nearest compatible row and current-score column; abstain on missing digits | Original-source parser and generic layout/runtime regressions | Implemented; absent digits remain unknown |
| PERF-01 | Historical OCR3805.52s dominates runtime | Controlled backend/thread/algorithm probes, raw-output parity; retain OCR functionality | OCR agent + root full-run resource measurement | 25 fixed-crop backend controls completed; CPU selected experimentally; Video2 resources measured; further runs stopped under scope clarification |
| REFERENCE-01 | Preparation, pickup, omitted real play, edits in legacy proposals | Preserve all rows/metrics; per-case ambiguity disposition, independent review required | Root; all40 evidence-linked case records | All40 registered |
| PLAYER-01 | Off-cadence cut can leave no fresh detections; identity remains unreviewed | Force current detection after cut; detached source-bound probes consumed once | Source/cadence tests; four trackers on480 common actual detections | Defect fixed; ByteTrack retained; HOTA/IDF1 and sporting identity lack independent labels |
| COURT-01 | State VALID is not labelled registration accuracy | Retain geometry eligibility/rejection gates; audit invalid frames | Original91 invalid frames export zero projected player rows; full suite | Technical safeguards verified; physical court accuracy unvalidated; CourtAlign source unavailable |
| SHUTTLE-01 | Competing/static peaks and weak flight gaps | Retain existing bounded multi-candidate TrackNetV3 association; distinguish observation states | Gap/source probes; fresh Test1 all raw/association fields exactly unchanged | No unsupported decoder/model replacement; remaining observation gaps require reviewed shuttle evidence |
| SHOT-01 | Candidate contacts and estimated/unknown classes lack independent labels | Keep attribution/impact/classification separate and unknown-capable | Actual BST source/license/schema audit; no verified separate weight grant/current local checkpoint | Rules baseline retained; no sporting macro-F1 claim |
| MEDIA-01 | Full source/proxy time and tail integrity | Full source/proxy rational PTS plus decoding and contract suite | Baseline2917 and repaired3053 tests; fresh Test1 all17268 PTS verified | Full Test1/Test2/Test7 source/proxyPTS verified; native amateur original mapping remains uncertified |
| PRODUCT-01 | Empty named/official outputs can be misread as lost raw data | Keep evidence gates and inspect actual API/export/browser on independent copies | Existing product contracts and new explicit completion-recovery guard | Fresh Test1/Test2 API/browser/export parity passes; no invented named actor, winner or score |

The baseline full suite passed2,917 tests before implementation. The repaired core and initial harness passed3,053 tests; additional finalization/recovery tests are recorded separately and the full scope will be rerun after the catalogue fix. Fresh Test1 matches the frozen baseline exactly for every metric and per-rally comparison row (36TP/0FP/0FN); full own-cache replay has strict parity. Test2 completed full fresh inference and explicit independent finalization recovery; its unchanged evaluation yields68TP/7FP/5FN. Test7 completed normally and retains29TP/3FP/2FN on its original coarse reference.

New execution defects are also tracked: **CATALOG-21** is the benchmark completion allowlist rejecting the new codec after successful neural processing; its correction preserves strict codec validation and historical20 catalogues. Failed original receipts remain visible and independent completion recovery publishes no replacement predictions. **SQLITE-INSPECTION-01** records our read-only schema probe creating empty WAL/SHM files beside closed new Test1 outputs; they were preserved separately after checking no open handles, zero WAL and unchanged main-file hashes across removal from the run. Later checks query detached copies only. See `../pipeline-repair-runs-20261105/sqlite_inspection_side_effects_v1/receipt.json`; no pre-probe main-file hash was captured, and exact exported session/event content parity is the available additional evidence.

Every documented significant case is mapped below; full source observations and trace links are retained in [case register](../artifacts/benchmarking/experiments/pipeline_repair_20261105_v1/case_issue_register.json).

| Case | Issues | Baseline classification |
|---|---|---|
| gt_001 | FORMAT-01, REFERENCE-01 | Mixed boundary-convention ambiguity and format-initialization continuity loss; raw absence during preparation is not proved missed airborne flight. |
| gt_005 | REFERENCE-01 | Strong onset-convention ambiguity: the85-frame reference-relative delay includes prolonged preparation. Detector/association absence alone does not establish85 frames of missed play. |
| gt_006 | CONTACT-01, REFERENCE-01 | Likely floor/post-rally continuity contributing to a late ending, plus onset-convention ambiguity. The yellow marker alone does not identify a real floor shuttle. |
| gt_007 | REFERENCE-01 | Early contact/admission is recorded; false-contact versus reference-onset convention remains unresolved from the sampled images. |
| gt_008 | REFERENCE-01 | Early ending relative to the table has substantial terminal-boundary ambiguity; the later reference samples are post-point/reset rather than proof of active flight lost after3099. |
| gt_011 | REFERENCE-01 | ['annotation_merge_ambiguity', 'edited_recording', 'model_onset_uncertainty'] |
| gt_014 | REFERENCE-01 | Onset/ending convention ambiguity and possible reference span across a scene/point reset. Do not treat all54 frames before reference end as proven premature active-play termination. |
| gt_023 | SCENE-01, REFERENCE-01 | Source-supported false scene barrier during continuing play is the earliest clear active-exchange continuity loss in this case. This is a heuristic/content-model limitation; no software contract defect is proved. |
| gt_024 | REFERENCE-01 | Recorded provisional cancellation, but much of34-frame onset discrepancy is preparation/convention ambiguity; no proved active-flight loss from8593. |
| gt_030 | SCENE-01, REFERENCE-01 | Source-supported missed same-camera edit allows cross-edit/preparation contact evidence into early rally admission. This supports a scene/contact heuristic generalization failure; no numerical patch or independently reviewed contact label is introduced. |
| gt_031 | RALLY-01, REFERENCE-01 | ['temporal_policy', 'annotation_terminal_ambiguity'] |
| gt_032 | RALLY-01, REFERENCE-01 | ['temporal_policy', 'short_exchange_limit'] |
| gt_034 | CONTACT-01, REFERENCE-01 | Likely floor/pickup continuation lengthens the rally. Exact true terminal frame is not independently adjudicated, but both the reference and predicted ends occur within post-exchange behavior. |
| gt_035 | REFERENCE-01 | Strong onset-boundary ambiguity: calling the42-frame difference a missed airborne serve is unsupported by the source samples. Original reference remains unchanged. |
| gt_037 | CONTACT-01, REFERENCE-01 | Onset-convention ambiguity plus likely floor/pickup contribution to the terminal tail; no demonstrated relevant calibration failure in the actual target interval. |
| gt_039 | RALLY-02, REFERENCE-01 | ['model_availability_limit', 'temporal_continuity_policy', 'annotation_onset_ambiguity', 'scene_edit_limit'] |
| gt_041 | CONTACT-01, REFERENCE-01 | ['post_point_retrieval_continuity', 'contact_candidate_not_established_physical_impact'] |
| gt_042 | REFERENCE-01 | ['reference_onset_before_source_edit', 'reference_end_after_source_edit', 'post_cut_missing_observations'] |
| gt_044 | REFERENCE-01 | ['reference_onset_before_source_edit', 'serve_preparation_versus_launch_uncertain', 'weak_initial_perception'] |
| gt_046 | REFERENCE-01 | ['reference_end_after_source_transition', 'geometry_reacquisition_after_broadcast_transition', 'short_later_candidates'] |
| gt_048 | REFERENCE-01 | ['reference_end_after_source_transition', 'post_point_floor_or_dead_shuttle_observation'] |
| gt_052 | REFERENCE-01 | ['provisional_onset_fragmentation', 'serve_preparation_or_early_exchange_unresolved', 'endpoint_collection_convention'] |
| gt_053 | CONTACT-01, REFERENCE-01 | ['post_point_retrieval_continuity', 'low_motion_contact_candidates_extend_rally'] |
| gt_054 | CONTACT-01, REFERENCE-01 | ['preparation_admission_uncertainty', 'post_point_floor_continuity', 'physically_insufficient_contact_reopening'] |
| gt_055 | RALLY-02, REFERENCE-01 | ['model_onset_limit', 'model_availability_limit', 'temporal_continuity_policy'] |
| gt_056 | RALLY-01, REFERENCE-01 | ['temporal_policy', 'short_exchange_limit', 'annotation_terminal_ambiguity'] |
| gt_058 | REFERENCE-01 | ['annotation_activity_ambiguity', 'temporal_policy_negative_control'] |
| gt_059 | REFERENCE-01 | ['terminal_perception_loss', 'reference_end_after_source_edit'] |
| gt_061 | REFERENCE-01 | ['provisional_onset_fragmentation', 'serve_preparation_or_early_exchange_unresolved'] |
| gt_063 | RALLY-01, REFERENCE-01 | ['model_availability_limit', 'temporal_policy', 'annotation_onset_ambiguity'] |
| gt_067 | REFERENCE-01 | ['reference_onset_before_source_edit', 'reference_end_after_source_edit', 'short_onset_candidate'] |
| gt_069 | RALLY-02, REFERENCE-01 | ['model_availability_limit', 'temporal_continuity_policy', 'reference_terminal_ambiguity'] |
| gt_071 | CONTACT-01, REFERENCE-01 | ['reference_onset_before_source_transition', 'post_point_retrieval_motion_reopening'] |
| gt_072 | CONTACT-01, REFERENCE-01 | ['reference_onset_before_source_edit', 'post_point_floor_or_retrieval_continuity'] |
| pred_011 | REFERENCE-01 | ['annotation_merge_ambiguity', 'edited_recording'] |
| pred_038 | RALLY-02, REFERENCE-01 | ['model_availability_limit', 'temporal_continuity_policy'] |
| pred_039 | RALLY-02, REFERENCE-01 | ['model_availability_limit', 'temporal_continuity_policy'] |
| pred_045 | REFERENCE-01 | ['annotation_coverage_ambiguity', 'visually_supported_extra_exchange'] |
| pred_056 | RALLY-02, REFERENCE-01 | ['model_availability_limit', 'temporal_continuity_policy'] |
| pred_069 | RALLY-02, REFERENCE-01 | ['model_availability_limit', 'temporal_continuity_policy', 'reference_terminal_ambiguity'] |

Each accepted change requires a focused failing reproduction, regression, relevant suite and unchanged evaluation rules. Experiments use independent output directories, source/config/model hashes and no labels in inference. Production profile defaults will not be promoted from this investigation. Full neural runs freeze all source before launch. All unobservable or annotation-dependent cases retain explicit dispositions and original denominators.

## Executed case dispositions

The updated case register retains all40original cases plus the new short unmatched interval, with41stable union records and79source-contract memberships checked. Every original/fresh context has complete ordered raw/trace frame coverage, causal availability, observation/interpolation and epoch/provenance checks. These are integration contracts, not physical boundary labels. The [complete review](../../pipeline-repair-runs-20261105/fresh_test2_case_review_v1/REPORT.md) links current/frozen outputs and earliest supported changes; no original reference row or unmatched prediction was removed.

Full current tests pass3151with19warnings. All implementation/default/profile separation, regression fixtures and failed controls remain in the linked implementation/component/performance reports. Remaining model/evidence limits and data requirements are in[remaining issues](PIPELINE_REMAINING_ISSUES.md). The selected profile remains experimental and unchanged throughout all fresh inputs; the additional Test2 repeat was not performed; exact latest-profile NN repetition remains unvalidated.
