# Final production-readiness validation matrix

**Decision: NOT production-ready.** PASS, FAIL, BLOCKED and UNVALIDATED refer to the stated gate, not an aggregate score. All completed results and prior failed controls are retained.

| Release gate | State | Evidence and practical limit |
| --- | --- | --- |
| 1. Critical components on real input | UNVALIDATED | Six complete-input neural runs execute actual configured perception→events→analytics/export. Supported workflow execution passes; independent correctness of every component is not established. Optional ReID remains explicitly unavailable. |
| 2. Data/temporal/coordinate integrity | UNVALIDATED | Source/frontier/epoch/rollback/cache/wire tests pass; current UI/agent source projection defects repaired. Generic original↔canonical VFR/high-FPS mapping is absent; analysis-proxy indices are explicitly labelled. |
| 3. Reviewed physical contacts | BLOCKED | Typed physical reliability and GT27 dependency mitigation verified. Published draft-aligned anchor agreement measured, but independently certified physical-impact labels/calibration remain missing. |
| 4. Static/airborne association | UNVALIDATED | Real GT27/static ambiguity and real Test7 floor-shuttle controls retained; raw points never replaced. Independent false-continuity/localization denominators missing. |
| 5. Court/scene authority | UNVALIDATED | Image observations/court validity/source context remain explicit; same-camera barriers have actual source evidence. Independent reviewed landmarks/edit labels and physical geometry accuracy missing. |
| 6. Agreed start/end tolerances | BLOCKED | Full matched/all-GT metrics retained. Test1 scene start MAE 28.25/end 10.4722 frames; Test7 start 33.8621/end 19.7586 and maximum start error 242 frames. Tolerance/onset conventions unagreed and residual failures remain. |
| 7. Match-disjoint generalization | BLOCKED | Fifteen-entry manifest, zero eligible prospective blind recordings. Four exposed external runs reveal contact/shot/onset failures; they cannot become new blind tests. |
| 8. Four-player individual accuracy | BLOCKED | Actual doubles four local track keys on 1,719/3,600frames and current-pose coverage measured. No reviewed dense person/visibility/identity/movement truth; predicted named-hitter coverage is zero. |
| 9. Shots/individual attribution | FAIL | Current reference agreement: correct classes 3/64,1/25,1/21 at±3;77–91% unknown predictions. Geometry shadow adds many wrong labels; no promotion. |
| 10. Deployment GPU/performance | BLOCKED | Actual GTX1080Ti node/dtype/resource evidence and complete-input throughput measured. RTX4000Ada absent; no real-time or whole-model-GPU inference from profile names. |
| 11. CFR/VFR/live/playback | UNVALIDATED | Actual integer/fractional/VFR/offset/browser/growing-HLS controls pass. True-live adapter/recovery/latency, original-source map, other-browser/NVENC coverage and accepted old-HLS routing migration remain open. |
| 12. Orchestration faults/accounting | UNVALIDATED | Existing local service retry/stop/fault and durable cross-connection Q&A reservations pass. Reported accounting is not a billing hard cap; native strict bounds, Redis/distributed/remote failures and account-wide quotas unvalidated. |
| 13. Relevant software suites | PASS | Final main 2,280, research 458 and frontend 226 all pass; typecheck/build and actual final browser workflow pass. Earlier failed controls retained and calibration race reproduced/fixed. |
| 14. Regressions visible | PASS | All 36 Test1/all 31 Test7 rows, original/fresh-v1/selected comparisons, common-row changes, unmatched predictions and positive-overlap topology retained. Rejected alternatives remain visible. |
| 15. Reproducible evidence package | PASS within documented scope | Exact executed sources/input/model/profile/output identities, failed studies, independent review and final release index preserved. Historical Test7 lacks completion-time cache catalogue: posthoc 179 hashes+full event parity only; future writer/parent/reader guard fixed without backfill. |

## Final software and actual-input checks

| Check | Observed result | Evidence under `artifacts/benchmarking/experiments/` |
| --- | --- | --- |
| Main Python |2,280 passed;19 existing HTTP422 warnings;315.73s|`prod_20261105_full_python_v2.log`|
| Research |458 passed;8.03s|`prod_20261105_full_research_v2.log`|
| Frontend |226 passed/46files;5.92s|`prod_20261105_frontend_release_v5/tests.log`|
| TypeScript |exit0|`prod_20261105_frontend_release_v5/typecheck.log`|
| Isolated Vite build |exit0;7.01s; 45 assets,4 critical source-map byte bindings|`prod_20261105_frontend_release_v5/build_receipt.json`|
| Historical integrity |2,174/2,174 pass; repeated|`prod_20261105_final_integrity_v2/validation.json`|
| Test1 own-source parity |288cache files per arm,17,268orderedframes, exact interval/reason/CSV/contact/stroke payload checks|`prod_20261105_boundary_fresh_audit_v1/`, `*_replay_parity_audit_v4/`|
| Test7 own-source replay |179cache files,10,725steps/frontier10,724;248contact/stroke and32end payloads exact; posthoc cache-origin limit explicit|`prod_20261105_test7_semantic_causal_v2/`|
| Actual original-frame replays |1,125 exact-PTS source frames per arm,11 windows; 66 sampled Firefox renders pass|`prod_20261105_visual_*_v2/`, `prod_20261105_visual_browser_v2/`|
| New registry binding |45 focused controls; actual67-frame model-free plugin smoke|`prod_20261105_external_binding_regression_v1/`|
| Durable Q&A guard |52 dedicated new controls;117 merged focused passes; actual-root imports/Ruff|`prod_20261105_llm_budget_candidate_v2/actual_validation.json`|
| Q&A physical evidence |15 controls; legacy/stale/misaligned evidence unknown, analysis timebase explicit|`prod_20261105_tool_contact_provenance_green_v2.log`|
| Calibration Save |3 deterministic red→green cases; actual6/6 focused; old failure trace limit preserved|`prod_20261105_calibration_test_audit_v1/`, `frontend_release_v5/calibration_focused.log`|
| Real product workflow |67 frames/frontier66; 6/6 decoded barcode seeks;4 real downloads match;HTTP+WS failure projection/private retention/ownership/reuse|`prod_20261105_product_smoke_v5/results.json`|
| Real neural results→product |Prior v4-build stage, copied Test7 data:32rawends/248contacts/248strokes exact;21official CSV boundaries exact|`prod_20261105_neural_results_product_v3/results.json`|
| Real media/browser controls |9fixtures108seeks; growing108; fractional/AAC/migrated24 each within recorded scope|[PRODUCTION_MEDIA_COMPATIBILITY_REPORT.md](PRODUCTION_MEDIA_COMPATIBILITY_REPORT.md)|
| Future replay/catalogue proof |63 coupled focused controls; exact runner/helper/source/cache binding, before-Engine rejection|`prod_20261105_replay_catalogue_controls_v1/`|

Main/research/frontend are distinct suite scopes. Focused checks overlap their complete suites and must not be added to a misleading total. The old 2,201/297/202 and later210/223 frontend stages remain historical task evidence, superseded by the final counts above. Nineteen pre-existing HTTP422 warnings and unrelated format maintenance remain explicit. Ruff lint passes all changed Python files. All 23 new/current research files outside the legacy real-video harness pass formatting; that existing harness retains its independently verified pre-existing whole-file formatter debt. See `prod_20261105_final_source_checks_v1/`.

The first frontend v4 run failed an existing saved-calibration assertion. Its exact scheduling was unrecorded; a later independent native-DOM/real-hook test proved a stale mutation-callback failure with the same payload signature. The narrow explicit-variable fix passes all 3 controls and the final 226-test suite. Neither rerunning until green nor retroactively declaring the old root cause proved is used as acceptance.

Synthetic/control fixtures and assistant-reviewed pixels establish software/source contracts, not independent sporting labels. The formal release remains blocked despite the passing implementation gates.
