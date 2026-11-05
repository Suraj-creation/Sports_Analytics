# Production readiness audit — 5 November 2026

**Release decision: keep experimental.** Substantive reliability repairs, two fresh complete Test1 runs, independent own-cache audits and complete software suites are recorded. Reviewed match-disjoint component accuracy, prospective blind evaluation, four-person identity accuracy, agreed boundary tolerances and deployment-hardware evidence remain release gates. This document distinguishes implementation from sporting validation.

## Repository and immutable evidence

Work began at clean `Benchmarking` HEAD `181cb917dd923524c48772b55ecc71a49ae68518`, with one worktree and no existing dirty/untracked work. `main` remains `301baf08be5e989dd0ed93cb885733c3cf6f356a`. No reset, clean, rebase, deployment change or historical rewrite occurred. The full handoff, H01–H28 inventory, 5 November results, referenced reports/source/tests and available source-bound packages were read before edits. The current inventory is separate: [PRODUCTION_READINESS_FAILURE_INVENTORY.json](PRODUCTION_READINESS_FAILURE_INVENTORY.json).

Initial and independently repeated historical integrity checks each passed **2,174/2,174**: 1,766 frozen evidence files, 86 historical source blobs, 28 historical metric objects and input/model references. The 12 mandatory historical files remain byte-identical to task-start. Ignored artifacts are preserved locally; cloning Git alone does not restore them.

Test1 remains 1920×1080, 30 FPS, 17,268 frames, 575.6 seconds and 36 annotations. Video SHA256 `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`; GT SHA256 `30651cf7238924d6a5072b1dd71d34ca5839cd5b842f696e745229033ae4f887`. Zero-origin, half-open intervals, actual FPS, seven-column CSV, annotations and matching are unchanged. GT is used only after inference for evaluation/diagnostic overlays.

## Implemented and measured repairs

Production commit `130825008eb5d39f58130d4e15c8e3c1fb6911cd` contains the perception/event/API/media repairs. Harness commit `85993259a3a2838881ed2b18658a07967058d191` freezes the initial reproducible executors. New research-only harness corrections and audits retain their own executed-source copies and hashes.

- Typed contact evidence separates trajectory support, physical-impact support and actor attribution. Legacy numerical candidate scoring remains for compatibility; it can no longer supply physical confirmation. Automatic physical-confirmed count is zero. Observation confidence, heuristic support and calibrated probability remain distinct.
- Actual per-person pose/racket source stamps survive caching, storage and wire transport. Unknown/future/stale source evidence cannot become current physical support. A carried detector box may still have a genuinely current pose. Cache codec20, pipeline3 and track wire2 are versioned; legacy diagnostic reads retain unknown provenance.
- Optional bounded shuttle co-observation association retains raw points/candidates and explicitly abstains on a static/moving ambiguity. It never substitutes a predicted coordinate. Coherent moving witnesses, bounded history/expiry, epoch/provider ownership, rollback and floor/launch/apex controls are tested.
- Optional foreground content hypotheses are independent of camera/court authority. Prior-frame ROIs and source/frontier/schema validation precede epoch resets and model windows. The experimental barrier partitions TrackNet windows and background history; that interaction is explicitly measured rather than attributed to a single cause.
- Equal-rate VFR headers no longer bypass complete bounded-memory packet-PTS cadence checks. Corrected HLS muxing preserves encoded MP4 bytes while repairing browser physical-image origin. Old accepted assets/routing remain untouched; a tested new-root migration tool is available.
- Analytics checkpoints use an owned persistent journal: caller mutation, failed-append corruption and growing checkpoint copies are repaired. Checkpoint work is constant; restore remains linear and copying makes append cost higher.
- Agent tool parsing/player filters fail closed. Q&A publication fences both analysis generation and event sequence and verifies live citations without holding locks during model waits. UI labels distinguish estimates from human review.
- Existing external research harnesses had an obsolete plugin settings hook. Two failed pre-inference runs were preserved. Registry-based injection now has an actual 67-frame model-free plugin smoke and 45 focused controls; new protocol_v2 retains identical inputs/profile parameters.

No profile was promoted to default. Score, outcome, stroke, team, identity, singles/doubles and independent host contracts remain present.

## Actual end-to-end evidence

| Completed Test1 run | TP / FP / FN | Start MAE frames | End MAE frames | Mean IoU | Whole-run FPS |
| --- | --- | --- | --- | --- | --- |
| Historical selected | 36 / 0 / 0 | 29.1389 | 10.3333 | .867622 | Historical measurement retained separately |
| Fresh association | 36 / 0 / 0 | 29.1389 | 10.3333 | .867622 | 10.4669 |
| Fresh association + scene barrier | 36 / 0 / 0 | 28.2500 | 10.4722 | .871026 | 9.6235 |

The association arm retains **every selected interval** while removing suspect contact12766 and its stroke. GT27 remains `[12455,12954)` without that contact. The scene arm changes seven rows, improves GT22 start−29→−2 and GT34−15→+2, but worsens GT23 start+36→+42, GT16 end+41→+44 and other small boundaries. All36 rows, original/fresh-v1 references, unmatched predictions, common-row errors, tolerances and positive-overlap topology are retained in `artifacts/benchmarking/experiments/prod_20261105_full_comparison_v2/`. Tiny four/five-frame P22 spillovers into GT23 are reported, not mistaken for established semantic merges.

Each arm's own 288 cache hashes, executed source, full17,268-frame trace, EOF frontier, intervals/end reasons, CSV bytes and folded contact/stroke payloads were independently checked. Association has453 live contacts/strokes; scene446. Remaining tracker namespace and recorded-format provenance differences are explicitly resolved/audited. Semantic replay is not another neural inference run, and two configurations are not an identical-configuration repeat.

The fresh workers used separate actual GTX1080Ti GPUs and shared CPU/IO. Detector/pose node-placement probes separately measured CUDA/CPU placement; backend provider labels alone do not prove every node runs on GPU. No RTX4000Ada is available. Runtime figures are observed concurrent offline throughput, not an isolated speedup or real-time guarantee.

## Component, product and dataset scope

[PRODUCTION_COMPONENT_INVENTORY.md](PRODUCTION_COMPONENT_INVENTORY.md) maps22 declared contracts,27 responsibilities,16 local model entries, consumers, schemas, model hashes and known dead/optional/unwired paths. [AGENT_ORCHESTRATION_AUDIT.md](AGENT_ORCHESTRATION_AUDIT.md) distinguishes the existing grounded Q&A agent and EngineService/LocalBus/RedisBus from this investigation's specialist delegation. No substitute persistent multi-agent task system was invented.

The metadata audit now has **15 entries**, including newly discovered related Test7 and three published-reference clips. An initial12-entry metadata screen was too narrow; the new provenance review supersedes it. The user mission authorizes analysis of related local badminton material. Unknown licensing/reviewer history limits claims and redistribution; it is not an invented requirement to reapprove already authorized local investigation. Additional actual runs and qualified reference comparisons are tracked in [GENERALIZATION_EVALUATION_REPORT.md](GENERALIZATION_EVALUATION_REPORT.md) and [DOUBLES_VALIDATION_REPORT.md](DOUBLES_VALIDATION_REPORT.md). These exposed/draft-aligned references do not become prospective blind ground truth.

Final main Python: **2,280 passed**; research: **458 passed**; frontend: **226 passed**, typecheck and isolated build passed. Focused subsets overlap and are not summed. Full details, physical media/browser controls and external run status are in [PRODUCTION_READINESS_VALIDATION_MATRIX.md](PRODUCTION_READINESS_VALIDATION_MATRIX.md).

The remaining gates and feasible ongoing implementation are explicit in [PRODUCTION_READINESS_ROADMAP.md](PRODUCTION_READINESS_ROADMAP.md). No current result establishes independent contact, landing, shot, tracking, court, scoring or four-person accuracy.

## Final application/product/provenance verification

Application commit `f85b1df69dcab2e6a7a1394070e954e469cb522e` adds prospective durable reported-usage Q&A admission, strict opt-in provider bounds, exact live physical-contact projection and analysis-frame semantics, stable17-column application CSV, truthful failed coverage/exports/video pane, sanitized public HTTP+binaryWS failures and the deterministic calibration Save repair. Native model output defaults are preserved; reported mode is not a hard billing cap and native strict input bounds remain unsupported.

Final actual Firefox workflow v5 passes67frames/frontier66,6/6 independently decoded seeks,4 real downloaded exports, source reuse/ownership and public/private failure checks. A separate read-only-copy replay of actual Test7 neural results preserves32 raw intervals,248 contacts/strokes and21 existing official CSV rows exactly. No original SQLite connection, new inference, deployed asset change or event filtering for benchmark scores occurred.

Six fresh complete-input runs finished. Additional exposed references show contact timing F1 at±3 of73.56% India,69.44% Denmark and52.5% doubles, with most shot classes unknown. Test7 has29TP/3FP/2FN against31 coarse rows. These results are substantial release limitations, not merely missing paperwork. Existing motion scoring and geometry alternatives were causally tested and remain unpromoted.

Future full-upload cache receipts now bind exact bounded file/header/frame/source/proxy identities at worker completion and are verified after shutdown and before replay. Historical Test7's missing at-completion catalogue remains explicit posthoc provenance; no backfill occurred. New replay proofs also bind runner/transitive helper source versions.

AllH01–H28 and15 newly found defects/limitations have current evidence-linked dispositions. [PRODUCTION_READINESS_FINAL_REPORT.md](PRODUCTION_READINESS_FINAL_REPORT.md) is the authoritative consolidated release decision; [PRODUCTION_READINESS_VALIDATION_MATRIX.md](PRODUCTION_READINESS_VALIDATION_MATRIX.md) gives the final acceptance states.
