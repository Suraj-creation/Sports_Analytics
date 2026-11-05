# Independent production release review — 5 November 2026

**Recommendation: retain controlled experimental status; do not approve production promotion.** The repository contains substantive, tested reliability repairs. They do not supply independently reviewed contact/trajectory/identity/shot/doubles accuracy, a new blind match set, an agreed boundary tolerance, actual target-hardware measurements or deployed-cache migration. New full-video experiments were still running during this review; their incomplete outputs were deliberately excluded.

This is an independent read-only review of source `85993259a3a2838881ed2b18658a07967058d191` (production commit `130825008eb5d39f58130d4e15c8e3c1fb6911cd`). It reads current code, historical issue conclusions and source-bound controls, current readiness documents, dataset metadata and completed test logs. It launches no model, encode, browser, remote provider or service change. The orchestrator owns final inventory/report reconciliation and inference decisions. This report does not alter the historical H01–H28 inventory.

## Preservation and completed contract evidence

The safe historical verifier was independently executed into a new directory: `artifacts/benchmarking/experiments/prod_20261105_final_integrity_v1/validation.json`. **2,174/2,174 checks pass**, including frozen baseline files, historical source blobs, model/input hashes and historical experiment metric objects. Validation SHA-256 is `36d10ef9af42ea8a257fef26aaa71091f1e926f523235648cea5202fc6f68983`.

`Benchmarking` is current; `main` remains `301baf08be5e989dd0ed93cb885733c3cf6f356a`. Every supplied checkpoint remains an ancestor of HEAD. All 12 mandatory historical handoff/inventory/report/registry files are byte-identical to task-start `181cb91`. The frozen production source roots equal HEAD. No historical report, video, label, cache, model or accepted media is rewritten by this review. Exact reviewed readiness-document snapshots, SHA-256 values, reference ancestry and executable receipt are in `prod_20261105_final_release_review_v1/`.

Completed final-source logs independently read:

| Scope | Observed result | Limit |
| --- | --- | --- |
| Main Python suite | 2,201 passed, 19 existing warnings, 306.18 s | Software contracts, not independent sporting accuracy. |
| Frontend v2 | 202 passed, 43 files, 5.69 s | Current pose-provenance/estimate UI tests included. |
| Frontend v2 type check | `tsc -b --noEmit`, completed successfully per executor | Static types, not browser image alignment. |
| Frontend v2 production build | Vite completed in 7.21 s into new `frontend_release_v2/build` | Existing deployed frontend untouched. |
| Historical integrity | 2,174 passed | Does not assert completeness of unfinished new inference. |

The separately reported 297 research checks are recorded in `prod_20261105_full_research_v1.log`; their result is not a substitute for any sporting validation gate. The relevant completed logs are under `artifacts/benchmarking/experiments/` with the full `prod_20261105_` prefix. Suite scopes overlap where documented and must not be summed with their focused subsets.

## H01–H28 disposition recommendations

These recommendations preserve the original historical status while describing the new work and remaining gate. Cached interventions remain conditional evidence; final fresh comparisons must use each run's own observations and traces.

| Issue | Recommended current disposition | Evidence and remaining requirement |
| --- | --- | --- |
| H01 — GT23 fragmentation/edit | Partly resolved; scene hypotheses and continuity measured, onset semantics open | `PRODUCTION_SCENE_REPORT.md`: causal 13-proposal screen includes both edits; no authoritative geometry reset. Cached GT23 start worsens 8 frames with barriers. Fresh scene feedback and independent edit/onset labels remain required. |
| H02 — GT27/static T/early terminal | Conditional dependency mitigation; physical terminal validity open | `PRODUCTION_CONTACT_SHOT_REPORT.md` and cached association experiment: suppression alone fragments GT27; association can remove12766 while retaining the interval. This does not prove landing/contact or a correctly localized replacement. |
| H03 — GT31 delayed start/visibility | Proven old mask loss remains fixed; residual observability/onset open | Historical strong rejected peaks and corrected flight admission remain preserved. Pickup close-up does not justify backdating, and remaining invisible/subthreshold spans are unknown. |
| H04 — early GT4/GT22 | Partly bounded; GT4 remains open | Cached scene control improves GT22 start error−29→−2 while preserving the GT22/23 distinction; GT4's−71-frame early onset remains unreviewed. Require fresh per-row confirmation and onset labels. |
| H05 — persistent late starts | Causal classes documented; boundary reliability open | Historical all36 first-provider/motion/contact/cancellation tables remain intact. New pose freshness does not by itself establish earlier observable sporting onset. |
| H06 — end/duration residuals | Major historical truncation improved; terminal evidence open | Cached scene GT16 end worsens+41→+44. Keep all end/duration outliers, misses and common-row comparisons visible. |
| H07 — fine localization | Open acceptance/annotation gate | Detection F1 and average IoU do not establish frame-level onset/end quality. No user-agreed tolerance or reviewed onset convention exists. |
| H08 — discarded candidate explanations | Historical software observability fix retained | Bounded optional diagnostics, strict provenance and independent-provider compatibility remain; current codec20 adds pose/content/association fields. Unrecorded old heatmaps remain unavailable and top-k is not a calibrated posterior. |
| H09 — background/resize confounding | Factors partly isolated; localization/generalization open | Historical identical-input background arms are preserved. New association is not proof of better background modeling or resize selection. No independent localization denominator was added. |
| H10 — near-zero impulse ratio | Reliability semantics strengthened; legacy numerical sensitivity remains | Legacy candidate scoring still computes a relative ratio. Typed motion/physical evidence and association admission prevent that score becoming physical confirmation; they do not prove contact precision or globally replace the ratio provider. |
| H11 — sparse pose/racket | Freshness/provenance defects fixed; acquisition/accuracy gate open | Codec20/wire2 retain actual pose/racket source stamps; scheduled cadence and carried keypoints do not masquerade as fresh observation. No accepted event-triggered acquisition or reviewed physical-impact recall was established. |
| H12 — people/rejection/identity | Telemetry retained; real detection/association accuracy open | Fresh/carried/rejected/anonymous states remain separate. Neither four-player synthetic tests nor raw track counts establish stable human identity. |
| H13 — geometry versus physical truth | Open physical-calibration gate | Image continuity authority is distinct from geometry lifecycle. Full-height columns and line fit are image priors, not 3D airborne ownership, landing or line-call accuracy. |
| H14 — absent ReID | Known optional provider unavailable | No weights, names or embeddings fabricated. Enabling ReID still requires verified rights/hash/runtime and reviewed identity evidence as a separate experiment. |
| H15 — score/backend semantics | Actual limited runtime attribution measured; calibration open | `GPU_PERFORMANCE_REPORT.md` profiles actual CUDA/CPU nodes and Torch dtypes. Raw support/physical estimates remain uncalibrated. Profile names and FP32 exports cannot establish internal execution precision. |
| H16 — future activity/cadence coupling | Contract protections strengthened; fresh feedback verification pending | Exact source-frame pose stamps, provider/frontier/epoch and publication tests pass. Changed scene/association cadence still needs each completed full run's own-cache replay; VOD lookahead is declared, not causal-live. |
| H17 — limited exit recovery | Conservative cue retained; association broadened conditionally | Bounded co-observation memory, directional steps, expiry and reacquisition states mitigate one static-switch mechanism. Do not infer coordinates, merge arbitrary gaps or claim universal occlusion recovery. |
| H18 — VOD versus live | Open live capability/latency gate | Actual growing HLS append/seek works on fixtures; current runner does not establish RTSP/SRT/WebRTC ingestion. Buffered semantics and full-chunk background are not zero-lookahead live analysis. |
| H19 — generic timestamp mappings | Proven VFR detection fixed; general source correspondence remains open | `PRODUCTION_MEDIA_COMPATIBILITY_REPORT.md`: complete bounded-memory PTS scan, real integer/fractional/VFR/offset fixtures. Existing24→30/VFR/high-rate conversion policy stays; no arbitrary-source original↔proxy frame map exists. |
| H20 — browser HLS alignment | Proven new-generation mux defect fixed and Firefox validated; migration/coverage open | Actual player/hook image controls pass; AAC bf0 reproduces323/15360 origin. Immutable old HLS remains wrong until explicit new-root migration/routing. Other browsers and actual NVENC regeneration are separate gates. |
| H21 — runtime/rollback | Proven journal scaling/ownership defects fixed; full runtime claims bounded | `ANALYTICS_CHECKPOINT_REPORT.md`: constant-work checkpoint and owned inputs; append-copy cost rises, restore remains linear. Limited model probes do not establish end-to-end target-hardware throughput. |
| H22 — repeat inference | Pending completion and same-configuration repeat verification | Two different candidate configurations are two experiments, not repeatability of one accepted profile. Do not count cached or component replay as another full neural run. |
| H23 — generalization/component labels | Open external evidence gate | Frozen12-recording metadata has zero eligible new blind IDs. No independently reviewed four-player/contact/hitter/shot/localization set, new model comparison or target domain guarantee. |
| H24 — empty comparison header | Historical fixed export contract retained | No current evaluator changes; full historical metric/byte checks and benchmark controls retained. Do not reopen as a rally-accuracy defect or alter matching. |
| H25 — executor/reset provenance | Historical tooling fix retained; scope limits explicit | Generator/executor identity and event-derived epochs remain separate; Test1 research tools do not become generic validation executors. New source/model/config/cache identities must remain exact. |
| H26 — ignored artifacts/finalizers | Mitigated and reverified; operational backup gate remains | New2174-check audit passes. Clone alone cannot restore ignored evidence; fixed historical finalizers remain historical and were not reused to overwrite results. |
| H27 — empty OCR warning | Known noncausal warning; reviewed OCR accuracy open | Keep warnings/unknown scores and independent analytics. Neither removing OCR nor silence proves scoring correctness. |
| H28 — warning/format maintenance | Existing noncausal maintenance | Final main suite retains19 HTTP422 deprecations. Existing unrelated formatter debt remains distinct from new changed-file checks and sporting failures. |

## Dataset, agent, API and UI limits

The 12-recording manifest and exposure history are coherent with the frozen metadata snapshot: Test1 is development, eight unknown-identity Test2–10 entries are quarantined,0044 is exposed development,0046 is historical exposed evaluation and the250-frame doubles excerpt is AI-draft development. The prospective held-out count is zero. Historical expected hashes/filenames and metadata attestations do not establish present source availability, use rights, exhaustive labels or independence. Current Test1 authorization remains valid; this is a missing evidence gate for new validation claims, not a request to reapprove existing work.

`GENERALIZATION_EVALUATION_REPORT.md`, `DOUBLES_VALIDATION_REPORT.md` and `PRODUCTION_READINESS_ANNOTATION_PROTOCOL.md` correctly require reviewed match identities/splits, source correspondence, exhaustive per-component labels, uncertainty, review/adjudication and frozen metric semantics before new blind evaluation. They do not manufacture labels or change historical annotation review flags. Sixty-four AI-draft boxes on16 sampled frames cannot establish full four-person tracking/hitter/shot accuracy.

The existing agent remains grounded match Q&A with read-only tools; the real command service remains `EngineService` plus LocalBus/RedisBus. There is no new general persistent multi-agent research-task scheduler in `agents/`. Actual local fault→retry→stop controls are meaningful, but use a model-free runner and LocalBus. They do not prove remote provider cancellation, Redis deployment durability or distributed quotas.

Current source fixes malformed tool arguments, ambiguous/unrecognized player aliases and same-generation stale evidence publication. Final API snapshots fence a consistent event sequence across reads and publication, check live cited events, and hold no repository lock over the model wait. Returned `evidence_sequence` is a snapshot token, not an assertion that the event store will never change after the response. The agent's numeric/citation validator remains a consistency check; it cannot verify semantic truth or physical impacts.

The per-session LLM token-budget setting is still not enforced by this loop. History has12 entries and questions1,000 characters, but history-content/tool-call/provider-work budgets and external provider outages have no complete production validation here. New live-feed/Q&A wording distinguishes estimates/support bands from human review; the browser pose provenance also distinguishes carried keypoints. Those safeguards do not provide reviewed identities or calibrated confidence.

## Required final report reconciliation

The readiness inventory was still a provisional template at this review snapshot: all28 rows had empty new evidence lists and a shared open status. Finalization must preserve known fixes H08/H24/H25 and attach precise partial/open statuses and exact current evidence. The running matrix/roadmap also need their completed media and source-version details reconciled: perception codec is20, pipeline version3 and track wire2. Superseded under-validation text must not become a contradictory final claim.

The orchestrator has now provided completed final-source main/frontend test results, independently checked above. Fresh run metrics, own-cache traces, per-row regressions, backend/fallback/resource details and repeat conclusions remain pending until their actual completion and validation. Final aggregate summaries must not inherit earlier runtime claims or hide GT23/GT16 boundary regressions behind detection scores. No production default, asset URL, service or deployment was changed or approved by this review.

## Superseding review update: completed Test1 pair and expanded discovery

This appended stage supersedes the earlier **pending fresh-run**, **provisional28-row inventory** and **12-entry inventory-completeness** statements. The original review above remains a dated snapshot, including its cached-only recommendations. Current completed evidence, rather than a rewrite of that snapshot, is recorded here. External stress runs described below remain running and are not scored or called complete by this update.

The two frozen-source Test1 production runs at `8599325` are now complete through17,268 frames/frontier17,267. Their metadata says `completed`, every pinned core-source hash independently matches the current frozen files, and each run's own288-cache semantic replay reports exact36-interval parity. I independently compared fresh versus own-cache prediction CSV bytes: identical for both profiles. The replays remain semantic replay, not additional neural runs.

| Fresh profile | TP/FP/FN | Start MAE | End MAE | Mean IoU | Own-cache parity |
| --- | --- | ---: | ---: | ---: | --- |
| Association |36/0/0|29.1389|10.3333|.867622|Exact36 rows/CSV|
| Association + scene |36/0/0|28.2500|10.4722|.871026|Exact36 rows/CSV|

Association preserves every previously selected interval. Its own output/cache audit removes the suspect12766 contact while preserving GT27 `[12455,12954)`, so those boundaries no longer depend on retaining that particular contact. The raw painted-T observation remains inspectable as ambiguous/static with no selected trajectory coordinate. This is a source-bound causal mechanism result; it is not proof of exhaustive physical contact, correct landing or generalization.

Fresh scene feedback changes **seven** rows, rather than the four changed by the older cached scene counterfactual. The fresh result must not inherit that counterfactual's exact values:

| GT | Fresh scene effect relative to association/selected |
| --- | --- |
|16|End7499→7502; signed error+41→+44, regression.|
|17|Start7535→7537; +3→+5, regression.|
|19|Start8110→8111; +4→+5, regression; match remains recovered.|
|21|Start10250→10249 improves+5→+4; end10539→10538 worsens−24→−25.|
|22|Start10578→10605 improves−29→−2; end10737→10738 worsens+29→+30.|
|23|Start10769→10775 worsens+36→+42; **not** the cached10777/+44 result.|
|34|Start15983→16000 improves absolute error15→2.|

All other29 interval pairs remain exact; GT4's early start remains1803/−71. Every historical recovered match is retained, and neither fresh run has an unmatched prediction under the unchanged IoU0.5 evaluator. `prod_20261105_full_comparison_v2/results.json` retains the complete36-row and common-denominator comparisons against all references. Its positive half-open topology is correctly descriptive: prediction22 spills only4 frames into GT23 for association and5 for scene. That creates degree-two overlap edges without proving a physical split/merge. The corrected v2 interpretation explicitly retains that limitation; do not turn graph multiplicity into a rally-joining policy.

The independent contact audit counts453/446 live contacts and linked strokes, zero automatically physically confirmed impacts, and zero audited provenance/context violations for its checked fields. Physical probable/ambiguous/insufficient counts remain policy coverage, not accuracy. Exact PF/RF availability does not certify original VFR camera-exposure freshness or every asynchronous/live publication decision. The two profiles run different configurations concurrently on separate leased GTX1080Ti cards; their1649.78/1794.37-second worker times are descriptive, not isolated same-configuration performance repetitions. H22's identical-configuration repeat gate therefore remains open.

The readiness inventory now has specific production statuses and evidence for all28 original issues, preserving H08/H24/H25's earlier fixes. Its earlier empty-evidence template is superseded. H01/H02/H04/H11/H16 have stronger completed development evidence, while physical boundary, trajectory/impact, scene accuracy, identity and release acceptance gates remain open.

The metadata manifest now inventories **15 entries**, including previously exposed India/Denmark/DShuttleNet references discovered in the authorized local project data. Existing relevant-data investigation was already authorized; a missing per-recording checkbox was not a new permission requirement. Media-analysis authorization is now recorded separately from still-unknown redistribution/training rights and independent review. Test7's verified full source and primary31-row legacy hand-label table can support coarse rally-reference stress agreement. The three prepared clips contain published human anchors/classes with draft project source alignment, not absent labels. They do not supply new blind status, independently certified physical impacts or dense tracking truth. No genuine held-out seal is changed. Bounded Test1/Test7 identity evidence does not prove every edited frame is match-disjoint.

`PRODUCTION_ADDITIONAL_DATA_PROVENANCE.md` and `prod_20261105_data_provenance_discovery_v1/additional_available_materials.json` preserve the exact available proxies, annotations and crop mappings. Existing−1/−3/0 source-origin translations are fixed conditional import data, never offsets fitted against new predictions. The four external workers receive only clean uploaded media, empty known-format rosters and the frozen profile; original annotation/source/crop provenance is separate from inference. SS22 partitions are full-clip evaluation partitions, not independently labelled rally boundaries.

External v1 attempts stopped **before neural inference** because an old research harness patched a removed plugin-global `get_settings`. That was a real research-executor migration defect, not a production inference failure. Both harnesses now use the current explicit staged-registry binding; `BadmintonSession` derives perception caches from `registry.models_dir`, and `SessionRunner` already injects its Settings/registry. No synthetic attribute was introduced. Two regression controls reproduce the old failure. The final45-control run includes an actual67-frame CPU weightless continuous harness with retained observations, actual `SessionRunner._create_sport` construction with controlled media boundary, and rejection of a mismatched staged root. Deliberately disabled neural components produce explicit partial capability status; this smoke is not neural sporting validation.

The v1 attempts, original protocol and all intermediate failed fixture logs remain preserved. The root launched India_v2 and Test7_v2 under new `protocol_v2`, after those controls; Denmark/doubles are sequenced separately. The frozen profile bytes equal v1, with only the already declared passive diagnostic ranges disabled relative to the primary Test1 profile. No new threshold, precision, model, court/identity GT or annotation value enters inference. These external runs are still running at this append's review point. Their completed result/evaluation claims must wait for durable reports and before/after guards. API/agent remote-budget/cancellation feasibility also remains a separate investigation; no remote provider evidence is invented here.

## Superseding external completion and actual product control

The preceding running-status statement is a stage snapshot. The four v2 external
executors are now independently checked as `completed`, worker exit 0 and
`frozen_source_inputs_unchanged=true` in
`../production-readiness-runs-20261105/{india,denmark,doubles,test7}_v2.executor.json`.
India/Denmark/doubles report 4,800/3,300/3,600 frames respectively, with retained
observations. The Test7 full worker's result artifacts, rather than the generic
executor envelope, own its frame-count and rally-reference evaluation claims.
Recorded worker durations are 559.121/227.816/388.573/1167.769 seconds respectively.
These are exposed external stress runs under the unchanged frozen profile and
declared input mapping; the completion audit alone does not establish physical
contact, shot classification, boundary or four-person identity accuracy.

An additional actual local-product control used the real built frontend,
FastAPI factory, `EngineService`, `LocalBus`, upload storage, CPU media encoding,
segment pipeline, event store and binary WebSocket gateway. Firefox uploaded a
retained 67-frame barcoded fixture with all neural providers explicitly disabled,
observed completion at frontier 66, downloaded four real export links and sought
six frames with independently matching pixels. Unknown-source requests return
404; a repeated own source returns 200 and the same session ID. Malformed/empty
containers reach actual failed analysis. Both owned server/driver/Firefox process
sets were reaped, ports closed and production/build/input guards unchanged. No
deployment, port 8010 server, GPU worker or original media was changed.

The control reproduced four additional product failures: truncated empty
application CSV columns, fabricated 100% failed coverage without media, running
copy on failed exports, and private raw FFmpeg paths in HTTP and binary WebSocket
failure details. After all external runs finished, the orchestrator released the
freeze and approved the five-file correction; exact pre-edit digest and apply
checks passed. Actual-source focused tests now pass 15 API/export/WebSocket and
10 frontend cases plus TypeScript. The full private root-cause detail remains in
the original store/logs. `PRODUCTION_PRODUCT_SMOKE_REPORT.md` links source,
commands, screenshots, network evidence, red/green controls and compatibility
limits. A new-build post-fix actual browser run and final integrated tests remain
separate gates at this append's point; neither the control nor these repairs
imply badminton accuracy or public deployment promotion.

That pending local product gate subsequently passed in the new
`prod_20261105_product_smoke_v3/` run against final integrated source and the
independently receipted frontend release-v3 build. Exact source307/build45/input
guards remain unchanged. Actual HTTP and binary WebSocket failure details are
sanitized while post-shutdown private store details remain full; empty and failed
application CSVs retain17 columns; failed coverage and export copy are truthful.
The actual six pixel-identity seeks and four hash-matching browser downloads pass,
content-addressed reuse and unknown-session404 behavior remain intact, and all
owned processes/ports are closed. The failed undecodable media pane's loading
placeholder remains a recorded presentation limitation. No neural sporting,
authenticated multi-user, Redis, remote-provider or production deployment claim
is inferred from this CPU diagnostic product replay.

The last failed-source loading placeholder was then fixed with 13 new frontend
regressions while preserving ready partial playback, recovery and retry. The new
isolated frontend release-v4 build and actual product-smoke-v4 replay pass exact
source/build/input guards, all prior checks and the explicit video-unavailable
state. The full frontend repeat passes223/223; its first222/223 attempt retains a
separate unresolved calibration test observation, now independently reviewed.
No calibration code was changed by this workstream. The source/build receipt
retains that first failure and distinguishes the unchanged-source repeat.

A separate actual browser replay of copied completed Test7-v2 neural results now
passes with `start_engine=False`. It uses 896 independent byte copies and all898
original consumed-file hashes remain unchanged, with no original SQLite
connection or WAL/SHM processing. Exact exported live event IDs/counts match the
producer/durable fold:32 raw rally ends,248 contacts and248 strokes. The product
preserves21 intervals marked official by existing phase logic and all21 exported
boundaries; the other11 raw candidates remain retained. Four browser downloads
match HTTP exports; the original source SHA is retained and public URI redacted.
The complete backlog's actual shot view shows unknown/estimated and unassigned
evidence. `prod_20261105_neural_results_product_v3/` is the selected product
artifact; its v1/v2 predecessors are documented harness-control variants of the
same neural output, not additional inference or accuracy/generalization evidence.

The calibration follow-up subsequently demonstrated a real commit-to-passive-
effect mutation-option race with a native first-enabled DOM click. All three new
contracts fail on the actual prior component and pass after explicit click-time
`{sessionId,points,frame}` variables. The exact ordering of the original v4 failure
remains unrecorded; this repair addresses the separately controlled same-signature
software defect rather than claiming that original schedule was proved. The
backend's existing geometry validation rejects empty point sets. The detailed
qualified audit is `PRODUCTION_CALIBRATION_SAVE_REPORT.md`.

Final actual source passes calibration6/6, full frontend226/226 across46 files,
TypeScript and isolated release-v5 build; the receipt verifies four critical
source/sourcemap contents and45 assets. The final actual-browser
`prod_20261105_product_smoke_v5/` passes its unchanged309-source/45-build/input
guards, all6 exact pixel seeks,4 matching downloads, empty/failed17-column CSV,
truthful unavailable/partial/coverage states, public/private detail separation,
source reuse/404 ownership and cleanup. Result SHA256 is
`3c2bb9d86cc4165d1f0c7669bfedaa63afd38141b8fc9b24fc51dc6823751e78`.
The nonempty Test7 product-v3 snapshot remains valid as its explicit prior-build
stage; no new neural inference, input label/default profile change or deployment
is implied by this final product gate. All earlier failures and intermediate
receipts remain retained.
