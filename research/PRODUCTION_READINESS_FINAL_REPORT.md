# Production release-readiness result — 5 November 2026

**Release decision: NOT production-ready. Keep the profiles experimental.** Reliability defects were reproduced, repaired and tested; six fresh complete-input inference runs and source-bound counterfactuals were executed. Additional recordings expose substantial contact, shot and boundary failures. Passing Test1 rally detection and software suites does not satisfy the missing physical-accuracy, generalization, identity, live-mode or deployment gates.

## Delivered implementation

Work remains exclusively on `Benchmarking`; `main` stays `301baf08be5e989dd0ed93cb885733c3cf6f356a`. Task-start was clean `181cb917dd923524c48772b55ecc71a49ae68518`. No reset, rebase, cleanup of existing work, model/environment replacement, deployment change or default-profile promotion occurred.

| Commit / evidence | Resulting behavior |
| --- | --- |
| `130825008eb5d39f58130d4e15c8e3c1fb6911cd` | Typed contact reliability; exact pose/racket observation provenance; bounded opt-in shuttle ambiguity; independent content/court authority; cache 20 / pipeline 3 / wire 2; VFR detection and HLS-origin repairs; owned constant-work analytics checkpoints; initial agent/publication fixes. |
| `85993259a3a2838881ed2b18658a07967058d191` | Reproducible experiment/media/runtime/resource/provenance harnesses. This is the frozen source used for the six new neural runs. |
| `f85b1df69dcab2e6a7a1394070e954e469cb522e` | Durable Q&A token admission/accounting; physical uncertainty/source-contact projection; stable application CSV; public HTTP/WS error projection; truthful failed-job/video state; deterministic calibration Save race repair. |
| Final scoped research commit | Current controlled executors, tests, dataset protocol, all 28 dispositions, rejected studies and release evidence. Exact final Git identity is recorded in the release evidence index. |

Sport perception, event/FSM and evaluation source used for the neural runs remains unchanged after its freeze. Later application/LLM settings and research guards are explicitly separate from those inference results. A current-root rerun needs a new source/configuration freeze; old frozen source guards deliberately reject a changed root.

The contact pipeline now separates trajectory, physical-event and actor support. Finalized ledger events do not establish physical impact; all actual new automated physical-confirmed counts are zero. Raw model points/candidates are preserved, ambiguous static competitors are withheld rather than replaced with invented coordinates, and true floor shuttles remain a negative control. Relative impulse remains a legacy candidate feature: replacing it blindly was experimentally rejected.

Actual pose/racket source stamps survive cache/store/wire transport. Unknown, carried, reconstructed, stale or future evidence cannot become fresh physical observation. Content hypotheses use prior-frame context and remain independent of authoritative court geometry. No new neural model or fabricated identity was introduced.

The final product fixes include an independently reproduced calibration race: a native first-enabled DOM click could call the API with `{}` before TanStack refreshed mutation options. Explicit click-time variables fix all 3 red→green controls. Backend rejection prevents claiming an unobserved geometry overwrite. The earlier full-suite failure is retained; its particular scheduling was not recorded.

## Actual inference and external quality

| Input / profile | Frames processed | Rally TP / FP / FN | Start / end MAE frames | Mean IoU | Scope |
| --- | ---: | --- | --- | --- | --- |
| Test1 historical selected |17,268|36 /0 /0|29.1389 /10.3333|.867622|Immutable reference |
| Test1 fresh association |17,268|36 /0 /0|29.1389 /10.3333|.867622|Fresh GPU; all selected endpoints retained |
| Test1 fresh association+scene |17,268|36 /0 /0|28.2500 /10.4722|.871026|Fresh GPU; 7 changed rows with regressions |
| Test7 fixed association+scene |10,725|29 /3 /2|33.8621 /19.7586|.774815|Fresh full upload; 31 coarse legacy reference intervals |

India 4,800, Denmark 3,300 and published doubles 3,600-frame continuous inputs also completed fresh inference. Every run preserved its exact source/config/model/input/output identity. Each worker processed the full input, including gaps; labels never entered perception or event generation. The three clips use clean clip-only history, unlike older original-video-seeded comparisons.

| Published exposed reference | All GT anchors / predicted contacts | Contact F1 at ±3 / ±6 frames | Correct shot class on ±3-frame matches | Unknown predicted shot labels |
| --- | --- | --- | --- | --- |
| India singles |85 /89|73.56% /73.56%|3 /64|70 /89|
| Denmark singles |39 /33|69.44% /69.44%|1 /25|30 /33|
| Doubles |45 /35|52.50% /67.50%|1 /21|27 /35|

These are reference-agreement measurements under preserved earlier draft source alignments, not certified physical-contact precision. They retain every extra, missed anchor and unknown. Across the three exposed clips, contact micro F1 is 67.48%/71.17%, recording macro 65.17%/70.17%. Match-level blind accuracy and meaningful confidence intervals are not established. Shot taxonomies remain separate; low selective accuracy/coverage prevents production promotion.

All 36 Test1 rows, original/fresh-v1/selected common-row comparisons, unmatched predictions, IoU distributions, RMSE/bias/P50/P90/P95/max and both tolerance denominators are in `artifacts/benchmarking/experiments/prod_20261105_full_comparison_v2/`. All 31 Test7 rows are in `prod_20261105_external_test7_reference_v1/`. Full class confusions, matches/misses/extras and runtime scopes are in the external reference packages and `prod_20261105_external_summary_v1/`.

GT27 remains `[12455,12954)` after removing suspect contact 12766 and its stroke. GT2/19/20 remain recovered. The scene arm improves GT22 onset −29→−2 frames and GT34 −15→+2, but GT23 onset +36→+42 and GT16 end +41→+44 regress. GT4 −71, GT5 +98, GT9 +106, GT15 +86 and GT28 +61 remain important onset errors. There are no row-specific offsets, forced event counts, annotation changes or matching changes.

## Discriminating experiments and remaining mechanisms

- **Motion reliability:** the existing absolute/sensitivity-based provider retains Test1's 36 matches but sharply reduces external contact recall. Reject promotion; aggregate rally F1 would hide the damage.
- **Anonymous geometry brackets:** timing/contacts/actors/rally boundaries stay unchanged and some shot labels recover, but many new labels are wrong. Keep shadow/opt-in; no physical identities or pose are invented.
- **Perception and scene coupling:** the content barrier changes both TrackNet windows and background histories, producing 4,354 raw-coordinate differences and detector-cadence feedback. Cached scene replay alone cannot establish fresh perception results.
- **New Test7 failures:** a 32-frame raw loss splits GT3; GT22's initial candidate cancels during a 24-frame loss before a later fragment; GT23's 49-frame event cancels against the 60-frame minimum, before the later close-up. A real same-camera edit at frame 7706 correctly separates points, and a source-visible floor shuttle is distinct from GT27's painted-T distractor. No blind timeout/duration relaxation or interval merge was accepted.

[PRODUCTION_BOUNDARY_REVIEW.md](PRODUCTION_BOUNDARY_REVIEW.md), [PRODUCTION_CONTACT_ASSOCIATION_REVIEW.md](PRODUCTION_CONTACT_ASSOCIATION_REVIEW.md) and [PRODUCTION_SCENE_REPORT.md](PRODUCTION_SCENE_REPORT.md) contain the exact causal evidence, controls and rejection reasons. The synchronized own-source replay packages each have 1,125 exact-PTS frames across 11 windows; 66 sampled actual Firefox renders passed. Source review is diagnostic, not independent human ground truth.

## Completed software and product verification

| Verification | Result |
| --- | --- |
| Final main Python suite | **2,280 passed**, 19 existing HTTP 422 deprecation warnings; 315.73 s |
| Final research suite | **458 passed**, 8.03 s |
| Final frontend | **226 passed / 46 files**, 5.92 s; typecheck succeeds |
| Final isolated frontend build | Vite succeeds in 7.01s; 45 asset hashes and 4 critical source-map byte bindings verified; deployed dist untouched |
| Historical integrity | **2,174/2,174**, repeated; original videos/GT/models/frozen reports/results retained |
| Final actual browser upload |67 frames→frontier 66; 6/6 independently correct frame seeks; 4 downloaded exports match HTTP bytes; real WS/progress/ownership/reuse/failure controls pass |
| Actual nonempty neural results→product | Prior v4-build stage, copied Test7 data; 32 raw rally ends, 248 contacts and 248 strokes match producer IDs/counts. Existing application export has 21 official rallies, all boundaries exact; 11 nonofficial intervals remain visible in raw benchmark evaluation. No re-inference or original SQLite connection. |

Main/research/frontend suites are separate scopes; focused subsets overlap and are not added to these totals. Prior failed controls and the first frontend failure remain preserved. Actual browser fixtures and controlled provider calls validate contracts, not sporting accuracy or live-service reliability.

The tested cache lifecycle includes codec 20, pipeline 3, wire 2, source/epoch/frontier/rollback guards and exact runner/helper baseline proofs. Future full-upload executors now capture a bounded completion-time cache catalogue and verify it after worker close; current replay verifies it when present. Historical Test7 lacked that catalogue: its 179 cache hashes are posthoc and its full event replay matches, but no old metadata was backfilled. This limitation remains explicit.

## Release gates

| State | Gate / evidence requirement |
| --- | --- |
| **FAIL** | Current shot-classification coverage/accuracy and full individual analytics do not meet the requested capability; measured external failures remain. |
| **BLOCKED** | New match-disjoint reviewed validation/test recordings, independent physical-contact/shuttle/court/identity labels, agreed boundary tolerances and RTX4000Ada deployment measurements are absent. |
| **UNVALIDATED** | Continuous four-person identity, physical calibration, score/winner/pose/racket accuracy, true-live ingestion/recovery/latency, generic original↔proxy VFR/high-FPS mapping, distributed/Redis/provider failures and old-HLS deployment routing migration. |
| **PASS** | Recorded implementation contracts, current software suites, supported isolated product controls, immutable historical evidence and source-bound experiment reproduction within their stated scopes. |

The 15-entry manifest contains **zero eligible prospective blind recordings**. Doubles produces four local track keys on 1,719/3,600 frames, but those are model-coverage counts with no independent visibility/identity denominator. No IDF1/HOTA or per-person physical accuracy is claimed. Actual hardware is two GTX 1080 Ti cards; measured Test1 throughput 10.4669/9.6235 FPS and external 8.58–14.49 FPS do not establish real-time or RTX 4000 Ada performance. See [GENERALIZATION_EVALUATION_REPORT.md](GENERALIZATION_EVALUATION_REPORT.md), [DOUBLES_VALIDATION_REPORT.md](DOUBLES_VALIDATION_REPORT.md) and [GPU_PERFORMANCE_REPORT.md](GPU_PERFORMANCE_REPORT.md).

Q&A accounting defaults to prospective **reported** vendor usage with durable reservations and unknown-usage blocking. It may overshoot by one response and is not a billing hard cap. Strict admission is explicit opt-in and requires a verified input-bound provider capability; native providers do not yet provide it. SDK transport retries are disabled, but server-side fallback/billing and wall-clock cancellation remain separate validation limits. Full migration/retention details are in [PRODUCTION_LLM_BUDGET_REPORT.md](PRODUCTION_LLM_BUDGET_REPORT.md).

## Evidence and next release work

[PRODUCTION_READINESS_FAILURE_INVENTORY.json](PRODUCTION_READINESS_FAILURE_INVENTORY.json) gives truthful dispositions for all H01–H28 and 15 new findings; the historical inventory is unchanged. [PRODUCTION_READINESS_VALIDATION_MATRIX.md](PRODUCTION_READINESS_VALIDATION_MATRIX.md) maps every acceptance gate. [PRODUCTION_READINESS_EXPERIMENT_RESULTS.md](PRODUCTION_READINESS_EXPERIMENT_RESULTS.md) records successful and rejected studies. The annotation protocol and dataset/exposure manifests identify the exact independent review needed next.

The final machine-readable release index is `artifacts/benchmarking/experiments/prod_20261105_release_evidence_v1/manifest.json`. It records final Git identity, source/report/test/output hashes, artifact locations, preserved failures and explicit evidence limitations. Ignored artifacts remain local and need separate backup; Git commits alone do not contain model/video/evidence payloads.

The next release decision needs reviewed cross-match component data and measured improvement of the observed failure categories, exact-configuration repeat inference, verified deployment resources and completed live/media migration gates. No experimental profile was promoted or application deployed.
