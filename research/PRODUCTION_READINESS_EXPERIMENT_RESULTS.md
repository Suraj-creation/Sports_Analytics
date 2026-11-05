# Production-readiness experiment results — 5 November 2026

**Decision: retain experimental profiles; production gates do not pass.** These are executed experiments and repairs, including rejected alternatives. GT, matching, source videos, models, historical outputs and prior reports remain immutable. Cached semantic replay is explicitly distinguished from fresh neural inference. Exact source/config/model/input/output hashes and logs are retained with each unique artifact.

All artifact names below are relative to `artifacts/benchmarking/experiments/` and use the prefix `prod_20261105_` unless a historical reference is explicitly named. External fresh run directories are under `/home/administrator/Desktop/sport-analytics/production-readiness-runs-20261105/` because the existing real-video harness protects the repository tree from output reuse.

## Causal experiments and decisions

| Experiment / hypothesis | Mode and control | Observed result / decision |
| --- | --- | --- |
| Historical evidence integrity | Read-only rehash, Git-blob checks and unchanged CSV evaluator | Repeated2,174 checks pass; original/fresh-v1/selected outputs preserved. |
| Selected baseline replay | Recorded selected perception, same production domain providers | Exact36 intervals/end reasons and457 live contact/stroke timestamps. It is not fresh inference. |
| Suppress contact12766 alone | Cached one-event counterfactual; all shuttle inputs/other contacts unchanged | GT27 fragments; other35matches remain. Reject suppression-only fix. |
| Bounded static co-observation | Existing model candidates, coherent moving witnesses, expiry/epoch/raw-coordinate controls | Court-T ambiguity replaces a false accepted coordinate with missing/ambiguous evidence, never an alternative invented point. GT27 continuity can survive without12766. |
| Fresh association | Full17,268-frame neural production run, source8599325; fixed selected parameters |36TP/0FP/0FN, every selected interval unchanged;453 live contacts/strokes;12766 absent. Keep opt-in experimental. |
| Fresh association+content barrier | Full neural run; only content barrier adds a perception/event factor |36TP/0FP/0FN; startMAE28.25 versus29.1389, end10.4722 versus10.3333, IoU.871026 versus.867622. Seven changed rows include regressions. Keep experimental. |
| Own-cache replay parity | Each fresh run's own288 cache hashes, full step frontier, CSV/end reasons and folded payloads | Exact453/446 contact/stroke and36 end records, with explicit tracker namespace/recorded-format provenance resolution. No cached run counted as a neural repeat. |
| Foreground continuity versus histogram-only cuts | Causal prior-frame ROI/pixel/correspondence hypotheses; fast-play/invalid-context controls |13 hypotheses include missed same-camera edits. No independent cut labels or authoritative homography reset. Window and background history both change; no single-factor attribution to one of them. |
| Typed physical-contact assessment | Additive policy2, exact PF/RF freshness and geometry/source guards | Fresh association84 probable/140 ambiguous/229 insufficient; scene82/136/228;0 automatic physical-confirmed. Coverage, not physical precision/calibration. |
| Existing motion-reliability provider after association | One-variable cached provider swap with identical explicit.7216878365px sensitivity, unchanged thresholds | Test1 retains36matches but regressions remain. External F1 collapses India73.56→46.55%, Denmark69.44→40%, doubles52.5→40% at±3frames. Reject promotion. |
| Existing anonymous geometry brackets | One-variable own-cache arm after exact baseline; same episode/track/geometry, finite source brackets, publication-frontier checks | Contacts/actors/rally boundaries unchanged. Correct matched classes India3→11/64, Denmark1→6/25, doubles1→3/21; many new wrong labels. Keep shadow/opt-in; no names/pose/shuttle invented. |
| Source-current pose/racket | Actual per-person model results versus carried boxes, disabled cadence, missing/invalid/future/legacy values | Proven freshness loss fixed through cache20, pipeline3, Arrow/track wire2 and contact consumers. Browser stores source stamps; display reuse age alone is not physical source age. |
| Current-frame Q&A evidence | Old projection versus additive live frame-aligned contact references |15 controls pass. Tools expose analysis-frame timebase, separate physical status and source contact citations. Legacy/retracted/superseded/misaligned support remains unknown. No original-frame mapping is invented. |
| Equal-rate-header VFR | Real CFR/VFR/fractional/offset fixtures; bounded complete selected-video PTS scan | Header false-negative fixed. Full Test1 scan17,268 packets,~.95s/~67KB Python peak. Generic original↔proxy VFR/high-FPS mapping remains absent. |
| Physical HLS origin | Actual encoded pixel identities, Firefox VideoStage/useHls, AAC/fractional/growing/migration controls | Old AAC bf0 reproduces323/15360s origin; corrected assets pass all recorded seek controls with identical MP4 bytes. Old assets/routing untouched; migration tool is concrete but undeployed. |
| Analytics journal | Same typed inputs before/after; caller mutation, failed append, retractions/restores |5,000-operation checkpoint85.19ms→sub-.001ms/48B. Append copy cost rises, restore stays linear. No generic full-pipeline speedup claimed. |
| Actual GPU placement/precision | Existing weights, fixed real input, ORT node metadata and Torch tensor hooks | Detector758CUDA nodes; pose185CUDA+2CPU int64 shape nodes. TrackNet actual FP16/FP32; exported NumPy FP32. Five-sample/order-limited timing cannot select a precision default. |
| External current-profile neural stress | Frozen same profile, no annotation/calibration/name values in workers; all full clips/gaps | India4,800/Denmark3,300/doubles3,600/Test710,725frames completed with source guards. Metrics below expose substantial component failures. |
| Current external harness binding | Two retained v1 failures before NN; correct staged registry injection, actual67-frame model-free plugin smoke |45 focused controls pass; v2 profile bytes unchanged. No fake settings attribute or `create=True` workaround. |
| Durable LLM admission/accounting | Atomic cross-connection reservations versus lost-write race; reported(default)/strict(opt-in), failure/restart/repair/stale-answer controls |52 dedicated new cases and117 merged focused checks pass. Native defaults preserved; SDK retries disabled/30s I/O timeout. Unknown usage blocks later calls. Reported mode can overshoot by one response; native strict bound unsupported. |
| Real product upload/failure/export | Actual isolated FastAPI+EngineService/LocalBus+Firefox with CPU-only67-frame fixture, no neural providers | Stable empty17-column application CSV, truthful failed coverage, partial-export wording and sanitized HTTP+binaryWS failure detail repaired; private diagnostics retained. Final browser controls and nonempty neural-result replay recorded separately. |
| Replay proof lifecycle | Missing/stale runner or helper proof versus bound v2 metadata |15 red→green controls. New replay v2 binds runner/transitive helper hashes as well as engine/cache/source; completed v1 studies preserve their actual unchanged executed scripts. |

## Fresh Test1 comparisons

The immutable original baseline has30TP/19FP/6FN; fresh-v1 has35TP/4FP/1FN; historical selected and both new fresh arms have36TP/0FP/0FN. These counts use the unchanged IoU0.5 assignment and all36 annotations.

`prod_20261105_full_comparison_v2/` includes all36 endpoint/duration/IoU rows for both new candidates, common-row comparisons against original/fresh-v1/selected, all unmatched predictions, P50/P90/P95, RMSE/bias/max, ±1/3/5/10/15/30 both denominators and positive-overlap topology. Adjacent P22 spillover into GT23 is4/5frames; graph degree2 alone is not a semantic merge. GT2/19/20 remain recovered. GT4−71, GT5+98, GT9+106, GT15+86 and GT28+61 remain important onset errors; GT16end+44 and GT23start+42 in the scene arm are explicit regressions.

Full source-linked boundary calls, every cancellation class and per-row first observations are in [PRODUCTION_BOUNDARY_REVIEW.md](PRODUCTION_BOUNDARY_REVIEW.md). The source-synchronized replay packages each contain1,125 exact-PTS original frames across11 bounded windows, actual candidates/association/player/pose/court/contact/FSM/GT diagnostics and verified own trace/cache identities. Actual Firefox sampled66 renders passed; source screenshots distinguish ambiguous GT27 evidence from missing data. GT is offline visualization only.

## Exposed external references

| Recording | GT anchors / predicted contacts | ±3frame TP / FP / FN | Contact F1±3 / ±6 | Correct shot classes on ±3matches | Unknown shot fraction |
| --- | --- | --- | --- | --- | --- |
| India singles |85 /89|64 /25 /21|73.56% /73.56%|3 /64|78.65%|
| Denmark singles |39 /33|25 /8 /14|69.44% /69.44%|1 /25|90.91%|
| Published doubles |45 /35|21 /14 /24|52.50% /67.50%|1 /21|77.14%|

All169 publisher-human anchors, all157 live prediction candidates, misses, extras, class confusions, unknowns and frozen earlier draft source offsets remain visible. Their published timing agreement is not independently certified physical contact precision. No named/human player binding was supplied; all predicted named hitters remain unknown. Native and D9 taxonomy results remain separate.

Across these three exposed clips, contact micro F1 is67.48% at±3 and71.17% at±6; unweighted recording macro F1 is65.17%/70.17%. These are descriptive recording averages, not blinded match-level estimates. No confidence interval or unseen-match accuracy is claimed. Exact summary/input hashes and actual stage/resource scopes are in `prod_20261105_external_summary_v1/`.

Test7 uses all31 primary coarse legacy intervals with exact seconds×30, not generated proposals. Result29TP/3FP/2FN,F192.0635%,IoU.774815,startMAE33.8621/end19.7586frames. Matched maxstart242/maxend135frames; missed22/23 and extras `[1491,1615)`, `[6830,7018)`, `[7586,7695)` remain. See full31-row CSV and both tolerance denominators in `prod_20261105_external_test7_reference_v1/`. Whole-second labels limit frame-level interpretation; no arbitrary offset/merge was applied.

India's85-anchor causal table/136 exact-PTS source frames distinguish weak discarded detections, post-cut invalid registration, absent current player evidence and detector-cadence geometry abstention. At serve419, raw support.429/.432/.453 on416–418 is below the unchanged.5 admission threshold, leaving no reliable incoming fit. At1569/2714 geometry is reacquiring; at3736 current people are absent. These are separate mechanisms, not a reason to globally lower a threshold. Test7 misses have their own bounded original-frame review/semantic trace, with explicit provenance limitations.

## Reproducibility and retained failures

The Test1 executor is `research/run_pipeline_experiment.py`; new experiment directories retain its exact executed script/config/source/model hashes. Reproduce a candidate by preparing a new directory/configuration; current-root additions to API/LLM settings differ from the old frozen hash set and must be captured as a new run, never silently accepted under old source metadata.

`research/production_external_stress.py prepare/run` reuses the existing production real-video harness and SessionRunner. The frozen external protocol_v2 contains exact launch commands and input-only sessions. The offline adapter `production_external_reference_report.py` runs only after complete source/frame/frontier checks. New cached studies require exact baseline and runner/helper/cache proof; no cached replay is counted as fresh inference.

Retained failed/rejected evidence includes initial external hook failures, missing optional runtime monitor without installation, browser-smoke executor corrections, one failed offline review metadata attempt, contact suppression, motion scoring rejection and the first frontend calibration-test failure. An unchanged-source frontend repeat passes, but that isolated observed failure is not erased or assigned a causal explanation without reproduction.

No profile/default/deployment promotion occurred. The final release decision and explicit failed/blocked/unvalidated gates are in [PRODUCTION_READINESS_FINAL_REPORT.md](PRODUCTION_READINESS_FINAL_REPORT.md).
